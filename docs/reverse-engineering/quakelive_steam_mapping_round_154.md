# quakelive_steam.exe Mapping Round 154

Date: 2026-04-27

Scope: source-backed support-library mapping for the retained IJG
decompressor-control, inverse-DCT-manager, and sequential Huffman-decoder
lanes. This pass stayed mapping-only and anchored the `0x47C470` through
`0x47D9D0` slab against the checked-in `jdcoefct.c`, `jddctmgr.c`, and
`jdhuff.c` sources plus the committed HLIL.

## Summary

This round resolved `11` additional `quakelive_steam.exe` rows and corrected
`2` older over-specific JPEG aliases. Classification mix:

- `0` engine-owned functions
- `0` platform-service-owned functions
- `11` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main outcome is that the adjacent decompressor pipeline now reads as three
real retained IJG families instead of anonymous support glue:

- `sub_47C470` through `sub_47C740` close the single-MCU
  `jdcoefct.c` coefficient-controller lane around the contextualized
  `start_input_pass_d_coef`, `start_output_pass_d_coef`,
  `decompress_onepass`, and `jinit_d_coef_controller`
- `sub_47CD60` and `sub_47CF60` close the `jddctmgr.c` inverse-DCT manager
  around `start_pass_idctmgr` and `jinit_inverse_dct`
- `sub_47CFE0` through `sub_47D9D0` close the retained `jdhuff.c` sequential
  Huffman lane around `jpeg_make_d_derived_tbl`, `jpeg_fill_bit_buffer`,
  `jpeg_huff_decode`, `process_restart`, `decode_mcu`,
  `start_pass_huff_decoder`, and `jinit_huff_decoder`

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_47D470` | `1388` | support-library | `decode_mcu` | High | Closed from the exact sequential Huffman MCU walk: restart handling, per-block DC/AC table selection, zigzag-to-natural coefficient output, and the alternate AC discard path when `DCT_scaled_size == 1`. |
| 2 | `sub_47CFE0` | `507` | support-library | `jpeg_make_d_derived_tbl` | High | Closed from the exact Figure C.1/C.2/F.15 Huffman-table derivation flow: `huffsize`, `huffcode`, `valptr`, `mincode`, `maxcode`, and the 8-bit lookahead table fill. |
| 3 | `sub_47CD60` | `501` | support-library | `start_pass_idctmgr` | High | Closed from the per-component IDCT-method selection, `jpeg_idct_float` wiring, method-cache check, and quant-table-to-multiplier-table rebuild logic specific to `jddctmgr.c`. |
| 4 | `sub_47D1F0` | `261` | support-library | `jpeg_fill_bit_buffer` | High | Closed from the exact marker-aware byte loader: stuffed-`0xFF00` handling, end-of-segment warning gate, and the `printed_eod` state update used by both sequential and progressive Huffman decoders. |
| 5 | `sub_47C740` | `200` | support-library | `jinit_d_coef_controller` | High | Closed from the exact single-MCU-buffer initializer: allocate the `my_coef_controller`, install the input/output/decompress function pointers, reject `need_full_buffer`, and allocate `D_MAX_BLOCKS_IN_MCU * SIZEOF(JBLOCK)` workspace as ten `0x80`-byte blocks. |

## Evidence Notes

- `sub_47C470` and `sub_47C4D0` are the `jdcoefct.c` pass helpers, but they
  are contextualized here to avoid colliding with other JPEG-local
  `start_input_pass` / `start_output_pass` statics in the alias ledger. The
  HLIL shows `sub_47C470` zeroing `input_iMCU_row` and recomputing the
  within-row counters exactly as `start_input_pass` plus `start_iMCU_row`
  would, while `sub_47C4D0` is the tiny `output_iMCU_row = 0` reset used by
  the non-smoothing build.
- `sub_47C4F0` was previously over-labeled as `decompress_data`. The body is
  the one-MCU-buffer lockstep decoder from `jdcoefct.c`: it zeroes the
  `MCU_buffer`, calls `entropy->decode_mcu`, runs per-component inverse DCTs
  directly into the caller buffer, then advances both output and input iMCU
  counters. That is exact `decompress_onepass`, not the virtual-array
  multipass `decompress_data` variant.
- `sub_47C740` matches the `jinit_d_coef_controller` compile path where
  `need_full_buffer` is rejected and a single `D_MAX_BLOCKS_IN_MCU` workspace
  is allocated. The observed `0x500` block allocation matches ten `0x80`-byte
  `JBLOCK`s exactly.
- `sub_47CD60` and `sub_47CF60` are the `jddctmgr.c` pair. The HLIL preserves
  the `JDCT_FLOAT` dispatch, the per-component cached `cur_method` checks, the
  float AA&N multiplier build with the exact `aanscalefactor[]` constants, and
  the `0x54` manager allocation plus per-component zeroed multiplier tables.
- `sub_47CFE0`, `sub_47D1F0`, `sub_47D300`, `sub_47D400`, `sub_47D470`,
  `sub_47D890`, and `sub_47D9D0` form a contiguous `jdhuff.c` lane. The HLIL
  shows the derived-table builder, bit-buffer refill helper, generic Huffman
  decoder, restart-marker recovery, MCU entropy decoder, scan-start setup, and
  top-level entropy-decoder initializer with the expected vtable layout and
  table-nulling loop.

## Aliases Added

- `sub_47C470` -> `start_input_pass_d_coef`
- `sub_47C4D0` -> `start_output_pass_d_coef`
- `sub_47C740` -> `jinit_d_coef_controller`
- `sub_47CD60` -> `start_pass_idctmgr`
- `sub_47CF60` -> `jinit_inverse_dct`
- `sub_47CFE0` -> `jpeg_make_d_derived_tbl`
- `sub_47D1F0` -> `jpeg_fill_bit_buffer`
- `sub_47D300` -> `jpeg_huff_decode`
- `sub_47D400` -> `process_restart`
- `sub_47D890` -> `start_pass_huff_decoder`
- `sub_47D9D0` -> `jinit_huff_decoder`

## Alias Corrections

- `sub_47C4F0`: `decompress_data` -> `decompress_onepass`
- `sub_47D470`: `jpeg_decode_mcu` -> `decode_mcu`

## Verification

Static mapping validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- scoped duplicate-key scan for the `quakelive_steam` alias block passed with
  `0` duplicates
- recount after this pass: `1765` raw alias entries, `1694` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `30.952%` of `5473` functions
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
| 4 | `0x004FC240` | `FUN_004fc240` | `537` |
| 5 | `0x00466B90` | `FUN_00466b90` | `535` |
| 6 | `0x0051FF40` | `FUN_0051ff40` | `535` |
| 7 | `0x004FAF60` | `FUN_004faf60` | `534` |
| 8 | `0x00510410` | `FUN_00510410` | `533` |
| 9 | `0x00501ED0` | `FUN_00501ed0` | `529` |
| 10 | `0x00498BB0` | `FUN_00498bb0` | `526` |

The next pass can return to the large unresolved host leftovers at
`sub_4940D0`, `sub_4F4410`, and `sub_4999C0`, or keep harvesting adjacent IJG
compression helpers where the emitted support code still stays one-to-one with
the checked-in source.
