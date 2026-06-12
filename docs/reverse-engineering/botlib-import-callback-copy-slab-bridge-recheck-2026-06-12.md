# Botlib Import Callback Copy-Slab Bridge Recheck - 2026-06-12

## Scope

This round rechecked the host-to-botlib import callback ABI. The key retail
boundary is the callback slab that `SV_BotInitBotLib` builds before calling
`GetBotLibAPI`, and the `0x58` byte copy that `GetBotLibAPI` performs into the
botlib-owned import table.

Primary reconstructed files:

- `src/code/game/botlib.h`
- `src/code/server/sv_bot.c`
- `src/code/botlib/be_interface.c`
- `tests/test_botlib_import_callback_surface_parity.py`

Primary evidence:

- Binary Ninja HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part03.txt`
- Binary Ninja HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
- Ghidra functions table:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- Promoted aliases:
  `references/analysis/quakelive_symbol_aliases.json`

## Observed Retail Facts

- Retail `sub_4DD940` builds a contiguous stack callback slab from `var_5c`
  through `var_8`, then calls `sub_4A83C0(2, &var_5c)`.
- Retail `sub_4A83C0` copies `0x58` bytes from that caller slab into
  `data_16dd800`, which is exactly twenty-two 32-bit callback slots.
- The stack slab order is:
  print, trace, entity trace, point contents, PVS, BSP entity data, BSP model
  bounds, bot client command, zone allocation/free/available memory, hunk
  allocation, file open/read/write/close/seek, debug line create/delete/show,
  debug polygon create/delete.
- Retail uses the same debug-polygon delete helper for both debug-line delete
  and debug-polygon delete slots.

## Reconstruction Decision

The reconstructed source already matches the retail ABI:

- `botlib_import_t` exposes twenty-two callback fields in the retail order.
- `SV_BotInitBotLib` assigns every field before calling
  `GetBotLibAPI( BOTLIB_API_VERSION, &botlib_import )`.
- `GetBotLibAPI` copies the source callback slab with `botimport = *import`
  and asserts that the print callback is present before filling the export
  table.
- `DebugLineDelete` intentionally maps to `BotImport_DebugPolygonDelete`,
  matching the retail shared-delete slot.

No source-code reconstruction was needed. The closure was a stricter parity
gate: `test_botlib_import_callback_copy_slab_matches_retail_getapi_abi`.

## Confidence And Open Questions

- Focused botlib import callback ABI confidence:
  **before 94% -> after 99%**.
- Focused server-to-botlib initialization wiring confidence:
  **before 98% -> after 99%**.
- Overall botlib plus qagame/server wiring reconstruction parity:
  **83.90% -> 83.93%**.

Remaining uncertainty is outside this static ABI surface: runtime map-specific
AAS behavior and live bot decision quality still depend on broader subsystem
validation, but the host callback slab itself is now pinned by source, HLIL,
Ghidra, and alias evidence.
