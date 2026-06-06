# Botlib Cgame Native Import Slab Mapping - 2026-06-06

## Scope

This pass widens the botlib-adjacent boundary work across the dense native
cgame import slab at `0x004AF820..0x004B0500`. Earlier rounds had documented
the individual import wrappers, and the prior shutdown-boundary pass separated
`CL_ShutdownCGame` from the import table. The remaining gap was direct
`test_botlib_*.py` coverage for most promoted aliases in this related wiring
range.

No C source body change or alias JSON change was needed. The work here pins
the reconstructed import names, row sizes where Ghidra has function rows, HLIL
wrapper shapes, and the source import-table initializer.

## Evidence

- `references/analysis/quakelive_symbol_aliases.json`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part07.txt`
- `src/code/client/cl_cgame.c`
- `src/code/cgame/cg_public.h`
- `tests/test_botlib_cgame_native_import_slab_parity.py`

## Pinned Surface

The new parity gate covers the full promoted alias set in
`0x004AF820..0x004B0500`, including:

- command and collision-model wrappers from `QLCGImport_AddCommand` through
  `QLCGImport_CM_MarkFragments`;
- sound and renderer wrappers through shader registration, scene submission,
  color/stretch-pic, lerp-tag, remap, and scaled-text paths;
- advertisement bridge callbacks for cell shaders, active advert, map path,
  view parameters, frame time, clear delay, and loading-view parameters;
- snapshot, server-command, current-command, usercmd, usercmd-value, and memory
  wrappers;
- key, parser, cinematic, entity-token, publish-tagged-info, mirror, mute, and
  avatar-image wrappers;
- adjacent lifecycle owners `CL_GetServerCommand`, `CL_ShutdownCGame`,
  `CL_LoadCGameForCvarRegistration`, and `CL_InitCGame`.

## Source Findings

- `cg_public.h` preserves the recovered native cgame import enum with
  `CG_QL_IMPORT_COUNT = 128`.
- `CL_InitCGameImports` zeroes the table, resets the cgame color cache, and
  assigns the reconstructed wrappers to the recovered retail slots.
- The aliases that do not have Ghidra rows in this range are bounded by HLIL
  table/body evidence rather than forced into row-backed assertions:
  `QLCGImport_AdvertisementBridge_UpdateLoadingViewParameters`,
  `QLCGImport_GetCurrentCmdNumber`, and `QLCGImport_MemoryRemaining`.
- Reserved native import rows remain assigned to
  `QL_CG_trap_RetailReservedImport`; this pass does not invent behavior for
  unresolved retail-only callback slots.

## Coverage Result

`tests/test_botlib_cgame_native_import_slab_parity.py` now includes a final
scan over the promoted aliases in `0x004AF820..0x004B0500`. After this pass
there are no promoted names in that botlib-adjacent native cgame slab without a
direct `test_botlib_*.py` mention.

## Parity Estimate

- Focused native cgame import-slab alias coverage:
  **before 45% -> after 100%**
- Focused import-table source initializer coverage:
  **before 78% -> after 97%**
- Focused botlib plus cgame-boundary related wiring:
  **before 88% -> after 89%**

The overall increase is small because this pass closes evidence coverage for
already-reconstructed wrapper names and table wiring rather than changing
runtime behavior.
