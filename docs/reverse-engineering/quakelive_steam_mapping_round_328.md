# quakelive_steam.exe Mapping Round 328

Date: 2026-05-26

Scope: post-process framebuffer procedure gates versus shader procedure gates.

## Summary

Round 327 restored the return-valued GL error helper and post-effect link
helper. This pass closes the adjacent loader split: retail render-target
creation only gates on framebuffer/renderbuffer/rectangle-texture procedures,
while shader object and uniform procedures are required by the program loading
lane.

Observed facts:

- Retail `sub_4500B0` starts with a compact null-check over the framebuffer,
  renderbuffer, rectangle texture, and framebuffer attachment/status function
  pointers.
- The `sub_4500B0` prerequisite list does not include shader object,
  program-object, or uniform-location procedures.
- Retail `sub_450640` is the program loading owner. It checks the broad
  post-process/shader support flags, calls the fragment and vertex setup
  helpers, and delegates final link ownership to `sub_4505F0`.
- Retail framebuffer target creation therefore has a narrower procedure gate
  than the full shader-backed post-effect program path.

Inferred meaning:

- The source should keep framebuffer target creation independent from shader
  procedure availability. That preserves the retail ownership split and keeps
  render-target helpers from depending on later shader/uniform setup details.
- The full post-process active state still requires both the framebuffer lane
  and the shader lane; the split is about helper ownership and failure
  boundaries, not enabling a shaderless retail effect.

## Source Reconstruction

`tr_backend.c` now separates those gates:

- Added `RBPP_LoadFramebufferProcs`, which loads and validates only
  `GL_EXT_framebuffer_object`, `GL_ARB_texture_rectangle`, the FBO/renderbuffer
  entry points, and `GL_MAX_RECTANGLE_TEXTURE_SIZE_ARB`.
- Added `framebufferProcsLoaded` and `framebufferSupported` state so the
  framebuffer-only lane can cache its result independently.
- `RBPP_CreateRenderTarget` now calls `RBPP_LoadFramebufferProcs` rather than
  the full shader procedure loader.
- `RBPP_LoadProcs` now delegates to `RBPP_LoadFramebufferProcs` first, then
  checks and loads `GL_ARB_shader_objects`, `GL_ARB_vertex_shader`,
  `GL_ARB_fragment_shader`, program-object, shader-object, and uniform
  procedures.
- `RBPP_LoadProgram` remains on the full `RBPP_LoadProcs` gate.

## Evidence Table

| Symbol | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_4500B0` | `RBPP_CreateRenderTarget` | High | HLIL null-checks the framebuffer/renderbuffer/rectangle-texture procedure set before creating renderbuffers, rectangle textures, and FBO attachments; shader procedure pointers are absent from this prerequisite list. |
| `sub_450640` | `RBPP_LoadProgram` | High | HLIL checks the broad post-process/shader support flags, then calls the fragment, vertex, and link helpers for program setup. |

## Verification

Added parity guards in:

- `tests/test_renderer_internal_helper_mapping_parity.py`

Focused verification:

- `python -m pytest tests/test_renderer_post_process_parity.py tests/test_renderer_internal_helper_mapping_parity.py tests/test_renderer_export_tail_parity.py tests/test_renderer_full_parity_gate.py -q --tb=short`
  - Result: `46 passed, 1 skipped`.
- `python -m pytest tests/test_engine_cvar_retail_parity.py::test_engine_cvar_fortysecond_renderer_postprocess_state_tranche_matches_retail_contracts tests/test_engine_cvar_retail_parity.py::test_engine_cvar_twentyninth_renderer_postprocess_extension_tranche_matches_retail_contracts tests/test_engine_cvar_retail_parity.py::test_engine_cvar_thirtysecond_renderer_bloom_picmip_tranche_matches_retail_contracts -q --tb=short`
  - Result: `3 passed`.
- `python -m pytest tests/test_engine_client_command_parity.py::test_postprocess_restart_routes_through_renderer_export_not_renderer_cmd_registration -q --tb=short`
  - Result: `1 passed`.
- `git diff --check`
  - Result: pass; only repository LF-to-CRLF conversion warnings.

Post-process proc gate lane: before 99.985%, after 99.99%.
