# Botlib Obstacle Prediction Mapping - 2026-06-05

## Scope

This pass rechecked qagame bot obstacle prediction, the engine-owned
`AAS_PredictRoute` bridge, and adjacent bot inventory wiring against the
committed Binary Ninja HLIL and Ghidra retail references.

The main reconstruction result is a symbol-map correction: qagame retail
`0x1001DCF0` is `BotAIPredictObstacles`, not `BotCheckForGrenades`. The current
C source for the obstacle-prediction path already matches the recovered retail
shape. A follow-up source-shape correction in this cluster inlined the simple
grenade avoidance branch into `BotCheckSnapshot`, matching retail
`sub_1001eaf0`.

## Retail Evidence

- Qagame Binary Ninja HLIL at `0x1001DCF0` gates the body on the
  `bot_predictobstacles` cvar, compares `bs->predictobstacles_goalareanum`
  against the incoming goal area, and applies the same six-second throttle found
  in `ai_dmq3.c::BotAIPredictObstacles`.
- The same HLIL block calls the botlib import table at slot `0x13c` with the
  recovered constants `0x64`, `0x3e8`, `6`, `0x400`, `0x4000000`, and `0`.
  These line up with `trap_AAS_PredictRoute(..., 100, 1000,
  RSE_USETRAVELTYPE|RSE_ENTERCONTENTS, AREACONTENTS_MOVER, TFL_BRIDGE, 0)`.
- The mover branch tests `RSE_ENTERCONTENTS` plus `AREACONTENTS_MOVER`, extracts
  the mover model number, resolves the mover entity, and routes through the
  activation helpers corresponding to `BotGetActivateGoal`,
  `BotIsGoingToActivateEntity`, `BotGoForActivateGoal`, and
  `BotEnableActivateGoalAreas`.
- Ghidra companion call sites in `decompile_top_functions.c` repeatedly call
  `FUN_1001dcf0` from seek and battle node bodies with a `bot_goal_t`-shaped
  stack object, matching the source call pattern for `BotAIPredictObstacles`.
- Host botlib HLIL at `0x00494870` and the Ghidra decompile for
  `AAS_PredictRoute` initialize `endarea`, `stopevent`, `endcontents`,
  `endtravelflags`, `endpos`, and `time`; they do not initialize or maintain
  `numareas`. The source keeps that retail shape.

## Negative Checks

- The HMG inventory hypothesis was rejected. Retail `BotUpdateInventory`
  projects weapon bits through the chaingun-era inventory slots and skips
  `INVENTORY_HEAVYMACHINEGUN`; retail `BotNormalizeAmmoInventory` only rewrites
  the ammo slab from `INVENTORY_SHELLS` through `INVENTORY_BELT` when values are
  `-1`. The source already mirrors this and should not add
  `INVENTORY_HEAVYBULLETS` normalization without new evidence.
- `bot_predictobstacles` belongs to qagame setup, not host/server pre-registry
  wiring. The qagame cvar registration remains the only required source owner
  for this pass.
- The old `0x1001DCF0 -> BotCheckForGrenades` symbol-map entry included a
  duplicate-suppression claim that does not match the current source and is not
  supported by the observed retail obstacle-prediction body.
- Retail `BotCheckSnapshot` inlines the grenade avoidance check. Binary Ninja
  HLIL for `0x1001EAF0` calls `BotCheckEvents`, then checks the snapshot
  entity for `ET_MISSILE` plus `WP_GRENADE_LAUNCHER`, emits a 160-unit
  `AVOID_ALWAYS` avoid spot, and then calls `BotCheckForProxMines`.

## Changes

- Corrected `references/symbol-maps/qagame.json` so `0x1001DCF0` maps to
  `BotAIPredictObstacles` with the recovered route-prediction constants and
  mover activation path.
- Added focused regression coverage in
  `tests/test_botlib_internal_parity.py` for:
  - the qagame symbol-map correction,
  - the `BotAIPredictObstacles` source shape,
  - the qagame HLIL import-slot call and activation helpers,
  - the engine `AAS_PredictRoute` initialization layout,
  - the negative HMG inventory evidence.
- Reconstructed `src/code/game/ai_dmq3.c::BotCheckSnapshot` so grenade
  avoidance is inlined before `BotCheckForProxMines`, instead of calling a
  standalone `BotCheckForGrenades` helper that has no promoted retail owner.

## Open Questions

- No standalone retail address for the simple source-level grenade helper was
  promoted. The source now follows the observed retail shape by keeping the
  grenade branch inside `BotCheckSnapshot`.
- `aas_predictroute_t::numareas` remains a source/API layout field whose retail
  `AAS_PredictRoute` owner does not update in the observed engine references.
  Future work should only change it if a different retail caller proves a
  writer.

## Parity Estimate

- Focused qagame obstacle-prediction mapping: `45% -> 95%`. The principal gap
  was a wrong promoted symbol-map identity; the source body and import wiring
  were already close to retail.
- Focused bot inventory HMG audit: `70% -> 88%`. No code change, but the
  explicit negative evidence reduces false reconstruction risk.
- Overall botlib plus related wiring: approximately `64% -> 65%`.
