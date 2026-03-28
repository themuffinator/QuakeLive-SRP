# Quake Live Steam Host Mapping Round 50

## Scope

This round closes the remaining shader-parser and stencil-shadow gaps around
the already-mapped shader-management spine in `tr_shader.c` and `tr_shadows.c`.

The newly promoted slice covers:

- top-level shader definition parsing and sort/surface/deform helpers
- stage-iterator selection and shader finalization support helpers
- the shadow-volume edge renderer and stencil darkening finish path

The primary evidence for this round is:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `src/code/renderer/tr_shader.c`
- `src/code/renderer/tr_shadows.c`

## Shader Parser Closures

### `sub_456BD0`: `ParseDeform`

Observed local facts:

1. The helper emits the exact `missing deform parm` warning and enforces the
   `MAX_SHADER_DEFORMS` limit.
2. It recognizes the exact deform keywords used by the GPL parser:
   `projectionShadow`, `autosprite`, `autosprite2`, `text`, `bulge`, `wave`,
   `normal`, and `move`.
3. The waveform-bearing branches call the already mapped `ParseWaveForm`.

That is the exact top-level deform parser `ParseDeform`.

### `sub_456EC0`: `ParseSkyParms`

Observed local facts:

1. The helper emits the exact `"'skyParms' missing parameter"` warnings.
2. It builds the exact `"%s_%s.tga"` outerbox and innerbox image paths for the
   six skybox sides.
3. It applies the GPL default cloud height of `512` and initializes the sky
   texcoord tables.

That is exactly `ParseSkyParms`.

### `sub_4570B0`: `ParseSort`

The helper matches the exact shader sort tokens `portal`, `sky`, `opaque`,
`decal`, `seeThrough`, `banner`, `additive`, `nearest`, and `underwater`,
falling back to `atof` for numeric sorts. That is exactly `ParseSort`.

### `sub_457220`: `ParseSurfaceParm`

The helper scans the surface-parameter table strings, matches the parsed token,
and ORs the corresponding surface/content flags into the working shader. That
is the exact `ParseSurfaceParm`.

### `sub_457280`: `ParseShader`

Observed local facts:

1. The helper enforces the top-level `{ ... }` shader body and emits the exact
   `no concluding '}' in shader` warning on failure.
2. It dispatches the exact top-level keywords handled by `ParseShader`,
   including `deformVertexes`, `surfaceParm`, `fogParms`, `portal`,
   `skyparms`, `cull`, `sort`, and nested stage blocks.
3. It calls the newly mapped helpers `ParseStage`, `ParseDeform`, `ParseSort`,
   `ParseSurfaceParm`, `ParseVector`, `ParseTexMod`, and `ParseWaveForm`.

That is the full top-level shader parser `ParseShader`.

## Shader Finalization Helpers

### `sub_457820`: `ComputeStageIteratorFunc`

The helper defaults to `RB_StageIteratorGeneric`, selects the sky iterator for
sky shaders, and otherwise switches to the exact vertex-lit or
lightmapped-multitexture fast paths when the current stage layout matches the
GPL predicates. That is exactly `ComputeStageIteratorFunc`.

### `sub_4578F0`: `CollapseMultitexture`

Observed local facts:

1. The helper compares the two active stages against the exact multitexture
   collapse table and rejects incompatible blend/state combinations.
2. It preserves the 3dfx lightmap/TMU handling from the GPL source.
3. On success it rewrites the first stage state, moves bundle 1 into place,
   and `memmove`s the later stages down.

That is exactly `CollapseMultitexture`.

### `sub_457AE0`: `SortNewShader`

The helper insertion-sorts the most recently added shader into
`tr.sortedShaders[]`, increments moved `sortedIndex` values, and writes the
final `sortedIndex` back to the new shader. That is exactly `SortNewShader`.

### `sub_457BE0`: `GeneratePermanentShader`

Observed local facts:

1. The helper emits the exact `GeneratePermanentShader - MAX_SHADERS hit`
   warning and falls back to `tr.defaultShader`.
2. It `Hunk_Alloc`s a new `shader_t`, copies the working `shader`, allocates
   per-stage bundles and texmods, and appends the result to the shader arrays.
3. It calls `SortNewShader`, hashes `newShader->name`, and links the shader
   into the hash table.

That is exactly `GeneratePermanentShader`.

### `sub_457DA0`: `VertexLightingCollapse`

The helper implements the exact vertex-light fallback logic from
`VertexLightingCollapse`: it ranks opaque stages, strips lightmap-heavy stages,
applies the cross-fade hacks for non-opaque shaders, and clears later stages.

## Shadow Path Closures

### `sub_4592C0`: `R_RenderShadowEdges`

The helper walks `edgeDefs`/`numEdgeDefs`, rejects reverse-paired front-facing
edges, and emits `GL_TRIANGLE_STRIP` silhouette quads for the surviving edges.
That is exactly `R_RenderShadowEdges`.

### `sub_4593E0`: `RB_ShadowTessEnd`

Observed local facts:

1. The helper projects each tess vertex by `-512 * lightDir`, matching the GPL
   shadow-volume extrusion path.
2. It computes triangle facing, records three directed edges per triangle, and
   configures the stencil/cull state for the two edge-render passes.
3. It calls the newly mapped `R_RenderShadowEdges` twice with reversed culling
   for mirror vs non-mirror paths.

That is exactly `RB_ShadowTessEnd`.

### `sub_459790`: `RB_ShadowFinish`

The helper checks for `r_shadows == 2` and at least four stencil bits, binds
`tr.whiteImage`, sets the exact `0.6` darkening color, and draws the
`(-100,100,-10)` to `(100,-100,-10)` fullscreen quad under stencil test.
That is exactly `RB_ShadowFinish`.

## Split-Gap Note

`functions.csv` still lists `FUN_00457c0b`, but HLIL shows `0x00457C0B` is an
internal address inside `GeneratePermanentShader`, not a true standalone
function start. It should be treated as a Ghidra split artifact rather than a
remaining mapping gap.

## Open Follow-Up

After this round, the remaining standalone unresolved starts immediately beyond
this tranche are `0x004589D0`, `0x00459A60`, and `0x00459D00`.
