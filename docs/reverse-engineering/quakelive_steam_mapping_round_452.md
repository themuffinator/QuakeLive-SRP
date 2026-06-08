# quakelive_steam.exe Mapping Round 452

Date: 2026-06-08

Scope: native SteamMatchmakingServers list/detail availability boundary for the
browser server-list runtime path.

## Summary

This round reconstructs the retained Steam client state boundary for the
source-side native server-browser owner. Retail `JSBrowser` uses
SteamMatchmakingServers directly for refresh, cancellation, filtered
server-list requests, and detail requests. The source has a compatibility
split: native SteamMatchmakingServers requests are used when an opted-in
Steamworks provider is available, otherwise the Quake III source browser
fallback handles list and detail publication.

The native availability guard now also requires the retained
`SteamClient_IsInitialized()` flag before starting native list or detail
requests. This keeps source-only platform-service descriptors from opening a
native Steam server-browser path when the retail Steam client owner did not
actually initialize.

## Evidence

Primary evidence:

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `references/analysis/quakelive_symbol_aliases.json`
- `src/code/client/cl_main.c`
- `tests/test_platform_services.py`

Observed facts:

1. `functions.csv` records `FUN_00462e80` at `0x00462E80`, size `34`,
   `FUN_00462eb0` at `0x00462EB0`, size `451`, `FUN_00463090` at
   `0x00463090`, size `20`, and `FUN_004630b0` at `0x004630B0`, size `87`.
2. The alias map identifies `sub_462E80` as `SteamBrowser_RefreshList`,
   `sub_462EB0` as `JSBrowser_RequestServers`, `sub_463090` as
   `SteamBrowser_RequestServers`, and `sub_4630B0` as
   `SteamBrowser_RequestServerDetails`.
3. Retail `sub_462e80` checks the retained request handle at object offset `8`
   and calls SteamMatchmakingServers vtable slot `0x24`, the refresh-query
   path.
4. Retail `sub_462eb0` refuses to start when its refresh-active byte at object
   offset `4` is already set.
5. Retail `sub_462eb0` cancels an existing request handle through
   SteamMatchmakingServers vtable slot `0x18` before starting a new request.
6. Retail `sub_462eb0` builds a single filter pair with key `gamedir` and
   value `baseq3` for filtered remote list requests.
7. Retail `sub_462eb0` uses SteamUtils vtable slot `0x24` for the running app
   id and dispatches the SteamMatchmakingServers mode slots before publishing
   `servers.refresh.start`.
8. Retail `sub_463090` is a thin forwarder into `sub_462eb0(data_e30334,
   arg1)`.
9. Retail `sub_4630b0` allocates the JSBrowserDetails response object and
   forwards it into `sub_461f70` for the detail request.

## Source Reconstruction

- Added `SteamClient_IsInitialized()` to
  `CL_SteamBrowser_NativeListAvailable()`.
- Kept the existing `CL_MatchmakingServiceAvailable()` and
  `QL_Steamworks_HasServerBrowserInterface()` checks, preserving the
  repository's default-disabled online-service policy and the explicit native
  adapter requirement.
- Because `CL_SteamBrowser_NativeListAvailable()` is the common guard for
  `CL_SteamBrowser_BeginNativeRequest()`,
  `CL_SteamBrowser_BeginNativeDetailRequest()`, and native refresh reuse, this
  single source edit gates all native server-list, detail, and refresh paths.
- Extended `tests/test_platform_services.py` with HLIL evidence for retail
  refresh, cancellation, `gamedir=baseq3` filtering, request start
  publication, and the source guard ordering.

No game launch was needed because this pass is static source reconstruction
against committed HLIL/Ghidra evidence and does not need live Steam or renderer
behavior to disambiguate.

## Verification

- `python -m pytest tests/test_platform_services.py::test_client_browser_server_shims_reconstruct_retail_server_browser_surface -q --tb=short`
  - `1 passed`
- `python -m pytest tests/test_platform_services.py::test_client_browser_server_shims_reconstruct_retail_server_browser_surface tests/test_platform_services.py::test_client_browser_lobby_social_shims_reconstruct_retail_qz_instance_dispatch_surface tests/test_engine_client_command_parity.py::test_client_steam_command_registration_and_identity_wiring_match_retail_surface tests/test_application_initialization_mapping.py::test_policy_adjusted_common_client_server_wiring_matches_mapped_retail_chain -q --tb=short`
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

- Focused native server-browser retained-state boundary: **80% -> 95%**.
- Focused SteamMatchmakingServers request/detail owner confidence:
  **90% -> 94%**.
- Broader Steam launch/runtime integration reconstruction confidence:
  **97% -> 98%**.
- Static executable dependency parity for bundled media libraries:
  **100% -> 100%**.
- Repo-wide checked-in tree parity: **99% -> 99%**.
