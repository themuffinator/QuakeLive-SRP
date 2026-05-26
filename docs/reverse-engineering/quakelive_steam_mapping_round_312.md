# quakelive_steam.exe Mapping Round 312

Date: 2026-05-26

Scope: renderer image construction, upload-target handling, file fallback order,
and in-memory image type detection/wiring.

## Summary

This round re-opened the `tr_image.c` retail image band that earlier passes had
mostly closed. The previous source already had the broad Quake Live shape, but
the fresh HLIL pass found several small source-visible mismatches in the
constructor and memory loader edges:

- `sub_445720` (`R_CreateImageWithTarget`) uses `glGenTextures` when imported,
  with `1024 + tr.numImages` retained only as the no-import fallback.
- The retail bind helper accepts a texture target; target-aware image creation
  must bind the requested target before upload.
- `Upload32` skips power-of-two resampling for `GL_TEXTURE_RECTANGLE_ARB`.
- The literal `"browser"` image forces the upload sample count to RGBA, even
  when the current pixel payload has no transparent alpha values.
- `sub_446AB0` (`R_LoadImage`) resolves `.tga` requests through `.jpg`, then
  `.png`, then the original `.tga`.
- `sub_446F00` (`R_DetectImageTypeFromMemory`) returns retail selector values:
  `0` JPEG, `1` BMP, `2` TGA, `3` PNG, `4` unknown.
- `sub_446F80` (`R_LoadImageFromMemory`) creates decoded memory images with
  `GL_CLAMP` and `GL_TEXTURE_2D`; the caller does not provide a wrap mode.

## Source Reconstruction

The writable source now mirrors those retail details:

1. `R_CreateImageWithTarget` allocates texture IDs through `qglGenTextures`
   when available and falls back to the historical generated ID range only when
   the import is absent.
2. `GL_BindToTarget` reconstructs the target-aware bind behavior used by the
   constructor while preserving the current texture cache; `GL_Bind` remains
   the retail `GL_TEXTURE_2D` wrapper.
3. `Upload32` takes a forced-sample override, skips power-of-two conversion for
   rectangle textures, and keeps the normal mip/picmip/lightmap decision tree
   for 2D images.
4. `R_ForcedImageSamples` returns `4` only for the exact `"browser"` image name,
   restoring the retail browser-surface RGBA upload path.
5. `R_DetectImageTypeFromMemory` now uses the retail selector order and the
   observed magic-byte offsets instead of the older source-side robust detector.
6. `R_LoadImageFromMemory` was narrowed back to the retail call surface and
   hardcodes `GL_CLAMP` when reusing or creating decoded memory images.
7. `R_LoadImage` now checks `.jpg` and `.png` replacement assets before falling
   back to the original `.tga`.

## Evidence Notes

- Canonical HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
  at `0x004452F0`, `0x00445720`, `0x00445910`, `0x00446AB0`,
  `0x00446D00`, `0x00446F00`, and `0x00446F80`.
- Target-aware bind evidence:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt`
  at `0x00435730`.
- Companion corpus:
  `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`,
  `imports.txt`, `exports.txt`, and `functions.csv`.
- Symbol support:
  `references/analysis/quakelive_symbol_aliases.json` contains promoted
  aliases for `GL_BindToTarget`, `R_CreateImageWithTarget`, `R_LoadImage`,
  `R_DetectImageTypeFromMemory`, and `R_LoadImageFromMemory`.

## Verification

- `python -m pytest tests/test_renderer_memory_image_parity.py -q`
- `python -m pytest tests/test_renderer_memory_image_parity.py tests/test_renderer_post_process_parity.py tests/test_platform_services.py::test_launcher_resource_bridge_reconstructs_retail_web_fallback_owner -q`
- `.\\.vscode\\build.ps1 -Configuration Debug -Platform x86`

Parity estimate for this scoped renderer image lane:

- before: `97%`
- after: `99%`

Repo-wide checked-in tree parity remains estimated at `98%`; this pass closes
small but visible renderer-image edge mismatches rather than a new broad gap.
