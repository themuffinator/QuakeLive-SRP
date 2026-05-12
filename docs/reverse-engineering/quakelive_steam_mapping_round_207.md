# quakelive_steam.exe Mapping Round 207

Date: 2026-04-28

Scope: retained `qcommon/cmd.c` command-buffer and script-command owners around
the queue cluster `0x004C8430` through `0x004C8900`.

## Summary

This round resolved `8` additional `quakelive_steam.exe` aliases.
Classification mix:

- `8` engine-owned functions
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The useful outcome is that the anonymous command-buffer queue in the host
executable now reads as the real retained `cmd.c` command path instead of a
generic parser slab. The key closure is `sub_4C84E0 -> Cbuf_Execute`, and the
same pass also closes the neighboring `Cmd_Wait_f`, `Cmd_Exec_f`,
`Cmd_Vstr_f`, `Cmd_Echo_f`, `Cmd_Init`, and `Cbuf_ExecuteText` owners.

## Evidence Notes

- The decisive source anchors are
  [Cmd_List_f](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/cmd.c:842>),
  [Cmd_Wait_f](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/cmd.c:52>),
  [Cbuf_Execute](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/cmd.c:168>),
  [Cmd_Exec_f](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/cmd.c:239>),
  [Cmd_Vstr_f](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/cmd.c:271>),
  [Cmd_Echo_f](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/cmd.c:291>),
  [Cmd_Init](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/cmd.c:869>),
  and
  [Cbuf_ExecuteText](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/cmd.c:141>)
  in [cmd.c](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/cmd.c>).
- `sub_4C8430` is exact as `Cmd_List_f`. The HLIL walks the retained
  command-function list, optionally filters by a passed substring, prints each
  matching command, and ends with the exact `"%i commands\n"` summary.
- `sub_4C84B0` is exact as `Cmd_Wait_f`. The body is the retained two-branch
  command: if `Cmd_Argc() == 2` it copies `atoi( Cmd_Argv(1) )` into
  `cmd_wait`, otherwise it stores `1`.
- `sub_4C84E0` is exact as `Cbuf_Execute`. Its HLIL matches the retained
  command-buffer execution loop line-for-line: it honors `cmd_wait`, scans the
  front buffer for `;`, `\n`, or `\r` while tracking quotes, clamps to
  `MAX_CMD_LINE - 1`, copies the next command into a stack line buffer,
  compacts `cmd_text` with `memmove`, and then dispatches the parsed line.
- `sub_4C86D0`, `sub_4C87B0`, and `sub_4C87F0` are exact as `Cmd_Exec_f`,
  `Cmd_Vstr_f`, and `Cmd_Echo_f`. The retained string anchors
  `"exec <filename> : execute a script file\n"`, `"couldn't exec %s\n"`,
  `"execing %s\n"`, and
  `"vstr <variablename> : execute a variable command\n"` line up directly with
  the checked-in bodies.
- `sub_4C8890` is exact as `Cmd_Init`: it resets the alias-list head and
  registers `cmdlist`, `listcmds`, `exec`, `vstr`, `echo`, and `wait` in the
  same order as the retained source.
- `sub_4C8900` is exact as `Cbuf_ExecuteText`. The HLIL dispatches `EXEC_NOW`,
  `EXEC_INSERT`, and `EXEC_APPEND` to the retained helper targets, falls back
  to `Cbuf_Execute()` when the immediate text is null or empty, and preserves
  the exact fatal `"Cbuf_ExecuteText: bad exec_when"` path.

## Aliases Added

- `sub_4C8430` -> `Cmd_List_f`
- `sub_4C84B0` -> `Cmd_Wait_f`
- `sub_4C84E0` -> `Cbuf_Execute`
- `sub_4C86D0` -> `Cmd_Exec_f`
- `sub_4C87B0` -> `Cmd_Vstr_f`
- `sub_4C87F0` -> `Cmd_Echo_f`
- `sub_4C8890` -> `Cmd_Init`
- `sub_4C8900` -> `Cbuf_ExecuteText`

## Verification

Static/source validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- `pytest tests/test_engine_command_parity.py -q --tb=no`
  passed
- recount after this pass: `2176` raw alias entries, `2100` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `38.370%` of `5473` functions
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

The next pass can keep pushing through engine-owned executable glue by taking
the `0x004241C0` queue head, or pivot into the nearby unresolved bot-movement
lane around `0x004A21A0` now that the `cmd.c` command-buffer seam is closed.
