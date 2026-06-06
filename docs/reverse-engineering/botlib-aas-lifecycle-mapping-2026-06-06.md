# Botlib AAS Lifecycle Mapping - 2026-06-06

## Scope

This pass maps the botlib AAS lifecycle layer that sits below the previously
mapped sample/query, route, reachability, and movement corridors:

- `src/code/botlib/be_aas_bspq3.c`
- `src/code/botlib/be_aas_cluster.c`
- `src/code/botlib/be_aas_entity.c`
- `src/code/botlib/be_aas_file.c`
- `src/code/botlib/be_aas_main.c`
- `src/code/botlib/be_interface.c`
- `src/code/game/botlib.h`
- `src/code/game/g_syscalls.c`
- `src/code/server/sv_game.c`
- `src/code/server/ql_game_imports.inc`

The owning retail binary is `quakelive_steam.exe`. The committed HLIL and
Ghidra corpus were sufficient for this static mapping pass, so no game launch
was needed.

## Evidence Inputs

- Canonical binary: `assets/quakelive/quakelive_steam.exe`
- Binary Ninja HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part03.txt`
- Ghidra function rows:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- Source owners:
  `src/code/botlib/be_aas_bspq3.c`,
  `src/code/botlib/be_aas_cluster.c`,
  `src/code/botlib/be_aas_entity.c`,
  `src/code/botlib/be_aas_file.c`,
  `src/code/botlib/be_aas_main.c`,
  `src/code/botlib/be_interface.c`,
  `src/code/game/botlib.h`,
  `src/code/game/g_syscalls.c`,
  `src/code/server/sv_game.c`,
  and `src/code/server/ql_game_imports.inc`

## Promoted Names

| Retail address | Promoted name | Evidence summary |
|---|---|---|
| `sub_4829C0` | `AAS_Trace` | 46-byte direct `botimport.Trace` wrapper returning `bsp_trace_t`. |
| `sub_482A00` | `AAS_EntityCollision` | `botimport.EntityTrace` wrapper that copies the entity trace only when it beats the current fraction. |
| `sub_482A90` | `AAS_inPVS` | 10-byte direct `botimport.inPVS` wrapper. |
| `sub_482AA0` | `AAS_BSPModelMinsMaxsOrigin` | 10-byte direct `botimport.BSPModelMinsMaxsOrigin` wrapper. |
| `sub_482D20` | `AAS_FreeBSPEntities` | BSP entity/epair free loop clearing `bspworld` entity ownership. |
| `sub_485230` | `AAS_EntityModelindex` | Entity-valid guard followed by public entity-info `modelindex` return. |
| `sub_485270` | `AAS_EntityType` | Entity-valid guard followed by public entity-info `type` return. |
| `sub_4852C0` | `AAS_EntityModelNum` | Entity-valid guard followed by public entity-info `modelnum` return. |
| `sub_485310` | `AAS_OriginOfMoverWithModelNum` | Entity scan for movers with a matching model number and copied origin. |
| `sub_485450` | `AAS_NextEntity` | Sequential valid-entity iterator. |
| `sub_4854A0` | `AAS_SwapAASData` | Byte-swap pass over all loaded AAS lumps. |
| `sub_4857D0` | `AAS_LoadAASLump` | Sequential lump reader with hunk allocation, `FS_Seek`, `FS_Read`, and `lastoffset` tracking. |
| `sub_485D90` | `AAS_WriteAASLump` | Lump offset/length writer with file-size accumulation. |

Existing names in the same corridor were rechecked rather than repromoted:
`AAS_PointContents`, `AAS_NextBSPEntity`, BSP epair query helpers,
`AAS_ParseBSPEntities`, `AAS_DumpBSPData`, `AAS_LoadBSPFile`,
`AAS_UpdatePortal`, `AAS_FloodClusterAreas_r`, `AAS_FindClusters`,
`AAS_CreatePortals`, `AAS_InitClustering`, `AAS_EntityInfo`,
`AAS_ResetEntityLinks`, `AAS_InvalidateEntities`,
`AAS_UnlinkInvalidEntities`, `AAS_DumpAASData`, `AAS_LoadAASFile`,
`AAS_WriteAASFile`, `AAS_ContinueInit`, `AAS_StartFrame`, `AAS_LoadFiles`,
`AAS_LoadMap`, `AAS_Setup`, and `AAS_Shutdown`.

## Source Reconstruction

No C source body change is justified for this tranche. The checked-in source
already matches the observed retail static shape for the mapped lifecycle
owners:

- BSP wrappers delegate through the expected botlib import slots.
- BSP entity parsing uses the retail script flags, epair allocation/copy loop,
  `MAX_BSPENTITIES` guard, and `bspworld.numentities` accounting.
- Entity update/query helpers retain Quake Live's expanded entity-info payload,
  relink behavior, invalidation pass, and mover-origin scan.
- AAS file loading checks the AAS magic/version, decrypts current-version data,
  validates `sv_mapChecksum`, reads the 14 retail lumps in order, and swaps
  loaded data before marking the file loaded.
- Main lifecycle wiring preserves setup, continue-init, start-frame,
  load-map/load-files, and shutdown ordering.
- Cluster initialization preserves the loaded guard, forced-clustering controls,
  portal allocation/index setup, possible-portal pass, cluster flood, and
  reachability continuation path.
- Public AAS/BSP exports and both legacy and Quake Live qagame import wrappers
  remain in the source order expected by the retail syscall/import surfaces.

## Validation

Added `tests/test_botlib_aas_lifecycle_parity.py` to pin:

1. Alias names, Ghidra function-row sizes, and HLIL anchors for the BSP,
   cluster, entity, AAS-file, and main lifecycle band.
2. Source shape for BSP import wrappers, BSP entity parsing, epair helpers,
   BSP cleanup, and BSP load/dump behavior.
3. Source shape for entity update/query helpers and their AI goal/movement
   consumers.
4. Source shape for AAS data swapping, lump read/write helpers, AAS file
   load/write, main lifecycle setup/start-frame/load-map/shutdown, and cluster
   initialization.
5. Public `bsp_export_t`/`aas_export_t` order, `Init_BSP_Export` and
   `Init_AAS_Export` assignments, server VM syscall dispatch, Quake Live native
   import slab entries, and qagame syscall wrappers.

Focused validation:

```text
python -m pytest tests/test_botlib_aas_lifecycle_parity.py -q
```

Observed result:

```text
5 passed in 0.11s
```

Broader botlib validation:

```text
$files = Get-ChildItem tests -Filter test_botlib_*.py | ForEach-Object { $_.FullName }; python -m pytest $files -q
```

Observed result:

```text
80 passed in 2.27s
```

Mixed botlib/native import validation:

```text
python -m pytest tests/test_botlib_aas_lifecycle_parity.py tests/test_botlib_aas_sample_parity.py tests/test_botlib_reachability_generation_parity.py tests/test_botlib_route_runtime_parity.py tests/test_game_native_export_helper_parity.py -q
```

Observed result:

```text
29 passed in 0.53s
```

## Parity Estimate

- Focused AAS BSP/file/entity lifecycle mapping: approximately `78% -> 94%`.
- Overall botlib plus AAS lifecycle/import wiring: approximately `85% -> 86%`.
- Remaining uncertainty is live-map `.aas` content, map-dependent clustering
  and reachability quality, and runtime bot behavior, not the static lifecycle
  ownership or public wiring covered by this pass.
