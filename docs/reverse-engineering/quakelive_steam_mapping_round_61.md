# Quake Live Steam Host Mapping Round 61

## Scope

This round pivots from the adjacent Quake Live-specific sound helpers into the
next strong retained Quake III source seam:

- the retained `server/sv_bot.c` bot-client, debug-polygon, and botlib import
  bridge
- the retained server ownership helpers called through that import table
- direct retained owner closures for `CM_EntityString`, `SV_inPVS`, and
  `SV_PointContents`

Primary evidence for this round:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `src/code/server/sv_bot.c`
- `src/code/server/sv_game.c`
- `src/code/server/sv_world.c`
- `src/code/qcommon/cm_load.c`
- `src/code/game/botlib.h`
- `assets/quake3/src/code/server/sv_bot.c`
- `assets/quake3/src/code/server/sv_game.c`
- `assets/quake3/src/code/server/sv_world.c`
- `assets/quake3/src/code/qcommon/cm_load.c`

## Retained `sv_bot.c` Client / Debug / Print Closures

The opening tranche matches the retained `sv_bot.c` ownership directly:

- `sub_4DCD30 -> SV_BotAllocateClient`
- `sub_4DCDB0 -> SV_BotFreeClient`
- `sub_4DCE10 -> BotDrawDebugPolygons`
- `sub_4DCF90 -> BotImport_Print`

Observed facts:

1. `sub_4DCD30` scans the client array for a free bot slot, marks the client
   active, sets the bot flags and default rate fields, and matches the
   retained `SV_BotAllocateClient` role exactly.
2. `sub_4DCDB0` preserves the retained fatal guard string
   `SV_BotFreeClient: bad clientNum: %i`, then clears the bot client state
   through the same slot-based path as Quake III.
3. `sub_4DCE10` uses the exact retained bot debug cvars
   `bot_debug`, `bot_reachability`, `bot_groundonly`, and
   `bot_highlightarea`, then walks the debug polygon pool and draw path like
   `BotDrawDebugPolygons`.
4. `sub_4DCF90` matches `BotImport_Print` one-for-one, including the retained
   print-type switch and the literal strings
   `unknown print type\n`, `^3Warning: %s`, `^1Error: %s`,
   `^1Fatal: %s`, and `^1Exit: %s`.

## Retained Botlib Import / Debug-Line Closures

The following block matches the retained botlib import bridge from
`server/sv_bot.c`:

- `sub_4DD0B0 -> BotImport_Trace`
- `sub_4DD160 -> BotImport_EntityTrace`
- `sub_4DD210 -> BotImport_PointContents`
- `sub_4DD230 -> BotImport_inPVS`
- `sub_4DD240 -> BotImport_BSPEntityData`
- `sub_4DD250 -> BotImport_BSPModelMinsMaxsOrigin`
- `sub_4DD350 -> BotImport_GetMemory`
- `sub_4DD370 -> BotImport_FreeMemory`
- `sub_4DD380 -> BotImport_HunkAlloc`
- `sub_4DD3B0 -> BotImport_DebugPolygonCreate`
- `sub_4DD430 -> BotImport_DebugPolygonDelete`
- `sub_4DD450 -> BotImport_DebugLineCreate`
- `sub_4DD480 -> BotImport_DebugLineShow`
- `sub_4DD640 -> BotClientCommand`
- `sub_4DD670 -> SV_BotFrame`
- `sub_4DD6A0 -> SV_BotLibSetup`
- `sub_4DD6D0 -> SV_BotLibShutdown`
- `sub_4DD6F0 -> SV_BotInitCvars`
- `sub_4DD940 -> SV_BotInitBotLib`
- `sub_4DDA50 -> SV_BotGetConsoleMessage`
- `sub_4DDAC0 -> SV_BotGetSnapshotEntity`

Observed facts:

1. `sub_4DD940` assembles the import table in the same field order as
   `botlib_import_t` in `botlib.h`, which anchors the names of the adjacent
   `BotImport_*` helpers with high confidence.
2. `sub_4DD380` preserves the retained fatal string
   `SV_Bot_HunkAlloc: Alloc with marks already set\n` and then allocates from
   the high hunk, matching `BotImport_HunkAlloc`.
