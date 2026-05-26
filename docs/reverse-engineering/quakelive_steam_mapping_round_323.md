# quakelive_steam.exe Mapping Round 323

Date: 2026-05-26

Scope: color-correct uniform seeding versus live browser-active override.

## Summary

Round 321 split the recovered color-correct uniform writer out of the draw pass,
and round 322 wired the live `RE_BeginFrame` refresh branch. This pass closes a
small but important ownership difference between the init helper and the live
helper.

Observed facts:

- Retail `sub_43CD60`, the live color-correct uniform refresh helper, checks
  `data_15ee390`, the runtime browser-active state.
- When that browser state is active, `sub_43CD60` forces gamma reciprocal and
  contrast back to `1.0`, while still applying the overbright uniform.
- Retail `sub_43CFE0`, the color-correct init helper, does not check
  `data_15ee390`.
- `sub_43CFE0` seeds `p_gammaRecip`, `p_overbright`, and `p_contrast` directly
  from `r_gamma`, `r_overBrightBits`, and `r_contrast` before creating the
  color-correct rectangle texture.

Inferred meaning:

- Browser-active suppression is a live-frame refresh behavior, not part of the
  initial program uniform seed.
- The source can share one low-level writer only if the caller chooses whether
  to honor the browser-active override.

## Source Reconstruction

`RBPP_SetColorCorrectUniforms` now takes a `browserOverride` flag:

- `RBPP_InitColorCorrectResources` passes `qfalse`, matching `sub_43CFE0`.
- `RBPP_SetColorCorrectUniformsFromCvars` passes `qtrue`, matching
  `sub_43CD60`.

This keeps the existing uniform writer shared while preserving the two recovered
retail behaviors at their call sites.

## Evidence Table

| Symbol | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_43CD60` | `RBPP_SetColorCorrectUniformsFromCvars` | High | Live helper checks `data_15ee390` and suppresses gamma/contrast while browser rendering is active. |
| `sub_43CFE0` | `RBPP_InitColorCorrectResources` | High | Init helper seeds the same uniforms from cvars without the browser-active branch. |
| `data_15ee390` | browser-active runtime state | Medium-high | Updated by the browser activation path and read by the live color-correct helper; source mirrors through `web_browserActive`. |

## Verification

Added or tightened parity guards in:

- `tests/test_renderer_post_process_parity.py`
- `tests/test_renderer_internal_helper_mapping_parity.py`
- `tests/test_engine_cvar_retail_parity.py`

Focused verification:

- `python -m pytest tests/test_renderer_post_process_parity.py tests/test_renderer_internal_helper_mapping_parity.py tests/test_renderer_export_tail_parity.py tests/test_renderer_full_parity_gate.py -q --tb=short`
  - Result: `41 passed, 1 skipped`.
- `python -m pytest tests/test_engine_cvar_retail_parity.py::test_engine_cvar_fortysecond_renderer_postprocess_state_tranche_matches_retail_contracts tests/test_engine_cvar_retail_parity.py::test_engine_cvar_twentyninth_renderer_postprocess_extension_tranche_matches_retail_contracts tests/test_engine_cvar_retail_parity.py::test_engine_cvar_thirtysecond_renderer_bloom_picmip_tranche_matches_retail_contracts -q --tb=short`
  - Result: `3 passed`.
- `python -m pytest tests/test_engine_cvar_retail_parity.py::test_engine_cvar_twentythird_renderer_runtime_tuning_tranche_matches_retail_contracts tests/test_engine_cvar_retail_parity.py::test_engine_cvar_thirtyeighth_renderer_image_quality_tranche_matches_retail_contracts -q --tb=short`
  - Result: `2 passed`.
- `python -m pytest tests/test_engine_client_command_parity.py::test_postprocess_restart_routes_through_renderer_export_not_renderer_cmd_registration -q --tb=short`
  - Result: `1 passed`.
- `git diff --check`
  - Result: pass; only repository LF-to-CRLF conversion warnings.

Post-process color-correct browser override lane: before 99.85%, after 99.9%.
