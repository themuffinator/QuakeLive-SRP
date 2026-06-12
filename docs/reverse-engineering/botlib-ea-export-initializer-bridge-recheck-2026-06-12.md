# Botlib EA Export Initializer Bridge Recheck - 2026-06-12

## Scope

This round rechecked the botlib-side Elementary Action export initializer.
The retail owner is `Init_EA_Export` (`sub_4A8060`), which fills the nested
`ea_export_t` table immediately after `Init_AAS_Export` and before
`Init_AI_Export` in `GetBotLibAPI`.

Primary reconstructed files:

- `src/code/game/botlib.h`
- `src/code/botlib/be_interface.c`
- `tests/test_botlib_ea_parity.py`

Primary evidence:

- Binary Ninja HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part03.txt`
- Ghidra functions table:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- Promoted aliases:
  `references/analysis/quakelive_symbol_aliases.json`

## Observed Retail Facts

- Retail `GetBotLibAPI` calls `sub_4A8060(&data_16dd8b8)` after the AAS export
  initializer and before the AI export initializer.
- Retail `sub_4A8060` has Ghidra row
  `FUN_004a8060,004a8060,175,0,unknown`.
- `sub_4A8060` fills twenty-five EA callback slots. Most stores follow the
  visible source assignment order, but not strictly increasing struct offsets:
  `EA_Crouch` is stored to `arg1[0x10]` before `EA_MoveUp` through
  `EA_MoveRight` are stored to `arg1[0xa]..arg1[0xf]`.
- The retail `EA_EndRegular` callback stores the tiny no-op stub
  `sub_4D7980` at `arg1[0x16]`. HLIL shows `EA_GetInput` at `arg1[0x17]`
  immediately before that no-op store.
- Ghidra rows and promoted aliases cover the stable EA callbacks. The no-op
  `sub_4D7980` remains intentionally unpromoted in the alias map and is pinned
  by its `FUN_004d7980` row and HLIL table slot.

## Reconstruction Decision

The reconstructed source already matches the retail EA export setup:

- `ea_export_t` declares the public callback fields in the retail ABI order.
- `Init_EA_Export` assigns the callbacks in the retail source order, including
  assigning `EA_Crouch` before the movement-direction callbacks.
- `EA_EndRegular` remains an intentionally empty source function, matching the
  retail one-byte no-op export target.

No source-code reconstruction was needed. The closure was a whole-table parity
gate: `test_botlib_ea_public_export_initializer_matches_retail_store_order`.

## Confidence And Open Questions

- Focused EA public export initializer confidence:
  **before 92% -> after 99%**.
- Focused botlib EA export-to-native bridge confidence:
  **before 98% -> after 99%**.
- Overall botlib plus qagame/server wiring reconstruction parity:
  **83.96% -> 83.99%**.

Remaining uncertainty is outside this static EA export table: qagame bot input
consumption and runtime movement quality remain covered by the broader botlib
AI tests.
