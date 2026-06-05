"""Steamworks harness coverage for auth ticket flows."""
from __future__ import annotations

import ctypes
import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

QL_AUTH_RESULT_PENDING = 0
QL_AUTH_RESULT_ACCEPTED = 1
QL_AUTH_RESULT_DENIED = 2
QL_AUTH_RESULT_ERROR = 3

QL_AUTH_OUTCOME_SUCCESS = 0
QL_AUTH_OUTCOME_RETRY = 1
QL_AUTH_OUTCOME_FAILURE = 2

BEGIN_AUTH_OK = 0
BEGIN_AUTH_INVALID_TICKET = 1
BEGIN_AUTH_DUPLICATE_REQUEST = 2
BEGIN_AUTH_INVALID_VERSION = 3
BEGIN_AUTH_GAME_MISMATCH = 4
BEGIN_AUTH_EXPIRED_TICKET = 5
BEGIN_AUTH_UNKNOWN = 99
AUTH_RESPONSE_OK = 0
AUTH_RESPONSE_VAC_BANNED = 3
AVATAR_SIZE_SMALL = 0
AVATAR_SIZE_MEDIUM = 1
AVATAR_SIZE_LARGE = 2

TICKET_BUFFER = 256
AVATAR_BUFFER = 256 * 256 * 4


def _find_c_compiler() -> str:
    compiler = shutil.which("gcc") or shutil.which("clang") or shutil.which("cc")
    if not compiler:
        pytest.skip("No C compiler found for Steamworks harness")

    return compiler


class AuthResponse(ctypes.Structure):
    _fields_ = [
        ("result", ctypes.c_int),
        ("outcome", ctypes.c_int),
        ("message", ctypes.c_char * 128),
    ]


class SteamServerItem(ctypes.Structure):
    _fields_ = [
        ("serverIp", ctypes.c_uint32),
        ("serverPort", ctypes.c_uint16),
        ("queryPort", ctypes.c_uint16),
        ("ping", ctypes.c_int),
        ("gameDir", ctypes.c_char * 32),
        ("map", ctypes.c_char * 32),
        ("gameDescription", ctypes.c_char * 64),
        ("appId", ctypes.c_uint32),
        ("numPlayers", ctypes.c_int),
        ("maxPlayers", ctypes.c_int),
        ("botPlayers", ctypes.c_int),
        ("passwordProtected", ctypes.c_int),
        ("vacSecured", ctypes.c_int),
        ("lastPlayed", ctypes.c_uint32),
        ("serverVersion", ctypes.c_int),
        ("name", ctypes.c_char * 64),
        ("displayName", ctypes.c_char * 64),
        ("tags", ctypes.c_char * 128),
        ("steamId", ctypes.c_uint64),
    ]


class SteamServerBrowserResponse(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_char * 32),
        ("name", ctypes.c_char * 64),
        ("numPlayers", ctypes.c_int),
        ("maxPlayers", ctypes.c_int),
        ("ping", ctypes.c_int),
        ("map", ctypes.c_char * 32),
        ("botPlayers", ctypes.c_int),
        ("passwordProtected", ctypes.c_int),
        ("vacSecured", ctypes.c_int),
        ("serverIp", ctypes.c_uint32),
        ("serverPort", ctypes.c_uint16),
        ("steamId", ctypes.c_char * 32),
        ("tags", ctypes.c_char * 128),
        ("gametype", ctypes.c_char * 64),
        ("lastPlayed", ctypes.c_uint32),
    ]


class SteamServerBrowserFailure(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_int),
        ("eventName", ctypes.c_char * 64),
    ]


class SteamServerBrowserRefreshComplete(ctypes.Structure):
    _fields_ = [
        ("eventName", ctypes.c_char * 64),
    ]


class SteamServerBrowserDetailIdentity(ctypes.Structure):
    _fields_ = [
        ("serverIp", ctypes.c_uint32),
        ("serverPort", ctypes.c_uint16),
        ("id", ctypes.c_char * 32),
    ]


class SteamServerBrowserDetailEvent(ctypes.Structure):
    _fields_ = [
        ("identity", SteamServerBrowserDetailIdentity),
        ("eventName", ctypes.c_char * 64),
    ]


class SteamServerBrowserRuleResponse(ctypes.Structure):
    _fields_ = [
        ("identity", SteamServerBrowserDetailIdentity),
        ("eventName", ctypes.c_char * 64),
        ("rule", ctypes.c_char * 256),
        ("value", ctypes.c_char * 256),
    ]


class SteamServerBrowserPlayerResponse(ctypes.Structure):
    _fields_ = [
        ("identity", SteamServerBrowserDetailIdentity),
        ("eventName", ctypes.c_char * 64),
        ("name", ctypes.c_char * 64),
        ("score", ctypes.c_int),
        ("time", ctypes.c_int),
    ]


class SteamServerBrowserDetailLifecycle(ctypes.Structure):
    _fields_ = [
        ("identity", SteamServerBrowserDetailIdentity),
        ("completedCallbacks", ctypes.c_int),
        ("releaseReady", ctypes.c_int),
    ]


class SteamServerBrowserDetailResponseViews(ctypes.Structure):
    _fields_ = [
        ("rulesResponse", ctypes.c_void_p),
        ("playersResponse", ctypes.c_void_p),
        ("pingResponse", ctypes.c_void_p),
    ]


class SteamServerBrowserDetailRequest(ctypes.Structure):
    _fields_ = [
        ("lifecycle", SteamServerBrowserDetailLifecycle),
        ("detailObjectBase", ctypes.c_void_p),
        ("pingQuery", ctypes.c_int),
        ("playersQuery", ctypes.c_int),
        ("rulesQuery", ctypes.c_int),
        ("queriesActive", ctypes.c_int),
    ]


class SteamServerBrowserOwner(ctypes.Structure):
    _fields_ = [
        ("refreshActive", ctypes.c_int),
        ("request", ctypes.c_size_t),
    ]


def _c_string(value: bytes) -> bytes:
    return bytes(value).split(b"\0", 1)[0]


