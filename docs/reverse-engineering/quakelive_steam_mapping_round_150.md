# quakelive_steam.exe Mapping Round 150

Date: 2026-04-27

Scope: source-backed support-library mapping for the embedded IJG progressive
JPEG Huffman encoder lane. This pass stayed mapping-only and anchored the
`0x479E50` through `0x47ABC0` slab against the checked-in `jcphuff.c` source
and the committed HLIL.

## Summary

This round resolved `11` additional `quakelive_steam.exe` rows. Classification
mix:

- `0` engine-owned functions
- `0` platform-service-owned functions
- `11` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main outcome is that the previously anonymous progressive-JPEG entropy
encoder tranche now reads as exact retained IJG code rather than generic codec
glue:

- `sub_47A9F0` is the exact `start_pass_phuff` dispatcher that chooses the
  `encode_mcu_*` routine family from the `Ss == 0` and `Ah == 0` scan-mode
  combination, allocates the `MAX_CORR_BITS` correction-bit buffer, and swaps
  between `finish_pass_phuff` and `finish_pass_gather_phuff`
- `sub_479E50` through `sub_47A150` close the bit-output, buffered-bit,
  pending-EOBRUN, and restart-marker helper lane used only by the progressive
  encoder surface in this retained build
- `sub_47A250`, `sub_47A3A0`, and `sub_47A570` complete the missing DC-first,
  AC-first, and DC-refine MCU emitters beside the already mapped
  `encode_mcu_AC_refine`
- `sub_47ABC0` is the exact `jinit_phuff_encoder` allocator that installs the
  `start_pass_phuff` vtable entry and zeros the derived/count-table workspaces

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_47A9F0` | `445` | support-library | `start_pass_phuff` | High | Closed from the exact scan-mode dispatcher, `MAX_CORR_BITS` allocation, table-validation loop, and gather-vs-output finish-pass selection. |
| 2 | `sub_47A3A0` | `454` | support-library | `encode_mcu_AC_first` | High | Closed from the AC initial-scan loop over `jpeg_natural_order`, the `EOBRUN` accumulator, the `0xF0` ZRL emission path, and the restart-state maintenance. |
| 3 | `sub_47A250` | `328` | support-library | `encode_mcu_DC_first` | High | Closed from the point-transform-by-`Al` DC-difference path, magnitude-bit count, Huffman symbol emit, and restart-latch updates. |
| 4 | `sub_479E50` | `308` | support-library | `emit_bits` | High | Closed from the packed-bit output buffer, `0xFF` byte stuffing, and the gather-statistics short-circuit. |
| 5 | `sub_47ABC0` | `66` | support-library | `jinit_phuff_encoder` | High | Closed from the `0x6C` entropy-object allocation, `start_pass_phuff` install, table-pointer zeroing, and null `bit_buffer` setup. |

## Evidence Notes

- This tranche is progressive-only, not generic `jchuff.c`, because the HLIL
  surface exposes the exact `EOBRUN`, `BE`, and correction-bit-buffer fields
  used by `jcphuff.c`, plus the `MAX_CORR_BITS == 1000` allocation in
  `sub_47A9F0`.
- `sub_47A0D0` matches `emit_eobrun` exactly: it derives the bit width of
  `EOBRUN`, emits the `(nbits << 4)` AC Huffman symbol, conditionally emits the
  EOB payload bits, and then drains the buffered correction bits through
  `sub_479F90`.
- `sub_47A150` matches `emit_restart` exactly: it first flushes pending EOBRUN
  state, then emits the `0x7F, 7` partial-byte fill, writes `0xFF` plus
  `JPEG_RST0 + restart_num`, and finally resets either the DC predictors or
  the AC-side `EOBRUN`/`BE` state depending on `Ss == 0`.
- `sub_47A620`, already mapped in the previous corpus as `encode_mcu_AC_refine`,
  was the key anchor that made the rest of the surrounding slab stable. The new
  names complete the contiguous progressive-MCU family around it.
- Smaller helpers such as `flush_bits`, `emit_symbol`, and `dump_buffer` remain
  intentionally unmapped as standalone aliases in this build because the
  compiler folded them into their emitted callers instead of preserving separate
  function starts.

## Aliases Added

- `sub_479E50` -> `emit_bits`
- `sub_479F90` -> `emit_buffered_bits`
- `sub_47A0D0` -> `emit_eobrun`
- `sub_47A150` -> `emit_restart`
- `sub_47A250` -> `encode_mcu_DC_first`
- `sub_47A3A0` -> `encode_mcu_AC_first`
- `sub_47A570` -> `encode_mcu_DC_refine`
- `sub_47A8E0` -> `finish_pass_phuff`
- `sub_47A930` -> `finish_pass_gather_phuff`
- `sub_47A9F0` -> `start_pass_phuff`
- `sub_47ABC0` -> `jinit_phuff_encoder`

## Verification

Static mapping validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- scoped duplicate-key scan for the `quakelive_steam` alias block passed with
  `0` duplicates
- recount after this pass: `1725` raw alias entries, `1654` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `30.221%` of `5473` functions
- `git diff --check` passed aside from the repo's existing LF -> CRLF
  normalization warnings on touched text files
- no build or runtime launch was needed; this was mapping-only work on the
  committed evidence corpus

Parity estimate after this pass:

- strict-retail Windows replacement target: `100%` before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

After this round, the refreshed largest-unaliased queue still begins with:

| # | Address | Ghidra name | Size |
| ---: | --- | --- | ---: |
| 1 | `0x004940D0` | `FUN_004940d0` | `547` |
| 2 | `0x004F4410` | `FUN_004f4410` | `546` |
| 3 | `0x004999C0` | `FUN_004999c0` | `541` |
| 4 | `0x00480030` | `FUN_00480030` | `537` |
| 5 | `0x004FC240` | `FUN_004fc240` | `537` |
| 6 | `0x00466B90` | `FUN_00466b90` | `535` |
| 7 | `0x0051FF40` | `FUN_0051ff40` | `535` |
| 8 | `0x004FAF60` | `FUN_004faf60` | `534` |
| 9 | `0x00510410` | `FUN_00510410` | `533` |
| 10 | `0x00501ED0` | `FUN_00501ed0` | `529` |

The next pass can return to the large unresolved host leftovers at
`sub_4940D0`, `sub_4F4410`, and `sub_4999C0`, or keep harvesting the remaining
embedded JPEG surface such as the adjacent decompressor/upsampler helpers.
