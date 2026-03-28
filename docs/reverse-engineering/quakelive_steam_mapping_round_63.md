# Quake Live Steam Host Mapping Round 63

## Scope

This round closes the next retained Quake III server/game bridge tranche after
round 62 and carries that evidence into the adjacent startup/configstring
owners:

- the retained `server/sv_game.c` game-bridge helpers after `SV_inPVS`
- the generated `server/ql_game_imports.inc` wrappers that tailcall those
  retained owners inside the host
- the retained `server/sv_game.c` VM bootstrap owners and the retained
  `server/sv_init.c` configstring, userinfo, baseline, and startup helpers
  reached by the same bridge

Primary evidence for this round:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `src/code/server/sv_game.c`
- `src/code/server/sv_init.c`
- `src/code/server/ql_game_imports.inc`
- `assets/quake3/src/code/server/sv_game.c`
- `assets/quake3/src/code/server/sv_init.c`

## Retained `sv_game.c` Bridge Closures

The next retained `sv_game.c` owners line up directly with the Quake III
source and the surrounding strings/calls in HLIL:

- `sub_4E1330 -> SV_LocateGameData`
- `sub_4E1360 -> SV_GameDropClient`
- `sub_4E1390 -> SV_GameSendServerCommand`
- `sub_4E1430 -> SV_GetServerinfo`
- `sub_4E1500 -> SV_AdjustAreaPortalState`
- `sub_4E15A0 -> SV_EntityContact`
- `sub_4E1630 -> SV_GetUsercmd`

Observed facts:

1. `sub_4E1330` stores the exact `sv.gentities`, `sv.num_entities`,
   `sv.gentitySize`, `sv.gameClients`, and `sv.gameClientSize` state expected
   from retained `SV_LocateGameData`.
2. `sub_4E1360` validates `clientNum` against `sv_maxclients` and then
   tailcalls the already-mapped `SV_DropClient`, matching retained
   `SV_GameDropClient`.
3. `sub_4E1390` preserves the retained broadcast/single-client split from
   `SV_GameSendServerCommand`, including the `clientNum == -1` special case.
4. `sub_4E1430` retains the fatal string
   `SV_GetServerinfo: bufferSize == %i` and copies the server info string into
   the caller buffer exactly where Quake III expects it.
5. `sub_4E1500` still begins by validating the incoming `gEnt` through the
   retained `SV_SvEntityForGentity` guard and then forwards the resolved area
   pair into the CM area-portal state setter, which matches
   `SV_AdjustAreaPortalState`.
6. `sub_4E15A0` is the retained `SV_EntityContact` owner because it constructs
   the CM box trace against the entity clip handle returned from the shared
   entity and passes the `capsule = qfalse` variant expected by the stock
   source.
7. `sub_4E1630` preserves the exact fatal guard
   `SV_GetUsercmd: bad clientNum:%i` and copies the client's last usercmd into
   the output buffer.

## Generated `QL_G_trap_*` Wrapper Closures

The small wrappers around that same region are the generated native-import
helpers from `ql_game_imports.inc`:

- `sub_4E13E0 -> QL_G_trap_SetConfigstring`
- `sub_4E13F0 -> QL_G_trap_GetConfigstring`
- `sub_4E1410 -> QL_G_trap_GetUserinfo`
- `sub_4E1420 -> QL_G_trap_SetUserinfo`
- `sub_4E1470 -> QL_G_trap_SetBrushModel`
- `sub_4E1480 -> QL_G_trap_Trace`
- `sub_4E14B0 -> QL_G_trap_TraceCapsule`
- `sub_4E14E0 -> QL_G_trap_PointContents`
- `sub_4E14F0 -> QL_G_trap_InPVSIgnorePortals`
- `sub_4E1560 -> QL_G_trap_AreasConnected`
- `sub_4E1570 -> QL_G_trap_LinkEntity`
- `sub_4E1580 -> QL_G_trap_UnlinkEntity`
- `sub_4E1590 -> QL_G_trap_EntitiesInBox`
- `sub_4E1610 -> QL_G_trap_BotAllocateClient`
- `sub_4E1620 -> QL_G_trap_BotFreeClient`
- `sub_4E16C0 -> QL_G_trap_DebugPolygonCreate`
- `sub_4E16D0 -> QL_G_trap_DebugPolygonDelete`

Observed facts:

1. `sub_4E13E0`, `sub_4E13F0`, `sub_4E1410`, `sub_4E1420`, `sub_4E1470`,
   `sub_4E14E0`, `sub_4E14F0`, `sub_4E1570`, `sub_4E1580`, and `sub_4E1590`
   are all one-hop tailcalls into the already-identified host owners, exactly
   as the generated `QL_G_trap_*` wrappers are written in source.
2. `sub_4E1480` and `sub_4E14B0` both tailcall the shared retained trace owner
   with only the final `capsule` flag differing (`qfalse` vs `qtrue`), which
   matches `QL_G_trap_Trace` and `QL_G_trap_TraceCapsule`.
3. `sub_4E1560` is the generated `QL_G_trap_AreasConnected` wrapper because it
   is a direct tailcall into the CM area-connectivity owner.
