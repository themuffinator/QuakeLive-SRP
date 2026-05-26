# quakelive_steam.exe Mapping Round 327

Date: 2026-05-26

Scope: post-process GL error propagation, framebuffer attachment wiring, and
post-effect program link ownership.

## Summary

Round 326 restored the retail depth-stencil renderbuffer cache used by
post-process render targets. This pass follows the adjacent error and program
link helpers that `sub_4500B0` and `sub_450640` rely on.

Observed facts:

- Retail `sub_447E40` returns `0` when `glGetError` reports no error or when
  `r_ignoreGLErrors` is active. It reports `GL_CheckErrors: %s` and returns
  `1` on an unignored GL error path.
- Retail `sub_4500B0` calls `sub_447E40` immediately after rectangle texture
  storage and again after successful framebuffer status verification.
- After `sub_44FFD0` has created or found the depth-stencil renderbuffer,
  retail `sub_4500B0` attaches that renderbuffer handle directly to depth and
  stencil without rebinding `GL_RENDERBUFFER_EXT` in the target creation
  helper.
- Retail `sub_4505F0` creates a post-effect program object, attaches the
  fragment and vertex shader objects when present, links the program, and uses
  `sub_447E40` as the link success gate.
- Retail `sub_450640` delegates the final link step to `sub_4505F0` after the
  fragment and vertex compile/load helpers succeed.

Inferred meaning:

- `GL_CheckErrors` is a return-valued helper in the retail renderer. Existing
  call sites may ignore the return, but post-process creation and link paths
  branch on it.
- Renderbuffer binding belongs to the cache helper, while framebuffer target
  creation only consumes the cached handle for depth/stencil attachment.
- Link failure handling is GL-error driven in the retail post-effect lane; the
  source-only explicit link-status query was more defensive than the recovered
  retail code.

## Source Reconstruction

The renderer source now follows the recovered retail wiring:

- `GL_CheckErrors` returns `qboolean`: `qfalse` for no/ignored error and
  `qtrue` after the unignored fatal error path.
- `RBPP_CreateRenderTarget` uses `GL_CheckErrors()` after rectangle texture
  allocation and after framebuffer completeness, and no longer performs local
  `qglGetError()` checks in that helper.
- `RBPP_CreateRenderTarget` no longer binds `GL_RENDERBUFFER_EXT` while
  attaching depth/stencil storage; it directly attaches the cached
  renderbuffer handle.
- Added `RBPP_LinkProgram` for retail `sub_4505F0`, with create, attach,
  link, and `GL_CheckErrors`-gated success.
- `RBPP_LoadProgram` now delegates final link ownership to
  `RBPP_LinkProgram` and drops the source-only `GL_OBJECT_LINK_STATUS_ARB`
  query.
- `RBPP_CreateColorCorrectTexture` also uses `GL_CheckErrors()` for its
  rectangle texture allocation check.

## Evidence Table

| Symbol | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_447E40` | `GL_CheckErrors` | High | HLIL calls `glGetError`, returns `0` for no/ignored errors, formats the known GL error strings, reports `GL_CheckErrors: %s`, and returns `1` on the reported path. |
| `sub_4500B0` | `RBPP_CreateRenderTarget` | High | HLIL calls `sub_447E40` after texture allocation and after complete framebuffer status, and attaches the renderbuffer handle without a renderbuffer bind in this helper. |
| `sub_4505F0` | `RBPP_LinkProgram` | High | HLIL creates the program object, conditionally attaches fragment and vertex shader objects, links, and returns success from the inverted `sub_447E40` result. |
| `sub_450640` | `RBPP_LoadProgram` | High | HLIL calls the fragment and vertex setup helpers before delegating to `sub_4505F0` for the final link step. |

## Verification

Added parity guards in:

- `tests/test_renderer_internal_helper_mapping_parity.py`
- `tests/test_renderer_post_process_parity.py`

Focused verification:

- `python -m pytest tests/test_renderer_post_process_parity.py tests/test_renderer_internal_helper_mapping_parity.py tests/test_renderer_export_tail_parity.py tests/test_renderer_full_parity_gate.py -q --tb=short`
  - Result: `45 passed, 1 skipped`.
- `python -m pytest tests/test_engine_cvar_retail_parity.py::test_engine_cvar_fortysecond_renderer_postprocess_state_tranche_matches_retail_contracts tests/test_engine_cvar_retail_parity.py::test_engine_cvar_twentyninth_renderer_postprocess_extension_tranche_matches_retail_contracts tests/test_engine_cvar_retail_parity.py::test_engine_cvar_thirtysecond_renderer_bloom_picmip_tranche_matches_retail_contracts -q --tb=short`
  - Result: `3 passed`.
- `python -m pytest tests/test_engine_client_command_parity.py::test_postprocess_restart_routes_through_renderer_export_not_renderer_cmd_registration -q --tb=short`
  - Result: `1 passed`.
- `git diff --check`
  - Result: pass; only repository LF-to-CRLF conversion warnings.

Post-process GL error and link lane: before 99.97%, after 99.985%.
