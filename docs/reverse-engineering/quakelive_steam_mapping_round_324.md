# quakelive_steam.exe Mapping Round 324

Date: 2026-05-26

Scope: post-process framebuffer ownership and legacy scratch-lane retirement.

## Summary

The post-process pipeline now has one framebuffer owner in source:
`RBPP_CreateRenderTarget`, the rectangle-texture helper mapped to retail
`sub_4500B0`. The older compatibility reconstruction in `tr_backend.c`
allocated a separate `GL_TEXTURE_2D` scene target through `RB_CreateRenderTarget`
and carried fixed-function scratch-bloom helpers, but that family had no live
retail command path after the shader-backed post-process reconstruction.

Observed facts:

- Retail `sub_4500B0` creates post-process render targets with
  `GL_TEXTURE_RECTANGLE_ARB`.
- Retail attaches the color texture to `GL_COLOR_ATTACHMENT0_EXT`.
- Retail uses shared depth-stencil renderbuffer storage and attaches it to both
  `GL_DEPTH_ATTACHMENT_EXT` and `GL_STENCIL_ATTACHMENT_EXT`.
- Retail `sub_438790` binds the bloom-owned scene framebuffer, and
  `sub_4387D0` restores framebuffer `0`.
- The committed source already routes draw-surface capture, bloom pass,
  screenshot readback, and command ID `0x0b` through the `RBPP_*` scene-target
  helpers.

Inferred meaning:

- The legacy `RB_CreateRenderTarget` / `RB_DestroyRenderTarget` pair was a
  source-side compatibility duplicate, not an independent retail owner.
- The scratch texture bloom helpers were superseded by the recovered shader
  chain using `brightpass`, `downsample1`, `blurvertical`, `blurhoriz`, and
  `combine`.
- End-of-frame release and queued reset handling should call the recovered
  `RBPP_*` helpers directly.

## Source Reconstruction

`tr_backend.c` now retires the disconnected helper family:

- removed `glFramebufferProcs_t`, `renderTarget_t`, `s_fboProcs`, and
  `s_sceneRenderTarget`;
- removed the unused `RB_LoadFramebufferProcs`, `RB_CreateRenderTarget`,
  `RB_DestroyRenderTarget`, `RB_ReleaseOffscreenRenderTarget`, and
  `RB_ResetPostProcessState` wrappers;
- removed the fixed-function scratch-bloom helpers
  `RB_ApplyColorCorrection`, `RB_UploadBloomScratch`,
  `RB_ConfigureBloomStage`, `RB_DrawBloomSpread`, and `RB_DrawBloomPass`;
- kept `RB_GetFramebufferProc` because `RBPP_LoadProcs` still uses it to
  resolve the retail framebuffer and shader entry points;
- wired `RB_SwapBuffers` directly to `RBPP_ReleaseSceneRenderTarget`;
- wired `RB_ExecuteRenderCommands` directly to `RBPP_ResetIfNeeded`.

This leaves the framebuffer allocation path aligned with the retail
rectangle-texture render-target lane instead of carrying two competing source
models.

## Evidence Table

| Symbol | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_437E40` | `RBPP_CreateBloomRenderTargets` | High | HLIL calls `sub_4500B0` repeatedly to allocate the full, half, and optional quarter bloom target chain. |
| `sub_438790` | `RBPP_BindSceneRenderTarget` | High | HLIL binds `data_585F98` through `glBindFramebufferEXT(0x8D40, result)`. |
| `sub_4387D0` | `RBPP_ReleaseSceneRenderTarget` | High | HLIL calls `glBindFramebufferEXT(0x8D40, 0)`. |
| `sub_4500B0` | `RBPP_CreateRenderTarget` | High | HLIL creates a `GL_TEXTURE_RECTANGLE_ARB` texture, attaches it to the FBO, and attaches the same renderbuffer to depth and stencil. |

## Verification

Added parity guards in:

- `tests/test_renderer_post_process_parity.py`
- `tests/test_renderer_internal_helper_mapping_parity.py`

Focused verification:

- `python -m pytest tests/test_renderer_post_process_parity.py tests/test_renderer_internal_helper_mapping_parity.py tests/test_renderer_export_tail_parity.py tests/test_renderer_full_parity_gate.py -q --tb=short`
  - Result: `42 passed, 1 skipped`.
- `python -m pytest tests/test_engine_cvar_retail_parity.py::test_engine_cvar_fortysecond_renderer_postprocess_state_tranche_matches_retail_contracts tests/test_engine_cvar_retail_parity.py::test_engine_cvar_twentyninth_renderer_postprocess_extension_tranche_matches_retail_contracts tests/test_engine_cvar_retail_parity.py::test_engine_cvar_thirtysecond_renderer_bloom_picmip_tranche_matches_retail_contracts -q --tb=short`
  - Result: `3 passed`.
- `python -m pytest tests/test_engine_client_command_parity.py::test_postprocess_restart_routes_through_renderer_export_not_renderer_cmd_registration -q --tb=short`
  - Result: `1 passed`.
- `git diff --check`
  - Result: pass; only repository LF-to-CRLF conversion warnings.

Post-process framebuffer owner lane: before 99.9%, after 99.93%.