@pytest.fixture(scope="session", params=[False, True], ids=["steamworks_disabled", "steamworks_enabled"])
def steamworks_harness(request: pytest.FixtureRequest, tmp_path_factory: pytest.TempPathFactory) -> tuple[ctypes.CDLL, bool]:
    enabled = bool(request.param)
    build_dir = tmp_path_factory.mktemp(f"steamworks_harness_{'on' if enabled else 'off'}")
    lib_path = build_dir / ("steamworks_harness.dll" if os.name == "nt" else "libsteamworks_harness.so")
    compile_args = [
        _find_c_compiler(),
        "-shared",
    ]

    if os.name != "nt":
        compile_args.append("-fPIC")
    else:
        compile_args.extend(["-DWIN32", "-D_CRT_SECURE_NO_WARNINGS", "-Wno-return-type"])

    compile_cmd = [
        *compile_args,
        "-Isrc/common",
        "-Isrc/code",
        "-Isrc/code/game",
        "-Isrc/code/qcommon",
        "-DQL_BUILD_ONLINE_SERVICES=%d" % (1 if enabled else 0),
        "-DQL_BUILD_STEAMWORKS=%d" % (1 if enabled else 0),
        str(REPO_ROOT / "tests" / "steamworks_harness.c"),
        "-o",
        str(lib_path),
    ]
    subprocess.check_call(compile_cmd, cwd=REPO_ROOT)

    lib = ctypes.CDLL(str(lib_path))

    lib.QLR_Steamworks_Request.argtypes = [
        ctypes.c_char_p,
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_uint32),
    ]
    lib.QLR_Steamworks_Request.restype = ctypes.c_int
    lib.QLR_Steamworks_CancelTicket.argtypes = [ctypes.c_uint32]
    lib.QLR_Steamworks_CancelTicket.restype = ctypes.c_int

    lib.QLR_Steamworks_Validate.argtypes = [ctypes.c_char_p, ctypes.POINTER(AuthResponse)]
    lib.QLR_Steamworks_Validate.restype = ctypes.c_int

    lib.QLR_Steamworks_LoadAvatar.argtypes = [
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.c_int,
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_uint32),
    ]
    lib.QLR_Steamworks_LoadAvatar.restype = ctypes.c_int

    lib.QLR_Steamworks_ActivateOverlay.argtypes = [
        ctypes.c_char_p,
        ctypes.c_uint32,
        ctypes.c_uint32,
    ]
    lib.QLR_Steamworks_ActivateOverlay.restype = ctypes.c_int
    lib.QLR_Steamworks_ActivateOverlayToWebPage.argtypes = [ctypes.c_char_p]
    lib.QLR_Steamworks_ActivateOverlayToWebPage.restype = ctypes.c_int

    lib.QLR_Steamworks_HasServerBrowserInterface.argtypes = []
    lib.QLR_Steamworks_HasServerBrowserInterface.restype = ctypes.c_int
    lib.QLR_Steamworks_GetServerBrowserRequestModeLabel.argtypes = [ctypes.c_int]
    lib.QLR_Steamworks_GetServerBrowserRequestModeLabel.restype = ctypes.c_char_p
    lib.QLR_Steamworks_ServerBrowserRequestModeUsesGamedirFilter.argtypes = [ctypes.c_int]
    lib.QLR_Steamworks_ServerBrowserRequestModeUsesGamedirFilter.restype = ctypes.c_int
    lib.QLR_Steamworks_InitServerBrowserOwner.argtypes = [ctypes.POINTER(SteamServerBrowserOwner)]
    lib.QLR_Steamworks_InitServerBrowserOwner.restype = None
    lib.QLR_Steamworks_BeginServerBrowserOwnerRequest.argtypes = [
        ctypes.POINTER(SteamServerBrowserOwner),
        ctypes.c_int,
        ctypes.c_size_t,
    ]
    lib.QLR_Steamworks_BeginServerBrowserOwnerRequest.restype = ctypes.c_int
    lib.QLR_Steamworks_RefreshServerBrowserOwnerRequest.argtypes = [ctypes.POINTER(SteamServerBrowserOwner)]
    lib.QLR_Steamworks_RefreshServerBrowserOwnerRequest.restype = ctypes.c_int
    lib.QLR_Steamworks_CompleteServerBrowserOwnerRequest.argtypes = [ctypes.POINTER(SteamServerBrowserOwner)]
    lib.QLR_Steamworks_CompleteServerBrowserOwnerRequest.restype = ctypes.c_int
    lib.QLR_Steamworks_RequestServerList.argtypes = [ctypes.c_int, ctypes.c_size_t]
    lib.QLR_Steamworks_RequestServerList.restype = ctypes.c_size_t
    lib.QLR_Steamworks_GetServerListDetails.argtypes = [ctypes.c_size_t, ctypes.c_int]
    lib.QLR_Steamworks_GetServerListDetails.restype = ctypes.c_size_t
    lib.QLR_Steamworks_ReadServerListDetails.argtypes = [ctypes.c_size_t, ctypes.c_int, ctypes.POINTER(SteamServerItem)]
    lib.QLR_Steamworks_ReadServerListDetails.restype = ctypes.c_int
    lib.QLR_Steamworks_FormatServerBrowserResponseId.argtypes = [
        ctypes.c_uint32,
        ctypes.c_uint16,
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    lib.QLR_Steamworks_FormatServerBrowserResponseId.restype = None
    lib.QLR_Steamworks_BuildServerBrowserResponse.argtypes = [
        ctypes.POINTER(SteamServerItem),
        ctypes.POINTER(SteamServerBrowserResponse),
    ]
    lib.QLR_Steamworks_BuildServerBrowserResponse.restype = ctypes.c_int
    lib.QLR_Steamworks_ReadServerBrowserResponse.argtypes = [
        ctypes.c_size_t,
        ctypes.c_int,
        ctypes.POINTER(SteamServerBrowserResponse),
    ]
    lib.QLR_Steamworks_ReadServerBrowserResponse.restype = ctypes.c_int
    lib.QLR_Steamworks_ReadServerBrowserPingResponse.argtypes = [
        ctypes.POINTER(SteamServerBrowserResponse),
    ]
    lib.QLR_Steamworks_ReadServerBrowserPingResponse.restype = ctypes.c_int
    lib.QLR_Steamworks_FormatServerBrowserFailureEventName.argtypes = [
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    lib.QLR_Steamworks_FormatServerBrowserFailureEventName.restype = None
    lib.QLR_Steamworks_BuildServerBrowserFailure.argtypes = [
        ctypes.c_int,
        ctypes.POINTER(SteamServerBrowserFailure),
    ]
    lib.QLR_Steamworks_BuildServerBrowserFailure.restype = ctypes.c_int
    lib.QLR_Steamworks_BuildServerBrowserRefreshComplete.argtypes = [
        ctypes.POINTER(SteamServerBrowserRefreshComplete),
    ]
    lib.QLR_Steamworks_BuildServerBrowserRefreshComplete.restype = ctypes.c_int
    lib.QLR_Steamworks_FormatServerBrowserDetailId.argtypes = [
        ctypes.c_uint32,
        ctypes.c_uint16,
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    lib.QLR_Steamworks_FormatServerBrowserDetailId.restype = None
    lib.QLR_Steamworks_BuildServerBrowserDetailIdentity.argtypes = [
        ctypes.c_uint32,
        ctypes.c_uint16,
        ctypes.POINTER(SteamServerBrowserDetailIdentity),
    ]
    lib.QLR_Steamworks_BuildServerBrowserDetailIdentity.restype = ctypes.c_int
    lib.QLR_Steamworks_FormatServerBrowserDetailEventName.argtypes = [
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    lib.QLR_Steamworks_FormatServerBrowserDetailEventName.restype = ctypes.c_int
    lib.QLR_Steamworks_BuildServerBrowserDetailEvent.argtypes = [
        ctypes.POINTER(SteamServerBrowserDetailIdentity),
        ctypes.c_int,
        ctypes.c_int,
        ctypes.POINTER(SteamServerBrowserDetailEvent),
    ]
    lib.QLR_Steamworks_BuildServerBrowserDetailEvent.restype = ctypes.c_int
    lib.QLR_Steamworks_BuildServerBrowserRuleResponse.argtypes = [
        ctypes.POINTER(SteamServerBrowserDetailIdentity),
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.POINTER(SteamServerBrowserRuleResponse),
    ]
    lib.QLR_Steamworks_BuildServerBrowserRuleResponse.restype = ctypes.c_int
    lib.QLR_Steamworks_BuildServerBrowserPlayerResponse.argtypes = [
        ctypes.POINTER(SteamServerBrowserDetailIdentity),
        ctypes.c_char_p,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.POINTER(SteamServerBrowserPlayerResponse),
    ]
    lib.QLR_Steamworks_BuildServerBrowserPlayerResponse.restype = ctypes.c_int
    lib.QLR_Steamworks_InitServerBrowserDetailLifecycle.argtypes = [
        ctypes.c_uint32,
        ctypes.c_uint16,
        ctypes.POINTER(SteamServerBrowserDetailLifecycle),
    ]
    lib.QLR_Steamworks_InitServerBrowserDetailLifecycle.restype = ctypes.c_int
    lib.QLR_Steamworks_CompleteServerBrowserDetailCallback.argtypes = [
        ctypes.POINTER(SteamServerBrowserDetailLifecycle),
        ctypes.POINTER(ctypes.c_int),
    ]
    lib.QLR_Steamworks_CompleteServerBrowserDetailCallback.restype = ctypes.c_int
    lib.QLR_Steamworks_BuildServerBrowserDetailResponseViews.argtypes = [
        ctypes.c_size_t,
        ctypes.POINTER(SteamServerBrowserDetailResponseViews),
    ]
    lib.QLR_Steamworks_BuildServerBrowserDetailResponseViews.restype = ctypes.c_int
    lib.QLR_Steamworks_InitServerBrowserDetailRequest.argtypes = [
        ctypes.POINTER(SteamServerBrowserDetailRequest)
    ]
    lib.QLR_Steamworks_InitServerBrowserDetailRequest.restype = None
    lib.QLR_Steamworks_BeginServerBrowserDetailRequest.argtypes = [
        ctypes.POINTER(SteamServerBrowserDetailRequest),
        ctypes.c_uint32,
        ctypes.c_uint16,
        ctypes.c_size_t,
    ]
    lib.QLR_Steamworks_BeginServerBrowserDetailRequest.restype = ctypes.c_int
    lib.QLR_Steamworks_CompleteServerBrowserDetailRequestCallback.argtypes = [
        ctypes.POINTER(SteamServerBrowserDetailRequest),
        ctypes.POINTER(ctypes.c_int),
    ]
    lib.QLR_Steamworks_CompleteServerBrowserDetailRequestCallback.restype = ctypes.c_int
    lib.QLR_Steamworks_ReleaseServerListRequest.argtypes = [ctypes.c_size_t]
    lib.QLR_Steamworks_ReleaseServerListRequest.restype = None
    lib.QLR_Steamworks_RefreshServerListRequest.argtypes = [ctypes.c_size_t]
    lib.QLR_Steamworks_RefreshServerListRequest.restype = None
    lib.QLR_Steamworks_RequestServerDetails.argtypes = [
        ctypes.c_uint32,
        ctypes.c_uint16,
        ctypes.c_size_t,
        ctypes.c_size_t,
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
    ]
    lib.QLR_Steamworks_RequestServerDetails.restype = ctypes.c_int
    lib.QLR_Steamworks_CancelServerQuery.argtypes = [ctypes.c_int]
    lib.QLR_Steamworks_CancelServerQuery.restype = None

    lib.QLR_Steamworks_SetRichPresence.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    lib.QLR_Steamworks_SetRichPresence.restype = ctypes.c_int

    lib.QLR_Steamworks_CreateLobby.argtypes = [ctypes.c_int]
    lib.QLR_Steamworks_CreateLobby.restype = ctypes.c_int

    lib.QLR_Steamworks_SetFavoriteServer.argtypes = [ctypes.c_uint32, ctypes.c_uint16, ctypes.c_int]
    lib.QLR_Steamworks_SetFavoriteServer.restype = ctypes.c_int

    lib.QLR_Steamworks_LeaveLobby.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    lib.QLR_Steamworks_LeaveLobby.restype = ctypes.c_int

    lib.QLR_Steamworks_JoinLobby.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    lib.QLR_Steamworks_JoinLobby.restype = ctypes.c_int

    lib.QLR_Steamworks_SetLobbyServer.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint16]
    lib.QLR_Steamworks_SetLobbyServer.restype = ctypes.c_int

    lib.QLR_Steamworks_ShowInviteOverlay.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    lib.QLR_Steamworks_ShowInviteOverlay.restype = ctypes.c_int

    lib.QLR_Steamworks_InviteUserToLobby.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
    lib.QLR_Steamworks_InviteUserToLobby.restype = ctypes.c_int

    lib.QLR_Steamworks_InviteUserToGame.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_char_p]
    lib.QLR_Steamworks_InviteUserToGame.restype = ctypes.c_int

    lib.QLR_Steamworks_SayLobby.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_char_p]
    lib.QLR_Steamworks_SayLobby.restype = ctypes.c_int

    lib.QLR_Steamworks_RequestUserStats.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    lib.QLR_Steamworks_RequestUserStats.restype = ctypes.c_int

    lib.QLR_Steamworks_GetNumSubscribedItems.argtypes = []
    lib.QLR_Steamworks_GetNumSubscribedItems.restype = ctypes.c_uint32

    lib.QLR_Steamworks_GetSubscribedItems.argtypes = [ctypes.POINTER(ctypes.c_uint64), ctypes.c_uint32]
    lib.QLR_Steamworks_GetSubscribedItems.restype = ctypes.c_uint32

    lib.QLR_Steamworks_GetItemInstallInfo.argtypes = [
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint64),
        ctypes.POINTER(ctypes.c_char),
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint32),
    ]
    lib.QLR_Steamworks_GetItemInstallInfo.restype = ctypes.c_int

    lib.QLR_Steamworks_SubscribeItem.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    lib.QLR_Steamworks_SubscribeItem.restype = ctypes.c_int

    lib.QLR_Steamworks_UnsubscribeItem.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    lib.QLR_Steamworks_UnsubscribeItem.restype = ctypes.c_int

    lib.QLR_Steamworks_DownloadItem.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_int]
    lib.QLR_Steamworks_DownloadItem.restype = ctypes.c_int

    lib.QLR_Steamworks_Init.argtypes = []
    lib.QLR_Steamworks_Init.restype = ctypes.c_int

    lib.QLR_Steamworks_ServerInit.argtypes = [ctypes.c_uint32, ctypes.c_uint16, ctypes.c_int, ctypes.c_int]
    lib.QLR_Steamworks_ServerInit.restype = ctypes.c_int

    lib.QLR_Steamworks_ServerInitWithVersion.argtypes = [
        ctypes.c_uint32,
        ctypes.c_uint16,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_char_p,
    ]
    lib.QLR_Steamworks_ServerInitWithVersion.restype = ctypes.c_int

    lib.QLR_Steamworks_ServerShutdown.argtypes = []
    lib.QLR_Steamworks_ServerShutdown.restype = None

    lib.QLR_Steamworks_ServerIsInitialised.argtypes = []
    lib.QLR_Steamworks_ServerIsInitialised.restype = ctypes.c_int

    lib.QLR_Steamworks_ServerEnableHeartbeats.argtypes = [ctypes.c_int]
    lib.QLR_Steamworks_ServerEnableHeartbeats.restype = ctypes.c_int

    lib.QLR_Steamworks_ServerSetDedicated.argtypes = [ctypes.c_int]
    lib.QLR_Steamworks_ServerSetDedicated.restype = ctypes.c_int

    lib.QLR_Steamworks_ServerLogOn.argtypes = [ctypes.c_char_p]
    lib.QLR_Steamworks_ServerLogOn.restype = ctypes.c_int

    lib.QLR_Steamworks_ServerSetProduct.argtypes = [ctypes.c_char_p]
    lib.QLR_Steamworks_ServerSetProduct.restype = ctypes.c_int

    lib.QLR_Steamworks_ServerSetGameDir.argtypes = [ctypes.c_char_p]
    lib.QLR_Steamworks_ServerSetGameDir.restype = ctypes.c_int

    lib.QLR_Steamworks_ServerSetGameDescription.argtypes = [ctypes.c_char_p]
    lib.QLR_Steamworks_ServerSetGameDescription.restype = ctypes.c_int

    lib.QLR_Steamworks_ServerSetMaxPlayerCount.argtypes = [ctypes.c_int]
    lib.QLR_Steamworks_ServerSetMaxPlayerCount.restype = ctypes.c_int

    lib.QLR_Steamworks_ServerSetBotPlayerCount.argtypes = [ctypes.c_int]
    lib.QLR_Steamworks_ServerSetBotPlayerCount.restype = ctypes.c_int

    lib.QLR_Steamworks_ServerSetServerName.argtypes = [ctypes.c_char_p]
    lib.QLR_Steamworks_ServerSetServerName.restype = ctypes.c_int

    lib.QLR_Steamworks_ServerSetMapName.argtypes = [ctypes.c_char_p]
    lib.QLR_Steamworks_ServerSetMapName.restype = ctypes.c_int

    lib.QLR_Steamworks_ServerSetPasswordProtected.argtypes = [ctypes.c_int]
    lib.QLR_Steamworks_ServerSetPasswordProtected.restype = ctypes.c_int

    lib.QLR_Steamworks_ServerGetSteamID.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32)]
    lib.QLR_Steamworks_ServerGetSteamID.restype = ctypes.c_int

    lib.QLR_Steamworks_ServerSetGameTags.argtypes = [ctypes.c_char_p]
    lib.QLR_Steamworks_ServerSetGameTags.restype = ctypes.c_int

    lib.QLR_Steamworks_ServerSetKeyValue.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    lib.QLR_Steamworks_ServerSetKeyValue.restype = ctypes.c_int

    lib.QLR_Steamworks_ServerSetKeyValuesFromInfoString.argtypes = [ctypes.c_char_p]
    lib.QLR_Steamworks_ServerSetKeyValuesFromInfoString.restype = ctypes.c_int

    lib.QLR_Steamworks_ServerUpdateUserData.argtypes = [
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.c_char_p,
        ctypes.c_uint32,
    ]
    lib.QLR_Steamworks_ServerUpdateUserData.restype = ctypes.c_int

    lib.QLR_Steamworks_ServerGetPublicIP.argtypes = []
    lib.QLR_Steamworks_ServerGetPublicIP.restype = ctypes.c_uint32

    lib.QLR_Steamworks_SendP2PPacket.argtypes = [
        ctypes.c_uint64,
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.c_int,
        ctypes.c_int,
    ]
    lib.QLR_Steamworks_SendP2PPacket.restype = ctypes.c_int

    lib.QLR_Steamworks_IsP2PPacketAvailable.argtypes = [
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_int,
    ]
    lib.QLR_Steamworks_IsP2PPacketAvailable.restype = ctypes.c_int

    lib.QLR_Steamworks_ReadP2PPacket.argtypes = [
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_uint64),
        ctypes.c_int,
    ]
    lib.QLR_Steamworks_ReadP2PPacket.restype = ctypes.c_int

    lib.QLR_Steamworks_AcceptP2PSession.argtypes = [ctypes.c_uint64]
    lib.QLR_Steamworks_AcceptP2PSession.restype = ctypes.c_int

    lib.QLR_Steamworks_ServerSendP2PPacket.argtypes = [
        ctypes.c_uint64,
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.c_int,
        ctypes.c_int,
    ]
    lib.QLR_Steamworks_ServerSendP2PPacket.restype = ctypes.c_int

    lib.QLR_Steamworks_ServerIsP2PPacketAvailable.argtypes = [
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_int,
    ]
    lib.QLR_Steamworks_ServerIsP2PPacketAvailable.restype = ctypes.c_int

    lib.QLR_Steamworks_ServerReadP2PPacket.argtypes = [
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_uint64),
        ctypes.c_int,
    ]
    lib.QLR_Steamworks_ServerReadP2PPacket.restype = ctypes.c_int

    lib.QLR_Steamworks_ServerGetNextOutgoingPacket.argtypes = [
        ctypes.c_void_p,
        ctypes.c_int,
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_uint16),
    ]
    lib.QLR_Steamworks_ServerGetNextOutgoingPacket.restype = ctypes.c_int

    lib.QLR_Steamworks_ServerAcceptP2PSession.argtypes = [ctypes.c_uint64]
    lib.QLR_Steamworks_ServerAcceptP2PSession.restype = ctypes.c_int

    lib.QLR_Steamworks_Shutdown.argtypes = []
    lib.QLR_Steamworks_Shutdown.restype = None

    if enabled:
        lib.QLR_SteamworksMock_Reset.argtypes = []
        lib.QLR_SteamworksMock_Reset.restype = None

        lib.QLR_SteamworksMock_PrimeState.argtypes = []
        lib.QLR_SteamworksMock_PrimeState.restype = None

        lib.QLR_SteamworksMock_SetLibraryAvailable.argtypes = [ctypes.c_int]
        lib.QLR_SteamworksMock_SetLibraryAvailable.restype = None

        lib.QLR_SteamworksMock_SetInitResult.argtypes = [ctypes.c_int]
        lib.QLR_SteamworksMock_SetInitResult.restype = None

        lib.QLR_SteamworksMock_SetSteamGameServerInitResult.argtypes = [ctypes.c_int]
        lib.QLR_SteamworksMock_SetSteamGameServerInitResult.restype = None

        lib.QLR_SteamworksMock_SetUserAvailable.argtypes = [ctypes.c_int]
        lib.QLR_SteamworksMock_SetUserAvailable.restype = None

        lib.QLR_SteamworksMock_SetTicket.argtypes = [ctypes.c_char_p, ctypes.c_uint32, ctypes.c_uint32]
        lib.QLR_SteamworksMock_SetTicket.restype = None
        lib.QLR_SteamworksMock_GetCancelledTicketHandle.argtypes = []
        lib.QLR_SteamworksMock_GetCancelledTicketHandle.restype = ctypes.c_uint32
        lib.QLR_SteamworksMock_GetCancelAuthTicketCalls.argtypes = []
        lib.QLR_SteamworksMock_GetCancelAuthTicketCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_SetAuthResult.argtypes = [ctypes.c_int]
        lib.QLR_SteamworksMock_SetAuthResult.restype = None

        lib.QLR_SteamworksMock_SetSteamId.argtypes = [ctypes.c_uint64]
        lib.QLR_SteamworksMock_SetSteamId.restype = None

        lib.QLR_SteamworksMock_SetLobbyOwnerId.argtypes = [ctypes.c_uint64]
        lib.QLR_SteamworksMock_SetLobbyOwnerId.restype = None

        lib.QLR_SteamworksMock_SetSteamGameServerPublicIP.argtypes = [ctypes.c_uint32]
        lib.QLR_SteamworksMock_SetSteamGameServerPublicIP.restype = None

        lib.QLR_SteamworksMock_SetSteamGameServerId.argtypes = [ctypes.c_uint64]
        lib.QLR_SteamworksMock_SetSteamGameServerId.restype = None

        lib.QLR_SteamworksMock_SetAvatarHandles.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]
        lib.QLR_SteamworksMock_SetAvatarHandles.restype = None

        lib.QLR_SteamworksMock_SetAvatarPixels.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.c_uint32,
        ]
        lib.QLR_SteamworksMock_SetAvatarPixels.restype = None

        lib.QLR_SteamworksMock_SetUGCItemState.argtypes = [ctypes.c_uint32]
        lib.QLR_SteamworksMock_SetUGCItemState.restype = None

        lib.QLR_SteamworksMock_SetUGCDownloadInfo.argtypes = [ctypes.c_uint64, ctypes.c_uint64]
        lib.QLR_SteamworksMock_SetUGCDownloadInfo.restype = None

        lib.QLR_SteamworksMock_SetSubscribedItems.argtypes = [ctypes.POINTER(ctypes.c_uint64), ctypes.c_uint32]
        lib.QLR_SteamworksMock_SetSubscribedItems.restype = None

        lib.QLR_SteamworksMock_SetUGCInstallInfo.argtypes = [ctypes.c_uint64, ctypes.c_uint64, ctypes.c_char_p, ctypes.c_uint32]
        lib.QLR_SteamworksMock_SetUGCInstallInfo.restype = None

        lib.QLR_SteamworksMock_GetOverlayCallCount.argtypes = []
        lib.QLR_SteamworksMock_GetOverlayCallCount.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetOverlayDialog.argtypes = []
        lib.QLR_SteamworksMock_GetOverlayDialog.restype = ctypes.c_char_p

        lib.QLR_SteamworksMock_GetOverlaySteamId.argtypes = []
        lib.QLR_SteamworksMock_GetOverlaySteamId.restype = ctypes.c_uint64

        lib.QLR_SteamworksMock_GetOverlayWebCallCount.argtypes = []
        lib.QLR_SteamworksMock_GetOverlayWebCallCount.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetOverlayWebUrl.argtypes = []
        lib.QLR_SteamworksMock_GetOverlayWebUrl.restype = ctypes.c_char_p

        lib.QLR_SteamworksMock_GetRichPresenceCallCount.argtypes = []
        lib.QLR_SteamworksMock_GetRichPresenceCallCount.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetRichPresenceKey.argtypes = []
        lib.QLR_SteamworksMock_GetRichPresenceKey.restype = ctypes.c_char_p

        lib.QLR_SteamworksMock_GetRichPresenceValue.argtypes = []
        lib.QLR_SteamworksMock_GetRichPresenceValue.restype = ctypes.c_char_p

        lib.QLR_SteamworksMock_GetSteamGameServerInitCalls.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerInitCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerShutdownCalls.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerShutdownCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerLastInitIP.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerLastInitIP.restype = ctypes.c_uint32

        lib.QLR_SteamworksMock_GetSteamGameServerLastInitGamePort.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerLastInitGamePort.restype = ctypes.c_uint16

        lib.QLR_SteamworksMock_GetSteamGameServerLastInitServerMode.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerLastInitServerMode.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerLastInitVersion.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerLastInitVersion.restype = ctypes.c_char_p

        lib.QLR_SteamworksMock_GetSteamGameServerCallbackCalls.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerCallbackCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerHeartbeatCalls.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerHeartbeatCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerLastHeartbeatEnabled.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerLastHeartbeatEnabled.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerDedicatedCalls.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerDedicatedCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerLastDedicated.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerLastDedicated.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerLogOnCalls.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerLogOnCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerLogOnAnonymousCalls.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerLogOnAnonymousCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerProductCalls.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerProductCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerGameDirCalls.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerGameDirCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerGameDescriptionCalls.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerGameDescriptionCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerMaxPlayerCountCalls.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerMaxPlayerCountCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerBotPlayerCountCalls.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerBotPlayerCountCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerServerNameCalls.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerServerNameCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerMapNameCalls.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerMapNameCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerPasswordCalls.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerPasswordCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerGameTagsCalls.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerGameTagsCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerUserDataCalls.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerUserDataCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerKeyValueCalls.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerKeyValueCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerLastAccount.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerLastAccount.restype = ctypes.c_char_p

        lib.QLR_SteamworksMock_GetSteamGameServerLastKey.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerLastKey.restype = ctypes.c_char_p

        lib.QLR_SteamworksMock_GetSteamGameServerLastProduct.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerLastProduct.restype = ctypes.c_char_p

        lib.QLR_SteamworksMock_GetSteamGameServerLastGameDir.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerLastGameDir.restype = ctypes.c_char_p

        lib.QLR_SteamworksMock_GetSteamGameServerLastGameDescription.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerLastGameDescription.restype = ctypes.c_char_p

        lib.QLR_SteamworksMock_GetSteamGameServerLastServerName.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerLastServerName.restype = ctypes.c_char_p

        lib.QLR_SteamworksMock_GetSteamGameServerLastMapName.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerLastMapName.restype = ctypes.c_char_p

        lib.QLR_SteamworksMock_GetSteamGameServerLastGameTags.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerLastGameTags.restype = ctypes.c_char_p

        lib.QLR_SteamworksMock_GetSteamGameServerLastUserDataName.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerLastUserDataName.restype = ctypes.c_char_p

        lib.QLR_SteamworksMock_GetSteamGameServerLastUserDataId.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerLastUserDataId.restype = ctypes.c_uint64

        lib.QLR_SteamworksMock_GetSteamGameServerLastUserDataScore.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerLastUserDataScore.restype = ctypes.c_uint32

        lib.QLR_SteamworksMock_GetSteamGameServerLastMaxPlayerCount.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerLastMaxPlayerCount.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerLastBotPlayerCount.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerLastBotPlayerCount.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerLastPasswordProtected.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerLastPasswordProtected.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerLastValue.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerLastValue.restype = ctypes.c_char_p

        lib.QLR_SteamworksMock_GetLobbyCreateCalls.argtypes = []
        lib.QLR_SteamworksMock_GetLobbyCreateCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetLobbyLeaveCalls.argtypes = []
        lib.QLR_SteamworksMock_GetLobbyLeaveCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetLobbySetServerCalls.argtypes = []
        lib.QLR_SteamworksMock_GetLobbySetServerCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetFavoriteAddCalls.argtypes = []
        lib.QLR_SteamworksMock_GetFavoriteAddCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetFavoriteRemoveCalls.argtypes = []
        lib.QLR_SteamworksMock_GetFavoriteRemoveCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetLobbyJoinCalls.argtypes = []
        lib.QLR_SteamworksMock_GetLobbyJoinCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetLobbyInviteCalls.argtypes = []
        lib.QLR_SteamworksMock_GetLobbyInviteCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetLobbyUserInviteCalls.argtypes = []
        lib.QLR_SteamworksMock_GetLobbyUserInviteCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetLobbySayCalls.argtypes = []
        lib.QLR_SteamworksMock_GetLobbySayCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetUserStatsRequestCalls.argtypes = []
        lib.QLR_SteamworksMock_GetUserStatsRequestCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetLobbyCreateType.argtypes = []
        lib.QLR_SteamworksMock_GetLobbyCreateType.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetLobbyCreateMaxMembers.argtypes = []
        lib.QLR_SteamworksMock_GetLobbyCreateMaxMembers.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetLobbyLeaveId.argtypes = []
        lib.QLR_SteamworksMock_GetLobbyLeaveId.restype = ctypes.c_uint64

        lib.QLR_SteamworksMock_GetLobbyJoinId.argtypes = []
        lib.QLR_SteamworksMock_GetLobbyJoinId.restype = ctypes.c_uint64

        lib.QLR_SteamworksMock_GetLobbySetServerId.argtypes = []
        lib.QLR_SteamworksMock_GetLobbySetServerId.restype = ctypes.c_uint64

        lib.QLR_SteamworksMock_GetLobbyInviteId.argtypes = []
        lib.QLR_SteamworksMock_GetLobbyInviteId.restype = ctypes.c_uint64

        lib.QLR_SteamworksMock_GetLobbyUserInviteLobbyId.argtypes = []
        lib.QLR_SteamworksMock_GetLobbyUserInviteLobbyId.restype = ctypes.c_uint64

        lib.QLR_SteamworksMock_GetLobbyUserInviteTargetId.argtypes = []
        lib.QLR_SteamworksMock_GetLobbyUserInviteTargetId.restype = ctypes.c_uint64

        lib.QLR_SteamworksMock_GetLobbySetServerIp.argtypes = []
        lib.QLR_SteamworksMock_GetLobbySetServerIp.restype = ctypes.c_uint32

        lib.QLR_SteamworksMock_GetLobbySetServerPort.argtypes = []
        lib.QLR_SteamworksMock_GetLobbySetServerPort.restype = ctypes.c_uint16

        lib.QLR_SteamworksMock_GetFavoriteLastAppId.argtypes = []
        lib.QLR_SteamworksMock_GetFavoriteLastAppId.restype = ctypes.c_uint32

        lib.QLR_SteamworksMock_GetFavoriteLastIp.argtypes = []
        lib.QLR_SteamworksMock_GetFavoriteLastIp.restype = ctypes.c_uint32

        lib.QLR_SteamworksMock_GetFavoriteLastConnPort.argtypes = []
        lib.QLR_SteamworksMock_GetFavoriteLastConnPort.restype = ctypes.c_uint16

        lib.QLR_SteamworksMock_GetFavoriteLastQueryPort.argtypes = []
        lib.QLR_SteamworksMock_GetFavoriteLastQueryPort.restype = ctypes.c_uint16

        lib.QLR_SteamworksMock_GetFavoriteLastFlags.argtypes = []
        lib.QLR_SteamworksMock_GetFavoriteLastFlags.restype = ctypes.c_uint32

        lib.QLR_SteamworksMock_GetFavoriteLastPlayed.argtypes = []
        lib.QLR_SteamworksMock_GetFavoriteLastPlayed.restype = ctypes.c_uint32

        for name in [
            "QLR_SteamworksMock_GetP2PSendCalls",
            "QLR_SteamworksMock_GetP2PLastSendType",
            "QLR_SteamworksMock_GetP2PLastSendChannel",
            "QLR_SteamworksMock_GetP2PAvailableCalls",
            "QLR_SteamworksMock_GetP2PLastAvailableChannel",
            "QLR_SteamworksMock_GetP2PReadCalls",
            "QLR_SteamworksMock_GetP2PLastReadChannel",
            "QLR_SteamworksMock_GetP2PAcceptCalls",
            "QLR_SteamworksMock_GetServerP2PSendCalls",
            "QLR_SteamworksMock_GetServerP2PLastSendType",
            "QLR_SteamworksMock_GetServerP2PLastSendChannel",
            "QLR_SteamworksMock_GetServerP2PAvailableCalls",
            "QLR_SteamworksMock_GetServerP2PLastAvailableChannel",
            "QLR_SteamworksMock_GetServerP2PReadCalls",
            "QLR_SteamworksMock_GetServerP2PLastReadChannel",
            "QLR_SteamworksMock_GetServerP2PAcceptCalls",
            "QLR_SteamworksMock_GetServerOutgoingPacketCalls",
        ]:
            getattr(lib, name).argtypes = []
            getattr(lib, name).restype = ctypes.c_int

        for name in [
            "QLR_SteamworksMock_GetP2PLastSendSteamId",
            "QLR_SteamworksMock_GetP2PLastAcceptSteamId",
            "QLR_SteamworksMock_GetServerP2PLastSendSteamId",
            "QLR_SteamworksMock_GetServerP2PLastAcceptSteamId",
        ]:
            getattr(lib, name).argtypes = []
            getattr(lib, name).restype = ctypes.c_uint64

        for name in [
            "QLR_SteamworksMock_GetP2PLastSendLength",
            "QLR_SteamworksMock_GetServerP2PLastSendLength",
        ]:
            getattr(lib, name).argtypes = []
            getattr(lib, name).restype = ctypes.c_uint32

        lib.QLR_SteamworksMock_GetP2PLastSendByte.argtypes = [ctypes.c_int]
        lib.QLR_SteamworksMock_GetP2PLastSendByte.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetServerP2PLastSendByte.argtypes = [ctypes.c_int]
        lib.QLR_SteamworksMock_GetServerP2PLastSendByte.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetLobbySetServerGameServerId.argtypes = []
        lib.QLR_SteamworksMock_GetLobbySetServerGameServerId.restype = ctypes.c_uint64

        lib.QLR_SteamworksMock_GetLobbySayId.argtypes = []
        lib.QLR_SteamworksMock_GetLobbySayId.restype = ctypes.c_uint64

        lib.QLR_SteamworksMock_GetLobbySayMessage.argtypes = []
        lib.QLR_SteamworksMock_GetLobbySayMessage.restype = ctypes.c_char_p

        lib.QLR_SteamworksMock_GetUserStatsRequestId.argtypes = []
        lib.QLR_SteamworksMock_GetUserStatsRequestId.restype = ctypes.c_uint64

        lib.QLR_SteamworksMock_GetGameInviteCalls.argtypes = []
        lib.QLR_SteamworksMock_GetGameInviteCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetGameInviteTargetId.argtypes = []
        lib.QLR_SteamworksMock_GetGameInviteTargetId.restype = ctypes.c_uint64

        lib.QLR_SteamworksMock_GetGameInviteConnectString.argtypes = []
        lib.QLR_SteamworksMock_GetGameInviteConnectString.restype = ctypes.c_char_p

        for name in [
            "QLR_SteamworksMock_GetServerBrowserInternetCalls",
            "QLR_SteamworksMock_GetServerBrowserLanCalls",
            "QLR_SteamworksMock_GetServerBrowserFriendsCalls",
            "QLR_SteamworksMock_GetServerBrowserFavoritesCalls",
            "QLR_SteamworksMock_GetServerBrowserHistoryCalls",
            "QLR_SteamworksMock_GetServerBrowserReleaseCalls",
            "QLR_SteamworksMock_GetServerBrowserRefreshCalls",
            "QLR_SteamworksMock_GetServerBrowserGetDetailsCalls",
            "QLR_SteamworksMock_GetServerBrowserPingCalls",
            "QLR_SteamworksMock_GetServerBrowserPlayersCalls",
            "QLR_SteamworksMock_GetServerBrowserRulesCalls",
            "QLR_SteamworksMock_GetServerBrowserCancelQueryCalls",
            "QLR_SteamworksMock_GetServerBrowserPingOrder",
            "QLR_SteamworksMock_GetServerBrowserPlayersOrder",
            "QLR_SteamworksMock_GetServerBrowserRulesOrder",
            "QLR_SteamworksMock_GetServerBrowserLastIndex",
            "QLR_SteamworksMock_GetServerBrowserLastCancelQuery",
        ]:
            getattr(lib, name).argtypes = []
            getattr(lib, name).restype = ctypes.c_int

        for name in [
            "QLR_SteamworksMock_GetServerBrowserLastAppId",
            "QLR_SteamworksMock_GetServerBrowserLastFilterCount",
            "QLR_SteamworksMock_GetServerBrowserLastIp",
        ]:
            getattr(lib, name).argtypes = []
            getattr(lib, name).restype = ctypes.c_uint32

        lib.QLR_SteamworksMock_GetServerBrowserLastPort.argtypes = []
        lib.QLR_SteamworksMock_GetServerBrowserLastPort.restype = ctypes.c_uint16

        for name in [
            "QLR_SteamworksMock_GetServerBrowserLastResponse",
            "QLR_SteamworksMock_GetServerBrowserLastRequest",
            "QLR_SteamworksMock_GetServerBrowserLastPingResponse",
            "QLR_SteamworksMock_GetServerBrowserLastPlayersResponse",
            "QLR_SteamworksMock_GetServerBrowserLastRulesResponse",
        ]:
            getattr(lib, name).argtypes = []
            getattr(lib, name).restype = ctypes.c_size_t

        lib.QLR_SteamworksMock_GetServerBrowserLastFilterKey.argtypes = []
        lib.QLR_SteamworksMock_GetServerBrowserLastFilterKey.restype = ctypes.c_char_p

        lib.QLR_SteamworksMock_GetServerBrowserLastFilterValue.argtypes = []
        lib.QLR_SteamworksMock_GetServerBrowserLastFilterValue.restype = ctypes.c_char_p

        lib.QLR_SteamworksMock_GetUGCSubscribeCalls.argtypes = []
        lib.QLR_SteamworksMock_GetUGCSubscribeCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetUGCUnsubscribeCalls.argtypes = []
        lib.QLR_SteamworksMock_GetUGCUnsubscribeCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetUGCDownloadCalls.argtypes = []
        lib.QLR_SteamworksMock_GetUGCDownloadCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerUGCSubscribeCalls.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerUGCSubscribeCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerUGCUnsubscribeCalls.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerUGCUnsubscribeCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerUGCDownloadCalls.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerUGCDownloadCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerUGCLastItemId.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerUGCLastItemId.restype = ctypes.c_uint64

        lib.QLR_SteamworksMock_GetSteamGameServerUGCLastHighPriority.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerUGCLastHighPriority.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetUGCLastItemId.argtypes = []
        lib.QLR_SteamworksMock_GetUGCLastItemId.restype = ctypes.c_uint64

        lib.QLR_SteamworksMock_GetUGCLastHighPriority.argtypes = []
        lib.QLR_SteamworksMock_GetUGCLastHighPriority.restype = ctypes.c_int

        lib.QLR_Steamworks_RequestAllUGCQuery.argtypes = [ctypes.c_uint32]
        lib.QLR_Steamworks_RequestAllUGCQuery.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetUGCCreateQueryCalls.argtypes = []
        lib.QLR_SteamworksMock_GetUGCCreateQueryCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetUGCSendQueryCalls.argtypes = []
        lib.QLR_SteamworksMock_GetUGCSendQueryCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetUGCReleaseQueryCalls.argtypes = []
        lib.QLR_SteamworksMock_GetUGCReleaseQueryCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetUGCLastQueryType.argtypes = []
        lib.QLR_SteamworksMock_GetUGCLastQueryType.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetUGCLastMatchingType.argtypes = []
        lib.QLR_SteamworksMock_GetUGCLastMatchingType.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetUGCLastCreatorAppId.argtypes = []
        lib.QLR_SteamworksMock_GetUGCLastCreatorAppId.restype = ctypes.c_uint32

        lib.QLR_SteamworksMock_GetUGCLastConsumerAppId.argtypes = []
        lib.QLR_SteamworksMock_GetUGCLastConsumerAppId.restype = ctypes.c_uint32

        lib.QLR_SteamworksMock_GetUGCLastFilter.argtypes = []
        lib.QLR_SteamworksMock_GetUGCLastFilter.restype = ctypes.c_uint32

        lib.QLR_SteamworksMock_GetUGCLastQueryHandle.argtypes = []
        lib.QLR_SteamworksMock_GetUGCLastQueryHandle.restype = ctypes.c_uint64

        lib.QLR_SteamworksMock_GetUGCLastSentQueryHandle.argtypes = []
        lib.QLR_SteamworksMock_GetUGCLastSentQueryHandle.restype = ctypes.c_uint64

        lib.QLR_SteamworksMock_GetUGCLastReleasedQueryHandle.argtypes = []
        lib.QLR_SteamworksMock_GetUGCLastReleasedQueryHandle.restype = ctypes.c_uint64

        lib.QLR_SteamworksMock_SetAppId.argtypes = [ctypes.c_uint32]
        lib.QLR_SteamworksMock_SetAppId.restype = None

        lib.QLR_SteamworksMock_SetServerBrowserServerName.argtypes = [ctypes.c_char_p]
        lib.QLR_SteamworksMock_SetServerBrowserServerName.restype = None

        lib.QLR_SteamworksMock_SetServerBrowserRequestResult.argtypes = [ctypes.c_size_t]
        lib.QLR_SteamworksMock_SetServerBrowserRequestResult.restype = None

        lib.QLR_SteamworksMock_SetServerBrowserDetailQueryResults.argtypes = [
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
        ]
        lib.QLR_SteamworksMock_SetServerBrowserDetailQueryResults.restype = None

        lib.QLR_SteamworksMock_SetLobbyChatEntryMessage.argtypes = [ctypes.c_char_p]
        lib.QLR_SteamworksMock_SetLobbyChatEntryMessage.restype = None

        lib.QLR_SteamworksMock_SetFavoriteResults.argtypes = [ctypes.c_int, ctypes.c_int]
        lib.QLR_SteamworksMock_SetFavoriteResults.restype = None

        lib.QLR_SteamworksMock_SetP2PResults.argtypes = [
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
        ]
        lib.QLR_SteamworksMock_SetP2PResults.restype = None

        lib.QLR_SteamworksMock_SetP2PReadPacket.argtypes = [
            ctypes.c_uint64,
            ctypes.c_void_p,
            ctypes.c_uint32,
        ]
        lib.QLR_SteamworksMock_SetP2PReadPacket.restype = None

        lib.QLR_SteamworksMock_SetServerP2PResults.argtypes = [
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
        ]
        lib.QLR_SteamworksMock_SetServerP2PResults.restype = None

        lib.QLR_SteamworksMock_SetServerP2PReadPacket.argtypes = [
            ctypes.c_uint64,
            ctypes.c_void_p,
            ctypes.c_uint32,
        ]
        lib.QLR_SteamworksMock_SetServerP2PReadPacket.restype = None

        lib.QLR_SteamworksMock_SetServerOutgoingPacket.argtypes = [
            ctypes.c_void_p,
            ctypes.c_int,
            ctypes.c_uint32,
            ctypes.c_uint16,
        ]
        lib.QLR_SteamworksMock_SetServerOutgoingPacket.restype = None

        lib.QLR_Steamworks_RegisterHarnessCallbacks.argtypes = []
        lib.QLR_Steamworks_RegisterHarnessCallbacks.restype = ctypes.c_int

        lib.QLR_Steamworks_UnregisterHarnessCallbacks.argtypes = []
        lib.QLR_Steamworks_UnregisterHarnessCallbacks.restype = None

        lib.QLR_Steamworks_RegisterServerHarnessCallbacks.argtypes = []
        lib.QLR_Steamworks_RegisterServerHarnessCallbacks.restype = ctypes.c_int

        lib.QLR_Steamworks_UnregisterServerHarnessCallbacks.argtypes = []
        lib.QLR_Steamworks_UnregisterServerHarnessCallbacks.restype = None

        lib.QLR_Steamworks_BindUGCQueryCallResult.argtypes = [ctypes.c_uint64]
        lib.QLR_Steamworks_BindUGCQueryCallResult.restype = ctypes.c_int

        lib.QLR_Steamworks_RunCallbackPump.argtypes = []
        lib.QLR_Steamworks_RunCallbackPump.restype = None

        lib.QLR_Steamworks_RunServerCallbackPump.argtypes = []
        lib.QLR_Steamworks_RunServerCallbackPump.restype = None

        lib.QLR_SteamworksMock_QueueRichPresenceJoinRequested.argtypes = [ctypes.c_uint64, ctypes.c_char_p]
        lib.QLR_SteamworksMock_QueueRichPresenceJoinRequested.restype = ctypes.c_int

        lib.QLR_SteamworksMock_QueueAvatarImageLoaded.argtypes = [ctypes.c_uint64, ctypes.c_int, ctypes.c_int, ctypes.c_int]
        lib.QLR_SteamworksMock_QueueAvatarImageLoaded.restype = ctypes.c_int

        lib.QLR_SteamworksMock_QueueLobbyEnter.argtypes = [ctypes.c_uint64, ctypes.c_uint32, ctypes.c_int, ctypes.c_uint32]
        lib.QLR_SteamworksMock_QueueLobbyEnter.restype = ctypes.c_int

        lib.QLR_SteamworksMock_QueueMicroAuthorizationResponse.argtypes = [ctypes.c_uint32, ctypes.c_uint64, ctypes.c_int]
        lib.QLR_SteamworksMock_QueueMicroAuthorizationResponse.restype = ctypes.c_int

        lib.QLR_SteamworksMock_QueueItemInstalled.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
        lib.QLR_SteamworksMock_QueueItemInstalled.restype = ctypes.c_int

        lib.QLR_SteamworksMock_QueueDownloadItemResult.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_int,
        ]
        lib.QLR_SteamworksMock_QueueDownloadItemResult.restype = ctypes.c_int

        lib.QLR_SteamworksMock_QueueUGCQueryCompleted.argtypes = [
            ctypes.c_uint64,
            ctypes.c_uint64,
            ctypes.c_int,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_int,
        ]
        lib.QLR_SteamworksMock_QueueUGCQueryCompleted.restype = ctypes.c_int

        lib.QLR_SteamworksMock_QueueValidateAuthTicketResponse.argtypes = [ctypes.c_uint64, ctypes.c_uint64, ctypes.c_int]
        lib.QLR_SteamworksMock_QueueValidateAuthTicketResponse.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetRegisterCallbackCalls.argtypes = []
        lib.QLR_SteamworksMock_GetRegisterCallbackCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetUnregisterCallbackCalls.argtypes = []
        lib.QLR_SteamworksMock_GetUnregisterCallbackCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetRegisterCallResultCalls.argtypes = []
        lib.QLR_SteamworksMock_GetRegisterCallResultCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetUnregisterCallResultCalls.argtypes = []
        lib.QLR_SteamworksMock_GetUnregisterCallResultCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetClientCallbackCaptureCount.argtypes = []
        lib.QLR_SteamworksMock_GetClientCallbackCaptureCount.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetLastCallbackKind.argtypes = []
        lib.QLR_SteamworksMock_GetLastCallbackKind.restype = ctypes.c_char_p

        lib.QLR_SteamworksMock_GetLastCallbackText.argtypes = []
        lib.QLR_SteamworksMock_GetLastCallbackText.restype = ctypes.c_char_p

        lib.QLR_SteamworksMock_GetLastCallbackId.argtypes = []
        lib.QLR_SteamworksMock_GetLastCallbackId.restype = ctypes.c_uint64

        lib.QLR_SteamworksMock_GetLastCallbackAuxId.argtypes = []
        lib.QLR_SteamworksMock_GetLastCallbackAuxId.restype = ctypes.c_uint64

        lib.QLR_SteamworksMock_GetLastCallbackAppId.argtypes = []
        lib.QLR_SteamworksMock_GetLastCallbackAppId.restype = ctypes.c_uint32

        lib.QLR_SteamworksMock_GetLastCallbackResult.argtypes = []
        lib.QLR_SteamworksMock_GetLastCallbackResult.restype = ctypes.c_int

    return lib, enabled


