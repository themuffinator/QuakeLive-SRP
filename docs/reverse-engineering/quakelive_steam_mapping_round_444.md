# quakelive_steam.exe Mapping Round 444

Date: 2026-06-08

Scope: native UI sound import-table wiring for shared engine sound wrappers.

## Summary

This round maps the UI-side native sound slots in the retail Steam executable
against the source UI import bridge. Retail reuses the same tiny engine sound
wrappers that the native cgame import table uses:

- UI slot 34: `sub_4BEFB0`, tailcalling `S_StartLocalSound`
- UI slot 35: `sub_4AFEC0`, tailcalling `S_RegisterSound`
- UI slot 71: raw thunk `0x4B02F0`, tailcalling `S_StopBackgroundTrack`
- UI slot 72: `sub_4AFED0`, tailcalling `S_StartBackgroundTrack`

No source behavior change was needed in this round. The existing source bridge
already wires those UI slots to the matching engine helpers and keeps the
Quake Live-specific `QL_UI_trap_S_RegisterSound_QL()` normalization for native
UI callers that pass non-boolean compressed values.

## Evidence

Primary evidence:

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part07.txt`
- `references/analysis/quakelive_symbol_aliases.json`
- `src/code/client/cl_ui.c`
- `src/code/client/ql_ui_imports.inc`
- `src/code/ui/ui_public.h`
- `src/code/ui/ui_syscalls.c`

Observed facts:

1. `functions.csv` records `FUN_004befb0` size `9`, `FUN_004afec0` size `9`,
   `FUN_004afed0` size `9`, and `FUN_004db030` size `35`.
2. HLIL part 04 shows `sub_4BEFB0` tailcalling `sub_4DB3F0`
   (`S_StartLocalSound`), `sub_4AFEC0` tailcalling `sub_4D9E50`
   (`S_RegisterSound`), and `sub_4AFED0` tailcalling `sub_4DB060`
   (`S_StartBackgroundTrack`).
3. HLIL part 04 also shows a retail call to `sub_4DB030`; part 07 records UI
   slot `0x00567454` as raw thunk `0x4B02F0`, the compact stop-background-track
   table entry next to the parser-source wrappers.
4. HLIL part 07 records UI sound slots:
   `data_5673C0 = sub_4BEFB0`, `data_5673C4 = sub_4AFEC0`,
   `data_567454 = 0x4B02F0`, and `data_567458 = sub_4AFED0`.
5. The source `uiQlImport_t` enum maps those same behaviors to slots 34, 35,
   71, and 72, and `CL_InitUIImports()` assigns the matching `QL_UI_trap_S_*`
   wrappers.

## Test Reconstruction

`tests/test_ui_menu_files.py` now pins the UI native sound bridge against:

- alias-table names for the shared sound wrappers
- Ghidra function rows and sizes
- Binary Ninja HLIL wrapper tailcalls
- Binary Ninja HLIL UI import-table entries
- source-side `CL_InitUIImports()` assignments
- source-side `ql_ui_imports.inc` legacy syscall wrapper shapes

## Verification

Commands run:

- `python -m json.tool references\analysis\quakelive_symbol_aliases.json > $null`
  -> passed
- `python -m pytest tests\test_ui_menu_files.py::test_ui_native_import_table_matches_recovered_retail_slots tests\test_platform_services.py::test_module_side_syscall_wrappers_normalize_qboolean_contracts -q --tb=short`
  -> `2 passed`
- `git diff --check -- tests\test_ui_menu_files.py docs\reverse-engineering\quakelive_steam_mapping_round_444.md`
  -> passed with only an LF-to-CRLF working-copy warning on the touched test file

## Parity Estimate

- Focused native UI sound import wiring confidence: **82% -> 94%**.
- Focused UI sound bridge source behavior confidence: **94% -> 95%**.
- Broader client sound-system wiring confidence: **88% -> 89%**.
- Repo-wide checked-in tree parity: **99% -> 99%**.
