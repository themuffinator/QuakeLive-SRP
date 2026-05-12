# quakelive_steam.exe Mapping Round 151

Date: 2026-04-27

Scope: source-backed support-library mapping for the embedded IJG JPEG
decompressor control/API lane. This pass stayed mapping-only and anchored the
`0x47AC10` through `0x47C260` slab against the checked-in `jdmainct.c`,
`jdapimin.c`, and `jdapistd.c` sources plus the committed HLIL.

## Summary

This round resolved `11` additional `quakelive_steam.exe` rows. Classification
mix:

- `0` engine-owned functions
- `0` platform-service-owned functions
- `11` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main outcome is that the adjacent decompressor control surface now reads as
exact retained IJG code rather than anonymous state-machine glue:

- `sub_47AC10`, `sub_47AC60`, and `sub_47B1F0` close the `jdmainct.c`
  main-buffer-controller lane around `start_pass_main`,
  `process_data_simple_main`, and `jinit_d_main_controller`, with the already
  mapped `process_data_context_main` still acting as the context-row anchor
- `sub_47BCD0` through `sub_47C260` close the top-level decompressor API lane
  from object creation and default-parameter setup through header consumption,
  startup, output-pass setup, scanline reads, and final teardown
- the compiler-extracted helper surface around the funny-pointer setup and the
  surrounding upsample internals remains intentionally unpromoted here because
  those emitted bodies do not stay one-to-one with a single checked-in source
  function

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_47AC60` | `473` | support-library | `process_data_simple_main` | High | Closed from the exact single-pass main-buffer flow: fill `jmain->buffer` once via `coef->decompress_data`, expose `min_DCT_scaled_size` row groups, and reset `buffer_full` when `rowgroup_ctr` drains. |
| 2 | `sub_47BD60` | `454` | support-library | `default_decompress_parms` | High | Closed from the exact colorspace guesswork over `num_components`, JFIF/Adobe/component-ID handling, and the terminal default-policy field writes for scaling, gamma, fancy upsampling, block smoothing, and quantization. |
| 3 | `sub_47C000` | `202` | support-library | `jpeg_finish_decompress` | High | Closed from the `DSTATE_SCANNING`/`DSTATE_RAW_OK`/`DSTATE_BUFIMAGE` state machine, the trailer `consume_input` loop until EOI, `term_source`, and the terminal `jpeg_abort` cleanup. |
| 4 | `sub_47B1F0` | `185` | support-library | `jinit_d_main_controller` | High | Closed from the exact main-controller allocation, `start_pass_main` install, `need_full_buffer` rejection, and the split between context-row and non-context-row workspace setup. |
| 5 | `sub_47BF30` | `167` | support-library | `jpeg_consume_input` | High | Closed from the `DSTATE_START`/`DSTATE_INHEADER`/`DSTATE_READY` transition logic, `reset_input_controller`, `init_source`, delegated `consume_input`, and the `default_decompress_parms` handoff on SOS. |

## Evidence Notes

- `sub_47BCD0` is the exact `jpeg_create_decompress` body: it preserves
  `err`, zeroes the whole `jpeg_decompress_struct`, sets
  `is_decompressor = TRUE`, initializes the memory manager, clears the quant
  and Huffman table pointers, then installs the marker reader and input
  controller before setting `global_state = DSTATE_START`.
- `sub_47C0D0` is the exact `jpeg_read_header` front end. The HLIL shows the
  required `DSTATE_START`/`DSTATE_INHEADER` gate, the delegated
  `jpeg_consume_input` call, the `JPEG_REACHED_SOS` to `JPEG_HEADER_OK`
  rewrite, and the `JPEG_REACHED_EOI` plus `require_image` handling that
  falls back to `jpeg_abort` before returning the tables-only result.
- `sub_47C150` and `sub_47C260` line up as the `jdapistd.c` pair
  `output_pass_setup` and `jpeg_start_decompress`: the first performs the
  `prepare_for_output_pass` setup and final raw/scanning state selection,
  while the second handles the `DSTATE_READY` and `DSTATE_PRELOAD` entry logic
  before tail-calling `output_pass_setup`.
- `sub_47AC10` is exact `start_pass_main`, not a generic buffer reset helper.
  The HLIL matches the `JBUF_PASS_THRU` switch, the context-row branch that
  installs `process_data_context_main` and rebuilds the funny-pointer lists,
  and the common `buffer_full`/`rowgroup_ctr` reset.
- I intentionally did not promote the surrounding `sub_47B0E0` and
  `sub_47B2C0` bodies this round. They clearly belong to the `jdmainct.c`
  funny-pointer setup, but the emitted code fuses source-local helper work in
  a way that does not hold a stable one-function-to-one-function mapping.

## Aliases Added

- `sub_47AC10` -> `start_pass_main`
- `sub_47AC60` -> `process_data_simple_main`
- `sub_47B1F0` -> `jinit_d_main_controller`
- `sub_47BCD0` -> `jpeg_create_decompress`
- `sub_47BD60` -> `default_decompress_parms`
- `sub_47BF30` -> `jpeg_consume_input`
- `sub_47C000` -> `jpeg_finish_decompress`
- `sub_47C0D0` -> `jpeg_read_header`
- `sub_47C150` -> `output_pass_setup`
- `sub_47C1C0` -> `jpeg_read_scanlines`
- `sub_47C260` -> `jpeg_start_decompress`

## Verification

Static mapping validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- scoped duplicate-key scan for the `quakelive_steam` alias block passed with
  `0` duplicates
- recount after this pass: `1736` raw alias entries, `1665` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `30.422%` of `5473` functions
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
`sub_4940D0`, `sub_4F4410`, and `sub_4999C0`, or keep harvesting the nearby
JPEG decompressor helpers that remain bounded but not yet one-to-one promoted.
