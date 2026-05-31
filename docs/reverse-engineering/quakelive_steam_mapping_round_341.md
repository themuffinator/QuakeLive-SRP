# Quake Live Steam Host Mapping Round 341

Scope: renderer post-process command payload execution wiring.

## Evidence

Owning retail binary:

- `assets/quakelive/quakelive_steam.exe`

Committed evidence used:

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `references/analysis/quakelive_symbol_aliases.json`

Observed facts:

- `RB_ColorCorrectPostProcessCommand` at `0x00436DC0` consumes the queued
  command texture at `arg1 + 4` and program at `arg1 + 8`, then returns
  `arg1 + 0x10`.
- `R_AddColorCorrectPostProcessCommand` at `0x0043CD10` allocates a `0x10`
  command, writes command ID `9`, and stores the color-correct texture/program
  handles.
- `R_AddBloomPostProcessCommand` at `0x004384D0` allocates a `0x38` command,
  writes command ID `0xa`, and stores eight bloom texture handles plus five
  program handles.
- `RB_BloomPostProcessCommand` at `0x00436EC0` consumes those command payload
  handles while running the downsample, bright-pass, blur, optional
  quarter-resolution, and combine passes, then returns `arg1 + 0x38`.

Inference:

- The command-buffer ABI is not just structural size/order. Retail uses the
  queued handles as the execution source of truth, while framebuffer selection
  remains owned by the recovered render-target globals.

## Source Update

- `RBPP_ApplyColorCorrectPass` now takes the typed color-correct command and
  binds the queued texture/program handles.
- `RBPP_ApplyBloom` now takes the typed bloom command and uses the queued
  texture/program handles for every pass in the bloom chain.
- The bloom fallback blit now presents the queued scene texture instead of
  re-reading the live scene target texture handle.
- The existing command emitters still populate the recovered `0x10` and
  `0x38` payloads, and the backend handlers now pass those payloads through to
  execution.

## Parity Estimate

- Post-process command payload wiring lane: before 99.99%, after 100%.
- Strict renderer estimate remains 100%.
- Repo-wide estimate remains 98% until unrelated portability, packaging,
  online-service, and source-legacy surfaces are closed.

## Verification

- `python -m pytest tests/test_renderer_post_process_parity.py tests/test_renderer_internal_helper_mapping_parity.py tests/test_renderer_export_tail_parity.py tests/test_renderer_full_parity_gate.py -q --tb=short`
  - Result: `47 passed, 1 skipped`.
