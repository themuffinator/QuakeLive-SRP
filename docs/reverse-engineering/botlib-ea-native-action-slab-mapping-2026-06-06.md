# Botlib EA Native Action Slab Mapping - 2026-06-06

## Scope

This pass closes the qagame native elementary-action import slab from
`G_QL_IMPORT_BOTLIB_EA_SAY = 85` through
`G_QL_IMPORT_BOTLIB_EA_RESET_INPUT = 109`.

The important reconstruction point is `G_QL_IMPORT_BOTLIB_EA_WALK = 89`.
Retail exposes it as a native-only import between `EA_Action` and `EA_Gesture`,
but the legacy `BOTLIB_EA_*` syscall enum deliberately has no
`BOTLIB_EA_WALK` entry. The correct source shape is therefore to keep
`trap_EA_Walk` absent from qagame syscall wrappers while preserving the server
native import slot that calls `botlib_export->ea.EA_Walk`.

## Evidence

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part07.txt`
- `src/code/game/g_public.h`
- `src/code/game/g_syscalls.c`
- `src/code/game/g_local.h`
- `src/code/game/botlib.h`
- `src/code/botlib/be_ea.c`
- `src/code/botlib/be_interface.c`
- `src/code/server/sv_game.c`
- `src/code/server/ql_game_imports.inc`
- `tests/test_botlib_ea_native_action_slab_parity.py`

## Findings

- Native slots 85 through 109 are now pinned against Ghidra row sizes, HLIL
  table entries, source enum slots, server import bindings, and wrapper bodies.
- `EA_Walk` remains native-only:
  - `G_QL_IMPORT_BOTLIB_EA_WALK = 89` exists in the native enum.
  - `SV_InitGameImports` binds it to `QL_G_trap_EA_Walk`.
  - `QL_G_trap_EA_Walk` calls `botlib_export->ea.EA_Walk( client )`.
  - There is no `BOTLIB_EA_WALK` legacy enum member.
  - There is no `trap_EA_Walk` in `g_syscalls.c` or `g_local.h`.
- The EA native slot order differs from the `ea_export_t` struct order in a few
  places. The test pins the observed export offsets, including `EA_Command`
  jumping to `+0x58`, `EA_Say` to `+0x5c`, `EA_Walk` to `+0x68`, and
  `EA_Crouch` to `+0x98`.

## Coverage Result

`tests/test_botlib_ea_native_action_slab_parity.py` now prevents three common
regressions:

- adding a fake legacy `BOTLIB_EA_WALK` syscall;
- removing the direct native `G_QL_IMPORT_BOTLIB_EA_WALK` slot;
- reordering the EA slab by name instead of by the retail native table.

## Parity Estimate

- Focused EA native action slab mapping:
  **before 78% -> after 99%**
- Focused native-only botlib import classification:
  **before 84% -> after 96%**
- Overall botlib plus qagame native import wiring:
  **before 91% -> after 92%**

No runtime launch was needed. The committed HLIL table and source wrapper shape
settle this slice cleanly.
