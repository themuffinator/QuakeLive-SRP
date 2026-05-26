# quakelive_steam.exe Mapping Round 319

Date: 2026-05-26

Scope: post-process private refexport tail slots and bloom uniform setter wiring.

## Summary

Round 318 reconstructed the post-process backend command ABI. This pass closes
the adjacent private-tail wiring by adding the missing no-argument bloom command
slot and the five-float bloom uniform setter slot.

Observed facts:

- `GetRefAPI` (`sub_449F70`) clears `0x9c` bytes for the retail refresh export
  table.
- The post-`inPVS` tail assignments are ordered as:
  - `data_5878c0 = j_sub_43CBA0`
  - `data_5878c4 = j_sub_4384D0`
  - `data_5878c8 = sub_449F10`
  - `data_5878cc = sub_451420`
- `sub_451420` sets `data_1740d08 = 1` and forwards five floats to
  `sub_4386D0`.
- `sub_4386D0` writes the bright-pass threshold uniform and the four combine
  uniforms in the order bloom saturation, scene intensity, bloom intensity, and
  scene saturation.
- `sub_436EC0` checks `data_1740d08` after the bloom pass, calls
  `sub_438590`, and clears the dirty flag.
- `sub_438590` refreshes those same bloom uniforms from the cvar lane and
  clamps negative values to zero.

Inferred meaning:

- The retail private tail has a distinct bloom command emitter slot between
  scene capture and restart.
- `sub_451420` is not a render-command emitter; it is a temporary uniform
  setter whose dirty flag causes the next bloom command to restore cvar-owned
  uniform values.

## Source Reconstruction

`refexport_t` now includes `RetailBloomPostProcessCommand` between
`RetailPostProcessCapture` and `PostProcessRestart`, preserving the observed
retail tail order.

`GetRefAPI` now assigns:

- `re.RetailPostProcessCapture = R_AddBindSceneRenderTargetCommand`
- `re.RetailBloomPostProcessCommand = R_AddBloomPostProcessCommand`
- `re.PostProcessRestart = R_PostProcessRestart`
- `re.RetailPostProcessPass = R_SetPostProcessBloomParameters`

`tr_backend.c` now reconstructs the bloom uniform helper family:

- `RBPP_SetBloomUniforms` maps `sub_4386D0`.
- `RBPP_SetBloomUniformsFromCvars` maps `sub_438590`.
- `R_SetPostProcessBloomParameters` maps `sub_451420`.

The source dirty flag `s_bloomUniformsDirty` mirrors the observed
`data_1740d08` behavior: `R_SetPostProcessBloomParameters` marks temporary
uniform ownership dirty, and `RB_BloomPostProcessCommand` restores cvar values
after the bloom command.

## Evidence Table

| Symbol | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_4384D0` | `R_AddBloomPostProcessCommand` | High | Installed at `data_5878c4`, directly after the scene-target capture command tail slot. |
| `sub_4386D0` | `RBPP_SetBloomUniforms` | High | Writes the bright-pass threshold and four combine uniforms from five float arguments. |
| `sub_438590` | `RBPP_SetBloomUniformsFromCvars` | High | Reads bloom cvars, clamps negative values, and writes the same uniform family. |
| `sub_451420` | `R_SetPostProcessBloomParameters` | High | Sets the dirty flag and tailcalls `sub_4386D0` with five floats. |

## Verification

Added parity guards in:

- `tests/test_renderer_export_tail_parity.py`
- `tests/test_renderer_post_process_parity.py`
- `tests/test_renderer_internal_helper_mapping_parity.py`
- `tests/test_renderer_full_parity_gate.py`

Focused verification:

- `python -m pytest tests/test_renderer_post_process_parity.py tests/test_renderer_internal_helper_mapping_parity.py tests/test_renderer_export_tail_parity.py tests/test_renderer_full_parity_gate.py -q --tb=short`
  - Result: `37 passed, 1 skipped`.
- `python -m pytest tests/test_engine_client_command_parity.py::test_postprocess_restart_routes_through_renderer_export_not_renderer_cmd_registration -q --tb=short`
  - Result: `1 passed`.
- `git diff --check`
  - Result: pass; only repository LF-to-CRLF conversion warnings.

Post-process private-tail lane: before 96%, after 99%.
