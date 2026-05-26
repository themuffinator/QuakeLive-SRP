# quakelive_steam.exe Mapping Round 321

Date: 2026-05-26

Scope: shader color-correct uniform refresh helper and related draw-pass wiring.

## Summary

Previous post-process passes reconstructed the command ABI, bloom private tail,
and bloom uniform slot order. This pass closes the adjacent color-correct
uniform refresh helper that was already promoted in the alias ledger but still
folded into the source draw pass.

Observed facts:

- `sub_43CD60` is a standalone helper guarded by `sub_43CCE0`.
- It binds the color-correct program at `data_586220`.
- It writes:
  - `data_586224` / `p_gammaRecip`
  - `data_586228` / `p_overbright`
  - `data_58622c` / `p_contrast`
- `sub_43CFE0` performs the same initial uniform writes after loading
  `scripts/colorcorrect.fs` and before creating the color-correct texture.
- `sub_436DC0`, the color-correct backend command handler, consumes the
  command payload and draws the pass without owning the cvar-to-uniform math.

Inferred meaning:

- Color-correct uniform calculation is a helper-level concern, separate from
  framebuffer copy and full-screen draw execution.
- The source command handler may refresh the uniforms immediately before draw
  to preserve retail live-cvar behavior under the reconstructed threaded command
  path, but the write logic should live in the recovered helper family.

## Source Reconstruction

`tr_backend.c` now separates:

- `RBPP_SetColorCorrectUniforms`, the low-level writer used during
  color-correct program initialization.
- `RBPP_SetColorCorrectUniformsFromCvars`, the active-state guarded helper that
  maps `sub_43CD60`.
- `RBPP_ApplyColorCorrectPass`, the backend command body that copies the
  framebuffer and draws the pass.

`RBPP_InitColorCorrectResources` now seeds the program uniforms immediately
after loading the color-correct program, matching the initialization write
sequence in `sub_43CFE0`.

## Evidence Table

| Symbol | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_43CD60` | `RBPP_SetColorCorrectUniformsFromCvars` | High | Guarded by `sub_43CCE0`; writes `p_gammaRecip`, `p_overbright`, and `p_contrast`. |
| `data_586224` | `gammaRecipUniform` | High | Resolved from `p_gammaRecip` in `sub_43CFE0` and written by `sub_43CD60`. |
| `data_586228` | `overbrightUniform` | High | Resolved from `p_overbright` in `sub_43CFE0` and written by `sub_43CD60`. |
| `data_58622c` | `contrastUniform` | High | Resolved from `p_contrast` in `sub_43CFE0` and written by `sub_43CD60`. |

## Verification

Added or tightened parity guards in:

- `tests/test_renderer_post_process_parity.py`
- `tests/test_renderer_internal_helper_mapping_parity.py`

Focused verification:

- `python -m pytest tests/test_renderer_post_process_parity.py tests/test_renderer_internal_helper_mapping_parity.py tests/test_renderer_export_tail_parity.py tests/test_renderer_full_parity_gate.py -q --tb=short`
  - Result: `39 passed, 1 skipped`.
- `python -m pytest tests/test_engine_client_command_parity.py::test_postprocess_restart_routes_through_renderer_export_not_renderer_cmd_registration -q --tb=short`
  - Result: `1 passed`.
- `python -m pytest tests/test_engine_cvar_retail_parity.py::test_engine_cvar_fortysecond_renderer_postprocess_state_tranche_matches_retail_contracts tests/test_engine_cvar_retail_parity.py::test_engine_cvar_twentyninth_renderer_postprocess_extension_tranche_matches_retail_contracts -q --tb=short`
  - Result: `2 passed`.
- `git diff --check`
  - Result: pass; only repository LF-to-CRLF conversion warnings.

Post-process color-correct uniform helper lane: before 99.5%, after 99.7%.
