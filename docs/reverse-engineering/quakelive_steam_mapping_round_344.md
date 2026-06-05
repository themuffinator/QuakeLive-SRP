# Quake Live Steam Host Mapping Round 344

Scope: SteamDataSource fallback-owner labeling and resource-bridge diagnostics.

## Evidence

Owning retail binary:

- `assets/quakelive/quakelive_steam.exe`

Committed evidence used:

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/exports.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- `references/analysis/quakelive_symbol_aliases.json`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt`
- `docs/reverse-engineering/quakelive_steam_mapping_round_91.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_289.md`

Observed facts:

- `analysis_symbols.txt` exposes `SteamDataSource::vftable` at `0x00532B80`
  and the embedded
  `CCallback<class SteamDataSource, struct AvatarImageLoaded_t, 0>` vtable at
  `0x00532B68`.
- The alias map keeps `sub_4640C0` as `SteamDataSource_OnRequest`,
  `sub_464290` as `SteamDataSource_OnAvatarImageLoaded`,
  `sub_464300` as `SteamDataSource_Init`, `sub_464440` as
  `SteamDataSource_Shutdown`, and `sub_464510` as `SteamDataSource_Destroy`.
- HLIL part 06 records the `SteamDataSource` vtable and the
  `Awesomium::DataSource::SendResponse` import at `0x0052C6B0`.
- HLIL and symbols expose `QLResourceInterceptor::vftable` at `0x00547F94`,
  with the alias map preserving `sub_434620` as `QLResourceInterceptor_OnRequest`
  and `sub_434600` as `QLResourceInterceptor_OnFilterNavigation`.
- Round 91 already reconstructed the retained fallback chain:
  `QLResourceInterceptor_OnRequest` tries SteamDataSource, projects retail `ql`
  host resources through launcher/web filesystem owners, then falls back to the
  broader launcher request resolver.
- Round 289 made the SteamDataSource vtable, callback, lifecycle, and
  ResponseThread anchors source-visible, while explicitly bounding the exact
  live Awesomium delayed-response object.

Inference:

- The current source can name the non-avatar `steam://` fallback owner with high
  confidence because the route is already implemented and test-pinned, but the
  exact retail non-avatar SteamDataSource resource semantics remain unpromoted.
- `QLResourceInterceptor launcher/web fallback` is a source-side owner label for
  the retained compatibility route, not a claim that retail stored that exact
  string or cvar.

## Source Update

- Added `CL_GetSteamDataSourceFallbackOwnerLabel()` in
  `src/code/client/cl_steam_resources.c`.
- Extended `CL_LogSteamResourceBridgeUnavailable()` so diagnostics publish the
  supported SteamDataSource subset, the fallback owner, and the native gap in a
  single line.
- Added ROM diagnostic cvars for the resource bridge:
  `ui_resourceBridgeSteamDataSourceSubset`,
  `ui_resourceBridgeSteamDataSourceNativeGap`, and
  `ui_resourceBridgeSteamDataSourceFallbackOwner`.
- Updated the non-avatar `CL_SteamDataSource_Request()` branch to report
  `non-avatar Steam URI routed to launcher/web fallback owner` for both
  disabled-service and enabled-service-but-no-native-owner paths.
- Updated platform-service and Awesomium parity guards so the fallback label,
  cvars, and revised non-avatar route stay source-visible.

## Guardrails

- This does not add a new live SteamDataSource owner.
- This does not enable Steamworks, Awesomium, or Quake Live online services by
  default.
- The `steam://avatar/...` path remains the native SteamDataSource subset, and
  non-avatar `steam://` requests remain routed toward the retained
  launcher/resource fallback.
- The read-only `assets/` and `src/ui/` trees were not modified.
- No runtime game launch was needed; this was static source reconstruction,
  tests, and build verification.

## Parity Estimate

- Focused SteamDataSource fallback-owner diagnostic surface: before 82%,
  after 96%.
- Broader SteamDataSource resource bridge source visibility: before 93%,
  after 95%.
- Repo-wide parity remains 99% because the online-service default-disabled
  policy and exact live Awesomium delayed-response gap are unchanged.

## Verification

- `python -m pytest tests/test_platform_services.py::test_steam_resource_bridge_reconstructs_avatar_url_fetches tests/test_platform_services.py::test_client_steam_callback_owner_reconstructs_retail_frame_pump_and_lifecycle tests/test_platform_services.py::test_launcher_resource_bridge_reconstructs_retail_web_fallback_owner tests/test_platform_services.py::test_launcher_resource_fallbacks_survive_service_disabled_policy tests/test_platform_services.py::test_steamworks_modern_adapter_gaps_stay_explicit_until_owned tests/test_awesomium_browser_parity.py::test_awesomium_browser_host_verifier_covers_closed_gap_anchors tests/test_awesomium_browser_parity.py::test_awesomium_steam_data_source_retail_wiring_is_source_visible -q --tb=short`
  - Result: `7 passed`.
- `"C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe" src\code\quakelive.sln /t:Build /p:Configuration=Debug /p:Platform=x86 /m /nologo`
  - Result: build succeeded with `0 Warning(s)` and `0 Error(s)`.
- `"C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe" src\code\quakelive_steam.vcxproj /t:Build /p:Configuration=Debug /p:Platform=x86 /p:QLBuildOnlineServices=1 /p:QLBuildSteamworks=1 /p:QLBuildOpenSteam=0 /p:QLRequireAwesomiumSdk=0 /p:QLRequireSteamworksSdk=0 /m /nologo`
  - Result: build succeeded with `3 Warning(s)` and `0 Error(s)`;
    warnings were `BSCMAKE BK4502` browse-info truncation messages for
    `cl_awesomium_win32.sbr`, `platform_backend_steamworks.sbr`, and
    `platform_steamworks.sbr`.
- `git diff --check`
  - Result: no whitespace errors; Git reported existing CRLF-normalization
    warnings.
- `powershell -ExecutionPolicy Bypass -File tools\ci\verify-awesomium-browser-host-parity.ps1`
  - Result: the new SteamDataSource fallback cvar anchors were verified before
    the script stopped on an unrelated existing
    `CL_Awesomium_BuildUserScript(...)` literal drift in
    `src/code/client/cl_awesomium_win32.cpp`.