def test_request_produces_expected_ticket(steamworks_harness: tuple[ctypes.CDLL, bool]) -> None:
    lib, enabled = steamworks_harness

    ticket_buffer = ctypes.create_string_buffer(TICKET_BUFFER)
    ticket_length = ctypes.c_int()
    ticket_handle = ctypes.c_uint32()

    if enabled:
        lib.QLR_SteamworksMock_Reset()
        lib.QLR_SteamworksMock_PrimeState()

    result = lib.QLR_Steamworks_Request(
        ticket_buffer,
        ctypes.sizeof(ticket_buffer),
        ctypes.byref(ticket_length),
        ctypes.byref(ticket_handle),
    )

    if not enabled:
        assert result == 0
        return

    assert result != 0
    assert ticket_buffer.value.decode() == "12345678"
    assert ticket_length.value == 8
    assert ticket_handle.value == 1


def test_validate_maps_auth_results(steamworks_harness: tuple[ctypes.CDLL, bool]) -> None:
    lib, enabled = steamworks_harness

    if not enabled:
        response = AuthResponse()
        assert lib.QLR_Steamworks_Validate(b"deadbeef", ctypes.byref(response)) == 0
        return

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()

    raw_ticket = ctypes.create_string_buffer(b"\xAA\xBB\xCC")
    lib.QLR_SteamworksMock_SetTicket(raw_ticket, 3, 99)

    ticket_buffer = ctypes.create_string_buffer(TICKET_BUFFER)
    ticket_length = ctypes.c_int()
    ticket_handle = ctypes.c_uint32()

    assert lib.QLR_Steamworks_Request(
        ticket_buffer,
        ctypes.sizeof(ticket_buffer),
        ctypes.byref(ticket_length),
        ctypes.byref(ticket_handle),
    )

    ticket_hex = ticket_buffer.value
    assert ticket_hex == b"aabbcc"
    assert ticket_length.value == 6
    assert ticket_handle.value == 99

    lib.QLR_SteamworksMock_SetAuthResult(BEGIN_AUTH_OK)
    success = AuthResponse()
    assert lib.QLR_Steamworks_Validate(ticket_hex, ctypes.byref(success))
    assert success.result == QL_AUTH_RESULT_ACCEPTED
    assert success.outcome == QL_AUTH_OUTCOME_SUCCESS
    assert success.message.decode() == "Steam ticket accepted"

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()
    lib.QLR_SteamworksMock_SetTicket(raw_ticket, 3, 77)
    lib.QLR_SteamworksMock_SetAuthResult(BEGIN_AUTH_INVALID_TICKET)

    denied = AuthResponse()
    assert lib.QLR_Steamworks_Validate(ticket_hex, ctypes.byref(denied))
    assert denied.result == QL_AUTH_RESULT_DENIED
    assert denied.outcome == QL_AUTH_OUTCOME_FAILURE
    assert "invalid" in denied.message.decode().lower()

    lib.QLR_SteamworksMock_SetLibraryAvailable(0)
    lib.QLR_SteamworksMock_SetInitResult(0)
    lib.QLR_SteamworksMock_PrimeState()

    runtime_missing = AuthResponse()
    assert lib.QLR_Steamworks_Validate(ticket_hex, ctypes.byref(runtime_missing))
    assert runtime_missing.result == QL_AUTH_RESULT_ERROR
    assert runtime_missing.outcome == QL_AUTH_OUTCOME_FAILURE
    assert "runtime" in runtime_missing.message.decode().lower()


