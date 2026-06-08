# quakelive_steam.exe Mapping Round 455

Date: 2026-06-08

Scope: Steam GameServer serverinfo key-value publication retained-state
boundary for launch/runtime integration.

## Summary

This round reconstructs the retained initialized-state gate around retail
`SteamServer_SetKeyValuesFromInfoString` (`sub_465A60`). Retail checks the
GameServer initialized flag before walking the serverinfo string and before
calling the SteamGameServer key-value vtable slot. The source wrapper now
matches that owner boundary directly by returning before `Info_NextPair(...)`
unless `state.gameServerInitialised` is true.

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

1. `functions.csv` records `FUN_00465a60` at `0x00465A60`, size `141`.
2. The alias map identifies `sub_465A60` as
   `SteamServer_SetKeyValuesFromInfoString`.
3. `imports.txt` records retail `SteamGameServer` import ownership for this
   server publication cluster.
4. HLIL for `sub_465A60` sets `cond:0 = data_e30358 == 0`.
5. HLIL only enters the info-string walker when `not(cond:0)` and the
   incoming info-string pointer is non-null.
6. HLIL uses the info-string pair splitter (`sub_4D9380`) before calling
   SteamGameServer vtable slot `0x50` for each key/value pair.

## Source Reconstruction

- Added an explicit `state.gameServerInitialised` check to
  `QL_Steamworks_ServerSetKeyValuesFromInfoString(...)` before assigning
  `head`, calling `Info_NextPair(...)`, or dispatching
  `QL_Steamworks_ServerSetKeyValue(...)`.
- Kept the existing null-info-string validation and per-pair failure return.
- Extended `tests/test_platform_services.py` with HLIL evidence for
  `sub_465A60` and source guard-order assertions.

No game launch was needed because this pass is static source reconstruction
against committed HLIL/Ghidra evidence plus harness/build/import verification.

## Verification

- `python -m pytest tests/test_platform_services.py::test_server_game_server_wrappers_reconstruct_mapped_server_slots -q --tb=short`
  - `1 passed`
- `python -m pytest tests/test_platform_services.py::test_server_game_server_wrappers_reconstruct_mapped_server_slots tests/test_platform_services.py::test_server_info_changes_reconstruct_retail_steam_rule_publication tests/test_platform_services.py::test_server_published_state_reconstructs_retail_steam_server_owner tests/test_platform_services.py::test_server_spawn_and_shutdown_reconstruct_retail_steam_identity_and_heartbeat_control tests/test_platform_services.py::test_server_frame_reconstructs_retail_steam_server_owner -q --tb=short`
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

- Focused Steam GameServer key-value retained-state boundary:
  **86% -> 98%**.
- Focused Steam GameServer publication wrapper confidence: **93% -> 98%**.
- Broader Steam launch/runtime integration reconstruction confidence:
  **98% -> 98%**.
- Static executable dependency parity for bundled media libraries:
  **100% -> 100%**.
- Repo-wide checked-in tree parity: **99% -> 99%**.
