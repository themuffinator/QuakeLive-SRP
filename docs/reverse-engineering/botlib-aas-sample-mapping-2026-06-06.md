# Botlib AAS Sample Mapping - 2026-06-06

## Scope

This pass maps the botlib AAS sample/query layer and the engine/qagame wiring
that exposes it:

- `src/code/botlib/be_aas_sample.c`
- `src/code/botlib/be_interface.c`
- `src/code/game/botlib.h`
- `src/code/game/g_public.h`
- `src/code/game/g_syscalls.c`
- `src/code/server/sv_game.c`
- `src/code/server/ql_game_imports.inc`

The owning retail binary is `quakelive_steam.exe`. The committed HLIL and
Ghidra corpus are sufficient for this static mapping round, so no game launch
was needed.

## Evidence Inputs

- Canonical binary: `assets/quakelive/quakelive_steam.exe`
- Binary Ninja HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part03.txt`
- Ghidra function rows:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- Source owners:
  `src/code/botlib/be_aas_sample.c`,
  `src/code/botlib/be_interface.c`,
  `src/code/game/botlib.h`,
  `src/code/game/g_public.h`,
  `src/code/game/g_syscalls.c`,
  `src/code/server/sv_game.c`,
  and `src/code/server/ql_game_imports.inc`

## Promoted Names

| Retail address | Promoted name | Evidence summary |
|---|---|---|
| `sub_495270` | `AAS_PresenceTypeBoundingBox` | Normal/crouch presence bounding boxes and fatal unknown-presence diagnostic. |
| `sub_495350` | `AAS_InitAASLinkHeap` | `max_aaslinks` libvar, default `6144`, and link-heap free-list setup. |
| `sub_495420` | `AAS_FreeAASLinkHeap` | Frees the link heap and clears heap state. |
| `sub_495450` | `AAS_InitAASLinkedEntities` | Allocates the per-area linked-entity head array from `numareas`. |
| `sub_495490` | `AAS_FreeAASLinkedEntities` | Frees and clears the linked-entity head array. |
| `sub_4954B0` | `AAS_PointAreaNum` | BSP node walk from node `1`, returning the negative leaf area number. |
| `sub_495540` | `AAS_PointReachabilityAreaIndex` | Null-origin total reachability count plus point-area cluster index calculation. |
| `sub_495670` | `AAS_AreaPresenceType` | Area bounds guard and `areasettings[areanum].presencetype` return. |
| `sub_4956C0` | `AAS_PointPresenceType` | Point-area lookup with `PRESENCE_NONE` fallback for no area. |
| `sub_495700` | `AAS_AreaEntityCollision` | Presence bbox expansion, linked-entity scan, pass-entity skip, and BSP collision copy-out. |
| `sub_4957F0` | `AAS_TraceClientBBox` | 127-entry trace stack, presence rejection, entity collision path, and trace-plane epsilon. |
| `sub_495F40` | `AAS_TraceAreas` | 127-entry area trace stack, area/point collection, and stack-overflow guard. |
| `sub_4962F0` | `AAS_InsideFace` | Edge separator-normal checks for point-in-face classification. |
| `sub_496460` | `AAS_BoxOnPlaneSide2` | Non-axial bbox-vs-plane side calculation using two extreme corners. |
| `sub_496550` | `AAS_UnlinkFromAreas` | Removes entity links from area lists and returns links to the free list. |
| `sub_4965C0` | `AAS_AASLinkEntity` | BSP stack walk linking a bbox into touched AAS areas. |
| `sub_496760` | `AAS_LinkEntityClientBBox` | Presence bbox expansion wrapper around `AAS_AASLinkEntity`. |
| `sub_4967E0` | `AAS_BBoxAreas` | Temporary entity link pass used to enumerate areas touched by a bbox. |
| `sub_496830` | `AAS_AreaInfo` | Copies cluster, contents, flags, presence type, bounds, and center into public info. |
| `sub_496920` | `AAS_PlaneFromNum` | Loaded guard and direct `aasworld.planes[planenum]` lookup. |

## Source Reconstruction

No C source body change is justified for this tranche. The checked-in
`be_aas_sample.c` implementation already matches the retail static shape for
the mapped helpers:

- Presence box constants match the retail normal and crouch extents.
- Link heap setup uses the retail `max_aaslinks` default and free-list layout.
- Point, area, and reachability-index queries follow the observed BSP/cluster
  traversal and diagnostic behavior.
- Client bbox tracing and trace-area enumeration retain the retail 127-entry
  traversal stack and overflow diagnostics.
- Area entity collision, entity linking, temporary bbox-area enumeration, and
  unlinking preserve the observed linked-list ownership model.
- Public AAS export order and both the legacy syscall table and Quake Live
  native qagame import slab match the current retail-backed wiring shape.

## Validation

Added `tests/test_botlib_aas_sample_parity.py` to pin:

1. The promoted sample-layer aliases, Ghidra function sizes, HLIL function
   headers, and key diagnostics.
2. Source shape for presence bounding boxes, link heap lifecycle, linked-area
   lifecycle, point/area presence queries, and reachability-area indexing.
3. Source shape for area entity collision, client bbox tracing, area tracing,
   face/plane geometry, entity area linking, bbox area enumeration, area info,
   and plane lookup.
4. Public `aas_export_t` order, `Init_AAS_Export` assignments, server VM
   syscall dispatch, legacy qagame import table, Quake Live native import
   slab, qagame direct wrappers, and qagame syscall wrappers.

Focused validation:

```text
python -m pytest tests/test_botlib_aas_sample_parity.py -q
```

Observed result:

```text
4 passed in 0.13s
```

Broader botlib validation:

```text
$files = Get-ChildItem tests -Filter test_botlib_*.py | ForEach-Object { $_.FullName }; python -m pytest $files -q
```

Observed result:

```text
75 passed in 2.64s
```

Mixed botlib/native import validation:

```text
python -m pytest tests/test_botlib_aas_sample_parity.py tests/test_botlib_reachability_generation_parity.py tests/test_botlib_route_runtime_parity.py tests/test_botlib_internal_parity.py tests/test_game_native_export_helper_parity.py -q
```

Observed result:

```text
56 passed in 1.57s
```

## Parity Estimate

- Focused AAS sample/query helper mapping: approximately `79% -> 95%`.
- Overall botlib plus AAS sample/import wiring: approximately `84% -> 85%`.
- Remaining uncertainty is live-map `.aas` content and map-dependent bot
  behavior, not the static sample/query ownership or public wiring covered by
  this pass.
