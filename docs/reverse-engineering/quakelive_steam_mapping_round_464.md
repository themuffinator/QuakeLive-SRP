# Quake Live Steam Mapping Round 464: GameServer Negative Callback Logs

## Scope

This round tightens the Steam GameServer connect-failure and disconnect
callback lane around retail `sub_465C10` and `sub_465C30`. The source already
cleared the server-connected flag, but it still inspected callback payload
result fields and emitted source-only detail diagnostics.

## Evidence

Primary evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- `references/analysis/quakelive_symbol_aliases.json`

Observed facts:

- The alias map promotes `sub_465C10` as
  `SteamServerCallbacks_OnConnectFailure`.
- The alias map promotes `sub_465C30` as
  `SteamServerCallbacks_OnServersDisconnected`.
- Retail callback registration installs `sub_465C10` for
  `SteamServerConnectFailure_t` callback id `0x66`.
- Retail callback registration installs `sub_465C30` for
  `SteamServersDisconnected_t` callback id `0x67`.
- `sub_465C10` writes `data_e30354 = 0` and returns through a fixed
  `Failed to connect to Steam servers` log.
- `sub_465C30` writes `data_e30354 = 0` and returns through the fixed
  `Disconnected from Steam servers\n` log.
- Neither retail callback reads the Steam payload result field before clearing
  the connected flag or logging.

## Source Reconstruction

Implemented source changes:

- Updated `SV_SteamServerConnectFailureCallback` to ignore the adapter payload,
  clear `sv_steamServerConnected`, and print
  `Failed to connect to Steam servers\n`.
- Updated `SV_SteamServerDisconnectedCallback` to ignore the adapter payload,
  clear `sv_steamServerConnected`, and print
  `Disconnected from Steam servers\n`.
- Kept the source callback signatures intact because the platform adapter still
  dispatches typed Steam callback payloads.
- Expanded platform-service and netcode parity tests to pin the HLIL
  registration/function sequence and reject payload-result logging in the
  engine owner callbacks.

## Confidence

High confidence:

- Callback ownership and callback id registration for connect failure and
  disconnect.
- The connected-flag clear in both retail functions.
- The fixed log messages and absence of payload-result handling in the retail
  callback bodies.

Medium confidence:

- The source adapter continues to validate dispatch payloads before calling
  these handlers. That is retained as adapter hygiene; the reconstruction here
  is limited to the engine callback owner behavior once dispatch has arrived.

## Validation

- `python -m pytest tests/test_platform_services.py::test_server_callback_auth_owner_reconstructs_retail_steam_gameserver_bundle tests/test_netcode_parity_manifest.py::test_ql_server_browser_and_master_heartbeat_related_wiring_parity_recheck -q --tb=short`
  - 2 passed.
- `python -m pytest tests/test_platform_services.py tests/test_netcode_parity_manifest.py tests/test_steamworks_harness.py -q --tb=short`
  - 289 passed.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .vscode/build.ps1 -Configuration Debug -Platform x86 -Targets quakelive_steam`
  - Build succeeded with 0 warnings and 0 errors.
- `dumpbin /dependents build\win32\Debug\bin\quakelive_steam.exe`
  - No dynamic `steam_api`, `libpng`, `vorbis`, or `ogg` dependency was present.
- `git diff --check -- src/code/server/sv_client.c tests/test_platform_services.py tests/test_netcode_parity_manifest.py IMPLEMENTATION_PLAN.md docs/reverse-engineering/quakelive_steam_mapping_round_464.md`
  - Passed with repository LF-to-CRLF working-copy warnings only.

## Parity Estimate

- Focused negative GameServer callback parity: 72% -> 98%.
- Steam launch/runtime integration parity: 79% -> 80%.
