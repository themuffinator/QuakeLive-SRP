# Quake Live Steam Host Mapping Round 41

## Scope

This round closes the exact low-level image processing and upload helpers immediately below `R_CreateImage` inside `quakelive_steam.exe`.

The previous pass mapped the high-level image lifecycle. This one promotes the gamma correction helper, texture filtering mode switch, image-frame accounting helper, resampler, light scaling path, mip generators, mip-level blend helper, and the main `Upload32` texture upload core.

The primary local evidence for this round is:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `src/code/renderer/tr_image.c`

## Exact Image Utility Helpers

### `sub_4447D0`: `R_GammaCorrect`

Observed local facts:

1. The helper iterates a caller-supplied byte buffer for exactly `bufSize` bytes.
2. For each byte it performs the same table remap used by the source:
   - `buffer[i] = s_gammatable[buffer[i]]`
3. It performs no other channel logic or bounds shaping.

That is the exact gamma-table application helper `R_GammaCorrect`.

### `sub_444800`: `GL_TextureMode`

Observed local facts:

1. The helper walks the same six-entry texture filter mode table used by the source.
2. It emits the same invalid-mode warning:
   - `bad filter name\n`
3. It keeps the same Voodoo-specific trilinear guard and emits:
   - `Refusing to set trilinear on a voodoo.\n`
4. On success it stores the chosen `gl_filter_min` and `gl_filter_max` values.
5. It then walks all live images and, for every mipmapped image, binds it and applies the new `GL_TEXTURE_MIN_FILTER` and `GL_TEXTURE_MAG_FILTER` parameters.

That closes `sub_444800` as the exact texture filter mode switch helper `GL_TextureMode`.

### `sub_444900`: `R_SumOfUsedImages`

Observed local facts:

1. The helper walks the live `tr.images` table.
2. It only counts images whose `frameUsed` equals the current frame counter.
3. For those images it accumulates `uploadWidth * uploadHeight`.

That is the exact per-frame image texel accounting helper `R_SumOfUsedImages`.

## Exact Resample, Light Scale, And Mip Helpers

### `sub_444AF0`: `ResampleTexture`

Observed local facts:

1. The helper emits the same hard width limit failure:
   - `ResampleTexture: max width`
2. It builds the same `p1[]` and `p2[]` lookup arrays from `fracstep = inwidth * 0x10000 / outwidth`.
3. For each output row it samples the same two source rows:
   - `(i + 0.25) * inheight / outheight`
   - `(i + 0.75) * inheight / outheight`
4. For each output pixel it averages the same four RGBA source texels from those two rows.

That is the exact general texture resampler `ResampleTexture`.

### `sub_444D00`: `R_LightScaleTexture`

Observed local facts:

1. The helper first checks the shader color-correction predicate and returns
   without upload-time RGB scaling when that pass is active.
2. The helper splits on the same `only_gamma` flag used by the source.
3. In the `only_gamma` path it only does work when hardware gamma is unavailable and remaps RGB through `s_gammatable`.
4. In the full light-scale path it walks `width * height` pixels and applies:
   - `s_intensitytable` only when hardware gamma is available
   - `s_gammatable[s_intensitytable[x]]` when hardware gamma is unavailable
5. It leaves alpha untouched in all paths.

That closes `sub_444D00` as the exact light scaling helper `R_LightScaleTexture`.

### `sub_444E20`: `R_MipMap2`

Observed local facts:

1. The helper computes `outWidth = inWidth >> 1` and `outHeight = inHeight >> 1`.
2. It allocates a temporary `outWidth * outHeight * 4` buffer.
3. For each output texel and channel it applies the same weighted `4 x 4` kernel with total weight `36`.
4. It copies the temporary result back into the input buffer and frees the temporary memory.

That is the exact high-quality mip reduction helper `R_MipMap2`.

### `sub_4450A0`: `R_MipMap`

Observed local facts:

1. The helper first checks `r_simpleMipMaps`.
2. When simple mipmaps are disabled it tailcalls the now-closed `R_MipMap2`.
3. It returns immediately on `1 x 1` inputs.
4. When one dimension collapses to zero it keeps the larger dimension and averages source pairs.
5. Otherwise it averages the same `2 x 2` texel quads in place.

