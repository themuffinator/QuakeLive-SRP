# Botlib Goal Tail Item Producer Reconstruction - 2026-06-12

## Scope

This pass reconstructed item-goal behavior for the two-word Quake Live
`bot_goal_t` tail. Earlier work sized the goal record to `0x40` bytes and kept
the tail as `qlGoalExtra[2]` so activate-goal records and goal-stack copies
matched retail. The first round focused on whether any retail producer writes
those tail words directly; the follow-up in the same evidence band recovered a
consumer-side gate for word `0x0e`.

## Retail evidence

- Owning binary: `quakelive_steam.exe`.
- Owning function: `BotGetLevelItemGoal` / `sub_49DDF0`.
- Binary Ninja HLIL writes the normal item-goal words, including:
  - origin words `0x00..0x02`;
  - areanum word `0x03`;
  - mins/maxs words `0x04..0x09`;
  - entitynum word `0x0a`;
  - number word `0x0b`;
  - flags word `0x0c`.
- The same retail body clears goal word `0x0f` and goal word `0x0e` before
  returning the level-item number.
- Adjacent stack helpers copy the whole `0x40`-byte goal record:
  `BotPushGoal`, `BotGetTopGoal`, and `BotGetSecondGoal` all use retail
  `0x40` copies.
- Follow-up retail evidence: `BotItemGoalInVisButNotVisible` /
  `sub_49F560` enters the trace path only when the item flag is set and goal
  word `0x0e` is zero.

## Source reconstruction

- `BotGetLevelItemGoal` now clears `goal->qlGoalExtra[0]` and
  `goal->qlGoalExtra[1]` when it fills a matching level-item goal.
- `BotItemGoalInVisButNotVisible` now rejects non-item goals and goals with
  `qlGoalExtra[0]` set before doing its visibility trace, matching the retail
  word-`0x0e` gate.
- `bot_goal_t::qlGoalExtra` remains generically named. The recovered evidence
  proves producer initialization for item goals, a visibility-path gate for
  word `0x0e`, and full-record preservation through the goal stack; it does
  not yet identify a stronger gameplay meaning for word `0x0f`.
- The `be_ai_goal.h` field comment now records the recovered retail behavior:
  item-goal producer clears and word `0x0e` gates item visibility rechecks.

## Verification

- `tests/test_botlib_goal_item_parity.py` pins the source producer writes,
  visibility consumer gate, and retail HLIL anchors for goal words `0x0e` and
  `0x0f`.
- `tests/test_botlib_internal_parity.py` pins the `bot_goal_t` field comment
  and the broader internal botlib source gate.

## Parity estimate

- Focused `BotGetLevelItemGoal` tail-producer confidence:
  **before 70% -> after 94%**.
- Focused `bot_goal_t` ABI/layout confidence:
  **before 97% -> after 98%**.
- Overall botlib plus qagame/server wiring reconstruction parity:
  **before 84.29% -> after 84.31%**.
