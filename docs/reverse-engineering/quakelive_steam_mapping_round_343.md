# Quake Live Steam Host Mapping Round 343

Scope: WebUI server-browser native `JSBrowserDetails` owner wiring.

## Evidence

Owning retail binary:

- `assets/quakelive/quakelive_steam.exe`

Committed evidence used:

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- `references/analysis/quakelive_symbol_aliases.json`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt`
- `docs/reverse-engineering/quakelive_steam_mapping_round_06.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_307.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_309.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_310.md`

Observed facts:

- Retail `SteamBrowser_RequestServerDetails` (`sub_4630B0`) allocates one
  `0x58`-byte `JSBrowserDetails` object, installs three callback vfptrs, then
  enters `JSBrowserDetails_RequestServerDetails` (`sub_461F70`).
- The detail object stores the rules callback view at base `+0`, players at
  base `+4`, ping at base `+8`, requested IP at `+0xc`, requested port at
  `+0x10`, and the browser detail id string at `+0x14`.
- `JSBrowserDetails_RequestServerDetails` formats the id as `"%u_%i"` and
  calls the `SteamMatchmakingServers` interface in the observed order:
  `PingServer` through vtable slot `0x34`, `ServerRules` through slot `0x3c`,
  then `PlayerDetails` through slot `0x38`.
- The vtable cluster in HLIL part 06 matches the three retained response
  families: ping response/failed, players response/failed/end, and rules
  response/failed/end.
- Successful ping responses publish the same
  `servers.details.%u_%u.response` family used by list rows after projecting
  the raw Steam `gameserveritem_t` payload.
- Rules callbacks publish
  `servers.rules.%s.response`, `servers.rules.%s.failed`, and
  `servers.rules.%s.end`.
- Player callbacks publish
  `servers.players.%s.response`, `servers.players.%s.failed`, and
  `servers.players.%s.end`.
- Retail increments the shared completion counter only from terminal detail
  callbacks, with the object released when the ping, rules, and player query
  lanes have all terminated.

Inference:

- The source callback owner keeps a linked list around the reconstructed retail
  object shape so shutdown can cancel outstanding native query handles without
  relying on retail heap lifetime side effects. This is source-side lifecycle
  hygiene around the observed `JSBrowserDetails` layout, not a claim that
  retail stores a linked list.
- The player callback still coerces Steam's floating `timePlayed` argument into
  the integer browser payload reconstructed in round 307.

## Source Update

- Added `QL_Steamworks_ReadServerBrowserPingResponse`, which projects the raw
  `gameserveritem_t` delivered by `PingServer` into the retained
  `ql_steam_server_browser_response_t` shape. The helper uses the existing
  row projection, keeps the app-id gate, and zeroes disabled or invalid output.
- Added the client-owned `clSteamNativeServerDetail_t` object with the
  observed rules/players/ping callback views at base, `base + 4`, and
  `base + 8`.
- Wired native ping success/failure, rule response/failure/end, and player
  response/failure/end callbacks in `cl_main.c` to publish the retained WebUI
  event families.
- `CL_Steam_RequestServerDetails` now tries the native
  `ISteamMatchmakingServers` detail owner first in opted-in Steamworks builds,
  then falls back to the existing UDP status query if the native provider or
  request is unavailable.
- Client Steam browser shutdown now releases outstanding native detail requests
  and cancels any retained ping/rules/player query handles through the wrapper
  cancellation primitive.
- The Steamworks harness now exports and tests the ping-row projection so list
  row and detail ping response payloads stay pinned together.

## Guardrails

- This does not enable Steamworks or Quake Live online services by default.
  The path remains behind `QL_BUILD_ONLINE_SERVICES`, and runtime provider
  disablement still falls through to source-owned fallbacks.
- The read-only `assets/` and `src/ui/` trees were not modified.
- No runtime game launch was needed; this was a static reconstruction plus
  harness/source parity pass.

## Parity Estimate

- Focused WebUI server-detail request dispatch lane: before 74%, after 98%.
- Broader server-browser/details surface: before 98%, after 99%.
- Repo-wide parity remains 99% because the online-service policy boundary and
  friends/history compatibility lanes are unchanged.

## Verification

- `python -m pytest tests/test_steamworks_harness.py::test_server_browser_ping_response_projection_matches_retail_jsbrowserdetails_payload_shape -q --tb=short`
  - Result: `2 passed`.
- `python -m pytest tests/test_platform_services.py::test_client_browser_server_shims_reconstruct_retail_server_browser_surface tests/test_netcode_parity_manifest.py::test_ql_server_browser_and_master_heartbeat_related_wiring_parity_recheck -q --tb=short`
  - Result: `2 passed`.
- `python -m pytest tests/test_steamworks_harness.py -q --tb=short`
  - Result: `80 passed`.
- `"C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe" src\code\quakelive.sln /t:Build /p:Configuration=Debug /p:Platform=x86 /m /nologo`
  - Result: build succeeded with `0 Warning(s)` and `0 Error(s)`.
- `"C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe" src\code\quakelive_steam.vcxproj /t:Build /p:Configuration=Debug /p:Platform=x86 /p:QLBuildOnlineServices=1 /p:QLBuildSteamworks=1 /p:QLBuildOpenSteam=0 /p:QLRequireAwesomiumSdk=0 /p:QLRequireSteamworksSdk=0 /m /nologo`
  - Result: build succeeded with `2 Warning(s)` and `0 Error(s)`;
    warnings were `BSCMAKE BK4502` browse-info truncation messages for
    `cl_awesomium_win32.sbr` and `platform_backend_steamworks.sbr`.
