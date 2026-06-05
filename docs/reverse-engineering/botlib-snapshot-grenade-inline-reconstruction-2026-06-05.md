# Botlib Snapshot Grenade Inline Reconstruction - 2026-06-05

## Scope

This pass rechecked the qagame bot snapshot sweep around grenade avoidance,
prox-mine handling, and botlib avoid-spot insertion. The owning retail function
is qagame `0x1001EAF0`, mapped as `BotCheckSnapshot`.

## Retail Evidence

- Binary Ninja HLIL for `0x1001EAF0` clears the avoid-spot list through import
  slot `+0x2c4`, resets the kamikaze body and prox-mine count, and loops over
  `BotAI_GetSnapshotEntity`.
- Inside the loop, retail calls `sub_1001e4c0` (`BotCheckEvents`), then checks
  the local snapshot state for `ET_MISSILE` plus `WP_GRENADE_LAUNCHER`. When
  that branch matches, it calls the botlib avoid-spot import with radius `160`
  and `AVOID_ALWAYS`.
- The same loop then calls `sub_1001e400` (`BotCheckForProxMines`) and keeps
  the kamikaze-body branch local to `BotCheckSnapshot`.

## Source Reconstruction

- `src/code/game/ai_dmq3.c::BotCheckSnapshot` now inlines the grenade avoidance
  branch before `BotCheckForProxMines`.
- The standalone `BotCheckForGrenades` helper was removed from source because
  no retail owner was promoted for it and the branch is visible inline in the
  retail snapshot sweep.
- `references/symbol-maps/qagame.json` already keeps `BotCheckSnapshot` at
  `0x1001EAF0` and records the inlined grenade branch.

## Verification

- `tests/test_botlib_internal_parity.py::test_qagame_bot_ai_aliases_cover_recent_botlib_mapping_round`
  now asserts that source no longer defines or calls `BotCheckForGrenades`, and
  that the snapshot body contains the retail ordering: avoid-spot clear,
  snapshot loop, `BotCheckEvents`, inline grenade avoid-spot branch,
  `BotCheckForProxMines`, kamikaze-body scan, and the local player-state event
  tail. The same test also keeps the retail HLIL evidence for `BotCheckEvents`
  and `BotCheckForProxMines`.

## Parity Estimate

- Focused qagame snapshot/avoidance source shape: `72% -> 94%`.
- Overall botlib plus related wiring: approximately `68% -> 69%`.
