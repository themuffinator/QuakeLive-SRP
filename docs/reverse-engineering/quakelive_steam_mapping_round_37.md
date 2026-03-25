# Quake Live Steam Host Mapping Round 37

## Scope

This round closes a broad exact-match renderer tranche inside `quakelive_steam.exe`.

The main goal was to stop leaving the already-bounded renderer internals half-generic once the local source and committed HLIL now pin them cleanly. This pass promotes the top-level renderer export constructor, the renderer init entry point, the exact lighting and mark-projection helpers behind the already-mapped exports, and the internal MD3 model pipeline that feeds `R_AddMD3Surfaces`.

The primary local evidence for this round is:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `src/code/renderer/tr_init.c`
- `src/code/renderer/tr_light.c`
- `src/code/renderer/tr_marks.c`
- `src/code/renderer/tr_mesh.c`
- `src/code/renderer/tr_model.c`

## `sub_449F70`: Exact `GetRefAPI`

Observed local facts:

1. The helper copies the incoming import table into the global renderer import slab, matching `ri = *rimp;`.
2. It zeroes the static export table at `data_587848`, matching `Com_Memset( &re, 0, sizeof( re ) );`.
3. It emits the exact mismatch string:
   - `Mismatched REF_API_VERSION: expected %i, got %i\n`
4. It rejects any API version other than `9`, which is the committed `REF_API_VERSION`.
5. It then assembles the full renderer export table in the same source order, including the already-mapped scene/draw tail and the still-open font slot between `RE_RenderScene` and `RE_SetColor`:
   - `sub_44F550`
   - `sub_44F960`
   - `sub_43C7B0`
   - `sub_44DCD0`
   - `sub_44F710`
   - `sub_44F8A0`
   - `sub_450840`
   - `sub_450CD0`
   - `sub_4508C0`
   - `sub_44B060`
   - `sub_450E00`
   - `sub_450E40`
   - `sub_450E80`
   - `sub_451360`
   - `sub_43C650`
   - `sub_43C6C0`
   - `sub_436350`
   - `sub_4366D0`
   - `sub_4590F0`
   - `sub_43BEF0`
   - `sub_45E320`
6. The helper returns `&data_587848`, matching the source `return &re;`.

That closes `sub_449F70` as the exact renderer export constructor `GetRefAPI`.

## `sub_44A1F0`: Exact `R_Init`

Observed local facts:

1. The body emits the exact start and end banners:
   - `----- R_Init -----\n`
   - `----- finished R_Init -----\n`
2. It clears the renderer-global state blocks for `tr`, `backEnd`, and `tess`.
3. It fills the same four waveform tables over `FUNCTABLE_SIZE == 1024`:
   - `sinTable`
   - `squareTable`
   - `sawToothTable`
   - `inverseSawToothTable`
   - plus the derived `triangleTable`
4. It calls the same init chain, in the same order, as the committed source:
   - `R_InitFogTable`
   - `R_NoiseInit`
   - `R_Register`
   - backend poly/polyvert allocation
   - `R_ToggleSmpFrame`
   - `InitOpenGL`
   - `RB_InitRenderTargets`
   - `R_InitColorCorrection`
   - `R_InitImages`
   - `R_InitShaders`
   - `R_InitSkins`
   - `R_ModelInit`
   - `R_InitFreeType`
5. It performs the final `glGetError` check and prints `glGetError() = 0x%x\n` on non-zero error.

That is an exact body-level match for `R_Init`.

## Exact Lighting Helpers

### `sub_44A810`: `R_SetupEntityLightingGrid`

Observed local facts:

1. The helper chooses between `ent->e.lightingOrigin` and `ent->e.origin` from the same renderfx test used by the source `RF_LIGHTING_ORIGIN` branch.
2. It subtracts `tr.world->lightGridOrigin`, multiplies by `lightGridInverseSize`, floors each axis, stores integer cell positions, and clamps each position against `lightGridBounds - 1`.
3. It clears the same three output vectors:
   - `ambientLight`
   - `directedLight`
   - local `direction`
4. It builds the same light-grid addressing steps:
   - `8`
   - `8 * lightGridBounds[0]`
   - `8 * lightGridBounds[0] * lightGridBounds[1]`
