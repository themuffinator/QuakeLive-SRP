# quakelive_steam.exe Mapping Round 162

Date: 2026-04-27

Scope: retained libpng `pngrutil.c` unknown-chunk control plus the adjacent
`pngwutil.c` chunk-write helper lane around the old `0x00511670` queue head.
This pass stayed mapping-only.

## Summary

This round resolved `7` additional `quakelive_steam.exe` rows.
Classification mix:

- `0` engine-owned functions
- `0` platform-service-owned functions
- `7` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The useful outcome is that the old round-158 libpng deferral is now closed:
`sub_511670` resolves cleanly as `png_handle_unknown`, and the adjacent
anonymous `0x00511C80` through `0x00511D90` slab now reads as the concrete
PNG writer helpers that serialize integers, emit the file signature, and
write chunk headers/data/CRC trailers. That turns the surrounding
`pngrutil.c`/`pngwutil.c` lane from alternating named and anonymous helpers
into a much more coherent retained libpng band.

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_511670` | `520` | CRT/STL/support-library | `png_handle_unknown` | High | Closed from the exact `IDAT`-phase checks, `read_user_chunk_fn` callback path, `error in user chunk` string, `unknown critical chunk` string, and final unknown-chunk keep/discard handling. |
| 2 | `sub_511D90` | `120` | CRT/STL/support-library | `png_write_sig` | High | Closed from the exact eight-byte PNG signature write with the `sig_bytes` offset/state update preserved in HLIL. |
| 3 | `sub_511CD0` | `72` | CRT/STL/support-library | `png_write_chunk_header` | High | Closed from the exact length/name big-endian writes, CRC reset, and immediate CRC update over the chunk tag. |
| 4 | `sub_511D20` | `50` | CRT/STL/support-library | `png_write_chunk_data` | High | Closed from the exact guarded data write plus CRC accumulation over the chunk payload. |
| 5 | `sub_511D60` | `44` | CRT/STL/support-library | `png_write_chunk_end` | High | Closed from the exact CRC trailer write using the current `png_ptr->crc` state. |
| 6 | `sub_511C80` | `35` | CRT/STL/support-library | `png_save_uint_32` | High | Closed from the exact four-byte big-endian integer store helper. |
| 7 | `sub_511CB0` | `19` | CRT/STL/support-library | `png_save_uint_16` | High | Closed from the exact two-byte big-endian integer store helper. |

## Evidence Notes

- The read-side ownership anchor is the checked-in
  [png_handle_unknown](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libpng/pngrutil.c:2773>)
  body in
  [pngrutil.c](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libpng/pngrutil.c:2773>).
  The HLIL preserves the exact control signals that matter here: the `IDAT`
  transition rules, the user-chunk callback branch, and the paired
  `error in user chunk` / `unknown critical chunk` diagnostics.
- The writer-side anchors come straight from
  [pngwutil.c](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libpng/pngwutil.c:41>):
  [png_save_uint_32](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libpng/pngwutil.c:41>),
  [png_save_uint_16](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libpng/pngwutil.c:54>),
  [png_write_sig](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libpng/pngwutil.c:68>),
  [png_write_chunk_header](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libpng/pngwutil.c:90>),
  [png_write_chunk_data](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libpng/pngwutil.c:144>),
  and [png_write_chunk_end](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libpng/pngwutil.c:163>).
- `sub_511670` was intentionally deferred in
  [round 158](</E:/Repositories/QuakeLive-reverse/docs/reverse-engineering/quakelive_steam_mapping_round_158.md:1>)
  because the surrounding unknown-chunk control wording looked less stable
  than the neighboring fixed-name chunk handlers. Rechecking it against HLIL
  and the committed libpng source now makes the exact ownership safe.
- I intentionally left the larger write-side helpers below this slab alone in
  this pass. `sub_511E10` was already mapped as `png_text_compress`, but the
  lower `pngwutil.c` write/compress seam still deserves separate boundary work
  rather than forced names.

## Aliases Added

- `sub_511670` -> `png_handle_unknown`
- `sub_511C80` -> `png_save_uint_32`
- `sub_511CB0` -> `png_save_uint_16`
- `sub_511CD0` -> `png_write_chunk_header`
- `sub_511D20` -> `png_write_chunk_data`
- `sub_511D60` -> `png_write_chunk_end`
- `sub_511D90` -> `png_write_sig`

## Verification

Static mapping validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- scoped duplicate-key scan for the `quakelive_steam` alias block passed with
  `0` duplicates
- recount after this pass: `1849` raw alias entries, `1777` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `32.468%` of `5473` functions
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
| 3 | `0x00523B40` | `FUN_00523b40` | `520` |
| 4 | `0x00524370` | `FUN_00524370` | `520` |
| 5 | `0x00524580` | `FUN_00524580` | `520` |
| 6 | `0x00417790` | `FUN_00417790` | `518` |
| 7 | `0x0041AD70` | `FUN_0041ad70` | `517` |
| 8 | `0x00512340` | `FUN_00512340` | `517` |
| 9 | `0x004F5200` | `FUN_004f5200` | `514` |
| 10 | `0x00437710` | `FUN_00437710` | `513` |

The next pass can return to the still-transformed `vorbisfile.c` search helper
at `sub_4FC240`, the opaque `sub_4FAF60` file-wrapper slab, or keep pushing
through the larger retained support-library queue heads now that the libpng
unknown-chunk and chunk-write seams are less anonymous.
