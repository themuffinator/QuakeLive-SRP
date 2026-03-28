# Quake Live Steam Host Mapping Round 48

## Scope

This round closes most of the remaining `tr_shade_calc.c` host block and one
adjacent deformation helper from `tr_shadows.c`.

The newly promoted slice covers:

- the full tessellation deformation dispatch path
- text, autosprite, and autosprite2 deformation helpers
- entity-color, wave, fog, and lighting color generators
- fog, environment, turbulent, scale, scroll, transform, rotate, and stretch
  texcoord generators
- the projection-shadow deformation path

The primary evidence for this round is:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `src/code/renderer/tr_shade_calc.c`
- `src/code/renderer/tr_shadows.c`

## Deformation Pipeline

### `sub_453210`: `RB_CalcDeformNormals`

Observed local facts:

1. The helper calls `R_NoiseGet4f` three times per vertex with the exact
   `0`, `100`, and `200` X offsets used by the GPL code.
2. Each noise sample is scaled by `ds->deformationWave.amplitude` and added to
   one normal component.
3. The loop ends with `VectorNormalizeFast( normal )`.

That is the exact wavy-normal helper `RB_CalcDeformNormals`.

### `sub_4533D0`: `RB_CalcBulgeVertexes`

Observed local facts:

1. The helper computes `now = refdef.time * bulgeSpeed * 0.001`.
2. It derives the sine-table index from `st[0] * bulgeWidth + now`.
3. The resulting scale is multiplied by `bulgeHeight` and applied along the
   current normal.

That is the exact bulge deformation helper `RB_CalcBulgeVertexes`.

### `sub_453480`: `DeformText`

Observed local facts:

1. The helper builds a text basis from the first quad, computes top/bottom Z,
   and re-centers the origin exactly like the GPL routine.
2. It clears `tess.numIndexes` and `tess.numVertexes` before rebuilding the
   geometry.
3. It iterates the input string, skips spaces, derives `row` and `col` from the
   character, uses `0.0625f` cell sizes, and emits quads through
   `RB_AddQuadStampExt`.

That is the exact text deformation routine `DeformText`.

### `sub_453790`: `GlobalVectorToLocal`

Observed local facts:

1. The helper is only three dot products.
2. Each output component is the dot of the input vector with one
   `backEnd.or.axis` row.

That is the exact basis-conversion helper `GlobalVectorToLocal`.

### `sub_453800`: `AutospriteDeform`

Observed local facts:

1. The function emits the exact warning strings for odd vertex and index counts.
2. It selects either world axes or `GlobalVectorToLocal` depending on whether
   the current entity is the world.
3. For each 4-vertex quad it computes the midpoint, derives a radius from the
   first-corner delta times `0.707`, applies mirror and non-normalized-axis
   corrections, and calls `RB_AddQuadStamp`.

That is the exact forward-facing sprite deform helper `AutospriteDeform`.

### `sub_453A80`: `Autosprite2Deform`

Observed local facts:

1. The helper emits the exact `Autosprite2` odd-count warnings.
2. It derives the forward vector from the current view axis, again converting to
   local space for non-world entities.
3. It scans the six quad edges, tracks the two shortest edges, computes their
   midpoints, derives the major and minor axes, and reprojects both edge pairs.

That is the exact rectangular pivoting helper `Autosprite2Deform`.

### `sub_454C80`: `RB_CalcDeformVertexes`

Observed local facts:

1. The first branch handles the zero-frequency case by evaluating the wave once
   and applying `normal * scale` to every vertex.
2. The second branch selects the waveform table, computes
   `(xyz[0] + xyz[1] + xyz[2]) * deformationSpread`, and folds that into the
   wave phase.
3. Both paths add the scaled normal offset into `tess.xyz`.

That is the exact wave deformation helper `RB_CalcDeformVertexes`.

### `sub_454E30`: `RB_CalcMoveVertexes`

Observed local facts:

1. The helper evaluates the deformation wave exactly once.
2. It scales `ds->moveVector` by that value.
3. It adds the same offset to every vertex in `tess.xyz`.

