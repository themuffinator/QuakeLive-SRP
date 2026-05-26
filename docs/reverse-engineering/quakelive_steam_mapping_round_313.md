# quakelive_steam.exe Mapping Round 313

Date: 2026-05-26

Scope: renderer target-aware texture binding and the image-constructor wiring
that depends on it.

## Summary

Round 312 reconstructed the remaining `tr_image.c` edge behavior, but a fresh
pass over the adjacent renderer bind band found one ownership cleanup still
worth closing: `sub_435730` is not image-local glue. It is the generalized
texture-target binder in `tr_backend.c`, and `sub_4357B0` is the exact
`GL_TEXTURE_2D` wrapper that retail exposes as the usual `GL_Bind` lane.

Observed facts:

- `sub_435730(void *image, int target)` reads the image texnum at offset `0x50`,
  applies the `r_nobind` dlight override, compares the current TMU texture
  cache, writes `frameUsed` at offset `0x54`, updates the cache, and calls
  the imported `glBindTexture(target, texnum)`.
- `sub_4357B0(void *image)` tail-calls `sub_435730(image, 0xde1)`.
- `R_CreateImageWithTarget` binds the requested target before the upload path
  configures texture parameters and image storage.

Inferred meaning:

- `sub_435730` should be named `GL_BindToTarget` and live with the existing GL
  state wrappers in `tr_backend.c`.
- `R_CreateImageWithTarget` should call that shared helper directly instead of
  carrying a private `tr_image.c` duplicate.

## Source Reconstruction

The source now reflects that split:

1. `tr_backend.c` contains `GL_BindToTarget( image_t *image, int glTarget )`.
2. `GL_Bind( image_t *image )` is the retail-style wrapper over
   `GL_BindToTarget( image, GL_TEXTURE_2D )`.
3. `tr_local.h` exposes the helper to renderer image construction.
4. `R_CreateImageWithTarget` binds `glTarget` through `GL_BindToTarget`.
5. `references/analysis/quakelive_symbol_aliases.json` promotes
   `sub_435730 -> GL_BindToTarget` beside the existing
   `sub_4357B0 -> GL_Bind`.

## Evidence Notes

- Canonical HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt`
  at `0x00435730` and `0x004357B0`.
- Companion corpus:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  records `FUN_00435730` and `FUN_004357b0` in the same renderer state-helper
  band.
- Prior context:
  round 144 already classified `sub_4357B0` as the `GL_TEXTURE_2D` wrapper over
  a generalized binder; this round names and wires that generalized owner.

## Verification

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
- `python -m pytest tests/test_renderer_memory_image_parity.py tests/test_renderer_internal_helper_mapping_parity.py -q`
- `python -m pytest tests/test_renderer_memory_image_parity.py tests/test_renderer_post_process_parity.py tests/test_platform_services.py::test_launcher_resource_bridge_reconstructs_retail_web_fallback_owner tests/test_awesomium_browser_parity.py::test_awesomium_surface_rebuild_and_mouse_mapping_reconstruct_browser_surface_space -q`
- `.\\.vscode\\build.ps1 -Configuration Debug -Platform x86`

Parity estimate for this scoped renderer image/bind lane:

- before: `99.0%`
- after: `99.4%`

Repo-wide checked-in tree parity remains estimated at `98%`; this pass closes a
source-ownership mismatch in already-reconstructed renderer image wiring.
