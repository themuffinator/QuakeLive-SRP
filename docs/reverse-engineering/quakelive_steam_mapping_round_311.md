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
   arena-name hook and the `.dm_73` demo argument scan.

## Evidence Notes

- Canonical HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
  at `0x004B6A60`, `0x004B7660`, `0x004C82F0`, `0x004CB950`, and
  `0x004CCDF0`.
- Companion corpus:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  lists `FUN_004b6a60`, `FUN_004b7660`, `FUN_004c82f0`, `FUN_004cb950`, and
  `FUN_004ccdf0` with sizes matching the inspected HLIL bodies.
- Existing source anchors:
  `src/code/client/cl_keys.c`, `src/code/qcommon/common.c`,
  `src/code/qcommon/cmd.c`, and `src/code/qcommon/cvar.c`.

## Aliases Added

- `sub_4CCDF0` -> `Cvar_CommandCompletion`

Recount after this pass:

- `2445` raw `quakelive_steam` alias entries
- `2439` strict Ghidra address-backed aliases
- `44.564%` address-backed coverage over the `5473` function baseline

## Verification

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
- `python -m pytest tests/test_engine_command_parity.py::test_console_autocomplete_matches_retail_argument_sources_and_field_rebuild -q --tb=short`
- `python -m pytest tests/test_engine_command_parity.py -q --tb=short`
- `git diff --check -- src/code/qcommon/cvar.c src/code/qcommon/common.c src/code/qcommon/qcommon.h src/code/client/cl_keys.c tests/test_engine_command_parity.py references/analysis/quakelive_symbol_aliases.json docs/reverse-engineering/quakelive_steam_mapping_round_311.md`

Parity estimate for this scoped console auto-completion surface:

- before: `96%`
- after: `100%`

Repo-wide checked-in tree parity remains estimated at `98%`; this closes a
small source-visible completion mismatch rather than a broad subsystem gap.
