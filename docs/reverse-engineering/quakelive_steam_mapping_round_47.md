# Quake Live Steam Host Mapping Round 47

## Scope

This round closes the main `tr_shade.c` shading and stage-iterator spine that
starts immediately after the scene-registration tranche.

The newly promoted slice covers:

- animated image binding and debug triangle/normal draws
- surface begin/setup and multitexture submission
- dynamic-light and fog overlay passes
- per-stage color and texcoord generation
- the generic, vertex-lit, and lightmapped stage iterators
- the surface-end dispatch path

The primary evidence for this round is:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `src/code/renderer/tr_shade.c`

## Exact Image-Bind And Debug Helpers

### `sub_451830`: `R_BindAnimatedImage`

Observed local facts:

1. The helper first checks the video-map flag and calls the cinematic run and
   upload imports on the stored handle.
2. It falls back to binding `image[0]` when the animation count is `<= 1`.
3. Otherwise it computes the exact animation frame index from
   `shaderTime * imageAnimationSpeed * FUNCTABLE_SIZE`, right-shifts by
   `FUNCTABLE_SIZE2`, clamps negative values, mods by the animation count, and
   binds that image.

That is the exact animated-image bind helper `R_BindAnimatedImage`.

### `sub_4518B0`: `DrawTris`

Observed local facts:

1. The helper binds the renderer white image and sets the draw color to white.
2. It applies the exact wireframe depth-range setup used for triangle-outline
   debugging.
3. It disables color and texcoord arrays, points the vertex array at the padded
   XYZ buffer, optionally locks arrays, calls the draw-elements helper, unlocks
   arrays, and restores the depth range.

That is the exact debug helper `DrawTris`.

### `sub_451990`: `DrawNormals`

Observed local facts:

1. The helper binds the white image, sets the depth range to `0,0`, and draws
   GL lines.
2. For each vertex it emits the source position and then emits a second point
   at `xyz + 2 * normal`.
3. It finishes by restoring the depth range to `0,1`.

That is the exact debug helper `DrawNormals`.

## Exact Surface And Pass Helpers

### `sub_451A80`: `RB_BeginSurface`

Observed local facts:

1. The helper resolves `shader->remappedShader` when present.
2. It zeroes tess index, vertex, and dlight counters and stores the resolved
   shader, fog number, stage pointer array, pass count, and iterator callback.
3. It computes `shaderTime` from the renderer float time minus `shader->timeOffset`
   and clamps to `shader->clampTime` when needed.

That is the exact setup helper `RB_BeginSurface`.

### `sub_451B20`: `DrawMultitextured`

Observed local facts:

1. The helper fetches the requested stage from the current `xstages` table.
2. It sets stage state, handles the portal polygon-mode workaround, selects
   texture units `0` and `1`, points both texcoord arrays, and binds both
   stage bundles through `R_BindAnimatedImage`.
3. It chooses the lightmap texture environment exactly like the source and
   then draws the indexed batch before disabling texturing on texture unit `1`.

That is the exact multitexture submission helper `DrawMultitextured`.

### `sub_451C10`: `ProjectDlightTexture`

Observed local facts:

1. The helper iterates the current dynamic-light list and skips lights whose
   bit is not set in the current tess dlight mask.
2. It computes projected texcoords and per-vertex modulated colors into local
   arrays, tracking clip bits for each vertex.
3. It rebuilds a hit-index list for triangles whose three vertices are not all
   clipped out, binds the dlight image, selects additive vs non-additive state,
   draws the surviving triangles, and updates the dlight index counters.

That is the exact dynamic-light pass helper `ProjectDlightTexture`.

### `sub_452020`: `RB_FogPass`

Observed local facts:

1. The helper enables color and texcoord arrays and points them at the staging
   color and texcoord buffers.
2. It fills every staged vertex color with the current fog volume's packed
   fog color.
3. It calls the fog texcoord calculator, binds the fog image, selects the
   `FP_EQUAL` vs normal fog blend state, and draws the indexed batch.

That is the exact fog overlay helper `RB_FogPass`.

## Exact Per-Stage Generation Helpers

### `sub_4521F0`: `ComputeColors`

Observed local facts:

