# Botlib Import Wrapper Body Recheck - 2026-06-12

## Scope

This round rechecked the server-owned botlib import callback wrapper bodies
after the import callback slab itself had already been pinned. The goal was to
tie the reconstructed `sv_bot.c` wrappers to the retail Binary Ninja HLIL body
shapes, including helpers that retail inlined rather than preserving as
standalone functions.

Primary reconstructed files:

- `src/code/server/sv_bot.c`
- `tests/test_botlib_import_callback_surface_parity.py`

Primary Binary Ninja evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`

Companion evidence:

- `references/analysis/quakelive_symbol_aliases.json`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`

## Observed Retail Facts

- Retail `BotImport_Print` (`sub_4DCF90`) formats through `vsprintf`, dispatches
  message/warning/error/fatal/exit print types, and preserves the default
  `"unknown print type\n"` path.
- Retail `BotImport_Trace` (`sub_4DD0B0`) and `BotImport_EntityTrace`
  (`sub_4DD160`) call the server trace and entity clip helpers with the final
  capsule flag set to `0`, then copy the trace result into the botlib BSP trace
  layout and zero the Quake III botlib-only residual fields.
- Retail simple pass-through wrappers match the reconstructed source:
  `PointContents` calls `sub_4E6AC0(point, -1)`, `inPVS` tailcalls
  `sub_4E1230`, and `BSPEntityData` tailcalls `sub_4C0250`.
- Retail `BotImport_BSPModelMinsMaxsOrigin` (`sub_4DD250`) gets inline-model
  bounds, expands rotated models through the radius helper, conditionally copies
  mins/maxs, and clears origin when provided.
- Retail memory wrappers match the source contracts: zone allocation uses tag
  `2`, free tailcalls the zone free helper, and hunk allocation errors when a
  hunk mark is active before allocating from hunk preference `0`.
- Retail debug polygon create/delete use the debug polygon array pointer and
  `0x60c` stride, reserve index `0`, copy `numPoints * 0xc` bytes, and share
  the delete function for both polygon and debug-line delete slots.
- Retail has no function entry or promoted alias for a standalone
  `BotImport_DebugPolygonShow` at `0x4DD400`. The source helper's behavior is
  inlined into `BotImport_DebugLineShow` (`sub_4DD480`), which writes the
  polygon slot directly after building the four-point line quad.
- Retail `BotClientCommand` (`sub_4DD640`) dispatches through
  `SV_ExecuteClientCommand` with the final trusted flag set to `1`, matching
  the reconstructed `qtrue` source call.

## Reconstruction Decision

No source-code change was needed. The existing reconstruction already matches
the retail wrapper behavior, including the source-level `BotImport_DebugPolygonShow`
helper that retail folds into `BotImport_DebugLineShow` under optimization.

The closure was a stricter Binary Ninja-backed parity gate:
`test_botlib_import_callback_wrapper_hlil_bodies_match_source_contracts`.
The source-body gate was also expanded to cover `BotImport_Print`,
`BotImport_DebugPolygonShow`, `BotImport_DebugPolygonDelete`, and
`BotClientCommand`.

## Confidence And Open Questions

- Focused botlib import wrapper body confidence:
  **before 88% -> after 99%**.
- Focused host import callback source-to-HLIL mapping confidence:
  **before 96% -> after 99%**.
- Overall botlib plus qagame/server wiring reconstruction parity:
  **84.06% -> 84.09%**.

Remaining uncertainty is outside these host callback wrappers: deeper botlib
decision behavior, map-specific AAS behavior, and runtime bot quality still
need broader validation rounds.
