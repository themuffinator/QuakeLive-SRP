# quakelive_steam.exe Mapping Round 205

Date: 2026-04-28

Scope: retained console/input host-field and demo-completion helpers around the
old queue head `0x004B6630`.

## Summary

This round resolved `5` additional `quakelive_steam.exe` aliases.
Classification mix:

- `4` engine-owned functions
- `0` platform-service-owned functions
- `1` CRT/STL/support-library function
- `0` Awesomium functions
- `0` Steam SDK support functions

This was a mixed exact/descriptive pass. The useful outcome is that the
anonymous host-field seam in the console/input lane no longer blocks the queue:
`0x004B6630` is now owned, the retained `Console_CompleteArgument` demo
completion callback is explicit, and the lingering top queue is now led by the
older `FUN_004b3672` console split artifact and the unrelated `0x004241C0`
libzmq seam.

## Evidence Notes

- The exact source anchors are
  [Con_DrawHostField](</E:/Repositories/QuakeLive-reverse/src/code/client/cl_console.c:301>)
  in
  [cl_console.c](</E:/Repositories/QuakeLive-reverse/src/code/client/cl_console.c>)
  and
  [Console_CompleteArgument](</E:/Repositories/QuakeLive-reverse/src/code/client/cl_keys.c:664>)
  in
  [cl_keys.c](</E:/Repositories/QuakeLive-reverse/src/code/client/cl_keys.c>).
- `sub_4B6830` is exact as `Con_DrawHostField`. The only observed callers are
  the retained console input and chat draw sites, and the HLIL behavior matches
  the source-owned host-field path: UTF-8-aware substring extraction, host font
  measurement, cursor blink gating, and the final underscore/pipe cursor draw.
- `sub_4B6A60` is exact as `Console_CompleteArgument`. Its HLIL strips a
  leading slash, accepts only the `"demo"` command name, fetches `.dm_73`
  entries from the `demos` directory, and invokes the caller-provided callback
  for each match exactly like the retained completion helper in `cl_keys.c`.
- `sub_4B6620` is the tiny `_time64` forwarder and was safe to promote
  directly.
- `sub_4B6630` and `sub_4B6820` are intentionally descriptive helper names,
  not source-faithful public owners. Retail has split the host-field draw path
  into a large internal helper plus a 9-byte tailcall thunk before the public
  entry. The committed source does not expose those helper boundaries, so I
  labeled them `Con_DrawHostField_helper` and `Con_DrawHostField_thunk` rather
  than pretending they are separate checked-in source functions.
- I deliberately left `FUN_004b3672` deferred. The HLIL still shows it is the
  larger body split out of the already-mapped `Con_Find_f` neighborhood, and I
  did not want to invent a misleading second exact public owner for that Ghidra
  artifact in the same round.

## Aliases Added

- `sub_4B6620` -> `_time64`
- `sub_4B6630` -> `Con_DrawHostField_helper`
- `sub_4B6820` -> `Con_DrawHostField_thunk`
- `sub_4B6830` -> `Con_DrawHostField`
- `sub_4B6A60` -> `Console_CompleteArgument`

## Verification

Static mapping validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- scoped duplicate-key scan for the `quakelive_steam` alias block passed with
  `0` duplicates
- recount after this pass: `2167` raw alias entries, `2094` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `38.261%` of `5473` functions
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
| 1 | `0x004B3672` | `FUN_004b3672` | `495` |
| 2 | `0x004241C0` | `FUN_004241c0` | `482` |
| 3 | `0x00498890` | `FUN_00498890` | `480` |
| 4 | `0x00480DD0` | `FUN_00480dd0` | `479` |
| 5 | `0x004C84E0` | `FUN_004c84e0` | `479` |
| 6 | `0x0050EF80` | `FUN_0050ef80` | `476` |
| 7 | `0x00412970` | `FUN_00412970` | `472` |
| 8 | `0x004A21A0` | `FUN_004a21a0` | `470` |
| 9 | `0x0050BB00` | `FUN_0050bb00` | `469` |
| 10 | `0x004A0770` | `FUN_004a0770` | `467` |

The next pass can either finally retire the residual `FUN_004b3672`
`Con_Find_f` split, pivot into the freshly promoted `0x004241C0` libzmq seam,
or return to the nearby bot-movement leftovers around `0x004A21A0`.
