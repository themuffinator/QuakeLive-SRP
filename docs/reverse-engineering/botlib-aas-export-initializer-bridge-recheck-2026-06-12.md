# Botlib AAS Export Initializer Bridge Recheck - 2026-06-12

## Scope

This round rechecked the botlib-side public AAS export initializer. The
retail owner is `Init_AAS_Export` (`sub_4A7FC0`), which fills the nested
`aas_export_t` table before `GetBotLibAPI` returns the complete botlib export
surface to the host.

Primary reconstructed files:

- `src/code/game/botlib.h`
- `src/code/botlib/be_interface.c`
- `tests/test_botlib_aas_native_wrapper_slab_parity.py`

Primary evidence:

- Binary Ninja HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part03.txt`
- Ghidra functions table:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- Promoted aliases:
  `references/analysis/quakelive_symbol_aliases.json`

## Observed Retail Facts

- Retail `GetBotLibAPI` calls `sub_4A7FC0(&data_16dd860)` before the EA and
  AI export initializers.
- Retail `sub_4A7FC0` has Ghidra row
  `FUN_004a7fc0,004a7fc0,154,0,unknown`.
- `sub_4A7FC0` writes twenty-two AAS callbacks from `arg1[0]` through
  `arg1[0x15]`.
- The retail order is:
  `AAS_EntityInfo`, `AAS_Initialized`, `AAS_PresenceTypeBoundingBox`,
  `AAS_Time`, `AAS_PointAreaNum`, `AAS_PointReachabilityAreaIndex`,
  `AAS_TraceAreas`, `AAS_BBoxAreas`, `AAS_AreaInfo`,
  `AAS_PointContents`, `AAS_NextBSPEntity`, `AAS_ValueForBSPEpairKey`,
  `AAS_VectorForBSPEpairKey`, `AAS_FloatForBSPEpairKey`,
  `AAS_IntForBSPEpairKey`, `AAS_AreaReachability`,
  `AAS_AreaTravelTimeToGoalArea`, `AAS_EnableRoutingArea`,
  `AAS_PredictRoute`, `AAS_AlternativeRouteGoals`, `AAS_Swimming`,
  and `AAS_PredictClientMovement`.
- The promoted alias corpus maps every callback target in this initializer to
  its reconstructed AAS owner. Ghidra function rows are available for the
  initializer and the stable AAS callback targets except the small
  `AAS_Initialized` row, which remains pinned here through BN HLIL and alias
  evidence.

## Reconstruction Decision

The reconstructed source already matches the retail AAS export table:

- `aas_export_t` declares the twenty-two callbacks in retail order.
- `Init_AAS_Export` assigns the callbacks in the same order.
- `GetBotLibAPI` invokes `Init_AAS_Export` at the same point in the nested
  botlib export setup.

No source-code reconstruction was needed. The closure was a whole-table parity
gate: `test_aas_public_export_initializer_matches_retail_table_order`.

## Confidence And Open Questions

- Focused AAS public export initializer confidence:
  **before 92% -> after 99%**.
- Focused botlib AAS export-to-native bridge confidence:
  **before 98% -> after 99%**.
- Overall botlib plus qagame/server wiring reconstruction parity:
  **83.93% -> 83.96%**.

Remaining uncertainty is in runtime AAS path behavior and map-data-specific
results, not in the public AAS export table wiring.
