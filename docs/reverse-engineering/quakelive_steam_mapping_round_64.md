# Quake Live Steam Host Mapping Round 64

## Scope

This round closes the next retained Quake III server/bootstrap tranche after
round 63:

- the retained `server/sv_game.c` entity-token and VM lifecycle helpers
- the generated botlib/game-import wrappers immediately after that seam
- the retained `server/sv_init.c` clear/spawn/init/shutdown owners
- the shared `PC_AddGlobalDefine` thunk that Quake Live reuses across multiple
  native VM import tables

Primary evidence for this round:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `src/code/server/sv_game.c`
- `src/code/server/sv_init.c`
- `src/code/server/ql_game_imports.inc`
- `assets/quake3/src/code/server/sv_game.c`
- `assets/quake3/src/code/server/sv_init.c`

## Retained `sv_game.c` VM / Token Closures

The next retained `sv_game.c` owners line up directly with the Quake III source
and the surrounding HLIL behavior:

- `sub_4E1680 -> SV_GetEntityToken`
- `sub_4E2A40 -> SV_ShutdownGameProgs`
- `sub_4E2A80 -> SV_InitGameVM`
- `sub_4E2CA0 -> SV_GameCommand`

Observed facts:

1. `sub_4E1680` calls the already-mapped retained `COM_Parse`, copies the
   parsed token with `Q_strncpyz`, and returns `qfalse` only when both the
   parse pointer and token are empty, which matches retained
   `SV_GetEntityToken`.
2. `sub_4E2A40` checks the active game VM handle, calls `GAME_SHUTDOWN`,
   destroys the VM, and clears the retained VM globals exactly where
   `SV_ShutdownGameProgs` does in Quake III.
3. `sub_4E2A80` still resolves the entity-string owner through
   `CM_EntityString`, clears client/entity bridge state, and then calls into
   the game VM init path. Quake Live folds extra `.ent` handling around the
   same retained `SV_InitGameVM` owner rather than replacing it.
4. `sub_4E2CA0` preserves the retained `sv.state == SS_GAME` gate and only
   dispatches `GAME_CONSOLE_COMMAND` when the server is live, which matches
   retained `SV_GameCommand`.

## Generated Botlib Wrapper Closures

The adjacent wrapper slab is the generated botlib seam from
`server/ql_game_imports.inc`:

- `sub_4E16E0 -> QL_G_trap_BotLibSetup`
- `sub_4E16F0 -> QL_G_trap_BotLibShutdown`
- `sub_4E1700 -> QL_G_trap_BotLibVarSet`
- `sub_4E1720 -> QL_G_trap_BotLibVarGet`
- `sub_4E1760 -> QL_G_trap_BotLibStartFrame`
- `sub_4E1780 -> QL_G_trap_BotLibLoadMap`
- `sub_4E17A0 -> QL_G_trap_BotLibUpdateEntity`
- `sub_4E17C0 -> QL_G_trap_BotLibTest`
- `sub_4E17E0 -> QL_G_trap_BotGetSnapshotEntity`
- `sub_4E17F0 -> QL_G_trap_BotGetServerCommand`
- `sub_4E1800 -> QL_G_trap_BotUserCommand`

Observed facts:

1. `sub_4E16E0` and `sub_4E16F0` are pure tailcalls into the already-closed
   retained owners `SV_BotLibSetup` and `SV_BotLibShutdown`, exactly matching
   the generated wrappers in `ql_game_imports.inc`.
2. `sub_4E1700`, `sub_4E1720`, `sub_4E1760`, `sub_4E1780`, `sub_4E17A0`, and
   `sub_4E17C0` are one-hop jumps through the import table offsets emitted in
   the same order as `BOTLIB_LIBVAR_SET`, `BOTLIB_LIBVAR_GET`,
   `BOTLIB_START_FRAME`, `BOTLIB_LOAD_MAP`, `BOTLIB_UPDATENTITY`, and
   `BOTLIB_TEST`.
3. `sub_4E17E0` and `sub_4E17F0` tailcall the already-mapped retained owners
   `SV_BotGetSnapshotEntity` and `SV_BotGetConsoleMessage`, matching the
   generated `BOTLIB_GET_SNAPSHOT_ENTITY` and `BOTLIB_GET_CONSOLE_MESSAGE`
   wrappers.
