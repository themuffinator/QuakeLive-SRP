# quakelive_steam.exe Mapping Round 311

Date: 2026-05-25

Scope: console auto-line-completion and the retained command/cvar/UI/demo
argument-completion wiring.

## Summary

This round rechecked the console completion path across the retail Steam host
and source-reconstructed the one stale cvar-completion detail left behind by
the older source shape.

- `sub_4B7660` remains the `Console_Key` owner. The `K_TAB` branch calls
  `Field_CompleteCommand` with the console edit field and the retained
  `Console_CompleteArgument` callback.
- `sub_4CB950` remains the shared `Field_CompleteCommand` owner. It tokenizes
  the edit field, tracks the active token in the shared completion globals,
  gathers command names, cvar names, and command-specific argument candidates,
  rebuilds the line with the recovered leading `\` policy, and prints the
  multi-match list.
- `sub_4B6A60` remains `Console_CompleteArgument`. The HLIL first reaches the
  native UI arena-name iterator when the UI export table is available, then
  accepts only `demo`/`\demo` for the filesystem argument pass and enumerates
  `demos/*.dm_73`.
- `uix86.dll` `sub_10003930` is the UI arena-name iterator used by that host
  callback. Its arena-list walk calls back the first map-list pointer, which
  `UI_LoadArenas` also feeds into `levelshots/preview/%s`; source therefore
  returns `mapLoadName` map tokens rather than the long display-name field.
- `sub_4C82F0` remains `Cmd_CommandCompletion`, the simple command-list
  callback walker.
- `sub_4CCDF0` is now promoted as `Cvar_CommandCompletion`. The second
  parameter is retail-significant: the discovery pass calls candidates back as
  bare cvar names, while the multi-match print pass calls back
  `name = "value"` strings so the console displays current cvar values.

## Source Reconstruction

The writable source now mirrors that two-phase cvar callback contract:

1. `Cvar_CommandCompletion` takes `qboolean includeValues`.
2. `Field_CompleteCommand` calls `Cvar_CommandCompletion( FindMatches, qfalse )`
   while gathering the common prefix.
3. The multi-match print path calls
   `Cvar_CommandCompletion( PrintMatches, matchCount > 1 ? qtrue : qfalse )`,
   matching the retail `arg2 == 1` formatting branch in `sub_4CCDF0`.
4. The client-side completion callback still keeps the recovered native UI
   arena map-token hook and the `.dm_73` demo argument scan.

Follow-up wiring recheck on 2026-06-05:

- `Console_Key` routes `K_TAB` to `Field_CompleteCommand` with
  `Console_CompleteArgument`.
- `Cmd_CommandCompletion`, `Cvar_CommandCompletion`, `FindMatches`,
  `PrintMatches`, and the shared field rebuild keep the observed retail walker
  order, prefix matching, common-prefix clipping, cvar value-print branch, and
  leading-backslash rebuild behavior.
- `VM_CallNativeExports` preserves the QL native UI export index adjustment
  (`callnum - 1`) so the legacy `UI_FOR_EACH_ARENA_NAME` call reaches
  `UI_NATIVE_EXPORT_FOR_EACH_ARENA_NAME` in the recovered native table.
- `UI_ForEachArenaName` now returns executable map tokens from `mapLoadName`,
  while the separate UI feeder/display paths continue to use long display
  names where retail does.

## Evidence Notes

- Canonical HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
  at `0x004B6A60`, `0x004B7660`, `0x004C82F0`, `0x004CB950`, and
  `0x004CCDF0`.
  `references/hlil/quakelive/uix86.all/uix86.dll_hlil_split/uix86.dll_hlil_part01.txt`
  at `0x10003930` and `0x10003190` confirms the UI callback uses the
  map-token pointer.
- Companion corpus:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  lists `FUN_004b6a60`, `FUN_004b7660`, `FUN_004c82f0`, `FUN_004cb950`, and
  `FUN_004ccdf0` with sizes matching the inspected HLIL bodies.
- Existing source anchors:
  `src/code/client/cl_keys.c`, `src/code/qcommon/common.c`,
  `src/code/qcommon/cmd.c`, `src/code/qcommon/cvar.c`, and
  `src/code/ui/ui_main.c`.

## Aliases Added

- `sub_4CCDF0` -> `Cvar_CommandCompletion`

Recount after this pass:

- `2445` raw `quakelive_steam` alias entries
- `2439` strict Ghidra address-backed aliases
- `44.564%` address-backed coverage over the `5473` function baseline

## Verification

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
- `python -m pytest tests/test_engine_command_parity.py::test_console_autocomplete_matches_retail_argument_sources_and_field_rebuild -q --tb=short`
- `python -m pytest tests/test_ui_menu_files.py::test_ui_native_export_table_matches_recovered_retail_order -q --tb=short`
- `python -m pytest tests/test_engine_command_parity.py -q --tb=short`
- `git diff --check -- src/code/ui/ui_main.c tests/test_engine_command_parity.py docs/reverse-engineering/quakelive_steam_mapping_round_311.md`

Parity estimate for this scoped console auto-completion surface:

- before: `96%`
- after: `100%`

Repo-wide checked-in tree parity remains estimated at `98%`; this closes a
small source-visible completion mismatch rather than a broad subsystem gap.
