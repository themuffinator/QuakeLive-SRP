# Quake Live Steam Host Mapping Round 42

## Scope

This round closes the renderer image format loader tranche inside `quakelive_steam.exe`, including the file-backed and buffer-backed BMP/PCX/PNG/TGA/JPG paths, the JPEG screenshot save helpers, and the Quake Live in-memory image loader.

It also corrects the public `R_CreateImage` entry point split: the source-shaped seven-argument wrapper lives at `0x00445910`, while the previously promoted `0x00445720` helper is the Quake Live target-aware internal variant that the wrapper feeds.

The primary local evidence for this round is:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `src/code/renderer/tr_image.c`

## Public Create-Image Entry Correction

### `sub_445910`: `R_CreateImage`

Observed local facts:

1. The helper is a pure tail wrapper over `sub_445720`.
2. It forwards the exact seven source-shaped arguments used by the GPL-side `R_CreateImage`.
3. It hardcodes the final argument as `0x0DE1` (`GL_TEXTURE_2D`).
4. Retail callers that match the source-side public API, including the lightmap, font stash, Steam avatar, and browser image creation paths, call this wrapper rather than the eight-argument helper directly.

That closes `sub_445910` as the public image-construction helper `R_CreateImage`.

### `sub_445720`: `R_CreateImageWithTarget`

Observed local facts:

1. The helper contains all of the construction logic previously bounded in round 40: allocation, hash insertion, upload, wrap-mode setup, and TMU handling.
2. Unlike the public wrapper, it accepts an extra final argument and threads it into the GL bind/parameter path.
3. The public `sub_445910` wrapper proves the helper sits one layer below `R_CreateImage`.
4. The helper uses `glGenTextures` when the GL import is available and retains the historical `1024 + tr.numImages` fallback only for the no-import path.
5. It binds through the target-aware `GL_BindToTarget` helper and forces the upload sample count to RGBA only for the literal `"browser"` surface image.

The exact internal retail name is still unproven, but the role is now stable enough to promote `sub_445720` as the inferred target-aware helper `R_CreateImageWithTarget`.

## Exact File And Buffer Image Loaders

### `sub_445940`: `LoadBMPFromBuffer`

Observed local facts:

1. The helper decodes a caller-supplied BMP byte buffer instead of reading from the filesystem.
2. Its hard failures use the exact `LoadBMPFromBuffer` string prefix:
   - `LoadBMPFromBuffer: only Windows-style BMP files supported (%s)\n`
   - `LoadBMPFromBuffer: header size does not match file size (%d vs. %d) (%s)\n`
   - `LoadBMPFromBuffer: only uncompressed BMP files supported (%s)\n`
   - `LoadBMPFromBuffer: monochrome and 4-bit BMP files not supported (%s)\n`
3. It allocates an RGBA destination buffer and expands 8/16/24/32-bit BMP payloads in the same per-pixel cases used by the source-side loader family.

That is the exact in-memory BMP decoder `LoadBMPFromBuffer`.

### `sub_445C80`: `LoadBMP`

Observed local facts:

1. The helper calls the filesystem read helper up front and clears the outgoing `pic` pointer before any work.
2. It passes the loaded file buffer and file length to the now-closed `LoadBMPFromBuffer`.
3. It frees the temporary file buffer on the way out.

That closes `sub_445C80` as the exact file-backed BMP loader `LoadBMP`.

### `sub_445CC0`: `LoadPCX`

Observed local facts:

1. The helper reads the PCX file through the filesystem layer, validates the same manufacturer/version/encoding/depth constraints, and rejects dimensions at or above `1024`.
2. It emits the exact malformed-file warning:
   - `Bad pcx file %s (%i x %i) (%i x %i)\n`
3. It allocates an 8-bit pixel buffer plus an optional `768`-byte palette copy, then expands run-length packets into the destination.
4. It emits the same malformed overrun warning:
   - `PCX file %s was malformed`

