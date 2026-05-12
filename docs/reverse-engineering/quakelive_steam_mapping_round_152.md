# quakelive_steam.exe Mapping Round 152

Date: 2026-04-27

Scope: source-backed support-library mapping for the embedded IJG JPEG color
deconverter lane. This pass stayed mapping-only and anchored the `0x47C810`
through `0x47CBF0` slab against the checked-in `jdcolor.c` source plus the
committed HLIL.

## Summary

This round resolved `6` additional `quakelive_steam.exe` rows. Classification
mix:

- `0` engine-owned functions
- `0` platform-service-owned functions
- `6` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main outcome is that the next decompressor-adjacent support block now
reads as exact retained IJG color-space conversion code rather than anonymous
sample-shuffle helpers:

- `sub_47C810` and `sub_47C8E0` close the YCbCr-to-RGB table-build and
  conversion lane around `build_ycc_rgb_table` and `ycc_rgb_convert`
- `sub_47CA00` and `sub_47CA80` close the exact pass-through and grayscale
  conversion helpers `null_convert` and `grayscale_convert`
- `sub_47CAB0` and `sub_47CBF0` close the YCCK path and top-level converter
  initializer `ycck_cmyk_convert` and `jinit_color_deconverter`

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_47CBF0` | `330` | support-library | `jinit_color_deconverter` | High | Closed from the exact allocator and dispatch surface: install the start-pass stub, validate component counts against `jpeg_color_space`, choose `null_convert` or `grayscale_convert` for identity/grayscale paths, and call `build_ycc_rgb_table` before installing the YCbCr or YCCK converters. |
| 2 | `sub_47CAB0` | `307` | support-library | `ycck_cmyk_convert` | High | Closed from the four-plane Y/Cb/Cr/K walk and the exact inverted RGB equations (`MAXJSAMPLE - ...`) with K passed through unchanged, which is unique to the IJG YCCK-to-CMYK converter. |
| 3 | `sub_47C8E0` | `273` | support-library | `ycc_rgb_convert` | High | Closed from the table-driven three-plane Y/Cb/Cr readout, the precomputed `Cr_r_tab`/`Cb_b_tab`/`Cr_g_tab`/`Cb_g_tab` usage, and the interleaved RGB write pattern. |
| 4 | `sub_47C810` | `202` | support-library | `build_ycc_rgb_table` | High | Closed from the exact four-table allocation and fill formulas for the JPEG color deconverter's `Cr_r_tab`, `Cb_b_tab`, `Cr_g_tab`, and `Cb_g_tab` precomputation pass. |
| 5 | `sub_47CA00` | `118` | support-library | `null_convert` | High | Closed from the identity interleave loop that copies `num_components` separate input planes into packed output rows without color transform. |

## Evidence Notes

- `sub_47C810` is the exact `jdcolor.c` table-builder. The HLIL shows four
  `0x400`-entry allocations followed by the same fixed-point constants used by
  IJG to precompute the red, blue, and green contribution tables for Cr/Cb.
- `sub_47C8E0` is exact `ycc_rgb_convert`: it consumes three input component
  planes, looks up the precomputed Cr/Cb tables, range-limits the result, and
  emits packed RGB triples row by row.
- `sub_47CA80` is exact `grayscale_convert`, not a generic copier. The body is
  just the one-plane sample-row copy wrapper used when the output colorspace is
  grayscale.
- `sub_47CA00` stays distinct from `grayscale_convert` because it interleaves
  an arbitrary `num_components` worth of source planes into packed output and
  therefore matches the `null_convert` path used for already-matching color
  spaces.
- `sub_47CBF0` is the exact `jinit_color_deconverter` initializer. The HLIL
  matches the color-space/component-count validation matrix plus the method
  dispatch to `grayscale_convert`, `null_convert`, `ycc_rgb_convert`, or
  `ycck_cmyk_convert`, with the YCbCr/YCCK cases both calling the same table
  builder first.

## Aliases Added

- `sub_47C810` -> `build_ycc_rgb_table`
- `sub_47C8E0` -> `ycc_rgb_convert`
- `sub_47CA00` -> `null_convert`
- `sub_47CA80` -> `grayscale_convert`
- `sub_47CAB0` -> `ycck_cmyk_convert`
- `sub_47CBF0` -> `jinit_color_deconverter`

## Verification

Static mapping validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- scoped duplicate-key scan for the `quakelive_steam` alias block passed with
  `0` duplicates
- recount after this pass: `1742` raw alias entries, `1671` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `30.532%` of `5473` functions
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
`sub_4940D0`, `sub_4F4410`, and `sub_4999C0`, or keep harvesting adjacent JPEG
decompressor helpers where the emitted binaries still stay one-to-one with the
checked-in IJG source.
