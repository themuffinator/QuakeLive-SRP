# Botlib Export Table Layout Recheck - 2026-06-05

## Scope

This pass rechecked the internal botlib export table produced by
`GetBotLibAPI` in the retail `quakelive_steam.exe` owner. It covers the public
`botlib_export_t` layout, the internal AAS/EA/AI subtable offsets, the EA
action table slot that was still shaped like the older source carry, and the AI
tail slots that retail keeps just before the `BotLibSetup` tail.

## Retail Evidence

- Binary Ninja HLIL at `0x004a83c0` clears `0x224` bytes at `data_16dd860`,
  then initializes AAS at `data_16dd860`, EA at `data_16dd8b8`, and AI at
  `data_16dd91c`.
- The same owner writes `BotLibSetup` at `data_16dda50` and
  `BotLibStartFrame` at `data_16dda64`, matching the public
  `botlib_export_t` tail after the three subtables.
- The retail AAS export initializer writes `AAS_PredictRoute` at AAS slot
  `0x12`, `AAS_AlternativeRouteGoals` at `0x13`, `AAS_Swimming` at `0x14`, and
  `AAS_PredictClientMovement` at `0x15`.
- The retail EA export initializer writes `EA_Action` at EA slot `3`,
  `EA_Walk` at slot `4`, and `EA_Gesture` at slot `5`. It also keeps the no-op
  `EA_EndRegular` slot at `0x16`, `EA_GetInput` at `0x17`, and
  `EA_ResetInput` at `0x18`.
- The retail AI export initializer writes
  `GeneticParentsAndChildSelection` at AI slot `0x4a`, followed by two debug
  visualization exports at slots `0x4b` and `0x4c`.
- The slot `0x4b` body refreshes shown debug geometry every `0.1` seconds,
  optionally filters AAS areas around an origin by a `512` unit radius and PVS,
  shows area polygons, and draws reachability arrows with color variants for
  jump, walk-off-ledge, and rocket-jump travel types.
- The slot `0x4c` body resolves a move-state handle, clears shown debug lines,
  iterates `numavoidspots` at move-state offset `0x300`, and draws crosses from
  the avoid-spot array at offset `0x80` using each spot radius.

## Source Reconstruction

- `src/code/game/botlib.h` now includes `EA_Walk` in `ea_export_t` between
  `EA_Action` and `EA_Gesture`, matching the retail slot-4 export.
- `src/code/game/botlib.h` now also includes the two AI tail exports after
  `GeneticParentsAndChildSelection`, preserving retail's `BotLibSetup` tail
  offset at `0x1f0`.
- `src/code/botlib/be_interface.c::Init_EA_Export` now fills that slot with
  `EA_Walk`, while preserving the existing named assignments for crouch,
  movement, view, end-regular, get-input, and reset-input.
- `src/code/botlib/be_interface.c::Init_AI_Export` now fills the retail AI tail
  with conservative working names `BotDrawDebugAreas` and `BotDrawAvoidSpots`.
  The first helper reuses existing AAS debug primitives to show nearby or
  selected AAS areas and reachability arrows. The second helper reuses the
  existing move-state avoid-spot storage and draws each avoid spot as a red
  cross.
- `references/analysis/quakelive_symbol_aliases.json` now promotes the paired
  Binary Ninja names `sub_484BF0 -> BotDrawDebugAreas` and
  `sub_484DC0 -> BotDrawAvoidSpots`, keeping the source reconstruction and
  shared mapping corpus synchronized.
- `src/code/game/g_public.h`, `src/code/game/g_syscalls.c`, and
  `src/code/server/sv_game.c` now keep the direct AAS native quartet in retail
  order: predict route, alternative route goals, swimming, then predict client
  movement.

## Verification

- `tests/test_botlib_internal_parity.py::test_botlib_export_table_retail_layout_includes_ea_walk_slot`
  checks the source table shape, `EA_Walk`/`EA_Crouch` action bits, the AAS
  quartet order, the AI debug tail exports, and the HLIL `GetBotLibAPI` table
  offsets, debug-helper bodies, and promoted alias names.
- `tests/test_game_native_export_helper_parity.py::test_qagame_native_import_table_uses_public_header_count`
  checks the qagame native import slot numbers, direct mapper behavior, server
  import-table population, and the matching qagame Ghidra offsets.

## Parity Estimate

- Focused internal botlib export table layout: `92% -> 98%`.
- Overall botlib plus related wiring: approximately `68% -> 69%`.