That is the exact PCX loader `LoadPCX`.

### `sub_445E70`: `LoadPCX32`

Observed local facts:

1. The helper calls the now-closed `LoadPCX`.
2. It returns early with `*pic = NULL` when the 8-bit decode fails.
3. It allocates a `4 * width * height` RGBA buffer.
4. It walks the indexed pixels and expands them through the copied palette with alpha forced to `255`.
5. It frees the temporary 8-bit pixel buffer and palette afterward.

That closes `sub_445E70` as the exact 32-bit PCX expansion helper `LoadPCX32`.

### `sub_445F10`: `PNGReadData`

Observed local facts:

1. The helper resolves libpng’s custom IO pointer from the `png_struct`.
2. It clamps the requested read length against the current offset and total buffer size.
3. It copies from the in-memory PNG payload into the caller’s destination and advances the offset.

That is the exact libpng memory read callback `PNGReadData`.

### `sub_445F50`: `LoadPNGFromBuffer`

Observed local facts:

1. The helper receives a filename string for error reporting plus a caller-supplied PNG buffer and length.
2. It initializes libpng through the same create-info / setjmp recovery flow used by the source-side PNG path.
3. On decode failure it emits the same warning:
   - `LoadPNG: Error occurred while decoding %s.\n`
4. It installs the now-closed `PNGReadData` callback, expands palette/gray/TRNS payloads, strips 16-bit channels, fills missing alpha with `0xFF`, allocates row pointers, and decodes into a contiguous RGBA buffer without requesting a per-file libpng gamma transform.

The local GPL tree only exposes the file-backed entry point, but the retail helper role is stable enough to promote `sub_445F50` as the inferred in-memory decoder `LoadPNGFromBuffer`.

### `sub_446160`: `LoadPNG`

Observed local facts:

1. The helper reads the named file through the filesystem layer and zeros the outgoing `pic` pointer before doing work.
2. It forwards the loaded file buffer and length to the now-closed `LoadPNGFromBuffer`.
3. It frees the temporary file buffer before returning.

That closes `sub_446160` as the exact file-backed PNG loader `LoadPNG`.

### `sub_4461B0`: `LoadTGAFromBuffer`

Observed local facts:

1. The helper parses the TGA header directly from a caller-supplied memory buffer.
2. It emits the same validation failures used by the file-backed source loader:
   - `LoadTGA: Only type 2 (RGB), 3 (gray), and 10 (RGB) TGA images supported\n`
   - `LoadTGA: colormaps not supported\n`
   - `LoadTGA: Only 32 or 24 bit images supported (no colormaps)\n`
   - `LoadTGA: illegal pixel_size '%d' in file '%s'\n`
3. It allocates an RGBA buffer and decodes the same uncompressed and RLE packet layouts as the source-side loader.

The local tree only keeps the file-backed entry point, so the retail memory decoder is promoted as the inferred helper `LoadTGAFromBuffer`.

### `sub_4465A0`: `LoadTGA`

Observed local facts:

1. The helper reads the named TGA through the filesystem layer and clears the outgoing `pic` pointer before decode.
2. It forwards the file buffer to the now-closed `LoadTGAFromBuffer`.
3. It frees the temporary file buffer afterward.

That closes `sub_4465A0` as the exact file-backed TGA loader `LoadTGA`.

### `sub_4465E0`: `LoadJPGFromBuffer`

Observed local facts:

1. The helper receives a caller-supplied JPEG byte buffer and output pointers.
2. It builds a decompression context, feeds the memory source into the decoder, and allocates an output image buffer sized from the decoded width, height, and channel count.
3. It iterates scanlines into the destination buffer, then walks the alpha channel positions and forces them to `255`.
4. The file-backed wrapper directly above it proves this helper is the in-memory JPEG decode core rather than the filesystem entry point.

The exact internal retail name is unproven in the committed sources, but the role is stable enough to promote `sub_4465E0` as the inferred helper `LoadJPGFromBuffer`.

