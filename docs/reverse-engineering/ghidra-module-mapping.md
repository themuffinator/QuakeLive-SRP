# Quake Live Ghidra Module Mapping

This crosswalk keeps the OpenAlice-style Ghidra corpus aligned with the existing
HLIL references, symbol maps, and writable source tree.

## Binary To Source Crosswalk

| Retail binary | Ghidra corpus path | Companion HLIL path | Primary source tree | Typical recovery focus |
| --- | --- | --- | --- | --- |
| `assets/quakelive/quakelive_steam.exe` | `references/reverse-engineering/ghidra/quakelive_steam/` | `references/hlil/quakelive/quakelive_steam.exe/` | `src/code/client/`, `src/code/qcommon/`, `src/code/renderer/`, platform glue in `src-re/` | Steam/bootstrap flow, Awesomium host behavior, launcher-to-engine bridge |
| `assets/quakelive/baseq3/cgamex86.dll` | `references/reverse-engineering/ghidra/cgamex86/` | `references/hlil/quakelive/cgamex86.dll/` | `src/code/cgame/` | HUD logic, prediction, scoreboard, client-only rules |
| `assets/quakelive/baseq3/qagamex86.dll` | `references/reverse-engineering/ghidra/qagamex86/` | `references/hlil/quakelive/qagamex86.dll/` | `src/code/game/` | gameplay rules, configstrings, item logic, server-side state |
| `assets/quakelive/baseq3/uix86.dll` | `references/reverse-engineering/ghidra/uix86/` | `references/hlil/quakelive/uix86.all/` | `src/code/ui/`, `src/ui/` | menu dispatch, feeder logic, localization, launcher/UI bridge fallbacks |

## Recommended Triage Order

1. Pick the retail binary that owns the behavior in question.
2. Read `metadata.txt`, `imports.txt`, `exports.txt`, and `functions.csv` in that
   corpus directory.
3. Use `analysis_symbols.txt` to find renamed or analyst-promoted symbols.
4. Use `decompile_top_functions.c` only after the smaller files narrow the target.
5. Cross-check the same area in the matching HLIL dump when behavior, call shape,
   or control flow is still ambiguous.
6. Map the confirmed behavior back to the source tree listed above and record the
   result in the relevant documentation or parity ledger.

## Evidence Rules

- Prefer interface edges first: imports, exports, configstrings, syscalls, and
  string tables usually expose subsystem boundaries faster than a raw decompile.
- Keep module ownership stable. Do not chase a `qagame` rule through `cgame` or
  `ui` unless the call chain or shared data proves the bridge exists.
- When the Ghidra corpus and HLIL disagree, treat the HLIL and the retail binary
  as authoritative and record the disagreement explicitly.
