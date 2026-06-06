# Botlib Movement Late Support Mapping - 2026-06-06

## Scope

This pass closes a documentation and parity-test gap over the late AAS
movement/reachability support corridor. The direct botlib row scan was already
closed except for the documented libjpeg false leads and the folded weapon-jump
thunk, so the useful work here was to pin promoted names that had not yet been
covered by a focused botlib regression gate.

No C source body change or alias change was needed. The checked-in source
already matches the static retail shapes for the helpers below.

## Evidence

- `references/analysis/quakelive_symbol_aliases.json`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part03.txt`
- `src/code/botlib/be_aas_move.c`
- `src/code/botlib/be_aas_reach.c`
- `src/code/botlib/be_ai_move.c`
- `tests/test_botlib_movement_late_support_parity.py`

## Pinned Alias Band

| Address | Alias | Role |
| --- | --- | --- |
| `0x004866A0` | `AAS_DropToFloor` | 100-unit downward trace, startsolid reject, and origin snap to trace end. |
| `0x00486A60` | `AAS_AgainstLadder` | Ladder-area probe with nearby area nudges, ladder face plane proximity, and `AAS_PointInsideFace`. |
| `0x00486C20` | `AAS_OnGround` | Client bbox trace, hit-distance guard, and max-steepness plane check. |
| `0x00486FF0` | `AAS_ApplyFriction` | Horizontal speed/control/stopspeed friction scaling. |
| `0x00487080` | `AAS_ClipToBBox` | Presence bbox expansion and fraction/plane collision clipping against a bbox. |
| `0x004886A0` | `AAS_GetJumpPadInfo` | `trigger_push` model/target parsing, start-area trace, and push velocity derivation. |
| `0x004890E0` | `AAS_Reachability_EqualFloorHeight` | Grounded adjacent-area common-edge walk reachability creation. |
| `0x0048EBE0` | `AAS_FindFaceReachabilities` | Func-bobbing face-to-area reachability search using closest-edge pairs. |
| `0x004A2BC0` | `BotTravel_Elevator` | Elevator approach/center/wait movement state. |
| `0x004A3410` | `BotTravel_FuncBobbing` | Func-bobbing platform approach/center/wait movement state. |
| `0x004A4640` | `BotFinishTravel_WeaponJump` | Air-control finish for rocket/BFG jump reachabilities. |
| `0x004A4700` | `BotTravel_JumpPad` | Walk-to-jumppad-start movement. |
| `0x004A47A0` | `BotFinishTravel_JumpPad` | Air-control finish for jumppad travel. |
| `0x004A4870` | `BotReachabilityTime` | Timeout table for late travel types and fallback error path. |
| `0x004A4910` | `BotMoveInGoalArea` | Final goal-area walk/swim movement and state reset. |

## Source Findings

- `AAS_DropToFloor`, `AAS_AgainstLadder`, `AAS_OnGround`,
  `AAS_ApplyFriction`, and `AAS_ClipToBBox` in `be_aas_move.c` provide the
  low-level movement physics predicates used by prediction and bot movement.
- `AAS_GetJumpPadInfo`, `AAS_Reachability_EqualFloorHeight`, and
  `AAS_FindFaceReachabilities` in `be_aas_reach.c` bridge those movement
  primitives into reachability generation for jumppads, walk links, and
  func-bobbing movers.
- `BotTravel_Elevator`, `BotTravel_FuncBobbing`,
  `BotFinishTravel_WeaponJump`, `BotTravel_JumpPad`,
  `BotFinishTravel_JumpPad`, `BotReachabilityTime`, and `BotMoveInGoalArea`
  in `be_ai_move.c` are the late travel dispatch bodies reached by
  `BotMoveToGoal`.
- `BotMoveToGoal` uses `AAS_OnGround` and `AAS_AgainstLadder` to refresh
  movement flags, uses `BotReachabilityTime` when adopting a reachability, and
  dispatches the late elevator, func-bobbing, weapon-jump, jumppad, and
  goal-area handlers in the same source order checked by the parity gate.

## Parity Estimate

- Focused late AAS movement/support mapping:
  **before 68% -> after 96%**
- Focused late travel dispatch coverage:
  **before 72% -> after 96%**
- Overall botlib plus movement/reachability wiring:
  **before 86% -> after 87%**

The overall movement is intentionally small because this pass locks down
already-promoted source owners rather than adding new behavior. The remaining
uncertainty is live map-dependent movement quality and the folded
rocket/BFG wrapper at `0x00486F40`, not the static helper ownership covered
here.

## Validation

- `python -m pytest tests/test_botlib_movement_late_support_parity.py -q`
  - `4 passed`