### `sub_446740`: `LoadJPG`

Observed local facts:

1. The helper reads the JPEG file through the filesystem layer.
2. It returns immediately when the file read fails.
3. It forwards the loaded buffer to the now-closed `LoadJPGFromBuffer`.
4. It frees the temporary file buffer on success and failure paths.

That closes `sub_446740` as the exact file-backed JPEG loader `LoadJPG`.

## Exact JPEG Save Helpers

### `sub_417780`: `empty_output_buffer`

Observed local facts:

1. The helper consists solely of `return TRUE`.
2. `SaveJPG` stores its address as the JPEG destination manager’s `empty_output_buffer` callback.

That is the exact JPEG destination callback `empty_output_buffer`.

### `sub_446780`: `init_destination`

Observed local facts:

1. The helper resolves the destination manager out of `cinfo->dest`.
2. It copies `outfile` into `next_output_byte`.
3. It copies `size` into `free_in_buffer`.

That is the exact JPEG destination bootstrap callback `init_destination`.

### `sub_4467A0`: `jpeg_write_scanlines`

Observed local facts:

1. The helper validates that the compressor state is the active scanning state and raises the same bad-state error path when it is not.
2. It warns when `next_scanline >= image_height`.
3. It invokes the optional progress hook, the optional pass-startup hook, clamps `num_lines` to the remaining rows, calls the main `process_data` callback, and advances `next_scanline` by the returned row count.

That closes `sub_4467A0` as the exact `jpeg_write_scanlines` implementation embedded in the retail host.

### `sub_446860`: `term_destination`

Observed local facts:

1. The helper resolves the destination manager out of `cinfo->dest`.
2. It computes `size - free_in_buffer`.
3. It stores that byte count into the global `hackSize`.

That is the exact JPEG destination shutdown callback `term_destination`.

### `sub_446880`: `SaveJPG`

Observed local facts:

1. The helper allocates `image_width * image_height * 4` bytes of temporary output storage.
2. It installs the now-closed `init_destination`, `empty_output_buffer`, and `term_destination` callbacks into the JPEG destination manager.
3. It sets `input_components = 4`, `in_color_space = JCS_RGB`, applies the quality parameter, and starts compression.
4. It iterates scanlines bottom-up from the source image buffer and feeds them through the now-closed `jpeg_write_scanlines`.
5. It finishes compression, writes `hackSize` bytes to disk, frees the temp buffer, and destroys the compressor object.

That closes `sub_446880` as the exact screenshot/output helper `SaveJPG`.

## Exact In-Memory Image Path

### `sub_446F00`: `R_DetectImageTypeFromMemory`

Observed local facts:

1. The helper classifies an incoming memory buffer by magic bytes instead of filename extension.
2. It returns the retail selector order: `0` JPEG, `1` BMP, `2` TGA, `3` PNG, and `4` unknown.
3. Its PNG check looks at bytes `1..3` for `PNG`, its JPEG check looks for `JFIF` at bytes `6..9`, and its TGA check uses the colormap, image-type, and pixel-size header bytes.
4. The now-closed `R_LoadImageFromMemory` uses those selector values as a switch discriminator for the specific decoder entry points.

The exact retail symbol name is not exported by the committed corpus, but the role is stable enough to promote `sub_446F00` as the inferred type detector `R_DetectImageTypeFromMemory`.

### `sub_446F80`: `R_LoadImageFromMemory`

Observed local facts:

1. The helper first hashes the image name into the live image table and reuses an existing image when the name already exists.
2. On a miss it calls the now-closed `R_DetectImageTypeFromMemory`.
3. It dispatches to the now-closed in-memory decoder set:
   - `LoadJPGFromBuffer`
   - `LoadBMPFromBuffer`
   - `LoadTGAFromBuffer`
   - `LoadPNGFromBuffer`
