# Freeze Tag Thaw Respawn Tail Mapping - 2026-06-06

## Scope

This pass reconstructs the Freeze-specific thaw visual and respawn tail around
`GibEntity`, `EV_THAW_PLAYER`, `PM_NORMAL`, and `ClientSpawn`. It follows the
assisted-thaw obituary/team-sound pass and moves the normal thaw visual owner
out of the direct Freeze mutator path.

## Evidence

- qagame owner binary: `qagamex86.dll`.
- Companion Ghidra corpus:
  `references/reverse-engineering/ghidra/qagamex86/functions.csv` and
  `references/reverse-engineering/ghidra/qagamex86/decompile_top_functions.c`.
- Symbol support:
  `references/symbol-maps/qagame.json`.
- Existing source targets:
  `src/code/game/g_freeze.c`, `src/code/game/g_combat.c`,
  `src/code/game/g_client.c`, and `src/code/game/g_local.h`.

## Observed Retail Facts

`FUN_1004CD40` / `G_FreezeClientEndFrame` completes the assisted thaw reward
and event layer, then calls `FUN_10046d80(param_1)`. The mapped symbol row for
`FUN_10046d80` is `GibEntity`, with a 379-byte retail body.

`FUN_1004C1B0` / `Freeze_RoundStateTransition` exposes the same thaw visual and
respawn tail independently during round-state cleanup. When it sees a frozen
player (`pm_type == 4`, matching `PM_FREEZE`) eligible for winning-team thaw, it
emits event ordinal `0x57` (`EV_THAW_PLAYER`), writes `0` to the client movement
type (`PM_NORMAL`), and tailcalls `FUN_1003bc30` (`ClientSpawn`).

The existing frozen-marker reconstruction maps retail `client + 0x17c` to
`ps.powerups[PW_NUM_POWERUPS]` and the entitystate high bit. That marker is the
stable source-level predicate for the Freeze-only `GibEntity` thaw branch.

## Source Reconstruction

- Added a `GibEntity` prototype to `g_local.h` so Freeze thaw completion can
  route through the shared retail gib/thaw tail.
- Extended `GibEntity` with a Freeze-specific marker branch after the normal
  `EV_GIB_PLAYER` emission. When `ps.powerups[PW_NUM_POWERUPS]` is still set,
  the branch emits `EV_THAW_PLAYER`, records the thawed client in
  `otherEntityNum`, restores `PM_NORMAL`, calls `ClientSpawn`, and returns
  before the ordinary corpse invisibility/content clear.
- Split helper-credit side effects into `G_FreezeAwardThawAssist` so assisted
  thaw obituary, team sound, medal, assist count, and score are applied before
  the thawed client is respawned.
- Changed `G_FreezeSetClientFrozenState` to preserve the frozen marker long
  enough for `GibEntity` to detect the retail thaw-respawn path. The old direct
  `EV_THAW_PLAYER` path remains only as a fallback for stale or malformed state
  where the marker has already been lost.
- Follow-up mapping in
  `docs/reverse-engineering/freeze-tag-winning-thaw-respawn-mapping-2026-06-06.md`
  split winning-team thaw back out of `G_FreezeThawClient`, matching the direct
  round-controller `EV_THAW_PLAYER -> PM_NORMAL -> ClientSpawn` sequence.

## Confidence And Open Questions

Confidence is high for the `EV_THAW_PLAYER -> PM_NORMAL -> ClientSpawn` tail:
the Ghidra round-controller body shows that sequence directly, and the
assisted-thaw end-frame body independently falls into `FUN_10046d80` after the
helper reward/event surface.

Confidence is medium-high for placing the marker check inside `GibEntity`
itself. The symbol map identifies `FUN_10046d80` as the shared retail gib
helper, the recovered end-frame body calls it at thaw completion, and the
existing frozen marker maps cleanly to the source powerup sentinel. The exact
instruction-level body for `FUN_10046d80` is not emitted in
`decompile_top_functions.c`, so this placement should stay guarded by the
focused parity tests until a fresh HLIL/Ghidra export includes that function.

Remaining follow-up: audit whether thaw respawn should preserve or reapply any
Freeze-specific spawn protection beyond the normal `ClientSpawn` path. The
current reconstruction follows the observed retail respawn tail rather than the
older in-place thaw health/armor restore.
