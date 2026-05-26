# quakelive_steam.exe Mapping Round 318

Date: 2026-05-26

Scope: retail post-process backend command ABI, emitters, executor cases, and
refexport capture wiring.

## Summary

This pass extends Rounds 316 and 317 from resource ownership into the command
buffer layer. The retail renderer does not run bloom and color correction as a
hidden side effect of `RB_SwapBuffers`; it queues explicit backend commands and
then executes them before the swap command.

Observed facts:

- `sub_43CD10` allocates `0x10` command bytes, writes command ID `9`, then
  stores the color-correct texture and program handles at offsets `+4` and
  `+8`.
- `sub_4384D0` allocates `0x38` command bytes, writes command ID `0xa`, then
  stores eight bloom texture / target handles and five program handles through
  offset `+0x34`.
- `sub_43CBA0` allocates a four-byte command and writes command ID `0xb`.
- `sub_437A50` dispatches command IDs `9`, `10`, and `11` to the
  color-correct handler, bloom handler, and scene-target binder respectively.
- `sub_436DC0` advances by `0x10`; `sub_436EC0` advances by `0x38`. They are
  command handlers, with the pass-specific drawing now factored into source
  helpers.
- `RE_EndFrame` (`sub_43CAC0`) calls the color-correct emitter before queuing
  the swap command.
- The private refexport tail installs `j_sub_43CBA0` at `data_5878c0` and
  `j_sub_4384D0` at `data_5878c4`.

Inferred meaning:

- Command IDs `9`, `10`, and `11` are the stable post-process command ABI lane.
- Command ID `8` remains reserved in this source reconstruction so that the
  post-process command values line up with retail.
- The source can keep strongly typed post-process pass helpers while mapping
  `sub_436DC0` and `sub_436EC0` to command-handler wrappers.

## Source Reconstruction

`tr_local.h` now defines the recovered command payloads:

- `colorCorrectPostProcessCommand_t` is `0x10` bytes on the x86 GL handle ABI:
  command ID, color-correct texture, color-correct program, and padding.
- `bloomPostProcessCommand_t` is `0x38` bytes: command ID, eight texture /
  target handles, and five program handles.
- `bindSceneRenderTargetCommand_t` is the four-byte command ID `0x0b`.

The enum now preserves the retail post-process command numbers by inserting the
reserved `RC_SUB_IMAGE` slot before the advertisement command and then adding:

- `RC_COLOR_CORRECT_POST_PROCESS`
- `RC_BLOOM_POST_PROCESS`
- `RC_BIND_SCENE_RENDER_TARGET`

`tr_backend.c` now reconstructs both sides of the lane:

- Frontend emitters:
  - `R_AddBindSceneRenderTargetCommand`
  - `R_AddBloomPostProcessCommand`
  - `R_AddColorCorrectPostProcessCommand`
- Backend handlers:
  - `RB_BindSceneRenderTargetCommand`
  - `RB_BloomPostProcessCommand`
  - `RB_ColorCorrectPostProcessCommand`

`R_AddDrawSurfCmd` queues the scene-target bind command before each draw-surface
command, matching the retail backend command path instead of binding directly in
`RB_RenderDrawSurfList`. `RE_EndFrame` queues bloom and color-correct commands
before `RC_SWAP_BUFFERS`; `RB_SwapBuffers` no longer owns the post-process pass
as a hidden side effect.

`FixRenderCommandList` now advances across the new command payloads so shader
registration during a frame does not desynchronize the command walk.

The private refexport capture slot now points at
`R_AddBindSceneRenderTargetCommand`, matching the retail `data_5878c0`
assignment. The adjacent bloom tail slot remains documented by the ABI evidence,
but the current public struct does not yet expose a distinct no-argument bloom
slot without reworking the existing private-tail layout.

## Evidence Table

| Symbol | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_436DC0` | `RB_ColorCorrectPostProcessCommand` | High | HLIL copies from the framebuffer, binds the color-correct program, draws a full-screen quad, and returns `arg1 + 0x10`. |
| `sub_436EC0` | `RB_BloomPostProcessCommand` | High | HLIL consumes the `0x38` bloom payload, runs the downsample / bright-pass / blur / combine chain, and returns `arg1 + 0x38`. |
| `sub_4384D0` | `R_AddBloomPostProcessCommand` | High | HLIL gates on post-process support, allocates `0x38`, writes command ID `0xa`, and stores target / program handles. |
| `sub_43CBA0` | `R_AddBindSceneRenderTargetCommand` | High | HLIL allocates four bytes and writes command ID `0xb`; the executor checks `sub_4384A0` before binding. |
| `sub_43CD10` | `R_AddColorCorrectPostProcessCommand` | High | HLIL gates on post-process support, allocates `0x10`, writes command ID `9`, and stores texture / program handles. |

## Verification

Added parity guards in:

- `tests/test_renderer_post_process_parity.py`
- `tests/test_renderer_internal_helper_mapping_parity.py`

Focused validation:

- `python -m pytest tests/test_renderer_post_process_parity.py tests/test_renderer_internal_helper_mapping_parity.py tests/test_renderer_export_tail_parity.py tests/test_renderer_full_parity_gate.py -q --tb=short`
  passed: `35 passed, 1 skipped`.
- `python -m pytest tests/test_engine_client_command_parity.py::test_postprocess_restart_routes_through_renderer_export_not_renderer_cmd_registration -q --tb=short`
  passed: `1 passed`.
- `git diff --check` completed without whitespace errors; Git reported only
  line-ending normalization warnings for modified text files.

Post-process command ABI lane: before 88%, after 96%.

Round 319 follows this pass by closing the exact private-tail layout for the
no-argument bloom emitter slot at `data_5878c4`.
