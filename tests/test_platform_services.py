from __future__ import annotations

import subprocess
import shutil
import textwrap
import os
from pathlib import Path
from typing import Dict, Tuple

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

_SERVICE_TABLE_PROBE = textwrap.dedent(
    """
    #include <stdio.h>

    #include "src/common/platform/platform_services.c"

#ifndef QL_STEAMWORKS_INIT_RESULT
#define QL_STEAMWORKS_INIT_RESULT 1
#endif

#if QL_BUILD_STEAMWORKS
/*
=============
QL_Steamworks_Init
=============
*/
qboolean QL_Steamworks_Init( void ) {
    return QL_STEAMWORKS_INIT_RESULT;
}
#endif

    static int qlower(int ch) {
        return tolower(ch & 0xff);
    }

    int Q_stricmp( const char *s1, const char *s2 ) {
        if ( !s1 ) {
            s1 = "";
        }
        if ( !s2 ) {
            s2 = "";
        }

        while ( *s1 && *s2 ) {
            int diff = qlower(*s1++) - qlower(*s2++);
            if ( diff ) {
                return diff;
            }
        }

        return qlower(*s1) - qlower(*s2);
    }

    static void dump_descriptor(const char *label, const ql_platform_feature_descriptor *descriptor) {
        const char *provider = descriptor && descriptor->provider ? descriptor->provider : "<null>";
        printf(
            "%s|%s|%d|%d\\n",
            label,
            provider,
            descriptor && descriptor->compiled ? 1 : 0,
            descriptor && descriptor->initialised ? 1 : 0
        );
    }

    int main(void) {
        const ql_platform_service_table *services = QL_GetPlatformServices();
        dump_descriptor("auth", &services->auth);
        dump_descriptor("matchmaking", &services->matchmaking);
        dump_descriptor("workshop", &services->workshop);
        dump_descriptor("overlay", &services->overlay);
        dump_descriptor("stats", &services->stats);
        return 0;
    }
    """
)

