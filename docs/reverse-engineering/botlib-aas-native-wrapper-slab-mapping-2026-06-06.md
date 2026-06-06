# Botlib AAS Native Wrapper Slab Mapping - 2026-06-06

## Scope

This pass closes the qagame native AAS import slab from
`G_QL_IMPORT_BOTLIB_AAS_BBOX_AREAS = 61` through
`G_QL_IMPORT_BOTLIB_AAS_PREDICT_CLIENT_MOVEMENT = 82`.

The reconstruction point is table order. Retail places `AAS_BBoxAreas` and
`AAS_AreaInfo` in native slots 61 and 62, then binds `AAS_EntityInfo` at slot
63 even though the tiny `EntityInfo` trampoline lives earlier in memory at
`0x004e1830`. The checked-in source should therefore preserve the retail native
slot order, not sort these wrappers by function address or legacy syscall enum
layout.

## Evidence

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part07.txt`
- `src/code/game/g_public.h`
- `src/code/game/g_syscalls.c`
- `src/code/server/sv_game.c`
- `src/code/server/ql_game_imports.inc`
- `tests/test_botlib_aas_native_wrapper_slab_parity.py`

## Findings

- Native slots 61 through 82 are now pinned against the retail import table,
  wrapper row sizes, source native enum values, legacy syscall remapping, the
  server native import initializer, and the legacy `ql_import_f` dispatch array.
- `AAS_Initialized` and `AAS_Time` appear in the HLIL table as raw code
  addresses `0x4e1840` and `0x4e1860`, not as ordinary Ghidra function rows.
  The parity gate intentionally checks their bytes and table entries instead of
  inventing promoted function-row aliases.
- The export offsets remain the retail AAS export layout:
  `EntityInfo` jumps through `+0x00`, `Initialized` through `+0x04`,
  `PresenceTypeBoundingBox` through `+0x08`, `Time` through `+0x0c`,
  `TraceAreas` through `+0x18`, `BBoxAreas` through `+0x1c`,
  and `PredictClientMovement` through `+0x54`.
- `QL_G_trap_AAS_Time` keeps the integer syscall return and float bit-cast
  source shape, while `QL_G_trap_AAS_PredictClientMovement` keeps
  `QL_G_PASSFLOAT(frametime)`.

## Coverage Result

`tests/test_botlib_aas_native_wrapper_slab_parity.py` prevents these
regressions:

- reordering AAS native imports by function address instead of retail table
  slot;
- treating raw thunks at `0x4e1840` and `0x4e1860` as normal promoted function
  rows;
- dropping the legacy syscall-to-native import map for route and movement AAS
  wrappers;
- losing the float marshaling details in `AAS_Time` or
  `AAS_PredictClientMovement`.

## Parity Estimate

- Focused AAS native wrapper slab mapping:
  **before 70% -> after 98%**
- Focused qagame botlib native import table coverage:
  **before 92% -> after 94%**
- Overall botlib plus qagame native import wiring:
  **before 92% -> after 93%**

No runtime launch was needed. The committed HLIL table, Ghidra rows, and source
wrapper shape settle this slice without executing the game.
