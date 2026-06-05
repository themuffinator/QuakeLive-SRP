# `Botlib` Internal Parity Audit And Implementation Plan

Last updated: 2026-06-05

Scope: `src/code/botlib/*` internals as owned by retail `quakelive_steam.exe`, excluding the already-closed server bridge/import table in `src/code/server/sv_bot.c`

Purpose: close the remaining-engine host/support `EH-G04` confidence gap by separating the already-mapped botlib bridge from the still-unaudited internal helper tree, publishing a retail-backed evidence trail for representative internal owners, and adding deterministic probes for the AAS, reachability, and goal-state helpers that materially affect live bot behavior.

## Owning Retail Binary And Evidence Base

Owning retail binary:

- `assets/quakelive/quakelive_steam.exe`

Primary committed evidence used for this pass:

- `docs/reverse-engineering/quakelive_steam_mapping_round_61.md`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/*`
- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`
- `src/code/botlib/be_interface.c`
- `src/code/botlib/be_aas_sample.c`
- `src/code/botlib/be_aas_main.c`
- `src/code/botlib/be_aas_reach.c`
- `src/code/botlib/be_ai_goal.c`
- `tests/test_botlib_internal_parity.py`
- `tests/botlib_internal_harness.c`
- `tests/test_bot_resource_loading.py`

## Audit Method

1. Start with the already-closed retail bridge owner lane from mapping round `61` so the audit does not relitigate `sv_bot.c`.
2. Look for direct retail signals inside `quakelive_steam.exe` before treating an internal helper as merely a Quake III carry:
   - promoted or mappable call/export context
   - retained fatal/error strings in HLIL or Ghidra companion output
   - repeated public export-table wiring in `be_interface.c`
3. Treat deterministic harness probes as secondary proof for helpers whose runtime behavior is simple, pure, and stable enough to test without a live map load.
4. Separate observed retail facts from source-backed inference:
   - observed retail facts: bridge/import ownership, retained strings, exported helper wiring
   - inference: helpers whose exact body is not directly named in the retail corpus but remain strongly consistent with the retained Quake III carry and current export wiring

## Bridge Closure Baseline

The server-owned botlib bridge is already strongly closed and is not reopened by this audit.

Observed facts from `quakelive_steam_mapping_round_61.md`:

- retail `sv_bot.c` ownership is closed for `SV_BotAllocateClient`, `SV_BotFreeClient`, `BotDrawDebugPolygons`, the `BotImport_*` bridge family, `SV_BotFrame`, `SV_BotLibSetup`, `SV_BotLibShutdown`, `SV_BotInitCvars`, `SV_BotInitBotLib`, `SV_BotGetConsoleMessage`, and `SV_BotGetSnapshotEntity`
- direct retained owners exposed through that bridge are also bounded: `CM_EntityString`, `Z_AvailableMemory`, `SV_inPVS`, and `SV_PointContents`

Conclusion:

- the open botlib work is not a bridge-ownership problem anymore
- the remaining question was internal helper confidence, not whether the engine still owns the import seam
- 2026-06-05 recheck: `docs/reverse-engineering/botlib-server-import-bridge-recheck-2026-06-05.md`
  adds focused regression coverage for `SV_BotInitBotLib`, the `BotImport_*`
  trace/BSP/debug helpers, the retail `0x004DD940` import table, and the
  qagame syscall bridge while confirming no C source body change was needed.
- 2026-06-05 native-import recheck:
  `docs/reverse-engineering/botlib-native-import-compat-bridge-recheck-2026-06-05.md`
  pins the adjacent qagame native import compatibility slab, separating named
  retail `G_QL_IMPORT_BOTLIB_*` slots and direct bot-AI resource slots from the
  smaller retained legacy botlib ID set that is intentionally served through
  `G_QL_IMPORT_COMPAT_BASE + arg`.
- 2026-06-05 export-table layout recheck:
  `docs/reverse-engineering/botlib-export-table-layout-recheck-2026-06-05.md`
  pins retail `GetBotLibAPI`, the internal AAS/EA/AI table offsets, the hidden
  `EA_Walk` slot between `EA_Action` and `EA_Gesture`, the two AI debug tail
  slots after `GeneticParentsAndChildSelection`, and the direct AAS quartet
  order exported by `quakelive_steam.exe`.
- 2026-06-05 structure-reader mapping:
  `docs/reverse-engineering/botlib-structure-resource-reader-mapping-2026-06-05.md`
  identifies `l_struct.c` as a productive forward botlib section and pins
  `FindField`, `ReadNumber`, and `ReadStructure` against the retail
  `quakelive_steam.exe` HLIL, Ghidra call sites, and bot item/weapon resource
  consumers. The same pass now also pins the concrete `iteminfo`,
  `weaponinfo`, and `projectileinfo` field tables, retail allocation sizes, and
  weapon/projectile fix-up wiring while documenting the adjacent write helpers
  as source-real but not yet safely retail-aliased.
- 2026-06-05 parser-sibling extension: the same mapping note now covers the
  adjacent characteristic and fuzzy-weight resource readers. It pins
  `BotLoadCharacterFromFile`, `BotLoadCachedCharacter`,
  `BotLoadCharacterSkill`, `ReadValue`, `ReadFuzzyWeight`,
  `ReadFuzzySeperators_r`, `ReadWeightConfig`, and `FindFuzzyWeight` against
  retail HLIL/Ghidra evidence, including character allocation `0x2cc`, weight
  config allocation `0x444`, characteristic index bounds, default-character
  fallback, weight cache behavior, recursive fuzzy-switch parsing, and the
  source `#if 0` writer boundary.
- 2026-06-05 precompiler source-handle mapping:
  `docs/reverse-engineering/botlib-precompiler-source-handle-mapping-2026-06-05.md`
  selects the next botlib slice after the parser-resource corridor and pins
  `PC_LoadSourceHandle`, `PC_FreeSourceHandle`, `PC_ReadTokenHandle`,
  `PC_SourceFileAndLine`, `PC_SetBaseFolder`, and
  `PC_CheckOpenSourceHandles` against retail HLIL/Ghidra evidence. The pass
  also records the related ABI wiring through `GetBotLibAPI`,
  `botlib_export_t`, `SV_GameSystemCallsImpl`, qagame compatibility imports,
  and classic `trap_PC_*` wrappers, while preserving the fact that only
  `PC_AddGlobalDefine` has a named direct native qagame slot.

## Retail-Backed Internal Anchors

### AAS sampling and setup anchors

Observed retail facts:

- the retail HLIL corpus preserves the fatal string `AAS_PresenceTypeBoundingBox: unknown presence type\n`
- the retail HLIL corpus also preserves `AAS initialized.\n`
- `be_interface.c` still exports `AAS_PresenceTypeBoundingBox` through the public AAS table

Interpretation:

- `AAS_PresenceTypeBoundingBox` is not just an inherited anonymous helper; it remains visible enough in the retail corpus to be treated as a real internal ownership anchor
- the surrounding AAS setup/sample lane remains a stable retained carry unless contradictory retail evidence appears

### Goal-state lifecycle anchors

Observed retail facts:

- the retail HLIL corpus preserves `goal state handle %d out of range\n`
- the retail HLIL corpus preserves `invalid goal state %d\n`
- the retail HLIL corpus preserves `goal heap overflow\n`
- the retail HLIL corpus also preserves `invalid goal state handle %d\n`
- `be_interface.c` still exports `BotResetGoalState`, `BotResetAvoidGoals`, `BotPushGoal`, `BotPopGoal`, `BotEmptyGoalStack`, `BotAllocGoalState`, and `BotFreeGoalState`

Interpretation:

- the goal-state allocator, handle guards, stack operations, and avoid-goal timers are retail-visible enough to justify direct source-backed regression coverage
- this lane materially affects live bot planning and is now bounded beyond the old bridge/resource-only coverage

### Reachability helper anchors

Observed facts:

- `be_interface.c` still exports `AAS_AreaTravelTimeToGoalArea`, which keeps the internal reachability lane on the public botlib surface
- `be_aas_reach.c` still contains the retained Quake III jump/fall formulas and the `bot_notteam` travel-flag translator
- no committed retail alias round currently promotes these exact helper names directly

Inference:

- `AAS_FallDamageDistance`, `AAS_FallDelta`, `AAS_MaxJumpHeight`, `AAS_MaxJumpDistance`, and `AAS_TravelFlagsForTeam` should be treated as strong source-backed carries with stable exported call context, not as currently unbounded unknowns

## Deterministic Proof Surface Added In This Pass

Proof owner:

- `tests/test_botlib_internal_parity.py`
- `tests/botlib_internal_harness.c`

Covered internal behaviors:

1. AAS presence bounds
   - `AAS_PresenceTypeBoundingBox`
   - verifies retail-shaped normal and crouch hulls
2. AAS vector projection carry
   - `AAS_ProjectPointOntoVector`
   - verifies the retained projection math used by the AAS helper lane
3. Reachability physics carries
   - `AAS_FallDamageDistance`
   - `AAS_FallDelta`
   - `AAS_MaxJumpHeight`
   - `AAS_MaxJumpDistance`
   - verifies the retained jump/fall formulas against deterministic seeded physics settings
4. Team travel-flag translation
   - `AAS_TravelFlagsForTeam`
   - verifies `bot_notteam -> TRAVELFLAG_NOTTEAM1/TRAVELFLAG_NOTTEAM2`
5. Goal-state lifecycle
   - `BotAllocGoalState`
   - `BotPushGoal`
   - `BotGetTopGoal`
   - `BotGetSecondGoal`
   - `BotPopGoal`
   - `BotEmptyGoalStack`
   - `BotResetGoalState`
   - `BotSetAvoidGoalTime`
   - `BotAvoidGoalTime`
   - `BotRemoveFromAvoidGoals`
   - `BotFreeGoalState`
   - verifies stack ordering, timer decay, reset semantics, and retail-visible invalid-handle strings

Why this proof surface is enough to close `EH-G04`:

- it no longer leaves botlib bounded only by the server bridge and a high-level bot resource schedule test
- it exercises representative internal helpers from the three gameplay-relevant internal lanes that mattered most to this audit:
  - AAS/sample math
  - reachability physics/flags
  - goal-state planning state
- it also cross-checks the writable source for the expected bodies and public export-table wiring so the harness cannot silently drift away from the audited owners

## Inherited Quake III Carries Versus Quake Live-Specific Deltas

### Treated as inherited carries for this audit

These helpers are now explicitly treated as retained Quake III carries that still fit the retail Quake Live host:

- `AAS_PresenceTypeBoundingBox`
- `AAS_ProjectPointOntoVector`
- `AAS_FallDamageDistance`
- `AAS_FallDelta`
- `AAS_MaxJumpHeight`
- `AAS_MaxJumpDistance`
- `AAS_TravelFlagsForTeam`
- `BotGoalStateFromHandle`
- `BotResetAvoidGoals`
- `BotRemoveFromAvoidGoals`
- `BotAvoidGoalTime`
- `BotSetAvoidGoalTime`
- `BotPushGoal`
- `BotPopGoal`
- `BotEmptyGoalStack`
- `BotGetTopGoal`
- `BotGetSecondGoal`
- `BotResetGoalState`
- `BotAllocGoalState`
- `BotFreeGoalState`

Reasoning:

- their current source bodies are stable retained Quake III carries
- their surrounding retail anchors are strong enough that treating them as active unknowns would now overstate the gap
- the new deterministic probes make their behavioral contract machine-visible

### Still treated as Quake Live-specific or map/game dependent deltas

These lanes remain outside the narrow `EH-G04` closure claim:

- map-loaded AAS graph contents and any retail-produced `.aas` data differences
- gameplay-layer physics or item weighting that flows in from game cvars, entity epairs, or module logic
- combat/weapon/character heuristics such as fight-weapon choice, item desirability tuning, and chat logic
- large-scale route generation or bot movement integration that depends on full live entity/world state rather than deterministic helper inputs

Interpretation:

- this pass closes the internal-proof gap for representative helper ownership
- it does not claim that every gameplay-tuning nuance inside all of botlib has already been exhaustively reverse-mapped against a live retail match

## Historical `FIXME` Markers

Observed fact:

- the internal `botlib` tree still contains historical GPL-era `FIXME` comments

Interpretation:

- those comments are no longer sufficient, by themselves, to keep `EH-G04` open
- after this audit they are treated as implementation notes inside a now-bounded subsystem, not as proof that the whole internal botlib lane remains unaudited

## Validation Snapshot

Validation command for this closure pass:

1. `pytest tests/test_botlib_internal_parity.py tests/test_bot_resource_loading.py tests/test_engine_host_support_full_parity_gate.py -q --tb=no`

Observed result on 2026-04-10:

- `14 passed, 1 skipped`

Follow-up focused validation on 2026-06-05 expanded the botlib proof lane with
export-table, qagame native-import, showpath, entity-layout, selected-bot
telemetry, structure-reader, and snapshot-ordering sentinels. The current
focused botlib/native suite is tracked in `tests/test_botlib_internal_parity.py`
and `tests/test_game_native_export_helper_parity.py`; recent tranche runs
include the full pair passing with `24 passed`.

Broader remaining-engine host/support validation after wiring this proof lane back into the shared workflow is recorded in the parent host/support audit and gate artifact.

## Gap Outcome

`EH-G04` is now considered closed.

Why:

- the bridge owner was already mapped
- the internal helper tree now has one dedicated retail-backed audit
- representative AAS, reachability, and goal-state helpers now have deterministic regression coverage
- inherited carries versus Quake Live-specific deltas are now explicitly bounded instead of being left as an undifferentiated unknown

## Implementation Summary

Completed in this pass:

1. Published this dedicated botlib internal audit and implementation note.
2. Added `tests/test_botlib_internal_parity.py` and `tests/botlib_internal_harness.c` for deterministic native proof of representative internal helpers.
3. Wired the new proof lane into the remaining-engine host/support gate and validation workflow.
4. Reclassified the open botlib internal lane from “bridge-only confidence” to “subsystem-level confidence with bounded remaining map/game-specific deltas”.

## Follow-On Work

No new standalone botlib closure tranche is required to keep `EH-G04` closed
under the remaining-engine host/support audit after this pass. However, the
June 2026 reconstruction rounds show that smaller botlib refinement tranches
are still worthwhile when the committed retail references expose a concrete
source, ABI, or mapping mismatch.

Relevant future work can still happen when it is driven by a more specific
gameplay or retail-reference question:

- deeper route-generation or live-map AAS investigations if a concrete retail mismatch appears
- weapon/goal desirability tuning audits if the gameplay/module audits surface a bot behavior regression
- compatibility-lane cleanup under `EH-P5` and strict-retail boundary reporting under `EH-P1`
