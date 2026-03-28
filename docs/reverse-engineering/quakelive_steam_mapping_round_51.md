# Quake Live Steam Host Mapping Round 51

## Scope

This round closes the next renderer tranche after the shader/shadow work by
mapping the skybox/cloud pipeline in `tr_sky.c` and the early backend surface
helpers in `tr_surface.c`.

The newly promoted slice covers:

- sky polygon clipping and projection to box faces
- skybox drawing, cloud vertex generation, and the sky stage iterator
- backend quad stamps, sun rendering, and primitive surface builders
- beam, rail, mesh, face, and grid tessellation helpers

The primary evidence for this round is:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `src/code/renderer/tr_sky.c`
- `src/code/renderer/tr_surface.c`

## Sky Pipeline Closures

### `sub_459A60`: `AddSkyPolygon`

Observed local facts:

1. The helper sums the polygon vertices, picks one of six sky axes from the
   dominant absolute component, and uses the exact signed `vec_to_st` mapping.
2. It projects each vertex by dividing the selected `s`/`t` components by the
   chosen depth component and skips near-zero divisors at `0.001`.
3. It updates the per-face `sky_mins` and `sky_maxs` bounds exactly as in the
   GPL source.

That is exactly `AddSkyPolygon`.

### `sub_459D00`: `ClipSkyPolygon`

The helper enforces the exact `MAX_CLIP_VERTS` bound, clips against the six
`sky_clip` planes with `ON_EPSILON == 0.1`, and forwards fully clipped polys to
`AddSkyPolygon`. That is the recursive sky clipper `ClipSkyPolygon`.

### `sub_45A150`: `ClearSkyBox`

The helper resets the six `sky_mins` entries to `9999` and the six `sky_maxs`
entries to `-9999`. That is exactly `ClearSkyBox`.

### `sub_45A1F0`: `RB_ClipSkyPolygons`

The helper calls `ClearSkyBox`, walks the tess indexes in triples, subtracts
`backEnd.viewParms.or.origin` from each triangle vertex, and feeds the result
to `ClipSkyPolygon( 3, ..., 0 )`. That is exactly `RB_ClipSkyPolygons`.

### `sub_45A300`: `MakeSkyVec`

Observed local facts:

1. The helper uses the exact six-entry `st_to_vec` table from `tr_sky.c`.
2. It computes `boxSize = backEnd.viewParms.zFar / 1.75`, fills `outXYZ`, then
   remaps and clamps `s`/`t` between `sky_min` and `sky_max`.
3. When an output ST pointer is present, it writes the final clamped
   `(s, 1 - t)` pair.

That is exactly `MakeSkyVec`.

### `sub_45A460`: `DrawSkySide`

The helper binds one skybox image and emits `GL_TRIANGLE_STRIP` rows across the
requested subdivision rectangle using `s_skyTexCoords` and `s_skyPoints`. That
is exactly `DrawSkySide`.

### `sub_45A530`: `DrawSkyBox`

Observed local facts:

1. The helper zeroes the sky texcoord buffer, snaps `sky_mins`/`sky_maxs` to
   `HALF_SKY_SUBDIVISIONS`, clamps them to `[-4, 4]`, and skips empty faces.
2. It calls `MakeSkyVec` for each subdivision point on every visible face.
3. It renders each face via `DrawSkySide` using the exact `sky_texorder`
   indirection into `shader->sky.outerbox`.

That is exactly `DrawSkyBox`.

### `sub_45A7B0`: `FillCloudySkySide`

The helper appends the current side's cloud vertices into `tess`, adds the
view-origin offset, copies sky texcoords, and conditionally generates the first
pass's triangle indexes. That is exactly `FillCloudySkySide`.

### `sub_45A9D0`: `R_BuildCloudData`

Observed local facts:

1. The helper sets `sky_min = 1/256`, `sky_max = 255/256`, and clears the tess
   vertex/index counts.