3. `sub_4DD3B0`, `sub_4DD430`, `sub_4DD450`, and `sub_4DD480` preserve the
   retained debug polygon and debug line create/delete/show behavior,
   including the shared polygon-slot allocator used by the line helper.
4. `sub_4DD670` retains the `SV_BotFrame` role and call-site behavior even
   though the decompiler collapses its parameter list; the HLIL call sites
   still pass the bot frame time exactly like Quake III.
5. `sub_4DDA50` and `sub_4DDAC0` match the retained reliable-command console
   drain and snapshot-entity iteration helpers from `sv_bot.c`.

## Retained Server Ownership Closures

The import bridge also exposed direct retained owners outside the local
`sv_bot.c` body:

- `sub_4C0250 -> CM_EntityString`
- `sub_4C9220 -> Z_AvailableMemory`
- `sub_4E1230 -> SV_inPVS`
- `sub_4E6AC0 -> SV_PointContents`

Observed facts:

1. `sub_4C0250` is a direct getter over the collision-model entity-string
   global, matching the retained `CM_EntityString` helper in `cm_load.c`.
2. `sub_4C9220` computes `zone->size - zone->used`, matching the retained
   `Z_AvailableMemory` helper that `SV_BotInitBotLib` exports to botlib.
3. `sub_4E1230` matches `SV_inPVS` exactly: it resolves both points to leaves,
   compares clusters through the PVS, and then performs the same area-portal
   connectivity checks as the retained Quake III source.
4. `sub_4E6AC0` matches `SV_PointContents`: it queries world contents first,
   then iterates linked entities and merges transformed brush-model contents
   while respecting the passed entity skip number.

## Completion Summary

This round promotes `29` retained aliases:

- `sv_bot.c` client/debug/print seam: `SV_BotAllocateClient`,
  `SV_BotFreeClient`, `BotDrawDebugPolygons`, `BotImport_Print`
- botlib import bridge and snapshot helpers: `BotImport_Trace`,
  `BotImport_EntityTrace`, `BotImport_PointContents`, `BotImport_inPVS`,
  `BotImport_BSPEntityData`, `BotImport_BSPModelMinsMaxsOrigin`,
  `BotImport_GetMemory`, `BotImport_FreeMemory`, `BotImport_HunkAlloc`,
  `BotImport_DebugPolygonCreate`, `BotImport_DebugPolygonDelete`,
  `BotImport_DebugLineCreate`, `BotImport_DebugLineShow`,
  `BotClientCommand`, `SV_BotFrame`, `SV_BotLibSetup`,
  `SV_BotLibShutdown`, `SV_BotInitCvars`, `SV_BotInitBotLib`,
  `SV_BotGetConsoleMessage`, `SV_BotGetSnapshotEntity`
- retained owners: `CM_EntityString`, `Z_AvailableMemory`, `SV_inPVS`,
  `SV_PointContents`

Focused band results after this pass:

- botlib/client seam `0x4DCD30-0x4DD0B0`: `3 -> 0`
- retained botlib import core `0x4DD0B0-0x4DDAE0`: `18 -> 0`
- broad retained botlib/server tranche `0x4DCD30-0x4DDAE0`: `21 -> 0`
- isolated retained owner `0x4E1230`: `1 -> 0`
- isolated retained owner `0x4E6AC0`: `1 -> 0`

Extra HLIL-only promotions not present as standalone `functions.csv` starts:

- `0x004C9220 -> Z_AvailableMemory`
- `0x004DCD30 -> SV_BotAllocateClient`
- `0x004DD240 -> BotImport_BSPEntityData`
- `0x004DD6A0 -> SV_BotLibSetup`
- `0x004DD6D0 -> SV_BotLibShutdown`

Global `quakelive_steam.exe` coverage after this pass:

- raw alias entries: `799 -> 828`
- address-backed aliases: `798 -> 827`
- Ghidra function coverage: `14.581% -> 15.111%` of `5473`

This round fully closes the retained `sv_bot.c` seam exposed by the current
HLIL and Ghidra corpus. The next nearby unresolved starts are no longer in the
botlib bridge itself; they sit in later server/Steam-facing helpers beyond the
closed `0x4DCD30-0x4DDAE0` tranche.
