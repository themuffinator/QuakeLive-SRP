# Botlib Fuzzy Weight Runtime Mapping - 2026-06-05

## Conflict Check

Active session `019e97e9-ddaa-7e53-81bb-6511a54422c2` is working the
`l_struct.c` resource-structure reader and the shared
`tests/test_botlib_internal_parity.py` file. This pass deliberately selected a
different botlib section:

- primary source owner: `src/code/botlib/be_ai_weight.c`
- related consumers: `src/code/botlib/be_ai_goal.c` and
  `src/code/botlib/be_ai_weap.c`
- related export wiring: `src/code/botlib/be_interface.c` and
  `src/code/game/botlib.h`
- new verification file: `tests/test_botlib_weight_runtime_parity.py`

No `assets/`, `src/ui/`, `l_struct.c`, or shared botlib parity-test edits were
made.

## Selected Forward Section

The recommended next botlib work area is the fuzzy weight runtime:

- weight config parsing and caching in `ReadWeightConfig`
- nested switch/case/default fuzzy tree parsing in `ReadFuzzySeperators_r`
- numeric and `balance(...)` return parsing in `ReadValue` and
  `ReadFuzzyWeight`
- deterministic and undecided scoring in `FuzzyWeight_r` and
  `FuzzyWeightUndecided_r`
- mutation, balance-range scaling, and interbreed helpers
- item and weapon consumers that turn parsed weights into goal and weapon
  choices

This is a good future section because it is engine-owned botlib code, not an
online-service divergence, and it gates both long-term item selection and fight
weapon choice. It is also safely separated from the active `l_struct` session:
the structure reader parses character/item/weapon schemas, while this pass
focuses on the fuzzy logic weight language and runtime scoring tree.

## Evidence Sources

Retail owner: `quakelive_steam.exe`, because the botlib runtime is compiled into
the host executable.

