# quakelive_steam.exe Mapping Round 210

Date: 2026-04-28

Scope: the retained startup-command parser/storage lane in `qcommon/common.c`
around `0x004C9EB0`, plus the neighboring shutdown owner at `0x004C94A0`.

## Summary

This round resolved `2` additional `quakelive_steam.exe` aliases and rebuilt
the startup-command data flow in `src/` so it more closely matches the retail
binary.
Classification mix:

- `2` engine-owned functions
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main source win is that startup command lines are no longer stored as raw
`+set foo bar` text and re-tokenized later. They are now materialized once into
tokenized, heap-backed console-line storage, and the downstream startup helpers
consume that retained representation directly.

## Evidence Notes

- The decisive retained source anchors are
  [Com_ParseCommandLine](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:674>),
  [Com_SafeMode](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:761>),
  [Com_StartupVariable](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:791>),
  [Com_AddStartupCommands](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:823>),
  [Com_Shutdown](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:3526>),
  and the upgraded
  [Cbuf_AddTokenized](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/cmd.c:110>)
  helper.
- `sub_4C9EB0` is now promoted as `Com_ParseCommandLine`. The HLIL shows the
  retained startup-line builder counting command tokens, handling the special
  `+bind key +command` lane, stripping leading `+` from real console-command
  heads, and storing the resulting command lines in tokenized NUL-separated
  storage.
- `sub_4C94A0` is now promoted as `Com_Shutdown`. The observed call sites match
  the retained fatal-error and quit paths, and the body shape matches the
  shutdown owner role: it frees startup-command storage, closes retained file
  handles, shuts runtime services down, and clears the crash marker by writing
  `"0"` to `profile.pid`.
- Source reconstruction performed this round:
  [Com_ParseCommandLine](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:674>)
  now builds retained tokenized startup-line storage instead of keeping raw
  text slices, and
  [Com_SafeMode](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:761>),
  [Com_StartupVariable](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:791>),
  and
  [Com_AddStartupCommands](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:823>)
  now consume that representation directly.
- Compatibility bridge note: the retail executable receives an argv vector,
  while the checked-in tree still enters `Com_Init(...)` through a flattened
  command-line string. The reconstructed parser therefore tokenizes that flat
  input once up front, recreates the retail command-line storage layout, and
  preserves the checked-in tree's legacy bare-first-command compatibility when
  no leading `+` is present.
- Follow-on source tightening: the reconstructed
  [Cbuf_AddTokenized](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/cmd.c:110>)
  helper now consumes tokenized startup lines directly instead of
  re-tokenizing them internally, which matches the retail helper contract much
  more closely than the prior compatibility-only bridge.

## Aliases Added

- `sub_4C94A0` -> `Com_Shutdown`
- `sub_4C9EB0` -> `Com_ParseCommandLine`

## Verification

Static/source validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- `pytest tests/test_engine_command_parity.py -q --tb=no`
  passed (`12 passed`)
- `pytest tests/test_engine_cvar_retail_parity.py -q --tb=no`
  still reports the same `3` unrelated pre-existing failures in the current
  dirty tree:
  `test_engine_cvar_third_server_tranche_matches_retail_contracts`,
  `test_engine_cvar_fourteenth_core_timing_tranche_matches_retail_contracts`,
  and
  `test_engine_cvar_fifteenth_server_state_tranche_matches_retail_contracts`
- recount after this pass: `2198` raw alias entries, `2122` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `38.772%` of `5473` functions
- `git diff --check` passed aside from the repo's existing LF -> CRLF
  normalization warnings on touched text files

Parity estimate after this pass:

- strict-retail Windows replacement target: `100%` before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

The next useful follow-up in this startup/common neighborhood is the larger
supporting parser/cleanup lane around `0x004CA010` and the remaining startup
adjacent helper ownership still hanging off the rebuilt command-line store.
