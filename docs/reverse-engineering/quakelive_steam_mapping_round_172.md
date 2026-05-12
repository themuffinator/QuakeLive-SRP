# quakelive_steam.exe Mapping Round 172

Date: 2026-04-27

Scope: exact retained `qcommon/unzip.c` recovery in the adjacent public
zlib/minizip API lane from `0x004E9690` through `0x004E9EA0`. This pass stayed
mapping-only and used the committed HLIL corpus plus the checked-in
minizip/zlib source in `src/code/qcommon/unzip.c` as the exact naming anchor.

## Summary

This round resolved `8` additional `quakelive_steam.exe` rows and corrected
`1` earlier alias in the same corridor.
Classification mix:

- `0` engine-owned functions
- `0` platform-service-owned functions
- `8` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The useful outcome is that the retained unzip/zlib seam below
`inflate_blocks` no longer stops at the internal helpers. The public zlib API
lane now reads cleanly as `inflate_blocks_free`, `inflateReset`,
`inflateEnd`, `inflateInit2_`, and `inflate`, while the adjacent minizip
read-path surface now has exact public ownership for `unzOpenCurrentFile`,
`unzReadCurrentFile`, `unzCloseCurrentFile`, and `unzClose`. I also corrected
`sub_4E98A0` from the old placeholder `unzip_inflate` to the exact retained
public `inflate`.

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_4E98A0` | `913` | support-library | `inflate` | High | Corrected from the earlier placeholder `unzip_inflate`. The HLIL matches the exact retained `inflate` state machine: method/flag parsing, preset-dictionary handoff, `inflate_blocks` dispatch, trailing Adler check, and the retained zlib error strings. |
| 2 | `sub_4E9C70` | `374` | support-library | `unzReadCurrentFile` | High | Closed from the exact read-buffer refill path, optional initial seek to `pos_in_zipfile + byte_before_the_zipfile`, store-vs-deflate split, `inflate(&stream, Z_SYNC_FLUSH)` tail, and `UNZ_EOF` / zlib error returns. |
| 3 | `sub_4E9EA0` | `289` | support-library | `unzOpenCurrentFile` | High | Closed from the exact `unzlocal_CheckCurrentFileCoherencyHeader` gate, `0x6C` read-state allocation, `0x10000` read buffer allocation, `inflateInit2(..., -MAX_WBITS)` setup, and the `s->pfile_in_zip_read` install. |
| 4 | `sub_4E97B0` | `236` | support-library | `inflateInit2_` | High | Closed from the exact `version[0]` / `sizeof(z_stream) == 0x38` guard, default `zcalloc` / `zcfree` install, signed negative-window `nowrap` handling, `8..15` window check, `inflate_blocks_new` allocation, and `inflateReset` tail. |
| 5 | `sub_4E9690` | `131` | support-library | `inflate_blocks_free` | High | Closed from the exact `inflate_blocks_reset` prefree, followed by frees of `window`, `hufts`, and the outer state object. |
| 6 | `sub_4E9DF0` | `98` | support-library | `unzCloseCurrentFile` | High | Closed from the exact read-buffer free, optional `inflateEnd` on `stream_initialised`, state free, and `s->pfile_in_zip_read = NULL` tail. |
| 7 | `sub_4E9760` | `68` | support-library | `inflateEnd` | High | Closed from the exact stream/state null guards, optional `inflate_blocks_free`, `zfree(state)`, and `state = Z_NULL` tail. |
| 8 | `sub_4E9720` | `63` | support-library | `inflateReset` | High | Closed from the exact `total_in = total_out = 0`, `msg = Z_NULL`, `nowrap ? imBLOCKS : imMETHOD`, and `inflate_blocks_reset` reinitialization path. |
| 9 | `sub_4E9E60` | `56` | support-library | `unzClose` | High | Closed from the exact optional `unzCloseCurrentFile`, `fclose(file)`, final `free(unz_s*)`, and `UNZ_OK` return. |

## Evidence Notes

- The decisive source anchor for the zlib public API lane is
  [inflate_blocks_free](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/unzip.c:2823>),
  [inflateReset](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/unzip.c:3987>),
  [inflateEnd](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/unzip.c:4000>),
  [inflateInit2_](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/unzip.c:4014>),
  and [inflate](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/unzip.c:4076>).
- The decisive source anchor for the public minizip read-path lane is
  [unzOpenCurrentFile](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/unzip.c:1863>),
  [unzReadCurrentFile](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/unzip.c:1963>),
  [unzCloseCurrentFile](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/unzip.c:2183>),
  and [unzClose](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/unzip.c:1433>).
- The committed HLIL preserves the same constants and control flow directly:
  the `sizeof(z_stream) == 0x38` gate in `inflateInit2_`, the negative-window
  `nowrap` bit carried through the `arg3 < 0` path, the `0x10000` read-buffer
  allocation in `unzOpenCurrentFile`, and the `inflate(..., Z_SYNC_FLUSH)`
  loop in `unzReadCurrentFile`.
- I intentionally left the tiny `unzeof` and `unzGetLocalExtrafield` helpers
  alone again in this pass. Their source ownership is clear, but the current
  committed Ghidra row layout does not expose them as separate high-value
  queue entries, so I prioritized the exact public helpers that were still
  consuming named function starts in `functions.csv`.

## Aliases Added

- `sub_4E9690` -> `inflate_blocks_free`
- `sub_4E9720` -> `inflateReset`
- `sub_4E9760` -> `inflateEnd`
- `sub_4E97B0` -> `inflateInit2_`
- `sub_4E9C70` -> `unzReadCurrentFile`
- `sub_4E9DF0` -> `unzCloseCurrentFile`
- `sub_4E9E60` -> `unzClose`
- `sub_4E9EA0` -> `unzOpenCurrentFile`

## Alias Corrected

- `sub_4E98A0` -> `inflate` (from the earlier placeholder `unzip_inflate`)

## Verification

Static mapping validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- scoped duplicate-key scan for the `quakelive_steam` alias block passed with
  `0` duplicates
- recount after this pass: `2014` raw alias entries, `1942` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `35.483%` of `5473` functions
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

The next pass can still return to the transformed `vorbisfile.c` helper at
`sub_4FC240`, take the persistent STL/iostream queue head at `sub_41AD70`, or
push back into the large engine-owned host leftover at `sub_4E6730` now that
the retained unzip/zlib lane is mapped almost end-to-end.
