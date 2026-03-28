# Quake Live Steam Host Mapping Round 45

## Scope

This round closes most of the remaining standalone `tr_light.c` and `tr_main.c`
helper band immediately above the previous renderer bootstrap pass.

The newly promoted tranche covers:

- dynamic-light transform and bmodel mask helpers
- the entity-light debug logger
- the front-end cull, transform, and orientation math chain
- the portal, mirror, and offscreen rejection helpers
- the drawsurf sort and render-view spine

The primary local evidence for this round is:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `src/code/renderer/tr_light.c`
- `src/code/renderer/tr_main.c`

## Exact Dynamic-Light Helpers

### `sub_44A490`: `R_TransformDlights`

Observed local facts:

1. The helper iterates an array of light records and subtracts the
   orientation origin from each light origin.
2. It writes three transformed coordinates into the per-light trailing
   storage using the exact `DotProduct( temp, or->axis[n] )` pattern.
3. `sub_44A720` calls it before computing the bmodel dlight mask.

That is the exact dynamic-light transform helper `R_TransformDlights`.

### `sub_44A720`: `R_DlightBmodel`

Observed local facts:

1. The helper calls the newly closed `R_TransformDlights` on
   `tr.refdef.num_dlights`, `tr.refdef.dlights`, and `tr.or`.
2. It tests each transformed light against the six bmodel bounds planes and
   accumulates a bitmask.
3. It stores the resulting mask into `tr.currentEntity->needDlights` and then
   writes the same mask to face, grid, and triangle surface dlight bitfields.

That is the exact bmodel dlight masker `R_DlightBmodel`.

### `sub_44ABE0`: `LogLight`

Observed local facts:

1. The helper only runs for entities with the first-person renderfx bit set.
2. It computes the max ambient and directed components from the entity light
   vectors.
3. It prints the exact debug string:
   - `amb:%i  dir:%i\n`

That is the exact debug-light logger `LogLight`.

## Exact Culling, Transform, And Orientation Helpers

### `sub_44B1E0`: `R_CullLocalBox`

Observed local facts:

1. The helper returns early when the nocull CVar is enabled.
2. It expands the eight bounds corners, transforms them into world space with
   `tr.or.origin` and `tr.or.axis`, and then tests them against the four view
   frustum planes.
3. It returns the exact three-way cull states used by `tr_main.c`:
   out, in, or clipped.

That is the exact box-cull helper `R_CullLocalBox`.

### `sub_44B4E0`: `R_CullPointAndRadius`

Observed local facts:

1. The helper checks a world-space point sphere against the four frustum
   planes.
2. It returns immediately when the point sphere is fully outside any plane.
3. It tracks the clipped case separately and otherwise reports fully inside.

That is the exact sphere-cull helper `R_CullPointAndRadius`.

### `sub_44D1A0`: `R_CullLocalPointAndRadius`

Observed local facts:

1. The helper first calls the local-to-world transform helper on the input
   point.
2. It then tail-calls the exact world-space sphere cull helper.

That is the exact wrapper `R_CullLocalPointAndRadius`.

### `sub_44B570`: `R_LocalNormalToWorld`

Observed local facts:

1. The helper multiplies a local vector by the three orientation axes without
   adding origin.
2. The coefficient order matches the source `R_LocalNormalToWorld` layout.

That is the exact normal transform helper `R_LocalNormalToWorld`.

### `sub_44B5E0`: `R_LocalPointToWorld`

Observed local facts:

1. The helper uses the same axis multiply as `R_LocalNormalToWorld`.
2. It additionally adds `tr.or.origin` to all three outputs.

That is the exact point transform helper `R_LocalPointToWorld`.

### `sub_44B660`: `R_TransformModelToClip`

Observed local facts:

1. The helper multiplies a 3D source point by a 4x4 model matrix to produce an
   intermediate eye-space vec4.
2. It then multiplies that eye vector by a second 4x4 projection matrix to
   produce the clip-space vec4.

That is the exact clip transform helper `R_TransformModelToClip`.

### `sub_44B760`: `myGlMultMatrix`

Observed local facts:

1. The helper multiplies two 4x4 matrices into a third output matrix.
2. The inner multiply-add order matches the local renderer matrix helper.
3. `sub_44B810` and `sub_44B9E0` both use it in the exact spots where the
   source uses `myGlMultMatrix`.

That is the exact matrix multiply helper `myGlMultMatrix`.

### `sub_44B810`: `R_RotateForEntity`

Observed local facts:

1. Non-model entities copy `viewParms->world` straight into the output
   orientation.
2. Model entities copy entity origin and axis into the output orientation,
   build a GL matrix, multiply it by `viewParms->world.modelMatrix`, and
   compute `viewOrigin`.
