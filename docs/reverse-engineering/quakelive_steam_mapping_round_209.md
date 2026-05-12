# quakelive_steam.exe Mapping Round 209

Date: 2026-04-28

Scope: the remaining token-preserving startup-command seam between the
retained `cmd.c` command buffer and `common.c` startup-command injection,
centered on `sub_4C7D50`.

## Summary

This round resolved `1` additional `quakelive_steam.exe` alias and restored
the missing token-preserving startup-command append helper in `src/`.
Classification mix:

- `1` engine-owned function
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The useful outcome is behavioral rather than just nominative: startup command
injection now re-quotes argv tail tokens before they are written into the
command buffer, so arguments containing separators survive the later command
execution pass again.

## Evidence Notes

- The decisive retained helper anchor is the newly restored
  [Cbuf_AddTokenized](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/cmd.c:110>)
  in [cmd.c](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/cmd.c>), used
  by [Com_AddStartupCommands](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:732>)
  in [common.c](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c>).
- Observed fact from HLIL: `sub_4C7D50` appends the first token verbatim,
  appends later tokens as ` "token"`, emits the exact
  `"Cbuf_AddTokenized: overflow\n"` string on failure, and always terminates
  the appended command with `\n`.
- Observed fact from the retail caller: `sub_4C8AE0` (`Com_AddStartupCommands`)
  routes startup lines through that helper instead of raw `Cbuf_AddText(...)`
  plus a manual newline.
- Source reconstruction note: the retail helper consumes pre-tokenized
  NUL-separated startup lines. The checked-in source still keeps a simpler raw
  startup-line store, so the restored
  [Cbuf_AddTokenized](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/cmd.c:110>)
  uses `Cmd_TokenizeString(...)` internally as a compatibility bridge before it
  performs the retained re-quoting append. That preserves the binary-observed
  output contract without forcing a larger startup-parser rewrite in this pass.

## Aliases Added

- `sub_4C7D50` -> `Cbuf_AddTokenized`

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
- recount after this pass: `2196` raw alias entries, `2120` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `38.736%` of `5473` functions
- `git diff --check` passed aside from the repo's existing LF -> CRLF
  normalization warnings on touched text files

Parity estimate after this pass:

- strict-retail Windows replacement target: `100%` before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

The next useful startup/command follow-up is the larger argv-driven
`Com_ParseCommandLine` ownership seam at `0x004C9EB0`, which the committed HLIL
shows building tokenized startup-line storage from the executable argv vector.
That is a larger reconstruction than this round because the current checked-in
tree still enters `Com_Init(...)` through flattened command-line strings on all
platforms.
