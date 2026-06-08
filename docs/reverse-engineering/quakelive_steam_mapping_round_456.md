# quakelive_steam.exe Mapping Round 456

Date: 2026-06-08

Scope: Steam GameServer heartbeat retained-state boundary for launch/runtime
integration.

## Summary

This round reconstructs the retained initialized-state gate around retail
`SteamServer_EnableHeartbeats` (`sub_465DB0`). Retail checks the GameServer
initialized flag before calling SteamGameServer vtable slot `0x9C` for
heartbeat control. The source wrapper now mirrors that boundary directly by
returning before `QL_Steamworks_GetGameServer()` unless
`state.gameServerInitialised` is true.

## Evidence

Primary evidence:

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `references/analysis/quakelive_symbol_aliases.json`
- `src/common/platform/platform_steamworks.c`
- `tests/test_platform_services.py`

Observed facts:

1. The alias map identifies `sub_465DB0` as
   `SteamServer_EnableHeartbeats`.
2. `imports.txt` records retail `SteamGameServer` import ownership for this
   server publication cluster.
3. HLIL for `sub_465DB0` checks `data_e30358 != 0` before touching the native
   GameServer interface.
4. HLIL dispatches SteamGameServer vtable slot `0x9C` with `(arg1 == 1)` after
   the retained initialized-state branch.

## Source Reconstruction

- Added an explicit `state.gameServerInitialised` check to
  `QL_Steamworks_ServerEnableHeartbeats(...)` before calling
  `QL_Steamworks_GetGameServer()`.
- Kept the existing vtable/null checks and boolean return behavior.
- Extended `tests/test_platform_services.py` with HLIL evidence for
  `sub_465DB0` and source guard-order assertions.

No game launch was needed because this pass is static source reconstruction
against committed HLIL/Ghidra evidence plus harness/build/import verification.

## Verification

- `python -m pytest tests/test_platform_services.py::test_server_game_server_wrappers_reconstruct_mapped_server_slots -q --tb=short`
  - `1 passed`
- `python -m pytest tests/test_platform_services.py::test_server_game_server_wrappers_reconstruct_mapped_server_slots tests/test_platform_services.py::test_server_spawn_and_shutdown_reconstruct_retail_steam_identity_and_heartbeat_control tests/test_platform_services.py::test_server_published_state_reconstructs_retail_steam_server_owner tests/test_platform_services.py::test_server_frame_reconstructs_retail_steam_server_owner tests/test_platform_services.py::test_net_restart_reconstructs_retail_network_and_steam_server_restart_order -q --tb=short`
  - `5 passed`
- `python -m pytest tests/test_platform_services.py tests/test_steamworks_harness.py -q --tb=short`
  - `245 passed`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .vscode/build.ps1 -Configuration Debug -Platform x86 -Targets quakelive_steam`
  - `Build succeeded.`
  - `0 Warning(s)`
  - `0 Error(s)`
- `dumpbin /dependents build\win32\Debug\bin\quakelive_steam.exe`
  - Dynamic dependencies are Windows/debug CRT DLLs only.
  - No dynamic `libpng`, `vorbis`, `ogg`, or `steam_api` dependency is present.

## Parity Estimate

- Focused Steam GameServer heartbeat retained-state boundary:
  **88% -> 98%**.
- Focused Steam GameServer publication wrapper confidence: **95% -> 98%**.
- Broader Steam launch/runtime integration reconstruction confidence:
  **98% -> 98%**.
- Static executable dependency parity for bundled media libraries:
  **100% -> 100%**.
- Repo-wide checked-in tree parity: **99% -> 99%**.