_HYBRID_FALLBACK_PROBE = textwrap.dedent(
    """
    #include <stdio.h>
    #include <stdarg.h>
    #include <string.h>
    #include <ctype.h>

    #include "client.h"
    #include "src/common/platform/platform_services.c"
    #include "src/common/platform/backends/platform_backend_steamworks.c"
    #include "src/common/platform/backends/platform_backend_open_steam.c"
    #include "src/common/auth_credentials.c"
    #include "src/code/client/ql_auth.c"

#ifndef QL_STEAMWORKS_INIT_RESULT
#define QL_STEAMWORKS_INIT_RESULT 1
#endif

/*
=============
QL_Steamworks_Init
=============
*/
qboolean QL_Steamworks_Init( void ) {
    return QL_STEAMWORKS_INIT_RESULT;
}

/*
=============
QL_Steamworks_RunCallbacks
=============
*/
void QL_Steamworks_RunCallbacks( void ) {}

/*
=============
QL_Steamworks_RequestAuthTicket
=============
*/
qboolean QL_Steamworks_RequestAuthTicket( char *ticketBuffer, size_t ticketBufferSize, int *ticketLength, uint32_t *ticketHandle ) {
const char *stubTicket = "retry:TICKET-HYBRID-FALLBACK";

if ( ticketBuffer && ticketBufferSize > 0 ) {
Q_strncpyz( ticketBuffer, stubTicket, (int)ticketBufferSize );
}

if ( ticketLength && ticketBuffer ) {
*ticketLength = (int)strlen( ticketBuffer );
}

(void)ticketHandle;
return qtrue;
}

/*
=============
QL_Steamworks_ValidateTicket
=============
*/
qboolean QL_Steamworks_ValidateTicket( const char *ticketHex, ql_auth_response_t *response ) {
(void)ticketHex;
(void)response;
return qfalse;
}

    static int qlower(int ch) {
        return tolower(ch & 0xff);
    }

    void QDECL Com_Printf( const char *fmt, ... ) {
        va_list args;
        va_start(args, fmt);
        vfprintf(stderr, fmt, args);
        va_end(args);
    }

    int QDECL Com_sprintf( char *dest, int size, const char *fmt, ... ) {
        if ( !dest || size <= 0 ) {
            return 0;
        }

        va_list args;
        va_start(args, fmt);
        int written = vsnprintf(dest, (size_t)size, fmt, args);
        va_end(args);

        dest[size - 1] = '\\0';
        return written;
    }

    void Q_strncpyz( char *dest, const char *src, int destsize ) {
        if ( !dest || destsize <= 0 ) {
            return;
        }

        if ( !src ) {
            dest[0] = '\\0';
            return;
        }

        size_t count = destsize > 1 ? (size_t)(destsize - 1) : (size_t)0;
        if ( count == 0 ) {
            dest[0] = '\\0';
            return;
        }

        strncpy(dest, src, count);
        dest[count] = '\\0';
    }

    int Q_stricmp( const char *s1, const char *s2 ) {
        if ( !s1 ) {
            s1 = "";
        }
        if ( !s2 ) {
            s2 = "";
        }

        while ( *s1 && *s2 ) {
            int diff = qlower(*s1++) - qlower(*s2++);
            if ( diff ) {
                return diff;
            }
        }

        return qlower(*s1) - qlower(*s2);
    }

    int Q_stricmpn( const char *s1, const char *s2, int n ) {
        if ( n <= 0 ) {
            return 0;
        }

        if ( !s1 ) {
            s1 = "";
        }
        if ( !s2 ) {
            s2 = "";
        }

        while ( n-- > 0 ) {
            unsigned char c1 = (unsigned char)*s1++;
            unsigned char c2 = (unsigned char)*s2++;
            int diff = qlower(c1) - qlower(c2);
            if ( diff || !c1 || !c2 ) {
                return diff;
            }
        }

        return 0;
    }

/*
=============
CL_OnlineServicesEnabled
=============
*/
qboolean CL_OnlineServicesEnabled( void ) {
#if QL_BUILD_ONLINE_SERVICES
        return qtrue;
#else
        return qfalse;
#endif
}

/*
=============
CL_SteamServicesEnabled
=============
*/
qboolean CL_SteamServicesEnabled( void ) {
#if QL_PLATFORM_HAS_STEAM_SERVICES
        return CL_OnlineServicesEnabled();
#else
        return qfalse;
#endif
}

    int main(void) {
        ql_auth_credential_t credential;
        memset(&credential, 0, sizeof(credential));
        credential.kind = QL_AUTH_CREDENTIAL_STEAM;
        Q_strncpyz(credential.value, "retry:TICKET-ABCDEFGHIJKLMNOP", sizeof(credential.value));
        credential.length = strlen(credential.value);

        ql_auth_response_t response;
        memset(&response, 0, sizeof(response));

        qboolean handled = QL_Auth_ExecuteRequest(&credential, &response);

        printf("handled=%d\\n", handled ? 1 : 0);
        printf("result=%d\\n", response.result);
        printf("outcome=%d\\n", response.outcome);
        printf("message=%s\\n", response.message);
        return 0;
    }
    """
)


def _compile_and_run(
    workdir: Path,
    source: str,
    macros: Dict[str, int],
    *,
    include_client_stub: bool = False,
) -> str:
    workdir.mkdir(parents=True, exist_ok=True)
    c_path = workdir / "probe.c"
    c_path.write_text(source, encoding="utf-8")
    exe_path = workdir / "probe"
    compiler = shutil.which("gcc") or shutil.which("clang") or shutil.which("cc")

    if not compiler:
        pytest.skip("No C compiler found for platform service probe")

    include_args = [f"-I{REPO_ROOT}", "-Isrc/common", "-Isrc/code", "-Isrc/code/game", "-Isrc/code/qcommon"]
    if include_client_stub:
        include_args.insert(0, "-Itests/stubs")

    macro_args = [f"-D{key}={value}" for key, value in macros.items()]
    platform_args = []

    if os.name == "nt":
        platform_args.extend(["-DWIN32", "-D_CRT_SECURE_NO_WARNINGS", "-Wno-return-type"])

    if include_client_stub:
        macro_args.append("-DQL_AUTH_HAS_CLIENT_BACKEND=1")

    compile_cmd = [
        compiler,
        "-std=c99",
        "-Wall",
        "-Werror",
        *platform_args,
        *include_args,
        *macro_args,
        str(c_path),
        "-o",
        str(exe_path),
    ]

    subprocess.run(compile_cmd, cwd=REPO_ROOT, check=True, capture_output=True)
    result = subprocess.run([str(exe_path)], cwd=REPO_ROOT, check=True, capture_output=True, text=True)
    return result.stdout


def _parse_service_output(output: str) -> Dict[str, Tuple[str, bool, bool]]:
    services: Dict[str, Tuple[str, bool, bool]] = {}
    for line in output.strip().splitlines():
        label, provider, compiled, initialised = line.split("|", 3)
        services[label] = (provider, compiled == "1", initialised == "1")
    return services


