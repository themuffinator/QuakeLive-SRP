# qagame Direct Command Table Tail Reconstruction - 2026-05-25

## Scope

This pass closes the remaining named rows in the recovered retail
`data_10080750` direct `game` command table:

- `addscore`
- `addteamscore`
- `setmatchtime`
- `rcon`

`rcon` is a special case: retail exposes the row and help description, but the
handler slot is null. The reconstructed dispatcher keeps it visible in help and
lets it fall through rather than inventing qagame-side rcon execution.

## Evidence

Owning retail binary: `qagamex86.dll`.

- `references/hlil/quakelive/qagamex86.dll/.../qagamex86.dll.bndb_hlil_part02.txt`
  shows table rows at `0x100808F4`, `0x10080908`, `0x1008091C`, and
  `0x10080930`.
- `sub_10061670` resolves a PlayerID, parses argv 2 as a whole score delta,
  calls the score helper, broadcasts `Player score adjusted.`, and reports
  whether the player's score was increased or decreased.
- `sub_10061730` parses a team token through the shared direct-command team
  parser, parses argv 2 as a score delta, calls `AddTeamScore`, broadcasts
  `Team score adjusted.`, and emits the same increase/decrease print.
- `sub_10062CE0` parses a whole-second match time, rewrites
  `CS_LEVEL_START_TIME`, and broadcasts
  `Match time has been set to %s.` with the retail `%i:%i%i` minute/second
  formatter from `sub_10070B40`.
- The `rcon` row at `0x10080930` has privilege `2`, name `rcon`, a null handler
  slot, and the description ` <command> ^3run command on server`.

## Reconstruction

- Added direct table entries for `addscore`, `addteamscore`, `setmatchtime`,
  and help-visible `rcon`.
- Updated `G_DispatchDirectCommand` so a matched null-handler row falls through
  instead of being called.
- Added `Cmd_AddScore_f`, `Cmd_AddTeamScore_f`, and `Cmd_SetMatchTime_f` using
  the existing PlayerID/team parsers and score/timer source helpers.
- Added a local match-time formatter that mirrors the retail `%i:%i%i` output.
- Added helper-seam tests for the table offsets, exact strings, null-handler
  dispatch behavior, and source-side score/time wiring.

## Parity Estimate

Scoped direct command table tail:

- Before: **18%**. The symbol map identified the functions, but source had no
  direct table rows or handlers for the score/time commands, and `rcon` was not
  represented as a help-visible null-handler row.
- After: **91%**. The remaining named table rows, privilege floors, score
  adjustment broadcasts, match-time configstring update, and null-handler
  behavior are reconstructed from committed HLIL evidence. Remaining risk is
  limited to exact integer conversion edge cases around the optimized retail
  `atof`/rounding path.

Repo-wide estimate remains **98%**.
