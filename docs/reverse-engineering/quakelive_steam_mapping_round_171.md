# quakelive_steam.exe Mapping Round 171

Date: 2026-04-27

Scope: exact retained `qcommon/unzip.c` recovery in the old `0x004E74B0`
through `0x004E8BE0` corridor. This pass stayed mapping-only and used the
committed HLIL corpus plus the checked-in minizip/zlib source in
`src/code/qcommon/unzip.c` as the exact naming anchor.

## Summary

This round resolved `16` additional `quakelive_steam.exe` rows and corrected
`1` earlier over-generic alias.
Classification mix:

- `0` engine-owned functions
- `0` platform-service-owned functions
- `16` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The useful outcome is that the anonymous retained zip/inflate seam around
`sub_4E74B0` through `sub_4E8BE0` now reads as real minizip and older zlib
ownership instead of a mix of unnamed wrappers and one imprecise tree-builder
label. The main closures are the `unz*` file-iteration wrappers, the header
coherency validator, the older `inflate_flush` / `inflate_trees_*` /
`inflate_blocks_*` helpers, and the local checksum/allocation lane. I also
corrected `sub_4E78C0` from the generic `inflate_table` to the exact retained
`huft_build`.

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_4E7610` | `393` | support-library | `unzlocal_CheckCurrentFileCoherencyHeader` | High | Closed from the exact `0x04034B50` local-header magic check, compression-method validation, optional flag-bit-8 size/CRC bypass, and filename/extra-field size accounting in `unzip.c`. |
| 2 | `sub_4E78C0` | `1351` | support-library | `huft_build` | High | Corrected from the earlier generic `inflate_table`. The HLIL matches the retained code-length count, offset generation, canonical-code walk, multi-level table allocation, and `Z_BUF_ERROR`/`Z_DATA_ERROR` return rules in the exact `huft_build` body. |
| 3 | `sub_4E7EC0` | `365` | support-library | `inflate_trees_dynamic` | High | Closed from the exact two-stage literal/length then distance tree build, the `288`-entry work buffer, and the three retained error strings for oversubscribed, incomplete, and empty distance trees. |
| 4 | `sub_4E77C0` | `241` | support-library | `inflate_flush` | High | Closed from the exact sliding-window copy path, checksum callback updates, wraparound copy at `s->end`, and `Z_BUF_ERROR -> Z_OK` normalization. |
| 5 | `sub_4E89F0` | `298` | support-library | `adler32` | High | Closed from the exact `NMAX == 0x15B0` chunking, `DO16`-style unrolled accumulation, `BASE == 0xFFF1` modulus reduction, and `(s2 << 16) | s1` return. |
| 6 | `sub_4E8BE0` | `158` | support-library | `inflate_blocks_new` | High | Closed from the exact three allocations for the outer state, `MANY == 0x5A0` huft buffer, and window, followed by the `inflate_blocks_reset` tail. |
| 7 | `sub_4E8B70` | `112` | support-library | `inflate_blocks_reset` | High | Closed from the exact optional check-value store, `BTREE`/`DTREE` free path, `CODES` free path, mode reset to `TYPE`, and checksum reinitialization callback. |
| 8 | `sub_4E8350` | `55` | support-library | `inflate_codes_new` | High | Closed from the exact `0x1C` state allocation, mode reset to `START`, and persisted `lbits` / `dbits` / `ltree` / `dtree` fields. |
| 9 | `sub_4E7E20` | `140` | support-library | `inflate_trees_bits` | High | Closed from the exact `19`-entry work allocation, `huft_build(..., 19, 19, NULL, NULL, ...)` call, and the retained oversubscribed/incomplete bit-length tree error strings. |
| 10 | `sub_4E7530` | `102` | support-library | `unzGoToNextFile` | High | Closed from the exact `current_file_ok` / end-of-list checks, `0x2E + filename + extra + comment` central-directory stride, `num_file++`, and trailing `unzlocal_GetCurrentFileInfoInternal` refresh. |
| 11 | `sub_4E74E0` | `73` | support-library | `unzGoToFirstFile` | High | Closed from the exact reset of `pos_in_central_dir` to `offset_central_dir`, `num_file = 0`, and the initial `unzlocal_GetCurrentFileInfoInternal` refresh with `current_file_ok` update. |
| 12 | `sub_4E75C0` | `66` | support-library | `unzSetCurrentFileInfoPosition` | High | Closed from the exact stored-position writeback, refresh through `unzlocal_GetCurrentFileInfoInternal`, and unconditional `UNZ_OK` return. |
| 13 | `sub_4E74B0` | `46` | support-library | `unzGetCurrentFileInfo` | High | Closed from the exact direct forwarding wrapper into `unzlocal_GetCurrentFileInfoInternal`; the retail calling convention shuffles the decompiler argument names, but the wrapper shape matches the retained public API exactly. |
| 14 | `sub_4E8B30` | `22` | support-library | `zcalloc` | High | Closed from the exact `items * size` allocation helper used as the retained default `zalloc` hook. |
| 15 | `sub_4E8B50` | `18` | support-library | `zcfree` | High | Closed from the exact retained default `zfree` hook that only frees the pointer and ignores the opaque argument. |
| 16 | `sub_4E75A0` | `29` | support-library | `unzGetCurrentFileInfoPosition` | High | Closed from the exact `*pos = s->pos_in_central_dir` load with `UNZ_PARAMERROR` / `UNZ_OK` return behavior. |
| 17 | `sub_4E77A0` | `29` | support-library | `unztell` | High | Closed from the exact `pfile_in_zip_read->stream.total_out` return path after the usual null/read-state guard checks. |

## Evidence Notes

- The decisive source anchor for the public zip wrapper lane is
  [unzip.c](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/unzip.c:1622>)
  through
  [unzip.c](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/unzip.c:2215>),
  especially
  [unzGetCurrentFileInfo](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/unzip.c:1622>),
  [unzGoToFirstFile](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/unzip.c:1637>),
  [unzGoToNextFile](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/unzip.c:1659>),
  [unzGetCurrentFileInfoPosition](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/unzip.c:1686>),
  [unzSetCurrentFileInfoPosition](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/unzip.c:1702>),
  [unzlocal_CheckCurrentFileCoherencyHeader](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/unzip.c:1777>),
  and [unztell](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/unzip.c:2088>).
- The decisive source anchor for the retained older-zlib corridor is
  [inflate_flush](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/unzip.c:2860>),
  [huft_build](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/unzip.c:3007>),
  [inflate_trees_bits](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/unzip.c:3208>),
  [inflate_trees_dynamic](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/unzip.c:3235>),
  [inflate_codes_new](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/unzip.c:3667>),
  [adler32](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/unzip.c:3879>),
  [inflate_blocks_reset](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/unzip.c:2532>),
  [inflate_blocks_new](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/unzip.c:2550>),
  [zcalloc](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/unzip.c:4287>),
  and [zcfree](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/unzip.c:4293>).
- The committed HLIL preserves the same constants and control flow directly:
  the `0x2E` central-directory item stride in `unzGoToNextFile`, the
  `0x04034B50` local-header magic and flag-bit-8 bypass in
  `unzlocal_CheckCurrentFileCoherencyHeader`, the `MANY == 0x5A0` huft
  workspace allocation in `inflate_blocks_new`, and the `NMAX == 0x15B0`
  reduction loop in `adler32`.
- I intentionally left the larger `unzOpenCurrentFile` / `unzReadCurrentFile`
  / `unzeof` / `unzGetLocalExtrafield` / `unzCloseCurrentFile` seam alone in
  this pass. The retail layout interleaves that stateful read path more
  aggressively with the local inflate helpers than I wanted to force-name in
  the same round, while this tranche was already enough to close the clean
  exact wrappers and retained helper lane.

## Aliases Added

- `sub_4E74B0` -> `unzGetCurrentFileInfo`
- `sub_4E74E0` -> `unzGoToFirstFile`
- `sub_4E7530` -> `unzGoToNextFile`
- `sub_4E75A0` -> `unzGetCurrentFileInfoPosition`
- `sub_4E75C0` -> `unzSetCurrentFileInfoPosition`
- `sub_4E7610` -> `unzlocal_CheckCurrentFileCoherencyHeader`
- `sub_4E77A0` -> `unztell`
- `sub_4E77C0` -> `inflate_flush`
- `sub_4E7E20` -> `inflate_trees_bits`
- `sub_4E7EC0` -> `inflate_trees_dynamic`
- `sub_4E8350` -> `inflate_codes_new`
- `sub_4E89F0` -> `adler32`
- `sub_4E8B30` -> `zcalloc`
- `sub_4E8B50` -> `zcfree`
- `sub_4E8B70` -> `inflate_blocks_reset`
- `sub_4E8BE0` -> `inflate_blocks_new`

## Alias Corrected

- `sub_4E78C0` -> `huft_build` (from the earlier generic `inflate_table`)

## Verification

Static mapping validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- scoped duplicate-key scan for the `quakelive_steam` alias block passed with
  `0` duplicates
- recount after this pass: `2006` raw alias entries, `1934` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `35.337%` of `5473` functions
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
| 3 | `0x004E6730` | `FUN_004e6730` | `504` |
| 4 | `0x004B4100` | `FUN_004b4100` | `502` |
| 5 | `0x00475200` | `FUN_00475200` | `497` |
| 6 | `0x0047DA20` | `FUN_0047da20` | `497` |
| 7 | `0x00409670` | `FUN_00409670` | `496` |
| 8 | `0x004B3672` | `FUN_004b3672` | `495` |
| 9 | `0x0051A990` | `FUN_0051a990` | `493` |
| 10 | `0x0041C400` | `FUN_0041c400` | `492` |

The next pass can return to the still-transformed `vorbisfile.c` helper at
`sub_4FC240`, take the persistent STL/iostream queue head at `sub_41AD70`, or
push back into the large engine-owned host leftover at `sub_4E6730` now that
the retained unzip/zlib seam is much less anonymous.