def _extract_function_block(text: str, signature: str) -> str:
    start = text.find(signature)
    if start == -1:
        raise AssertionError(f"function signature not found: {signature}")

    brace_start = text.find("{", start)
    if brace_start == -1:
        raise AssertionError(f"opening brace not found for: {signature}")

    depth = 0
    for index in range(brace_start, len(text)):
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]

    raise AssertionError(f"unterminated function block for: {signature}")


def test_platform_service_table_tracks_build_flags(tmp_path) -> None:
    build_disabled = {
        "auth": ("Build-disabled (QL_BUILD_ONLINE_SERVICES=0)", False, False),
        "matchmaking": ("Build-disabled (QL_BUILD_ONLINE_SERVICES=0)", False, False),
        "workshop": ("Build-disabled (QL_BUILD_ONLINE_SERVICES=0)", False, False),
        "overlay": ("Build-disabled (QL_BUILD_ONLINE_SERVICES=0)", False, False),
        "stats": ("Build-disabled (QL_BUILD_ONLINE_SERVICES=0)", False, False),
    }

    scenarios = [
        (
            {},
            build_disabled,
        ),
        (
            {"QL_BUILD_ONLINE_SERVICES": 0, "QL_BUILD_STEAMWORKS": 1, "QL_BUILD_OPEN_STEAM": 1},
            build_disabled,
        ),
        (
            {"QL_BUILD_ONLINE_SERVICES": 1, "QL_BUILD_STEAMWORKS": 1, "QL_BUILD_OPEN_STEAM": 0},
            {
                "auth": ("Steamworks", True, True),
                "matchmaking": ("Steamworks", True, True),
                "workshop": ("Steam UGC", True, True),
                "overlay": ("Steam Overlay", True, True),
                "stats": ("Steam Stats", True, True),
            },
        ),
        (
            {"QL_BUILD_ONLINE_SERVICES": 1, "QL_BUILD_STEAMWORKS": 0, "QL_BUILD_OPEN_STEAM": 1},
            {
                "auth": ("Open Steam Adapter", True, True),
                "matchmaking": ("GameNetworkingSockets", True, True),
                "workshop": ("REST UGC Service", True, True),
                "overlay": ("In-Process UI Overlay", True, True),
                "stats": ("Metrics REST Adapter", True, True),
            },
        ),
        (
            {"QL_BUILD_ONLINE_SERVICES": 1, "QL_BUILD_STEAMWORKS": 1, "QL_BUILD_OPEN_STEAM": 1},
            {
                "auth": ("Hybrid", True, True),
                "matchmaking": ("Hybrid: Steamworks + GameNetworkingSockets", True, True),
                "workshop": ("Hybrid: Steam UGC + REST Mirror", True, True),
                "overlay": ("Hybrid: Steam Overlay + In-Process UI", True, True),
                "stats": ("Hybrid: Steam Stats + Metrics REST", True, True),
            },
        ),
        (
            {"QL_BUILD_ONLINE_SERVICES": 1, "QL_BUILD_STEAMWORKS": 1, "QL_BUILD_OPEN_STEAM": 0, "QL_STEAMWORKS_INIT_RESULT": 0},
            {
                "auth": ("Steamworks", True, False),
                "matchmaking": ("Steamworks", True, False),
                "workshop": ("Steam UGC", True, False),
                "overlay": ("Steam Overlay", True, False),
                "stats": ("Steam Stats", True, False),
            },
        ),
        (
            {"QL_BUILD_ONLINE_SERVICES": 1, "QL_BUILD_STEAMWORKS": 1, "QL_BUILD_OPEN_STEAM": 1, "QL_STEAMWORKS_INIT_RESULT": 0},
            {
                "auth": ("Hybrid", True, True),
                "matchmaking": ("Hybrid: Steamworks + GameNetworkingSockets", True, True),
                "workshop": ("Hybrid: Steam UGC + REST Mirror", True, True),
                "overlay": ("Hybrid: Steam Overlay + In-Process UI", True, True),
                "stats": ("Hybrid: Steam Stats + Metrics REST", True, True),
            },
        ),
    ]

    for idx, (macros, expected) in enumerate(scenarios):
        workdir = tmp_path / f"service_probe_{idx}"
        output = _compile_and_run(workdir, _SERVICE_TABLE_PROBE, macros)
        services = _parse_service_output(output)
        assert services == expected


