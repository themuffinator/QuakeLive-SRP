# quakelive_steam.exe Mapping Round 157

Date: 2026-04-27

Scope: engine-owned botlib routing-cache recovery around the old
`0x004940D0` queue head, plus exact retained `libvorbis` `mdct.c` helper
mapping around the old `0x0051FF40` support-library head. This pass stayed
mapping-only.

## Summary

This round resolved `16` additional `quakelive_steam.exe` rows.
Classification mix:

- `8` engine-owned functions
- `0` platform-service-owned functions
- `8` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main engine outcome is that the old `0x00493F30` through `0x00494D10`
botlib slab now reads cleanly as the area-cache/portal-cache routing helpers
from `be_aas_route.c` plus the flood helper under `AAS_AlternativeRouteGoals`.
The important distinction is that the already mapped `sub_493BA0` remains
`AAS_UpdateAreaRoutingCache`, while the old queue head `sub_4940D0` is the
separate portal-cache updater that drives cache expansion by calling back into
`sub_493F30`.

The support-library outcome is that the old `0x0051FB50` through
`0x00520430` slab now resolves as the retained `mdct.c` setup and butterfly
lane underneath the already mapped `mdct_forward` and `mdct_backward`
implementations.

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_4940D0` | `547` | engine-owned | `AAS_UpdatePortalRoutingCache` | High | Closed from the exact portal-cache worklist flow, portal fanout, and recursive calls into `AAS_GetAreaRoutingCache`. |
| 2 | `sub_51FF40` | `535` | support-library | `mdct_butterfly_32` | High | Closed from the exact 32-point butterfly constants and the final `mdct_butterfly_16` pair. |
| 3 | `sub_51FB90` | `500` | support-library | `mdct_init` | High | Closed from the exact trig-table, bitreverse-table, and `lookup->scale = 4.f / n` initialization path. |
| 4 | `sub_493F30` | `414` | engine-owned | `AAS_GetAreaRoutingCache` | High | Closed from the exact two-dimensional `clusterareacache[cluster][clusterareanum]` lookup/allocation/link/update flow. |
| 5 | `sub_5202C0` | `350` | support-library | `mdct_butterfly_generic` | High | Closed from the exact staged trig-stride `trigint` walk over the generic butterfly body. |
| 6 | `sub_520160` | `337` | support-library | `mdct_butterfly_first` | High | Closed from the exact first-stage `T[0/1]`, `T[4/5]`, `T[8/9]`, `T[12/13]` butterfly layout. |
| 7 | `sub_494300` | `331` | engine-owned | `AAS_GetPortalRoutingCache` | High | Closed from the exact one-dimensional `portalcache[areanum]` lookup/allocation/link/update flow. |
| 8 | `sub_51FE40` | `248` | support-library | `mdct_butterfly_16` | High | Closed from the exact 16-point half-angle stages and paired `mdct_butterfly_8` calls. |
| 9 | `sub_520430` | `180` | support-library | `mdct_butterflies` | High | Closed from the exact `log2n - 5` stage count, first-stage/generic-stage loop, and final 32-point sweep. |
| 10 | `sub_51FD90` | `167` | support-library | `mdct_butterfly_8` | High | Closed from the exact in-place 8-point butterfly register pattern. |
| 11 | `sub_494D10` | `145` | engine-owned | `AAS_AltRoutingFloodCluster_r` | High | Closed from the exact recursive flood across adjacent faces while clearing the midrange-area valid bit and appending cluster areas. |
| 12 | `sub_494C10` | `123` | engine-owned | `AAS_NextAreaReachability` | High | Closed from the exact `firstreachablearea` / `numreachableareas` iteration logic and matching fatal/range diagnostics. |
| 13 | `sub_494C90` | `113` | engine-owned | `AAS_NextModelReachability` | High | Closed from the exact `TRAVEL_ELEVATOR` / `TRAVEL_FUNCBOB` scan over the reachability table. |
| 14 | `sub_494BB0` | `89` | engine-owned | `AAS_ReachabilityFromNum` | High | Closed from the exact initialized/range guards plus `sizeof(aas_reachability_t) == 0x2c` copy/clear behavior. |
| 15 | `sub_51FB50` | `56` | support-library | `mdct_clear` | High | Closed from the exact `trig` / `bitrev` free-and-zero path. |
| 16 | `sub_494830` | `49` | engine-owned | `AAS_AreaTravelTimeToGoalArea` | High | Closed from the exact wrapper that returns only the `traveltime` out-parameter from `AAS_AreaRouteToGoalArea`. |

## Evidence Notes

- The botlib routing-cache tranche maps one-to-one against the checked-in
  [be_aas_route.c](</E:/Repositories/QuakeLive-reverse/src/code/botlib/be_aas_route.c:1399>)
  and
  [be_aas_routealt.c](</E:/Repositories/QuakeLive-reverse/src/code/botlib/be_aas_routealt.c:66>)
  helpers:
  [AAS_GetAreaRoutingCache](</E:/Repositories/QuakeLive-reverse/src/code/botlib/be_aas_route.c:1399>),
  [AAS_UpdatePortalRoutingCache](</E:/Repositories/QuakeLive-reverse/src/code/botlib/be_aas_route.c:1445>),
  [AAS_GetPortalRoutingCache](</E:/Repositories/QuakeLive-reverse/src/code/botlib/be_aas_route.c:1543>),
  [AAS_AreaTravelTimeToGoalArea](</E:/Repositories/QuakeLive-reverse/src/code/botlib/be_aas_route.c:1767>),
  [AAS_ReachabilityFromNum](</E:/Repositories/QuakeLive-reverse/src/code/botlib/be_aas_route.c:1919>),
  [AAS_NextAreaReachability](</E:/Repositories/QuakeLive-reverse/src/code/botlib/be_aas_route.c:1939>),
  [AAS_NextModelReachability](</E:/Repositories/QuakeLive-reverse/src/code/botlib/be_aas_route.c:1974>),
  [AAS_AltRoutingFloodCluster_r](</E:/Repositories/QuakeLive-reverse/src/code/botlib/be_aas_routealt.c:66>),
  and [AAS_AlternativeRouteGoals](</E:/Repositories/QuakeLive-reverse/src/code/botlib/be_aas_routealt.c:99>).
- `sub_493F30` versus `sub_494300` was the key ownership split. The former
  indexes a two-dimensional cache table by cluster and cluster-area number and
  therefore matches `AAS_GetAreaRoutingCache`; the latter indexes a
  one-dimensional per-area portal cache list and therefore matches
  `AAS_GetPortalRoutingCache`.
- `sub_4940D0` is specifically `AAS_UpdatePortalRoutingCache`, not another
  copy of `AAS_UpdateAreaRoutingCache`. The HLIL seeds a work item from
  `portalcache->cluster/areanum/starttraveltime`, probes portal reachability
  through `sub_493F30`, updates `portalcache->traveltimes[portalnum]`, and
  adds the `portalmaxtraveltimes` penalty for the next cluster hop exactly as
  the source does.
- The MDCT tranche maps one-to-one against the bundled
  [mdct.c](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/mdct.c:51>)
  helper lane:
  [mdct_init](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/mdct.c:51>),
  [mdct_butterfly_8](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/mdct.c:93>),
  [mdct_butterfly_16](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/mdct.c:117>),
  [mdct_butterfly_32](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/mdct.c:152>),
  [mdct_butterfly_first](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/mdct.c:216>),
  [mdct_butterfly_generic](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/mdct.c:263>),
  [mdct_butterflies](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/mdct.c:316>),
  and [mdct_clear](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/mdct.c:338>).
- `sub_51FF40` is an exact `mdct_butterfly_32` hit. The retained constants
  `0.9238795`, `0.3826834`, and `0.7071067` line up with `cPI1_8`,
  `cPI3_8`, and `cPI2_8`, and the function ends by dispatching into the two
  16-point butterflies just like source.
- `sub_51FB90` is an exact `mdct_init` hit. The body allocates `bitrev` and
  `trig`, builds the three trig sub-tables, writes the paired bitreverse
  entries, and stores the final `scale = 4.f / n` value in the lookup.

## Aliases Added

- `sub_493F30` -> `AAS_GetAreaRoutingCache`
- `sub_4940D0` -> `AAS_UpdatePortalRoutingCache`
- `sub_494300` -> `AAS_GetPortalRoutingCache`
- `sub_494830` -> `AAS_AreaTravelTimeToGoalArea`
- `sub_494BB0` -> `AAS_ReachabilityFromNum`
- `sub_494C10` -> `AAS_NextAreaReachability`
- `sub_494C90` -> `AAS_NextModelReachability`
- `sub_494D10` -> `AAS_AltRoutingFloodCluster_r`
- `sub_51FB50` -> `mdct_clear`
- `sub_51FB90` -> `mdct_init`
- `sub_51FD90` -> `mdct_butterfly_8`
- `sub_51FE40` -> `mdct_butterfly_16`
- `sub_51FF40` -> `mdct_butterfly_32`
- `sub_520160` -> `mdct_butterfly_first`
- `sub_5202C0` -> `mdct_butterfly_generic`
- `sub_520430` -> `mdct_butterflies`

## Verification

Static mapping validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- scoped duplicate-key scan for the `quakelive_steam` alias block passed with
  `0` duplicates
- recount after this pass: `1799` raw alias entries, `1728` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `31.573%` of `5473` functions
- `git diff --check` passed aside from the repo's existing LF -> CRLF
  normalization warnings on touched text files
- no build or runtime launch was needed; this was mapping-only work on the
  committed evidence corpus

Parity estimate after this pass:

- strict-retail Windows replacement target: `100%` before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

After this round, the refreshed largest-unaliased queue begins with:

| # | Address | Ghidra name | Size |
| ---: | --- | --- | ---: |
| 1 | `0x004FC240` | `FUN_004fc240` | `537` |
| 2 | `0x004FAF60` | `FUN_004faf60` | `534` |
| 3 | `0x00510410` | `FUN_00510410` | `533` |
| 4 | `0x00501ED0` | `FUN_00501ed0` | `529` |
| 5 | `0x00498BB0` | `FUN_00498bb0` | `526` |
| 6 | `0x00503630` | `FUN_00503630` | `526` |
| 7 | `0x004AC440` | `FUN_004ac440` | `521` |
| 8 | `0x00511670` | `FUN_00511670` | `520` |
| 9 | `0x00523B40` | `FUN_00523b40` | `520` |
| 10 | `0x00524370` | `FUN_00524370` | `520` |

The next pass can return to the still-transformed `vorbisfile.c` search helper
at `sub_4FC240`, stay in the large adjacent support-library leftovers around
`sub_4FAF60` and `sub_510410`, or push deeper into the remaining AAS route
and visibility debt beyond the newly cleaned cache layer.
