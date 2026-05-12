# quakelive_steam.exe Mapping Round 153

Date: 2026-04-27

Scope: source-backed support-library mapping for the retained IJG JPEG
compressor sampling lane plus the adjacent decompressor stdio source-manager
helpers. This pass stayed mapping-only and anchored the `0x47B2C0` through
`0x480030` slab against the checked-in `jcsample.c`, `jdatasrc.c`, and
`jdmarker.c` sources plus the committed HLIL.

## Summary

This round resolved `12` additional `quakelive_steam.exe` rows and corrected
`1` older over-specific JPEG alias. Classification mix:

- `0` engine-owned functions
- `0` platform-service-owned functions
- `12` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main outcome is that the previously anonymous `0x47B***` sampling slab now
reads as exact retained IJG compressor code rather than a misleading
decompressor-upsample cluster:

- `sub_47B2C0` through `sub_47BB50` close the `jcsample.c` downsampler lane
  around `sep_downsample`, `int_downsample`, `fullsize_downsample`,
  `h2v1_downsample`, `h2v2_downsample`, `h2v2_smooth_downsample`,
  `fullsize_smooth_downsample`, and `jinit_downsampler`
- `sub_47C300` through `sub_47C3F0` close the retained `jdatasrc.c` stdio
  source-manager helpers `init_source`, `fill_input_buffer`,
  `skip_input_data`, and `jpeg_stdio_src`
- `sub_480030` closes the marker-recovery helper `jpeg_resync_to_restart`,
  which also retires one of the current queue-head JPEG leftovers

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_480030` | `537` | support-library | `jpeg_resync_to_restart` | High | Closed from the exact marker-recovery state machine: classify unread markers into discard/scan/hold actions, emit the `must resync` warning, and tail into the `next_marker` scan loop when action `2` is chosen. |
| 2 | `sub_47BB50` | `376` | support-library | `jinit_downsampler` | High | Closed from the exact per-component sampling-ratio dispatch over `fullsize`, `2h1v`, `2h2v`, and integral-factor paths, plus the `CCIR601` rejection and `smoothing_factor`-driven context-row setup unique to `jcsample.c`. |
| 3 | `sub_47B350` | `377` | support-library | `int_downsample` | High | Closed from the generic integral-ratio box-filter body: call the edge-expander first, then average each `h_expand * v_expand` input cell group into one output sample. |
| 4 | `sub_47B710` | `654` | support-library | `h2v2_smooth_downsample` | High | Closed from the exact `memberscale` / `neighscale` weighted 2x2 smoothing math over one context row above and below; this also corrects the earlier mistaken decompressor-side alias. |
| 5 | `sub_47B9B0` | `400` | support-library | `fullsize_smooth_downsample` | High | Closed from the full-width smoothing body that consumes above/current/below rows with the `1-8*SF` versus `SF` weighting used only by the compressor-side fullsize smoother. |

## Evidence Notes

- `sub_47B2C0` is exact `sep_downsample`, not a decompressor helper. The HLIL
  walks `cinfo->comp_info`, computes `in_ptr = input_buf[ci] + in_row_index`
  and `out_ptr = output_buf[ci] + out_row_group_index * v_samp_factor`, then
  dispatches through the per-component method table exactly as `jcsample.c`
  does.
- `sub_47B4E0`, `sub_47B560`, and `sub_47B630` line up exactly as
  `fullsize_downsample`, `h2v1_downsample`, and `h2v2_downsample`. The first
  calls the row-copy helper then pads with the last sample, while the latter
  two implement the expected pairwise and 2x2 averaging loops with the same
  alternating-bias patterns as IJG.
- `sub_47B710` was previously over-labeled as
  `h2v2_fancy_upsample`. The HLIL instead shows the compressor-side smoothing
  weights `16384 - smoothing_factor * 80` and `smoothing_factor * 16`, plus
  the required above/below context rows, which is exact
  `h2v2_smooth_downsample`.
- `sub_47C300`, `sub_47C320`, `sub_47C370`, and `sub_47C3F0` are the retained
  `jdatasrc.c` lane. The `0x1000` buffer size, `infile` pointer bump,
  `bytes_in_buffer` / `next_input_byte` management, and source-manager vtable
  install match the checked-in `jpeg_stdio_src` implementation exactly.
- `sub_480030` is exact `jpeg_resync_to_restart`. The HLIL preserves the same
  three-action decision tree over unread marker class, emits the recovery
  trace and warning flow, scans forward with `next_marker` when action `2` is
  selected, and clears `unread_marker` only in the action-`1` discard case.

## Aliases Added

- `sub_47B2C0` -> `sep_downsample`
- `sub_47B350` -> `int_downsample`
- `sub_47B4E0` -> `fullsize_downsample`
- `sub_47B560` -> `h2v1_downsample`
- `sub_47B630` -> `h2v2_downsample`
- `sub_47B9B0` -> `fullsize_smooth_downsample`
- `sub_47BB50` -> `jinit_downsampler`
- `sub_47C300` -> `init_source`
- `sub_47C320` -> `fill_input_buffer`
- `sub_47C370` -> `skip_input_data`
- `sub_47C3F0` -> `jpeg_stdio_src`
- `sub_480030` -> `jpeg_resync_to_restart`

## Alias Correction

- `sub_47B710`: `h2v2_fancy_upsample` -> `h2v2_smooth_downsample`

## Verification

Static mapping validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- scoped duplicate-key scan for the `quakelive_steam` alias block passed with
  `0` duplicates
- recount after this pass: `1754` raw alias entries, `1683` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `30.751%` of `5473` functions
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
| 4 | `0x004FC240` | `FUN_004fc240` | `537` |
| 5 | `0x00466B90` | `FUN_00466b90` | `535` |
| 6 | `0x0051FF40` | `FUN_0051ff40` | `535` |
| 7 | `0x004FAF60` | `FUN_004faf60` | `534` |
| 8 | `0x00510410` | `FUN_00510410` | `533` |
| 9 | `0x00501ED0` | `FUN_00501ed0` | `529` |
| 10 | `0x00498BB0` | `FUN_00498bb0` | `526` |

The next pass can return to the large unresolved host leftovers at
`sub_4940D0`, `sub_4F4410`, and `sub_4999C0`, or keep harvesting adjacent IJG
helpers where the emitted compressor/decompressor support code still stays
one-to-one with the checked-in source.
