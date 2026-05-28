# Quake Live Steam Mapping Round 336 - FontStash Reset Draw-Queue Boundary

## Evidence

- HLIL `quakelive_steam.exe` `0x00442300` keeps the retail
  `R_fonsErrorCallback` path: full-atlas errors double the retained FontStash
  atlas toward `2048 x 1024`, then call the reset helper at the cap.
- The mapped FontStash band documents `fons__flush` at `0x00441A50` as the
  queued-vertex drain used by the retained text renderer before atlas updates
  can invalidate pending glyph UVs.
- Runtime Campgrounds probes reproduced a repeated
  `R_fonsErrorCallback: error 1 val 0` / `Max font atlas size, flushing`
  sequence immediately after the loading-info cvars were published, matching a
  max-atlas reset during loading-screen host text.

## Reconstruction

- `src/code/renderer/tr_font.c` now drains pending renderer commands before
  `R_fonsErrorCallback` resizes or clears `*fontstash`.
- Atlas growth still preserves pixels and rescales cached glyph UVs for future
  draws; the new drain protects glyph quads that were queued before the resize
  and still hold UVs for the previous atlas dimensions.
- The max-size reset still clears retained glyph state, but only after queued
  text has been rendered against the old atlas contents.

## Confidence

High for the draw-queue boundary. The source no longer has FontStash's native
vertex queue, but `R_SyncRenderThread()` is the equivalent renderer-side drain
for the queued `RE_StretchPic` glyph commands used by this reconstruction.
