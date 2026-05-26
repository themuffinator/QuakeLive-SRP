# quakelive_steam.exe Mapping Round 325

Date: 2026-05-26

Scope: bloom framebuffer teardown ordering and post-process program cleanup.

## Summary

Round 324 collapsed the source onto the retail rectangle-texture framebuffer
owner. This pass tightens the corresponding shutdown side by matching the
retail lifetime order in `sub_437DA0` and the shader-program destruction shape
in `sub_4506A0`.

Observed facts:

- Retail `sub_437DA0` first walks the bloom program range and calls
  `sub_4506A0` for each program record.
- The same helper then deletes all bloom rectangle textures from the texture
  handle array, then all framebuffers from the framebuffer array, then all
  renderbuffers from the depth-stencil renderbuffer array.
- Retail clears each handle slot after deleting it.
- Retail ends the helper by setting `r_bloomActive` to `0`.
- Retail `sub_4506A0` detaches fragment and vertex shader objects from the
  linked program before deleting the program and shader objects.

Inferred meaning:

- Bloom target shutdown is grouped by GL object kind, not target-by-target.
- Program cleanup should detach shader objects before deleting the linked
  program object.
- The source can preserve the `ppRenderTarget_t` struct representation while
  still following the retail grouped delete order.

## Source Reconstruction

`tr_backend.c` now mirrors the retail teardown lane more closely:

- `RBPP_DestroyBloomPrograms` destroys the bloom programs in retail memory
  order: brightpass, downsample, blurvertical, blurhoriz, combine.
- `RBPP_ShutdownBloomResources` builds the eight bloom target pointers in
  retail target order and performs three deletion passes: textures,
  framebuffers, then depth-stencil renderbuffers.
- Each target slot is cleared after the grouped delete passes.
- `RBPP_ShutdownBloomResources` clears `r_bloomActive` directly when the cvar
  exists, matching the retail shutdown helper's final mirror update.
- `RBPP_DestroyProgram` now resolves and uses `glDetachObjectARB` so shader
  objects are detached before the linked program is deleted.
- `RBPP_DestroyRenderTarget` was adjusted to use the same texture ->
  framebuffer -> renderbuffer order for single-target cleanup paths.

## Evidence Table

| Symbol | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_437DA0` | `RBPP_ShutdownBloomResources` | High | HLIL walks the program records, deletes texture handles, deletes framebuffer handles, deletes renderbuffer handles, and clears `r_bloomActive`. |
| `sub_4506A0` | `RBPP_DestroyProgram` | High | HLIL detaches shader objects from the linked program, deletes the program, deletes shader objects, and clears handles. |

## Verification

Added or tightened parity guards in:

- `tests/test_renderer_post_process_parity.py`
- `tests/test_renderer_internal_helper_mapping_parity.py`

Focused verification:

- `python -m pytest tests/test_renderer_post_process_parity.py tests/test_renderer_internal_helper_mapping_parity.py tests/test_renderer_export_tail_parity.py tests/test_renderer_full_parity_gate.py -q --tb=short`
  - Result: `43 passed, 1 skipped`.
- `python -m pytest tests/test_engine_cvar_retail_parity.py::test_engine_cvar_fortysecond_renderer_postprocess_state_tranche_matches_retail_contracts tests/test_engine_cvar_retail_parity.py::test_engine_cvar_twentyninth_renderer_postprocess_extension_tranche_matches_retail_contracts tests/test_engine_cvar_retail_parity.py::test_engine_cvar_thirtysecond_renderer_bloom_picmip_tranche_matches_retail_contracts -q --tb=short`
  - Result: `3 passed`.
- `python -m pytest tests/test_engine_client_command_parity.py::test_postprocess_restart_routes_through_renderer_export_not_renderer_cmd_registration -q --tb=short`
  - Result: `1 passed`.
- `git diff --check`
  - Result: pass; only repository LF-to-CRLF conversion warnings.

Post-process bloom teardown lane: before 99.93%, after 99.95%.
