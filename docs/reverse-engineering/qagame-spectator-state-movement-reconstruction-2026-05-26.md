# Qagame Spectator State and Movement Reconstruction - 2026-05-26

## Scope

This pass rechecked the retail qagame spectator state machine and the shared
movement leaf used by spectator flight. It covers `SpectatorThink`, adjacent
follow-state helpers, the server-side `PM_FlyMove` body, and the Flight pickup
boundary because Flight shares the same fly-move leaf as spectators.

No game launch was needed. The mismatches were settled by the committed HLIL,
symbol maps, and static parity tests.

## Evidence Map

| Retail address | Recovered owner | Source owner | Evidence |
| --- | --- | --- | --- |
| `0x10033E30` | `SpectatorThink` | `src/code/game/g_active.c` | HLIL unlinks a linked spectator entity before the state branch, writes `PM_SPECTATOR`, writes speed `0x1e0` (`480`), builds a `pmove_t`, runs `Pmove`, copies `ps.origin` to `s.origin`, calls `G_TouchTriggers`, stores old/current buttons, returns immediately after attack-edge follow cycling, and then checks a `BUTTON_ANY` edge for stop-follow behavior. |
| `0x10033C00` | `G_TouchTriggers` | `src/code/game/g_active.c` | Symbol map pins the `40,40,52` trigger box, spectator teleporter gating, ET_ITEM checks, and jump-pad reset that the spectator pmove path calls after movement. |
| `0x10035470` | `SpectatorClientEndFrame` | `src/code/game/g_active.c` | Resolves follow1/follow2, mirrors connected non-`PM_SPECTATOR` targets, forces the copied playerstate back to `PM_SPECTATOR | PMF_FOLLOW`, and routes stale explicit player targets through active-team follow cycling before falling back to `StopFollowing`. No POI camera branch is present. |
| `0x10035960` / `0x1003BC30` | `G_CAADRespawnAsSpectator` and `ClientSpawn` spectator handoff | `src/code/game/g_team.c`, `src/code/game/g_client.c` | Round-eliminated Clan Arena / Attack & Defend clients copy the corpse, pre-seed `PM_SPECTATOR`, rerun `ClientSpawn`, count active teams, and only call `FollowCycle` when both sides still have active players. `ClientSpawn` treats a pre-existing `PM_SPECTATOR` as the spectator-spawn selector that makes this handoff work. |
| `0x10040D10` | `StopFollowing` | `src/code/game/g_cmds.c` | Restores persisted team, forces `PM_SPECTATOR`, clears `PMF_FOLLOW`, sets `SPECTATOR_FREE`, resets the spectator target/clientNum to self, and unlinks linked entities. It does not consult `g_teamSpecFreeCam`. |
| `0x10040F30` / `0x10041130` / `0x100412E0` | Follow command and cycling | `src/code/game/g_cmds.c` | Covers player-string follow selection, the `pw` suffix preserve-current-flag-carrier guard, no-arg follow cycling for active team participants, the inner cycle worker, and public next/prev command entry. |
| `0x1002FA20` / cgame `0x10003EF0` | `PM_FlyMove` | `src/code/game/bg_pmove.c` | Both shared movement islands run only `PM_Friction`, `PM_BuildWishMove3D`, `PM_Accelerate(..., pm_flyaccelerate)`, and `PM_StepSlideMove(qfalse)`. There is no Flight fuel/thrust branch. |
| `0x1004DFE0` | `Pickup_Powerup` | `src/code/game/g_items.c` | Flight uses the same direct `quantity * 1000` powerup timer addition as other powerups; registered Flight cvars are not consumed here. |

Observed facts:

1. `SpectatorThink` writes `client->ps.speed = 480`; the older `400` value came
   from the GPL/Q3 baseline, not the retail Quake Live qagame binary.
2. `trap_UnlinkEntity` happens before the spectator pmove setup when
   `ent->r.linked` is non-zero. The current source had the call after
   `G_TouchTriggers`, which inverted the retail ordering.
3. Attack-edge cycling returns immediately. This prevents the same input frame
   from also flowing into the later `BUTTON_ANY` stop-follow branch.
4. The later `BUTTON_ANY` branch calls `StopFollowing` for spectators, and for
   the training-map follow case already represented in source by
   `level.trainingMapActive`.
5. The shared fly-move body has no `STAT_PLAYER_ITEM_THRUST`,
   `STAT_PLAYER_ITEM_TIME`, or `PMF_USE_ITEM_HELD` logic. Those belong to the
   invulnerability holdable movement leaf, not spectator/Flight fly movement.
