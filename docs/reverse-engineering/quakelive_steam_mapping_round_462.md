# Quake Live Steam Mapping Round 462: GameServer Connected Serverinfo Replay

## Scope

This round tightens the Steam GameServer connected-success callback around
retail `sub_466800`. The source already reconstructed the connected flag,
public server identity publication, full state refresh, and stats requery path,
but it did not replay the serverinfo key/value batch after a Steam backend
reconnect.

## Evidence

Primary evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/analysis/quakelive_symbol_aliases.json`

Observed facts:

- `sub_466800` is promoted as
  `SteamServerCallbacks_OnServersConnected` in the alias map.
- HLIL logs `Connected to Steam servers\n`, then writes
  `data_e30354 = 1`.
- The callback exits early when the retained server owner field at offset
  `0x30` is zero.
- When a server is active, retail calls `sub_465B00()`,
  `sub_466260(1)`, `sub_4CDBE0(4)`, and then returns through
  `sub_465A60(..., &data_1206288)`.
- Earlier rounds bounded `sub_465B00` as public Steam GameServer identity
  publication, `sub_466260(1)` as a full Steam GameServer state refresh, and
  `sub_465A60` as the Steam GameServer key/value batch sender.

## Source Reconstruction

Implemented source changes:

- Extended `SV_SteamServerConnectedCallback` to fetch
  `Cvar_InfoString( CVAR_SERVERINFO )` after the identity, full state, and
  stats refresh path.
- Replayed the current serverinfo batch via
  `QL_Steamworks_ServerSetKeyValuesFromInfoString( serverInfo )`, matching the
  retail reconnect-side `sub_465A60(..., &data_1206288)` tail.
- Expanded platform-service and netcode parity tests to pin the HLIL
  `sub_466800` sequence and source-level connected callback call order.

## Confidence

High confidence:

- Callback ownership, connected flag write, and active-server guard.
- The identity and full-state ordering in the connected callback.
- The final `sub_465A60` call as serverinfo key/value replay, because the same
  helper is already mapped by its SteamGameServer vtable slot `0x50` loop.

Medium confidence:

- The exact retained meaning of `sub_4CDBE0(4)` remains broader than this
  round. The source keeps the existing stats requery continuation in that
  position instead of inventing a new live-service behavior.

## Validation

- `python -m pytest tests/test_platform_services.py::test_server_callback_auth_owner_reconstructs_retail_steam_gameserver_bundle tests/test_netcode_parity_manifest.py::test_ql_server_browser_and_master_heartbeat_related_wiring_parity_recheck -q --tb=short`
  - 2 passed.
- `python -m pytest tests/test_platform_services.py tests/test_netcode_parity_manifest.py tests/test_steamworks_harness.py -q --tb=short`
  - 289 passed.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .vscode/build.ps1 -Configuration Debug -Platform x86 -Targets quakelive_steam`
  - Build succeeded with 0 warnings and 0 errors.
- `dumpbin /dependents build\win32\Debug\bin\quakelive_steam.exe`
  - No dynamic `steam_api`, `libpng`, `vorbis`, or `ogg` dependency was present.
- `git diff --check -- src/code/server/sv_client.c tests/test_platform_services.py tests/test_netcode_parity_manifest.py IMPLEMENTATION_PLAN.md docs/reverse-engineering/quakelive_steam_mapping_round_462.md`
  - Passed with repository LF-to-CRLF working-copy warnings only.

## Parity Estimate

- Focused connected-success GameServer publication parity: 84% -> 97%.
- Steam launch/runtime integration parity: 78% -> 79%.
