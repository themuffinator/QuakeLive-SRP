# Quake Live Steam Mapping Round 193

## Scope

This round returns to mapping-only work in the retained IJG JPEG seam and
closes two adjacent support-library families: the decompressor
postprocessing controller in `jdpostct.c` and the compressor color
converter in `jccolor.c`.

Primary evidence for this pass:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `src/code/jpeg-6/jdpostct.c`
- `src/code/jpeg-6/jccolor.c`
- `src/code/jpeg-6/jmorecfg.h`

## Summary

This round adds `11` exact `quakelive_steam.exe` aliases and corrects `1`
older JPEG misread.

Classification mix:

- `0` engine-owned functions
- `0` platform-service-owned functions
- `12` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The useful outcome is that the old anonymous slab from `0x00475020` through
`0x00475AB0` now reads as exact retained IJG ownership instead of mixed
opaque color/pipeline glue. The pass also fixes the stale
`sub_474D90 -> decompress_onepass` alias: that function is actually the
`jdpostct.c` strip-buffer owner `post_process_1pass`, while the real
coefficient-controller `decompress_onepass` remains correctly mapped at
`sub_47C4F0`.

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_474D90` | `642` | support-library | `post_process_1pass` | High | Corrected from the older `decompress_onepass` placeholder. The mode switch at `sub_475400` and the strip-buffer fill -> quantize -> emit body match `jdpostct.c` exactly. |
| 2 | `sub_475020` | `480` | support-library | `post_process_prepass` | High | Closed from the exact first-pass 2-pass quantizer flow: reposition virtual strip when `next_row == 0`, upsample into `post->buffer`, let `cquantize` scan the new rows with null output, then roll `starting_row` once the strip fills. |
| 3 | `sub_475200` | `497` | support-library | `post_process_2pass` | High | Closed from the exact second-pass quantizer flow: reopen the current strip read-only, bound `num_rows` by strip/output/image height, emit through `color_quantize`, then advance `next_row` and `starting_row`. |
| 4 | `sub_475400` | `234` | support-library | `start_pass_dpost` | High | Closed from the exact `JBUF_PASS_THRU` / `JBUF_SAVE_AND_PASS` / `JBUF_CRANK_DEST` dispatcher and the virtual-buffer presence checks. |
| 5 | `sub_4754F0` | `274` | support-library | `jinit_d_post_controller` | High | Closed from the exact post-controller allocation and the split strip-buffer versus whole-image setup. |
| 6 | `sub_475610` | `199` | support-library | `rgb_ycc_start` | High | Closed from the exact eight-section `rgb_ycc_tab` allocation and the fixed-point fill constants for `R_Y_OFF` through `B_CR_OFF`. |
| 7 | `sub_4756E0` | `269` | support-library | `rgb_ycc_convert` | High | Closed from the exact RGB-to-YCbCr inner loop over interleaved `RGB_PIXELSIZE` input with three separate output component planes. |
| 8 | `sub_4757F0` | `143` | support-library | `rgb_gray_convert` | High | Closed from the exact RGB-to-luma-only path using the shared `rgb_ycc_tab` Y coefficients. |
| 9 | `sub_475880` | `320` | support-library | `cmyk_ycck_convert` | High | Closed from the exact Adobe-style `R=255-C`, `G=255-M`, `B=255-Y` conversion while passing `K` through unchanged. |
| 10 | `sub_4759D0` | `89` | support-library | `grayscale_convert` | High | Closed from the exact row-copy loop that forwards the first input component using `input_components` stride. |
| 11 | `sub_475A30` | `120` | support-library | `null_convert` | High | Closed from the exact per-component split-plane fill loop used for no-conversion compression input. |
| 12 | `sub_475AB0` | `441` | support-library | `jinit_color_converter` | High | Closed from the exact `in_color_space` / `jpeg_color_space` validation ladder and the converter-method selection matrix. |

## Evidence Notes

- The decisive source anchors are
  [post_process_1pass](</E:/Repositories/QuakeLive-reverse/src/code/jpeg-6/jdpostct.c:126>),
  [post_process_prepass](</E:/Repositories/QuakeLive-reverse/src/code/jpeg-6/jdpostct.c:158>),
  [post_process_2pass](</E:/Repositories/QuakeLive-reverse/src/code/jpeg-6/jdpostct.c:202>),
  [start_pass_dpost](</E:/Repositories/QuakeLive-reverse/src/code/jpeg-6/jdpostct.c:73>),
  [jinit_d_post_controller](</E:/Repositories/QuakeLive-reverse/src/code/jpeg-6/jdpostct.c:250>),
  [rgb_ycc_start](</E:/Repositories/QuakeLive-reverse/src/code/jpeg-6/jccolor.c:86>),
  [rgb_ycc_convert](</E:/Repositories/QuakeLive-reverse/src/code/jpeg-6/jccolor.c:130>),
  [rgb_gray_convert](</E:/Repositories/QuakeLive-reverse/src/code/jpeg-6/jccolor.c:186>),
  [cmyk_ycck_convert](</E:/Repositories/QuakeLive-reverse/src/code/jpeg-6/jccolor.c:225>),
  [grayscale_convert](</E:/Repositories/QuakeLive-reverse/src/code/jpeg-6/jccolor.c:280>),
  [null_convert](</E:/Repositories/QuakeLive-reverse/src/code/jpeg-6/jccolor.c:309>),
  and [jinit_color_converter](</E:/Repositories/QuakeLive-reverse/src/code/jpeg-6/jccolor.c:352>).
- The `jccolor.c` closure depends on the repo's retained
  [RGB_PIXELSIZE == 4 configuration](</E:/Repositories/QuakeLive-reverse/src/code/jpeg-6/jmorecfg.h:302>).
  That explains why the retail `JCS_RGB` validation and stride logic differ
  from stock 3-byte RGB builds but still match the checked-in source exactly.
- `sub_474D90` is decisively not `decompress_onepass`: the real
  coefficient-controller owner was already corrected earlier at
  `sub_47C4F0`, while `sub_474D90` sits under the exact `start_pass_dpost`
  pass-mode dispatcher beside `post_process_prepass` and `post_process_2pass`.

## Aliases Added

- `sub_475020` -> `post_process_prepass`
- `sub_475200` -> `post_process_2pass`
- `sub_475400` -> `start_pass_dpost`
- `sub_4754F0` -> `jinit_d_post_controller`
- `sub_475610` -> `rgb_ycc_start`
- `sub_4756E0` -> `rgb_ycc_convert`
- `sub_4757F0` -> `rgb_gray_convert`
- `sub_475880` -> `cmyk_ycck_convert`
- `sub_4759D0` -> `grayscale_convert`
- `sub_475A30` -> `null_convert`
- `sub_475AB0` -> `jinit_color_converter`

## Alias Corrected

- `sub_474D90`: `decompress_onepass` -> `post_process_1pass`

## Verification

Static mapping validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- scoped duplicate-key scan for the `quakelive_steam` alias block passed with
  `0` duplicates
- recount after this pass: `2053` raw alias entries, `1981` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `36.196%` of `5473` functions
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
| 4 | `0x0047DA20` | `FUN_0047da20` | `497` |
| 5 | `0x00409670` | `FUN_00409670` | `496` |
| 6 | `0x004B3672` | `FUN_004b3672` | `495` |
| 7 | `0x0041C400` | `FUN_0041c400` | `492` |
| 8 | `0x00414AC0` | `FUN_00414ac0` | `490` |
| 9 | `0x0046A420` | `FUN_0046a420` | `490` |
| 10 | `0x004DC730` | `FUN_004dc730` | `490` |

The next pass can keep climbing the remaining JPEG seam at `sub_47DA20`,
return to the persistent STL/host head at `sub_41AD70`, or pivot back into
the larger engine-owned leftovers around `sub_4E6730` and `sub_4B4100`.