That is the exact move deformation helper `RB_CalcMoveVertexes`.

### `sub_454F40`: `RB_DeformTessGeometry`

Observed local facts:

1. The function loops over `shader->numDeforms`.
2. Its switch dispatches to the exact deformation helpers promoted above:
   `RB_CalcDeformVertexes`, `RB_CalcDeformNormals`,
   `RB_CalcBulgeVertexes`, `RB_CalcMoveVertexes`,
   `AutospriteDeform`, `Autosprite2Deform`, and `DeformText`.
3. The remaining switch arm targets `sub_4598E0`, which matches the projection
   shadow deform in `tr_shadows.c`.

That is the exact deformation dispatcher `RB_DeformTessGeometry`.

### `sub_4598E0`: `RB_ProjectionShadowDeform`

Observed local facts:

1. The helper builds the ground vector from the renderer orientation Z axis.
2. It computes `groundDist` from the entity shadow plane and current origin.
3. It adjusts the light direction when the ground dot is below `0.5`, inverts by
   that dot, and projects every tess vertex along that light vector by `h`.

That is the exact projection-shadow helper `RB_ProjectionShadowDeform`.

## Color And Fog Helpers

### `sub_4540F0`: `RB_CalcColorFromEntity`

The helper copies the packed `shaderRGBA` dword from `backEnd.currentEntity`
into every destination color slot. That is exactly `RB_CalcColorFromEntity`.

### `sub_454120`: `RB_CalcColorFromOneMinusEntity`

The helper inverts each byte of `shaderRGBA`, packs the result, and fills the
destination array with that dword. That is exactly
`RB_CalcColorFromOneMinusEntity`.

### `sub_454170`: `RB_CalcAlphaFromEntity`

The helper advances to the alpha byte of each destination color and writes
`shaderRGBA[3]`. That is exactly `RB_CalcAlphaFromEntity`.

### `sub_4541B0`: `RB_CalcAlphaFromOneMinusEntity`

The helper writes `0xff - shaderRGBA[3]` into the alpha byte of each vertex.
That is exactly `RB_CalcAlphaFromOneMinusEntity`.

### `sub_455020`: `RB_CalcWaveColor`

Observed local facts:

1. When `wf->func == GF_NOISE`, the helper calls `R_NoiseGet4f(0,0,0, ...)`
   with `(shaderTime + phase) * frequency`.
2. Otherwise it falls back to the merged waveform evaluator at `sub_454B70` and
   scales by `tr.identityLight`.
3. It clamps the glow to `[0, 1]`, converts to a `0..255` byte, packs
   `RGBA = v,v,v,255`, and fills the output array.

That is the exact wave-color helper `RB_CalcWaveColor`.

### `sub_4550F0`: `RB_CalcWaveAlpha`

The helper evaluates the wave, clamps it to `[0, 1]`, converts to a byte, and
writes only the alpha lane of each destination color. That is exactly
`RB_CalcWaveAlpha`.

### `sub_455160`: `RB_CalcModulateColorsByFog`

Observed local facts:

1. The function stack-allocates a large temporary texcoord array and first calls
   `sub_4541F0`, the promoted fog texcoord generator.
2. It calls the fog-factor helper for each generated `(s, t)` pair.
3. It multiplies the destination RGB lanes by `1 - fogFactor`, leaving alpha
   untouched.

That is the exact fog color modulator `RB_CalcModulateColorsByFog`.

### `sub_4552C0`: `RB_CalcModulateAlphasByFog`

The helper follows the same pattern but touches only the alpha byte of each
destination color. That is exactly `RB_CalcModulateAlphasByFog`.

### `sub_455390`: `RB_CalcModulateRGBAsByFog`

The helper again reuses generated fog texcoords and applies the same `1 - fog`
factor to all four color lanes. That is exactly `RB_CalcModulateRGBAsByFog`.

## Texcoord And Lighting Helpers

### `sub_4541F0`: `RB_CalcFogTexCoords`

Observed local facts:

