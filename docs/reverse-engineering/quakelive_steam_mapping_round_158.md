# quakelive_steam.exe Mapping Round 158

Date: 2026-04-27

Scope: retained `libpng` `pngrutil.c` chunk-handler recovery around the old
`0x00510410` queue head. This pass stayed mapping-only.

## Summary

This round resolved `6` additional `quakelive_steam.exe` rows.
Classification mix:

- `0` engine-owned functions
- `0` platform-service-owned functions
- `6` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main outcome is that the remaining anonymous gaps inside the already-clean
`pngrutil.c` handler lane now resolve as the retained `iCCP`, `sPLT`, `sCAL`,
`tIME`, `tEXt`, and `zTXt` chunk readers. This closes the obvious holes between
the already mapped `png_handle_cHRM`, `png_handle_tRNS`, `png_handle_bKGD`,
`png_handle_hIST`, `png_handle_pHYs`, `png_handle_oFFs`, and `png_handle_pCAL`
helpers, so the retail chunk parser now reads as a coherent libpng dispatcher
band instead of alternating named and anonymous handlers.

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_510410` | `533` | support-library | `png_handle_sPLT` | High | Closed from the exact `Missing IHDR before sPLT`, `Invalid sPLT after IDAT`, `malformed sPLT chunk`, `sPLT chunk has bad length`, `sPLT chunk too long`, and `sPLT chunk requires too much memory` diagnostics plus the exact sample-depth and entry-decoding loop. |
| 2 | `sub_510250` | `435` | support-library | `png_handle_iCCP` | High | Closed from the exact `Missing IHDR before iCCP`, `Invalid iCCP after IDAT`, `Duplicate iCCP chunk`, `Malformed iCCP chunk`, `Ignoring nonzero compression type`, `Profile size field missing`, and `Ignoring truncated iCCP profile` flow. |
| 3 | `sub_511520` | `330` | support-library | `png_handle_zTXt` | High | Closed from the exact `Missing IHDR before zTXt`, `Truncated zTXt chunk`, `Unknown compression type in zTXt chunk`, and `Out of memory processing zTXt chunk` path plus the inflate-and-store text payload lane. |
| 4 | `sub_5112E0` | `281` | support-library | `png_handle_tIME` | High | Closed from the exact `Out of place tIME chunk`, `Duplicate tIME chunk`, and `Incorrect tIME chunk length` checks plus the 7-byte timestamp decode into `png_time`. |
| 5 | `sub_511400` | `278` | support-library | `png_handle_tEXt` | High | Closed from the exact `Missing IHDR before tEXt`, `No memory to process text chunk`, and `Insufficient memory to process tEXt chunk` flow plus the keyword/text split before `png_set_text_2`. |
| 6 | `sub_511120` | `160` | support-library | `png_handle_sCAL` | High | Closed from the exact `Missing IHDR before sCAL`, `Invalid sCAL after IDAT`, `Duplicate sCAL chunk`, `Truncated sCAL chunk`, `malformed width string`, `malformed height string`, and `Invalid sCAL data` checks. |

## Evidence Notes

- The recovered tranche maps directly onto the checked-in
  [pngrutil.c](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libpng/pngrutil.c:1340>)
  handler lane:
  [png_handle_iCCP](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libpng/pngrutil.c:1340>),
  [png_handle_sPLT](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libpng/pngrutil.c:1564>),
  [png_handle_sCAL](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libpng/pngrutil.c:2276>),
  [png_handle_tIME](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libpng/pngrutil.c:2350>),
  [png_handle_tEXt](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libpng/pngrutil.c:2387>),
  and [png_handle_zTXt](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libpng/pngrutil.c:2459>).
- `sub_510250` is a strong exact `png_handle_iCCP` hit even though the retail
  build preserves an older-style benign-error wording instead of the newer
  validation helpers in the checked-in libpng. The identity is still stable
  from the keyword scan, compression-type check, profile-size header read, and
  decompressed-profile handoff into the already mapped `png_set_iCCP` lane.
- `sub_510410` is an exact `png_handle_sPLT` hit. The HLIL reads the palette
  name, consumes the sample depth byte, validates the entry stride as either
  `6` or `10`, allocates `10 * nentries` bytes, and decodes either byte or
  16-bit channel values before committing through the already mapped
  `png_set_sPLT` helper.
- `sub_511120` is the exact `sCAL` parser even though the retail compiler has
  emitted it through `strtod`-based validation rather than the newer
  `png_check_fp_number` helper structure used by the checked-in source. The
  chunk-level semantics, error strings, and final `png_set_sCAL_s` handoff are
  still one-to-one.
- I intentionally left `sub_511670` unresolved in this pass. Its shape clearly
  belongs to the unknown-chunk handling/control lane, but the retail wording
  (`unknown critical chunk`) and fused callback/keep-handling flow do not line
  up closely enough with the checked-in `png_handle_unknown` body for the exact
  alias to be risk-free yet.

## Aliases Added

- `sub_510250` -> `png_handle_iCCP`
- `sub_510410` -> `png_handle_sPLT`
- `sub_511120` -> `png_handle_sCAL`
- `sub_5112E0` -> `png_handle_tIME`
- `sub_511400` -> `png_handle_tEXt`
- `sub_511520` -> `png_handle_zTXt`

## Verification

Static mapping validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- scoped duplicate-key scan for the `quakelive_steam` alias block passed with
  `0` duplicates
- recount after this pass: `1805` raw alias entries, `1734` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `31.683%` of `5473` functions
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
| 3 | `0x00501ED0` | `FUN_00501ed0` | `529` |
| 4 | `0x00498BB0` | `FUN_00498bb0` | `526` |
| 5 | `0x00503630` | `FUN_00503630` | `526` |
| 6 | `0x004AC440` | `FUN_004ac440` | `521` |
| 7 | `0x00511670` | `FUN_00511670` | `520` |
| 8 | `0x00523B40` | `FUN_00523b40` | `520` |
| 9 | `0x00524370` | `FUN_00524370` | `520` |
| 10 | `0x00524580` | `FUN_00524580` | `520` |

The next pass can return to the still-transformed `vorbisfile.c` search helper
at `sub_4FC240`, the opaque `sub_4FAF60` file-wrapper slab, or stay inside the
adjacent libpng unknown-chunk control seam beginning at `sub_511670`.