1. The helper switches on the stage `rgbGen` field and covers the exact source
   cases for identity, identity-lighting, diffuse lighting, exact vertex,
   const, vertex, one-minus-vertex, fog, waveform, entity, and
   one-minus-entity color generation.
2. It then switches on `alphaGen` and covers the exact source-side alpha cases,
   including identity, const, waveform, lighting specular, entity,
   one-minus-entity, vertex, one-minus-vertex, and portal alpha.
3. It finally checks the current fog number and applies the exact
   `adjustColorsForFog` switch with RGB, alpha, and RGBA modulation helpers.

That is the exact per-stage color builder `ComputeColors`.

### `sub_452830`: `ComputeTexCoords`

Observed local facts:

1. The helper iterates the two texture bundles for the stage.
2. For each bundle it switches on the exact `tcGen` family used by the source:
   identity, texture, lightmap, vector, fog, environment-mapped, and bad.
3. It then iterates `numTexMods` and dispatches the exact texmod family used by
   the source: none, turbulent, entity-translate, scroll, scale, stretch,
   transform, and rotate, with the same fatal error path for unknown texmods.

That is the exact texcoord-generation helper `ComputeTexCoords`.

## Exact Iterator And Surface-End Helpers

### `sub_452A60`: `RB_IterateStagesGeneric`

Observed local facts:

1. The helper walks the current stage table until a null stage pointer is hit.
2. For each stage it calls the newly closed `ComputeColors` and
   `ComputeTexCoords`.
3. It conditionally re-enables the staged arrays, chooses between
   `DrawMultitextured` and the single-texture draw path, and honors the
   lightmap-only early-out condition.

That is the exact generic stage loop `RB_IterateStagesGeneric`.

### `sub_452B90`: `RB_StageIteratorGeneric`

Observed local facts:

1. The helper logs the exact generic iterator banner, sets face culling, and
   applies polygon offset when required.
2. It chooses the exact `setArraysOnce` path based on pass count and
   multitexture state, locks the vertex array, and then calls
   `RB_IterateStagesGeneric`.
3. It conditionally runs `ProjectDlightTexture`, conditionally runs
   `RB_FogPass`, unlocks arrays, and disables polygon offset when it had been
   enabled.

That is the exact generic stage iterator `RB_StageIteratorGeneric`.

### `sub_452D80`: `RB_StageIteratorVertexLitTexture`

Observed local facts:

1. The helper begins by computing diffuse vertex colors into the staged color
   buffer.
2. It logs the exact vertex-lit iterator banner, sets culling, enables the
   color and texcoord arrays, locks the vertex array, binds the first bundle,
   sets stage state, and draws the indexed batch.
3. It then runs the same conditional dlight pass, fog pass, and array unlock
   sequence as the source.

That is the exact iterator `RB_StageIteratorVertexLitTexture`.

### `sub_452F10`: `RB_StageIteratorLightmappedMultitexture`

Observed local facts:

1. The helper logs the exact lightmapped-multitexture iterator banner and sets
   face culling.
2. It applies `GLS_DEFAULT`, sets the vertex pointer, enables the constant
   color path, configures texture unit `0` for the base bundle and texture unit
   `1` for the lightmap bundle, with the exact lightmap-vs-modulate texenv
   branch.
3. It locks arrays, draws the indexed batch, disables texture unit `1`, and
   then performs the same conditional dlight, fog, and unlock sequence.

That is the exact iterator `RB_StageIteratorLightmappedMultitexture`.

### `sub_4530E0`: `RB_EndSurface`

Observed local facts:

1. The helper early-outs when the tess index count is zero.
2. It emits the exact `SHADER_MAX_INDEXES` and `SHADER_MAX_VERTEXES` fatal
   checks, handles the shadow-shader special case, and honors the debug-sort
   cutoff.
3. It updates the backend shader/index/vertex counters, dispatches through the
   stored current stage-iterator callback, runs the `DrawTris` and
   `DrawNormals` debug paths when enabled, zeroes the tess index count, and
   logs the trailing separator.

That is the exact surface-finalization helper `RB_EndSurface`.

## Open Follow-Up

This pass intentionally stops before the deformation helpers that begin at
`0x00453210`. The HLIL there clearly belongs to the tess deformation pipeline,
but the exact retail source names need a dedicated pass to avoid speculative
promotions.
