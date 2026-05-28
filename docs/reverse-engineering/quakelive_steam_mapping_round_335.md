# Quake Live Steam Mapping Round 335: Registration Image Touch Visibility

Date: 2026-05-28

Scope: renderer end-registration image residency pass and the visible image-cache
overlay observed during Campgrounds loading.

## Evidence Checked

- HLIL at `0x00449EF0` maps the retail `RE_EndRegistration` export: it syncs
  the render thread, returns on low physical memory, and tail-calls the image
  cache quad helper at `0x004374B0`.
- Ghidra labels `0x004374B0` as the `RB_ShowImages`-equivalent helper. The same
  helper is also called from `RB_SwapBuffers` only when `r_showImages` is nonzero.
- Runtime `qconsole.log` showed `msec to draw all images` during the Campgrounds
  launch while `r_showImages` was not configured in the VS Code launch task or
  local configs, matching the end-registration warm-up path rather than an
  intentional debug overlay.

## Reconstruction Decision

The source keeps the retail registration-tail purpose, but separates it from the
visible debug overlay:

- `RB_ShowImages` remains the `r_showImages` diagnostic overlay and still draws
  the image cache during swap when explicitly enabled.
- `RE_EndRegistration` now calls `RB_TouchImages`, which performs a non-visual
  bind walk over the uploaded image cache instead of issuing screen-space quads.

This is a source-safety reconstruction of the retail intent. It avoids leaking
the cache warm-up quads or their GL state into loading or first in-game frames
while keeping the debug overlay and residency pass distinct.

## Parity Estimate

- Focused renderer image-cache launch slice: **72% -> 86%**.
- Repo-wide parity remains **98% -> 98%**.