That closes `sub_4450A0` as the exact in-place mipmap helper `R_MipMap`.

### `sub_445270`: `R_BlendOverTexture`

Observed local facts:

1. The helper computes `inverseAlpha = 255 - blend[3]`.
2. It computes the same premultiplied RGB terms:
   - `blend[0] * blend[3]`
   - `blend[1] * blend[3]`
   - `blend[2] * blend[3]`
3. For each pixel it updates only RGB with the same blend formula:
   - `(data[channel] * inverseAlpha + premult[channel]) >> 9`
4. It leaves alpha untouched.

That is the exact mip-color overlay helper `R_BlendOverTexture`.

## Exact Upload Core

### `sub_4452F0`: `Upload32`

Observed local facts:

1. The helper rounds the incoming dimensions up to powers of two, optionally rounds down when `r_roundImagesDown` is enabled, and skips that power-of-two correction for rectangle textures.
2. When resampling is required it allocates a temporary buffer and calls the now-closed `ResampleTexture`.
3. It applies the same optional `r_picmip` reduction and clamps dimensions to at least `1`.
4. It repeatedly halves both dimensions when needed to stay within `glConfig.maxTextureSize`.
5. It scans the incoming texels to determine RGB maxima and whether any alpha differs from `255`, then selects the same internal format decision tree for:
   - `GL_RGB4_S3TC`
   - `GL_RGB5`
   - `GL_RGB8`
   - `GL_RGBA4`
   - `GL_RGBA8`
   - plain `3` / `4`
   - forced `3` for lightmaps
6. It either uploads the base level directly for non-mipmapped same-size textures or copies/scales into a working buffer and then calls the now-closed `R_LightScaleTexture`.
7. In the mipmapped path it repeatedly calls the now-closed `R_MipMap`, optionally applies the now-closed `R_BlendOverTexture` when `r_colorMipLevels` is enabled, and uploads each mip level with `qglTexImage2D`.
8. It applies the same filter selection at the end:
   - mipmapped textures use `gl_filter_min` / `gl_filter_max`
   - non-mipmapped textures use `GL_LINEAR`
9. It stores upload width, upload height, and internal format through the output pointers, calls the GL error check helper, and frees the same temporary buffers.

That is the exact `Upload32` texture upload core.

## Promoted Aliases

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4447D0` (`0x004447D0`) | `R_GammaCorrect` | Observed | Exact gamma-table remap helper. |
| `sub_444800` (`0x00444800`) | `GL_TextureMode` | Observed | Exact texture filter mode switch helper. |
| `sub_444900` (`0x00444900`) | `R_SumOfUsedImages` | Observed | Exact per-frame image texel accounting helper. |
| `sub_444AF0` (`0x00444AF0`) | `ResampleTexture` | Observed | Exact general texture resampler. |
| `sub_444D00` (`0x00444D00`) | `R_LightScaleTexture` | Observed | Exact image light scaling helper. |
| `sub_444E20` (`0x00444E20`) | `R_MipMap2` | Observed | Exact high-quality mip reduction helper. |
| `sub_4450A0` (`0x004450A0`) | `R_MipMap` | Observed | Exact in-place mipmap helper. |
| `sub_445270` (`0x00445270`) | `R_BlendOverTexture` | Observed | Exact mip-color overlay helper. |
| `sub_4452F0` (`0x004452F0`) | `Upload32` | Observed | Exact texture upload core. |

## Coverage Impact

On the committed `quakelive_steam.exe` Ghidra baseline of `5473` functions, this pass moves the explicit `quakelive_steam` alias set from `395` to `404` functions, which is approximately `7.2%` to `7.4%` host-symbol coverage.

## Open Questions

1. The shared filename hash helper at `sub_4D8990` is now well-bounded, but this round leaves it unmapped because the current local tree exposes multiple near-matching source-side hash helpers with different signatures and post-mix behavior.
2. The next clean continuation inside the renderer image band is the format loader cluster itself: `LoadBMP`, `LoadPCX`, `LoadPCX32`, `LoadTGA`, `LoadJPG`, and the Quake Live PNG path including the in-memory image loader at `sub_446F80`.
3. The unresolved export slot at `sub_451360` remains open and should stay unmapped until its Quake Live-specific interface is proven directly against HLIL and surrounding call sites.
