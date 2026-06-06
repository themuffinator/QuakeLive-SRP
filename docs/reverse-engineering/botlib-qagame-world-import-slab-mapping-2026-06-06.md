# Botlib Qagame World Import Slab Mapping - 2026-06-06

## Scope

This pass closes the botlib-adjacent qagame world import slab immediately before
the bot client and botlib native imports. The covered native table range is
slots 31 through 42, followed by the already mapped bot allocation slot 43:

- brush model, trace, capsule trace, point contents;
- PVS and PVS-ignore-portals;
- area portal state and area connectivity;
- link, unlink, entities-in-box, and non-capsule entity contact.

These imports are not botlib algorithms themselves, but they are the world and
visibility plumbing that qagame and bot-facing code use immediately before the
botlib table starts.

## Evidence

- `references/analysis/quakelive_symbol_aliases.json`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part07.txt`
- `src/code/game/g_public.h`
- `src/code/game/g_syscalls.c`
- `src/code/server/sv_game.c`
- `src/code/server/ql_game_imports.inc`
- `tests/test_botlib_qagame_world_import_slab_parity.py`

## Source Reconstruction

- Added `G_QL_IMPORT_IN_PVS_IGNORE_PORTALS = 36`.
- Added `G_QL_IMPORT_AREAS_CONNECTED = 38`.
- Corrected the native order to `G_QL_IMPORT_LINKENTITY = 39` and
  `G_QL_IMPORT_UNLINK_ENTITY = 40`.
- Added `G_QL_IMPORT_ENTITY_CONTACT = 42`.
- Routed `G_IN_PVS_IGNORE_PORTALS`, `G_AREAS_CONNECTED`, and
  `G_ENTITY_CONTACT` through direct native imports instead of falling back to
  the compatibility table.
- Updated `SV_InitGameImports` to bind the recovered slots to the existing
  qagame import wrappers.

## Retail Shape Notes

- Retail slot 35 points at the existing `BotImport_inPVS` helper rather than a
  separate generated `QL_G_trap_InPVS` wrapper. The current source still routes
  slot 35 through `QL_G_trap_InPVS`, which has the same public syscall
  contract. This pass leaves that function-pointer identity difference
  documented rather than changing it without broader ABI impact review.
- Slot 42 is the non-capsule `EntityContact` helper. `EntityContactCapsule`
  remains covered by the legacy compatibility import table and does not have a
  direct slot in this native slab.
- The retail native table at `0x0056CFFC..0x0056D02C` now matches the source
  enum and server initializer for slots 31 through 43, including the corrected
  link/unlink order.

## Coverage Result

`tests/test_botlib_qagame_world_import_slab_parity.py` pins promoted aliases,
Ghidra row sizes, HLIL wrapper shapes, native table order, qagame syscall
remapping, and `SV_InitGameImports` assignments for the full world/import slab.

## Parity Estimate

- Focused qagame world/import slab native slot parity:
  **before 76% -> after 98%**
- Focused botlib-adjacent qagame import environment coverage:
  **before 90% -> after 91%**
- Overall botlib plus related server/game wiring:
  **before 90% -> after 91%**

The repo-wide parity estimate remains effectively **99%** because this is a
narrow native import-table correction inside an already high-parity subsystem.