6. `SpectatorClientEndFrame` validates followed players with
   `cl->ps.pm_type != PM_SPECTATOR`, not `sess.sessionTeam`, and forces the
   copied playerstate back to `PM_SPECTATOR` after mirroring.
7. The retail follow-cycle worker is client-only: it skips disconnected
   clients, `PM_SPECTATOR` clients, clients already marked `PMF_FOLLOW`, and
   cross-team targets when the caller is an active team participant.
8. The previous source POI camera list and `addpoi` / `delpoi` / `pois`
   direct commands have no matching branch in the retail qagame HLIL.
9. `Cmd_Follow_f` does not parse `follow1` or `follow2`; those tokens belong
   to `SetTeam`. The command resolves argument 1 through
   `ClientNumberFromString`, rejects `PM_SPECTATOR` targets, and treats a
   third `"pw"` token as a no-switch guard while the current followed target is
   carrying a flag.
10. The public follow-cycle command entry has no training-map print/gate and
    promotes non-spectator callers by checking `sess.sessionTeam`, not the
    spectator-state enum.
11. `G_CAADRespawnAsSpectator` does not pick a direct follow target, relink the
    entity, or install a free/scoreboard fallback after `ClientSpawn`. The
    retail body relies on pre-seeding `PM_SPECTATOR` before `ClientSpawn`, then
    calls `FollowCycle` only when both active teams still have players.

## Reconstruction

Source changes:

1. Moved spectator unlinking to the retail pre-pmove position and guarded it
   with `ent->r.linked`.
2. Restored the retail spectator speed constant to `480`.
3. Kept `Pmove` before `G_TouchTriggers`, with trigger touch using the moved
   spectator origin.
4. Added the retail control-flow split where attack-edge follow cycling returns
   before the `BUTTON_ANY` stop-follow edge can run.
5. Routed attack-edge and stale-target cycling through the recovered inner
   `FollowCycle` worker instead of the public command wrapper.
6. Rebuilt `SpectatorClientEndFrame` around the retail player-only follow
   target rules, including active-team fallback cycling and no POI support.
7. Rebuilt `StopFollowing` around the exact retail free-spectator state reset.
8. Rebuilt `Cmd_Follow_f` around player-string resolution, the retail `"pw"`
   suffix guard, and `PM_SPECTATOR` target rejection.
9. Removed source-only training-map gates from `Cmd_Follow_f` and
   `Cmd_FollowCycle_f`; the follow state is cleaned up by the retail
   spectator/end-frame paths.
10. Rebuilt the CA/A-D eliminated-player spectator path around the retail
    `PM_SPECTATOR` pre-seed, `ClientSpawn`, team-count, and `FollowCycle`
    sequence, and taught `ClientSpawn` to preserve that pre-existing spectator
    spawn mode.
11. Collapsed `PM_FlyMove` back to the retail four-call 3D wish-vector path.
12. Removed source-only Flight fuel/thrust seeding from `Pickup_Powerup`; the
    registered Flight cvars remain table entries, but `g_items.c` and shared
    pmove no longer consume them.

## Tests

Focused coverage updated:

- `tests/test_game_active_pmove_wiring_parity.py`
- `tests/test_game_attack_defend_parity.py`
- `tests/test_game_factory_regen_parity.py`
- `tests/test_game_helper_seam_parity.py`
- `tests/test_game_spectator_connection_parity.py`
- `tests/test_pmove_helper_parity.py`
- `tests/test_spawn_spec_cvars.py`
- `tests/test_cgame_spectator_parity.py`

Verification command:

```powershell
python -m pytest tests/test_game_attack_defend_parity.py tests/test_game_spectator_connection_parity.py tests/test_game_active_pmove_wiring_parity.py tests/test_game_helper_seam_parity.py tests/test_pmove_helper_parity.py tests/test_game_factory_regen_parity.py tests/test_bg_misc_validation_fixtures.py tests/test_spawn_spec_cvars.py tests/test_cgame_spectator_parity.py -q --tb=short
```

Result: `164 passed`.

## Parity Estimate

Scoped spectator state/movement parity: **before 93% -> after 99.9%**.

The remaining 0.1% is live-behavior confidence around copied playerstate side
fields and training-map follow exits, not a known static mismatch.
Repo-wide parity remains **98%** because this closes a narrow
qagame/shared-pmove lane.
