# Freeze Tag Winning-Team Thaw Respawn Mapping - 2026-06-06

## Scope

This pass maps and reconstructs the Freeze round-controller path that thaws
frozen members of the winning team when `g_freezeThawWinningTeam` is enabled.
It is separate from assisted thaw: retail performs a direct thaw visual and
`ClientSpawn` handoff from the round-state controller instead of routing through
the assisted-thaw `GibEntity` branch.

## Evidence

- qagame owner binary: `qagamex86.dll`.
- Ghidra function row:
  `references/reverse-engineering/ghidra/qagamex86/functions.csv`,
  `FUN_1004c1b0,1004c1b0,2470`.
- Companion decompile:
  `references/reverse-engineering/ghidra/qagamex86/decompile_top_functions.c`.
- Source targets:
  `src/code/game/g_active.c`, `src/code/game/g_freeze.c`, and
  `src/code/game/g_client.c`.

## Observed Retail Facts

In `FUN_1004C1B0` / `Freeze_RoundStateTransition`, the active-round cleanup
loop scans connected player entities. For frozen clients on the winning-team
thaw path, retail checks `pm_type == 4`, matching `PM_FREEZE`.

The thaw handoff is explicit:

- emit event ordinal `0x57`, matching `EV_THAW_PLAYER`.
- write `0` to the client movement type, matching `PM_NORMAL`.
- tailcall `FUN_1003BC30`, matching `ClientSpawn`.

The adjacent non-frozen spectator/dead branches also clear movement type and
call `ClientSpawn`, but they do not emit `EV_THAW_PLAYER`. That keeps the thaw
visual specific to the `PM_FREEZE` case.

## Source Reconstruction

- Added `G_FreezeRespawnThawedWinner` in `g_active.c`.
- The helper emits `EV_THAW_PLAYER` at the frozen client's playerstate origin,
  records the thawed client in `otherEntityNum`, restores `PM_NORMAL`, and calls
  `ClientSpawn`.
- `G_FreezeThawWinningPlayers` now routes frozen winners through that helper
  instead of `G_FreezeThawClient`.
- Assisted thaw and admin/manual thaw remain routed through `G_FreezeThawClient`
  and the recovered `GibEntity` marker branch.

## Confidence And Open Questions

Confidence is high for the winning-team thaw sequence because the Ghidra
round-controller body exposes the `EV_THAW_PLAYER -> PM_NORMAL -> ClientSpawn`
operations directly, and the source enum values align with the observed
`pm_type == 4` / `pm_type = 0` constants.

Open follow-up: the decompile does not expose the hidden `G_TempEntity` origin
argument for `FUN_1006c490(0x57)`. The source uses `ps.origin`, matching the
existing thaw visual producers and the cgame event consumer expectations.
