# Quake Live Steam Host Mapping Round 52

## Scope

This round closes the remaining `tr_world.c` spine after the sky/surface work
and then pushes into the adjoining host-side arena/map-pool management block.

The newly promoted slice covers:

- world culling, dlight filtering, BSP traversal, and PVS marking
- the shared arena info parser and host arena-definition loader
- Quake Live's host-side map-pool helpers around `mappool.txt` and `nextmaps`

Primary evidence for this round:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `src/code/renderer/tr_world.c`
- `src/code/ui/ui_gameinfo.c`
- `src/code/game/g_bot.c`
- `src/code/game/g_factory.c`

## World Model Closures

### `sub_45D7F0`: `R_CullGrid`

Observed facts:

1. The helper checks `r_nocurves`, then selects `R_CullLocalPointAndRadius` or
   `R_CullPointAndRadius` based on `tr.currentEntityNum`.
2. On `CULL_OUT` and `CULL_CLIP` it updates the exact patch sphere/box cull
   counters before optionally calling `R_CullLocalBox`.
3. It returns `qtrue` only for fully rejected grids.

That is exactly `R_CullGrid`.

### `sub_45D890`: `R_CullSurface`

The helper dispatches on `SF_GRID`, `SF_TRIANGLES`, and `SF_FACE`, respects
`r_nocull`, `shader->cullType`, and `r_facePlaneCull`, and compares the viewer
dot product against `plane.dist +/- 8`. That is exactly `R_CullSurface`.

### `sub_45D960`: `R_DlightFace`

The helper iterates the active dlight bitmask, measures signed distance from
each light origin to the face plane, clears non-intersecting bits, updates
`tr.pc.c_dlightSurfacesCulled` when nothing remains, and stores the result to
`face->dlightBits[tr.smpFrame]`. That is exactly `R_DlightFace`.

### `sub_45DB70`: `R_DlightGrid`

The helper performs the six-axis radius-vs-bounds checks against
`grid->meshBounds`, clears non-touching light bits, updates the same culled
counter, and stores to `grid->dlightBits[tr.smpFrame]`. That is exactly
`R_DlightGrid`.

### `sub_45DE60`: `R_DlightSurface`

The helper dispatches on `SF_FACE`, `SF_GRID`, and `SF_TRIANGLES`, forwards to
`R_DlightFace`, `R_DlightGrid`, or the trisurf fast path, and increments
`tr.pc.c_dlightSurfaces` when the resulting mask is non-zero. That is exactly
`R_DlightSurface`.

### `sub_45DEB0`: `R_AddBrushModelSurfaces`

Observed facts:

1. The helper resolves `ent->e.hModel` through `R_GetModelByHandle` and reads
   the embedded `bmodel`.
2. It culls the local bounds, calls `R_DlightBmodel`, and iterates each brush
   surface.
3. Inside the surface loop, the `R_AddWorldSurface` logic is compiler-folded
   inline: view-count guard, `R_CullSurface`, optional `R_DlightSurface`, then
   `R_AddDrawSurf`.

This code entity corresponds to `R_AddBrushModelSurfaces`, with
`R_AddWorldSurface` inlined into the emitted loops instead of appearing as a
standalone start.

### `sub_45DF70`: `R_RecursiveWorldNode`

The helper checks `node->visframe`, performs the four frustum plane tests with
`BoxOnPlaneSide`, splits dlights against `node->plane`, recurses front child
first, updates `tr.viewParms.visBounds`, and then emits marked surfaces from
leaf nodes. That is exactly `R_RecursiveWorldNode`.

### `sub_45E270`: `R_PointInLeaf`

The exact error string `R_PointInLeaf: bad model`, the BSP plane walk, and the
terminal `contents != -1` condition identify this helper as `R_PointInLeaf`.

### `sub_45E2E0`: `R_ClusterPVS`

The helper returns `tr.world->novis` when the world or vis data is absent or
when the cluster index is out of range; otherwise it returns
`tr.world->vis + cluster * tr.world->clusterBytes`. That is exactly
`R_ClusterPVS`.

### `sub_45E370`: `R_MarkLeaves`

Observed facts:

1. The helper checks `r_lockpvs`, recomputes the current view cluster through
   `R_PointInLeaf`, and emits the exact `cluster:%i  area:%i\n` diagnostic.
2. It increments `tr.visCount`, handles the `r_novis` fast path, and otherwise
   fetches the PVS through `R_ClusterPVS`.
3. It walks every node/leaf, filters by cluster and area mask, and bubbles
   `visframe` markings up each parent chain.

That is exactly `R_MarkLeaves`.

### `sub_45E4F0`: `R_AddWorldSurfaces`

The helper checks `r_drawworld` and `RDF_NOWORLDMODEL`, sets
`tr.currentEntityNum = ENTITYNUM_WORLD`, calls `R_MarkLeaves`, clears
`tr.viewParms.visBounds`, clamps `tr.refdef.num_dlights` to `32`, and kicks off
`R_RecursiveWorldNode`. That is exactly `R_AddWorldSurfaces`.

