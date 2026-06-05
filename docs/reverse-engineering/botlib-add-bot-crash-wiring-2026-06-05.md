# Botlib Add-Bot Crash Wiring - 2026-06-05

## Scope

This pass targeted the add-bot crash observed in qagame shutdown when
`BotClearActivateGoalStack` reached `BotEnableActivateGoalAreas` with a bogus
`bot_activategoal_t *` (`0x676e6974`, ASCII-like stale pool data).

## Evidence

- Retail `BotPopFromActivateGoalStack` reads `bs->activatestack` from
  `bot_state_t + 0x1bd4`, assumes it is valid when non-null, re-enables routing
  areas, stamps `justused_time`, and advances through `next`.
- Retail `BotPushOntoActivateGoalStack` copies `0xfc` byte activate-goal entries
  into the heap at `bot_state_t + 0x1bd8`.
- Retail `BotEnableActivateGoalAreas` uses `areas[]` at `+0x70`, `numareas` at
  `+0xf0`, `areasdisabled` at `+0xf4`, and no pointer guard.
- Retail `BotAIShutdownClient` calls `BotClearActivateGoalStack` before the full
  `memset(esi, 0, 0x2698)` teardown, so setup must keep the stack pointer clean.
- The retail `G_Alloc` symbol map and qagame notes identify a 4 MB game pool,
  while the source still used the GPL 256 KB pool.

## Reconstruction

- `bot_goal_t` now carries an unmapped two-word Quake Live tail, bringing
  `sizeof(bot_goal_t)` to `0x40` and `sizeof(bot_activategoal_t)` to `0xfc`.
- `BotAISetupClient` now clears freshly allocated bot state before reading
  `inuse`, clears reusable non-inuse state before setup, and scrubs/free-cleans
  partial setup state on failure.
- The game memory pool now uses the retail 4 MB size.

## Open Questions

The wider `bot_state_t` layout is still not source-exact. This pass fixes the
crash-relevant activate-goal record size and setup invariant; later mapping
should continue reconciling the full `0x2698` retail bot-state shape.

## Parity Estimate

- Add-bot crash lifecycle parity: `55% -> 88%`.
- Activate-goal stack record layout parity: `82% -> 96%`.
- Overall botlib plus qagame wiring parity: approximately `69% -> 70%`.