3. The helper is called from the exact places that need model-space culling and
   portal rotation.

That is the exact orientation builder `R_RotateForEntity`.

### `sub_44B9E0`: `R_RotateForViewer`

Observed local facts:

1. The helper clears `tr.or`, seeds the identity axes, and copies
   `tr.viewParms.or.origin` into `tr.or.viewOrigin`.
2. It builds the viewer matrix from the current camera axes and origin.
3. It multiplies that viewer matrix by the static flip matrix and stores the
   result into `tr.or.modelMatrix`.
4. It finishes by copying `tr.or` into `tr.viewParms.world`.

That is the exact viewer-orientation setup helper `R_RotateForViewer`.

### `sub_44BB50`: `SetFarClip`

Observed local facts:

1. The helper special-cases the no-world-model path and writes `2048` as the
   far clip distance.
2. Otherwise it iterates the eight `visBounds` corners, computes the squared
   distance from the current view origin, and keeps the maximum.
3. It stores the square root of that maximum into the current view's `zFar`.

That is the exact far-clip helper `SetFarClip`.

### `sub_44BE00`: `R_SetupProjection`

Observed local facts:

1. The helper starts by calling `SetFarClip`.
2. It derives `xmin`, `xmax`, `ymin`, and `ymax` from `r_znear`, `fov_x`, and
   `fov_y` using the same `tan(... * pi / 360)` formulas as the source.
3. It writes the exact 4x4 projection matrix layout used by `tr_main.c`.

That is the exact projection builder `R_SetupProjection`.

### `sub_44BF90`: `R_SetupFrustum`

Observed local facts:

1. The helper computes the horizontal and vertical frustum normals from
   `fovX`, `fovY`, `sin`, and `cos`.
2. It stores the four frustum plane normals and then sets plane type, dist, and
   signbits for each plane.

That is the exact frustum setup helper `R_SetupFrustum`.

## Exact Portal, Mirror, And Drawsurf Helpers

### `sub_44C210`: `R_MirrorPoint`

Observed local facts:

1. The helper subtracts the surface origin from the input point.
2. It projects that local point onto the three surface axes and rebuilds it in
   the camera basis.
3. It adds the camera origin to the transformed result.

That is the exact mirror-point helper `R_MirrorPoint`.

### `sub_44C330`: `R_MirrorVector`

Observed local facts:

1. The helper zeroes the output vector.
2. It projects the input vector onto the three surface axes and accumulates the
   result in the camera basis without adding origin.

That is the exact mirror-vector helper `R_MirrorVector`.

### `sub_44C410`: `R_PlaneForSurface`

Observed local facts:

1. The helper handles null surfaces by zeroing the plane and forcing
   `normal[0] = 1`.
2. It copies the stored plane for face surfaces.
3. It reconstructs planes from indexed vertices for triangle and poly surfaces.

That is the exact plane extraction helper `R_PlaneForSurface`.

### `sub_44C4F0`: `R_GetPortalOrientations`

Observed local facts:

1. The helper starts by calling `R_PlaneForSurface` on `drawSurf->surface`.
2. For non-world entities it rotates the portal plane through
   `R_RotateForEntity` and `R_LocalNormalToWorld`.
3. It scans `tr.refdef.entities` for `RT_PORTALSURFACE`, distinguishes mirror
   entities from camera portals, optionally applies the rotate/bob paths, and
   returns the mirror flag through the output boolean.

That is the exact portal-orientation resolver `R_GetPortalOrientations`.

### `sub_44C990`: `IsMirror`

Observed local facts:

1. The helper repeats the portal-plane setup and optional entity rotation logic
   from `R_GetPortalOrientations`.
2. It scans for the closest `RT_PORTALSURFACE`.
3. It returns true only when the matched portal entity has identical `origin`
   and `oldorigin`, which is the exact mirror test used by the source.

That is the exact mirror classification helper `IsMirror`.

### `sub_44D1D0`: `SurfIsOffscreen`

Observed local facts:

1. The helper early-outs on the SMP-active path.
2. It calls `R_RotateForViewer`, decomposes the drawsurf sort, begins the
   surface, generates tessellation, and transforms each tess vertex through the
   clip-space helper.
3. It performs the exact trivial-reject, backface, portal-range, and mirror
   checks from `tr_main.c`.

That is the exact portal visibility helper `SurfIsOffscreen`.

### `sub_44D440`: `R_MirrorViewBySurface`

Observed local facts:

1. The helper rejects recursive portal views and the `r_noportals` /
   `r_fastsky` disable paths.
2. It calls the exact offscreen rejection helper and the exact portal
   orientation resolver.
3. It mirrors the old view origin and axes through `R_MirrorPoint` and
   `R_MirrorVector`, renders the mirrored view, and restores the old view parms.