@pytest.mark.parametrize(
    ("begin_result", "expected_result", "expected_outcome", "message_fragment"),
    [
        (BEGIN_AUTH_DUPLICATE_REQUEST, QL_AUTH_RESULT_PENDING, QL_AUTH_OUTCOME_RETRY, "already processing"),
        (BEGIN_AUTH_INVALID_VERSION, QL_AUTH_RESULT_DENIED, QL_AUTH_OUTCOME_FAILURE, "version mismatch"),
        (BEGIN_AUTH_GAME_MISMATCH, QL_AUTH_RESULT_DENIED, QL_AUTH_OUTCOME_FAILURE, "another game"),
        (BEGIN_AUTH_EXPIRED_TICKET, QL_AUTH_RESULT_PENDING, QL_AUTH_OUTCOME_RETRY, "expired"),
        (BEGIN_AUTH_UNKNOWN, QL_AUTH_RESULT_ERROR, QL_AUTH_OUTCOME_FAILURE, "unknown"),
    ],
)
def test_validate_maps_edge_auth_results_without_optimistic_acceptance(
    steamworks_harness: tuple[ctypes.CDLL, bool],
    begin_result: int,
    expected_result: int,
    expected_outcome: int,
    message_fragment: str,
) -> None:
    lib, enabled = steamworks_harness

    if not enabled:
        return

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()
    lib.QLR_SteamworksMock_SetAuthResult(begin_result)

    response = AuthResponse()
    assert lib.QLR_Steamworks_Validate(b"12345678", ctypes.byref(response))
    assert response.result == expected_result
    assert response.outcome == expected_outcome
    assert message_fragment in response.message.decode().lower()


@pytest.mark.parametrize(
    ("steam_id", "owner_id", "auth_response"),
    [
        (0x0110000100ABCDEF, 0x0110000100ABCDEF, AUTH_RESPONSE_OK),
        (0x0110000100ABCDEF, 0, AUTH_RESPONSE_OK),
        (0x0110000100ABCDEF, 0x0110000100123456, AUTH_RESPONSE_OK),
        (0x0110000100ABCDEF, 0x0110000100123456, AUTH_RESPONSE_VAC_BANNED),
    ],
)
def test_server_validate_auth_ticket_response_dispatch_matrix_from_server_callback_pump(
    steamworks_harness: tuple[ctypes.CDLL, bool],
    steam_id: int,
    owner_id: int,
    auth_response: int,
) -> None:
    lib, enabled = steamworks_harness

    if not enabled:
        return

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()

    assert lib.QLR_Steamworks_ServerInit(0x01020304, 27960, 1, 1)
    assert lib.QLR_Steamworks_RegisterServerHarnessCallbacks()
    assert lib.QLR_SteamworksMock_GetRegisterCallbackCalls() == 5
    assert lib.QLR_SteamworksMock_QueueValidateAuthTicketResponse(
        steam_id,
        owner_id,
        auth_response,
    )

    assert lib.QLR_SteamworksMock_GetClientCallbackCaptureCount() == 0

    lib.QLR_Steamworks_RunServerCallbackPump()

    assert lib.QLR_SteamworksMock_GetSteamGameServerCallbackCalls() == 1
    assert lib.QLR_SteamworksMock_GetClientCallbackCaptureCount() == 1
    assert lib.QLR_SteamworksMock_GetLastCallbackKind() == b"server_validate_auth"
    assert lib.QLR_SteamworksMock_GetLastCallbackId() == steam_id
    assert lib.QLR_SteamworksMock_GetLastCallbackAuxId() == owner_id
    assert lib.QLR_SteamworksMock_GetLastCallbackResult() == auth_response

    lib.QLR_Steamworks_UnregisterServerHarnessCallbacks()
    assert lib.QLR_SteamworksMock_GetUnregisterCallbackCalls() == 5


def test_cancel_ticket_routes_to_steam_user_cancel_path(steamworks_harness: tuple[ctypes.CDLL, bool]) -> None:
    lib, enabled = steamworks_harness

    if not enabled:
        assert lib.QLR_Steamworks_CancelTicket(99) == 0
        return

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()
    assert lib.QLR_Steamworks_Init() != 0

    assert lib.QLR_Steamworks_CancelTicket(99) != 0
    assert lib.QLR_SteamworksMock_GetCancelAuthTicketCalls() == 1
    assert lib.QLR_SteamworksMock_GetCancelledTicketHandle() == 99


def test_load_avatar_returns_expected_rgba_payload(steamworks_harness: tuple[ctypes.CDLL, bool]) -> None:
    lib, enabled = steamworks_harness

    out_width = ctypes.c_uint32()
    out_height = ctypes.c_uint32()
    out_length = ctypes.c_uint32()
    buffer = (ctypes.c_uint8 * AVATAR_BUFFER)()

    if not enabled:
        assert not lib.QLR_Steamworks_LoadAvatar(
            0x89ABCDEF,
            0x01234567,
            AVATAR_SIZE_LARGE,
            buffer,
            len(buffer),
            ctypes.byref(out_width),
            ctypes.byref(out_height),
            ctypes.byref(out_length),
        )
        return

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()

    pixels = (ctypes.c_uint8 * 16)(
        0x10, 0x20, 0x30, 0x40,
        0x50, 0x60, 0x70, 0x80,
        0x90, 0xA0, 0xB0, 0xC0,
        0xD0, 0xE0, 0xF0, 0xFF,
    )
    lib.QLR_SteamworksMock_SetAvatarHandles(0, 0, 77)
    lib.QLR_SteamworksMock_SetAvatarPixels(2, 2, pixels, len(pixels))

    assert lib.QLR_Steamworks_LoadAvatar(
        0x89ABCDEF,
        0x01234567,
        AVATAR_SIZE_LARGE,
        buffer,
        len(buffer),
        ctypes.byref(out_width),
        ctypes.byref(out_height),
        ctypes.byref(out_length),
    )
    assert out_width.value == 2
    assert out_height.value == 2
    assert out_length.value == 16
    assert bytes(buffer[: out_length.value]) == bytes(pixels)


def test_load_avatar_uses_requested_size_slot(steamworks_harness: tuple[ctypes.CDLL, bool]) -> None:
    lib, enabled = steamworks_harness

    if not enabled:
        return

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()
    lib.QLR_SteamworksMock_SetAvatarHandles(0, 55, 0)

    pixels = (ctypes.c_uint8 * 16)(
        0x01, 0x02, 0x03, 0x04,
        0x05, 0x06, 0x07, 0x08,
        0x09, 0x0A, 0x0B, 0x0C,
        0x0D, 0x0E, 0x0F, 0x10,
    )
    lib.QLR_SteamworksMock_SetAvatarPixels(2, 2, pixels, len(pixels))

    buffer = (ctypes.c_uint8 * AVATAR_BUFFER)()
    out_width = ctypes.c_uint32()
    out_height = ctypes.c_uint32()
    out_length = ctypes.c_uint32()

    assert lib.QLR_Steamworks_LoadAvatar(
        0x11111111,
        0x22222222,
        AVATAR_SIZE_MEDIUM,
        buffer,
        len(buffer),
        ctypes.byref(out_width),
        ctypes.byref(out_height),
        ctypes.byref(out_length),
    )

    assert not lib.QLR_Steamworks_LoadAvatar(
        0x11111111,
        0x22222222,
        AVATAR_SIZE_LARGE,
        buffer,
        len(buffer),
        ctypes.byref(out_width),
        ctypes.byref(out_height),
        ctypes.byref(out_length),
    )


def test_activate_overlay_routes_dialog_and_identity(steamworks_harness: tuple[ctypes.CDLL, bool]) -> None:
    lib, enabled = steamworks_harness

    if not enabled:
        assert not lib.QLR_Steamworks_ActivateOverlay(b"steamid", 0x89ABCDEF, 0x01234567)
        return

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()

    assert lib.QLR_Steamworks_ActivateOverlay(b"friendadd", 0x89ABCDEF, 0x01234567)
    assert lib.QLR_SteamworksMock_GetOverlayCallCount() == 1
    assert lib.QLR_SteamworksMock_GetOverlayDialog() == b"friendadd"
    assert lib.QLR_SteamworksMock_GetOverlaySteamId() == 0x0123456789ABCDEF


def test_activate_overlay_to_web_page_routes_url(steamworks_harness: tuple[ctypes.CDLL, bool]) -> None:
    lib, enabled = steamworks_harness

    if not enabled:
        assert not lib.QLR_Steamworks_ActivateOverlayToWebPage(b"https://example.com/ql")
        return

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()

    assert lib.QLR_Steamworks_ActivateOverlayToWebPage(b"https://example.com/ql")
    assert lib.QLR_SteamworksMock_GetOverlayWebCallCount() == 1
    assert lib.QLR_SteamworksMock_GetOverlayWebUrl() == b"https://example.com/ql"

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()

    assert lib.QLR_Steamworks_ActivateOverlayToWebPage(b"")
    assert lib.QLR_SteamworksMock_GetOverlayWebCallCount() == 1
    assert lib.QLR_SteamworksMock_GetOverlayWebUrl() == b""


def test_server_browser_helpers_use_mapped_matchmaking_servers_slots(steamworks_harness: tuple[ctypes.CDLL, bool]) -> None:
    lib, enabled = steamworks_harness

    if not enabled:
        ping_query = ctypes.c_int(99)
        players_query = ctypes.c_int(99)
        rules_query = ctypes.c_int(99)

        assert not lib.QLR_Steamworks_HasServerBrowserInterface()
        assert lib.QLR_Steamworks_GetServerBrowserRequestModeLabel(0) == b"internet"
        assert lib.QLR_Steamworks_GetServerBrowserRequestModeLabel(1) == b"lan"
        assert lib.QLR_Steamworks_GetServerBrowserRequestModeLabel(2) == b"friends"
        assert lib.QLR_Steamworks_GetServerBrowserRequestModeLabel(3) == b"favorites"
        assert lib.QLR_Steamworks_GetServerBrowserRequestModeLabel(4) == b"history"
        assert lib.QLR_Steamworks_GetServerBrowserRequestModeLabel(99) == b"internet"
        assert lib.QLR_Steamworks_ServerBrowserRequestModeUsesGamedirFilter(0)
        assert not lib.QLR_Steamworks_ServerBrowserRequestModeUsesGamedirFilter(1)
        assert lib.QLR_Steamworks_ServerBrowserRequestModeUsesGamedirFilter(2)
        assert lib.QLR_Steamworks_ServerBrowserRequestModeUsesGamedirFilter(3)
        assert lib.QLR_Steamworks_ServerBrowserRequestModeUsesGamedirFilter(4)
        assert lib.QLR_Steamworks_ServerBrowserRequestModeUsesGamedirFilter(99)
        assert lib.QLR_Steamworks_RequestServerList(0, 0xABCDEF) == 0
        assert lib.QLR_Steamworks_GetServerListDetails(0x12345678, 1) == 0
        server = SteamServerItem()
        server.appId = 0x54100
        assert not lib.QLR_Steamworks_ReadServerListDetails(0x12345678, 1, ctypes.byref(server))
        assert server.appId == 0
        lib.QLR_Steamworks_RefreshServerListRequest(0x12345678)
        lib.QLR_Steamworks_ReleaseServerListRequest(0x12345678)
        assert not lib.QLR_Steamworks_RequestServerDetails(
            0x01020304,
            27960,
            0xAAA0,
            0xBBB0,
            0xCCC0,
            ctypes.byref(ping_query),
            ctypes.byref(players_query),
            ctypes.byref(rules_query),
        )
        assert ping_query.value == 0
        assert players_query.value == 0
        assert rules_query.value == 0
        lib.QLR_Steamworks_CancelServerQuery(11)
        return

    mode_cases = [
        (0, "QLR_SteamworksMock_GetServerBrowserInternetCalls", b"gamedir", b"baseq3", 1),
        (1, "QLR_SteamworksMock_GetServerBrowserLanCalls", b"", b"", 0),
        (2, "QLR_SteamworksMock_GetServerBrowserFriendsCalls", b"gamedir", b"baseq3", 1),
        (3, "QLR_SteamworksMock_GetServerBrowserFavoritesCalls", b"gamedir", b"baseq3", 1),
        (4, "QLR_SteamworksMock_GetServerBrowserHistoryCalls", b"gamedir", b"baseq3", 1),
        (99, "QLR_SteamworksMock_GetServerBrowserInternetCalls", b"gamedir", b"baseq3", 1),
    ]
    mode_labels = {
        0: b"internet",
        1: b"lan",
        2: b"friends",
        3: b"favorites",
        4: b"history",
        99: b"internet",
    }

    for mode, call_getter, expected_key, expected_value, expected_filter_count in mode_cases:
        response = 0xABC000 + mode

        lib.QLR_SteamworksMock_Reset()
        lib.QLR_SteamworksMock_PrimeState()

        assert lib.QLR_Steamworks_HasServerBrowserInterface()
        assert lib.QLR_Steamworks_GetServerBrowserRequestModeLabel(mode) == mode_labels[mode]
        assert bool(lib.QLR_Steamworks_ServerBrowserRequestModeUsesGamedirFilter(mode)) == (expected_filter_count == 1)
        assert lib.QLR_Steamworks_RequestServerList(mode, response) == 0x13572468
        assert getattr(lib, call_getter)() == 1
        assert lib.QLR_SteamworksMock_GetServerBrowserLastAppId() == 0x54100
        assert lib.QLR_SteamworksMock_GetServerBrowserLastResponse() == response
        assert lib.QLR_SteamworksMock_GetServerBrowserLastFilterCount() == expected_filter_count
        assert lib.QLR_SteamworksMock_GetServerBrowserLastFilterKey() == expected_key
        assert lib.QLR_SteamworksMock_GetServerBrowserLastFilterValue() == expected_value

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()

    request = lib.QLR_Steamworks_RequestServerList(2, 0xABCDEF)
    assert request == 0x13572468
    assert lib.QLR_Steamworks_GetServerListDetails(request, 7) != 0
    assert lib.QLR_SteamworksMock_GetServerBrowserGetDetailsCalls() == 1
    assert lib.QLR_SteamworksMock_GetServerBrowserLastRequest() == request
    assert lib.QLR_SteamworksMock_GetServerBrowserLastIndex() == 7

    lib.QLR_Steamworks_RefreshServerListRequest(request)
    assert lib.QLR_SteamworksMock_GetServerBrowserRefreshCalls() == 1
    assert lib.QLR_SteamworksMock_GetServerBrowserLastRequest() == request

    lib.QLR_Steamworks_ReleaseServerListRequest(request)
    assert lib.QLR_SteamworksMock_GetServerBrowserReleaseCalls() == 1
    assert lib.QLR_SteamworksMock_GetServerBrowserLastRequest() == request

    ping_query = ctypes.c_int()
    players_query = ctypes.c_int()
    rules_query = ctypes.c_int()
    assert lib.QLR_Steamworks_RequestServerDetails(
        0x01020304,
        27960,
        0xAAA0,
        0xBBB0,
        0xCCC0,
        ctypes.byref(ping_query),
        ctypes.byref(players_query),
        ctypes.byref(rules_query),
    )
    assert ping_query.value == 11
    assert players_query.value == 12
    assert rules_query.value == 13
    assert lib.QLR_SteamworksMock_GetServerBrowserPingCalls() == 1
    assert lib.QLR_SteamworksMock_GetServerBrowserRulesCalls() == 1
    assert lib.QLR_SteamworksMock_GetServerBrowserPlayersCalls() == 1
    assert lib.QLR_SteamworksMock_GetServerBrowserPingOrder() == 1
    assert lib.QLR_SteamworksMock_GetServerBrowserRulesOrder() == 2
    assert lib.QLR_SteamworksMock_GetServerBrowserPlayersOrder() == 3
    assert lib.QLR_SteamworksMock_GetServerBrowserLastIp() == 0x01020304
    assert lib.QLR_SteamworksMock_GetServerBrowserLastPort() == 27960
    assert lib.QLR_SteamworksMock_GetServerBrowserLastPingResponse() == 0xAAA0
    assert lib.QLR_SteamworksMock_GetServerBrowserLastPlayersResponse() == 0xBBB0
    assert lib.QLR_SteamworksMock_GetServerBrowserLastRulesResponse() == 0xCCC0
    lib.QLR_Steamworks_CancelServerQuery(0)
    assert lib.QLR_SteamworksMock_GetServerBrowserCancelQueryCalls() == 0
    lib.QLR_Steamworks_CancelServerQuery(ping_query.value)
    assert lib.QLR_SteamworksMock_GetServerBrowserCancelQueryCalls() == 1
    assert lib.QLR_SteamworksMock_GetServerBrowserLastCancelQuery() == 11
    lib.QLR_Steamworks_CancelServerQuery(players_query.value)
    assert lib.QLR_SteamworksMock_GetServerBrowserCancelQueryCalls() == 2
    assert lib.QLR_SteamworksMock_GetServerBrowserLastCancelQuery() == 12
    lib.QLR_Steamworks_CancelServerQuery(rules_query.value)
    assert lib.QLR_SteamworksMock_GetServerBrowserCancelQueryCalls() == 3
    assert lib.QLR_SteamworksMock_GetServerBrowserLastCancelQuery() == 13

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()
    lib.QLR_SteamworksMock_SetServerBrowserDetailQueryResults(11, 0, 13)

    ping_query.value = -1
    players_query.value = -1
    rules_query.value = -1
    assert not lib.QLR_Steamworks_RequestServerDetails(
        0x01020304,
        27960,
        0xAAA0,
        0xBBB0,
        0xCCC0,
        ctypes.byref(ping_query),
        ctypes.byref(players_query),
        ctypes.byref(rules_query),
    )
    assert ping_query.value == 0
    assert players_query.value == 0
    assert rules_query.value == 0
    assert lib.QLR_SteamworksMock_GetServerBrowserPingCalls() == 1
    assert lib.QLR_SteamworksMock_GetServerBrowserRulesCalls() == 1
    assert lib.QLR_SteamworksMock_GetServerBrowserPlayersCalls() == 1
    assert lib.QLR_SteamworksMock_GetServerBrowserPingOrder() == 1
    assert lib.QLR_SteamworksMock_GetServerBrowserRulesOrder() == 2
    assert lib.QLR_SteamworksMock_GetServerBrowserPlayersOrder() == 3
    assert lib.QLR_SteamworksMock_GetServerBrowserCancelQueryCalls() == 2
    assert lib.QLR_SteamworksMock_GetServerBrowserLastCancelQuery() == 13


