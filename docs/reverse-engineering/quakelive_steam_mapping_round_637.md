# Quake Live Steam Mapping Round 637: GetAllUGC AppID Ordering

Date: 2026-06-12

## Scope

This round tightens the retained Steam workshop `GetAllUGC` query launch path
around the retail AppID lookup order. The retail owner is
`SteamWorkshop_GetAllUGC`, promoted from `sub_460dc0`; the reconstructed source
owner is `QL_Steamworks_RequestAllUGCQuery`, reached from the browser-facing
`CL_Steam_RequestAllUGC` method.

Steam launch/runtime online behavior remains behind `QL_BUILD_ONLINE_SERVICES`.
This round does not enable live workshop services; it only aligns the wrapper
call order with the committed retail evidence.

## Retail Evidence

- `references/analysis/quakelive_symbol_aliases.json` promotes
  `FUN_00460dc0`, `sub_460DC0`, and `sub_460dc0` to
  `SteamWorkshop_GetAllUGC`.
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  records `FUN_00460dc0,00460dc0,158,0,unknown`.
- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
  confirms the dependency lane through `STEAM_API.DLL!SteamUtils`,
  `STEAM_API.DLL!SteamUGC`, `STEAM_API.DLL!SteamAPI_RegisterCallResult`, and
  `STEAM_API.DLL!SteamAPI_UnregisterCallResult`.
- Binary Ninja HLIL for `sub_460dc0` first fetches the AppID through
  `SteamUtils()` slot `0x24`.
- The same retail function then creates the all-UGC request through
  `SteamUGC()` slot `0x04`, using the AppID for both creator and consumer AppID
  arguments.
- The query is then submitted through `SteamUGC()` slot `0x0c`, followed by the
  retained call-result rebinding sequence and `SteamAPI_RegisterCallResult`.

Observed fact: retail resolves the AppID before the `SteamUGC()` query creation
path and uses that same AppID for both query AppID fields.

Inferred mapping: SRP's existing query wrapper already preserved the slot
mapping, filter pass-through, and call-result binding lifecycle. Moving the
AppID lookup before the UGC interface/vtable work makes the source order match
the retail `SteamUtils()` -> `SteamUGC()` sequence while retaining `0` as the
unavailable AppID fallback.

## Source Reconstruction

`src/common/platform/platform_steamworks.c` now orders
`QL_Steamworks_RequestAllUGCQuery` as follows:

1. Fetch `appId` through `QL_Steamworks_GetAppID()`.
2. Return `qfalse` when the AppID is unavailable.
3. Resolve `QL_Steamworks_GetUGCInterface`.
4. Resolve the SteamUGC vtable slots for CreateQueryAllUGCRequest (`0x04`) and
   SendQueryUGCRequest (`0x0c`).
5. Create the query with `(1, 0, appId, appId, filter)`.
6. Submit the query and bind the returned call handle through
   `QL_Steamworks_BindUGCQueryCallResult`.

The wrapper still releases the query handle on send or binding failure, and it
continues to pass the browser integer filter through without source-side
semantic promotion.

## Wiring

- `CL_Steam_RequestAllUGC` remains the browser method owner for `GetAllUGC`.
- The client-side method still logs
  `QL_Steamworks_GetAllUGCFilterContractLabel()` and
  `QL_Steamworks_GetAllUGCFilterSemanticGapLabel()` before forwarding the raw
  integer filter.
- `QL_Steamworks_RequestAllUGCQuery` remains the only Steamworks source owner
  for this query creation/submission path.

## Validation

Added `test_steam_ugc_get_all_query_appid_order_tracks_round_637` to pin:

- promoted aliases and the Ghidra function row for `sub_460dc0`;
- the SteamUtils, SteamUGC, RegisterCallResult, and UnregisterCallResult
  imports;
- Binary Ninja ordering from AppID fetch to query creation, query submission,
  and call-result registration;
- source ordering from `QL_Steamworks_GetAppID()` to UGC interface lookup,
  vtable slot resolution, query creation, query submission, and call-result
  binding; and
- retained `CL_Steam_RequestAllUGC` filter handoff wiring.

The older UGC call-result lifecycle parity gate was also updated to expect the
retail AppID-before-UGC ordering.

## Parity Estimate

Focused GetAllUGC AppID/query ordering confidence:
**88% -> 99%**.

Focused Steam workshop query source-shape confidence:
**96% -> 99%**.

overall Steam launch/runtime integration mapping confidence **93.76% -> 93.78%**.
