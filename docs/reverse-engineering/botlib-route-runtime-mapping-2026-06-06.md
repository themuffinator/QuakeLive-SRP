# Botlib Route Runtime Mapping - 2026-06-06

## Scope

This pass selects the engine-owned AAS route runtime as the next botlib mapping
slice:

- `src/code/botlib/be_aas_route.c`
- `src/code/botlib/be_aas_routealt.c`
- `src/code/botlib/be_interface.c`
- `src/code/game/botlib.h`
- `src/code/game/g_syscalls.c`
- `src/code/server/sv_game.c`
- `src/code/server/ql_game_imports.inc`

The owning retail binary is `quakelive_steam.exe`. The committed Binary Ninja
HLIL and Ghidra function inventory provide the canonical evidence. This pass
does not require a game launch because the route-cache and route-query evidence
is visible in static retail references and the current source already matches
the observed bodies.

## Retail Evidence

Primary anchors:

- `AAS_FreeOldestCache @ 0x00493010`
- `AAS_FreeAllClusterAreaCache @ 0x00493140`
- `AAS_InitClusterAreaCache @ 0x00493230`
- `AAS_FreeAllPortalCache @ 0x004932E0`
- `AAS_InitRoutingUpdate @ 0x00493390`
- `AAS_WriteRouteCache @ 0x00493420`
- `AAS_ReadCache @ 0x00493670`
- `AAS_ReadRouteCache @ 0x004936D0`
- `AAS_InitReachabilityAreas @ 0x004938A0`
- `AAS_InitRouting @ 0x00493A50`
- `AAS_FreeRoutingCaches @ 0x00493AD0`
- `AAS_UpdateAreaRoutingCache @ 0x00493BA0`
- `AAS_GetAreaRoutingCache @ 0x00493F30`
- `AAS_UpdatePortalRoutingCache @ 0x004940D0`
- `AAS_GetPortalRoutingCache @ 0x00494300`
- `AAS_AreaRouteToGoalArea @ 0x00494460`
- `AAS_AreaTravelTimeToGoalArea @ 0x00494830`
- `AAS_PredictRoute @ 0x00494870`
- `AAS_ReachabilityFromNum @ 0x00494BB0`
- `AAS_NextAreaReachability @ 0x00494C10`
- `AAS_NextModelReachability @ 0x00494C90`
- `AAS_AltRoutingFloodCluster_r @ 0x00494D10`
- `AAS_AlternativeRouteGoals @ 0x00494DB0`

Observed retail facts:

- The route-cache writer builds `maps/%s.rcd`, writes the `MERC` route-cache
  identifier, keeps version `2`, records area and cluster counts, and stores
  CRCs over the area and cluster tables before writing portal-cache and
  cluster-area-cache chains.
- The route-cache reader uses the same `maps/%s.rcd` path, validates the
  `MERC` identifier, version, area count, cluster count, and CRCs, then
  rebuilds the portal and cluster cache linked lists. `AAS_ReadCache` restores
  the `reachabilities` pointer from the serialized cache size.
- `AAS_InitRouting` initializes travel flags, area-content travel flags,
  routing update slabs, reversed reachability, cluster cache, portal cache,
  area travel times, portal maximum travel times, reachability pass areas, the
  `max_routingcache` limit, and then attempts `AAS_ReadRouteCache`.
- `AAS_AreaRouteToGoalArea` performs the retail initialized/self-area guards,
  developer-gated range diagnostics, low-memory oldest-cache eviction loop,
  `TFL_DONOTENTER` widening, same-cluster cache lookup, portal-cache fallback,
  and best portal route selection.
- `AAS_AreaTravelTimeToGoalArea` is the thin wrapper over
  `AAS_AreaRouteToGoalArea` that returns only the travel-time out parameter.
- `AAS_PredictRoute` initializes `stopevent`, `endarea`, `endcontents`,
  `endtravelflags`, `endpos`, and `time`; then it walks reachability routes
  until the goal, max area count, map area count, max time, or a stop event is
  reached.
- `AAS_ReachabilityFromNum`, `AAS_NextAreaReachability`, and
  `AAS_NextModelReachability` retain the exact zero/copy behavior, fatal/range
  diagnostics, and elevator/func-bobbing model scan from the source.
- `AAS_AlternativeRouteGoals` keeps the retail midrange-area filter with the
  `1.1 * goaltraveltime` start threshold and `0.8 * goaltraveltime` goal
  threshold, floods adjacent midrange areas, chooses the cluster-center area,
  writes extra travel time, and caps output at `maxaltroutegoals`.

## Changes

- Promoted the missing route-cache helper aliases in
  `references/analysis/quakelive_symbol_aliases.json`:
  - `sub_493010 -> AAS_FreeOldestCache`
  - `sub_493140 -> AAS_FreeAllClusterAreaCache`
  - `sub_493230 -> AAS_InitClusterAreaCache`
  - `sub_4932E0 -> AAS_FreeAllPortalCache`
  - `sub_493390 -> AAS_InitRoutingUpdate`
  - `sub_493670 -> AAS_ReadCache`
  - `sub_4936D0 -> AAS_ReadRouteCache`
  - `sub_4938A0 -> AAS_InitReachabilityAreas`
- Added `tests/test_botlib_route_runtime_parity.py`, covering:
  - new and existing route helper aliases,
  - Ghidra function rows and sizes,
  - route-cache read/write source shape and HLIL anchors,
  - route initialization and shutdown order,
  - area route, travel-time wrapper, prediction, reachability copy/iterator,
    and model reachability source shape,
  - alternative-route goal selection and AAS export/import wiring.

## Negative Checks

- No C route body was changed. The retail HLIL matches the current source
  shape closely enough that changing the route algorithm would be speculative.
- The high-bit team travel flags are still handled through area-content and
  route travel-flag paths. The inline travel-type helper's effective retail
  behavior masks to the low travel-type bits before table lookup, so this pass
  does not "fix" the inherited helper without a contrary retail signal.
- No live-map AAS route generation claim is made. This pass maps and pins the
  route runtime source shape; it does not assert that every shipped `.aas`
  graph or map-dependent bot path is behaviorally exhausted.

## Validation

Focused validation:

```text
python -m pytest tests/test_botlib_route_runtime_parity.py -q
```

Observed result:

```text
4 passed in 0.21s
```

Broader botlib validation:

```text
python -m pytest tests/test_botlib_route_runtime_parity.py tests/test_botlib_weight_runtime_parity.py tests/test_botlib_support_runtime_parity.py tests/test_botlib_precompiler_token_parity.py tests/test_botlib_precompiler_macro_parity.py tests/test_botlib_precompiler_directive_parity.py tests/test_botlib_memory_parity.py tests/test_botlib_libvar_parity.py tests/test_botlib_internal_parity.py tests/test_botlib_ea_parity.py tests/test_botlib_chat_parity.py -q
```

Observed result:

```text
61 passed in 1.87s
```

## Parity Estimate

- Focused AAS route-cache/readback helper mapping: approximately `70% -> 96%`.
- Focused route query, prediction, and alternative-route-goal source mapping:
  approximately `82% -> 97%`.
- Overall botlib plus related AAS route/import wiring: approximately
  `78% -> 80%`.
- Repo-wide parity remains approximately `99%`; this pass reduces botlib route
  uncertainty and promotes evidence-backed names rather than changing broad
  runtime behavior.