def test_server_browser_owner_reconstructs_retail_refresh_lifecycle(steamworks_harness: tuple[ctypes.CDLL, bool]) -> None:
    lib, enabled = steamworks_harness
    owner = SteamServerBrowserOwner()

    owner.refreshActive = 1
    owner.request = 0x12345678
    lib.QLR_Steamworks_InitServerBrowserOwner(ctypes.byref(owner))
    assert owner.refreshActive == 0
    assert owner.request == 0

    if not enabled:
        assert not lib.QLR_Steamworks_BeginServerBrowserOwnerRequest(ctypes.byref(owner), 0, 0xABCDEF)
        assert owner.refreshActive == 0
        assert owner.request == 0
        assert not lib.QLR_Steamworks_RefreshServerBrowserOwnerRequest(ctypes.byref(owner))
        assert not lib.QLR_Steamworks_CompleteServerBrowserOwnerRequest(ctypes.byref(owner))
        return

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()

    assert lib.QLR_Steamworks_BeginServerBrowserOwnerRequest(ctypes.byref(owner), 0, 0xABCDEF)
    assert owner.refreshActive == 1
    assert owner.request == 0x13572468
    assert lib.QLR_SteamworksMock_GetServerBrowserInternetCalls() == 1
    assert lib.QLR_SteamworksMock_GetServerBrowserLastResponse() == 0xABCDEF

    assert not lib.QLR_Steamworks_BeginServerBrowserOwnerRequest(ctypes.byref(owner), 1, 0x123456)
    assert owner.refreshActive == 1
    assert owner.request == 0x13572468
    assert lib.QLR_SteamworksMock_GetServerBrowserLanCalls() == 0
    assert lib.QLR_SteamworksMock_GetServerBrowserReleaseCalls() == 0

    assert lib.QLR_Steamworks_RefreshServerBrowserOwnerRequest(ctypes.byref(owner))
    assert lib.QLR_SteamworksMock_GetServerBrowserRefreshCalls() == 1
    assert lib.QLR_SteamworksMock_GetServerBrowserLastRequest() == 0x13572468

    assert lib.QLR_Steamworks_CompleteServerBrowserOwnerRequest(ctypes.byref(owner))
    assert owner.refreshActive == 0
    assert owner.request == 0x13572468

    assert lib.QLR_Steamworks_BeginServerBrowserOwnerRequest(ctypes.byref(owner), 1, 0x123456)
    assert owner.refreshActive == 1
    assert owner.request == 0x13572468
    assert lib.QLR_SteamworksMock_GetServerBrowserReleaseCalls() == 1
    assert lib.QLR_SteamworksMock_GetServerBrowserLanCalls() == 1
    assert lib.QLR_SteamworksMock_GetServerBrowserLastResponse() == 0x123456
    assert lib.QLR_SteamworksMock_GetServerBrowserLastFilterCount() == 0

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()
    lib.QLR_SteamworksMock_SetServerBrowserRequestResult(0)
    lib.QLR_Steamworks_InitServerBrowserOwner(ctypes.byref(owner))

    assert not lib.QLR_Steamworks_BeginServerBrowserOwnerRequest(ctypes.byref(owner), 2, 0xABCDEF)
    assert owner.refreshActive == 0
    assert owner.request == 0
    assert lib.QLR_SteamworksMock_GetServerBrowserFriendsCalls() == 1
    assert lib.QLR_SteamworksMock_GetServerBrowserLastResponse() == 0xABCDEF
    assert not lib.QLR_Steamworks_RefreshServerBrowserOwnerRequest(ctypes.byref(owner))


def test_server_browser_detail_reader_projects_retail_gameserveritem_row(steamworks_harness: tuple[ctypes.CDLL, bool]) -> None:
    lib, enabled = steamworks_harness
    server = SteamServerItem()

    if not enabled:
        server.appId = 0x54100
        assert not lib.QLR_Steamworks_ReadServerListDetails(0x12345678, 3, ctypes.byref(server))
        assert server.appId == 0
        return

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()

    request = lib.QLR_Steamworks_RequestServerList(0, 0xABCDEF)
    assert request == 0x13572468
    assert lib.QLR_Steamworks_ReadServerListDetails(request, 5, ctypes.byref(server))
    assert lib.QLR_SteamworksMock_GetServerBrowserGetDetailsCalls() == 1
    assert lib.QLR_SteamworksMock_GetServerBrowserLastRequest() == request
    assert lib.QLR_SteamworksMock_GetServerBrowserLastIndex() == 5
    assert server.serverIp == 0x01020304
    assert server.serverPort == 27960
    assert server.queryPort == 27961
    assert server.ping == 42
    assert _c_string(server.gameDir) == b"baseq3"
    assert _c_string(server.map) == b"campgrounds"
    assert _c_string(server.gameDescription) == b"Clan Arena"
    assert server.appId == 0x54100
    assert server.numPlayers == 7
    assert server.maxPlayers == 16
    assert server.botPlayers == 2
    assert server.passwordProtected
    assert server.vacSecured
    assert server.lastPlayed == 123456789
    assert server.serverVersion == 1069
    assert _c_string(server.name) == b"QLR Test Server"
    assert _c_string(server.displayName) == b"QLR Test Server"
    assert _c_string(server.tags) == b"duel,instagib"
    assert server.steamId == 0x0123456789ABCDEF

    lib.QLR_SteamworksMock_SetAppId(0x123456)
    cleared = SteamServerItem()
    cleared.appId = 0x54100
    assert not lib.QLR_Steamworks_ReadServerListDetails(request, 5, ctypes.byref(cleared))
    assert cleared.appId == 0
    assert _c_string(cleared.name) == b""
    assert _c_string(cleared.displayName) == b""


def test_server_browser_detail_reader_uses_retail_empty_name_fallback(steamworks_harness: tuple[ctypes.CDLL, bool]) -> None:
    lib, enabled = steamworks_harness

    if not enabled:
        return

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()
    lib.QLR_SteamworksMock_SetServerBrowserServerName(b"")

    request = lib.QLR_Steamworks_RequestServerList(0, 0xABCDEF)
    server = SteamServerItem()
    assert lib.QLR_Steamworks_ReadServerListDetails(request, 5, ctypes.byref(server))
    assert _c_string(server.name) == b""
    assert _c_string(server.displayName) == b"1.2.3.4:27960"


def test_server_browser_response_projection_matches_retail_jsbrowser_payload_shape(steamworks_harness: tuple[ctypes.CDLL, bool]) -> None:
    lib, enabled = steamworks_harness
    response = SteamServerBrowserResponse()

    if not enabled:
        response.numPlayers = 99
        assert not lib.QLR_Steamworks_ReadServerBrowserResponse(0x12345678, 3, ctypes.byref(response))
        assert response.numPlayers == 0
        assert _c_string(response.id) == b""
        return

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()

    response_id = ctypes.create_string_buffer(32)
    lib.QLR_Steamworks_FormatServerBrowserResponseId(0x01020304, 27960, response_id, len(response_id))
    assert response_id.value == b"16909060_27960"

    request = lib.QLR_Steamworks_RequestServerList(0, 0xABCDEF)
    server = SteamServerItem()
    assert lib.QLR_Steamworks_ReadServerListDetails(request, 5, ctypes.byref(server))

    built = SteamServerBrowserResponse()
    assert lib.QLR_Steamworks_BuildServerBrowserResponse(ctypes.byref(server), ctypes.byref(built))
    assert _c_string(built.id) == b"16909060_27960"
    assert _c_string(built.name) == b"QLR Test Server"
    assert built.numPlayers == 7
    assert built.maxPlayers == 16
    assert built.ping == 42
    assert _c_string(built.map) == b"campgrounds"
    assert built.botPlayers == 2
    assert built.passwordProtected
    assert built.vacSecured
    assert built.serverIp == 0x01020304
    assert built.serverPort == 27960
    assert _c_string(built.steamId) == str(0x0123456789ABCDEF).encode()
    assert _c_string(built.tags) == b"duel,instagib"
    assert _c_string(built.gametype) == b"Clan Arena"
    assert built.lastPlayed == 123456789

    response = SteamServerBrowserResponse()
    assert lib.QLR_Steamworks_ReadServerBrowserResponse(request, 5, ctypes.byref(response))
    assert _c_string(response.id) == b"16909060_27960"
    assert _c_string(response.name) == b"QLR Test Server"
    assert _c_string(response.steamId) == str(0x0123456789ABCDEF).encode()
    assert _c_string(response.gametype) == b"Clan Arena"

    lib.QLR_SteamworksMock_SetServerBrowserServerName(b"")
    unnamed = SteamServerBrowserResponse()
    assert lib.QLR_Steamworks_ReadServerBrowserResponse(request, 5, ctypes.byref(unnamed))
    assert _c_string(unnamed.id) == b"16909060_27960"
    assert _c_string(unnamed.name) == b"1.2.3.4:27960"

    lib.QLR_SteamworksMock_SetAppId(0x123456)
    cleared = SteamServerBrowserResponse()
    cleared.numPlayers = 99
    assert not lib.QLR_Steamworks_ReadServerBrowserResponse(request, 5, ctypes.byref(cleared))
    assert cleared.numPlayers == 0
    assert _c_string(cleared.id) == b""
    assert _c_string(cleared.name) == b""


def test_server_browser_ping_response_projection_matches_retail_jsbrowserdetails_payload_shape(steamworks_harness: tuple[ctypes.CDLL, bool]) -> None:
    lib, enabled = steamworks_harness
    response = SteamServerBrowserResponse()

    if not enabled:
        response.numPlayers = 99
        assert not lib.QLR_Steamworks_ReadServerBrowserPingResponse(ctypes.byref(response))
        assert response.numPlayers == 0
        assert _c_string(response.id) == b""
        return

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()

    assert lib.QLR_Steamworks_ReadServerBrowserPingResponse(ctypes.byref(response))
    assert _c_string(response.id) == b"16909060_27960"
    assert _c_string(response.name) == b"QLR Test Server"
    assert response.numPlayers == 7
    assert response.maxPlayers == 16
    assert response.ping == 42
    assert _c_string(response.map) == b"campgrounds"
    assert response.botPlayers == 2
    assert response.passwordProtected
    assert response.vacSecured
    assert response.serverIp == 0x01020304
    assert response.serverPort == 27960
    assert _c_string(response.steamId) == str(0x0123456789ABCDEF).encode()
    assert _c_string(response.tags) == b"duel,instagib"
    assert _c_string(response.gametype) == b"Clan Arena"

    lib.QLR_SteamworksMock_SetServerBrowserServerName(b"")
    unnamed = SteamServerBrowserResponse()
    assert lib.QLR_Steamworks_ReadServerBrowserPingResponse(ctypes.byref(unnamed))
    assert _c_string(unnamed.id) == b"16909060_27960"
    assert _c_string(unnamed.name) == b"1.2.3.4:27960"

    lib.QLR_SteamworksMock_SetAppId(0x123456)
    cleared = SteamServerBrowserResponse()
    cleared.numPlayers = 99
    assert not lib.QLR_Steamworks_ReadServerBrowserPingResponse(ctypes.byref(cleared))
    assert cleared.numPlayers == 0
    assert _c_string(cleared.id) == b""
    assert _c_string(cleared.name) == b""


def test_server_browser_failure_and_refresh_projections_match_retail_callbacks(steamworks_harness: tuple[ctypes.CDLL, bool]) -> None:
    lib, enabled = steamworks_harness
    failure = SteamServerBrowserFailure()
    refresh = SteamServerBrowserRefreshComplete()

    if not enabled:
        failure.id = 77
        refresh.eventName = b"stale"
        assert not lib.QLR_Steamworks_BuildServerBrowserFailure(7, ctypes.byref(failure))
        assert failure.id == 0
        assert _c_string(failure.eventName) == b""
        assert not lib.QLR_Steamworks_BuildServerBrowserRefreshComplete(ctypes.byref(refresh))
        assert _c_string(refresh.eventName) == b""
        return

    event_name = ctypes.create_string_buffer(64)
    lib.QLR_Steamworks_FormatServerBrowserFailureEventName(7, event_name, len(event_name))
    assert event_name.value == b"servers.details.7.failed"

    assert lib.QLR_Steamworks_BuildServerBrowserFailure(7, ctypes.byref(failure))
    assert failure.id == 7
    assert _c_string(failure.eventName) == b"servers.details.7.failed"

    assert lib.QLR_Steamworks_BuildServerBrowserFailure(-1, ctypes.byref(failure))
    assert failure.id == -1
    assert _c_string(failure.eventName) == b"servers.details.-1.failed"

    assert lib.QLR_Steamworks_BuildServerBrowserRefreshComplete(ctypes.byref(refresh))
    assert _c_string(refresh.eventName) == b"servers.refresh.end"

    owner = SteamServerBrowserOwner()
    lib.QLR_Steamworks_InitServerBrowserOwner(ctypes.byref(owner))
    owner.refreshActive = 1
    assert lib.QLR_Steamworks_CompleteServerBrowserOwnerRequest(ctypes.byref(owner))
    assert owner.refreshActive == 0


def test_server_browser_detail_identity_and_events_match_retail_jsbrowserdetails_contract(steamworks_harness: tuple[ctypes.CDLL, bool]) -> None:
    lib, enabled = steamworks_harness
    identity = SteamServerBrowserDetailIdentity()
    event = SteamServerBrowserDetailEvent()

    if not enabled:
        identity.serverIp = 0x01020304
        event.eventName = b"stale"
        assert not lib.QLR_Steamworks_BuildServerBrowserDetailIdentity(0x01020304, 27960, ctypes.byref(identity))
        assert identity.serverIp == 0
        assert identity.serverPort == 0
        assert _c_string(identity.id) == b""
        assert not lib.QLR_Steamworks_BuildServerBrowserDetailEvent(ctypes.byref(identity), 0, 0, ctypes.byref(event))
        assert event.identity.serverIp == 0
        assert _c_string(event.eventName) == b""
        return

    detail_id = ctypes.create_string_buffer(32)
    lib.QLR_Steamworks_FormatServerBrowserDetailId(0x01020304, 27960, detail_id, len(detail_id))
    assert detail_id.value == b"16909060_27960"

    signed_port_id = ctypes.create_string_buffer(32)
    lib.QLR_Steamworks_FormatServerBrowserDetailId(0x01020304, 0xCFC7, signed_port_id, len(signed_port_id))
    assert signed_port_id.value == b"16909060_-12345"

    assert lib.QLR_Steamworks_BuildServerBrowserDetailIdentity(0x01020304, 27960, ctypes.byref(identity))
    assert identity.serverIp == 0x01020304
    assert identity.serverPort == 27960
    assert _c_string(identity.id) == b"16909060_27960"

    invalid_identity = SteamServerBrowserDetailIdentity()
    invalid_identity.serverIp = 99
    assert not lib.QLR_Steamworks_BuildServerBrowserDetailIdentity(0, 27960, ctypes.byref(invalid_identity))
    assert invalid_identity.serverIp == 0
    assert _c_string(invalid_identity.id) == b""

    expectations = [
        (0, 0, b"servers.rules.16909060_27960.response"),
        (0, 1, b"servers.rules.16909060_27960.failed"),
        (0, 2, b"servers.rules.16909060_27960.end"),
        (1, 0, b"servers.players.16909060_27960.response"),
        (1, 1, b"servers.players.16909060_27960.failed"),
        (1, 2, b"servers.players.16909060_27960.end"),
    ]
    for channel, phase, expected in expectations:
        event_name = ctypes.create_string_buffer(64)
        assert lib.QLR_Steamworks_FormatServerBrowserDetailEventName(channel, phase, identity.id, event_name, len(event_name))
        assert event_name.value == expected

        event = SteamServerBrowserDetailEvent()
        assert lib.QLR_Steamworks_BuildServerBrowserDetailEvent(ctypes.byref(identity), channel, phase, ctypes.byref(event))
        assert event.identity.serverIp == 0x01020304
        assert event.identity.serverPort == 27960
        assert _c_string(event.identity.id) == b"16909060_27960"
        assert _c_string(event.eventName) == expected

    invalid_name = ctypes.create_string_buffer(64)
    assert not lib.QLR_Steamworks_FormatServerBrowserDetailEventName(99, 0, identity.id, invalid_name, len(invalid_name))
    assert invalid_name.value == b""

    assert not lib.QLR_Steamworks_BuildServerBrowserDetailEvent(ctypes.byref(identity), 0, 99, ctypes.byref(event))
    assert event.identity.serverIp == 0
    assert _c_string(event.eventName) == b""


