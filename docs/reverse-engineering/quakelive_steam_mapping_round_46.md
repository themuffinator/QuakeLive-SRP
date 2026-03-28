# Quake Live Steam Host Mapping Round 46

## Scope

This round closes the clean standalone helpers immediately above the renderer
scene-registration tranche from the previous pass.

The promoted slice covers:

- the renderer noise-table bootstrap and 4D noise sampler
- the scene-frame SMP toggle/reset helper
- the scene poly-to-drawsurf bridge
- the clip-to-window projection helper used by flare-space tests

The primary evidence for this round is:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `src/code/renderer/tr_noise.c`
- `src/code/renderer/tr_scene.c`
- `src/code/renderer/tr_main.c`
- `src/code/renderer/tr_flares.c`

## Exact Noise Helpers

### `sub_44FC90`: `R_NoiseInit`

Observed local facts:

1. The helper starts with the exact fixed seed `srand(1001)`.
2. It iterates `0x100` float/int table slots and fills one table with
   `rand()/RAND_MAX * 2 - 1`.
3. It fills the paired permutation table with an unsigned byte derived from
   `rand()/RAND_MAX * 255`.

That is the exact noise bootstrap helper `R_NoiseInit`.

### `sub_44FD20`: `R_NoiseGet4f`

Observed local facts:

1. The helper floors all four float inputs and keeps the fractional parts.
2. It performs the exact nested permutation-table lookups used by
   `INDEX( x, y, z, t )`.
3. It bilinearly interpolates the front and back layers, then lerps between
   the two z-slices, and finally lerps the two t-slices.

That is the exact 4D noise sampler `R_NoiseGet4f`.

## Exact Scene Helpers

### `sub_4507E0`: `R_ToggleSmpFrame`

Observed local facts:

1. The helper toggles the SMP frame index only when the SMP CVar is enabled;
   otherwise it resets the frame index to zero.
2. It clears the active command buffer `used` count for the chosen SMP frame.
3. It zeroes the first-scene and count trackers for drawsurfs, dlights,
   entities, polys, and polyverts before tail-calling the next scene helper.

That is the exact scene-frame reset helper `R_ToggleSmpFrame`.

### `sub_450870`: `R_AddPolygonSurfaces`

Observed local facts:

1. The helper sets `tr.currentEntityNum` to `ENTITYNUM_WORLD` and rebuilds the
   shifted entity sort key.
2. It iterates `tr.refdef.polys` for `tr.refdef.numPolys`.
3. For each poly it resolves the shader handle and calls `R_AddDrawSurf` with
   the poly pointer, resolved shader, fog index, and `qfalse`.

That is the exact scene poly bridge `R_AddPolygonSurfaces`.

## Exact Projection Helper

### `sub_4514C0`: `R_TransformClipToWindow`

Observed local facts:

1. The helper divides clip-space `x` and `y` by `w`.
2. It computes normalized depth with the exact
   `(clip[2] + clip[3]) / (2 * clip[3])` formula.
3. It converts normalized coordinates into viewport-space window coordinates
   using the `0.5 * (1 + normalized)` scale-and-bias pattern and rounds the
   screen-space `x` and `y`.
4. The immediately preceding helper at `sub_451460` performs the same
   clip-bound checks that appear inline in `RB_AddFlare`, which strengthens the
   local renderer ownership of this block.

That is the exact clip-to-window helper `R_TransformClipToWindow`.

## Open Follow-Up

This pass intentionally leaves the remaining `0x44FFD0-0x4507C0` block
unpromoted. The HLIL there clearly belongs to Quake Live post-effect and
render-target setup, but the exact retail source names are not yet stable
enough to promote confidently.

The small helpers at `sub_451420` and `sub_451460` also remain unpromoted.
They look compiler-extracted from nearby renderer call sites rather than clean
top-level retail function boundaries.