That is the exact mirror-view helper `R_MirrorViewBySurface`.

### `sub_44CB00`: `R_SpriteFogNum`

Observed local facts:

1. The helper returns zero when `RDF_NOWORLDMODEL` is active.
2. It scans fog volumes starting at index `1`.
3. It tests sprite origin plus/minus radius against fog bounds and returns the
   first matching fog index.

That is the exact sprite fog classifier `R_SpriteFogNum`.

### `sub_44CBA0`: `shortsort`

Observed local facts:

1. The helper performs the short insertion-style drawsurf sort used under the
   cutoff threshold.
2. It swaps the packed `(sort, surface)` drawsurf pairs exactly as the source
   macro does.

That is the exact fallback sort helper `shortsort`.

### `sub_44CBE0`: `qsortFast`

Observed local facts:

1. The helper implements the non-recursive quicksort with explicit lo/hi
   stacks.
2. It falls back to `shortsort` under the small-array cutoff.
3. It sorts on the packed drawsurf `sort` field exactly as the source does.

That is the exact drawsurf sorter `qsortFast`.

### `sub_44CD40`: `R_AddDrawSurf`

Observed local facts:

1. The helper masks `tr.refdef.numDrawSurfs` into the drawsurf ring.
2. It packs shader index, shifted entity number, fog index, and dlight map into
   the drawsurf sort word.
3. It stores the surface pointer and increments the drawsurf count.

That is the exact drawsurf enqueue helper `R_AddDrawSurf`.

### `sub_44CD90`: `R_DecomposeSort`

Observed local facts:

1. The helper unpacks fog number, shader index, entity number, and dlight bits
   from the drawsurf sort word.
2. The bit shifts and masks match the local renderer constants exactly.

That is the exact drawsurf unpack helper `R_DecomposeSort`.

### `sub_44CDE0`: `R_AddEntitySurfaces`

Observed local facts:

1. The helper checks the draw-entities CVar, iterates
   `tr.refdef.entities`, zeros `needDlights`, and preshifts the current entity
   number.
2. It applies the first-person portal skip and then dispatches on `reType` and
   model type exactly as the source does.
3. It carries the exact fatal string:
   - `R_AddEntitySurfaces: Bad reType`

That is the exact entity-surface enqueue pass `R_AddEntitySurfaces`.

### `sub_44D610`: `R_SortDrawSurfs`

Observed local facts:

1. The helper handles the empty drawsurf case by immediately adding the draw
   command.
2. It clamps the drawsurf count to the maximum, calls `qsortFast`, and then
   iterates drawsurfs while unpacking sort keys.
3. It carries the exact `Shader '%s'with sort == SS_BAD` error path and invokes
   the exact mirror-view helper before finally emitting the draw command.

That is the exact drawsurf sort-and-portal pass `R_SortDrawSurfs`.

### `sub_44CFF0`: `R_DebugPolygon`

Observed local facts:

1. The helper sets the depth-mask and additive blend state, draws a filled
   polygon, then switches to line mode.
2. It clamps depth range to `0,0` for the wireframe overlay, restores it to
   `0,1`, and emits the same immediate-mode polygon loop used by the source.

That is the exact debug polygon callback `R_DebugPolygon`.

### `sub_44D700`: `R_RenderView`

Observed local facts:

1. The helper rejects zero-sized viewports, copies the incoming view parms into
   the global renderer state, and bumps the view counter.
2. It performs the exact renderer front-end spine:
   `R_RotateForViewer`, `R_SetupFrustum`, world/polygon surface generation,
   `R_SetupProjection`, `R_AddEntitySurfaces`, and `R_SortDrawSurfs`.
3. It also retains the exact debug-surface callback path through
   `R_DebugPolygon`.

That is the exact render-view entry point `R_RenderView`.

In this retail build, `R_GenerateDrawSurfs` and `R_DebugGraphics` do not appear
to survive as separate `functions.csv` starts; their behavior is structurally
embedded inside `R_RenderView`.

