# quakelive_steam.exe Mapping Round 195

Date: 2026-04-28

Scope: retained FontStash/STB host-text support recovery across the atlas,
state, blur, font-add, and rasterizer seam from `0x00440F50` through
`0x00443690`, plus the adjacent unresolved rasterizer helpers at
`0x00442F80`, `0x004433E0`, and `0x00443480`.

## Summary

This round resolved `19` additional `quakelive_steam.exe` rows.
Classification mix:

- `0` engine-owned functions
- `0` platform-service-owned functions
- `19` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The useful outcome is that the anonymous host-text support slab now reads
cleanly as the retained FontStash allocator/lifetime lane plus the remaining
`stb_truetype` rasterizer helpers. The fontstash core now has explicit
ownership for atlas creation and packing (`fons__allocAtlas`,
`fons__atlasInsertNode`, `fons__atlasAddSkylineLevel`,
`fons__atlasRectFits`, `fons__atlasAddRect`, and `fons__addWhiteRect`), font
lifetime (`fons__allocFont`, `fonsAddFontMem`, `fonsAddFont`,
`fonsCreateInternal`, and `fonsDeleteInternal`), state/blur
(`fonsPushState`, `fonsClearState`, `fons__blurCols`, `fons__blurRows`, and
`fons__blur`), and the remaining support-library rasterizer handoff
(`stbtt__rasterize`, `stbtt_Rasterize`, and
`stbtt_MakeGlyphBitmapSubpixel`).

## Evidence Notes

- The strongest ownership anchor in this pass is the official FontStash source
  [`fontstash.h`](https://raw.githubusercontent.com/memononen/fontstash/master/src/fontstash.h),
  whose retained non-FreeType path exactly matches the atlas allocator,
  skyline packer, state stack, blur pass, and add-font lifetime observed in
  the committed HLIL.
- `sub_443560` is exact as `fonsCreateInternal` because the HLIL preserves the
  full constructor sequence: copy `FONSparams`, allocate the `0x20000` texture
  buffer, call the renderer-create callback, allocate the atlas with
  `0x100` nodes, allocate the scratch buffer, seed the white rectangle, then
  push and clear the initial state.
- `sub_443690` is exact as `fonsAddFont` because it is a thin file loader over
  `fopen` / `ftell` / `fread` that forwards to `sub_4415F0` with
  `freeData = 1`, matching FontStash's file-to-memory add path exactly.
- `sub_4415F0` and `sub_441CF0` are exact as `fonsAddFontMem` and
  `fonsDeleteInternal`: the former allocates a new `FONSfont`, zeroes the LUT
  to `-1`, stores the font data pointer and ownership flag, initializes the
  retained `stbtt_fontinfo`, and caches normalized metrics; the latter tears
  down the renderer callback, all retained fonts/glyph arrays, atlas buffers,
  scratch memory, and the context itself.
- The atlas helpers are exact because the HLIL preserves the skyline data
  model byte-for-byte: `sub_440F50` allocates a `FONSatlas`,
  `sub_440FD0` inserts one skyline node, `sub_441070` inserts a new skyline
  level then merges or shrinks overlapping spans, `sub_4411E0` tests rectangle
  fit over skyline spans, and `sub_441260` chooses the best insertion point
  before committing it through `sub_441070`.
- `sub_441340` is exact as `fons__addWhiteRect` because the only observed
  caller is the constructor, and the body allocates an atlas region, fills it
  with `0xff`, and updates the dirty rectangle exactly as the upstream helper
  does.
- `sub_441700`, `sub_441780`, and `sub_441810` are exact as
  `fons__blurCols`, `fons__blurRows`, and `fons__blur`. The column helper
  walks contiguous bytes across each row, the row helper walks by atlas stride,
  and the wrapper performs the same four-pass blur sequence as upstream.
- The remaining rasterizer trio is exact from the preserved call chain into the
  already-mapped STB helpers: `sub_4433E0` computes
  `flatness_in_pixels / min(scale_x, scale_y)` before calling
  `stbtt_FlattenCurves` and `sub_442F80`, so it is exact `stbtt_Rasterize`;
  `sub_442F80` builds edge records, sorts them, and dispatches to
  `stbtt__rasterize_sorted_edges`, so it is exact `stbtt__rasterize`; and
  `sub_443480` matches the retained `stbtt_MakeGlyphBitmapSubpixel` flow with
  `stbtt__GetGlyphShapeTT`, `stbtt_GetGlyphBitmapBoxSubpixel`, and
  `stbtt_Rasterize`.

## Aliases Added

- `sub_440F50` -> `fons__allocAtlas`
- `sub_440FD0` -> `fons__atlasInsertNode`
- `sub_441070` -> `fons__atlasAddSkylineLevel`
- `sub_4411E0` -> `fons__atlasRectFits`
- `sub_441260` -> `fons__atlasAddRect`
- `sub_441340` -> `fons__addWhiteRect`
- `sub_441450` -> `fonsPushState`
- `sub_4414E0` -> `fonsClearState`
- `sub_441520` -> `fons__allocFont`
- `sub_4415F0` -> `fonsAddFontMem`
- `sub_441700` -> `fons__blurCols`
- `sub_441780` -> `fons__blurRows`
- `sub_441810` -> `fons__blur`
- `sub_441CF0` -> `fonsDeleteInternal`
- `sub_442F80` -> `stbtt__rasterize`
- `sub_4433E0` -> `stbtt_Rasterize`
- `sub_443480` -> `stbtt_MakeGlyphBitmapSubpixel`
- `sub_443560` -> `fonsCreateInternal`
- `sub_443690` -> `fonsAddFont`

## Verification

Static mapping validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- scoped duplicate-key scan for the `quakelive_steam` alias block passed with
  `0` duplicates
- recount after this pass: `2079` raw alias entries, `2007` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `36.671%` of `5473` functions
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
| 1 | `0x0041AD70` | `FUN_0041ad70` | `517` |
| 2 | `0x004E6730` | `FUN_004e6730` | `504` |
| 3 | `0x004B4100` | `FUN_004b4100` | `502` |
| 4 | `0x00409670` | `FUN_00409670` | `496` |
| 5 | `0x004B3672` | `FUN_004b3672` | `495` |
| 6 | `0x0041C400` | `FUN_0041c400` | `492` |
| 7 | `0x00414AC0` | `FUN_00414ac0` | `490` |
| 8 | `0x0046A420` | `FUN_0046a420` | `490` |
| 9 | `0x004DC730` | `FUN_004dc730` | `490` |
| 10 | `0x004C12F0` | `FUN_004c12f0` | `488` |

The next pass can return to the persistent STL/iostream queue head at
`sub_41AD70`, resume the engine-owned leftovers at `sub_4E6730` and
`sub_4B4100`, or tackle the more inference-heavy ZeroMQ `pipe.cpp` seam at
`sub_409670` now that the retained FontStash lane is no longer anonymous.
