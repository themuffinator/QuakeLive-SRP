# quakelive_steam.exe Mapping Round 315

Date: 2026-05-26

Scope: `tr_image.c` upload-time gamma/intensity scaling under shader-backed
color correction.

## Summary

This pass re-opened the color path around `sub_444D00` after the previous
image-loader and diagnostic rounds. The retail helper does one extra ownership
check before the old Quake III gamma/intensity branches: it calls
`sub_43CCE0` and returns immediately when shader color correction is active.

Observed facts:

- `sub_444D00` starts by calling `sub_43CCE0`.
- The normal `only_gamma` and full light-scale branches are only reachable when
  that predicate returns `0`.
- `sub_43CCE0` itself requires post-process support, color-correction resource
  state, and the `r_colorCorrectActive` mirror before it returns `1`.
- Alpha remains untouched in every RGB scaling path.

Inferred meaning:

- Upload-time gamma/intensity remapping must not run while shader color
  correction owns the final image correction pass.
- The reconstructed source equivalent is `tr.colorCorrectActive`, the frontend
  mirror already published from the backend-validated post-process state.

## Source Reconstruction

`R_LightScaleTexture` now exits before upload-time gamma/intensity scaling when shader color correction is active.

`R_LightScaleTexture` now exits before either the `only_gamma` path or the
normal light-scaling path when `tr.colorCorrectActive` is true. This keeps
texture upload RGB data from being pre-gamma-adjusted under the shader
color-correction pipeline and restores retail ownership between upload-time
light scaling and post-process color correction.

## Evidence Table

| Symbol | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_43CCE0` | `RBPP_ColorCorrectEnabled` | High | Predicate checks post-process enabled state, color-correction resources, and `r_colorCorrectActive`. |
| `sub_444D00` | `R_LightScaleTexture` | High | Calls `sub_43CCE0` first, then enters the retained `only_gamma` / intensity-table branches only when it returns `0`. |
| `sub_4452F0` | `Upload32` | High | Calls `R_LightScaleTexture` before mip upload, so this gate directly affects uploaded image RGB data. |

## Verification

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
- `python -m pytest tests/test_renderer_post_process_parity.py tests/test_renderer_internal_helper_mapping_parity.py tests/test_renderer_memory_image_parity.py -q`
- `python -m pytest tests/test_renderer_memory_image_parity.py tests/test_renderer_post_process_parity.py tests/test_platform_services.py::test_launcher_resource_bridge_reconstructs_retail_web_fallback_owner tests/test_awesomium_browser_parity.py::test_awesomium_surface_rebuild_and_mouse_mapping_reconstruct_browser_surface_space -q`
- `MSBuild.exe src\\code\\renderer\\renderer.vcxproj /p:Configuration=Debug /p:Platform=x86 /m`

Parity estimate for this scoped renderer image/color lane:

- before: `99.6%`
- after: `99.8%`

Repo-wide checked-in tree parity remains estimated at `98%`; this pass closes
a real rendered-output risk in the color-correct image upload path.