## Promoted Aliases

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_44A490` (`0x0044A490`) | `R_TransformDlights` | Observed | Exact dlight origin transform helper. |
| `sub_44A720` (`0x0044A720`) | `R_DlightBmodel` | Observed | Exact bmodel dynamic-light mask helper. |
| `sub_44ABE0` (`0x0044ABE0`) | `LogLight` | Observed | Exact first-person light debug logger. |
| `sub_44B1E0` (`0x0044B1E0`) | `R_CullLocalBox` | Observed | Exact local-box frustum cull helper. |
| `sub_44B4E0` (`0x0044B4E0`) | `R_CullPointAndRadius` | Observed | Exact point-sphere frustum cull helper. |
| `sub_44B570` (`0x0044B570`) | `R_LocalNormalToWorld` | Observed | Exact local-normal transform helper. |
| `sub_44B5E0` (`0x0044B5E0`) | `R_LocalPointToWorld` | Observed | Exact local-point transform helper. |
| `sub_44B660` (`0x0044B660`) | `R_TransformModelToClip` | Observed | Exact model-to-clip vec4 transform helper. |
| `sub_44B760` (`0x0044B760`) | `myGlMultMatrix` | Observed | Exact 4x4 matrix multiply helper. |
| `sub_44B810` (`0x0044B810`) | `R_RotateForEntity` | Observed | Exact entity orientation builder. |
| `sub_44B9E0` (`0x0044B9E0`) | `R_RotateForViewer` | Observed | Exact viewer orientation builder. |
| `sub_44BB50` (`0x0044BB50`) | `SetFarClip` | Observed | Exact far-clip computation helper. |
| `sub_44BE00` (`0x0044BE00`) | `R_SetupProjection` | Observed | Exact projection-matrix setup helper. |
| `sub_44BF90` (`0x0044BF90`) | `R_SetupFrustum` | Observed | Exact frustum-plane setup helper. |
| `sub_44C210` (`0x0044C210`) | `R_MirrorPoint` | Observed | Exact mirror-point helper. |
| `sub_44C330` (`0x0044C330`) | `R_MirrorVector` | Observed | Exact mirror-vector helper. |
| `sub_44C410` (`0x0044C410`) | `R_PlaneForSurface` | Observed | Exact drawsurf plane extraction helper. |
| `sub_44C4F0` (`0x0044C4F0`) | `R_GetPortalOrientations` | Observed | Exact portal orientation resolver. |
| `sub_44C990` (`0x0044C990`) | `IsMirror` | Observed | Exact mirror portal classifier. |
| `sub_44CB00` (`0x0044CB00`) | `R_SpriteFogNum` | Observed | Exact sprite fog lookup helper. |
| `sub_44CBA0` (`0x0044CBA0`) | `shortsort` | Observed | Exact small-array drawsurf sort helper. |
| `sub_44CBE0` (`0x0044CBE0`) | `qsortFast` | Observed | Exact non-recursive drawsurf quicksort. |
| `sub_44CD40` (`0x0044CD40`) | `R_AddDrawSurf` | Observed | Exact drawsurf enqueue helper. |
| `sub_44CD90` (`0x0044CD90`) | `R_DecomposeSort` | Observed | Exact drawsurf unpack helper. |
| `sub_44CDE0` (`0x0044CDE0`) | `R_AddEntitySurfaces` | Observed | Exact entity surface enqueue pass. |
| `sub_44CFF0` (`0x0044CFF0`) | `R_DebugPolygon` | Observed | Exact debug polygon callback. |
| `sub_44D1A0` (`0x0044D1A0`) | `R_CullLocalPointAndRadius` | Observed | Exact local-space sphere-cull wrapper. |
| `sub_44D1D0` (`0x0044D1D0`) | `SurfIsOffscreen` | Observed | Exact offscreen portal rejection helper. |
| `sub_44D440` (`0x0044D440`) | `R_MirrorViewBySurface` | Observed | Exact mirror-view render helper. |
| `sub_44D610` (`0x0044D610`) | `R_SortDrawSurfs` | Observed | Exact drawsurf sort-and-portal pass. |
| `sub_44D700` (`0x0044D700`) | `R_RenderView` | Observed | Exact front-end render-view entry point. |

## Coverage Impact

On the committed `quakelive_steam.exe` Ghidra baseline of `5473` functions, this
pass moves the explicit address-backed `quakelive_steam` alias set from `442` to
`473` functions, which is approximately `8.1%` to `8.6%` host-symbol coverage.

The raw alias table moves from `443` to `474` entries.

For the focused renderer band `0x44A000-0x44D800`, the remaining true
`functions.csv` gaps drop from `33` to `2`. The only unresolved standalone
entries left in that band are:

- `0x0044B130`
- `0x0044D0D0`

The narrower lighting-plus-main band closures are:

- `0x44A000-0x44B100`: `3 -> 0`
- `0x44B100-0x44D000`: `24 -> 1`
- `0x44D000-0x44D800`: `6 -> 1`

## Open Questions

1. `0x0044B130` remains unmatched. It is clearly another small cull-oriented
   helper but does not yet tie down to a stable retail source name.
2. `0x0044D0D0` is still unresolved. It appears to be a Quake Live-specific
   overlay or debug draw helper that sits on the `R_RenderView` tail path.
3. `R_WorldToLocal`, `R_TransformClipToWindow`, `R_GenerateDrawSurfs`, and
   `R_DebugGraphics` do not currently appear as distinct `functions.csv`
   entries in this retail build; at least some of that behavior appears to be
   inlined into adjacent helpers.