def test_hybrid_fallback_accepts_when_steam_pending(tmp_path) -> None:
    workdir = tmp_path / "hybrid_fallback"
    output = _compile_and_run(
        workdir,
        _HYBRID_FALLBACK_PROBE,
        {"QL_BUILD_ONLINE_SERVICES": 1, "QL_BUILD_STEAMWORKS": 1, "QL_BUILD_OPEN_STEAM": 1},
        include_client_stub=True,
    )

    details = dict(line.split("=", 1) for line in output.strip().splitlines())

    assert details["handled"] == "1"
    assert details["result"] == str(QL_AUTH_RESULT_ACCEPTED := 1)
    assert details["outcome"] == str(QL_AUTH_OUTCOME_SUCCESS := 0)
    assert "Hybrid fallback accepted credential via open adapter" in details["message"]


def test_online_service_bridge_only_hard_stubs_when_build_disabled() -> None:
    cl_cgame = (REPO_ROOT / "src/code/client/cl_cgame.c").read_text(encoding="utf-8")
    cl_ui = (REPO_ROOT / "src/code/client/cl_ui.c").read_text(encoding="utf-8")
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")

    refresh_block = _extract_function_block(cl_cgame, "void CL_RefreshOnlineServicesBridgeState( void )")
    assert "#if !QL_PLATFORM_HAS_ONLINE_SERVICES" in refresh_block
    assert 'Cvar_Set( "ui_browserAwesomium", "0" );' in refresh_block
    assert "CL_GetOverlayServiceDescriptor()" in refresh_block
    assert 'Cvar_Set( "ui_browserAwesomium", overlayAvailable ? "1" : "0" );' in refresh_block

    assert '#include "../../common/platform/platform_config.h"' in ui_main
    assert "#define UI_BROWSER_AWESOMIUM_DEFAULT \"0\"" in ui_main
    assert '"ui_browserAwesomium", UI_BROWSER_AWESOMIUM_DEFAULT, CVAR_TEMP' in ui_main

    show_browser_block = _extract_function_block(cl_cgame, "void CL_Web_ShowBrowser_f( void )")
    assert "#if !QL_PLATFORM_HAS_ONLINE_SERVICES" in show_browser_block
    assert "CL_RefreshOnlineServicesBridgeState();" in show_browser_block
    assert "CL_OnlineServicesEnabled()" not in show_browser_block

    advert_init_block = _extract_function_block(cl_cgame, "static void CL_AdvertisementBridge_InitCGame( void )")
    assert "cl_advertisementBridge.initialised = qtrue;" in advert_init_block
    assert "CL_RefreshOnlineServicesBridgeState();" in advert_init_block

    import82_block = _extract_function_block(cl_ui, "static void QDECL QL_UI_trap_InitAdvertisementBridge( void )")
    assert "CL_RefreshOnlineServicesBridgeState();" in import82_block

    init_ui_block = _extract_function_block(cl_ui, "void CL_InitUI( void )")
    assert "CL_RefreshOnlineServicesBridgeState();" in init_ui_block


def test_disabled_online_services_no_longer_force_console_fallback() -> None:
    cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")
    cl_scrn = (REPO_ROOT / "src/code/client/cl_scrn.c").read_text(encoding="utf-8")
    client_h = (REPO_ROOT / "src/code/client/client.h").read_text(encoding="utf-8")

    assert "CL_UseDisconnectedConsoleFallback" not in client_h
    assert "CL_UseDisconnectedConsoleFallback" not in cl_main
    assert "CL_UseDisconnectedConsoleFallback" not in cl_scrn
    assert "disconnected console fallback active" not in cl_main
    assert "fallback draw path active" not in cl_scrn

    frame_block = _extract_function_block(cl_main, "void CL_Frame ( int msec ) {")
    assert 'VM_Call( uivm, UI_SET_ACTIVE_MENU, UIMENU_MAIN );' in frame_block
    assert "cls.keyCatchers = KEYCATCH_CONSOLE;" not in frame_block
    assert "S_StopBackgroundTrack();" not in frame_block

    draw_block = _extract_function_block(cl_scrn, "void SCR_DrawScreenField( stereoFrame_t stereoFrame ) {")
    assert "uiFullscreen = VM_Call( uivm, UI_IS_FULLSCREEN );" in draw_block
    assert 'VM_Call( uivm, UI_SET_ACTIVE_MENU, UIMENU_MAIN );' in draw_block
    assert "consoleFallback" not in draw_block