2. It checks `input->shader->sky.cloudHeight` and then iterates the active
   shader stages.
3. Inside that loop it executes the exact `FillCloudBox` logic inline:
   per-face subdivision bounds, `MakeSkyVec` reconstruction, cloud texcoord
   fetches, and `FillCloudySkySide` submission.

This code entity corresponds to `R_BuildCloudData`, with `FillCloudBox`
compiler-folded into it rather than emitted as a standalone function.

### `sub_45AD30`: `R_InitSkyTexCoords`

The helper seeds `zFar = 1024`, iterates all `6 x 9 x 9` sky samples, calls
`MakeSkyVec`, computes the exact cloud-layer intersection scalar `p`, stores it
to `s_cloudTexP`, normalizes the intersection vector, and writes the two
`Q_acos`-derived cloud texture angles. That is exactly `R_InitSkyTexCoords`.

### `sub_45AF00`: `RB_StageIteratorSky`

Observed local facts:

1. The helper early-outs on `r_fastsky`, calls `RB_ClipSkyPolygons`, and sets
   the depth range based on `r_showsky`.
2. It conditionally draws the outer skybox via `DrawSkyBox`.
3. It calls `R_BuildCloudData`, then `RB_StageIteratorGeneric`, restores the
   normal depth range, and marks `backEnd.skyRenderedThisView = qtrue`.

That is exactly `RB_StageIteratorSky`. HLIL shows it as a real helper even
though it is not listed as a standalone `functions.csv` start.

## Surface Helper Closures

### `sub_45B000`: `RB_CheckOverflow`

The helper checks `tess.numVertexes + verts` and `tess.numIndexes + indexes`
against the exact `SHADER_MAX_*` limits, flushes with `RB_EndSurface`, prints
the exact overflow diagnostics, and restarts with `RB_BeginSurface`. That is
exactly `RB_CheckOverflow`.

### `sub_45B090`: `RB_AddQuadStampExt`

Observed local facts:

1. The helper reserves `4` verts and `6` indexes, writes the exact quad index
   order, and builds the four quad corners from `origin +/- left +/- up`.
2. It fills a constant normal from `-backEnd.viewParms.or.axis[0]`.
3. It assigns the provided `(s1,t1,s2,t2)` texcoords and splats the same color
   to all four vertices.

That is exactly `RB_AddQuadStampExt`.

### `sub_45B320`: `RB_AddQuadStamp`

The helper is just the fixed-coord wrapper around `RB_AddQuadStampExt` with
`0, 0, 1, 1`. That is exactly `RB_AddQuadStamp`.

### `sub_45B360`: `RB_DrawSun`

The helper checks `backEnd.skyRenderedThisView` and `r_drawSun`, derives the
sun quad basis from `tr.sunDirection`, pushes the far depth range, submits a
sun quad, and restores the normal depth range. That is exactly `RB_DrawSun`.

### `sub_45B510`: `RB_SurfacePolychain`

The helper emits the exact debug string `--- RB_SurfacePolychain ---`, copies
the polychain verts/modulate colors into tess, and triangulates the fan by
anchoring every triangle at the first new vertex. That is exactly
`RB_SurfacePolychain`.

### `sub_45B640`: `RB_SurfaceTriangles`

The helper emits `--- RB_SurfaceTriangles ---`, ORs the surface dlight bits,
copies the triangle indexes with the tess vertex base applied, and then copies
the draw verts into tess including normals, texcoords, colors, and per-vertex
dlight bits. That is exactly `RB_SurfaceTriangles`.

### `sub_45B800`: `RB_SurfaceBeam`

The helper builds the six-segment beam ring around the entity direction,
selects the white image, sets additive blend state, and renders the exact
triangle strip beam. That is exactly `RB_SurfaceBeam`.

### `sub_45B9E0`: `DoRailCore`