5. It performs the same eight-sample trilerp, skipping samples whose ambient triple is all zero.
6. It accumulates the ambient and directed RGB triplets from bytes `0..5`, then decodes the lat/long direction from bytes `7` and `6` through the renderer sine table.
7. It renormalizes by `totalFactor` when the accumulated weight is between `0` and `0.99`, scales by `r_ambientScale` and `r_directedScale`, and normalizes the final direction into `ent->lightDir`.

That is the exact light-grid setup helper from `tr_light.c`.

### `sub_44ACB0`: `R_SetupEntityLighting`

Observed local facts:

1. The helper early-outs when `ent->lightingCalculated` is already set, then sets that flag on the first pass.
2. It again chooses between `lightingOrigin` and `origin` from the same `RF_LIGHTING_ORIGIN` branch as the source.
3. If `RDF_NOWORLDMODEL` is set or the world light grid is absent, it initializes both ambient and directed light to `tr.identityLight * 150` and copies the global sun direction.
4. Otherwise it dispatches directly into `sub_44A810`, the now-closed `R_SetupEntityLightingGrid`.
5. It adds the fixed minimum ambient contribution of `tr.identityLight * 32` to all three ambient channels.
6. It scales the initial light direction by the directed-light magnitude, then loops `refdef->num_dlights` and applies the exact inverse-square dynamic-light contribution with the same `DLIGHT_AT_RADIUS` and `DLIGHT_MINIMUM_RADIUS` constants.
7. It clamps ambient light against `tr.identityLightByte`, conditionally calls the debug logger that prints `amb:%i  dir:%i\n`, packs `ambientLightInt`, normalizes the working light vector, and transforms it into entity-local space through `ent->e.axis`.

That closes `sub_44ACB0` as the exact entity-lighting setup path.

## Exact Mark-Projection Helpers

### `sub_44D7F0`: `R_BoxSurfaces_r`

Observed local facts:

1. The helper tail-recurses over BSP nodes while `node->contents == -1`.
2. It uses the same `BoxOnPlaneSide` split against the node plane and recurses to both children when the box straddles the split.
3. In leaves, it walks `firstmarksurface` / `nummarksurfaces`.
4. It rejects surfaces with `SURF_NOIMPACT | SURF_NOMARKS` or `CONTENTS_FOG`.
5. For face surfaces it reruns `BoxOnPlaneSide` against the face plane and rejects faces whose plane normal forms a sharp angle with the projection direction via the same `DotProduct(normal, dir) > -0.5` test.
6. It de-duplicates via `surf->viewCount` and appends `surf->data` into the caller-provided list until `listsize` is reached.

That is an exact match for `R_BoxSurfaces_r`.

### `sub_44D920`: `R_AddMarkFragments`

Observed local facts:

1. The helper iterates the bounding planes and repeatedly clips the polygon through the same ping-pong pair of clip buffers.
2. It uses the same clip epsilon `0.5`.
3. It returns immediately when clipping removes the polygon entirely.
4. It also returns when `numClipPoints + *returnedPoints > maxPoints`, matching the point-buffer overflow guard.
5. On success it writes the next `markFragment_t` entry with:
   - `firstPoint = *returnedPoints`
   - `numPoints = numClipPoints`
6. It then copies the surviving polygon points into `pointBuffer + *returnedPoints * 3` and increments both returned counters.

That closes `sub_44D920` as the exact fragment-emission helper from `tr_marks.c`.

## Exact MD3 Surface Pipeline Helpers

### `sub_44E890`: `ProjectRadius`

Observed local facts:

1. The helper computes `c = DotProduct( viewAxis0, viewOrigin )`.
2. It computes the front-axis distance of `location` and returns `0` when the projected point is behind the viewer.
3. It builds the same temporary vector `p = { 0, fabs(r), -dist }`.
4. It multiplies that vector by the current projection matrix to produce a four-component projected vector.
5. It returns `projected[1] / projected[3]`, clamped to `1.0f`.

That is the exact static helper `ProjectRadius`.

### `sub_44E990`: `R_CullModel`

Observed local facts:

