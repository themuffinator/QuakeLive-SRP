# quakelive_steam.exe Mapping Round 320

Date: 2026-05-26

Scope: post-process bloom combine uniform slot order and private-tail argument
names.

## Summary

Round 319 closed the private refexport tail. This pass tightens the source
reconstruction by aligning the five-float bloom setter's source-level argument
names and write order with the retail combine uniform slots.

Observed facts:

- `sub_4380F0` resolves the combine uniforms in this order:
  - `data_5860c8 = p_bloomsaturation`
  - `data_5860cc = p_scenesaturation`
  - `data_5860d0 = p_bloomintensity`
  - `data_5860d4 = p_sceneintensity`
- `sub_438590` refreshes the same slots from cvars in that order.
- `sub_4386D0` writes `arg2` to `data_5860c8`, `arg4` to `data_5860cc`,
  `arg3` to `data_5860d0`, and `arg5` to `data_5860d4`.

Inferred meaning:

- The private export wrapper `sub_451420` should be treated as:
  `brightThreshold`, `bloomSaturation`, `bloomIntensity`,
  `sceneSaturation`, `sceneIntensity`.
- The source helper can still accept a named helper signature, but its write
  order should mirror the retail slot order rather than the shader declaration
  order.

## Source Reconstruction

`RBPP_SetBloomUniforms` and `R_SetPostProcessBloomParameters` now name the last
two arguments as `sceneSaturation` then `sceneIntensity`.

`ppProgram_t`, `RBPP_LoadProgram`, and `RBPP_SetBloomUniforms` now keep the
combine uniform order:

- `bloomSaturationUniform`
- `sceneSaturationUniform`
- `bloomIntensityUniform`
- `sceneIntensityUniform`

This does not change the public tail ABI size or slot count. It corrects the
source reconstruction so future callers of `RetailPostProcessPass` do not pass
scene intensity and scene saturation in the wrong order.

## Evidence Table

| Symbol / Data | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `data_5860c8` | `bloomSaturationUniform` | High | `sub_4380F0` resolves `p_bloomsaturation`; `sub_4386D0` writes `arg2`. |
| `data_5860cc` | `sceneSaturationUniform` | High | `sub_4380F0` resolves `p_scenesaturation`; `sub_4386D0` writes `arg4`. |
| `data_5860d0` | `bloomIntensityUniform` | High | `sub_4380F0` resolves `p_bloomintensity`; `sub_4386D0` writes `arg3`. |
| `data_5860d4` | `sceneIntensityUniform` | High | `sub_4380F0` resolves `p_sceneintensity`; `sub_4386D0` writes `arg5`. |

## Verification

Added or tightened parity guards in:

- `tests/test_renderer_post_process_parity.py`
- `tests/test_renderer_internal_helper_mapping_parity.py`

Focused verification:

- `python -m pytest tests/test_renderer_post_process_parity.py tests/test_renderer_internal_helper_mapping_parity.py tests/test_renderer_export_tail_parity.py tests/test_renderer_full_parity_gate.py -q --tb=short`
  - Result: `38 passed, 1 skipped`.
- `python -m pytest tests/test_engine_client_command_parity.py::test_postprocess_restart_routes_through_renderer_export_not_renderer_cmd_registration -q --tb=short`
  - Result: `1 passed`.
- `python -m pytest tests/test_engine_cvar_retail_parity.py::test_engine_cvar_thirtysecond_renderer_bloom_picmip_tranche_matches_retail_contracts -q --tb=short`
  - Result: `1 passed`.
- `git diff --check`
  - Result: pass; only repository LF-to-CRLF conversion warnings.

Post-process bloom uniform naming lane: before 99%, after 99.5%.