4. `sub_4E1610` is HLIL-only in the committed `functions.csv` export, but the
   body is a pure tailcall into the already-mapped `SV_BotAllocateClient`,
   which matches `QL_G_trap_BotAllocateClient` in the generated import table.
5. `sub_4E1620`, `sub_4E16C0`, and `sub_4E16D0` tailcall the already-mapped
   retained bot/debug owners in the exact order emitted by
   `ql_game_imports.inc`.

## Retained VM Bootstrap / `sv_init.c` Closures

The bridge then lands in the retained VM bootstrap and server-init core:

- `sub_4E2B90 -> SV_RestartGameProgs`
- `sub_4E2C10 -> SV_InitGameProgs`
- `sub_4E2CC0 -> SV_SetConfigstring`
- `sub_4E2EC0 -> SV_GetConfigstring`
- `sub_4E30D0 -> SV_SetUserinfo`
- `sub_4E3150 -> SV_GetUserinfo`
- `sub_4E31B0 -> SV_CreateBaseline`
- `sub_4E3210 -> SV_Startup`
- `sub_4E3300 -> SV_ChangeMaxClients`

Observed facts:

1. `sub_4E2B90` preserves the retained `VM_Restart on game failed` fatal path
   and the restart-only `GAME_SHUTDOWN` / `VM_Restart` sequence from
   `server/sv_game.c` `SV_RestartGameProgs`.
2. `sub_4E2C10` preserves the retained `bot_enable` bootstrap,
   `VM_Create on game failed` fatal, and final `SV_InitGameVM( qfalse )` call
   from `server/sv_game.c` `SV_InitGameProgs`, with Quake Live's native-module
   path folded around the same owner.
3. `sub_4E2CC0` and `sub_4E2EC0` preserve the retained configstring fatal
   strings and the expected chunked `cs` / `bcs0` / `bcs1` / `bcs2` broadcast
   behavior from `server/sv_init.c`.
4. `sub_4E30D0` and `sub_4E3150` preserve the retained userinfo guards
   `SV_SetUserinfo: bad index %i\n`,
   `SV_GetUserinfo: bufferSize == %i`, and
   `SV_GetUserinfo: bad index %i\n` from `server/sv_init.c`.
5. `sub_4E31B0` is the retained `SV_CreateBaseline` owner because it iterates
   the linked entities, writes `s.number`, and copies each entityState into the
   `sv.svEntities[].baseline` slab.
6. `sub_4E3210` and `sub_4E3300` preserve the retained `sv_maxclients`
   allocation/reallocation logic from `SV_Startup` and `SV_ChangeMaxClients`,
   including the `SV_Startup: svs.initialized` fatal from `server/sv_init.c`.

## Completion Summary

This round promotes `33` aliases:

- retained `sv_game.c` owners: `SV_LocateGameData`, `SV_GameDropClient`,
  `SV_GameSendServerCommand`, `SV_GetServerinfo`,
  `SV_AdjustAreaPortalState`, `SV_EntityContact`, `SV_GetUsercmd`
- generated wrappers: `QL_G_trap_SetConfigstring`,
  `QL_G_trap_GetConfigstring`, `QL_G_trap_GetUserinfo`,
  `QL_G_trap_SetUserinfo`, `QL_G_trap_SetBrushModel`, `QL_G_trap_Trace`,
  `QL_G_trap_TraceCapsule`, `QL_G_trap_PointContents`,
  `QL_G_trap_InPVSIgnorePortals`, `QL_G_trap_AreasConnected`,
  `QL_G_trap_LinkEntity`, `QL_G_trap_UnlinkEntity`,
  `QL_G_trap_EntitiesInBox`, `QL_G_trap_BotAllocateClient`,
  `QL_G_trap_BotFreeClient`, `QL_G_trap_DebugPolygonCreate`,
  `QL_G_trap_DebugPolygonDelete`
- retained VM/bootstrap + `sv_init.c` owners: `SV_RestartGameProgs`,
  `SV_InitGameProgs`, `SV_SetConfigstring`, `SV_GetConfigstring`,
  `SV_SetUserinfo`, `SV_GetUserinfo`, `SV_CreateBaseline`, `SV_Startup`,
  `SV_ChangeMaxClients`

Focused band results after this pass:

- retained `sv_game` bridge + native-wrapper band `0x4E1330-0x4E16D0`:
  `25 -> 2` remaining standalone gaps
- retained VM/bootstrap + `sv_init` band `0x4E2B90-0x4E3300`:
  `11 -> 2`
- combined focused slices: `36 -> 4`

Extra HLIL-only promotion not present as a standalone `functions.csv` start:

- `0x004E1610 -> QL_G_trap_BotAllocateClient`

Global `quakelive_steam.exe` coverage after this pass:

- raw alias entries: `861 -> 894`
- address-backed aliases: `860 -> 893`
- Ghidra function coverage: `15.714% -> 16.316%` of `5473`

The remaining standalone gaps in these focused retained slices are:

- `0x004E1400`
- `0x004E1680`
- `0x004E2CA0`
- `0x004E2F30`

`0x004E1400` and `0x004E2F30` sit in the Quake Live configstring rebroadcast
glue around the retained Quake III owners. `0x004E1680` and `0x004E2CA0` look
like Quake Live-specific Steam/VM helper glue adjacent to the retained
ownership closed here rather than additional stock Quake III owners.
