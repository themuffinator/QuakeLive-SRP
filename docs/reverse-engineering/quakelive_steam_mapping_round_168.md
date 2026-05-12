# quakelive_steam.exe Mapping Round 168

Date: 2026-04-27

Scope: retained `libpng 1.2.24` writer/setter recovery centered on the old
queue heads `0x0050C790` and `0x00510050`. This pass stayed mapping-only and
used the exact checked upstream `pngwrite.c`, `pngset.c`, `pngwutil.c`,
`pngmem.c`, `pngrutil.c`, and `pngwio.c` control flow as the naming anchor.

## Summary

This round added `38` exact `quakelive_steam.exe` aliases and corrected `1`
older libpng write-lane alias.
Classification mix:

- `0` engine-owned functions
- `0` platform-service-owned functions
- `38` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The useful outcome is that the retained libpng writer/setter slab now reads as
one coherent ownership band instead of alternating between exact read-side
names and anonymous write-side glue. The old queue heads `sub_50C790` and
`sub_510050` close cleanly as `png_create_write_struct_2` and
`png_handle_sRGB`, the private setter lane from `sub_50CB10` through
`sub_50DDB0` now names the real `png_set_*` surface, and the chunk-writer lane
from `sub_511C50` through `sub_514130` now exposes the missing
`PLTE`/`hIST`/`IDAT`/`tRNS`/`bKGD`/`oFFs`/`sCAL`/`pHYs`/`tIME` helpers.

