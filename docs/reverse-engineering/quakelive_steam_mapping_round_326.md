# quakelive_steam.exe Mapping Round 326

Date: 2026-05-26

Scope: post-process depth-stencil renderbuffer cache and render-target wiring.

## Summary

Round 325 matched the grouped bloom teardown order. This pass closes the
allocation-side gap by reconstructing retail `sub_44FFD0`, the small
depth-stencil renderbuffer cache used by `sub_4500B0` before rectangle texture
and framebuffer creation.

Observed facts:

- Retail `sub_44FFD0` exits unless the selected pixel format has at least
  24 depth bits.
- The helper searches an eight-entry table keyed by width and height and
  returns an existing renderbuffer when dimensions match.
- On a cache miss, retail creates a renderbuffer, binds
  `GL_RENDERBUFFER_EXT`, allocates `GL_DEPTH24_STENCIL8_EXT`, checks
  `glGetError`, unbinds the renderbuffer, and stores width, height, and handle
  in the cache.
- Retail `sub_4500B0` calls `sub_44FFD0` before texture creation. If the
  helper returns less than one, it prints the developer diagnostic
  `Unable to create render buffer object.` and aborts target creation.
- Retail `sub_450710` and `sub_450780` clear the renderbuffer cache storage
  and reset the cache count before rebuilding or shutting down post-process
  resources.

Inferred meaning:

- Bloom targets of the same dimensions reuse the same packed depth-stencil
  renderbuffer instead of allocating one renderbuffer per target.
- The cache belongs to the post-process resource lifetime, not to a single
  `ppRenderTarget_t`.
- Source teardown can preserve the existing grouped target handle deletion
  while also clearing the reconstructed cache metadata after those handles are
  released.

## Source Reconstruction

`tr_backend.c` now mirrors the retail allocation lane:

- Added an eight-entry `ppRenderbufferCacheEntry_t` table to `ppState_t`.
- Promoted `sub_44FFD0` as `RBPP_CreateDepthStencilRenderbuffer`.
- `RBPP_CreateRenderTarget` now obtains `target->depthBuffer` from the cache
  helper before creating the rectangle texture and framebuffer.
- The render-target creation order now follows the retail sequence more
  closely: depth-stencil renderbuffer, rectangle texture upload and sampler
  state, texture unbind, framebuffer creation, then color/depth/stencil
  attachment.
- `RBPP_ShutdownBloomResources` clears the renderbuffer cache table and count
  after releasing the grouped bloom target handles.

## Evidence Table

| Symbol | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_44FFD0` | `RBPP_CreateDepthStencilRenderbuffer` | High | HLIL checks `data_1743bac >= 0x18`, searches the width/height cache, allocates `GL_DEPTH24_STENCIL8_EXT`, checks `glGetError`, and stores width, height, and renderbuffer handle in the eight-entry cache. |
| `sub_4500B0` | `RBPP_CreateRenderTarget` | High | HLIL calls `sub_44FFD0` before texture creation, aborts with the renderbuffer diagnostic when it fails, then attaches the returned handle to depth and stencil framebuffer attachments. |
| `sub_450710` | `RBPP_RebuildState` | High | HLIL clears `data_1716e20` and resets `data_5881e8` before post-process rebuild. |
| `sub_450780` | `RBPP_Shutdown` | High | HLIL clears `data_1716e20` and resets `data_5881e8` on post-process shutdown. |

## Verification

Added parity guards in:

- `tests/test_renderer_internal_helper_mapping_parity.py`

Focused verification:

- `python -m pytest tests/test_renderer_post_process_parity.py tests/test_renderer_internal_helper_mapping_parity.py tests/test_renderer_export_tail_parity.py tests/test_renderer_full_parity_gate.py -q --tb=short`
  - Result: `44 passed, 1 skipped`.
- `python -m pytest tests/test_engine_cvar_retail_parity.py::test_engine_cvar_fortysecond_renderer_postprocess_state_tranche_matches_retail_contracts tests/test_engine_cvar_retail_parity.py::test_engine_cvar_twentyninth_renderer_postprocess_extension_tranche_matches_retail_contracts tests/test_engine_cvar_retail_parity.py::test_engine_cvar_thirtysecond_renderer_bloom_picmip_tranche_matches_retail_contracts -q --tb=short`
  - Result: `3 passed`.
- `python -m pytest tests/test_engine_client_command_parity.py::test_postprocess_restart_routes_through_renderer_export_not_renderer_cmd_registration -q --tb=short`
  - Result: `1 passed`.
- `git diff --check`
  - Result: pass; only repository LF-to-CRLF conversion warnings.

Post-process depth-stencil renderbuffer cache lane: before 99.95%, after 99.97%.