def test_server_browser_detail_response_payloads_match_retail_jsbrowserdetails_contract(steamworks_harness: tuple[ctypes.CDLL, bool]) -> None:
    lib, enabled = steamworks_harness
    identity = SteamServerBrowserDetailIdentity()
    rule_response = SteamServerBrowserRuleResponse()
    player_response = SteamServerBrowserPlayerResponse()

    if not enabled:
        rule_response.identity.serverIp = 0x01020304
        rule_response.rule = b"stale"
        player_response.score = 99
        assert not lib.QLR_Steamworks_BuildServerBrowserRuleResponse(
            ctypes.byref(identity),
            b"sv_hostname",
            b"QLR Test Server",
            ctypes.byref(rule_response),
        )
        assert rule_response.identity.serverIp == 0
        assert _c_string(rule_response.eventName) == b""
        assert _c_string(rule_response.rule) == b""
        assert not lib.QLR_Steamworks_BuildServerBrowserPlayerResponse(
            ctypes.byref(identity),
            b"player",
            15,
            120,
            ctypes.byref(player_response),
        )
        assert player_response.score == 0
        assert player_response.time == 0
        assert _c_string(player_response.name) == b""
        return

    assert lib.QLR_Steamworks_BuildServerBrowserDetailIdentity(0x01020304, 27960, ctypes.byref(identity))

    assert lib.QLR_Steamworks_BuildServerBrowserRuleResponse(
        ctypes.byref(identity),
        b"sv_hostname",
        b"QLR Test Server",
        ctypes.byref(rule_response),
    )
    assert rule_response.identity.serverIp == 0x01020304
    assert rule_response.identity.serverPort == 27960
    assert _c_string(rule_response.identity.id) == b"16909060_27960"
    assert _c_string(rule_response.eventName) == b"servers.rules.16909060_27960.response"
    assert _c_string(rule_response.rule) == b"sv_hostname"
    assert _c_string(rule_response.value) == b"QLR Test Server"

    assert lib.QLR_Steamworks_BuildServerBrowserRuleResponse(
        ctypes.byref(identity),
        None,
        None,
        ctypes.byref(rule_response),
    )
    assert _c_string(rule_response.rule) == b""
    assert _c_string(rule_response.value) == b""

    assert lib.QLR_Steamworks_BuildServerBrowserPlayerResponse(
        ctypes.byref(identity),
        b"xaero",
        15,
        120,
        ctypes.byref(player_response),
    )
    assert player_response.identity.serverIp == 0x01020304
    assert player_response.identity.serverPort == 27960
    assert _c_string(player_response.identity.id) == b"16909060_27960"
    assert _c_string(player_response.eventName) == b"servers.players.16909060_27960.response"
    assert _c_string(player_response.name) == b"xaero"
    assert player_response.score == 15
    assert player_response.time == 120

    assert lib.QLR_Steamworks_BuildServerBrowserPlayerResponse(
        ctypes.byref(identity),
        None,
        -1,
        0,
        ctypes.byref(player_response),
    )
    assert _c_string(player_response.name) == b""
    assert player_response.score == -1
    assert player_response.time == 0

    invalid_identity = SteamServerBrowserDetailIdentity()
    assert not lib.QLR_Steamworks_BuildServerBrowserRuleResponse(
        ctypes.byref(invalid_identity),
        b"sv_hostname",
        b"QLR Test Server",
        ctypes.byref(rule_response),
    )
    assert rule_response.identity.serverIp == 0
    assert _c_string(rule_response.eventName) == b""
    assert _c_string(rule_response.rule) == b""
    assert not lib.QLR_Steamworks_BuildServerBrowserPlayerResponse(
        ctypes.byref(invalid_identity),
        b"xaero",
        15,
        120,
        ctypes.byref(player_response),
    )
    assert player_response.score == 0
    assert player_response.time == 0


def test_server_browser_detail_lifecycle_reconstructs_retail_three_callback_release_counter(steamworks_harness: tuple[ctypes.CDLL, bool]) -> None:
    lib, enabled = steamworks_harness
    lifecycle = SteamServerBrowserDetailLifecycle()
    release_ready = ctypes.c_int(7)

    if not enabled:
        lifecycle.identity.serverIp = 0x01020304
        lifecycle.completedCallbacks = 2
        lifecycle.releaseReady = 1
        assert not lib.QLR_Steamworks_InitServerBrowserDetailLifecycle(0x01020304, 27960, ctypes.byref(lifecycle))
        assert lifecycle.identity.serverIp == 0
        assert lifecycle.completedCallbacks == 0
        assert lifecycle.releaseReady == 0

        lifecycle.completedCallbacks = 2
        lifecycle.releaseReady = 1
        assert not lib.QLR_Steamworks_CompleteServerBrowserDetailCallback(ctypes.byref(lifecycle), ctypes.byref(release_ready))
        assert lifecycle.completedCallbacks == 0
        assert lifecycle.releaseReady == 0
        assert release_ready.value == 0
        return

    assert lib.QLR_Steamworks_InitServerBrowserDetailLifecycle(0x01020304, 27960, ctypes.byref(lifecycle))
    assert lifecycle.identity.serverIp == 0x01020304
    assert lifecycle.identity.serverPort == 27960
    assert _c_string(lifecycle.identity.id) == b"16909060_27960"
    assert lifecycle.completedCallbacks == 0
    assert lifecycle.releaseReady == 0

    for expected_count in (1, 2):
        release_ready.value = 7
        assert lib.QLR_Steamworks_CompleteServerBrowserDetailCallback(ctypes.byref(lifecycle), ctypes.byref(release_ready))
        assert lifecycle.completedCallbacks == expected_count
        assert lifecycle.releaseReady == 0
        assert release_ready.value == 0

    release_ready.value = 0
    assert lib.QLR_Steamworks_CompleteServerBrowserDetailCallback(ctypes.byref(lifecycle), ctypes.byref(release_ready))
    assert lifecycle.completedCallbacks == 3
    assert lifecycle.releaseReady == 1
    assert release_ready.value == 1

    release_ready.value = 0
    assert not lib.QLR_Steamworks_CompleteServerBrowserDetailCallback(ctypes.byref(lifecycle), ctypes.byref(release_ready))
    assert lifecycle.completedCallbacks == 3
    assert lifecycle.releaseReady == 1
    assert release_ready.value == 1

    invalid_lifecycle = SteamServerBrowserDetailLifecycle()
    invalid_lifecycle.completedCallbacks = 99
    assert not lib.QLR_Steamworks_InitServerBrowserDetailLifecycle(0, 27960, ctypes.byref(invalid_lifecycle))
    assert invalid_lifecycle.completedCallbacks == 0
    assert invalid_lifecycle.releaseReady == 0

    blank_lifecycle = SteamServerBrowserDetailLifecycle()
    release_ready.value = 1
    assert not lib.QLR_Steamworks_CompleteServerBrowserDetailCallback(ctypes.byref(blank_lifecycle), ctypes.byref(release_ready))
    assert release_ready.value == 0


def test_server_browser_detail_request_owner_reconstructs_retail_response_views_and_release(steamworks_harness: tuple[ctypes.CDLL, bool]) -> None:
    lib, enabled = steamworks_harness
    detail_base = 0x1000
    views = SteamServerBrowserDetailResponseViews()
    request = SteamServerBrowserDetailRequest()
    release_ready = ctypes.c_int(7)

    if not enabled:
        views.rulesResponse = 0xAAA0
        assert not lib.QLR_Steamworks_BuildServerBrowserDetailResponseViews(detail_base, ctypes.byref(views))
        assert not views.rulesResponse
        assert not views.playersResponse
        assert not views.pingResponse

        request.detailObjectBase = detail_base
        request.pingQuery = 11
        request.playersQuery = 12
        request.rulesQuery = 13
        request.queriesActive = 1
        lib.QLR_Steamworks_InitServerBrowserDetailRequest(ctypes.byref(request))
        assert not request.detailObjectBase
        assert request.pingQuery == 0
        assert request.playersQuery == 0
        assert request.rulesQuery == 0
        assert request.queriesActive == 0

        request.detailObjectBase = detail_base
        request.queriesActive = 1
        assert not lib.QLR_Steamworks_BeginServerBrowserDetailRequest(ctypes.byref(request), 0x01020304, 27960, detail_base)
        assert not request.detailObjectBase
        assert request.queriesActive == 0

        request.detailObjectBase = detail_base
        request.queriesActive = 1
        release_ready.value = 1
        assert not lib.QLR_Steamworks_CompleteServerBrowserDetailRequestCallback(ctypes.byref(request), ctypes.byref(release_ready))
        assert not request.detailObjectBase
        assert request.queriesActive == 0
        assert release_ready.value == 0
        return

    assert lib.QLR_Steamworks_BuildServerBrowserDetailResponseViews(detail_base, ctypes.byref(views))
    assert views.rulesResponse == detail_base
    assert views.playersResponse == detail_base + 4
    assert views.pingResponse == detail_base + 8

    assert not lib.QLR_Steamworks_BuildServerBrowserDetailResponseViews(0, ctypes.byref(views))
    assert not views.rulesResponse
    assert not views.playersResponse
    assert not views.pingResponse

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()

    assert lib.QLR_Steamworks_BeginServerBrowserDetailRequest(ctypes.byref(request), 0x01020304, 27960, detail_base)
    assert request.detailObjectBase == detail_base
    assert request.queriesActive == 1
    assert request.pingQuery == 11
    assert request.playersQuery == 12
    assert request.rulesQuery == 13
    assert request.lifecycle.identity.serverIp == 0x01020304
    assert request.lifecycle.identity.serverPort == 27960
    assert _c_string(request.lifecycle.identity.id) == b"16909060_27960"
    assert lib.QLR_SteamworksMock_GetServerBrowserPingCalls() == 1
    assert lib.QLR_SteamworksMock_GetServerBrowserRulesCalls() == 1
    assert lib.QLR_SteamworksMock_GetServerBrowserPlayersCalls() == 1
    assert lib.QLR_SteamworksMock_GetServerBrowserPingOrder() == 1
    assert lib.QLR_SteamworksMock_GetServerBrowserRulesOrder() == 2
    assert lib.QLR_SteamworksMock_GetServerBrowserPlayersOrder() == 3
    assert lib.QLR_SteamworksMock_GetServerBrowserLastRulesResponse() == detail_base
    assert lib.QLR_SteamworksMock_GetServerBrowserLastPlayersResponse() == detail_base + 4
    assert lib.QLR_SteamworksMock_GetServerBrowserLastPingResponse() == detail_base + 8

    assert not lib.QLR_Steamworks_BeginServerBrowserDetailRequest(ctypes.byref(request), 0x01020305, 27961, 0x2000)
    assert request.detailObjectBase == detail_base
    assert request.queriesActive == 1
    assert lib.QLR_SteamworksMock_GetServerBrowserPingCalls() == 1

    for expected_count in (1, 2):
        release_ready.value = 7
        assert lib.QLR_Steamworks_CompleteServerBrowserDetailRequestCallback(ctypes.byref(request), ctypes.byref(release_ready))
        assert request.lifecycle.completedCallbacks == expected_count
        assert request.queriesActive == 1
        assert request.pingQuery == 11
        assert release_ready.value == 0

    release_ready.value = 0
    assert lib.QLR_Steamworks_CompleteServerBrowserDetailRequestCallback(ctypes.byref(request), ctypes.byref(release_ready))
    assert request.lifecycle.completedCallbacks == 3
    assert request.lifecycle.releaseReady == 1
    assert request.queriesActive == 0
    assert not request.detailObjectBase
    assert request.pingQuery == 0
    assert request.playersQuery == 0
    assert request.rulesQuery == 0
    assert release_ready.value == 1

    release_ready.value = 0
    assert not lib.QLR_Steamworks_CompleteServerBrowserDetailRequestCallback(ctypes.byref(request), ctypes.byref(release_ready))
    assert release_ready.value == 1

    invalid_request = SteamServerBrowserDetailRequest()
    invalid_request.pingQuery = 99
    assert not lib.QLR_Steamworks_BeginServerBrowserDetailRequest(ctypes.byref(invalid_request), 0, 27960, detail_base)
    assert invalid_request.pingQuery == 0
    assert invalid_request.queriesActive == 0

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()
    lib.QLR_SteamworksMock_SetServerBrowserDetailQueryResults(11, 0, 13)

    failed_request = SteamServerBrowserDetailRequest()
    assert not lib.QLR_Steamworks_BeginServerBrowserDetailRequest(
        ctypes.byref(failed_request),
        0x01020304,
        27960,
        detail_base,
    )
    assert not failed_request.detailObjectBase
    assert failed_request.pingQuery == 0
    assert failed_request.playersQuery == 0
    assert failed_request.rulesQuery == 0
    assert failed_request.queriesActive == 0
    assert lib.QLR_SteamworksMock_GetServerBrowserPingCalls() == 1
    assert lib.QLR_SteamworksMock_GetServerBrowserRulesCalls() == 1
    assert lib.QLR_SteamworksMock_GetServerBrowserPlayersCalls() == 1
    assert lib.QLR_SteamworksMock_GetServerBrowserCancelQueryCalls() == 2
    assert lib.QLR_SteamworksMock_GetServerBrowserLastCancelQuery() == 13


def test_set_rich_presence_uses_mapped_friends_slot(steamworks_harness: tuple[ctypes.CDLL, bool]) -> None:
    lib, enabled = steamworks_harness

    if not enabled:
        assert not lib.QLR_Steamworks_SetRichPresence(b"status", b"At the main menu")
        return

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()

    assert lib.QLR_Steamworks_SetRichPresence(b"status", b"At the main menu")
    assert lib.QLR_SteamworksMock_GetRichPresenceCallCount() == 1
    assert lib.QLR_SteamworksMock_GetRichPresenceKey() == b"status"
    assert lib.QLR_SteamworksMock_GetRichPresenceValue() == b"At the main menu"


