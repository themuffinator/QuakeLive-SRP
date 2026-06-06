# Botlib Server/Game Bridge Mapping - 2026-06-06

## Scope

This pass closes the server-to-qagame bridge around the botlib import surface:
`SV_Bot*`, `BotImport_*`, and the native `QL_G_trap_Bot*` wrappers at
`0x004DCD30..0x004DDAC0` and `0x004E1610..0x004E1800`.

Unlike the adjacent cgame and parser passes, this round includes a small source
reconstruction. Retail HLIL shows qagame native import slots for bot free and
debug polygon create/delete at slots 44, 47, and 48. The source already had
legacy wrappers for those calls, but the native enum, syscall remap, and server
native import table did not bind the recovered native slots.

## Evidence

- `references/analysis/quakelive_symbol_aliases.json`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part07.txt`
- `src/code/server/sv_bot.c`
- `src/code/server/sv_game.c`
- `src/code/server/ql_game_imports.inc`
- `src/code/game/g_public.h`
- `src/code/game/g_syscalls.c`
- `tests/test_botlib_server_game_bridge_parity.py`

## Pinned Surface

The new parity gate pins the promoted server botlib bridge aliases from
`SV_BotAllocateClient` through `SV_BotGetSnapshotEntity`, including the
`BotImport_*` callbacks handed to `GetBotLibAPI`.

The qagame-side wrapper slab is pinned from `QL_G_trap_BotAllocateClient`
through `QL_G_trap_BotUserCommand`, including `SV_GetUsercmd`,
`SV_GetEntityToken`, debug polygon wrappers, `PC_AddGlobalDefine`, direct
botlib setup/shutdown tailcalls, and botlib-export table jumps.

## Source Reconstruction

- Added `G_QL_IMPORT_BOT_FREE_CLIENT = 44`.
- Added `G_QL_IMPORT_DEBUG_POLYGON_CREATE = 47`.
- Added `G_QL_IMPORT_DEBUG_POLYGON_DELETE = 48`.
- Mapped `G_BOT_FREE_CLIENT`, `G_DEBUG_POLYGON_CREATE`, and
  `G_DEBUG_POLYGON_DELETE` through `G_MapNativeImport`.
- Bound those slots in `SV_InitGameProgs` to the existing
  `QL_G_trap_BotFreeClient`, `QL_G_trap_DebugPolygonCreate`, and
  `QL_G_trap_DebugPolygonDelete` wrappers.

## Retail Shape Notes

- `SV_BotAllocateClient` scans `svs.clients`, claims an active bot slot, updates
  the paired gentity, sets `NA_BOT`, and uses the retail `16384` rate constant.
- `SV_BotFreeClient` validates the range, frees the client state, clears the bot
  flag, resets the network address to `NA_BAD`, and refreshes the gentity bot
  flag.
- `SV_BotFrame` gates on `bot_enable` and `gvm`, then calls
  `BOTAI_START_FRAME`.
- `SV_BotLibSetup` and `SV_BotLibShutdown` tail through `botlib_export`.
- `SV_BotGetConsoleMessage` consumes reliable server commands in order.
- `SV_BotGetSnapshotEntity` indexes the current outgoing snapshot frame.
- The native qagame table at `0x0056D02C..0x0056D070` matches slots 43 through
  60, including the three newly bound source slots.

## Coverage Result

`tests/test_botlib_server_game_bridge_parity.py` now scans both promoted alias
ranges and requires every botlib/debug-polygon bridge alias in those ranges to
have a direct `test_botlib_*.py` mention.

## Parity Estimate

- Focused server/qagame botlib bridge alias coverage:
  **before 72% -> after 100%**
- Focused native qagame botlib import-slot source parity:
  **before 82% -> after 98%**
- Focused botlib plus server/game wiring:
  **before 89% -> after 90%**

The repo-wide parity estimate remains effectively unchanged at **99%** because
this is a narrow source and evidence closure in an already reconstructed
subsystem.
