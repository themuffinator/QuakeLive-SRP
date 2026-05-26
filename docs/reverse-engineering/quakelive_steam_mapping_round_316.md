# quakelive_steam.exe Mapping Round 316

Date: 2026-05-26

Scope: direct reconstruction of the retail color-correction predicate wiring
used by gamma and image upload paths.

## Summary

This pass tightened the Round 315 gamma fix by replacing the local
`tr.colorCorrectActive` proxy with a source-level reconstruction of
`sub_43CCE0` itself.

Observed facts:

- `sub_43CCE0` returns `1` only when `sub_4507C0` succeeds, the shader /
  rectangle-texture support flag is set, and `r_colorCorrectActive->integer`
  is non-zero.
- `sub_444D00` calls `sub_43CCE0` before either upload-time gamma or full
  intensity scaling.
- `sub_4475D0` calls `sub_43CCE0` once before the overbright hardware-gamma
  clamp and once before `GLimp_SetGamma`.

Inferred meaning:

- Shader-backed color correction, when active, owns final display correction
  and must suppress both upload-time RGB remapping and the OS gamma-ramp write.
- The predicate should live in the backend post-process owner rather than being
  approximated from the frontend mirror alone.

## Source Reconstruction

`RBPP_ColorCorrectEnabled()` now mirrors the retail `sub_43CCE0` checks:

- `RB_PostProcessEnabled()` for the post-process runtime gate.
- `s_postProcess.supported` for the recovered shader / rectangle-texture
  capability flag.
- `r_colorCorrectActive->integer` for the retail ROM mirror that indicates the
  color-correction path is active.

`R_LightScaleTexture` now calls `RBPP_ColorCorrectEnabled()` before touching
texture RGB values.

`R_SetColorMappings` now calls `RBPP_ColorCorrectEnabled()` at the same two decision points retail calls `sub_43CCE0`.
The first call preserves overbright ownership for the shader path when hardware
gamma is unavailable; the second suppresses `GLimp_SetGamma` while shader color
correction owns final output correction.

## Evidence Table

| Symbol | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_43CCE0` | `RBPP_ColorCorrectEnabled` | High | HLIL shows `sub_4507C0`, shader support, and `r_colorCorrectActive` cvar checks. |
| `sub_444D00` | `R_LightScaleTexture` | High | First call is `sub_43CCE0`; the RGB modification paths only execute when it returns `0`. |
| `sub_4475D0` | `R_SetColorMappings` | High | Calls `sub_43CCE0` before overbright clamping and again before hardware gamma upload. |

## Verification

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
- `python -m pytest tests/test_renderer_post_process_parity.py tests/test_renderer_internal_helper_mapping_parity.py tests/test_renderer_memory_image_parity.py -q`
- `MSBuild.exe src\\code\\renderer\\renderer.vcxproj /p:Configuration=Debug /p:Platform=x86 /m`

Parity estimate for this scoped renderer gamma/image lane:

- before: `99.8%`
- after: `99.9%`

Repo-wide checked-in tree parity remains estimated at `98%`; this pass removes
one more approximation from the retail color-correction and image upload path.
