# quakelive_steam.exe Mapping Round 149

Date: 2026-04-27

Scope: source-backed support-library mapping for the embedded IJG JPEG
compressor lanes plus one exact MSVC locale helper at the queue head. This
pass stayed mapping-only and anchored the `0x475***` through `0x479***` slab
against the checked-in `src/code/jpeg-6` source tree and the committed HLIL.

## Summary

This round resolved `32` additional `quakelive_steam.exe` rows. Classification
mix:

- `0` engine-owned functions
- `0` platform-service-owned functions
- `32` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main outcome is that the previously anonymous JPEG compressor tranche now
reads as exact retained IJG code rather than generic codec glue:

- `jcdctmgr.c` is now anchored by `start_pass_fdctmgr` beside the already named
  `forward_DCT_float`
- `jcmarker.c` now has its full marker-writer ladder named from `emit_dqt`
  through `jinit_marker_writer`
- `jcmaster.c` now has the exact initial-setup, scan-setup, pass-setup, and
  master-control helpers promoted
- `jcomapi.c` and `jcparam.c` now expose the JPEG object lifecycle, default
  table setup, colorspace selection, and quality-setting helpers used by the
  screenshot/save-JPEG path
- the compiler-inlined helpers stay intentionally unmapped as standalone names:
  `jpeg_quality_scaling`, `jpeg_set_linear_quality`, and `add_huff_table` were
  folded into their emitted callers in this build

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_403BB0` | `537` | support-library | `std::money_get<char,class std::istreambuf_iterator<char,struct std::char_traits<char> > >::_Getmfld` | High | Closed from the exact HLIL title; this is a pure MSVC locale/monetary parsing helper. |
| 2 | `sub_475CA0` | `545` | support-library | `start_pass_fdctmgr` | High | Closed from the checked-in `jcdctmgr.c` divisor-table setup, including the float `aanscalefactor` lane and the `JDCT_FLOAT` allocation path. |
| 3 | `sub_477930` | `536` | support-library | `emit_dqt` | High | Closed from the `0xFF 0xDB` marker emission, 8-bit versus 16-bit precision probe, and `sent_table` latch. |
| 4 | `sub_478870` | `471` | support-library | `initial_setup` | High | Closed from the `jcmaster.c` dimension, component-count, sampling-factor, and `total_iMCU_rows` setup logic. |
| 5 | `sub_479500` | `432` | support-library | `jpeg_add_quant_table` | High | Closed from the quant-table scale/clamp loop and the `sent_table = FALSE` reset. |
| 6 | `sub_479D50` | `245` | support-library | `jpeg_set_defaults` | High | Closed from the default precision, quality-75 table setup, standard Huffman-table init, restart/JFIF defaults, and terminal `jpeg_default_colorspace` call. |

## Evidence Notes

- `sub_478800` allocates a `0x18` marker-writer vtable object and stores the
  exact six method pointers in the same order as `jcmarker.c`:
  `write_any_marker`, `write_file_header`, `write_frame_header`,
  `write_scan_header`, `write_file_trailer`, and `write_tables_only`. That
  closes `sub_4783E0` through `sub_478800` as one exact `jcmarker.c` tranche.
- `sub_479380` allocates a `0x20` master-control object, wires
  `prepare_for_pass`, `pass_startup`, and `finish_pass_master`, then runs
  `initial_setup`, optional `jpeg_validate_script`, and the `transcode_only`
  pass-type selection. That is the exact `jinit_c_master_control` body from
  `jcmaster.c`.
- `sub_479440` calls the memory-manager `free_pool` path and then resets
  `global_state` to `0x64` or `0xC8` depending on `is_decompressor`, matching
  `jpeg_abort`. `sub_479470` then matches `jpeg_destroy` by calling
  `self_destruct`, nulling `mem`, and zeroing `global_state`.
- `sub_4796B0` is reached directly from the screenshot/save-JPEG path at
  `0x00446966` immediately after `sub_479D50`, computes the standard
  quality-scaling curve, and then rebuilds the luminance and chrominance
  quantization tables through `sub_479500`. In this build that emitted body is
  the exact `jpeg_set_quality` surface.
- `sub_479720` writes the hard-coded standard luminance/chrominance Huffman
  `bits[]` and `huffval[]` tables into four `JHUFF_TBL` objects. The smaller
  `add_huff_table` helper is not emitted as a standalone function here; the
  compiler folded it into `std_huff_tables`.
- `sub_4798A0` covers all six `J_COLOR_SPACE` cases and writes the exact
  component IDs and sampling defaults from `jpeg_set_colorspace`, while
  `sub_479BC0` provides the matching `jpeg_default_colorspace` switch that maps
  `RGB` and `YCbCr` input to `JCS_YCbCr`.

## Aliases Added

- `sub_403BB0` -> `std::money_get<char,class std::istreambuf_iterator<char,struct std::char_traits<char> > >::_Getmfld`
- `sub_475CA0` -> `start_pass_fdctmgr`
- `sub_477930` -> `emit_dqt`
- `sub_477B50` -> `emit_dht`
- `sub_477D20` -> `emit_sof`
- `sub_477E90` -> `emit_sos`
- `sub_478060` -> `emit_jfif_app0`
- `sub_478270` -> `emit_adobe_app14`
- `sub_4783E0` -> `write_any_marker`
- `sub_478450` -> `write_file_header`
- `sub_478490` -> `write_frame_header`
- `sub_478580` -> `write_scan_header`
- `sub_478700` -> `write_file_trailer`
- `sub_478720` -> `write_tables_only`
- `sub_478800` -> `jinit_marker_writer`
- `sub_478870` -> `initial_setup`
- `sub_478E90` -> `select_scan_parameters`
- `sub_478F80` -> `per_scan_setup`
- `sub_479140` -> `prepare_for_pass`
- `sub_4792E0` -> `pass_startup`
- `sub_479310` -> `finish_pass_master`
- `sub_479380` -> `jinit_c_master_control`
- `sub_479440` -> `jpeg_abort`
- `sub_479470` -> `jpeg_destroy`
- `sub_4794A0` -> `jpeg_alloc_quant_table`
- `sub_4794D0` -> `jpeg_alloc_huff_table`
- `sub_479500` -> `jpeg_add_quant_table`
- `sub_4796B0` -> `jpeg_set_quality`
- `sub_479720` -> `std_huff_tables`
- `sub_4798A0` -> `jpeg_set_colorspace`
- `sub_479BC0` -> `jpeg_default_colorspace`
- `sub_479D50` -> `jpeg_set_defaults`

## Verification

Static mapping validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- scoped duplicate-key scan for the `quakelive_steam` alias block passed with
  `0` duplicates
- recount after this pass: `1714` raw alias entries, `1643` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `30.020%` of `5473` functions
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
embedded support-library surface such as the still-unmapped `sub_480030`
marker-reader helper.
