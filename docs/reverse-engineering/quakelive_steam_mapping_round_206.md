# quakelive_steam.exe Mapping Round 206

Date: 2026-04-28

Scope: retained client console helper-boundary reconstruction around the
residual `Con_Find_f` split artifact `0x004B3672`, plus the adjacent
host-field wrapper/helper seam in `cl_console.c`.

## Summary

This round resolved `1` additional `quakelive_steam.exe` alias.
Classification mix:

- `1` engine-owned function
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The useful outcome is that the remaining console queue head from round 205 is
no longer an orphaned Ghidra split row. The checked-in source now mirrors the
retail helper boundaries more closely: `Con_Find_f` keeps the command-line
guard while the search body lives in the new `Con_FindMatchesInHistory`
helper, and `Con_DrawHostField` is now an explicit thin wrapper over the
already-mapped internal `Con_DrawHostField_helper` body.

## Evidence Notes

- The exact source anchors are
  [Con_Find_f](</E:/Repositories/QuakeLive-reverse/src/code/client/cl_console.c:902>)
  and
  [Con_FindMatchesInHistory](</E:/Repositories/QuakeLive-reverse/src/code/client/cl_console.c:839>)
  in
  [cl_console.c](</E:/Repositories/QuakeLive-reverse/src/code/client/cl_console.c>).
- `FUN_004b3672` is the large retained body split out of `sub_4B3630` in the
  committed Ghidra export. The HLIL starts that split immediately after the
  public `Cmd_Argc() != 2` usage/error branch, then performs `Cmd_Argv(1)`,
  loads the retained `con.current`/`con.totallines`/`con.linewidth` globals,
  walks scrollback rows, filters out `"\find"` and `"usage: find "`, emits
  `"\n## MATCH LIST:\n"` / `"\n## %s\n"`, and ends with the exact match-count
  summary branches. The reconstructed `Con_FindMatchesInHistory` helper now
  matches that internal ownership boundary directly instead of leaving the
  split as an anonymous artifact.
- The retained host-field lane around `sub_4B6630` / `sub_4B6830` was already
  mapped in round 205, but the checked-in source still kept the whole body
  under one public function. This pass reconstructs the same helper/wrapper
  split in source by moving the UTF-8-aware draw/cursor body under
  `Con_DrawHostField_helper` and leaving `Con_DrawHostField` as the thin
  forwarder, matching the retail wrapper shape more closely without changing
  behavior.
- No runtime launch was needed. The evidence chain was the existing
  `cl_console.c` source, the committed HLIL around `0x004B3630` and
  `0x004B6630`, and the current alias corpus.

## Aliases Added

- `FUN_004b3672` -> `Con_FindMatchesInHistory`

## Verification

Static/source validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- `pytest tests/test_engine_command_parity.py tests/test_cl_console_cgame_parity.py tests/test_engine_cvar_retail_parity.py::test_engine_cvar_sixth_client_tranche_matches_retail_contracts -q --tb=no`
  passed
- recount after this pass: `2168` raw alias entries, `2095` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `38.281%` of `5473` functions
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
| 4 | `0x004C84E0` | `FUN_004c84e0` | `479` |
| 5 | `0x0050EF80` | `FUN_0050ef80` | `476` |
| 6 | `0x00412970` | `FUN_00412970` | `472` |
| 7 | `0x004A21A0` | `FUN_004a21a0` | `470` |
| 8 | `0x0050BB00` | `FUN_0050bb00` | `469` |
| 9 | `0x004A0770` | `FUN_004a0770` | `467` |
| 10 | `0x0042C830` | `FUN_0042c830` | `465` |

The next pass can stay on the host-executable console/browser side by taking
the new queue head `0x004241C0`, or pivot into the nearby bot-movement and
renderer-adjacent leftovers once the console helper split is fully recorded.
