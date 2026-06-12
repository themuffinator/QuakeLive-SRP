# Botlib Server Frame Callsite Wiring Recheck - 2026-06-12

## Scope

This round rechecked the server-owned callsites that drive botlib frames from
retail Quake Live. The focal function remains `SV_BotFrame` (`sub_4DD670`),
but this pass maps where retail calls it from server startup, spawn/restart
settling, and the live `SV_Frame` loop.

Primary reconstructed files:

- `src/code/server/sv_bot.c`
- `src/code/server/sv_init.c`
- `src/code/server/sv_main.c`
- `tests/test_botlib_server_game_bridge_parity.py`

Primary Binary Ninja evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt`

Companion evidence:

- `references/analysis/quakelive_symbol_aliases.json`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`

## Observed Retail Facts

- Retail `SV_BotFrame` is `sub_4DD670`; HLIL shows it checks both
  `bot_enable` and the game VM before jumping through the qagame
  `BOTAI_START_FRAME` export slot.
- Retail `SV_Init` (`sub_4E3AD0`) calls `SV_BotInitCvars`
  (`sub_4DD6F0`) and then tailcalls `SV_BotInitBotLib` (`sub_4DD940`).
- Retail `SV_SpawnServer` (`sub_4E3510`) initializes game progs through
  `sub_4E2C10`, runs three settle frames with a game-frame call followed by
  `sub_4DD670(data_1333780)`, then creates the baseline through
  `sub_4E31B0`.
- After reconnecting clients, retail `SV_SpawnServer` runs one more game frame
  and calls `sub_4DD670` again before advancing server time.
- Retail `SV_Frame` (`sub_4E49D0`) calls `sub_4DD670(data_1333780 + residual)`
  on the non-dedicated path before the frame-wait gate, and calls
  `sub_4DD670(data_1333780)` on the dedicated path after ping calculation and
  before the `GAME_RUN_FRAME` loop.

## Reconstruction Decision

The reconstructed source already matches this retail callsite shape:

- `SV_Init` initializes bot cvars before botlib.
- `SV_SpawnServer` calls `SV_BotFrame` inside the three settling frames before
  baseline creation and once more after reconnecting clients.
- `SV_Frame` preserves the retail dedicated/non-dedicated split for bot-frame
  time: `svs.time + sv.timeResidual` for non-dedicated and `svs.time` for
  dedicated.

No source-code reconstruction was needed. The closure was a Binary Ninja-backed
callsite parity gate:
`test_server_bot_frame_callsite_wiring_matches_retail_binary_ninja_refs`.

## Confidence And Open Questions

- Focused server bot-frame callsite wiring confidence:
  **before 90% -> after 99%**.
- Focused botlib server lifecycle wiring confidence:
  **before 98% -> after 99%**.
- Overall botlib plus qagame/server wiring reconstruction parity:
  **84.03% -> 84.06%**.

Remaining uncertainty is deeper bot decision behavior and map-specific runtime
validation, not this static server-to-botlib frame scheduling boundary.
