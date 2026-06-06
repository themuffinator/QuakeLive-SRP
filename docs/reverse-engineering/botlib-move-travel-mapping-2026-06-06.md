# Botlib Movement Travel Mapping - 2026-06-06

This pass maps the Quake Live retail `be_ai_move.c` movement helper and travel
method corridor against the committed `quakelive_steam.exe` HLIL and Ghidra
function rows. It follows the AAS route pass by pinning the higher-level bot
movement decisions that consume route reachabilities and expose the movement
helpers through botlib/qagame wiring.

## Evidence Inputs

- Canonical binary: `assets/quakelive/quakelive_steam.exe`
- Binary Ninja HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part03.txt`
- Ghidra function rows:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- Reconstructed source owner: `src/code/botlib/be_ai_move.c`
- Public/export wiring:
  `src/code/game/botlib.h`, `src/code/botlib/be_interface.c`,
  `src/code/server/sv_game.c`, `src/code/server/ql_game_imports.inc`,
  and `src/code/game/g_syscalls.c`

## Promoted And Corrected Names

The mapped corridor starts with mover/support helpers, continues through direct
steering, then covers travel methods and finish handlers used by
`BotMoveToGoal`.

| Retail address | Promoted name | Evidence summary |
|---|---|---|
| `sub_4A00B0` | `BotOnMover` | BSP model bounds plus mover-origin lookup, client bbox trace, and entity-model match. |
| `sub_4A0270` | `MoverDown` | Model origin plus `origin[2] + maxs[2] < reach->start[2]` elevator-down test. |
| `sub_4A0490` | `BotOnTopOfEntity` | Presence bbox trace three units down and non-world/non-none entity return. |
| `sub_4A0540` | `BotAddToAvoidReach` | `MAX_AVOIDREACH == 1` slot update with `AAS_Time() + avoidtime`. |
| `sub_4A0600` | `DistanceFromLineSquared` | Projection onto line, endpoint fallback, and squared distance return. |
| `sub_4A0A50` | `BotGetReachabilityToGoal` | `AAS_NextAreaReachability`, `AAS_ReachabilityFromNum`, route time, avoid spots, and best-time selection. |
| `sub_4A0C00` | `BotAddToTarget` | Segment clipping against lookahead distance and target copy. |
| `sub_4A0F10` | `BotVisible` | Single solid trace with full-fraction visibility return. |
| `sub_4A10E0` | `MoverBottomCenter` | BSP model center plus mover origin and reach start Z. |
| `sub_4A11A0` | `BotGapDistance` | Stair-friendly down trace followed by 8..100 gap probe. |
| `sub_4A1340` | `BotCheckBarrierJump` | Up/horizontal/down traces, `EA_Jump`, `EA_Move`, and `MFL_BARRIERJUMP`. |
| `sub_4A18E0` | `BotCheckBlocked` | Short path trace, blocked entity fields, and on-top-of-obstacle fallback. |
| `sub_4A1AA0` | `BotTravel_Walk` | Start/end steering, gap slowdown, walk flag handling, and movedir copy. |
| `sub_4A1C20` | `BotTravel_Crouch` | Reach-end direction, `EA_Crouch`, speed `400`. |
| `sub_4A1CD0` | `BotTravel_BarrierJump` | Start distance threshold, `EA_Jump`, capped approach speed. |
| `sub_4A1DC0` | `BotFinishTravel_BarrierJump` | Velocity-Z threshold and reach-end steering. |
| `sub_4A1E70` | `BotTravel_Swim` | Reach-start swimming vector, movement view angles, swimview flag. |
| `sub_4A1F30` | `BotTravel_WaterJump` | Reach-end vector with random vertical boost, forward/up movement, movement-view flag. |
| `sub_4A2040` | `BotFinishTravel_WaterJump` | Water/slime/lava contents check and random boosted end vector. |
| `sub_4A21A0` | `BotTravel_WalkOffLedge` | Start/end horizontal distance, optional horizontal jump velocity, and ledge approach speeds. |
| `sub_4A2380` | `BotAirControl` | 50-frame gravity simulation and `400 - (400 - 13 * dist)` speed. |
| `sub_4A24E0` | `BotFinishTravel_WalkOffLedge` | Reach-end lead point, `BotAirControl`, fallback horizontal steering. |
| `sub_4A2620` | `BotTravel_Jump` | `AAS_JumpReachRunStart`, 80-unit run-start probe, delayed jump, `ms->jumpreach`. |
| `sub_4A2900` | `BotFinishTravel_Jump` | `ms->jumpreach` guard and airborne speed `800`. |
| `sub_4A2A00` | `BotTravel_Ladder` | Ladder-facing view vector, zero movement command, and forward movement. |
| `sub_4A2AD0` | `BotTravel_Teleport` | `MFL_TELEPORTED` guard, teleporter start steering, 200/400 speed split. |
| `sub_4A3110` | `BotFinishTravel_Elevator` | Bottom-center versus top-end Z-distance choice with speed `300`. |
| `sub_4A3260` | `BotFuncBobStartEnd` | Signed `edgenum` endpoint unpacking and spawnflag-axis selection. |

One prior alias was corrected: `sub_4A2620` had been listed as
`BotFinishTravel_WalkOffLedge`, but the HLIL contains `AAS_JumpReachRunStart`,
the 80-unit run-start probe, `EA_DelayedJump`, and the `jumpreach` assignment,
which belongs to `BotTravel_Jump`. The walk-off-ledge pair is now mapped as
`sub_4A21A0 -> BotTravel_WalkOffLedge` and
`sub_4A24E0 -> BotFinishTravel_WalkOffLedge`.

## Source And Wiring Status

No C body change is justified by this pass. The current `be_ai_move.c` source
already preserves the retail movement/travel shape for the mapped corridor:
`BotMoveToGoal` dispatches the on-ground travel switch to the travel methods,
then dispatches airborne/continuation handling to the finish handlers. The
public `ai_export_t` layout, `Init_AI_Export`, legacy syscall wrappers, server
VM syscall dispatch, and Quake Live native import slab all still expose the
same movement helpers.

## Validation

Added `tests/test_botlib_move_travel_parity.py` to pin:

1. Alias names, Ghidra function-row sizes, and HLIL function headers for the
   movement/travel helper corridor.
2. Source shape for mover detection, reachability selection, movement view
   targets, visible-position prediction, direct movement, barrier jumps, gap
   checks, air control, travel methods, finish methods, and `BotMoveToGoal`
   dispatch.
3. Public botlib export order, `Init_AI_Export`, server VM syscall dispatch,
   Quake Live native import slab, `ql_game_imports.inc` wrappers, and qagame
   syscall wrappers.

Focused parity estimate for the mapped `be_ai_move.c` movement/travel corridor:
**before 73% -> after 94%**. Overall botlib plus movement/import wiring moves
approximately **80% -> 82%** because this pass corrects and pins a broad static
runtime tranche, while live-map behavior, bot tactical quality, and `.aas`
content-dependent movement remain outside this static mapping round.
