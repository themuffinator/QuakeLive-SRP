# Quake Live Steam Mapping Round 617: Lobby Callback Publication Lifecycle

Date: 2026-06-12

## Scope

This round pins the Steam lobby callback publication lifecycle for the retail
`quakelive_steam.exe` host and the SRP reconstruction. The focus is the
runtime path that turns Steam matchmaking callbacks into web-menu/browser
events:

- `LobbyCreated_t`
- `LobbyEnter_t`
- `LobbyChatUpdate_t`
- `LobbyChatMsg_t`
- `LobbyDataUpdate_t`
- `LobbyGameCreated_t`
- `LobbyKicked_t`
- `GameLobbyJoinRequested_t`

No live Steam service behavior was enabled or exercised. The reconstruction
remains behind `QL_BUILD_ONLINE_SERVICES` / `QL_BUILD_STEAMWORKS`, with the
default build retaining compatibility stubs.

## Retail Evidence

Observed Binary Ninja HLIL and Ghidra evidence:

- Alias map:
  - `FUN_00464bf0` -> `SteamLobbyCallbacks_OnLobbyCreated`
  - `FUN_00464d90` -> `SteamLobbyCallbacks_OnLobbyEnter`
  - `FUN_004652e0` -> `SteamLobbyCallbacks_OnLobbyChatUpdate`
  - `FUN_004645a0` -> `SteamLobbyCallbacks_OnLobbyChatMessage`
  - `FUN_00465490` -> `SteamLobbyCallbacks_OnLobbyDataUpdate`
  - `FUN_00464720` -> `SteamLobbyCallbacks_OnLobbyGameCreated`
  - `FUN_00464830` -> `SteamLobbyCallbacks_OnLobbyKicked`
  - `FUN_00464900` -> `SteamLobbyCallbacks_OnGameLobbyJoinRequested`
  - `FUN_004656a0` -> `SteamLobbyCallbacks_Init`
  - `FUN_00465840` -> `SteamLobby_Init`
- Ghidra function rows keep the callback bodies and init surfaces at
  `004645a0`, `00464720`, `00464830`, `00464900`, `00464bf0`, `00464d90`,
  `004652e0`, `00465490`, `004656a0`, and `00465840`.
- Ghidra imports confirm use of `SteamAPI_RegisterCallback`, `SteamFriends`,
  and `SteamMatchmaking`.
- Ghidra analysis symbols expose eight imported
  `CCallback<class_SteamLobbyCallbacks,...>::vftable` entries, one for each
  lobby callback payload type.
- HLIL callback registration order in `sub_4656a0` is:
  `0x201`, `0x1f8`, `0x1fa`, `0x1fb`, `0x1f9`, `0x1fd`, `0x200`, `0x14d`.
- HLIL strings and publication calls cover:
  - `lobby.%s.create`
  - `lobby.%s.enter`
  - `lobby.%s.user.joined`
  - `lobby.%s.user.left`
  - `lobby.%s.chat`
  - `lobby.%llu.updated`
  - `lobby.%llu.game_created`
  - `lobby.%llu.kicked`
  - `lobby.%llu.join_requested`
  - `lobby.%s.left`
  - `lobby.error`

Two state-management details are now treated as pinned retail behavior:

- successful lobby enter calls the retail leave-current helper before storing
  the newly entered lobby id;
- kicked publication occurs before the retained current-lobby words are
  cleared.

## Source Reconstruction

The SRP source now has explicit guard coverage for the following mapped
behavior:

- raw callback payload layouts and `QL_STEAMWORKS_STATIC_ASSERT_SIZE` entries
  match the retail callback ids and payload sizes:
  `0x10`, `0x18`, `0x20`, `0x18`, `0x18`, `0x18`, `0x18`, `0x10`;
- `QL_Steamworks_RegisterLobbyCallbacks` prepares and registers the eight
  callback objects in the retail order, while unregistering in reverse order;
- dispatch shims copy raw payload fields into typed SRP event structs, with
  `LobbyChatMsg_t` additionally pulling the full chat payload through
  `QL_Steamworks_ReadLobbyChatMessage`;
- `CL_Steam_Lobby_OnLobbyCreated` maps success to `lobby.%s.create` after the
  retail-style `"hello" = "world"` lobby-data write, and failure to
  `lobby.error`;
- `CL_Steam_Lobby_OnLobbyEnter` maps successful enter to `lobby.%s.enter`,
  preserving the retail owner, lobby-data, player-count, member-list, and
  leave-old-lobby behavior;
- `CL_Steam_Lobby_OnLobbyChatUpdate` uses state bit `0x01` to choose
  `lobby.%s.user.joined` versus `lobby.%s.user.left`;
- `CL_Steam_Lobby_OnLobbyChatMessage` ignores non-chat entry type values before
  publishing `lobby.%s.chat`;
- `CL_Steam_Lobby_OnLobbyDataUpdate` remains a thin
  `lobby.%llu.updated` / `{"id":"..."}` publication rather than rebuilding the
  full lobby-data object;
- `CL_Steam_Lobby_OnLobbyGameCreated`,
  `CL_Steam_Lobby_OnLobbyKicked`, and
  `CL_Steam_Lobby_OnGameLobbyJoinRequested` match the corresponding retail
  publication names and payload ownership;
- `CL_Steam_LeaveCurrentLobby` calls the platform leave wrapper, publishes
  `lobby.%s.left`, and then clears the retained lobby identity.

## Compatibility Boundary

This round only pins the callback-publication and retained-current-lobby
contracts. It does not change live service defaults, matchmaking policy, or
network behavior. Steam-backed online service usage remains an explicit
opt-in compatibility surface.

## Validation

New focused parity gate:

```powershell
python -m pytest tests/test_platform_services.py::test_steam_lobby_callback_publication_lifecycle_tracks_round_617 -q --tb=short
```

The gate checks alias names, Ghidra function/import rows, callback vtable
symbols, HLIL publication anchors, raw payload sizes, callback ids,
registration/unregistration order, dispatch field mapping, client-side
publication strings, retained lobby clear/leave policy, disabled header
stubs, this round note, and the Task A486 planning anchor.

## Confidence

- Focused Steam lobby callback publication confidence:
  **before 93% -> after 99%**.
- Focused current-lobby retained-state policy classification:
  **before 94% -> after 99%**.
- Overall Steam launch/runtime integration mapping confidence:
  **93.36% -> 93.38%**.
