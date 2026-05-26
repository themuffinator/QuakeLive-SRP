# quakelive_steam.exe Mapping Round 322

Date: 2026-05-26

Scope: live post-process cvar modified-latch refresh wiring in `RE_BeginFrame`.

## Summary

Previous post-process rounds reconstructed the shader command ABI, private
refexport tail, bloom uniform slot order, and the standalone color-correct
uniform helper. This pass closes the adjacent retail frame-begin wiring that
decides when those helpers run after live cvar edits.

Observed facts:

- Retail `RE_BeginFrame` checks `r_gamma->modified || r_contrast->modified`
  after texture-mode handling.
- That branch clears only `r_contrast->modified`, then calls `sub_43CD60`.
- Retail then checks the five live bloom tuning cvars:
  `r_bloomBrightThreshold`, `r_bloomSaturation`, `r_bloomSceneSaturation`,
  `r_bloomIntensity`, and `r_bloomSceneIntensity`.
- That bloom branch clears all five bloom modified latches, then calls
  `sub_438590`.
- The later gamma branch still sees `r_gamma->modified`, clears it, syncs the
  render thread, and calls `R_SetColorMappings`.

Inferred meaning:

- `R_UpdatePostProcessCvars` should own enable-state clamping, active mirror
  updates, and restart flags, but not consume the live tuning cvar latches.
- `RE_BeginFrame` owns the retail live refresh order: texture mode, live
  color-correct uniforms, live bloom uniforms, then gamma color mappings.
- The source helper boundary needs the two recovered uniform helpers callable
  from the frame-begin owner, while the low-level uniform writers stay private
  to `tr_backend.c`.

## Source Reconstruction

`tr_cmds.c` now adds `R_RefreshLivePostProcessCvars`, matching the retail
modified-latch sequence:

- color-correct refresh watches `r_gamma` and `r_contrast`;
- only `r_contrast` is cleared in that branch;
- bloom refresh watches and clears the five recovered live bloom controls;
- the helper calls `RBPP_SetColorCorrectUniformsFromCvars` and
  `RBPP_SetBloomUniformsFromCvars` in the recovered order.

`tr_init.c` no longer clears the live post-process tuning latches from
`R_UpdatePostProcessCvars`. `tr_local.h` now exposes the two active-state
guarded backend helpers needed by the frame-begin lane.

## Evidence Table

| Symbol | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_43C7B0` | `RE_BeginFrame` | High | HLIL address range `0043c7b0`; Ghidra frame-begin body contains texture-mode, live post-process, gamma, error, and draw-buffer branches. |
| `sub_43CD60` | `RBPP_SetColorCorrectUniformsFromCvars` | High | Called from the `r_gamma || r_contrast` modified-latch branch after clearing only `r_contrast`. |
| `sub_438590` | `RBPP_SetBloomUniformsFromCvars` | High | Called from the five-bloom-cvar modified-latch branch after clearing all five bloom latches. |
| `sub_4475D0(0)` | `R_SetColorMappings` | High | Called only from the later `r_gamma->modified` branch after clearing the gamma latch. |

## Verification

Added or tightened parity guards in:

- `tests/test_renderer_post_process_parity.py`
- `tests/test_renderer_internal_helper_mapping_parity.py`
- `tests/test_engine_cvar_retail_parity.py`

Focused verification:

- `python -m pytest tests/test_renderer_post_process_parity.py tests/test_renderer_internal_helper_mapping_parity.py tests/test_renderer_export_tail_parity.py tests/test_renderer_full_parity_gate.py -q --tb=short`
  - Result: `40 passed, 1 skipped`.
- `python -m pytest tests/test_engine_cvar_retail_parity.py::test_engine_cvar_fortysecond_renderer_postprocess_state_tranche_matches_retail_contracts tests/test_engine_cvar_retail_parity.py::test_engine_cvar_twentyninth_renderer_postprocess_extension_tranche_matches_retail_contracts tests/test_engine_cvar_retail_parity.py::test_engine_cvar_thirtysecond_renderer_bloom_picmip_tranche_matches_retail_contracts -q --tb=short`
  - Result: `3 passed`.
- `python -m pytest tests/test_engine_client_command_parity.py::test_postprocess_restart_routes_through_renderer_export_not_renderer_cmd_registration -q --tb=short`
  - Result: `1 passed`.
- Direct source sentinel for the `test_engine_cvar_fortyfirst_renderer_platform_scene_tranche_matches_retail_contracts` post-process assertions:
  - Result: passed.
- `python -m pytest tests/test_engine_cvar_retail_parity.py::test_engine_cvar_fortyfirst_renderer_platform_scene_tranche_matches_retail_contracts -q --tb=short`
  - Result: failed before the new post-process assertions on an unrelated read-only `src/ui/ui_main.c` `r_inGameVideo` expectation.
- `git diff --check`
  - Result: pass; only repository LF-to-CRLF conversion warnings.

Post-process live cvar refresh lane: before 99.7%, after 99.85%.