4. `sub_4E1800` forwards `(clientNum, usercmd_t*)` into the already-mapped
   retained `SV_ClientThink` owner, which matches `BOTLIB_USER_COMMAND`.
5. The pre-existing `sub_4E1740` alias was too narrow as
   `QLUIImport_PC_AddGlobalDefine`. Part 07 shows the same thunk exported in
   the cgame, UI, and qagame native import tables (`data_565B04`,
   `data_567498`, and `data_56D054`), so this round corrects it to the shared
   `PC_AddGlobalDefine` thunk name.

## Retained `sv_init.c` Init / Shutdown Closures

The next retained `sv_init.c` owners also close cleanly:

- `sub_4E34D0 -> SV_ClearServer`
- `sub_4E3510 -> SV_SpawnServer`
- `sub_4E3AD0 -> SV_Init`
- `sub_4E3ED0 -> SV_FinalMessage`
- `sub_4E3F60 -> SV_Shutdown`

Observed facts:

1. `sub_4E34D0` frees every live configstring entry and then clears the server
   state block, which is the retained `SV_ClearServer` behavior.
2. `sub_4E3510` retains the canonical startup strings
   `------ Server Initialization ------` and `Server: %s`, then follows the
   stock spawn sequence through clear, startup, game-prog init, baseline
   creation, and final heartbeat paths. That is retained `SV_SpawnServer`.
3. `sub_4E3AD0` still registers the operator commands, initializes server
   cvars, and then chains into the already-mapped botlib setup owners, which is
   the retained `SV_Init` path.
4. `sub_4E3ED0` iterates the client list twice to send the final print and
   `disconnect` commands before forcing snapshot transmission, which matches
   retained `SV_FinalMessage`.
5. `sub_4E3F60` preserves the shutdown banner, optionally calls
   `SV_FinalMessage`, tears down the game VM, clears the server, frees client
   state, drops `sv_running`, and prints the retained trailer line. That is
   retained `SV_Shutdown`.

## Completion Summary

This round promotes `20` new aliases and corrects `1` existing alias:

- retained `sv_game.c` owners: `SV_GetEntityToken`, `SV_ShutdownGameProgs`,
  `SV_InitGameVM`, `SV_GameCommand`
- generated botlib wrappers: `QL_G_trap_BotLibSetup`,
  `QL_G_trap_BotLibShutdown`, `QL_G_trap_BotLibVarSet`,
  `QL_G_trap_BotLibVarGet`, `QL_G_trap_BotLibStartFrame`,
  `QL_G_trap_BotLibLoadMap`, `QL_G_trap_BotLibUpdateEntity`,
  `QL_G_trap_BotLibTest`, `QL_G_trap_BotGetSnapshotEntity`,
  `QL_G_trap_BotGetServerCommand`, `QL_G_trap_BotUserCommand`
- corrected shared thunk: `sub_4E1740` from `QLUIImport_PC_AddGlobalDefine` to
  `PC_AddGlobalDefine`
- retained `sv_init.c` owners: `SV_ClearServer`, `SV_SpawnServer`, `SV_Init`,
  `SV_FinalMessage`, `SV_Shutdown`

Focused band results after this pass:

- botlib / token wrapper band `0x4E1680-0x4E1800`: `10 -> 0` remaining
  standalone gaps
- retained VM/bootstrap + `sv_init` band `0x4E2A40-0x4E3F60`: `9 -> 1`
- combined focused slices: `19 -> 1`

Extra HLIL-only promotions not present as standalone `functions.csv` starts:

- `0x004E16E0 -> QL_G_trap_BotLibSetup`
- `0x004E16F0 -> QL_G_trap_BotLibShutdown`

Global `quakelive_steam.exe` coverage after this pass:

- raw alias entries: `894 -> 914`
- address-backed aliases: `893 -> 913`
- Ghidra function coverage: `16.316% -> 16.682%` of `5473`

The remaining standalone gap in these focused retained slices is:

- `0x004E2F30`

`0x004E2F30` sits in the Quake Live configstring rebroadcast glue around the
retained Quake III `SV_SetConfigstring` owner rather than in the stock Quake III
init/shutdown owners closed here.
