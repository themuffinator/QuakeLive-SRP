# quakelive_steam.exe Mapping Round 198

Date: 2026-04-28

Scope: engine-owned client console recovery across the old queue head
`0x004B4100` and the adjacent search/draw/scroll helpers from `0x004B3630`
through `0x004B4A00`.

## Summary

This round resolved `15` additional `quakelive_steam.exe` aliases.
Classification mix:

- `15` engine-owned functions
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The useful outcome is that the anonymous client console lane now reads as the
real retained `cl_console.c` search, notify, resize, draw, scroll, close, and
clear family instead of a broken-up slab of opaque host glue. The main queue
head closure is `sub_4B4100 -> Con_DrawNotify`, and the surrounding pass also
lands the console search command, dump command, layout rebuild, linefeed,
prompt drawing, backscroll helpers, and close/clear owners.

## Evidence Notes

- `sub_4B3630` is exact as `Con_Find_f` because the HLIL matches the retained
  console-history search command line-for-line: it checks `Cmd_Argc() != 2`,
  prints the exact `"usage: find <substring>  ; This is a case sensitive
  search of the console history.\n"` string, copies each scrollback row into a
  temporary buffer, trims trailing spaces, filters out `"\find"` and
  `"usage: find "`, prints `"\n## MATCH LIST:\n"` and `"\n## %s\n"`, and ends
  with the singular/plural match-count summary. The committed Ghidra export
  still carries a large split row at `FUN_004b3672` inside this body, so I
  left that residual queue artifact alone instead of force-claiming a second
  public source name.
- `sub_4B3880` is exact as `Con_Dump_f`. Its HLIL keeps the exact
  `"usage: condump <filename>\n"`, `"Dumped console text to %s.\n"`, and
  `"ERROR: couldn't open.\n"` string anchors, and the control flow matches the
  retained file-open, whitespace-trim, write-line, and close sequence.
- `sub_4B3A30`, `sub_4B3A50`, and `sub_4B3C20` are exact as
  `Con_ClearNotify`, `Con_CheckResize`, and `Con_Linefeed`. The resize owner
  preserves the whole retained console-width recomputation and ring-buffer
  reformat path, while the linefeed helper advances `con.current`, updates
  notify timestamps, and clears the next row with the white-space `0x720`
  fill pattern seen in the checked-in source.
- `sub_4B3FF0`, `sub_4B4100`, `sub_4B47A0`, and `sub_4B4800` are exact as
  `Con_DrawInput`, `Con_DrawNotify`, `Con_DrawConsole`, and `Con_RunConsole`.
  The strongest `Con_DrawNotify` anchors are the retained chat prompt strings
  `"reply:"`, `"say:"`, and `"say team:"`; `Con_DrawConsole` still follows the
  exact disconnected/fullscreen-console vs notify-only branch structure; and
  `Con_RunConsole` retains the `con_height` / `con_speed` eased scroll logic.
- `sub_4B48B0`, `sub_4B48E0`, `sub_4B4900`, `sub_4B4920`, `sub_4B4930`, and
  `sub_4B4A00` are exact as `Con_PageUp`, `Con_PageDown`, `Con_Top`,
  `Con_Bottom`, `Con_Close`, and `Con_Clear_f`. These are all tiny,
  one-purpose owners in both HLIL and retained source: the scroll helpers
  adjust `con.display`, `Con_Close` clears the console field, notify times,
  keycatcher bit, and display fractions, and `Con_Clear_f` is the
  `CON_TEXTSIZE` white-space fill followed by `Con_Bottom()`. `Con_Clear_f`
  does not currently have a separate committed `functions.csv` row, so it
  contributes to the raw alias corpus but not the strict address-backed delta.
- I deliberately left the `toggleconsole` split seam deferred. Retail breaks
  that command across a `com_allowConsole` gate wrapper and an internal toggle
  body (`sub_4B49D0` / `sub_4B4980`), but the checked-in source keeps it as a
  single public `Con_ToggleConsole_f`, so forcing separate internal names here
  would overstate certainty.

## Aliases Added

- `sub_4B3630` -> `Con_Find_f`
- `sub_4B3880` -> `Con_Dump_f`
- `sub_4B3A30` -> `Con_ClearNotify`
- `sub_4B3A50` -> `Con_CheckResize`
- `sub_4B3C20` -> `Con_Linefeed`
- `sub_4B3FF0` -> `Con_DrawInput`
- `sub_4B4100` -> `Con_DrawNotify`
- `sub_4B47A0` -> `Con_DrawConsole`
- `sub_4B4800` -> `Con_RunConsole`
- `sub_4B48B0` -> `Con_PageUp`
- `sub_4B48E0` -> `Con_PageDown`
- `sub_4B4900` -> `Con_Top`
- `sub_4B4920` -> `Con_Bottom`
- `sub_4B4930` -> `Con_Close`
- `sub_4B4A00` -> `Con_Clear_f`

## Verification

Static mapping validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- scoped duplicate-key scan for the `quakelive_steam` alias block passed with
  `0` duplicates
- recount after this pass: `2125` raw alias entries, `2052` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `37.493%` of `5473` functions
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
| 1 | `0x004E6730` | `FUN_004e6730` | `504` |
| 2 | `0x004B3672` | `FUN_004b3672` | `495` |
| 3 | `0x0046A420` | `FUN_0046a420` | `490` |
| 4 | `0x004DC730` | `FUN_004dc730` | `490` |
| 5 | `0x004C12F0` | `FUN_004c12f0` | `488` |
| 6 | `0x004368A0` | `FUN_004368a0` | `484` |
| 7 | `0x00429DD0` | `FUN_00429dd0` | `483` |
| 8 | `0x004A4280` | `FUN_004a4280` | `483` |
| 9 | `0x004B6630` | `FUN_004b6630` | `483` |
| 10 | `0x004241C0` | `FUN_004241c0` | `482` |

The next pass can stay in the client/engine lane by untangling the residual
`FUN_004b3672` split and the still-heavy `sub_4E6730` seam, or pivot back to
the nearby large gameplay/host leftovers now that the public console family is
substantially mapped.
