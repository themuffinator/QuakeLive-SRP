# Botlib Move-State Lifecycle Recheck - 2026-06-05

## Scope

This pass rechecked the engine-owned botlib movement-state lifecycle and the
avoid-reach reset lane. No source behavior change was needed; the goal was to
pin retail evidence around the current source shape so later cleanup passes do
not "fix" retail-matching quirks by accident.

## Retail Evidence

- Binary Ninja HLIL for `quakelive_steam.exe` shows the move-state allocator
  `sub_49f9c0` allocating `0x304` bytes and using a 64-client handle table.
- `sub_49fa00` and `sub_49fa60` share the retail fatal strings
  `move state handle %d out of range` and `invalid move state %d`.
- `sub_49fab0` copies the `bot_initmove_t` input block, then masks only the
  movement flags that are sourced from the player state.
- `sub_4a5830` clears the avoid-reach id, time, and try arrays at offsets
  `+0x74`, `+0x78`, and `+0x7c`.
- `sub_4a58a0` clears the latest avoid-reach time, then checks the word at
  `+0x80` before decrementing `+0x7c`. With `MAX_AVOIDREACH == 1`, `+0x80`
  is the first word of `avoidspots[0].origin`, matching the source post-loop
  `ms->avoidreachtries[i]` read.
- `sub_4a5920` clears the full `0x304` move-state block.
- The retail AI export initializer assigns reset move state at slot `0x38`,
  reset avoid reach at `0x3b`, reset last avoid reach at `0x3c`, and
  alloc/free/init move state at `0x40..0x42`.

## Reconstruction

- Added aliases for `BotAllocMoveState`, `BotFreeMoveState`,
  `BotMoveStateFromHandle`, `BotInitMoveState`, `BotResetAvoidReach`,
  `BotResetLastAvoidReach`, and `BotResetMoveState`.
- Extended `tests/botlib_internal_harness.c` with a small copied move-state
  model and wrappers for allocation, initialization, reset, and avoid-reach
  probes.
- Added parity tests that verify the source layout, the retail export slots,
  the fatal strings, the full reset size, and the `+0x80` gate behavior.

## Confidence

High. The source field ordering, current helper bodies, retail HLIL offsets,
fatal strings, allocation size, and export table all agree.

## Parity Estimate

- Focused engine-owned botlib move-state lifecycle evidence parity:
  `60% -> 85%`.
- Broader engine-owned botlib internal mapping parity: `74% -> 76%`.