1. The helper indexes the current fog from `tr.world->fogs + tess.fogNum`.
2. It builds the exact fog-distance and fog-depth vectors from the current
   model/view orientation and fog surface plane.
3. It handles the `eyeOutside` clipped-fog branch and writes one `(s, t)` pair
   per tess vertex.

That is the exact fog texcoord generator `RB_CalcFogTexCoords`.

### `sub_4544A0`: `RB_CalcEnvironmentTexCoords`

The loop subtracts `viewOrigin`, normalizes the viewer vector, reflects it
about the normal, and writes `s = 0.5 + reflected[1] * 0.5`,
`t = 0.5 - reflected[2] * 0.5`. That is exactly
`RB_CalcEnvironmentTexCoords`.

### `sub_4545C0`: `RB_CalcTurbulentTexCoords`

The helper computes `now = phase + shaderTime * frequency`, then adds sine-table
offsets based on `(xyz[0] + xyz[2])` and `xyz[1]` scaled by the exact
`1/128 * 0.125` constants. That is exactly `RB_CalcTurbulentTexCoords`.

### `sub_454680`: `RB_CalcScaleTexCoords`

The helper multiplies each texcoord pair by the two scale components. That is
exactly `RB_CalcScaleTexCoords`.

### `sub_4546C0`: `RB_CalcScrollTexCoords`

The helper multiplies the scroll speeds by `shaderTime`, clamps them with
`floor` so they do not grow unbounded, and adds the results to each texcoord
pair. That is exactly `RB_CalcScrollTexCoords`.

### `sub_454750`: `RB_CalcTransformTexCoords`

The loop applies the exact 2x2 matrix-plus-translate transform to each `(s, t)`
pair. That is exactly `RB_CalcTransformTexCoords`.

### `sub_4547B0`: `RB_CalcRotateTexCoords`

The helper computes the negative degree rate times `shaderTime`, looks up sine
and cosine from the function table, builds the centered rotation matrix, and
delegates to `sub_454750`. That is exactly `RB_CalcRotateTexCoords`.

### `sub_454850`: `myftol`

The helper is a direct float-to-int conversion wrapper returning the converted
temporary. That is the exact integer helper `myftol`.

### `sub_454870`: `RB_CalcSpecularAlpha`

Observed local facts:

1. The helper uses the fixed `lightOrigin` vector.
2. It normalizes the light and view directions per vertex, computes the
   reflected vector, and forms the specular dot product.
3. It squares the contribution twice, scales by `255`, clamps at `255`, and
   writes the result into the alpha lane.

That is the exact specular-alpha helper `RB_CalcSpecularAlpha`.

### `sub_454A30`: `RB_CalcDiffuseColor`

The helper loads `ambientLight`, `directedLight`, and `lightDir` from the
current entity, computes the incoming dot with each normal, falls back to the
packed ambient color for nonpositive light, and otherwise writes clamped RGB
plus `alpha = 255`. That is exactly `RB_CalcDiffuseColor`.

### `sub_454B70`: `EvalWaveForm`

Observed local facts:

1. The helper performs the exact `genFunc_t` switch that the GPL `TableForFunc`
   routine implements.
2. It then immediately computes `base + table[index] * amplitude` with the
   `phase + shaderTime * frequency` term folded into the table index.

That is the exact `EvalWaveForm` helper. The standalone `TableForFunc` routine
has been compiler-folded into this host function rather than preserved as a
separate start.

### `sub_454C20`: `RB_CalcStretchTexCoords`

The helper evaluates the wave once, computes its reciprocal, builds the centered
stretch transform with `0.5 - 0.5 * p` translations, and delegates to
`sub_454750`. That is exactly `RB_CalcStretchTexCoords`.

## Open Follow-Up

This pass closes the main `tr_shade_calc.c` slice, but the later unresolved
cluster starting at `0x00455540` is still outside this note and needs a separate
evidence pass.

`EvalWaveFormClamped` is also not promoted separately because the host compiler
inlined that logic directly into `RB_CalcWaveAlpha` rather than preserving a
standalone function start.