Evidence checked:

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part03.txt`
- `references/analysis/quakelive_symbol_aliases.json`
- source counterparts under `src/code/botlib/` and `src/code/game/botlib.h`

The earlier broad mapping passes already promoted the two largest public weight
parser aliases:

- Round 120: `sub_4A6B40 -> ReadWeightConfig`
- Round 121: `sub_4A66A0 -> ReadFuzzySeperators_r`

This pass started as a coherent source-shape map for the smaller helpers and
their consumers. The follow-up alias-promotion tranche in
`botlib-fuzzy-weight-alias-promotion-2026-06-05.md` now promotes the stable
small-helper names in the alias artifact as well.

## Function Map

| Retail address | Source owner | Evidence | Status |
| --- | --- | --- | --- |
| `0x004A63F0` | `ReadValue` | `negative value set to zero`, `invalid return value %s` diagnostics and float write | Promoted in alias map; guarded by focused test |
| `0x004A64D0` | `ReadFuzzyWeight` | `balance`, `(`, `,`, `)`, `;` grammar and fallback scalar return path | Promoted in alias map; guarded by focused test |
| `0x004A65C0` | `FreeFuzzySeperators_r` | child/next recursive free then memory release | Promoted in alias map; guarded by focused test |
| `0x004A6600` | `FreeWeightConfig2` | frees each weight name and separator tree, then config | Promoted in alias map; guarded by focused test |
| `0x004A6670` | `FreeWeightConfig` | gated by `bot_reloadcharacters` before tail-calling full free | Promoted in alias map; guarded by focused test |
| `0x004A66A0` | `ReadFuzzySeperators_r` | switch index, `case`, `default`, duplicate-default error, auto default fallback | Existing alias; expanded source-shape guard |
| `0x004A6B40` | `ReadWeightConfig` | `weightFileList`, `botfiles`, `weight`, max count, `loaded %s` | Existing alias; expanded source-shape guard |
| `0x004A7140` | `FindFuzzyWeight` | linear weight-name scan and `-1` miss return | Promoted in alias map; guarded by focused test |
| `0x004A71A0` | `FuzzyWeight_r` | recursive child/next traversal and between-case interpolation | Promoted in alias map; guarded by focused test |
| `0x004A7260` | `FuzzyWeightUndecided_r` | same traversal plus `random()` between min/max range | Promoted in alias map; guarded by focused test |
| `0x004A7390` | `FuzzyWeight` | tiny wrapper into `FuzzyWeight_r` | Promoted in alias map; guarded by focused test |
| `0x004A73B0` | `FuzzyWeightUndecided` | tiny wrapper into `FuzzyWeightUndecided_r` | Promoted in alias map; guarded by focused test |
| `0x004A73D0` | `EvolveFuzzySeperator_r` | `0.01` mutation jump, `0.5` normal drift, min/max expansion | Promoted in alias map; guarded by focused test |
| `0x004A74B0` | `EvolveWeightConfig` and inlined evolution walk | per-weight traversal over fuzzy separator trees | Promoted in alias map; guarded by focused test |
| `0x004A75C0` | `InterbreedFuzzySeperator_r` | unequal child/balance/next diagnostics and average weight write | Promoted in alias map; guarded by focused test |
| `0x004A76D0` | `InterbreedWeightConfigs` | numweights equality guard and per-weight interbreed calls | Promoted in alias map; guarded by focused test |
| `0x004A7820` | `BotShutdownWeights` | scans `MAX_WEIGHT_FILES`, uses full free, nulls slots | Existing alias; expanded source-shape guard |

Observed function-size anchors from Ghidra:

- `FUN_004a63f0,004a63f0,211,0,unknown`
- `FUN_004a64d0,004a64d0,230,0,unknown`
- `FUN_004a65c0,004a65c0,55,0,unknown`
- `FUN_004a6600,004a6600,108,0,unknown`
- `FUN_004a6670,004a6670,35,0,unknown`
- `FUN_004a66a0,004a66a0,1180,0,unknown`
- `FUN_004a6b40,004a6b40,1524,0,unknown`
- `FUN_004a7140,004a7140,89,0,unknown`
- `FUN_004a71a0,004a71a0,180,0,unknown`
- `FUN_004a7260,004a7260,295,0,unknown`
- `FUN_004a7390,004a7390,28,0,unknown`
- `FUN_004a73b0,004a73b0,28,0,unknown`
- `FUN_004a73d0,004a73d0,220,0,unknown`
- `FUN_004a74b0,004a74b0,264,0,unknown`
- `FUN_004a75c0,004a75c0,258,0,unknown`
- `FUN_004a76d0,004a76d0,332,0,unknown`
- `FUN_004a7820,004a7820,158,0,unknown`

## Source Reconstruction Findings

No C body patch was needed. The checked-in source already preserves the retail
shape for the selected section, including details that are easy to mis-clean:

- The retail/source spelling is `Seperators`, not `Separators`.
- `ReadValue` accepts a leading `-`, warns that the negative value is set to
  zero, and then reads the numeric token.
- `ReadWeightConfig` keeps the retail misspelling in the load failure diagnostic:
  `counldn't load %s`.
- `ReadWeightConfig` caches loaded configs only when
  `bot_reloadcharacters == 0`; `FreeWeightConfig` is gated by the same cvar,
  while `BotShutdownWeights` directly calls the full free helper.
- `ReadFuzzySeperators_r` synthesizes a default separator with
  `MAX_INVENTORYVALUE` and zero weight when a switch has no explicit default.
- `FuzzyWeight_r` keeps the stock integer-division interpolation shape observed
  in HLIL before returning the scaled blend.
- `FuzzyWeightUndecided_r` deliberately calls `FuzzyWeight_r` for the child of
  the next separator while using undecided/randomized scoring for its current
  child path.
- `InterbreedFuzzySeperator_r` preserves the retail/source recursive child-call
  oddity: the recursive child path passes `fs2->child` for both parent
  arguments.

Those details are now covered by `tests/test_botlib_weight_runtime_parity.py`.

## Consumer And Export Wiring

The source and HLIL agree on the consumer chain:

