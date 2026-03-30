# Quake Live Steam Host Mapping Round 78

## Scope

This round closes the next bounded `quakelive_steam.exe` Steam host seam that
was still only partially reconstructed after the earlier game-server bootstrap,
identity, metadata, and published-state passes:

- the actual `SteamGameServer_Init(...)` ownership inside retail
  `sub_466ED0`
- the paired `SteamGameServer_Shutdown()` lifetime gate from retail
  `sub_465D30`
- the retail `data_e30358` game-server init predicate
- the dedicated-path `SteamUGC` versus `SteamGameServerUGC` owner split that
  sits immediately after the init import in the HLIL

The evidence stayed inside the committed corpus plus the writable source tree:

- `references/hlil/quakelive/quakelive_steam.exe/`
- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `docs/reverse-engineering/quakelive_steam_mapping_round_01.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_03.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_75.md`
- `src/common/platform/platform_steamworks.c`
- `src/code/qcommon/common.c`
- `src/code/server/sv_init.c`

## `sub_466ED0`: common-owner Steam game-server bootstrap

The earlier rounds already reconstructed the stable metadata writes that happen
after retail `SteamGameServer_Init(...)`, but Round 75 deliberately left the
init import itself in note-only form because the writable owner had not been
confirmed.

This round closes that ownership question from the committed HLIL:

1. `Com_Init` calls `sub_466ED0()` from the common startup path.
2. `sub_466ED0()` reads `net_ip`, `net_port`, and `sv_vac`.
3. It calls the imported `SteamGameServer_Init`.
4. It stores the return value into the shared `data_e30358` init flag.
5. It selects `SteamUGC()` versus `SteamGameServerUGC()` immediately after
   init.
6. It then performs the dedicated/logon/product/game-dir bootstrap writes that
   earlier rounds had already reconstructed.

The writable source now mirrors that bounded ownership in two layers:

- `src/common/platform/platform_steamworks.c`
  - `QL_Steamworks_ServerInit`
  - `QL_Steamworks_ServerShutdown`
  - `QL_Steamworks_ServerIsInitialised`
- `src/code/qcommon/common.c`
  - `Com_SteamPackGameServerIP`
  - `Com_InitSteamGameServer`

The platform wrapper now owns the direct import call with the retail-stable
arguments:

- packed `net_ip`
- Steam port `0`
- game port `net_port`
- query port `0xFFFF`
- secure mode `3` versus no-auth mode `2` from `sv_vac`
- fixed version string `"1069"`

The common owner now performs the adjacent one-time bootstrap writes in the
same startup tranche:

- `SetDedicated`
- `LogOn` / anonymous fallback
- initial `EnableHeartbeats( qfalse )`
- `SetProduct( "Quake Live" )`
- `SetGameDir( "baseq3" )`

Because this repository still keeps Quake Live-only online services behind a
fallback-friendly policy, the retained source keeps this startup path
non-fatal when Steam is unavailable instead of reproducing the retail fatal
error on missing game-server init.

## `sub_465D30` and `data_e30358`: lifetime and predicates

Round 03 already bounded `sub_465A30` as the shared predicate around
`data_e30358`, with `sub_466ED0` setting it and `sub_465D30` clearing it.

The writable source now models that directly:

- `QL_Steamworks_ServerIsInitialised()` returns the retained
  `gameServerInitialised` flag.
- `QL_Steamworks_ServerShutdown()` calls `SteamGameServer_Shutdown()` when the
  server path was active and clears both the init flag and the game-server UGC
  owner flag.
- `QL_Steamworks_Shutdown()` now mirrors the retail common quit owner more
  closely by cascading through the server shutdown path before unloading the
  Steam runtime.

This also tightens the retained wrappers around:

- `QL_Steamworks_RunServerCallbacks`
- `QL_Steamworks_GetGameServer`
- `QL_Steamworks_GetGameServerNetworking`

Those helpers now require the shared server-init predicate instead of only
checking whether the exported interface symbol exists.

## Dedicated workshop owner split

Retail `sub_466ED0` selects the active UGC owner immediately after game-server
init:

- non-dedicated path: `SteamUGC()`
- dedicated path: `SteamGameServerUGC()`

The writable source now mirrors that split in
`QL_Steamworks_GetUGCInterface()`. Dedicated server workshop calls route
through `SteamGameServerUGC()` while the reconstructed game-server path is
active, and the retained client path still falls back to `SteamUGC()`.

That closes the cleanest remaining workshop ownership gap without inventing a
larger workshop-mount owner beyond the evidence already committed.

## Verification

Updated coverage landed in:

- `tests/steamworks_harness.c`
- `tests/test_steamworks_harness.py`
- `tests/test_platform_services.py`

Command run:

```text
python -m pytest tests/test_steamworks_harness.py tests/test_platform_services.py tests/test_ui_menu_files.py -q
```

Result:

- `71 passed`

## Outcome

This round did not add new address aliases. It consumed already-mapped retail
ownership in three concrete ways:

- the Steamworks platform layer now reconstructs the retail game-server
  init/shutdown/predicate seam instead of only the later vtable writes
- the one-time dedicated/logon/product/game-dir bootstrap now lives in the
  common startup owner that the HLIL actually shows, rather than only in
  `SV_Init`
- dedicated workshop calls now route through the mapped `SteamGameServerUGC`
  owner when the reconstructed game-server path is active

Estimated parity for this round: `78% -> 79%`.