The important correction is that `sub_50C140` is not `png_write_start_row`.
The HLIL shows the public `png_write_row` entry that performs the
`png_write_info` preflight checks, calls the real start-row helper on first
use, applies interlace skipping, and advances through `png_write_finish_row`.
The actual retained `png_write_start_row` helper is the newly mapped
`sub_512960`.

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_50C790` | `503` | support-library | `png_create_write_struct_2` | High | Closed from the exact libpng version-compatibility warning strings, `PNG_ZBUF_SIZE` setup, `png_set_mem_fn`, `png_set_write_fn`, and default filter-heuristic initialization in retained `pngwrite.c`. |
| 2 | `sub_510050` | `501` | support-library | `png_handle_sRGB` | High | Closed from the exact `"Missing IHDR before sRGB"`, `"Duplicate sRGB chunk"`, `"Incorrect sRGB chunk length"`, and `"Unknown sRGB intent"` paths plus the `png_set_sRGB_gAMA_and_cHRM` tail in retained `pngrutil.c`. |
| 3 | `sub_50C140` | `564` | support-library | `png_write_row` | High | Corrected from the older `png_write_start_row` guess. The HLIL preserves the public row-write preflight, first-row start helper call, interlace-pass skip logic, and `png_write_finish_row` tail from retained `pngwrite.c`. |
| 4 | `sub_50D980` | `464` | support-library | `png_set_text_2` | High | Closed from the exact `iTXt chunk not supported.` warning, `info_ptr->text` growth/reallocation lane, keyword/text copy loop, and `num_text` increment in retained `pngset.c`. |
| 5 | `sub_5131A0` | `330` | support-library | `png_write_IDAT` | High | Closed from the exact `"IDAT"` chunk name, CMF/FLG zlib header normalization, size heuristics based on image dimensions, and `png_write_complete_chunk` tail in retained `pngwutil.c`. |
| 6 | `sub_50DC20` | `386` | support-library | `png_set_sPLT` | High | Closed from the exact `No memory for sPLT palettes.` and `Out of memory while processing sPLT chunk` warning lanes plus the per-palette name/entry duplication path from retained `pngset.c`. |
| 7 | `sub_513DC0` | `378` | support-library | `png_write_bKGD` | High | Closed from the exact palette/index vs RGB/gray writer split, the `"Invalid background palette index"` and 16-bit-on-8-bit warning paths, and the final `bKGD` chunk write in retained `pngwutil.c`. |
| 8 | `sub_50C9F0` | `231` | support-library | `png_write_png` | High | Closed from the exact transform-flag dispatch around `png_write_info`, `png_write_image`, and `png_write_end`, including the optional interlace-handling and invert/swap helpers from retained `pngwrite.c`. |
| 9 | `sub_512960` | `395` | support-library | `png_write_start_row` | High | Closed from the exact row/filter buffer allocation lane, filter-buffer priming bytes (`SUB`/`UP`/`AVG`/`PAETH`), and interlace pass-dimension setup in retained `pngwutil.c`. |
| 10 | `sub_513C50` | `361` | support-library | `png_write_tRNS` | High | Closed from the exact palette/gray/RGB split, `"Invalid number of transparent colors specified"`, and the 16-bit-on-8-bit `tRNS` warning path in retained `pngwutil.c`. |
| 11 | `sub_50DDB0` | `305` | support-library | `png_set_unknown_chunks` | High | Closed from the exact unknown-chunk array growth lane, `"Out of memory while processing unknown chunk."` warning, copied `name/data/size/location` fields, and `unknown_chunks_num` increment in retained `pngset.c`. |
| 12 | `sub_512170` | `251` | support-library | `png_write_PLTE` | High | Closed from the exact `"PLTE"` chunk assembly, palette-length validation, indexed-color guard, and per-entry RGB byte emission in retained `pngwutil.c`. |
| 13 | `sub_5120C0` | `171` | support-library | `png_write_compressed_data_out` | High | Closed from the exact `compression_state` drain path that writes either a single flat buffer or the gathered output-pointer list before flushing the residual zlib buffer tail. |
| 14 | `sub_50DF40` | `165` | support-library | `png_create_struct_2` | High | Closed from the exact `PNG_STRUCT_PNG` vs `PNG_STRUCT_INFO` size switch, optional user allocator callback, and zero-initialized allocation path in retained `pngmem.c`. |
| 15 | `sub_513770` | `256` | support-library | `png_write_sBIT` | High | Closed from the exact per-color-type significant-bit validation and the `"Invalid sBIT depth specified"` warning path before writing the `sBIT` chunk. |
| 16 | `sub_513FD0` | `200` | support-library | `png_write_sCAL` | High | Closed from the exact `"%12.12e"` formatting of width/height, `"sCAL"` chunk construction, and packed buffer write path in retained `pngwutil.c`. |
| 17 | `sub_50E2B0` | `102` | support-library | `png_set_write_fn` | High | Closed from the exact I/O callback install surface used by `png_create_write_struct_2`, including the `write_data_fn`/`output_flush_fn` stores and null-default setup from retained `pngwio.c`. |
| 18 | `sub_50E370` | `42` | support-library | `png_crc_read` | High | Closed from the exact read-and-CRC-update helper that the libpng reader chunk handlers call before `png_crc_finish`. |

## Evidence Notes

- The writer/top-level surface matches the retained
  `E:\Temp\libpng-1.2.24-src\pngwrite.c` implementation. The most decisive
  anchors are the shared libpng mismatch strings inside
  `png_create_write_struct_2`, the public `png_write_row` preflight and
  interlace logic, the `png_write_png` transform dispatch, and the `Z_SYNC_FLUSH`
  `png_write_flush` loop.
- The setter/storage lane matches the retained
  `E:\Temp\libpng-1.2.24-src\pngset.c` implementation. The decisive anchors are
  the `PNG_INFO_*` validity-bit writes, the `png_malloc_warn`-guarded
  `iCCP`/`text`/`sPLT`/unknown-chunk allocation lanes, and the exact warning
  strings `"Insufficient memory to process iCCP chunk."`,
  `"No memory for sPLT palettes."`, and
  `"Out of memory while processing unknown chunk."`.
- The chunk-reader and chunk-writer bands match the retained
  `E:\Temp\libpng-1.2.24-src\pngrutil.c` and
  `E:\Temp\libpng-1.2.24-src\pngwutil.c` implementations. The strongest
  signals are the exact chunk names (`"sRGB"`, `"PLTE"`, `"hIST"`, `"IDAT"`,
  `"tRNS"`, `"bKGD"`, `"oFFs"`, `"sCAL"`, `"pHYs"`, `"tIME"`) plus the
  preserved warning strings for malformed lengths, invalid palette counts, and
  out-of-range 16-bit-on-8-bit writes.
- The allocator/custom-memory helpers match the retained
  `E:\Temp\libpng-1.2.24-src\pngmem.c` implementation. `sub_50DF40`,
  `sub_50DFF0`, `sub_50E070`, and `sub_50E090` preserve the exact
  struct-type switch, user allocator/free callback dispatch, and default
  malloc/free fallback used by upstream libpng 1.2.x.
- I left a few smaller write-side leftovers such as `sub_50D750`,
  `sub_50DEF0`, and the remaining unaliased late-libvorbis heads untouched in
  this round because the larger exact libpng seam was dense enough to close
  first without forcing weaker one-off names.

## Aliases Added

- `sub_50C390` -> `png_write_flush`
- `sub_50C790` -> `png_create_write_struct_2`
- `sub_50C990` -> `png_write_image`
- `sub_50C9F0` -> `png_write_png`
- `sub_50CAE0` -> `png_create_write_struct`
- `sub_50CB10` -> `png_set_sBIT`
- `sub_50D620` -> `png_set_sCAL`
- `sub_50D660` -> `png_set_pHYs`
- `sub_50D690` -> `png_set_PLTE`
- `sub_50D780` -> `png_set_sRGB`
- `sub_50D7A0` -> `png_set_sRGB_gAMA_and_cHRM`
- `sub_50D880` -> `png_set_iCCP`
- `sub_50D980` -> `png_set_text_2`
- `sub_50DB50` -> `png_set_tIME`
- `sub_50DB80` -> `png_set_tRNS`
- `sub_50DC20` -> `png_set_sPLT`
- `sub_50DDB0` -> `png_set_unknown_chunks`
- `sub_50DF40` -> `png_create_struct_2`
- `sub_50DFF0` -> `png_destroy_struct_2`
- `sub_50E070` -> `png_malloc_default`
- `sub_50E090` -> `png_free_default`
- `sub_50E0F0` -> `png_set_mem_fn`
- `sub_50E2B0` -> `png_set_write_fn`
- `sub_50E370` -> `png_crc_read`
- `sub_510050` -> `png_handle_sRGB`
- `sub_511C50` -> `png_save_int_32`
- `sub_5120C0` -> `png_write_compressed_data_out`
- `sub_512170` -> `png_write_PLTE`
- `sub_512270` -> `png_write_hIST`
- `sub_512960` -> `png_write_start_row`
- `sub_5131A0` -> `png_write_IDAT`
- `sub_513770` -> `png_write_sBIT`
- `sub_513C50` -> `png_write_tRNS`
- `sub_513DC0` -> `png_write_bKGD`
- `sub_513F40` -> `png_write_oFFs`
- `sub_513FD0` -> `png_write_sCAL`
- `sub_5140A0` -> `png_write_pHYs`
- `sub_514130` -> `png_write_tIME`

## Alias Correction

- `sub_50C140`: `png_write_start_row` -> `png_write_row`

## Verification

Static mapping validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- scoped duplicate-key scan for the `quakelive_steam` alias block passed with
  `0` duplicates
- recount after this pass: `1971` raw alias entries, `1899` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `34.698%` of `5473` functions
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
| 3 | `0x0043F590` | `FUN_0043f590` | `507` |
| 4 | `0x004E6730` | `FUN_004e6730` | `504` |
| 5 | `0x00486D40` | `FUN_00486d40` | `504` |
| 6 | `0x004B4100` | `FUN_004b4100` | `502` |
| 7 | `0x0047DA20` | `FUN_0047da20` | `497` |
| 8 | `0x00475200` | `FUN_00475200` | `497` |
| 9 | `0x00409670` | `FUN_00409670` | `496` |
| 10 | `0x004B3672` | `FUN_004b3672` | `495` |

The next pass can return to the deferred `vorbisfile.c` recursive-search
helper at `sub_4FC240`, take the still-opaque STL/iostream queue head at
`sub_41AD70`, or pivot into the unresolved engine-owned/client-host leftovers
around `sub_43F590`, `sub_4E6730`, and `sub_486D40`.
