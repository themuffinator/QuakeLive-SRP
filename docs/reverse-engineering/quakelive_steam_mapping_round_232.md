# quakelive_steam.exe Mapping Round 232

Date: 2026-05-11

Scope: the retained client Steam/bootstrap registration seam in
`src/code/client/cl_main.c` plus the corresponding startup call sites in
`src/code/qcommon/common.c`, staying inside engine-owned bootstrap logic rather
than external-library implementation work.

## Summary

This round reconstructs two retail Steam bootstrap owners in source instead of
leaving their command and cvar work flattened into `CL_Init`.

Classification mix:

- `0` new engine/client aliases
- `0` engine/client alias renames
- `2` engine/client source reconstruction boundary fixes
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main source-parity wins are:

- restored an explicit `SteamLobby_Init()` helper in
  [`cl_main.c`](../../src/code/client/cl_main.c) for the
  `lobby_autoconnect` / `steam_maxLobbyClients` cvars plus
  `connect_lobby` registration
- restored an explicit `SteamClient_Init()` helper in
  [`cl_main.c`](../../src/code/client/cl_main.c) for callback bootstrap,
  lobby bootstrap, `+voice`, `-voice`, conditional `stats_clear`, and the
  initial `status = "At the main menu"` rich-presence write
- moved the startup calls into the two retained common startup lanes in
  [`common.c`](../../src/code/qcommon/common.c), so the client can rebuild the
  same Steam bootstrap surface both at initial startup and when switching back
  from dedicated mode

## Evidence Notes

- The committed retail common-startup lane calls `sub_461500()` from the
  broader engine bootstrap, outside the later `CL_Init` registration block.
- The committed retail body for `sub_461500` shows:
  - `sub_4659e0()` microtransaction callback bootstrap
  - `sub_465840()` lobby bootstrap
  - `sub_4c81d0("+voice", sub_4603f0)`
  - `sub_4c81d0("-voice", sub_460490)`
  - conditional `sub_4c81d0("stats_clear", sub_460520)`
  - `SteamFriends()->vtable[0xAC]("status", "At the main menu")`
- The committed retail body for `sub_465840` shows:
  - `sub_4ce0d0(..., "lobby_autoconnect", "", 0x100)`
  - `sub_4ce0d0(..., "steam_maxLobbyClients", "16", 1)`
  - `sub_4c81d0("connect_lobby", sub_464aa0)`
- The committed retail `CL_Init` lane still shows `clientviewprofile`,
  `clientfriendinvite`, `QLWebHost_RegisterCommands()`, and
  `sub_460610()` persona sync adjacent to each other, which is a better fit
  with the checked-in source once the broader Steam bootstrap work is moved
  back out of `CL_Init`.

## Source Reconstruction

- [`cl_main.c`](../../src/code/client/cl_main.c) now defines:
  - `static void SteamLobby_Init( void )`
  - `void SteamClient_Init( void )`
- `CL_Init` no longer owns:
  - `lobby_autoconnect`
  - `steam_maxLobbyClients`
  - `connect_lobby`
  - `+voice`
  - `-voice`
  - conditional `stats_clear`
  - callback bootstrap
  - main-menu rich-presence bootstrap
- [`qcommon.h`](../../src/code/qcommon/qcommon.h) now exposes
  `void SteamClient_Init( void );`
- [`common.c`](../../src/code/qcommon/common.c) now calls `SteamClient_Init()`
  in both client startup paths before `CL_Init()`

## Verification

Static/source validation:

- `pytest tests/test_engine_client_command_parity.py tests/test_platform_services.py -q --tb=no -k "steam_client_init or steam_lobby_init or connect_lobby or voice or stats_clear or callback_owner or main_menu_presence_seed or client_steam_command_registration"`
  passed with `5 passed, 85 deselected`
- `git diff --check -- src/code/qcommon/qcommon.h src/code/qcommon/common.c src/code/client/cl_main.c tests/test_engine_client_command_parity.py tests/test_platform_services.py`
  reported only the repo's existing LF -> CRLF normalization warnings on the
  touched text files

Alias accounting for the current dirty worktree:

- before this pass: `2238` raw `quakelive_steam` aliases, `2157` strict
  address-backed aliases
- after this pass: `2238` raw `quakelive_steam` aliases, `2157` strict
  address-backed aliases
- strict Ghidra address-backed coverage after this pass: `39.412%` of `5473`
  committed functions

Parity estimate after this pass:

- strict-retail Steam bootstrap/helper ownership lane: `99%` before,
  `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

The next nearby engine-only pass is to keep separating retail helper ownership
from the remaining flattened client bootstrap and shutdown seams without
expanding into external-library internals.
