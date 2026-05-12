# quakelive_steam.exe Mapping Round 169

Date: 2026-04-27

Scope: retained `stb_truetype` font-init, metrics, and rasterizer-helper
recovery centered on the old queue head `0x0043F590` and the adjacent
unaliased slab through `0x004400B0`. This pass stayed mapping-only and used
the committed HLIL corpus plus the retained upstream
`E:\Temp\stb-src\stb_truetype.h` implementation as the naming anchor.

## Summary

This round resolved `11` additional `quakelive_steam.exe` rows.
Classification mix:

- `0` engine-owned functions
- `0` platform-service-owned functions
- `11` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The useful outcome is that the old `0x0043F4D0` through `0x0043FFA0` slab now
reads cleanly as the retained `stb_truetype` table-loader and glyph-metrics
lane instead of an anonymous font blob. The queue head `sub_43F590` closes as
the exact `stbtt_InitFont_internal` owner, the surrounding helpers now expose
the real glyph-box, horizontal-metrics, kerning, and bitmap-box helpers, and
`sub_4400B0` marks the clean handoff into the version-2 rasterizer as
`stbtt__handle_clipped_edge` immediately before the already-mapped
`stbtt__fill_active_edges_new`.

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_43F590` | `507` | CRT/STL/support-library | `stbtt_InitFont_internal` | High | Closed from the exact `cmap`/`loca`/`head`/`glyf`/`hhea`/`hmtx`/`kern`/`maxp` table discovery, Unicode cmap selection loop, `numGlyphs` load, and `indexToLocFormat` store in retained `stb_truetype`. |
| 2 | `sub_4400B0` | `303` | CRT/STL/support-library | `stbtt__handle_clipped_edge` | High | Closed from the exact version-2 rasterizer clipping rules around `e->sy`/`e->ey`, the vertical-strip cases, and the partial-pixel coverage write that `sub_4401E0` depends on. |
| 3 | `sub_43FFA0` | `262` | CRT/STL/support-library | `stbtt_GetGlyphBitmapBoxSubpixel` | High | Closed from the exact `stbtt_GetGlyphBox` dependency, zero-on-miss path, and `floor/ceil` bitmap bounds computation; the caller at `0x0044393F` also preserves the hidden `shift_x`/`shift_y` zero arguments. |
| 4 | `sub_43FE20` | `233` | CRT/STL/support-library | `stbtt__GetGlyphKernInfoAdvance` | High | Closed from the exact first-`kern`-table guards, `glyph1 << 16 | glyph2` binary search key, and signed kerning-advance return. |
| 5 | `sub_43FD30` | `226` | CRT/STL/support-library | `stbtt_GetGlyphHMetrics` | High | Closed from the exact `numOfLongHorMetrics` split between direct 4-byte metric rows and the packed left-side-bearing tail. |
| 6 | `sub_43FBB0` | `196` | CRT/STL/support-library | `stbtt_GetGlyphBox` | High | Closed from the direct `stbtt__GetGlyfOffset` dependency plus the `x0/y0/x1/y1` loads from the glyf header. |
| 7 | `sub_43FAF0` | `177` | CRT/STL/support-library | `stbtt__GetGlyfOffset` | High | Closed from the exact short-vs-long `loca` handling, `numGlyphs` bounds check, and zero-length glyph `-1` return. |
| 8 | `sub_43FC80` | `163` | CRT/STL/support-library | `stbtt__close_shape` | High | Closed from the exact start-off/was-off contour closure rules and the `vcurve` vs `vline` vertex emission pattern. |
| 9 | `sub_43F4F0` | `158` | CRT/STL/support-library | `stbtt__find_table` | High | Closed from the exact sfnt table-record scan and 4-byte tag comparison against names like `cmap`, `loca`, and `head`. |
| 10 | `sub_43FF10` | `135` | CRT/STL/support-library | `stbtt_GetFontVMetrics` | High | Closed from the exact ascent/descent/lineGap reads from `hhea + 4`, `+6`, and `+8`, plus the normalized caller usage at `0x004416B3`. |
| 11 | `sub_43F4D0` | `31` | CRT/STL/support-library | `ttULONG` | High | Closed from the exact four-byte big-endian load helper used throughout the table-discovery lane. |

## Evidence Notes

- The strongest ownership anchor in this pass is the exact retained
  `stb_truetype` init and metrics corridor in `E:\Temp\stb-src\stb_truetype.h`:
  `ttULONG`, `stbtt__find_table`, `stbtt_InitFont_internal`,
  `stbtt__GetGlyfOffset`, `stbtt_GetGlyphBox`, `stbtt__close_shape`,
  `stbtt_GetGlyphHMetrics`, `stbtt__GetGlyphKernInfoAdvance`,
  `stbtt_GetFontVMetrics`, and `stbtt_GetGlyphBitmapBoxSubpixel`.
- The committed HLIL in
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
  preserves the decisive control flow directly. `sub_43F590` shows the
  table-name lookups and Unicode cmap scan exactly, `sub_43FD30` preserves the
  `numOfLongHorMetrics` split, `sub_43FE20` preserves the `glyph1 << 16 |
  glyph2` binary search over `kern`, and `sub_43FFA0` preserves the
  floor/ceil bitmap-box rounding with the hidden shift arguments still visible
  in the caller at `0x0044393F`.
- `sub_4400B0` is exact because the HLIL and retained source both preserve the
  same clipped-edge cases for the version-2 scanline rasterizer: early exit on
  zero-height edges, clipping against `e->sy` / `e->ey`, the left-of-pixel and
  right-of-pixel full-coverage cases, and the partial-pixel coverage formula.
  Its direct use from the already-mapped `sub_4401E0 ->
  stbtt__fill_active_edges_new` is the confirming second signal.
- I intentionally stopped at the stable loader/metrics/rasterizer seam in this
  round. The nearby codepoint wrappers and the remaining rasterizer area
  helpers can be closed next, but they did not need to be forced to make the
  old queue-head slab readable and exact.

## Aliases Added

- `sub_43F4D0` -> `ttULONG`
- `sub_43F4F0` -> `stbtt__find_table`
- `sub_43F590` -> `stbtt_InitFont_internal`
- `sub_43FAF0` -> `stbtt__GetGlyfOffset`
- `sub_43FBB0` -> `stbtt_GetGlyphBox`
- `sub_43FC80` -> `stbtt__close_shape`
- `sub_43FD30` -> `stbtt_GetGlyphHMetrics`
- `sub_43FE20` -> `stbtt__GetGlyphKernInfoAdvance`
- `sub_43FF10` -> `stbtt_GetFontVMetrics`
- `sub_43FFA0` -> `stbtt_GetGlyphBitmapBoxSubpixel`
- `sub_4400B0` -> `stbtt__handle_clipped_edge`

## Verification

Static mapping validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- scoped duplicate-key scan for the `quakelive_steam` alias block passed with
  `0` duplicates
- recount after this pass: `1982` raw alias entries, `1910` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `34.899%` of `5473` functions
- `git diff --check` passed aside from the repo's existing LF -> CRLF
  normalization warnings on touched text files
- no build or runtime launch was needed; this was mapping-only work on the
  committed evidence corpus

Parity estimate after this pass:

- strict-retail Windows replacement target: `100%` before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

After this round, the refreshed largest-unaliased queue begins with:

| # | Address | Ghidra name | Size |
| ---: | --- | --- | ---: |
| 1 | `0x004FC240` | `FUN_004fc240` | `537` |
| 2 | `0x0041AD70` | `FUN_0041ad70` | `517` |
| 3 | `0x00486D40` | `FUN_00486d40` | `504` |
| 4 | `0x004E6730` | `FUN_004e6730` | `504` |
| 5 | `0x004B4100` | `FUN_004b4100` | `502` |
| 6 | `0x00475200` | `FUN_00475200` | `497` |
| 7 | `0x0047DA20` | `FUN_0047da20` | `497` |
| 8 | `0x00409670` | `FUN_00409670` | `496` |
| 9 | `0x004B3672` | `FUN_004b3672` | `495` |
| 10 | `0x0051A990` | `FUN_0051a990` | `493` |

The next pass can return to the still-transformed `vorbisfile.c` search helper
at `sub_4FC240`, take the persistent STL/iostream queue head at
`sub_41AD70`, or pivot back into the unresolved engine-owned host leftovers
around `sub_486D40` and `sub_4E6730` now that the retained font seam is no
longer anonymous.
