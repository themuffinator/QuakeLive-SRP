# Botlib AI Export Initializer Bridge Recheck - 2026-06-12

## Scope

This round rechecked the botlib-side public AI export initializer. The retail
owner is `Init_AI_Export` (`sub_4A8110`), which fills the nested `ai_export_t`
table after the AAS and EA export initializers and before the top-level
`GetBotLibAPI` callback tail is assigned.

Primary reconstructed files:

- `src/code/game/botlib.h`
- `src/code/botlib/be_interface.c`
- `tests/test_botlib_internal_parity.py`

Primary evidence:

- Binary Ninja HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part03.txt`
- Ghidra functions table:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- Promoted aliases:
  `references/analysis/quakelive_symbol_aliases.json`

## Observed Retail Facts

- Retail `GetBotLibAPI` calls `sub_4A8110(&data_16dd91c)` after
  `Init_AAS_Export` and `Init_EA_Export`, and before assigning
  `Export_BotLibSetup` at `data_16dda50`.
- Retail `sub_4A8110` has Ghidra row
  `FUN_004a8110,004a8110,674,0,unknown`.
- `sub_4A8110` writes seventy-seven AI callback slots from `arg1[0]` through
  `arg1[0x4c]`, for a `0x134` byte AI export subtable.
- The retail store order matches the reconstructed source groups:
  character, chat, goal, movement, weapon, then the genetic/debug tail.
- The final three retail slots are:
  `GeneticParentsAndChildSelection` at `arg1[0x4a]`,
  `BotDrawDebugAreas` at `arg1[0x4b]`, and `BotDrawAvoidSpots` at
  `arg1[0x4c]`.
- Promoted aliases cover every callback target in this initializer. The
  companion Ghidra table has rows for the initializer and seventy-four callback
  targets; `BotAllocChatState`, `BotAllocMoveState`, and `BotAllocWeaponState`
  remain pinned through Binary Ninja HLIL function headers and aliases.

## Reconstruction Decision

The reconstructed source already matches the retail AI export setup:

- `ai_export_t` declares the seventy-seven public callbacks in retail ABI
  order.
- `Init_AI_Export` assigns the callbacks in the same order.
- `GetBotLibAPI` invokes `Init_AI_Export` at the retail nested-table offset,
  between the EA export initializer and the top-level botlib export tail.

No source-code reconstruction was needed. The closure was a whole-table parity
gate: `test_botlib_ai_public_export_initializer_matches_retail_table_order`.

## Confidence And Open Questions

- Focused AI public export initializer confidence:
  **before 90% -> after 99%**.
- Focused botlib AI export-to-native bridge confidence:
  **before 98% -> after 99%**.
- Overall botlib plus qagame/server wiring reconstruction parity:
  **83.99% -> 84.03%**.

Remaining uncertainty is in deeper AI behavior reconstruction, qagame
consumption of the callbacks, and runtime bot decision quality, not in the
public AI export table wiring.
