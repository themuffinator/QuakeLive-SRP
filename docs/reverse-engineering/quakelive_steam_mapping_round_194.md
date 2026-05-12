# Quake Live Steam Mapping Round 194

## Scope

This round stays in the retained IJG JPEG corridor and closes the
decompressor input-controller family in `jdinput.c`.

Primary evidence for this pass:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `src/code/jpeg-6/jdinput.c`

## Summary

This round resolves `8` additional `quakelive_steam.exe` rows.

Classification mix:

- `0` engine-owned functions
- `0` platform-service-owned functions
- `8` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The useful outcome is that the old anonymous ladder from `0x0047DA20`
through `0x0047DFD0` now reads cleanly as the exact retained JPEG
decompressor input-control pipeline instead of opaque state-machine glue:
header-time `initial_setup`, scan-time `per_scan_setup` and
`latch_quant_tables`, the `consume_markers` state transition owner, and the
surrounding reset/start/finish/controller-init callbacks.

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_47DA20` | `497` | support-library | `initial_setup` | High | Closed from the exact first-SOS decompressor setup: image-size and precision guards, `MAX_COMPONENTS` check, max sampling-factor walk, `min_DCT_scaled_size = DCTSIZE`, component block/sample dimension setup, and `has_multiple_scans` derivation. |
| 2 | `sub_47DC20` | `408` | support-library | `per_scan_setup` | High | Closed from the exact split between single-component and interleaved scans, including `MCUs_per_row`, `MCU_rows_in_scan`, per-component MCU geometry, `last_col_width`, `last_row_height`, and `MCU_membership`. |
| 3 | `sub_47DDC0` | `160` | support-library | `latch_quant_tables` | High | Closed from the exact current-scan quant-table save path: skip components with existing saved tables, validate `quant_tbl_no`, allocate `JQUANT_TBL`, `MEMCOPY`, and store `compptr->quant_table`. |
| 4 | `sub_47DE60` | `66` | support-library | `start_input_pass` | High | Closed from the exact wrapper sequence `per_scan_setup -> latch_quant_tables -> entropy->start_pass -> coef->start_input_pass`, then switching `consume_input` to `coef->consume_data`. |
| 5 | `sub_47DEB0` | `186` | support-library | `consume_markers` | High | Closed from the exact `JPEG_REACHED_SOS` / `JPEG_REACHED_EOI` / `JPEG_SUSPENDED` state machine, including the first-SOS `initial_setup`, later-scan `start_input_pass`, and the `output_scan_number` clamp on EOI. |
| 6 | `sub_47DF70` | `64` | support-library | `reset_input_controller` | High | Closed from the exact reset of `consume_input`, `has_multiple_scans`, `eoi_reached`, and `inheaders`, followed by `reset_error_mgr`, `reset_marker_reader`, and `coef_bits = NULL`. |
| 7 | `sub_47DFB0` | `20` | support-library | `finish_input_pass` | High | Closed from the exact one-line callback that restores `inputctl->consume_input = consume_markers`. |
| 8 | `sub_47DFD0` | `68` | support-library | `jinit_input_controller` | High | Closed from the exact controller allocation and vtable-style method hookup for `consume_input`, `reset_input_controller`, `start_input_pass`, and `finish_input_pass`. |

## Evidence Notes

- The decisive source anchors are
  [initial_setup](</E:/Repositories/QuakeLive-reverse/src/code/jpeg-6/jdinput.c:39>),
  [per_scan_setup](</E:/Repositories/QuakeLive-reverse/src/code/jpeg-6/jdinput.c:121>),
  [latch_quant_tables](</E:/Repositories/QuakeLive-reverse/src/code/jpeg-6/jdinput.c:220>),
  [start_input_pass](</E:/Repositories/QuakeLive-reverse/src/code/jpeg-6/jdinput.c:254>),
  [finish_input_pass](</E:/Repositories/QuakeLive-reverse/src/code/jpeg-6/jdinput.c:271>),
  [consume_markers](</E:/Repositories/QuakeLive-reverse/src/code/jpeg-6/jdinput.c:288>),
  [reset_input_controller](</E:/Repositories/QuakeLive-reverse/src/code/jpeg-6/jdinput.c:339>),
  and [jinit_input_controller](</E:/Repositories/QuakeLive-reverse/src/code/jpeg-6/jdinput.c:361>).
- `sub_47DA20` is especially stable because the HLIL reproduces the exact
  `initial_setup` ownership split between first-SOS size/precision checks,
  max sampling-factor discovery, component block geometry, and the final
  `has_multiple_scans` decision.
- `sub_47DEB0` is anchored by the exact three-way marker-consume state
  ladder and the two distinctive branches that matter in practice: first SOS
  calling `initial_setup`, later SOS calling `start_input_pass`.

## Aliases Added

- `sub_47DA20` -> `initial_setup`
- `sub_47DC20` -> `per_scan_setup`
- `sub_47DDC0` -> `latch_quant_tables`
- `sub_47DE60` -> `start_input_pass`
- `sub_47DEB0` -> `consume_markers`
- `sub_47DF70` -> `reset_input_controller`
- `sub_47DFB0` -> `finish_input_pass`
- `sub_47DFD0` -> `jinit_input_controller`

## Verification

Static mapping validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- scoped duplicate-key scan for the `quakelive_steam` alias block passed with
  `0` duplicates
- recount after this pass: `2061` raw alias entries, `1989` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `36.342%` of `5473` functions
- `git diff --check` passed aside from the repo's existing LF -> CRLF
  normalization warnings on touched text files
- no build or runtime launch was needed; this was mapping-only work on the
  committed evidence corpus

## Parity Estimate

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

The next pass can keep climbing the remaining support-library seam at
`sub_409670`, return to the persistent STL/host head at `sub_41AD70`, or
pivot back into the larger engine-owned leftovers around `sub_4E6730` and
`sub_4B4100`.