1. The helper resolves `newFrame` and `oldFrame` from the MD3 header `ofsFrames` plus `ent->e.frame` and `ent->e.oldframe`.
2. When `ent->e.nonNormalizedAxes == 0`, it performs the same sphere-cull fast path used by the source, including the two-frame comparison when the old and new frames differ.
3. It updates the same renderer performance counters for sphere cull in/out/clip.
4. It then builds the merged bounds box from the min of the old/new mins and the max of the old/new maxs.
5. It runs the same local-box cull and updates the matching box-cull performance counters before returning `CULL_IN`, `CULL_CLIP`, or `CULL_OUT`.

That is an exact body-level match for `R_CullModel`.

### `sub_44EBC0`: `R_ComputeLOD`

Observed local facts:

1. The helper returns `0` immediately when the current model exposes fewer than two LODs.
2. Otherwise it resolves the current MD3 frame from `tr.currentModel->md3[0] + ofsFrames + ent->e.frame`.
3. It computes the same frame radius from the frame bounds and feeds it into `sub_44E890`, the now-closed `ProjectRadius`.
4. It clamps `r_lodscale` to `20`, computes `1.0f - projectedRadius * lodscale`, multiplies by `numLods`, converts through `myftol`, and clamps to the valid LOD range.
5. It then applies `r_lodbias` and clamps the result a second time.

That is the exact LOD-selection helper `R_ComputeLOD`.

### `sub_44ECC0`: `R_ComputeFogNum`

Observed local facts:

1. The helper returns `0` immediately when `RDF_NOWORLDMODEL` is set.
2. It resolves the current MD3 frame and computes `localOrigin = ent->e.origin + md3Frame->localOrigin`.
3. It iterates world fog volumes starting at index `1`.
4. For each fog it applies the same three-axis radius-expanded bounds test:
   - `localOrigin[j] - radius >= fog->bounds[1][j]`
   - `localOrigin[j] + radius <= fog->bounds[0][j]`
5. It returns the first fog index whose bounds contain the model and otherwise returns `0`.

That closes `sub_44ECC0` as the exact fog-volume lookup helper.

### `sub_44EDB0`: `R_AddMD3Surfaces`

Observed local facts:

1. The helper derives the same `personalModel` test from `RF_THIRD_PERSON` and `!tr.viewParms.isPortal`.
2. On `RF_WRAP_FRAMES` it wraps both `ent->e.frame` and `ent->e.oldframe` by the current model's `numFrames`.
3. It emits the exact developer warning:
   - `R_AddMD3Surfaces: no such frame %d to %d for '%s'\n`
   and resets both frames to `0` on failure.
4. It calls the exact internal helper chain already mirrored by the source:
   - `sub_44EBC0` (`R_ComputeLOD`)
   - `sub_44E990` (`R_CullModel`)
   - `sub_44ACB0` (`R_SetupEntityLighting`) when the same personal-model and shadow conditions pass
   - `sub_44ECC0` (`R_ComputeFogNum`)
5. In the surface loop it handles the same three shader-selection branches:
   - `customShader`
   - `customSkin` surface-name lookup with the exact warnings
   - per-surface MD3 shader selection through `skinNum % surface->numShaders`
6. It adds the same optional stencil-shadow and projection-shadow drawsurfs, then adds the main drawsurf only when not rendering a hidden personal model.

That is the exact MD3 surface submission path from `tr_mesh.c`.

## Exact Model Registration Helpers

### `sub_44F080`: `R_GetModelByHandle`

Observed local facts:

1. The helper returns the default model when the handle is less than `1` or greater than or equal to `tr.numModels`.
2. Otherwise it returns `tr.models[index]` directly.

That is the exact handle lookup helper `R_GetModelByHandle`.

### `sub_44F0B0`: `R_AllocModel`

Observed local facts:

1. The helper returns `NULL` when `tr.numModels == 0x400`, matching `MAX_MOD_KNOWN`.
2. Otherwise it allocates `0x64` bytes from the low hunk, matching `sizeof( model_t )` in the current layout.
3. It writes `mod->index = tr.numModels`, stores the pointer in the model table, increments `tr.numModels`, and returns the new record.

That is the exact allocator `R_AllocModel`.

### `sub_44F690`: `R_GetTag`

Observed local facts:

1. The helper clamps the requested frame to `mod->numFrames - 1` when the incoming frame is too large.
2. It computes the tag base from `mod + ofsTags + frame * numTags * 0x70`, where `0x70` is the retail `md3Tag_t` stride.
3. It loops `numTags`, string-compares each tag name against the requested `tagName`, and returns the first match.
4. It returns `NULL` when no tag name matches.

