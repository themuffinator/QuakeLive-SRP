# quakelive_steam.exe Mapping Round 208

Date: 2026-04-28

Scope: retained `qcommon/cmd.c` command-buffer, argv/tokenization, and
dispatch helpers across `0x004C7CB0` through `0x004C8320`, plus the adjacent
`qcommon/common.c` redirect/startup/string helpers across `0x004C8970`
through `0x004C8B40`.

## Summary

This round resolved `19` additional `quakelive_steam.exe` aliases and closed
one small retained source seam in `src/`.
Classification mix:

- `19` engine-owned functions
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The highest-value closure is that the pre-dispatch `cmd.c` slab now reads as
the retained command-buffer/tokenization pipeline instead of disconnected
anonymous helpers. The neighboring `common.c` startup/redirect slice also now
has explicit owners, and `Com_SafeMode` regains the retained crash-triggered
safe-mode gate before the legacy command-line scan.

## Evidence Notes

- The decisive retained source anchors are
  [Cbuf_Init](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/cmd.c:74>),
  [Cbuf_AddText](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/cmd.c:88>),
  [Cbuf_InsertText](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/cmd.c:111>),
  [Cmd_Argc](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/cmd.c:339>),
  [Cmd_Argv](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/cmd.c:348>),
  [Cmd_Args](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/cmd.c:375>),
  [Cmd_TokenizeString](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/cmd.c:452>),
  [Cmd_CommandCompletion](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/cmd.c:615>),
  [Cmd_ExecuteString](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/cmd.c:777>),
  [Com_BeginRedirect](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:299>),
  [Com_EndRedirect](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:310>),
  [Com_SafeMode](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:668>),
  [Com_StartupVariable](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:699>),
  [Com_AddStartupCommands](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:732>),
  and
  [Com_StringContains](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:804>).
- `sub_4C7CB0`, `sub_4C7CF0`, and `sub_4C7E50` are exact as `Cbuf_Init`,
  `Cbuf_AddText`, and `Cbuf_InsertText`. The HLIL preserves the retained
  command-buffer globals, the exact overflow strings, the reverse move for
  inserted text, and the trailing newline append.
- `sub_4C7ED0` through `sub_4C8090` are the retained argv/tokenization strip:
  `Cmd_Argc`, `Cmd_Argv`, `Cmd_ArgvBuffer`, `Cmd_Args`, `Cmd_ArgsFrom`,
  `Cmd_ArgsBuffer`, `Cmd_Cmd`, and `Cmd_TokenizeString`. The Binary Ninja HLIL
  matches the retained string-buffer globals, quoted-token path, and comment
  skipping behavior line-for-line.
- `sub_4C82F0` and `sub_4C8320` are exact as `Cmd_CommandCompletion` and
  `Cmd_ExecuteString`. The retained callback walk, command-list move-to-front
  behavior, cvar/game/ui dispatch fallthrough, alias execution, and final
  server-forward path all line up directly with the checked-in source.
- `sub_4C8970`, `sub_4C89A0`, and `sub_4C8B40` are exact as
  `Com_BeginRedirect`, `Com_EndRedirect`, and `Com_StringContains`. Their HLIL
  bodies preserve the redirect globals and the case-sensitive / folded
  substring scan exactly.
- `sub_4C89E0`, `sub_4C8A70`, and `sub_4C8AE0` are the retained
  `Com_SafeMode`, `Com_StartupVariable`, and `Com_AddStartupCommands` owners.
  Observed fact: the retained `Com_SafeMode` first returns `qtrue` when the
  crash marker is live and `com_ignorecrash` is clear, then falls through to
  the familiar `safe` / `cvar_restart` command-line scan. Observed fact: the
  retained `Com_AddStartupCommands` still owns the same startup-line loop and
  non-`set` `added` flag, but feeds the command buffer through an extra
  token-preserving append helper that remains unnamed in this pass.
- Source reconstruction performed this round: `Com_SafeMode` in
  [common.c](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:668>)
  now restores the retained crash-triggered safe-mode short circuit
  (`com_crashed && !com_ignorecrash`) before the command-line scan.

## Aliases Added

- `sub_4C7CB0` -> `Cbuf_Init`
- `sub_4C7CF0` -> `Cbuf_AddText`
- `sub_4C7E50` -> `Cbuf_InsertText`
- `sub_4C7ED0` -> `Cmd_Argc`
- `sub_4C7EE0` -> `Cmd_Argv`
- `sub_4C7F00` -> `Cmd_ArgvBuffer`
- `sub_4C7F40` -> `Cmd_Args`
- `sub_4C7FD0` -> `Cmd_ArgsFrom`
- `sub_4C8060` -> `Cmd_ArgsBuffer`
- `sub_4C8080` -> `Cmd_Cmd`
- `sub_4C8090` -> `Cmd_TokenizeString`
- `sub_4C82F0` -> `Cmd_CommandCompletion`
- `sub_4C8320` -> `Cmd_ExecuteString`
- `sub_4C8970` -> `Com_BeginRedirect`
- `sub_4C89A0` -> `Com_EndRedirect`
- `sub_4C89E0` -> `Com_SafeMode`
- `sub_4C8A70` -> `Com_StartupVariable`
- `sub_4C8AE0` -> `Com_AddStartupCommands`
- `sub_4C8B40` -> `Com_StringContains`

## Verification

Static/source validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- `pytest tests/test_engine_command_parity.py -q --tb=no`
  passed (`12 passed`)
- recount after this pass: `2195` raw alias entries, `2119` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `38.717%` of `5473` functions
- `git diff --check` passed aside from the repo's existing LF -> CRLF
  normalization warnings on touched text files

Parity estimate after this pass:

- strict-retail Windows replacement target: `100%` before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

After this round, the refreshed largest-unaliased queue begins with:

| # | Address | Ghidra name | Size |
| ---: | --- | --- | ---: |
| 1 | `0x004241C0` | `FUN_004241c0` | `482` |
| 2 | `0x00498890` | `FUN_00498890` | `480` |
| 3 | `0x00480DD0` | `FUN_00480dd0` | `479` |
| 4 | `0x0050EF80` | `FUN_0050ef80` | `476` |
| 5 | `0x00412970` | `FUN_00412970` | `472` |
| 6 | `0x004A21A0` | `FUN_004a21a0` | `470` |
| 7 | `0x0050BB00` | `FUN_0050bb00` | `469` |
| 8 | `0x004A0770` | `FUN_004a0770` | `467` |
| 9 | `0x0042C830` | `FUN_0042c830` | `465` |
| 10 | `0x0049FED0` | `FUN_0049fed0` | `465` |

The next pass can either finish the retained startup-command helper seam around
`Com_AddStartupCommands` by promoting its token-preserving append helper, or
pivot back to the larger engine-owned queue head at `0x004241C0`.
