# Quake Live Steam Host Mapping Round 40

## Scope

This round closes the exact image bootstrap and image lookup tranche inside `quakelive_steam.exe`.

The previous pass mapped the shader-management layer. This one drops into the adjacent image system and promotes the image list command, image creation/loading path, runtime image lookup/reuse path, built-in image bootstrap helpers, fog image generation, color-mapping init, and texture teardown.

The primary local evidence for this round is:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `src/code/renderer/tr_image.c`

## Exact Image Listing And Creation Helpers

### `sub_444940`: `R_ImageList_f`

Observed local facts:

1. The helper emits the exact image-list header:
   - `\n      -w-- -h-- -mm- -TMU- -if...`
2. It walks the live `tr.images` table, sums `uploadWidth * uploadHeight`, and prints per-image width, height, mipmap flag, TMU, internal format tag, wrap mode, and image name.
3. It maps the same internal-format tags used by the source:
   - `I`
   - `IA`
   - `RGB`
   - `RGBA`
   - `RGBA8`
   - `RGB8`
   - `S3TC`
   - `RGBA4`
   - `RGB5`
4. It maps the same wrap-mode tags used by the source:
   - `clmp`
   - `rept`
   - `edge`
5. It emits the same trailers:
   - ` %i total texels (not including mipmaps)\n`
   - ` %i total images\n\n`

That is the exact image-list console command `R_ImageList_f`.

### `sub_445720`: `R_CreateImage`

Observed local facts:

1. The helper measures the incoming name and emits the exact overflow error:
   - `R_CreateImage: "%s" is too long\n`
2. It special-cases names beginning with `*lightmap`.
3. It checks the live image count against `0x800` and emits the same hard failure:
   - `R_CreateImage: MAX_DRAWIMAGES hit\n`
4. It allocates a `0x70`-byte `image_t`, stores it in the live image array, assigns `texnum = tr.numImages + 1024`, and increments the image count.
5. It stores `mipmap`, `allowPicmip`, `width`, `height`, and `wrapClampMode` in the same field layout used by the source.
6. It selects TMU `1` for lightmaps when multitexture is available and TMU `0` otherwise, binds the texture, uploads the image, applies the GL wrap parameters, and restores the active texture selection.
7. It hashes the image name into the image hash table and links the new record into the bucket chain.

That closes `sub_445720` as the exact image-construction helper `R_CreateImage`.

## Exact Image Loading And Lookup Helpers

### `sub_446AB0`: `R_LoadImage`

Observed local facts:

1. The helper clears the outgoing `pic`, `width`, and `height` pointers up front.
2. It dispatches on the same extension set used by the source:
   - `.tga`
   - `.pcx`
   - `.bmp`
   - `.jpg`
   - `.png`
3. On the `.tga` path it prefers Quake Live's replacement-asset extensions before falling back to the original TGA:
   - `.jpg`
   - `.png`
   - original `.tga`
4. It emits the exact final miss warning:
   - `image not found (tga/jpg/png): %s\n`

That is the exact top-level image loader `R_LoadImage`.

### `sub_446D00`: `R_FindImageFile`

Observed local facts:

1. The helper returns `NULL` immediately when the incoming name pointer is `NULL`.
2. It hashes the image name into the live image hash table and walks the bucket chain looking for a case-insensitive name match.
3. It treats `*white` as reusable regardless of parm mismatches, matching the source-side special case.
4. For other reused images it emits the same mismatch warnings when `mipmap`, `allowPicmip`, or `glWrapClampMode` differ.
5. On a miss it calls the now-closed `R_LoadImage`.
6. If the first load fails, it uppercases the file extension in a stack copy, emits:
   - `trying %s...\n`
   and retries the load.
7. When the load succeeds it calls the now-closed `R_CreateImage`, frees the temporary pixel buffer, and returns the created image.

That closes `sub_446D00` as the exact runtime image lookup/creation helper `R_FindImageFile`.

## Exact Built-In Image Bootstrap Helpers

### `sub_4470D0`: `R_CreateDlightImage`

Observed local facts:

1. The helper builds a `16 x 16` inverse-square radial falloff texture.
2. It clamps brightness values above `255` down to `255` and values below `75` down to `0`.
3. It writes equal RGB channels with alpha forced to `255`.
4. It registers the result as `*dlight` through the now-closed `R_CreateImage` with `GL_CLAMP`.

That is the exact built-in dynamic-light texture helper `R_CreateDlightImage`.

### `sub_4471D0`: `R_InitFogTable`

Observed local facts:

1. The helper iterates exactly `256` entries.
2. For each index it computes `pow(i / (FOG_TABLE_SIZE - 1), 0.5)` and writes the result into the global fog table.

That is the exact fog-table bootstrap helper `R_InitFogTable`.

### `sub_447210`: `R_FogFactor`

Observed local facts:

1. The helper subtracts `1 / 512` from `s` before any further work.
2. It returns `0` when the adjusted `s` is non-positive or when `t < 1 / 32`.
3. For intermediate `t` values it scales `s` by the same depth ramp used by the source and then multiplies the result by `8`.
4. It clamps the scaled value to `1` and indexes the fog table through the same float-to-int conversion helper.

That closes `sub_447210` as the exact fog-factor helper `R_FogFactor`.

### `sub_4472B0`: `R_CreateFogImage`

Observed local facts:

