# Botlib Activate-Goal Source And Mapping Pass - 2026-06-05

## Scope

This pass rechecked the qagame activate-goal helper cluster used by botlib route
prediction and blocked-movement handling. It focused on the contiguous retail
range from `BotFuncButtonActivateGoal` through `BotRandomMove`, immediately
before the already-mapped `BotAIBlocked` and `BotAIPredictObstacles` callers.

## Retail Evidence

- Binary Ninja HLIL for `0x1001CD40` fetches the BSP `classname` key and gates
  the no-classname error path on `var_a88 != 0`, i.e. the first byte of the
  stack buffer, not the buffer pointer.
- Ghidra agrees in `FUN_1001cd40`: after the same `classname` epair fetch,
  `abStack_a88[0] != 0` selects the normal `func_door` comparison path.
- Binary Ninja HLIL for `0x1001D810` generates a random yaw, builds a direction
  vector, calls the bot move import at `data_104b13ac + 0x2a0` with speed `400`
  and move type `1`, clears the move-result failure word, and stores the moved
  direction.
- `BotAIBlocked` calls `0x1001D810` only from the move-result type `8` branch,
  matching source `RESULTTYPE_INSOLIDAREA` and `ai_dmq3.c::BotRandomMove`.
- The GPL debug announcer strings used by
  `ai_dmq3.c::BotPrintActivateGoalInfo` are not present in the committed
  retail HLIL/Ghidra qagame references.

## Changes

- `ai_dmq3.c::BotGetActivateGoal` now checks `!*classname` after the first BSP
  classname fetch, matching the retail first-byte guard and fixing the previous
  always-false stack-array pointer test.
- `references/symbol-maps/qagame.json` now maps `0x1001D810` to
  `BotRandomMove` and documents the negative evidence for
  `BotPrintActivateGoalInfo`.
- `references/analysis/quakelive_symbol_aliases.json` now covers the paired
  `FUN_` and `sub_` names for the activate-goal helper run:
  `BotFuncButtonActivateGoal`, `BotFuncDoorActivateGoal`,
  `BotTriggerMultipleActivateGoal`, the activate-goal stack helpers,
  `BotGetActivateGoal`, `BotGoForActivateGoal`, and `BotRandomMove`.
- `tests/test_botlib_internal_parity.py` now asserts the source guard, alias
  coverage, symbol-map correction, retail HLIL/Ghidra first-byte checks, random
  move body evidence, and absence of the GPL debug speech strings from retail
  references.

## Open Questions

- `BotPrintActivateGoalInfo` remains present in source as a GPL-side helper, but
  this pass did not find retail evidence for promoting it to a recovered qagame
  function. Keep it out of the curated retail map unless a future reference
  finds the debug speech path in retail.

## Parity Estimate

- Focused activate-goal caller/source tranche: `86% -> 94%`.
- Overall botlib plus related qagame wiring: approximately `68% -> 69%`.
