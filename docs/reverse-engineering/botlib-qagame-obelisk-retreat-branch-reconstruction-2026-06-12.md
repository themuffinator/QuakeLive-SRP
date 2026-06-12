# Botlib QAGame Obelisk Retreat Branch Reconstruction - 2026-06-12

## Scope

This pass reconstructs the `GT_OBELISK` retreat arm in qagame's
`BotTeamGoals` dispatcher and removes the remaining source-only
`BotObeliskRetreatGoals` no-op from `ai_dmq3.c` / `ai_dmq3.h`.

## Evidence

- Owning retail binary: `qagamex86.dll`.
- Binary Ninja HLIL:
  `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt`.
- Companion Ghidra rows:
  - `FUN_10015120,10015120,722,0,unknown`
  - `FUN_10015960,10015960,219,0,unknown`
- Alias support:
  - `sub_10015120` / `FUN_10015120` => `BotObeliskSeekGoals`
  - `sub_10015960` / `FUN_10015960` => `BotTeamGoals`

Observed facts:

- Retail `BotTeamGoals` gates on `arg2 != 0` for retreat mode and dispatches
  `GT_CTF`, `GT_1FCTF`, and `GT_HARVESTER` to their reduced retreat helpers.
- Retail retreat mode has no `GT_OBELISK` helper call; it falls through to the
  shared order-time reset.
- Retail `BotTeamGoals` contains no promoted or table-backed
  `BotObeliskRetreatGoals` body between `BotGoHarvest` and
  `BotHarvesterSeekGoals`.
- The non-retreat `GT_OBELISK` branch calls `sub_10015120(arg1)`, and the
  alias map pins that target as `BotObeliskSeekGoals`.

Reconstruction:

- The source retreat dispatcher no longer has a `GT_OBELISK` helper branch,
  matching retail's fallthrough behavior for Obelisk retreat mode.
- The source seek dispatcher continues to route `GT_OBELISK` to
  `BotObeliskSeekGoals(bs)`.
- The source-only `BotObeliskRetreatGoals` empty function and declaration were
  removed.
- `tests/test_botlib_qagame_ai_dmq3_team_goal_parity.py` now pins the
  retreat-versus-seek source shape, the retail HLIL call anchor at
  `0x100159f7`, and the absence of the source-only retreat stub.

## Confidence

Confidence is high. The reconstruction is supported by the retail HLIL call
target, function-size rows, promoted aliases, existing source context, and the
absence of a distinct retail function row for the no-op retreat helper.

Parity estimate: focused Obelisk retreat-branch reconstruction confidence
**35% -> 99%**; focused qagame team-goal dispatcher parity **96% -> 98%**;
overall botlib plus qagame/server wiring reconstruction parity **84.15% ->
84.18%**.
