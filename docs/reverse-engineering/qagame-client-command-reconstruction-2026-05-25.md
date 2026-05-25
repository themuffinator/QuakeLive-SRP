# qagame Client Command Reconstruction - 2026-05-25

## Scope

This round reconstructs the retail `qagamex86.dll` direct-command tranche for
ten `game` client commands and their shared wiring:

- `players`
- `timeout`
- `timein`
- `allready`
- `pause`
- `unpause`
- `lock`
- `unlock`
- `putteam`
- `opsay`

The related `?` help entry is included because retail dispatch reaches it
through the same `data_10080750` table and `G_PrintDirectCommandHelp` walker.

## Evidence

Owning retail binary: `qagamex86.dll`.

Committed Ghidra corpus checked first:

- `references/reverse-engineering/ghidra/qagamex86/metadata.txt`
  identifies `qagamex86.dll`, 1027 functions, 65 imports, and 2 exports.
- `references/reverse-engineering/ghidra/qagamex86/exports.txt`
  exposes `dllEntry` and `entry`.
- `references/reverse-engineering/ghidra/qagamex86/imports.txt`
  confirms the C runtime helpers used by the recovered command parsers,
  including `atoi`, `isdigit`, `tolower`, and `toupper`.
- `references/reverse-engineering/ghidra/qagamex86/functions.csv`
  anchors `FUN_10060ee0`, `FUN_100611d0`, `FUN_100618b0`, and
  `FUN_10062e20`; the remaining table-adjacent starts are visible in HLIL and
  the symbol map even where the CSV does not split them.

Canonical HLIL evidence:

- `data_10080750` is the direct command table. The selected entries point to
  `Cmd_Players_f`, `Cmd_Timeout_f`, `Cmd_Timein_f`, `Cmd_AllReady_f`,
  `Cmd_Pause_f`, `Cmd_Lock_f`, `Cmd_Unlock_f`, `Cmd_PutTeam_f`, and
  `Cmd_OpSay_f`.
- The table rows include the recovered privilege floors: `players`, `timeout`,
  and `timein` are public; `allready`, `pause`, `unpause`, `lock`, `unlock`,
  `putteam`, and `opsay` require moderator privilege.
- `Cmd_Players_f` at `0x10060EE0` emits `print "%2d %llu %c %s\n"` rows and
  uses the recovered `" MA*"` privilege marker map.
- `G_ValidateDirectCommandState` at `0x10061090` owns the exact direct-command
  state rejection strings for intermission, warmup, round countdown, and live
  match use.
- `G_AdminResolvePlayerIdArg` at `0x100611D0` owns the numeric PlayerID parser
  and the exact missing/invalid PlayerID diagnostics.
- `G_AdminParseTeamArg` at `0x10061350` owns the single-letter team parser and
  exact `Missing TeamName`, `Invalid TeamName`, and invalid-command-team
  diagnostics.
- `G_TeamJoinAllowed` at `0x100618B0` checks the retail per-team lock latch and
  emits `The %s team is locked!`.
- `Cmd_Lock_f` and `Cmd_Unlock_f` at `0x10061940` / `0x10061A40` update the
  same latch and broadcast `The %s team is now %slocked`.
- `Cmd_PutTeam_f` at `0x10061B40` reuses PlayerID and team parsing, enforces
  duel restrictions, reports already-on-team cases, notifies the target, and
  forwards to `SetTeam`.
- `G_StartTimeout`, `Cmd_Pause_f`, `Cmd_Timeout_f`, and `Cmd_Timein_f` preserve
  the retail `pcp` timeout/timein broadcast strings and timeout configstring
  refresh boundary.

## Reconstruction

Source updates:

- Replaced the single-command `opsay` direct dispatcher with
  `s_directCommands[]`, covering the ten selected retail commands plus `?`.
- Added direct-command privilege resolution, help filtering, and console-safe
  feedback helpers.
- Rebuilt `/players` output around SteamID64, the `" MA*"` privilege marker,
  and the retail row format instead of the older score/ping table.
- Added `level.teamLocks[TEAM_NUM_TEAMS]` and routed `lock`, `unlock`, and
  `G_TeamJoinAllowed` through it while preserving the legacy
  `g_teamSpawnAsSpec` compatibility gate.
- Added HLIL-named PlayerID and team parsers for the direct admin command
  tranche.
- Reworked `allready`, `putteam`, `lock`, and `unlock` so privilege checks come
  from the direct table rather than repeated SteamID lookups.
- Retained timeout ownership and configstring wiring while switching the
  player-facing timeout/timein announcements to the recovered `pcp` commands.

Tests:

- `tests/test_game_helper_seam_parity.py::test_game_direct_command_table_reconstructs_retail_client_command_tranche`
  now pins the table entries, selected HLIL addresses, exact retail strings,
  shared helper boundaries, and source latch/wiring.
- Existing team-join and timeout seam tests were kept aligned with the new
  per-team lock latch and direct-command helper boundaries.

## Parity Estimate

Scoped direct-command tranche:

- Before: **42%**. The source had several command bodies, but only `opsay` was
  wired through a direct table, `/players` still used the older score/ping
  layout, team locking used only the compatibility cvar, and admin commands
  repeated SteamID privilege lookups instead of sharing the retail table and
  parser helpers.
- After: **89%**. The selected table rows, privilege floors, state gate,
  PlayerID/team parsers, per-team lock latch, player listing format, target
  movement notifications, and timeout broadcast strings are reconstructed from
  committed HLIL evidence. Remaining risk is limited to exact internal retail
  enum/flag layout and a few timeout edge branches where HLIL is byte-heavy
  around `0x100621C0` and `0x10062330`.

Repo-wide estimate remains **98%** because this closes a focused `qagame`
command tranche rather than the remaining compatibility-only and packaging
surfaces.
