# Botlib Bot Client And Debug Draw Wrapper Recheck - 2026-06-12

## Scope

This round rechecked the bot-client allocation/free and debug-draw wrapper band
that sits immediately before the server import callback wrappers. The goal was
to pin the qagame-facing bot allocation, usercmd, entity-token, and debug
polygon trap wrappers against the retail Binary Ninja HLIL, and to tie those
wrappers back to the reconstructed server source.

Primary reconstructed files:

- `src/code/server/sv_bot.c`
- `src/code/server/sv_game.c`
- `src/code/server/ql_game_imports.inc`
- `src/code/game/g_syscalls.c`
- `tests/test_botlib_server_game_bridge_parity.py`

Primary Binary Ninja evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt`

Companion evidence:

- `references/analysis/quakelive_symbol_aliases.json`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`

## Observed Retail Facts

- Retail `SV_BotAllocateClient` (`sub_4DCD30`) scans the client array for a
  free slot, returns `-1` on exhaustion, assigns the game entity number, marks
  the client active, stamps server time, sets the bot rate to `0x4000`, and
  stores the Steam bot identity returned by the retail Steam helper.
- Retail `SV_BotFreeClient` (`sub_4DCDB0`) validates the client index, clears
  the client state/name, and clears the bot flag on the associated game entity
  by masking off bit `0x8` in the entity flags field.
- Retail `BotDrawDebugPolygons` (`sub_4DCE10`) lazily registers
  `bot_debug`, `bot_reachability`, `bot_groundonly`, and `bot_highlightarea`,
  builds the `parm0` mask from attack/reachability/ground-only inputs, calls
  botlib `BotLibVarSet` and `Test`, then walks the debug polygon slab and calls
  the supplied draw callback for in-use polygons.
- Retail native qagame wrappers tailcall the server allocation/free and debug
  polygon helpers, copy `lastUsercmd` through `SV_GetUsercmd`, and tokenize
  entity data through `SV_GetEntityToken`.
- The reconstructed legacy syscall switch routes the same calls to
  `SV_BotAllocateClient`, `SV_BotFreeClient`, `SV_GetUsercmd`, `COM_Parse`,
  `BotImport_DebugPolygonCreate`, and `BotImport_DebugPolygonDelete`.

## Reconstruction Decision

No source-code change was needed. The reconstructed bot allocation/free, debug
draw, qagame native import wrappers, qagame syscall shims, and legacy server
syscall cases already match the retail contracts.

The closure was a stricter parity gate:
`test_server_and_native_qagame_bot_client_wrapper_hlil_bodies_match_retail_refs`.
The source-side bridge gate was expanded to cover `BotDrawDebugPolygons`,
`SV_GetUsercmd`, and the legacy syscall cases for bot allocation,
entity-token, and debug polygon forwarding.

## Confidence And Open Questions

- Focused bot client allocation/free wrapper confidence:
  **before 89% -> after 99%**.
- Focused qagame bot client/debug trap wrapper confidence:
  **before 90% -> after 99%**.
- Overall botlib plus qagame/server wiring reconstruction parity:
  **84.12% -> 84.15%**.

Remaining uncertainty is outside this static wrapper band: live bot behavior,
map-specific AAS behavior, and bot decision quality still require broader
validation.
