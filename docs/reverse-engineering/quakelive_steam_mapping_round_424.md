# Quake Live Steam Mapping Round 424

Date: 2026-06-07

## Scope

This round reconstructs the final client Steam shutdown wrapper at the normal
engine quit edge. The focus is the retail `SteamAPI_Shutdown` thunk, its
relationship to the adjacent `SteamServer_Shutdown` edge, and the placement of
both calls between common runtime teardown and process exit.

## Evidence

- `references/analysis/quakelive_symbol_aliases.json` promotes
  `sub_460540` as `SteamAPI_Shutdown`.
- Ghidra `functions.csv` carries `SteamAPI_Shutdown,00460540,6,1,unknown`,
  while `imports.txt` confirms the retail import from `STEAM_API.DLL`.
- Binary Ninja HLIL for `quakelive_steam.exe` shows `0x00460540` as a direct
  `SteamAPI_Shutdown` tailcall thunk.
- The retail quit path calls `SteamAPI_Shutdown()` at `0x004c9e97` after common
  engine shutdown and before the following `sub_465d30()`/exit calls.
- Binary Ninja HLIL for `sub_465d30` calls `SteamGameServer_Shutdown()` and
  clears the retained game-server initialisation flag; the common shutdown path
  calls this same server edge before writing `profile.pid`.

## Source Reconstruction

- Added a client-owned `SteamAPI_Shutdown()` wrapper beside the recovered
  Steam client wrappers.
- The wrapper drains client Steam callbacks and retained auth-ticket state
  through `CL_Steam_ShutdownCallbacks()` before releasing the platform
  Steamworks runtime through `QL_Steamworks_Shutdown()`.
- `Com_Quit_f()` now calls `SteamAPI_Shutdown()` after `FS_Shutdown(qtrue)` and
  before the final server Steam shutdown/`Sys_Quit()` edge, matching the retail
  normal-quit order.
- `Com_Shutdown()` now owns only the server-side `QL_Steamworks_ServerShutdown()`
  edge at this layer, matching the retail `sub_465d30` call in common shutdown
  instead of tearing down the full Steam client runtime early.
- `qcommon.h` and `null_client.c` expose deterministic fallback linkage for
  non-client and default-disabled online-service builds.

## Parity

Focused Steam shutdown-wrapper confidence moves from 78% to 91%.
The broader Steam launch/runtime integration slice moves from 76% to 77%.
