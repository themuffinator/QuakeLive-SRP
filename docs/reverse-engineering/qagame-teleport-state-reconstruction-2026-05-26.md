# Quake Live Teleport State Reconstruction - 2026-05-26

## Scope

This pass maps and reconstructs the teleporting state contract across server
qagame, client cgame, shared pmove, bot movement, and dropped powerup trigger
wiring.

Primary source files:

- `src/code/game/g_misc.c`
- `src/code/game/g_trigger.c`
- `src/code/game/g_target.c`
- `src/code/game/g_active.c`
- `src/code/game/g_client.c`
- `src/code/game/g_mover.c`
- `src/code/game/g_items.c`
- `src/code/game/ai_dmq3.c`
- `src/code/cgame/cg_predict.c`
- `src/code/cgame/cg_snapshot.c`
- `src/code/cgame/cg_playerstate.c`
- `src/code/cgame/cg_event.c`
- `src/code/cgame/cg_view.c`

Reference evidence:

- `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/`
- `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil_split/`
- `references/reverse-engineering/ghidra/qagamex86/`
- `references/reverse-engineering/ghidra/cgamex86/`
- `references/symbol-maps/qagame.json`
- `references/symbol-maps/cgame.json`

## Observed Facts

- Retail `qagamex86.dll` `sub_1005a420` is the shared server teleport helper.
  It emits source/destination temp events for non-spectators, unlinks the
  player, writes the destination origin with the one-unit z lift, computes the
  exit velocity from destination angles, scales it to 400 ups, sets
  `pm_time = 160`, ORs `PMF_TIME_KNOCKBACK`, toggles `EF_TELEPORT_BIT`, frees
  any active hook via `sub_1006e330`, sets view angles, kills blockers, mirrors
  playerstate back to entitystate, clears lag history, and relinks only
  non-spectators.
- `sub_1006e330` is already mapped as `Weapon_HookFree`; the body clears the
  owner hook pointer and grapple pull state before freeing the hook entity.
- `target_teleporter_use` (`0x100679D0`) and `trigger_teleporter_touch`
  (`0x1006B9A0`) both resolve a destination target and call `sub_1005a420`.
  The trigger path rejects non-clients, dead players, and non-spectators for
  spectator-only trigger brushes.
- `SP_trigger_teleport` (`0x1006BA00`) runs the shared trigger initializer,
  flips `SVF_NOCLIENT` according to the spectator-only spawnflag, precaches
  `sound/world/jumppad.wav`, sets `ET_TELEPORT_TRIGGER`, installs the touch
  callback, and links the entity.
- `Touch_DoorTriggerSpectator` (`0x1005F1E0`) chooses the door-trigger exit
  face along the thinnest axis and teleports spectators through the shared
  helper.
- `ClientEvents` (`0x10034860`) handles holdable teleporter use through the
  same helper after dropping carried flags/skulls and choosing a spawn point.
- `respawn` (`0x10039F20`) emits the `EV_PLAYER_TELEPORT_IN` temp event for
  immediate non-spectator spawns.
- `G_DroppedPowerupRunFrame` (`0x10050F80`) does not call `TeleportPlayer`
  because it operates on item entities, but it mirrors the teleporter exit
  contract for dropped powerups: destination origin, 400 ups forward velocity,
  +96 z lift, snapped velocity, teleout/telein sounds, and the same missing
  destination warning string.
- Bot movement consumes teleport/blocking state indirectly: retail
  `BotSetupForMovement` maps active `PMF_TIME_KNOCKBACK` plus positive
  `pm_time` to `MFL_TELEPORTED`, before the `PMF_TIME_WATERJUMP` branch.
- Client-side cgame consumes the state over three lanes:
  `CG_SetNextSnap` and `CG_TransitionSnapshot` use `EF_TELEPORT_BIT` to block
  interpolation/error decay, `CG_TouchTriggerPrediction` marks
  `cg.hyperspace` for predicted teleport triggers, and `CG_CalcViewValues` /
  `CG_DrawActiveFrame` converts that flag into hyperspace render flags and
  packet-entity suppression.
- `CG_EntityEvent` routes `EV_PLAYER_TELEPORT_IN` and
  `EV_PLAYER_TELEPORT_OUT` to the retail teleport sound plus `CG_SpawnEffect`.

## Source Reconstruction

The source already carried most of the reconstructed teleport state contract,
including `pm_time = 160`, `PMF_TIME_KNOCKBACK`, `EF_TELEPORT_BIT`, the trigger
and target teleporter callbacks, cgame interpolation gates, hyperspace
prediction, and bot movement consumption.

This pass restores the missing retail hook cleanup edge in
`TeleportPlayer`:

- After toggling `EF_TELEPORT_BIT`, `TeleportPlayer` now frees an active
  grappling hook with `Weapon_HookFree( player->client->hook )`.
- The ordering matches HLIL: teleport movement state first, hook cleanup next,
  then view-angle application and destination telefrag handling.

No runtime launch was required. This was a static reconstruction against the
committed HLIL/Ghidra evidence and source-level structural tests.

## Confidence

High for the reconstructed hook cleanup edge. It is backed by:

- Direct HLIL in `sub_1005a420` showing the `client->hook` null check and
  `sub_1006e330` call.
- Symbol-map ownership for `Weapon_HookFree` at `0x1006E330`.
- Existing source analogue and prototype for `Weapon_HookFree`.
- Multiple adjacent teleport-state stores in the same retail helper matching
  current source offsets and behavior.

Medium-high for the full wiring map. The individual server/cgame/bot anchors
are already named in symbol maps, and the new regression test ties the source
back to the committed HLIL strings and callsites. Remaining uncertainty is in
field-offset naming for some decompiler locals, not in the observable behavior.

## Parity Estimate

- Scoped teleporting state and wiring parity: before 96%, after 99%.
- Repo-wide parity estimate remains 98%.