That is the exact internal tag lookup helper `R_GetTag`.

### `sub_44F960`: `RE_RegisterModel`

Observed local facts:

1. The helper emits both source strings:
   - `RE_RegisterModel: NULL name\n`
   - `Model name exceeds MAX_QPATH\n`
2. It scans the current model table for a name match and returns an existing non-`MOD_BAD` handle when found.
3. It allocates a new model through `sub_44F0B0`, logs the same allocation failure string, copies the model name, and syncs the render thread before loading.
4. It loops LODs from `MD3_MAX_LODS - 1` down to `0`, appending the same `_%d.md3` suffix for non-zero LODs.
5. It reads the file, distinguishes `MD4_IDENT` from `MD3_IDENT`, and emits the exact unknown-fileid warning on mismatch.
6. It frees the file buffer, increments `numLods` on successful loads, duplicates lower-detail slots upward for any missing higher LODs, and marks the model `MOD_BAD` on failure.

That is the exact renderer model-registration entry point `RE_RegisterModel`.

## Promoted Aliases

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_449F70` (`0x00449F70`) | `GetRefAPI` | Observed | Exact renderer export-table constructor returning the populated `refexport_t`. |
| `sub_44A1F0` (`0x0044A1F0`) | `R_Init` | Observed | Exact renderer init entry point. |
| `sub_44A810` (`0x0044A810`) | `R_SetupEntityLightingGrid` | Observed | Exact light-grid trilerp helper for one entity. |
| `sub_44ACB0` (`0x0044ACB0`) | `R_SetupEntityLighting` | Observed | Exact entity-lighting setup path combining light-grid and dynamic-light contributions. |
| `sub_44D7F0` (`0x0044D7F0`) | `R_BoxSurfaces_r` | Observed | Exact recursive BSP mark-surface gather helper. |
| `sub_44D920` (`0x0044D920`) | `R_AddMarkFragments` | Observed | Exact clipped-mark fragment emission helper. |
| `sub_44E890` (`0x0044E890`) | `ProjectRadius` | Observed | Exact projected-radius helper used by the MD3 LOD path. |
| `sub_44E990` (`0x0044E990`) | `R_CullModel` | Observed | Exact MD3 sphere/box culling helper. |
| `sub_44EBC0` (`0x0044EBC0`) | `R_ComputeLOD` | Observed | Exact MD3 LOD selection helper. |
| `sub_44ECC0` (`0x0044ECC0`) | `R_ComputeFogNum` | Observed | Exact MD3 fog-volume lookup helper. |
| `sub_44EDB0` (`0x0044EDB0`) | `R_AddMD3Surfaces` | Observed | Exact MD3 surface submission path. |
| `sub_44F080` (`0x0044F080`) | `R_GetModelByHandle` | Observed | Exact model-table handle lookup helper. |
| `sub_44F0B0` (`0x0044F0B0`) | `R_AllocModel` | Observed | Exact model allocator. |
| `sub_44F690` (`0x0044F690`) | `R_GetTag` | Observed | Exact MD3 tag lookup helper. |
| `sub_44F960` (`0x0044F960`) | `RE_RegisterModel` | Observed | Exact renderer model-registration entry point. |

## Coverage Impact

On the committed `quakelive_steam.exe` Ghidra baseline of `5473` functions, this pass moves the explicit `quakelive_steam` alias set from `341` to `356` functions, which is approximately `6.2%` to `6.5%` host-symbol coverage.

## Open Questions

1. The adjacent MD3 loaders `sub_44F0F0` and `sub_44F300` are now more tightly bounded as the format-specific load paths, but this round stops short of promoting them until I write up the exact `R_LoadMD3` versus `R_LoadMD4` evidence cleanly.
2. `sub_44A150` is still left note-only. It is clearly part of the renderer bootstrap immediately before `R_Init`, but the current pass does not force whether its public-facing source name should follow a narrow registration helper or a broader pre-init platform/setup role.
3. `sub_451360` remains the still-open `GetRefAPI` font slot that sits between `RE_RenderScene` and `RE_SetColor`. Its export-table ownership is stable, but this round does not re-litigate the exact engine-side `RE_RegisterFont` proof because the surrounding renderer internals were the higher-value tranche to land first.