### Existing Alias Revalidated: `sub_45E320 -> R_inPVS`

This round revalidated the existing `R_inPVS` promotion by confirming the exact
`R_PointInLeaf -> CM_ClusterPVS -> R_PointInLeaf` flow and the bit test on the
destination leaf's cluster.

## Arena And Map-Pool Closures

### `sub_45E570`: `UI_ParseInfos`

The helper emits the exact strings `Missing { in info file\n`,
`Max infos exceeded\n`, `Unexpected end of info file\n`, and `<NULL>`, while
walking `{ key value }` blocks into allocated info strings. That is the shared
arena parser logic used by both `g_bot.c` and `ui_gameinfo.c`; for the host
mapping pass it is promoted as `UI_ParseInfos` because the surrounding callers
are the host-side arena cache loaders.

### `sub_45E760`: `Factory_FindById`

The helper linearly scans the host factory table, compares the requested id to
the first string field of each `0x834`-byte record, and returns the matching
entry pointer or `NULL`. That is exactly the host-side equivalent of
`Factory_FindById`.

### `sub_45E9F0`: `MapPool_FindEntryByMapName`

The helper walks the loaded map-pool entries, compares the leading map-name
field, and returns the matching record pointer. The current source tree does
not expose this helper as a standalone function, so the promoted name is
descriptive rather than sourced from a committed definition.

### `sub_45EA60`: `UI_LoadArenasFromFile`

Observed facts:

1. The helper enforces the exact `file not found` and `file too large` guard
   strings used by the arena loaders.
2. It reads one arena text file and immediately feeds the buffer through the
   `UI_ParseInfos` helper.
3. It then copies `"map"`, `"longname"`, and `"type"` keys into the host map
   cache, mirroring the arena-to-map-list construction performed by
   `UI_LoadArenas`.

This emitted function corresponds to the host-side `UI_LoadArenasFromFile`
stage, with part of the later cache-population work fused into the same body.

### `sub_45EC80`: `UI_LoadArenas`

The helper loads the default arenas file, enumerates `scripts/*.arena`, feeds
each path through `sub_45EA60`, and prints `%i arenas parsed\n`. That is
exactly the host-side `UI_LoadArenas` loader.

### `sub_45ED90`: `ReloadArenaDefinitions_f`

The helper prints `reloading arena definitions...\n`, clears the host arena
cache, resets the loaded count, and tailcalls `UI_LoadArenas`. The current tree
does not expose a matching standalone function, so this promotion is a
descriptive host-side command name inferred from the exact string plus the
reset-and-reload control flow.

### `sub_45EDD0`: `MapPool_LoadFromFile`

The helper opens a map-pool file, enforces the exact `rotation file not found`
and `rotations file too large` diagnostics, tokenizes each line, validates
factories via `Factory_FindById`, validates maps through
`MapPool_FindEntryByMapName`, and appends accepted entries into the host map
pool. The current source has a newer rotation-cache split, so this promotion
uses a descriptive host-side map-pool name.

### `sub_45F050`: `MapPool_BuildNextMapsCvar`

Observed facts:

1. The helper seeds the preview with the current map when available.
2. It appends additional entries from the loaded map pool, formatting
   `map_%i`, `title_%i`, `cfg_%i`, and `gt_%i` keys.
3. It writes the final info payload into the `nextmaps` cvar.

That is a clean host-side `nextmaps` builder, promoted as
`MapPool_BuildNextMapsCvar`.

### `sub_45F340`: `MapPool_Reload_f`

HLIL shows a non-`functions.csv` helper that prints `reloading map pool...\n`,
clears the map-pool storage, resets the count, and then tailcalls
`MapPool_LoadFromFile` with the current `sv_mapPoolFile` path. This is promoted
as `MapPool_Reload_f`.

## Completion Summary

This round promotes:

- `R_CullGrid`
- `R_CullSurface`
- `R_DlightFace`
- `R_DlightGrid`
- `R_DlightSurface`
- `R_AddBrushModelSurfaces`
- `R_RecursiveWorldNode`
- `R_PointInLeaf`
- `R_ClusterPVS`
- `R_MarkLeaves`
- `R_AddWorldSurfaces`
- `UI_ParseInfos`
- `Factory_FindById`
- `MapPool_FindEntryByMapName`
- `UI_LoadArenasFromFile`
- `UI_LoadArenas`
- `ReloadArenaDefinitions_f`
- `MapPool_LoadFromFile`
- `MapPool_BuildNextMapsCvar`
- `MapPool_Reload_f`

Remaining nearby standalone gaps after this pass are concentrated in the
random-map/factory helpers at:

- `0x0045E7D0`
- `0x0045E830`
- `0x0045E8B0`
- `0x0045E940`
- `0x0045F380`

These are all in the same Quake Live host map-pool/factory management band and
form the logical follow-up tranche.
