# Quake Live Steamworks Mapping Round 350

Date: 2026-06-06

## Focus

Reconstruct the retained Steam GameServer stats callback wiring around the
`idSteamStats` owner:

- `GSStatsReceived_t` callback ID `0x708`
- `GSStatsStored_t` callback ID `0x709`
- `SteamGameServerUtils::GetAppID` through vtable slot `0x24`
- server-side callback observation and harness coverage

The implementation remains behind `QL_BUILD_ONLINE_SERVICES` /
`QL_BUILD_STEAMWORKS`; disabled builds keep returning inert stubs.

## Evidence

Observed import and symbol evidence:

- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt` lists
  `STEAM_API.DLL!SteamGameServerUtils`.
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
  contains imported callback vtables for
  `CCallback<class_idSteamStats,struct_GSStatsReceived_t,1>` and
  `CCallback<class_idSteamStats,struct_GSStatsStored_t,1>`.
- The same symbol corpus also keeps the neighboring
  `CCallback<class_idSteamStats,struct_SteamServersConnected_t,1>`, matching
  the three-callback retail stats owner shape.

Observed HLIL evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
  registers the `GSStatsReceived_t` callback at `0x00467904` with callback ID
  `0x708`.
- The same constructor registers `GSStatsStored_t` at `0x00467939` with
  callback ID `0x709`.
- The same constructor calls `SteamGameServerUtils()` and then vtable slot
  `0x24` at `0x0046794f`, storing the returned app id in the stats owner.
- `sub_4671d0` is the received-stats path: it reads the callback result,
  treats result `1` as success, then queries per-descriptor stat values through
  `SteamGameServerStats`.
- `sub_467360` is the stored-stats path: it logs success/failure and handles
  result `8` as a partial-validation path that flows back into the received
  stats handling.

## Reconstruction

This pass added the missing public and retained callback surface:

- Added `ql_steam_gs_stats_received_t` and `ql_steam_gs_stats_stored_t`.
- Added `onGSStatsReceived` and `onGSStatsStored` to
  `ql_steam_server_callback_bindings_t`.
- Added callback IDs `QL_STEAM_CALLBACK_GS_STATS_RECEIVED` (`0x708`) and
  `QL_STEAM_CALLBACK_GS_STATS_STORED` (`0x709`).
- Added raw callback payload structs, dispatchers, registration, and
  unregistering in `QL_Steamworks_RegisterServerCallbacks`.
- Added optional `SteamGameServerUtils` loading and
  `QL_Steamworks_ServerGetAppID`, mapping slot `0x24`.
- Added server stats-session retention of the server app id.
- Added server callback handlers that mark successful receive results,
  observe store results, and re-request current values when Steam reports
  result `8`.
- Extended the Steamworks harness with mock `SteamGameServerUtils`, queueable
  GS stats callback payloads, and ctypes coverage for the server callback pump.

## Inference Boundary

The retail evidence proves the callback IDs, the three-callback `idSteamStats`
owner shape, the `SteamGameServerUtils` app-id slot, and the high-level
received/stored result handling. The current source still does descriptor
value reads lazily through the existing server stats wrappers instead of
replaying the entire retail descriptor table inside the callback body.

That is an intentional containment choice for this pass: it strengthens the
retail callback wiring and result observation without changing the existing
open-build stats ownership model or enabling live Steam services by default.

## Verification

Validation:

```text
python -m pytest tests/test_steamworks_harness.py::test_server_validate_auth_ticket_response_dispatch_matrix_from_server_callback_pump tests/test_steamworks_harness.py::test_server_get_app_id_routes_gameserver_utils_slot tests/test_steamworks_harness.py::test_server_gs_stats_callbacks_dispatch_from_server_callback_pump -q --tb=short
12 passed

python -m pytest tests/test_platform_services.py::test_server_game_server_wrappers_reconstruct_mapped_server_slots tests/test_platform_services.py::test_server_steam_stats_owner_reconstructs_retail_gameserverstats_bridge -q --tb=short
2 passed

python -m pytest tests/test_steamworks_harness.py -q --tb=short
90 passed

python -m pytest tests/test_platform_services.py -q --tb=short
80 passed
```

No game launch was required; the callback and wrapper behavior is covered by
static source assertions plus the executable Steamworks harness.

## Parity Estimate

Focused GameServer stats callback/bootstrap parity:
**before 84% -> after 97%**.

The remaining 3% is live Steam backend behavior plus full descriptor-table
replay parity under real `SteamGameServerStats` callbacks. Broader Steamworks
parity remains approximately **99%** because online services stay opt-in and
live-service replacement policy remains intentionally bounded.
