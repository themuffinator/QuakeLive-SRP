# quakelive_steam.exe Mapping Round 164

Date: 2026-04-27

Scope: retained libpng keyword and ancillary chunk-writer recovery around the
old `0x00512340` queue head. This pass stayed mapping-only.

## Summary

This round resolved `10` additional `quakelive_steam.exe` rows.
Classification mix:

- `0` engine-owned functions
- `0` platform-service-owned functions
- `10` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The useful outcome is that the anonymous libpng write-side seam around
`0x00512340` now reads as the real text/profile writer lane instead of a mix
of opaque keyword scrubbers and ad hoc chunk emitters. The former queue-head
`sub_512340` resolves cleanly as `png_check_keyword`, and the adjacent
writers now line up with the checked-in `pngwutil.c` ownership for `tEXt`,
`zTXt`, `pCAL`, `iCCP`, `sPLT`, and the small complete-chunk / trailer chunk
helpers.

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_512340` | `517` | CRT/STL/support-library | `png_check_keyword` | High | Closed from the exact 1-79 byte keyword scrub, bad-character tracking, trailing-space trim, and `keyword truncated` / formatted bad-character warning path. |
| 2 | `sub_5127A0` | `447` | CRT/STL/support-library | `png_write_pCAL` | High | Closed from the exact purpose keyword validation, `X0/X1/type/nparams` packing, per-parameter length accumulation, and chunk payload writer loop. |
| 3 | `sub_5135C0` | `424` | CRT/STL/support-library | `png_write_sPLT` | High | Closed from the exact keyword validation, depth-dependent `6` vs `10` byte entry encoding, and palette entry writer loop. |
| 4 | `sub_513450` | `355` | CRT/STL/support-library | `png_write_iCCP` | High | Closed from the exact ICC profile length/header checks, keyword validation, compression setup, and chunk writer with profile payload. |
| 5 | `sub_512640` | `339` | CRT/STL/support-library | `png_write_zTXt` | High | Closed from the exact no-compression fallback to `png_write_tEXt`, zTXt compression-type gate, text compression path, and chunk emission. |
| 6 | `sub_512550` | `232` | CRT/STL/support-library | `png_write_tEXt` | High | Closed from the exact keyword validation, optional empty-text handling, chunk length calculation, and `tEXt` payload writer path. |
| 7 | `sub_513350` | `142` | CRT/STL/support-library | `png_write_gAMA_fixed` | High | Closed from the exact `file_gamma * 100000 + 0.5` pack and `gAMA` complete-chunk write. |
| 8 | `sub_5133E0` | `110` | CRT/STL/support-library | `png_write_sRGB` | High | Closed from the exact intent range check and one-byte `sRGB` complete-chunk write. |
| 9 | `sub_5132F0` | `82` | CRT/STL/support-library | `png_write_IEND` | High | Closed from the exact zero-length `IEND` complete-chunk write and `PNG_HAVE_IEND` mode flag. |
| 10 | `sub_512DA0` | `50` | CRT/STL/support-library | `png_write_complete_chunk` | High | Closed from the exact header-data-end wrapper around `png_write_chunk_header`, `png_write_chunk_data`, and `png_write_chunk_end`. |

## Evidence Notes

- The recovered ownership maps directly onto the checked-in libpng sources:
  [png_check_keyword](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libpng/pngset.c:1910>)
  in [pngset.c](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libpng/pngset.c:1910>),
  plus the write-side helpers in
  [pngwutil.c](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libpng/pngwutil.c:192>):
  [png_write_complete_chunk](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libpng/pngwutil.c:192>),
  [png_write_IEND](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libpng/pngwutil.c:1090>),
  [png_write_gAMA_fixed](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libpng/pngwutil.c:1101>),
  [png_write_sRGB](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libpng/pngwutil.c:1116>),
  [png_write_iCCP](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libpng/pngwutil.c:1134>),
  [png_write_sPLT](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libpng/pngwutil.c:1196>),
  [png_write_tEXt](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libpng/pngwutil.c:1614>),
  [png_write_zTXt](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libpng/pngwutil.c:1657>),
  and [png_write_pCAL](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libpng/pngwutil.c:1828>).
- `sub_512340` is the strongest anchor in this pass. The HLIL preserves the
  full keyword sanitizer structure from `png_check_keyword`: legal character
  filter, single-space normalization, trailing-space removal, empty-keyword
  rejection, and the warning split between truncation and bad characters.
- The chunk writers are reinforced by the already-mapped helper lane just
  below them: `png_write_chunk_header`, `png_write_chunk_data`,
  `png_write_chunk_end`, `png_text_compress`, `png_write_IHDR`, and the small
  integer packers are all already named, so these functions land into a very
  stable local ownership band.
- I intentionally left the larger image-data writer at `sub_5131A0` deferred.
  It is clearly adjacent libpng write-side logic, but I wanted this pass to
  stay on exact one-to-one source owners rather than force a version-sensitive
  IDAT helper name.

## Aliases Added

- `sub_512340` -> `png_check_keyword`
- `sub_512550` -> `png_write_tEXt`
- `sub_512640` -> `png_write_zTXt`
- `sub_5127A0` -> `png_write_pCAL`
- `sub_512DA0` -> `png_write_complete_chunk`
- `sub_5132F0` -> `png_write_IEND`
- `sub_513350` -> `png_write_gAMA_fixed`
- `sub_5133E0` -> `png_write_sRGB`
- `sub_513450` -> `png_write_iCCP`
- `sub_5135C0` -> `png_write_sPLT`

## Verification

Static mapping validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- scoped duplicate-key scan for the `quakelive_steam` alias block passed with
  `0` duplicates
- recount after this pass: `1874` raw alias entries, `1802` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `32.925%` of `5473` functions
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
| 2 | `0x004FAF60` | `FUN_004faf60` | `534` |
| 3 | `0x00417790` | `FUN_00417790` | `518` |
| 4 | `0x0041AD70` | `FUN_0041ad70` | `517` |
| 5 | `0x004F5200` | `FUN_004f5200` | `514` |
| 6 | `0x00437710` | `FUN_00437710` | `513` |
| 7 | `0x00421830` | `FUN_00421830` | `512` |
| 8 | `0x0043F590` | `FUN_0043f590` | `507` |
| 9 | `0x004F7B70` | `FUN_004f7b70` | `506` |
| 10 | `0x004EE260` | `FUN_004ee260` | `505` |

The next pass can return to the still-transformed `vorbisfile.c` search helper
at `sub_4FC240`, the opaque `sub_4FAF60` file-wrapper slab, or revisit the
retained ZeroMQ XPUB lane now that the libpng writer seam around
`sub_512340` is no longer anonymous.