1. The helper allocates `0x8000` bytes, matching a `256 x 32 x 4` RGBA image.
2. It fills the texture by calling the now-closed `R_FogFactor` at `(x + 0.5) / 256` and `(y + 0.5) / 32`.
3. It writes white RGB with alpha set to `255 * d`.
4. It registers the result as `*fog` through the now-closed `R_CreateImage` with `GL_CLAMP`.
5. It frees the temporary buffer and sets the texture border color to all `1.0`.

That is the exact built-in fog texture helper `R_CreateFogImage`.

### `sub_4473F0`: `R_CreateDefaultImage`

Observed local facts:

1. The helper fills a `16 x 16` RGBA buffer with `0x20`.
2. It paints a full white border around the image on all four edges.
3. It registers the result as `*default` through the now-closed `R_CreateImage` with `mipmap = qtrue` and `GL_REPEAT`.

That is the exact default checker image helper `R_CreateDefaultImage`.

### `sub_4474C0`: `R_CreateBuiltinImages`

Observed local facts:

1. The helper calls the now-closed `R_CreateDefaultImage` first.
2. It fills an `8 x 8` white image and registers it as `*white`.
3. It fills an `8 x 8` image using `tr.identityLightByte` and registers it as `*identityLight`.
4. It creates the repeated `*scratch` images through the same loop structure used by the source.
5. The source-side tail after those loops is `R_CreateDlightImage(); R_CreateFogImage();`, and the retail body sits in the exact same bootstrap band immediately before color mapping and image init.

The Binary Ninja decompilation truncates part of the scratch-image loop into an invalid store, but the surrounding call sequence and data pattern still identify the function cleanly as `R_CreateBuiltinImages`.

### `sub_4475D0`: `R_SetColorMappings`

Observed local facts:

1. The helper pulls the current device gamma support state and clamps `r_overBrightBits` through the same fullscreen/color-depth policy used by the source.
2. It computes `tr.identityLight` and `tr.identityLightByte`.
3. It clamps `r_intensity` to at least `1` and clamps `r_gamma` to the same valid range through `Cvar_Set`.
4. It rebuilds the same gamma and intensity tables used by the image subsystem.
5. It calls the gamma-setter when hardware gamma is available.

That closes `sub_4475D0` as the exact color-mapping bootstrap helper `R_SetColorMappings`.

### `sub_4477E0`: `R_InitImages`

Observed local facts:

1. The helper clears the image hash table.
2. It then calls the now-closed `R_SetColorMappings`.
3. It tailcalls the now-closed `R_CreateBuiltinImages`.

That is the exact image-system init entry point `R_InitImages`.

### `sub_447800`: `R_DeleteTextures`

Observed local facts:

1. The helper iterates `tr.numImages` and deletes each texture handle.
2. It clears the live image table and resets `tr.numImages` to `0`.
3. It clears `glState.currenttextures`.
4. It unbinds texture `0`, and when multitexture is present it switches across both TMUs and unbinds both, matching the source teardown path.

That closes `sub_447800` as the exact renderer texture teardown helper `R_DeleteTextures`.

## Promoted Aliases

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_444940` (`0x00444940`) | `R_ImageList_f` | Observed | Exact image-list console command helper. |
| `sub_445720` (`0x00445720`) | `R_CreateImage` | Observed | Exact image construction and hash-link helper. |
| `sub_446AB0` (`0x00446AB0`) | `R_LoadImage` | Observed | Exact top-level image loader for disk-backed image formats. |
| `sub_446D00` (`0x00446D00`) | `R_FindImageFile` | Observed | Exact runtime image lookup and on-miss creation helper. |
| `sub_4470D0` (`0x004470D0`) | `R_CreateDlightImage` | Observed | Exact dynamic-light texture bootstrap helper. |
| `sub_4471D0` (`0x004471D0`) | `R_InitFogTable` | Observed | Exact fog lookup-table initializer. |
| `sub_447210` (`0x00447210`) | `R_FogFactor` | Observed | Exact fog alpha factor helper. |
| `sub_4472B0` (`0x004472B0`) | `R_CreateFogImage` | Observed | Exact fog texture bootstrap helper. |
| `sub_4473F0` (`0x004473F0`) | `R_CreateDefaultImage` | Observed | Exact default-image bootstrap helper. |
| `sub_4474C0` (`0x004474C0`) | `R_CreateBuiltinImages` | Observed | Exact built-in image creation chain. |
| `sub_4475D0` (`0x004475D0`) | `R_SetColorMappings` | Observed | Exact renderer gamma/intensity mapping bootstrap helper. |
| `sub_4477E0` (`0x004477E0`) | `R_InitImages` | Observed | Exact image-system init entry point. |
| `sub_447800` (`0x00447800`) | `R_DeleteTextures` | Observed | Exact renderer texture teardown helper. |

## Coverage Impact

On the committed `quakelive_steam.exe` Ghidra baseline of `5473` functions, this pass moves the explicit `quakelive_steam` alias set from `382` to `395` functions, which is approximately `7.0%` to `7.2%` host-symbol coverage.

## Open Questions

1. The adjacent image helper at `sub_446F80` is now tightly bounded as Quake Live’s in-memory image loader, but this round stops short of naming it because the current local source tree does not yet expose a proven exact public helper with the same interface.
2. The unresolved export slot at `sub_451360` remains open and should stay unmapped until its Quake Live-specific interface is proven directly against HLIL and surrounding call sites.
3. The next clean continuation inside this renderer band is the lower-level image processing pipeline: resampling, mip generation, light scaling, gamma correction, and the remaining upload helpers that feed `R_CreateImage`.