def test_game_server_helpers_use_mapped_server_slots(steamworks_harness: tuple[ctypes.CDLL, bool]) -> None:
    lib, enabled = steamworks_harness
    steam_id_low = ctypes.c_uint32()
    steam_id_high = ctypes.c_uint32()

    if not enabled:
        assert not lib.QLR_Steamworks_Init()
        assert not lib.QLR_Steamworks_ServerInit(0x01020304, 27960, 1, 1)
        assert not lib.QLR_Steamworks_ServerIsInitialised()
        assert not lib.QLR_Steamworks_ServerEnableHeartbeats(1)
        assert not lib.QLR_Steamworks_ServerSetDedicated(1)
        assert not lib.QLR_Steamworks_ServerLogOn(b"token")
        assert not lib.QLR_Steamworks_ServerSetProduct(b"Quake Live")
        assert not lib.QLR_Steamworks_ServerSetGameDir(b"baseq3")
        assert not lib.QLR_Steamworks_ServerSetGameDescription(b"Clan Arena")
        assert not lib.QLR_Steamworks_ServerSetMaxPlayerCount(16)
        assert not lib.QLR_Steamworks_ServerSetBotPlayerCount(3)
        assert not lib.QLR_Steamworks_ServerSetServerName(b"QLR Test Server")
        assert not lib.QLR_Steamworks_ServerSetMapName(b"campgrounds")
        assert not lib.QLR_Steamworks_ServerSetPasswordProtected(1)
        assert not lib.QLR_Steamworks_ServerGetSteamID(ctypes.byref(steam_id_low), ctypes.byref(steam_id_high))
        assert not lib.QLR_Steamworks_ServerSetGameTags(b"duel,instagib")
        assert not lib.QLR_Steamworks_ServerSetKeyValue(b"g_redScore", b"5")
        assert not lib.QLR_Steamworks_ServerSetKeyValuesFromInfoString(b"\\mapname\\campgrounds")
        assert not lib.QLR_Steamworks_ServerUpdateUserData(0x89ABCDEF, 0x01234567, b"QLR Player", 42)
        assert steam_id_low.value == 0
        assert steam_id_high.value == 0
        assert lib.QLR_Steamworks_ServerGetPublicIP() == 0
        return

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()
    lib.QLR_SteamworksMock_SetSteamGameServerId(0x0FEDCBA987654321)
    lib.QLR_SteamworksMock_SetSteamGameServerPublicIP(0x11223344)

    assert lib.QLR_Steamworks_Init()
    assert not lib.QLR_Steamworks_ServerIsInitialised()
    assert lib.QLR_Steamworks_ServerInit(0x01020304, 27960, 1, 1)
    assert lib.QLR_Steamworks_ServerIsInitialised()
    assert lib.QLR_Steamworks_ServerEnableHeartbeats(1)
    assert lib.QLR_Steamworks_ServerSetDedicated(1)
    assert lib.QLR_Steamworks_ServerLogOn(b"token-123")
    assert lib.QLR_Steamworks_ServerSetProduct(b"Quake Live")
    assert lib.QLR_Steamworks_ServerSetGameDir(b"baseq3")
    assert lib.QLR_Steamworks_ServerSetGameDescription(b"Clan Arena")
    assert lib.QLR_Steamworks_ServerSetMaxPlayerCount(16)
    assert lib.QLR_Steamworks_ServerSetBotPlayerCount(3)
    assert lib.QLR_Steamworks_ServerSetServerName(b"QLR Test Server")
    assert lib.QLR_Steamworks_ServerSetMapName(b"campgrounds")
    assert lib.QLR_Steamworks_ServerSetPasswordProtected(1)
    assert lib.QLR_Steamworks_ServerGetSteamID(ctypes.byref(steam_id_low), ctypes.byref(steam_id_high))
    assert steam_id_low.value == 0x87654321
    assert steam_id_high.value == 0x0FEDCBA9
    assert lib.QLR_Steamworks_ServerSetGameTags(b"duel,instagib")
    assert lib.QLR_Steamworks_ServerSetKeyValue(b"g_redScore", b"5")
    assert lib.QLR_Steamworks_ServerSetKeyValuesFromInfoString(b"\\gametype\\ca\\mapname\\campgrounds")
    assert lib.QLR_Steamworks_ServerUpdateUserData(0x89ABCDEF, 0x01234567, b"QLR Player", 42)
    assert lib.QLR_Steamworks_ServerGetPublicIP() == 0x11223344
    assert lib.QLR_Steamworks_ServerLogOn(b"")
    assert lib.QLR_Steamworks_ServerEnableHeartbeats(0)

    assert lib.QLR_SteamworksMock_GetSteamGameServerHeartbeatCalls() == 2
    assert lib.QLR_SteamworksMock_GetSteamGameServerLastHeartbeatEnabled() == 0
    assert lib.QLR_SteamworksMock_GetSteamGameServerDedicatedCalls() == 1
    assert lib.QLR_SteamworksMock_GetSteamGameServerLastDedicated() == 1
    assert lib.QLR_SteamworksMock_GetSteamGameServerLogOnCalls() == 1
    assert lib.QLR_SteamworksMock_GetSteamGameServerLogOnAnonymousCalls() == 1
    assert lib.QLR_SteamworksMock_GetSteamGameServerLastAccount() == b"token-123"
    assert lib.QLR_SteamworksMock_GetSteamGameServerProductCalls() == 1
    assert lib.QLR_SteamworksMock_GetSteamGameServerLastProduct() == b"Quake Live"
    assert lib.QLR_SteamworksMock_GetSteamGameServerGameDirCalls() == 1
    assert lib.QLR_SteamworksMock_GetSteamGameServerLastGameDir() == b"baseq3"
    assert lib.QLR_SteamworksMock_GetSteamGameServerGameDescriptionCalls() == 1
    assert lib.QLR_SteamworksMock_GetSteamGameServerLastGameDescription() == b"Clan Arena"
    assert lib.QLR_SteamworksMock_GetSteamGameServerMaxPlayerCountCalls() == 1
    assert lib.QLR_SteamworksMock_GetSteamGameServerLastMaxPlayerCount() == 16
    assert lib.QLR_SteamworksMock_GetSteamGameServerBotPlayerCountCalls() == 1
    assert lib.QLR_SteamworksMock_GetSteamGameServerLastBotPlayerCount() == 3
    assert lib.QLR_SteamworksMock_GetSteamGameServerServerNameCalls() == 1
    assert lib.QLR_SteamworksMock_GetSteamGameServerLastServerName() == b"QLR Test Server"
    assert lib.QLR_SteamworksMock_GetSteamGameServerMapNameCalls() == 1
    assert lib.QLR_SteamworksMock_GetSteamGameServerLastMapName() == b"campgrounds"
    assert lib.QLR_SteamworksMock_GetSteamGameServerPasswordCalls() == 1
    assert lib.QLR_SteamworksMock_GetSteamGameServerLastPasswordProtected() == 1
    assert lib.QLR_SteamworksMock_GetSteamGameServerGameTagsCalls() == 1
    assert lib.QLR_SteamworksMock_GetSteamGameServerLastGameTags() == b"duel,instagib"
    assert lib.QLR_SteamworksMock_GetSteamGameServerUserDataCalls() == 1
    assert lib.QLR_SteamworksMock_GetSteamGameServerLastUserDataId() == 0x0123456789ABCDEF
    assert lib.QLR_SteamworksMock_GetSteamGameServerLastUserDataName() == b"QLR Player"
    assert lib.QLR_SteamworksMock_GetSteamGameServerLastUserDataScore() == 42
    assert lib.QLR_SteamworksMock_GetSteamGameServerKeyValueCalls() == 3
    assert lib.QLR_SteamworksMock_GetSteamGameServerLastKey() == b"mapname"
    assert lib.QLR_SteamworksMock_GetSteamGameServerLastValue() == b"campgrounds"


def test_game_server_init_uses_retail_init_signature_and_dedicated_ugc_owner(steamworks_harness: tuple[ctypes.CDLL, bool]) -> None:
    lib, enabled = steamworks_harness

    if not enabled:
        assert not lib.QLR_Steamworks_ServerInit(0x01020304, 27960, 1, 1)
        assert not lib.QLR_Steamworks_ServerInitWithVersion(0x01020304, 27960, 1, 1, b"custom-build")
        return

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()

    assert lib.QLR_Steamworks_ServerInit(0x01020304, 27960, 1, 1)
    assert lib.QLR_SteamworksMock_GetSteamGameServerInitCalls() == 1
    assert lib.QLR_SteamworksMock_GetSteamGameServerLastInitIP() == 0x01020304
    assert lib.QLR_SteamworksMock_GetSteamGameServerLastInitGamePort() == 27960
    assert lib.QLR_SteamworksMock_GetSteamGameServerLastInitServerMode() == 3
    assert lib.QLR_SteamworksMock_GetSteamGameServerLastInitVersion() == b"1069"
    assert lib.QLR_Steamworks_ServerIsInitialised()

    lib.QLR_SteamworksMock_SetUGCItemState(4)
    assert lib.QLR_Steamworks_SubscribeItem(0x89ABCDEF, 0x01234567)
    assert lib.QLR_Steamworks_DownloadItem(0x89ABCDEF, 0x01234567, 1)
    assert lib.QLR_SteamworksMock_GetUGCSubscribeCalls() == 0
    assert lib.QLR_SteamworksMock_GetUGCDownloadCalls() == 0
    assert lib.QLR_SteamworksMock_GetSteamGameServerUGCSubscribeCalls() == 1
    assert lib.QLR_SteamworksMock_GetSteamGameServerUGCDownloadCalls() == 1
    assert lib.QLR_SteamworksMock_GetSteamGameServerUGCLastItemId() == 0x0123456789ABCDEF
    assert lib.QLR_SteamworksMock_GetSteamGameServerUGCLastHighPriority() == 1

    lib.QLR_Steamworks_ServerShutdown()
    assert not lib.QLR_Steamworks_ServerIsInitialised()
    assert lib.QLR_SteamworksMock_GetSteamGameServerShutdownCalls() == 1

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()
    assert lib.QLR_Steamworks_ServerInitWithVersion(0x01020304, 27961, 0, 0, b"custom-build")
    assert lib.QLR_SteamworksMock_GetSteamGameServerInitCalls() == 1
    assert lib.QLR_SteamworksMock_GetSteamGameServerLastInitGamePort() == 27961
    assert lib.QLR_SteamworksMock_GetSteamGameServerLastInitServerMode() == 2
    assert lib.QLR_SteamworksMock_GetSteamGameServerLastInitVersion() == b"custom-build"


def test_shutdown_cascades_game_server_shutdown(steamworks_harness: tuple[ctypes.CDLL, bool]) -> None:
    lib, enabled = steamworks_harness

    if not enabled:
        lib.QLR_Steamworks_Shutdown()
        return

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()

    assert lib.QLR_Steamworks_Init()
    assert lib.QLR_Steamworks_ServerInit(0x01020304, 27960, 1, 1)

    lib.QLR_Steamworks_Shutdown()

    assert lib.QLR_SteamworksMock_GetSteamGameServerShutdownCalls() == 1
    assert not lib.QLR_Steamworks_ServerIsInitialised()


def test_lobby_helpers_use_mapped_matchmaking_slots(steamworks_harness: tuple[ctypes.CDLL, bool]) -> None:
    lib, enabled = steamworks_harness

    if not enabled:
        assert not lib.QLR_Steamworks_CreateLobby(24)
        assert not lib.QLR_Steamworks_LeaveLobby(0x01234567, 0x89ABCDEF)
        assert not lib.QLR_Steamworks_JoinLobby(0xAAAAAAAA, 0xBBBBBBBB)
        assert not lib.QLR_Steamworks_SetLobbyServer(0x33333333, 0x44444444, 0x01020304, 27960)
        assert not lib.QLR_Steamworks_ShowInviteOverlay(0xCCCCCCCC, 0xDDDDDDDD)
        assert not lib.QLR_Steamworks_InviteUserToLobby(0x11111111, 0x22222222, 0x33333333, 0x44444444)
        assert not lib.QLR_Steamworks_InviteUserToGame(0x55555555, 0x66666666, b"+connect 1.2.3.4:27960")
        assert not lib.QLR_Steamworks_SayLobby(0x11111111, 0x22222222, b"hello lobby")
        assert not lib.QLR_Steamworks_RequestUserStats(0x12345678, 0x9ABCDEF0)
        return

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()

    assert lib.QLR_Steamworks_CreateLobby(24)
    assert lib.QLR_Steamworks_LeaveLobby(0x01234567, 0x89ABCDEF)
    assert lib.QLR_Steamworks_JoinLobby(0xAAAAAAAA, 0xBBBBBBBB)
    assert lib.QLR_Steamworks_SetLobbyServer(0x33333333, 0x44444444, 0x01020304, 27960)
    assert lib.QLR_Steamworks_ShowInviteOverlay(0xCCCCCCCC, 0xDDDDDDDD)
    assert lib.QLR_Steamworks_InviteUserToLobby(0x11111111, 0x22222222, 0x33333333, 0x44444444)
    assert lib.QLR_Steamworks_InviteUserToGame(0x55555555, 0x66666666, b"+connect 16909060:27960")
    assert lib.QLR_Steamworks_SayLobby(0x11111111, 0x22222222, b"hello lobby")
    assert lib.QLR_Steamworks_RequestUserStats(0x12345678, 0x9ABCDEF0)

    assert lib.QLR_SteamworksMock_GetLobbyCreateCalls() == 1
    assert lib.QLR_SteamworksMock_GetLobbyLeaveCalls() == 1
    assert lib.QLR_SteamworksMock_GetLobbyJoinCalls() == 1
    assert lib.QLR_SteamworksMock_GetLobbySetServerCalls() == 1
    assert lib.QLR_SteamworksMock_GetLobbyInviteCalls() == 1
    assert lib.QLR_SteamworksMock_GetLobbyUserInviteCalls() == 1
    assert lib.QLR_SteamworksMock_GetLobbySayCalls() == 1
    assert lib.QLR_SteamworksMock_GetUserStatsRequestCalls() == 1
    assert lib.QLR_SteamworksMock_GetGameInviteCalls() == 1
    assert lib.QLR_SteamworksMock_GetLobbyCreateType() == 2
    assert lib.QLR_SteamworksMock_GetLobbyCreateMaxMembers() == 24
    assert lib.QLR_SteamworksMock_GetLobbyLeaveId() == 0x89ABCDEF01234567
    assert lib.QLR_SteamworksMock_GetLobbyJoinId() == 0xBBBBBBBBAAAAAAAA
    assert lib.QLR_SteamworksMock_GetLobbySetServerId() == 0x4444444433333333
    assert lib.QLR_SteamworksMock_GetLobbySetServerIp() == 0x01020304
    assert lib.QLR_SteamworksMock_GetLobbySetServerPort() == 27960
    assert lib.QLR_SteamworksMock_GetLobbySetServerGameServerId() == 0x4444444433333333
    assert lib.QLR_SteamworksMock_GetLobbyInviteId() == 0xDDDDDDDDCCCCCCCC
    assert lib.QLR_SteamworksMock_GetLobbyUserInviteLobbyId() == 0x2222222211111111
    assert lib.QLR_SteamworksMock_GetLobbyUserInviteTargetId() == 0x4444444433333333
    assert lib.QLR_SteamworksMock_GetLobbySayId() == 0x2222222211111111
    assert lib.QLR_SteamworksMock_GetLobbySayMessage() == b"hello lobby"
    assert lib.QLR_SteamworksMock_GetUserStatsRequestId() == 0x9ABCDEF012345678
    assert lib.QLR_SteamworksMock_GetGameInviteTargetId() == 0x6666666655555555
    assert lib.QLR_SteamworksMock_GetGameInviteConnectString() == b"+connect 16909060:27960"


def test_favorite_server_helper_uses_mapped_matchmaking_slots(steamworks_harness: tuple[ctypes.CDLL, bool]) -> None:
    lib, enabled = steamworks_harness

    if not enabled:
        assert not lib.QLR_Steamworks_SetFavoriteServer(0x01020304, 27960, 1)
        assert not lib.QLR_Steamworks_SetFavoriteServer(0x01020304, 27960, 0)
        return

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()

    assert lib.QLR_Steamworks_SetFavoriteServer(0x01020304, 27960, 1)
    assert lib.QLR_SteamworksMock_GetFavoriteAddCalls() == 1
    assert lib.QLR_SteamworksMock_GetFavoriteRemoveCalls() == 0
    assert lib.QLR_SteamworksMock_GetFavoriteLastAppId() == 0x54100
    assert lib.QLR_SteamworksMock_GetFavoriteLastIp() == 0x01020304
    assert lib.QLR_SteamworksMock_GetFavoriteLastConnPort() == 27960
    assert lib.QLR_SteamworksMock_GetFavoriteLastQueryPort() == 27960
    assert lib.QLR_SteamworksMock_GetFavoriteLastFlags() == 1
    assert lib.QLR_SteamworksMock_GetFavoriteLastPlayed() > 0

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()

    assert lib.QLR_Steamworks_SetFavoriteServer(0x0A0B0C0D, 27961, 0)
    assert lib.QLR_SteamworksMock_GetFavoriteAddCalls() == 0
    assert lib.QLR_SteamworksMock_GetFavoriteRemoveCalls() == 1
    assert lib.QLR_SteamworksMock_GetFavoriteLastAppId() == 0x54100
    assert lib.QLR_SteamworksMock_GetFavoriteLastIp() == 0x0A0B0C0D
    assert lib.QLR_SteamworksMock_GetFavoriteLastConnPort() == 27961
    assert lib.QLR_SteamworksMock_GetFavoriteLastQueryPort() == 27961
    assert lib.QLR_SteamworksMock_GetFavoriteLastFlags() == 1
    assert lib.QLR_SteamworksMock_GetFavoriteLastPlayed() == 0

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()
    lib.QLR_SteamworksMock_SetFavoriteResults(-1, 0)

    assert not lib.QLR_Steamworks_SetFavoriteServer(0x01020304, 27960, 1)
    assert lib.QLR_SteamworksMock_GetFavoriteAddCalls() == 1

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()
    lib.QLR_SteamworksMock_SetFavoriteResults(1, 0)

    assert not lib.QLR_Steamworks_SetFavoriteServer(0x01020304, 27960, 0)
    assert lib.QLR_SteamworksMock_GetFavoriteRemoveCalls() == 1


def test_legacy_p2p_wrappers_use_mapped_steamnetworking_slots(steamworks_harness: tuple[ctypes.CDLL, bool]) -> None:
    lib, enabled = steamworks_harness
    steam_id = 0x0110000102030405
    payload_bytes = b"voice"
    payload = ctypes.create_string_buffer(payload_bytes)
    packet_size = ctypes.c_uint32(123)
    remote_id = ctypes.c_uint64(0xFFFFFFFFFFFFFFFF)
    read_buffer = ctypes.create_string_buffer(32)

    if not enabled:
        assert not lib.QLR_Steamworks_SendP2PPacket(steam_id, payload, len(payload_bytes), 1, 16)
        assert not lib.QLR_Steamworks_IsP2PPacketAvailable(ctypes.byref(packet_size), 16)
        assert packet_size.value == 0
        assert not lib.QLR_Steamworks_ReadP2PPacket(
            read_buffer,
            len(read_buffer),
            ctypes.byref(packet_size),
            ctypes.byref(remote_id),
            16,
        )
        assert packet_size.value == 0
        assert remote_id.value == 0
        assert not lib.QLR_Steamworks_AcceptP2PSession(steam_id)
        return

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()

    assert lib.QLR_Steamworks_SendP2PPacket(steam_id, payload, len(payload_bytes), 1, 16)
    assert lib.QLR_SteamworksMock_GetP2PSendCalls() == 1
    assert lib.QLR_SteamworksMock_GetP2PLastSendSteamId() == steam_id
    assert lib.QLR_SteamworksMock_GetP2PLastSendLength() == len(payload_bytes)
    assert lib.QLR_SteamworksMock_GetP2PLastSendType() == 1
    assert lib.QLR_SteamworksMock_GetP2PLastSendChannel() == 16
    for index, value in enumerate(payload_bytes):
        assert lib.QLR_SteamworksMock_GetP2PLastSendByte(index) == value

    read_payload = b"packet"
    read_payload_buffer = ctypes.create_string_buffer(read_payload)
    lib.QLR_SteamworksMock_SetP2PReadPacket(steam_id, read_payload_buffer, len(read_payload))

    packet_size.value = 0
    assert lib.QLR_Steamworks_IsP2PPacketAvailable(ctypes.byref(packet_size), 16)
    assert packet_size.value == len(read_payload)
    assert lib.QLR_SteamworksMock_GetP2PAvailableCalls() == 1
    assert lib.QLR_SteamworksMock_GetP2PLastAvailableChannel() == 16

    assert lib.QLR_Steamworks_ReadP2PPacket(
        read_buffer,
        len(read_buffer),
        ctypes.byref(packet_size),
        ctypes.byref(remote_id),
        16,
    )
    assert packet_size.value == len(read_payload)
    assert remote_id.value == steam_id
    assert read_buffer.raw[: packet_size.value] == read_payload
    assert lib.QLR_SteamworksMock_GetP2PReadCalls() == 1
    assert lib.QLR_SteamworksMock_GetP2PLastReadChannel() == 16

    assert lib.QLR_Steamworks_AcceptP2PSession(steam_id)
    assert lib.QLR_SteamworksMock_GetP2PAcceptCalls() == 1
    assert lib.QLR_SteamworksMock_GetP2PLastAcceptSteamId() == steam_id

    lib.QLR_SteamworksMock_SetP2PResults(0, 0, 0, 0)
    assert not lib.QLR_Steamworks_SendP2PPacket(steam_id, payload, len(payload_bytes), 1, 16)
    packet_size.value = 123
    assert not lib.QLR_Steamworks_IsP2PPacketAvailable(ctypes.byref(packet_size), 16)
    assert packet_size.value == 0
    remote_id.value = 0xFFFFFFFFFFFFFFFF
    assert not lib.QLR_Steamworks_ReadP2PPacket(
        read_buffer,
        len(read_buffer),
        ctypes.byref(packet_size),
        ctypes.byref(remote_id),
        16,
    )
    assert packet_size.value == 0
    assert remote_id.value == 0
    assert not lib.QLR_Steamworks_AcceptP2PSession(steam_id)


