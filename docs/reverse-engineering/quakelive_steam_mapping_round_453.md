# quakelive_steam.exe Mapping Round 453

Date: 2026-06-08

Scope: browser `SetFavoriteServer` retained-state boundary for the Steam
launch/runtime integration path.

## Summary

This round reconstructs the retained Steam client state boundary for the
browser favorite-server lane. Retail `qz_instance.SetFavoriteServer` dispatches
directly into SteamUtils and SteamMatchmaking after converting three browser
arguments. The source compatibility path mirrors favorites into the local Quake
III cache even when Steamworks is unavailable, but the native Steam favorite
update now requires the retained `SteamClient_IsInitialized()` flag before it
can reach the optional Steamworks adapter.

## Evidence

Primary evidence:

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt`
- `references/analysis/quakelive_symbol_aliases.json`
- `src/code/client/cl_cgame.c`
- `src/common/platform/platform_steamworks.c`
- `tests/test_platform_services.py`

Observed facts:

1. `metadata.txt` records the retail owner as `quakelive_steam.exe` with
   `5473` functions, `351` imports, and `4377` analysis symbols.
2. `functions.csv` records `FUN_00431e50` at `0x00431E50`, size `241`; this is
   the qz_instance browser method dispatcher used by the mapped web-host lane.
3. `imports.txt` records retail imports for `STEAM_API.DLL!SteamUtils` and
   `STEAM_API.DLL!SteamMatchmaking`.
4. The HLIL method-table data records the browser string
   `SetFavoriteServer` at `0x0052C7E4` and its table row at `0x0055C188`.
5. Retail `sub_431E50` case `0x13` checks the JS argument array size and only
   proceeds when `result u>= 3`.
6. The add branch calls `SteamUtils()`, `SteamMatchmaking()`, `_time64(...)`,
   converts the browser arguments, and dispatches SteamMatchmaking vtable slot
   `0x08`.
7. The remove branch calls `SteamUtils()`, `SteamMatchmaking()`, converts the
   browser arguments, and dispatches SteamMatchmaking vtable slot `0x0C`.
8. The source Steamworks wrapper already maps those slots through
   `QL_Steamworks_SetFavoriteServerForApp(...)`, using vtable index
   `0x08 / 4` for add and `0x0C / 4` for remove.

## Source Reconstruction

- Added `SteamClient_IsInitialized()` to the native favorite update condition
  in `CL_WebHost_SetFavoriteServer(...)`.
- Preserved the repository policy gate through `CL_SteamServicesEnabled()` and
  the existing optional `QL_Steamworks_SetFavoriteServerForApp(...)` adapter.
- Preserved the unconditional `CL_WebHost_MirrorFavoriteServer(...)` fallback
  so local favorites remain synchronized when online services are disabled,
  Steam is not initialized, or the native favorite update fails.
- Extended `tests/test_platform_services.py` with the retail HLIL case `0x13`
  evidence and source guard-order assertions.

No game launch was needed because this pass is static source reconstruction
against committed HLIL/Ghidra evidence and executable import verification.

## Verification

- `python -m pytest tests/test_platform_services.py::test_client_browser_favorite_server_lane_reconstructs_retail_steam_matchmaking_owner -q --tb=short`
  - `1 passed`
- `python -m pytest tests/test_platform_services.py::test_client_browser_favorite_server_lane_reconstructs_retail_steam_matchmaking_owner tests/test_platform_services.py::test_client_browser_server_shims_reconstruct_retail_server_browser_surface tests/test_platform_services.py::test_client_browser_lobby_social_shims_reconstruct_retail_qz_instance_dispatch_surface tests/test_application_initialization_mapping.py::test_policy_adjusted_common_client_server_wiring_matches_mapped_retail_chain -q --tb=short`
  - `4 passed`
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

- Focused browser favorite-server retained-state boundary: **82% -> 96%**.
- Focused qz_instance favorite wrapper confidence: **93% -> 96%**.
- Broader Steam launch/runtime integration reconstruction confidence:
  **98% -> 98%**.
- Static executable dependency parity for bundled media libraries:
  **100% -> 100%**.
- Repo-wide checked-in tree parity: **99% -> 99%**.
