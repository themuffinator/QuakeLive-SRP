# quakelive_steam.exe Mapping Round 317

Date: 2026-05-26

Scope: retail post-process scene-target ownership and bloom/color-correct
wiring in the renderer backend.

## Summary

This pass follows Round 316's direct color-correction predicate reconstruction
with the adjacent bloom predicate and scene framebuffer owner split.

Observed facts:

- `sub_4384A0` returns `1` only when `sub_4507C0` succeeds, the recovered
  shader / rectangle-texture support flag is set, and `r_bloomActive->integer`
  is non-zero.
- Retail screenshot readback helpers call `sub_4384A0` before releasing or
  rebinding the scene framebuffer.
- Retail command ID `0x0b` also checks `sub_4384A0` before rebinding the scene
  framebuffer.
- `sub_4380F0` owns the bloom resource setup and creates the scene render
  target as part of the bloom target chain. Color-correction setup
  (`sub_43CFE0`) is separate and operates on the default framebuffer copy.

Inferred meaning:

- `r_postProcessActive` is the broad shader post-process runtime gate, but the
  offscreen scene target is bloom-owned.
- Color-correct-only frames should not route world rendering through the bloom
  scene framebuffer; they render to the default framebuffer and then run the
  color-correct copy/pass.

## Source Reconstruction

`tr_backend.c` now has a source-level `RBPP_BloomEnabled()` predicate matching
the retail `sub_4384A0` checks:

- `RB_PostProcessEnabled()` for the broad post-process runtime gate.
- `s_postProcess.supported` for the recovered shader / rectangle-texture
  capability flag.
- `r_bloomActive->integer` for the retail ROM/cloud mirror that indicates the
  bloom path is active.

The bloom initializer now creates the full-resolution `sceneTarget` alongside
the downsample, bright-pass, blur, and optional quarter-resolution targets.
The bloom shutdown helper releases that scene target with the rest of the bloom
target chain.

Scene-target binding, screenshot readback release/rebind, and frame submission
now use `RBPP_BloomEnabled()` instead of the broad `RB_PostProcessEnabled()`
gate. This keeps the color-correct-only path on the default framebuffer while
preserving the bloom path's offscreen scene capture.

## Evidence Table

| Symbol | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_4384A0` | `RBPP_BloomEnabled` | High | HLIL shows `sub_4507C0`, shader support, and `r_bloomActive` checks. |
| `sub_4380F0` | `RBPP_InitBloomResources` | High | HLIL creates the scene target and bloom target chain only under `r_enableBloom`. |
| `sub_438790` | `RBPP_BindSceneRenderTarget` | High | HLIL command ID `0x0b` reaches this binder only after `sub_4384A0`. |
| screenshot helpers | `RB_BeginScreenshotReadback` / `RB_EndScreenshotReadback` | High | HLIL releases/rebinds the scene framebuffer only when `sub_4384A0` succeeds. |

## Verification

Focused checks run for this pass:

- `python -m pytest tests/test_renderer_post_process_parity.py tests/test_renderer_internal_helper_mapping_parity.py tests/test_renderer_full_parity_gate.py -q --tb=short`
  passed: `27 passed, 1 skipped`.
- `python -m pytest tests/test_renderer_export_tail_parity.py tests/test_engine_client_command_parity.py::test_postprocess_restart_routes_through_renderer_export_not_renderer_cmd_registration -q --tb=short`
  passed: `7 passed`.
- `git diff --check` completed without whitespace errors; Git reported only
  existing line-ending normalization warnings for modified text files.

Parity estimate for this scoped renderer post-process scene-target lane:

- before: `98%`
- after: `99.5%`

The strict renderer estimate remains `100%`; repo-wide checked-in tree parity
remains estimated at `98%` until the broader evidence-freshness lane is
rerun.
