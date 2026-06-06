# Botlib Route Prelude Mapping - 2026-06-06

## Scope

This pass covers the remaining unnamed AAS route prelude helpers immediately
before the already-mapped route runtime tranche:

- `src/code/botlib/be_aas_route.c`
- `src/code/botlib/be_aas_route.h`
- `src/code/botlib/be_aas_main.c`
- `src/code/botlib/be_ai_move.c`
- `references/analysis/quakelive_symbol_aliases.json`

The owning retail binary is `quakelive_steam.exe`. Evidence comes from the
committed Binary Ninja HLIL split for the Steam engine binary and the Ghidra
`functions.csv` inventory.

## Retail Evidence

Primary anchors:

- `AAS_RoutingInfo @ 0x004925F0`
- `AAS_ClusterAreaNum @ 0x00492630`
- `AAS_InitTravelFlagFromType @ 0x00492680`
- `AAS_TravelFlagForType @ 0x004927E0`
- `AAS_RemoveRoutingCacheInCluster @ 0x00492800`
- `AAS_RemoveRoutingCacheUsingArea @ 0x004928B0`
- `AAS_EnableRoutingArea @ 0x00492990`
- `AAS_AreaContentsTravelFlags @ 0x00492A20`
- `AAS_InitAreaContentsTravelFlags @ 0x00492A40`
- `AAS_CreateReversedReachability @ 0x00492B10`
- `AAS_AreaTravelTime @ 0x00492C30`
- `AAS_CalculateAreaTravelTimes @ 0x00492CD0`
- `AAS_InitPortalMaxTravelTimes @ 0x00492F20`

Observed retail facts:

- `AAS_RoutingInfo` prints area-cache update count, portal-cache update count,
  and current routing-cache bytes with the exact debug strings at
  `0x0053A7B4`, `0x0053A798`, and `0x0053A780`.
- `AAS_ClusterAreaNum` reads an area's cluster field, returns
  `clusterareanum` for normal areas, and resolves portal side membership
  through the front-cluster comparison for negative cluster IDs.
- `AAS_InitTravelFlagFromType` writes the travel-type flag table including
  Quake Live additions for double jump, ramp jump, strafe jump, jump pad, and
  func-bobbing travel.
- `AAS_TravelFlagForType` masks the low travel type bits with `0xFFFFFF`,
  bounds the table lookup, and returns `TFL_INVALID` for out-of-range values.
- `AAS_RemoveRoutingCacheInCluster` and
  `AAS_RemoveRoutingCacheUsingArea` inline the small unlink/free helper shape:
  time-list unlink, cache-size decrement, free, and list-head clearing.
- `AAS_EnableRoutingArea` uses the route-prelude invalidator at
  `0x004928B0` only when the disabled bit changes.
- `AAS_AreaContentsTravelFlags` is the direct area-content travel-flag table
  accessor, while `AAS_InitAreaContentsTravelFlags` allocates and fills that
  table from the source-side content decoder.
- `AAS_CreateReversedReachability` allocates the reversed reachability header
  table plus link slab, warns on 128+ reachable areas, and pushes reversed
  links onto the destination area's list.
- `AAS_AreaTravelTime` keeps the retail distance factors:
  crouch `1.3`, swim `1.0`, and normal walk `0.33`, with a minimum returned
  travel time of `1`.
- `AAS_CalculateAreaTravelTimes` precomputes the area travel-time lattice from
  reversed reachability and per-area reachability counts.
- `AAS_InitPortalMaxTravelTimes` is fused with the source-side
  `AAS_PortalMaxTravelTime` loop in retail; no standalone retail function was
  promoted for the small portal-max helper.

## Changes

- Promoted route-prelude aliases in
  `references/analysis/quakelive_symbol_aliases.json`:
  - `sub_4925F0 -> AAS_RoutingInfo`
  - `sub_492630 -> AAS_ClusterAreaNum`
  - `sub_492680 -> AAS_InitTravelFlagFromType`
  - `sub_4927E0 -> AAS_TravelFlagForType`
  - `sub_492800 -> AAS_RemoveRoutingCacheInCluster`
  - `sub_4928B0 -> AAS_RemoveRoutingCacheUsingArea`
  - `sub_492A20 -> AAS_AreaContentsTravelFlags`
  - `sub_492A40 -> AAS_InitAreaContentsTravelFlags`
  - `sub_492B10 -> AAS_CreateReversedReachability`
  - `sub_492C30 -> AAS_AreaTravelTime`
  - `sub_492F20 -> AAS_InitPortalMaxTravelTimes`
- Added `tests/test_botlib_route_prelude_parity.py`, covering:
  - alias-table rows,
  - Ghidra function sizes,
  - HLIL anchors and debug strings,
  - source-side route prelude structures,
  - AAS init and move-AI consumers,
  - a negative check preventing over-promotion of inlined/fused helpers.

## Negative Checks

- No C route body was changed. The retail build shape matches the current
  GPL-derived route source closely enough that algorithm edits would be
  speculative.
- The source helpers `AAS_UnlinkCache`, `AAS_LinkCache`,
  `AAS_FreeRoutingCache`, `AAS_RoutingTime`,
  `AAS_GetAreaContentsTravelFlags`, and `AAS_PortalMaxTravelTime` were not
  promoted as standalone symbols because this retail slice shows them inlined,
  fused, or otherwise absent as distinct callable functions.
- The adjacent `0x00482150..0x004829A0` unmapped block was rejected as a
  non-botlib false lead after HLIL inspection showed libjpeg memory-manager
  code rather than AAS route ownership.

## Validation

Focused validation:

```text
python -m pytest tests/test_botlib_route_prelude_parity.py -q
```

Observed result:

```text
4 passed in 0.07s
```

Broader botlib validation:

```text
$botlibTests = rg --files tests | Where-Object { $_ -match 'test_botlib_.*\.py$' }; python -m pytest $botlibTests -q
```

Observed result:

```text
99 passed in 2.54s
```

## Parity Estimate

- Focused AAS route-prelude helper mapping: approximately `55% -> 96%`.
- Focused route-cache invalidation and travel-flag wiring: approximately
  `72% -> 97%`.
- Overall botlib plus related AAS route/import wiring: approximately
  `80% -> 81%`.
- Repo-wide parity remains approximately `99%`; this pass reduces unmapped
  botlib helper uncertainty without changing runtime behavior.