- `BotLoadItemWeights` calls `ReadWeightConfig`, reports fatal
  `couldn't load weights`, requires `itemconfig`, and builds
  `ItemWeightIndex`.
- `ItemWeightIndex` maps item class names through `FindFuzzyWeight` and logs a
  missing fuzzy weight per item.
- `BotChooseLTGItem` and `BotChooseNBGItem` reject missing item weights, skip
  negative weight indexes, evaluate `FuzzyWeight`, apply roam scaling, and divide
  by travel time.
- `BotLoadWeaponWeights` frees previous weights, calls `ReadWeightConfig`,
  requires `weaponconfig`, and builds `WeaponWeightIndex`.
- `BotChooseBestFightWeapon` skips invalid weapons and negative fuzzy indexes
  before comparing `FuzzyWeight` results.
- `Init_AI_Export` exports item weight load/free/mutate/interbreed entries and
  weapon choice/load entries in the retail slot order.

Retail export-table anchors confirmed in HLIL:

- `arg1[0x31] = sub_49f6f0` (`BotLoadItemWeights`)
- `arg1[0x32] = sub_49f780` (`BotFreeItemWeights`)
- `arg1[0x33] = sub_49cc30` (`BotInterbreedGoalFuzzyLogic`)
- `arg1[0x34] = sub_49ccf0` (`BotSaveGoalFuzzyLogic`)
- `arg1[0x35] = sub_49cd30` (`BotMutateGoalFuzzyLogic`)
- `arg1[0x44] = sub_4a6190` (`BotChooseBestFightWeapon`)
- `arg1[0x46] = sub_4a6060` (`BotLoadWeaponWeights`)

## Observed Facts Versus Inference

Observed:

- Address starts and sizes are present in committed Ghidra `functions.csv`.
- HLIL contains the parser diagnostics, recursive calls, cvar gates, and export
  assignments listed above.
- Source contains matching function bodies and consumer wiring.
- Existing alias map already names the large public owners and consumer wrappers.

Inferred:

- The smaller helpers are best treated as a coherent internal fuzzy-weight
  runtime cluster rather than separate source-debt items, because the call graph
  and source adjacency are tight and all observed diagnostics/control flow match
  the checked-in C.
- The child-call oddity in `InterbreedFuzzySeperator_r` should remain unless a
  future retail build or independent binary proves otherwise.

Confidence: high for ownership and source shape. The follow-up promotion pass
resolved the earlier open question about whether the tiny helpers deserved
aliases by limiting the additions to stable function boundaries with direct
source owners.

## Verification

Added focused static regression coverage:

- `tests/test_botlib_weight_runtime_parity.py`

Recommended command:

```powershell
python -m pytest tests/test_botlib_weight_runtime_parity.py -q
```

No game launch was needed. This was a static reverse-engineering evidence pass,
not a runtime startup or renderer investigation.

## Parity Estimate

Before this pass:

- strict-retail Windows replacement target: `100%` unchanged from the current
  audit baseline
- repo-wide checked-in tree: approximately `99%` overall
- selected botlib fuzzy-weight section: approximately `94%` mapped confidence;
  large owner aliases existed, but lower helper ownership and source-shape
  sentinels were not consolidated

After this pass:

- strict-retail Windows replacement target: `100%` unchanged
- repo-wide checked-in tree: approximately `99%` overall
- selected botlib fuzzy-weight section: approximately `99%` mapped confidence;
  all public owners, internal helper ranges, source quirks, item/weapon wiring,
  and stable alias names are now covered by committed static tests and notes

The remaining `1%` section uncertainty is reserved for live behavior around real
retail botfiles and any future evidence that might split compiler inlining
artifacts differently.

## Follow-Up Queue

Good next work items that still avoid the active `l_struct` session:

1. Add a tiny non-binary text fixture for a fuzzy-weight config and a harnessed
   parser/evaluator test, if the current harness can expose `ReadWeightConfig`
   without broad botlib initialization.
2. Recheck real bot item and weapon weight files from the retail install only as
   read-only evidence; do not copy binary or asset payloads into the repo.
