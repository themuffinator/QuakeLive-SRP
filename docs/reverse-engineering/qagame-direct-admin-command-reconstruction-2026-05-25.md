# qagame Direct Admin Command Reconstruction - 2026-05-25

## Scope

This round reconstructs the next ten retail `qagamex86.dll` direct `game`
client commands and the shared access-list/drop wiring they use:

- `mute`
- `unmute`
- `tempban`
- `ban`
- `listaccess`
- `unban`
- `addadmin`
- `addmod`
- `demote`
- `abort`

It also corrects the adjacent `opsay` privilege floor to moderator because the
HLIL table row at `data_10080750 + 0x140` stores `1`, while the next row stores
`2` for `addadmin`.

## Evidence

Owning retail binary: `qagamex86.dll`.

Committed evidence checked:

- `references/reverse-engineering/ghidra/qagamex86/metadata.txt`,
  `imports.txt`, `exports.txt`, and `functions.csv` establish the qagame retail
  binary and the VM/syscall imports used by command parsing and client drops.
- `references/symbol-maps/qagame.json` names the relevant retail functions:
  `Cmd_Abort_f`, `Cmd_AddAdmin_f`, `Cmd_AddMod_f`, `Cmd_Demote_f`,
  `Cmd_Mute_f`, `Cmd_Unmute_f`, `G_KickOrBanClient`, `Cmd_Unban_f`,
  `Cmd_ListAccess_f`, and `G_PrintAccessListPage`.
- `references/hlil/quakelive/qagamex86.dll/.../qagamex86.dll.bndb_hlil_part02.txt`
  exposes the `data_10080750` command-table rows from `mute` through `abort`,
  the `sub_10062470` through `sub_10062C60` command bodies, and the exact
  promotion, demotion, kick, unban, and abort strings.
- `references/hlil/quakelive/qagamex86.dll/.../qagamex86.dll.bndb_hlil_part01.txt`
  anchors `G_PrintAccessListPage` at `0x100327D0` with
  `Access List: Page %i of %i`, `TEMP`, `PERM`, and `%llu %s %s`.

## Reconstruction

Source updates:

- Extended `s_directCommands[]` with the ten selected rows using the recovered
  privilege floors: moderator for `mute`, `unmute`, `tempban`, `ban`,
  `listaccess`, `unban`, and `abort`; admin for `addadmin`, `addmod`, and
  `demote`.
- Reworked `mute` and `unmute` to use the shared PlayerID resolver instead of
  legacy SteamID privilege rechecks. `mute` preserves the same-or-higher target
  guard visible in HLIL; `unmute` mirrors retail by simply clearing the muted
  session flag after target resolution.
- Added public access-list mutators in `g_main.c` for setting/removing cached
  SteamID entries, including temporary ban state, plus a retail-style
  `G_PrintAccessListPage` page printer.
- Rebuilt `tempban` and `ban` through the shared kick/ban helper. The direct
  rows use numeric PlayerID lookup, write `-1` access entries with temporary or
  permanent mode, reject privileged targets with `Can not kick admins.`, and
  drop targets with `was kicked`.
- Added `addadmin`, `addmod`, and `demote` handlers that update the live
  `sess.privilege`, mirror access-list state, broadcast the recovered status
  lines, and send the target `priv %i`.
- Added `unban` and `listaccess` command handlers for the recovered SteamID
  removal and one-based page argument behavior.
- Added `abort` handling for active matches: it rejects active timeouts,
  broadcasts the recovered `pcp` abort message, resets the game state to
  `PRE_GAME`, refreshes match-state publication, and queues `map_restart 3`.

Tests:

- `tests/test_game_helper_seam_parity.py::test_game_direct_admin_access_command_tranche_matches_retail_table`
  pins the selected table offsets, symbol-map names, exact HLIL strings,
  access-list page format, and source wiring.
- The existing direct-command and timeout helper tests now account for the
  corrected `opsay` privilege floor and access-tree kick/ban path.

## Parity Estimate

Scoped direct admin command tranche:

- Before: **34%**. The source had partial `mute`, `unmute`, and `ban` bodies,
  but they were outside the recovered command table, repeated legacy SteamID
  checks, used IP-ban console commands, and lacked the access-list mutation,
  promotion/demotion, list/unban, and abort command surface.
- After: **87%**. The selected table rows, privilege floors, shared target
  resolver, access-list printer/mutators, direct ban modes, promotion/demotion
  broadcasts, `priv %i` refreshes, and abort control path now line up with the
  committed HLIL evidence. Remaining risk is mostly around the exact retail
  container shape for the access tree and minor compatibility behavior kept for
  the legacy `admin kick` / `admin ban` wrapper.

Repo-wide estimate remains **98%** because this closes a focused `qagame`
command block rather than broad engine or UI surfaces.
