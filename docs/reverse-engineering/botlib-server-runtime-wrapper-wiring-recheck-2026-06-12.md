# Botlib Server Runtime Wrapper Wiring Recheck - 2026-06-12

## Scope

This round rechecked the runtime botlib bridge between qagame bot AI calls and
the server-owned botlib helpers. It follows the import-wrapper body round by
pinning the higher-level host helpers that set up botlib, drain reliable
commands for bot AI, expose snapshot entity iteration, and route native qagame
botlib wrappers through the retail export table.

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

- Retail `SV_BotLibSetup` (`sub_4DD6A0`) returns `0` when `bot_enable` is
  disabled, jumps through botlib export offset `0x1f0` when initialized, and
  otherwise prints the retained setup-without-init error before returning `-1`.
- Retail `SV_BotLibShutdown` (`sub_4DD6D0`) jumps through botlib export offset
  `0x1f4` when the export table exists and returns `-1` otherwise.
- Retail `SV_BotGetConsoleMessage` (`sub_4DDA50`) updates the client
  `lastPacketTime`, compares reliable acknowledge/sequence fields, advances the
  acknowledge cursor, uses the `0x3f` command ring mask, copies from the
  reliable command text slab, and returns `1` only when a command is delivered.
- Retail `SV_BotGetSnapshotEntity` (`sub_4DDAC0`) selects the current outgoing
  snapshot frame from the `0x1f` frame mask, rejects out-of-range sequence
  values with `-1`, and resolves snapshot entity numbers through the global
  snapshot entity ring.
- Retail native qagame wrappers preserve the setup/shutdown tailcalls to
  `sub_4DD6A0` and `sub_4DD6D0`, jump through botlib export offsets for
  libvars/map/update/test calls, tailcall the server snapshot/message helpers,
  and route bot user commands through the retained client-think helper.

## Reconstruction Decision

No source-code change was needed. The reconstructed server and qagame wrapper
surfaces already match the retail HLIL body contracts.

The closure was a stricter parity gate:
`test_server_and_native_qagame_botlib_runtime_wrapper_hlil_bodies_match_retail_refs`.
The native import-slot gate was also expanded to cover the source wrappers in
`ql_game_imports.inc`, the qagame-side `trap_BotLib*` syscall shims, and the
legacy `SV_GameSystemCallsImpl` cases for botlib runtime calls.

## Confidence And Open Questions

- Focused server botlib runtime helper confidence:
  **before 91% -> after 99%**.
- Focused native qagame botlib runtime wrapper confidence:
  **before 92% -> after 99%**.
- Overall botlib plus qagame/server wiring reconstruction parity:
  **84.09% -> 84.12%**.

Remaining uncertainty sits beyond this static wiring surface: map-specific AAS
behavior, bot decision quality, and live qagame/botlib interaction still need
broader runtime or corpus-backed validation.