4. On unknown data it emits the exact warning:
   - `WARNING: R_LoadImageFromMemory() Unable to detect image type.\n`
5. On successful decode it calls the now-corrected target-aware image constructor with `GL_CLAMP` / `GL_TEXTURE_2D` and frees the temporary RGBA buffer.

That closes `sub_446F80` as the exact Quake Live in-memory image loader `R_LoadImageFromMemory`.

## Promoted Aliases

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_417780` (`0x00417780`) | `empty_output_buffer` | Observed | Exact JPEG destination callback that always returns success. |
| `sub_445720` (`0x00445720`) | `R_CreateImageWithTarget` | Inferred | Quake Live target-aware internal image constructor sitting below the public wrapper. |
| `sub_445910` (`0x00445910`) | `R_CreateImage` | Observed | Exact public seven-argument image-construction entry point. |
| `sub_445940` (`0x00445940`) | `LoadBMPFromBuffer` | Observed | Exact in-memory BMP decoder. |
| `sub_445C80` (`0x00445C80`) | `LoadBMP` | Observed | Exact file-backed BMP loader. |
| `sub_445CC0` (`0x00445CC0`) | `LoadPCX` | Observed | Exact PCX loader. |
| `sub_445E70` (`0x00445E70`) | `LoadPCX32` | Observed | Exact 32-bit PCX expansion helper. |
| `sub_445F10` (`0x00445F10`) | `PNGReadData` | Observed | Exact libpng custom memory read callback. |
| `sub_445F50` (`0x00445F50`) | `LoadPNGFromBuffer` | Inferred | Retail in-memory PNG decode core. |
| `sub_446160` (`0x00446160`) | `LoadPNG` | Observed | Exact file-backed PNG loader. |
| `sub_4461B0` (`0x004461B0`) | `LoadTGAFromBuffer` | Inferred | Retail in-memory TGA decode core. |
| `sub_4465A0` (`0x004465A0`) | `LoadTGA` | Observed | Exact file-backed TGA loader. |
| `sub_4465E0` (`0x004465E0`) | `LoadJPGFromBuffer` | Inferred | Retail in-memory JPEG decode core. |
| `sub_446740` (`0x00446740`) | `LoadJPG` | Observed | Exact file-backed JPEG loader. |
| `sub_446780` (`0x00446780`) | `init_destination` | Observed | Exact JPEG destination initialization callback. |
| `sub_4467A0` (`0x004467A0`) | `jpeg_write_scanlines` | Observed | Exact embedded JPEG scanline writer. |
| `sub_446860` (`0x00446860`) | `term_destination` | Observed | Exact JPEG destination completion callback. |
| `sub_446880` (`0x00446880`) | `SaveJPG` | Observed | Exact JPEG screenshot/output helper. |
| `sub_446F00` (`0x00446F00`) | `R_DetectImageTypeFromMemory` | Inferred | Quake Live magic-byte image type detector for memory payloads. |
| `sub_446F80` (`0x00446F80`) | `R_LoadImageFromMemory` | Observed | Exact Quake Live in-memory image loader and image-table reuse helper. |

## Coverage Impact

On the committed `quakelive_steam.exe` Ghidra baseline of `5473` functions, this pass moves the explicit `quakelive_steam` alias set from `404` to `423` functions, which is approximately `7.4%` to `7.7%` host-symbol coverage.

## Open Questions

1. The retail host clearly embeds more of the JPEG destination/compression path than the current local tree surfaces as standalone helpers; `jpegDest` and any non-inlined `jpeg_start_compress` equivalent should stay open until their exact boundaries are proven from HLIL and call sites.
2. The corrected `R_CreateImage` split means earlier notes that treated `sub_445720` as the public entry point should now be read as describing the shared internal construction body rather than the outer API boundary.
3. The next clean continuation in the renderer band is the skin and skin-list cluster immediately following `R_DeleteTextures`, unless the team wants to keep pushing on the Quake Live-only image/memory path extensions.