The helper constructs the four rail-core corners from `start`, `end`, `up`,
`len`, and `spanWidth`, writes the expected texture coordinates, applies the
entity shader colors, and emits the six quad indexes. That is exactly the
static helper `DoRailCore`.

### `sub_45BDF0`: `DoRailDiscs`

Observed local facts:

1. The helper computes the four disc offsets from `cos/sin(45 + i * 90)` and
   `r_railWidth`.
2. It optionally advances the initial ring by one segment for long rails.
3. It appends one quad per segment, updates the ring positions, and writes the
   exact six indexes per disc.

That is exactly `DoRailDiscs`.

### `sub_45C310`: `RB_SurfaceRailRings`

The helper derives the rail direction from `oldorigin -> origin`, computes the
segment count from `r_railSegmentLength`, builds orthogonal basis vectors, and
calls `DoRailDiscs`. That is exactly `RB_SurfaceRailRings`.

### `sub_45C3F0`: `RB_SurfaceRailCore`

The helper computes the view-dependent right vector from the two view rays to
the rail endpoints and then calls `DoRailCore` with `r_railCoreWidth`. That is
exactly `RB_SurfaceRailCore`.

### `sub_45C540`: `RB_SurfaceLightningBolt`

The helper repeats the rail-core submission four times, rotating the right
vector by `45` degrees on each pass. That is exactly `RB_SurfaceLightningBolt`.

### `sub_45C6D0`: `VectorArrayNormalize`

The helper walks a vec4 normal array and normalizes the first three components
of each element in place. That is exactly `VectorArrayNormalize`.

### `sub_45C740`: `LerpMeshVertexes`

Observed local facts:

1. The helper reads the MD3 xyz/normal blocks for the current frame and, when
   needed, the old frame.
2. It has the exact fast path for `backlerp == 0` and the interpolation path
   for mixed frames.
3. It decodes MD3 lat/long normals through `tr.sinTable` and calls
   `VectorArrayNormalize` after interpolating normals.

That is exactly `LerpMeshVertexes`.

### `sub_45CCD0`: `RB_SurfaceMesh`

The helper computes `backlerp`, checks overflow against `numVerts` and
`numTriangles * 3`, calls `LerpMeshVertexes`, copies the triangle indexes, and
then copies the MD3 texture coordinates. That is exactly `RB_SurfaceMesh`.

### `sub_45CE40`: `RB_SurfaceFace`

The helper emits `--- RB_SurfaceFace ---`, copies the face indexes in reverse
order into tess, propagates the surface plane normal when needed, and copies
the packed face points/lightmap/color data into tess. That is exactly
`RB_SurfaceFace`.

### `sub_45D030`: `LodErrorForVolume`

The helper transforms a local point into world space through `backEnd.or`,
projects it onto the view forward axis, applies the radius clamp rules, and
returns `r_lodCurveError->value / d`. That is exactly `LodErrorForVolume`.

### `sub_45D160`: `RB_SurfaceGrid`

The helper computes the allowable LOD error via `LodErrorForVolume`, builds the
width/height index tables, chunks the grid into tess-sized strips, copies the
chosen draw verts into tess, and emits the exact two-triangle grid cells. That
is exactly `RB_SurfaceGrid`.

## Extra HLIL-Only Helpers

The following helpers also promote cleanly from HLIL even though they are not
standalone `functions.csv` starts in the committed Ghidra export:

- `0x0045D640 -> RB_SurfaceAxis`
- `0x0045D760 -> RB_SurfaceEntity`
- `0x0045D7B0 -> RB_SurfaceBad`

### `sub_45D7D0`: `RB_SurfaceDisplayList`

The helper is a one-call wrapper around `qglCallList( surf->listNum )`. That is
exactly `RB_SurfaceDisplayList`.

## Open Follow-Up

After this round, the next unresolved standalone starts in the same general
area are `0x004589D0` from the shader-registration block and `0x0045D7F0`
immediately after the surface-display-list helpers.