def test_legacy_game_server_p2p_wrappers_use_mapped_networking_slots(steamworks_harness: tuple[ctypes.CDLL, bool]) -> None:
    lib, enabled = steamworks_harness
    steam_id = 0x011000010A0B0C0D
    payload_bytes = b"hello"
    payload = ctypes.create_string_buffer(payload_bytes)
    packet_size = ctypes.c_uint32(123)
    remote_id = ctypes.c_uint64(0xFFFFFFFFFFFFFFFF)
    read_buffer = ctypes.create_string_buffer(32)
    outgoing_buffer = ctypes.create_string_buffer(32)
    outgoing_ip = ctypes.c_uint32(0xFFFFFFFF)
    outgoing_port = ctypes.c_uint16(0xFFFF)

    if not enabled:
        assert not lib.QLR_Steamworks_ServerSendP2PPacket(steam_id, payload, len(payload_bytes), 2, 16)
        assert not lib.QLR_Steamworks_ServerIsP2PPacketAvailable(ctypes.byref(packet_size), 16)
        assert packet_size.value == 0
        assert not lib.QLR_Steamworks_ServerReadP2PPacket(
            read_buffer,
            len(read_buffer),
            ctypes.byref(packet_size),
            ctypes.byref(remote_id),
            16,
        )
        assert packet_size.value == 0
        assert remote_id.value == 0
        assert lib.QLR_Steamworks_ServerGetNextOutgoingPacket(
            outgoing_buffer,
            len(outgoing_buffer),
            ctypes.byref(outgoing_ip),
            ctypes.byref(outgoing_port),
        ) == 0
        assert outgoing_ip.value == 0
        assert outgoing_port.value == 0
        assert not lib.QLR_Steamworks_ServerAcceptP2PSession(steam_id)
        return

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()
    assert lib.QLR_Steamworks_ServerInit(0, 27960, 1, 1)

    assert lib.QLR_Steamworks_ServerSendP2PPacket(steam_id, payload, len(payload_bytes), 2, 16)
    assert lib.QLR_SteamworksMock_GetServerP2PSendCalls() == 1
    assert lib.QLR_SteamworksMock_GetServerP2PLastSendSteamId() == steam_id
    assert lib.QLR_SteamworksMock_GetServerP2PLastSendLength() == len(payload_bytes)
    assert lib.QLR_SteamworksMock_GetServerP2PLastSendType() == 2
    assert lib.QLR_SteamworksMock_GetServerP2PLastSendChannel() == 16
    for index, value in enumerate(payload_bytes):
        assert lib.QLR_SteamworksMock_GetServerP2PLastSendByte(index) == value

    read_payload = b"relay"
    read_payload_buffer = ctypes.create_string_buffer(read_payload)
    lib.QLR_SteamworksMock_SetServerP2PReadPacket(steam_id, read_payload_buffer, len(read_payload))

    packet_size.value = 0
    assert lib.QLR_Steamworks_ServerIsP2PPacketAvailable(ctypes.byref(packet_size), 16)
    assert packet_size.value == len(read_payload)
    assert lib.QLR_SteamworksMock_GetServerP2PAvailableCalls() == 1
    assert lib.QLR_SteamworksMock_GetServerP2PLastAvailableChannel() == 16

    assert lib.QLR_Steamworks_ServerReadP2PPacket(
        read_buffer,
        len(read_buffer),
        ctypes.byref(packet_size),
        ctypes.byref(remote_id),
        16,
    )
    assert packet_size.value == len(read_payload)
    assert remote_id.value == steam_id
    assert read_buffer.raw[: packet_size.value] == read_payload
    assert lib.QLR_SteamworksMock_GetServerP2PReadCalls() == 1
    assert lib.QLR_SteamworksMock_GetServerP2PLastReadChannel() == 16

    assert lib.QLR_Steamworks_ServerAcceptP2PSession(steam_id)
    assert lib.QLR_SteamworksMock_GetServerP2PAcceptCalls() == 1
    assert lib.QLR_SteamworksMock_GetServerP2PLastAcceptSteamId() == steam_id

    outgoing_payload = b"udp!!"
    outgoing_payload_buffer = ctypes.create_string_buffer(outgoing_payload)
    lib.QLR_SteamworksMock_SetServerOutgoingPacket(
        outgoing_payload_buffer,
        len(outgoing_payload),
        0x01020304,
        27960,
    )

    assert lib.QLR_Steamworks_ServerGetNextOutgoingPacket(
        outgoing_buffer,
        len(outgoing_buffer),
        ctypes.byref(outgoing_ip),
        ctypes.byref(outgoing_port),
    ) == len(outgoing_payload)
    assert outgoing_buffer.raw[: len(outgoing_payload)] == outgoing_payload
    assert outgoing_ip.value == 0x01020304
    assert outgoing_port.value == 27960
    assert lib.QLR_SteamworksMock_GetServerOutgoingPacketCalls() == 1
    assert lib.QLR_Steamworks_ServerGetNextOutgoingPacket(
        outgoing_buffer,
        len(outgoing_buffer),
        ctypes.byref(outgoing_ip),
        ctypes.byref(outgoing_port),
    ) == 0
    assert lib.QLR_SteamworksMock_GetServerOutgoingPacketCalls() == 2

    lib.QLR_SteamworksMock_SetServerP2PResults(0, 0, 0, 0)
    assert not lib.QLR_Steamworks_ServerSendP2PPacket(steam_id, payload, len(payload_bytes), 2, 16)
    packet_size.value = 123
    assert not lib.QLR_Steamworks_ServerIsP2PPacketAvailable(ctypes.byref(packet_size), 16)
    assert packet_size.value == 0
    remote_id.value = 0xFFFFFFFFFFFFFFFF
    assert not lib.QLR_Steamworks_ServerReadP2PPacket(
        read_buffer,
        len(read_buffer),
        ctypes.byref(packet_size),
        ctypes.byref(remote_id),
        16,
    )
    assert packet_size.value == 0
    assert remote_id.value == 0
    assert not lib.QLR_Steamworks_ServerAcceptP2PSession(steam_id)


def test_set_lobby_server_requires_local_lobby_ownership(steamworks_harness: tuple[ctypes.CDLL, bool]) -> None:
    lib, enabled = steamworks_harness

    if not enabled:
        return

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()
    lib.QLR_SteamworksMock_SetSteamId(0x0123456789ABCDEF)
    lib.QLR_SteamworksMock_SetLobbyOwnerId(0x0FEDCBA987654321)

    assert not lib.QLR_Steamworks_SetLobbyServer(0xAAAAAAAA, 0xBBBBBBBB, 0x7F000001, 27960)
    assert lib.QLR_SteamworksMock_GetLobbySetServerCalls() == 0


def test_workshop_helpers_use_mapped_ugc_slots(steamworks_harness: tuple[ctypes.CDLL, bool]) -> None:
    lib, enabled = steamworks_harness

    if not enabled:
        assert not lib.QLR_Steamworks_SubscribeItem(0xAAAAAAAA, 0xBBBBBBBB)
        assert not lib.QLR_Steamworks_UnsubscribeItem(0xAAAAAAAA, 0xBBBBBBBB)
        assert not lib.QLR_Steamworks_DownloadItem(0xAAAAAAAA, 0xBBBBBBBB, 1)
        return

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()
    lib.QLR_SteamworksMock_SetUGCItemState(0)

    assert not lib.QLR_Steamworks_SubscribeItem(0xAAAAAAAA, 0xBBBBBBBB)
    assert lib.QLR_SteamworksMock_GetUGCSubscribeCalls() == 1

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()
    lib.QLR_SteamworksMock_SetUGCItemState(4)
    lib.QLR_SteamworksMock_SetUGCDownloadInfo(123, 456)

    assert lib.QLR_Steamworks_SubscribeItem(0xAAAAAAAA, 0xBBBBBBBB)
    assert lib.QLR_Steamworks_UnsubscribeItem(0xAAAAAAAA, 0xBBBBBBBB)
    assert lib.QLR_Steamworks_DownloadItem(0xAAAAAAAA, 0xBBBBBBBB, 1)

    assert lib.QLR_SteamworksMock_GetUGCSubscribeCalls() == 1
    assert lib.QLR_SteamworksMock_GetUGCUnsubscribeCalls() == 1
    assert lib.QLR_SteamworksMock_GetUGCDownloadCalls() == 1
    assert lib.QLR_SteamworksMock_GetUGCLastItemId() == 0xBBBBBBBBAAAAAAAA
    assert lib.QLR_SteamworksMock_GetUGCLastHighPriority() == 1


@pytest.mark.parametrize("filter_value", [0, 1, 0xFFFFFFFF])
def test_all_ugc_query_forwards_filter_to_retail_query_slot(
    steamworks_harness: tuple[ctypes.CDLL, bool],
    filter_value: int,
) -> None:
    lib, enabled = steamworks_harness

    if not enabled:
        assert not lib.QLR_Steamworks_RequestAllUGCQuery(filter_value)
        assert lib.QLR_SteamworksMock_GetUGCCreateQueryCalls() == 0
        return

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()
    lib.QLR_SteamworksMock_SetAppId(0x54100)

    assert lib.QLR_Steamworks_RegisterHarnessCallbacks()
    try:
        assert lib.QLR_Steamworks_RequestAllUGCQuery(filter_value)

        assert lib.QLR_SteamworksMock_GetUGCCreateQueryCalls() == 1
        assert lib.QLR_SteamworksMock_GetUGCSendQueryCalls() == 1
        assert lib.QLR_SteamworksMock_GetUGCReleaseQueryCalls() == 0
        assert lib.QLR_SteamworksMock_GetRegisterCallResultCalls() == 1
        assert lib.QLR_SteamworksMock_GetUGCLastQueryType() == 1
        assert lib.QLR_SteamworksMock_GetUGCLastMatchingType() == 0
        assert lib.QLR_SteamworksMock_GetUGCLastCreatorAppId() == 0x54100
        assert lib.QLR_SteamworksMock_GetUGCLastConsumerAppId() == 0x54100
        assert lib.QLR_SteamworksMock_GetUGCLastFilter() == filter_value
        assert lib.QLR_SteamworksMock_GetUGCLastQueryHandle() == 0x1122334455667788
        assert lib.QLR_SteamworksMock_GetUGCLastSentQueryHandle() == 0x1122334455667788
        assert lib.QLR_SteamworksMock_GetUGCLastReleasedQueryHandle() == 0
    finally:
        lib.QLR_Steamworks_UnregisterHarnessCallbacks()


def test_workshop_subscription_enumeration_uses_retail_ugc_mount_slots(
    steamworks_harness: tuple[ctypes.CDLL, bool],
) -> None:
    lib, enabled = steamworks_harness
    subscribed_items = (ctypes.c_uint64 * 3)(
        0x0123456789ABCDEF,
        0x1111111122222222,
        0x3333333344444444,
    )
    copied_items = (ctypes.c_uint64 * 2)()
    size_on_disk = ctypes.c_uint64()
    timestamp = ctypes.c_uint32()
    install_folder = ctypes.create_string_buffer(260)

    if not enabled:
        assert lib.QLR_Steamworks_GetNumSubscribedItems() == 0
        assert lib.QLR_Steamworks_GetSubscribedItems(copied_items, len(copied_items)) == 0
        assert not lib.QLR_Steamworks_GetItemInstallInfo(
            0x89ABCDEF,
            0x01234567,
            ctypes.byref(size_on_disk),
            install_folder,
            len(install_folder),
            ctypes.byref(timestamp),
        )
        return

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()
    lib.QLR_SteamworksMock_SetSubscribedItems(subscribed_items, len(subscribed_items))
    lib.QLR_SteamworksMock_SetUGCInstallInfo(
        subscribed_items[1],
        987654321,
        b"C:\\Workshop\\1111111122222222",
        77,
    )

    assert lib.QLR_Steamworks_GetNumSubscribedItems() == 3
    assert lib.QLR_Steamworks_GetSubscribedItems(copied_items, len(copied_items)) == 2
    assert list(copied_items) == [
        0x0123456789ABCDEF,
        0x1111111122222222,
    ]

    assert lib.QLR_Steamworks_GetItemInstallInfo(
        0x22222222,
        0x11111111,
        ctypes.byref(size_on_disk),
        install_folder,
        len(install_folder),
        ctypes.byref(timestamp),
    )
    assert size_on_disk.value == 987654321
    assert timestamp.value == 77
    assert install_folder.value == b"C:\\Workshop\\1111111122222222"


def test_callback_bundle_registration_and_dispatch_reconstructs_retail_client_owner(
    steamworks_harness: tuple[ctypes.CDLL, bool],
) -> None:
    lib, enabled = steamworks_harness

    if not enabled:
        return

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()
    lib.QLR_SteamworksMock_SetAppId(0x54100)
    lib.QLR_SteamworksMock_SetLobbyChatEntryMessage(b"queued lobby chat")

    assert lib.QLR_Steamworks_RegisterHarnessCallbacks()
    assert lib.QLR_SteamworksMock_GetRegisterCallbackCalls() == 18

    assert lib.QLR_SteamworksMock_QueueRichPresenceJoinRequested(0x0123456789ABCDEF, b"connect 127.0.0.1")
    lib.QLR_Steamworks_RunCallbackPump()

    assert lib.QLR_SteamworksMock_GetClientCallbackCaptureCount() == 1
    assert lib.QLR_SteamworksMock_GetLastCallbackKind() == b"rich_presence"
    assert lib.QLR_SteamworksMock_GetLastCallbackText() == b"connect 127.0.0.1"
    assert lib.QLR_SteamworksMock_GetLastCallbackId() == 0x0123456789ABCDEF

    assert lib.QLR_SteamworksMock_QueueAvatarImageLoaded(0x0FEDCBA987654321, 13, 64, 64)
    lib.QLR_Steamworks_RunCallbackPump()

    assert lib.QLR_SteamworksMock_GetClientCallbackCaptureCount() == 2
    assert lib.QLR_SteamworksMock_GetLastCallbackKind() == b"avatar_image_loaded"
    assert lib.QLR_SteamworksMock_GetLastCallbackId() == 0x0FEDCBA987654321
    assert lib.QLR_SteamworksMock_GetLastCallbackAuxId() == 13
    assert lib.QLR_SteamworksMock_GetLastCallbackAppId() == 64
    assert lib.QLR_SteamworksMock_GetLastCallbackResult() == 64

    assert lib.QLR_SteamworksMock_QueueLobbyEnter(0x0FEDCBA987654321, 7, 0, 1)
    lib.QLR_Steamworks_RunCallbackPump()

    assert lib.QLR_SteamworksMock_GetClientCallbackCaptureCount() == 3
    assert lib.QLR_SteamworksMock_GetLastCallbackKind() == b"lobby_enter"
    assert lib.QLR_SteamworksMock_GetLastCallbackId() == 0x0FEDCBA987654321
    assert lib.QLR_SteamworksMock_GetLastCallbackAppId() == 7
    assert lib.QLR_SteamworksMock_GetLastCallbackResult() == 1

    assert lib.QLR_SteamworksMock_QueueMicroAuthorizationResponse(0x54100, 99, 1)
    lib.QLR_Steamworks_RunCallbackPump()

    assert lib.QLR_SteamworksMock_GetClientCallbackCaptureCount() == 4
    assert lib.QLR_SteamworksMock_GetLastCallbackKind() == b"microtxn"
    assert lib.QLR_SteamworksMock_GetLastCallbackId() == 99
    assert lib.QLR_SteamworksMock_GetLastCallbackAppId() == 0x54100
    assert lib.QLR_SteamworksMock_GetLastCallbackResult() == 1

    assert lib.QLR_SteamworksMock_QueueItemInstalled(0x54100, 0x89ABCDEF, 0x01234567)
    lib.QLR_Steamworks_RunCallbackPump()

    assert lib.QLR_SteamworksMock_GetClientCallbackCaptureCount() == 5
    assert lib.QLR_SteamworksMock_GetLastCallbackKind() == b"workshop_installed"
    assert lib.QLR_SteamworksMock_GetLastCallbackId() == 0x0123456789ABCDEF
    assert lib.QLR_SteamworksMock_GetLastCallbackAppId() == 0x54100
    assert lib.QLR_SteamworksMock_GetLastCallbackResult() == 0

    assert lib.QLR_SteamworksMock_QueueDownloadItemResult(0x54100, 0x89ABCDEF, 0x01234567, 1)
    lib.QLR_Steamworks_RunCallbackPump()

    assert lib.QLR_SteamworksMock_GetClientCallbackCaptureCount() == 6
    assert lib.QLR_SteamworksMock_GetLastCallbackKind() == b"workshop_download_result"
    assert lib.QLR_SteamworksMock_GetLastCallbackId() == 0x0123456789ABCDEF
    assert lib.QLR_SteamworksMock_GetLastCallbackAppId() == 0x54100
    assert lib.QLR_SteamworksMock_GetLastCallbackResult() == 1

    lib.QLR_Steamworks_UnregisterHarnessCallbacks()
    assert lib.QLR_SteamworksMock_GetUnregisterCallbackCalls() == 18


def test_ugc_call_result_binding_routes_through_registered_client_bundle(
    steamworks_harness: tuple[ctypes.CDLL, bool],
) -> None:
    lib, enabled = steamworks_harness

    if not enabled:
        return

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()

    assert lib.QLR_Steamworks_RegisterHarnessCallbacks()
    assert lib.QLR_Steamworks_BindUGCQueryCallResult(0xAABBCCDD)
    assert lib.QLR_SteamworksMock_GetRegisterCallResultCalls() == 1

    assert lib.QLR_SteamworksMock_QueueUGCQueryCompleted(0xAABBCCDD, 0x1122334455667788, 1, 3, 5, 1)
    lib.QLR_Steamworks_RunCallbackPump()

    assert lib.QLR_SteamworksMock_GetClientCallbackCaptureCount() == 1
    assert lib.QLR_SteamworksMock_GetLastCallbackKind() == b"ugc"
    assert lib.QLR_SteamworksMock_GetLastCallbackId() == 0xAABBCCDD
    assert lib.QLR_SteamworksMock_GetLastCallbackAuxId() == 0x1122334455667788
    assert lib.QLR_SteamworksMock_GetLastCallbackAppId() == 3
    assert lib.QLR_SteamworksMock_GetLastCallbackResult() == 1

    lib.QLR_Steamworks_UnregisterHarnessCallbacks()
    assert lib.QLR_SteamworksMock_GetUnregisterCallResultCalls() == 1
