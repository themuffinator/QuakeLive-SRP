# Botlib Fuzzy Weight Alias Promotion - 2026-06-05

## Scope

This round continues the fuzzy-weight runtime mapping from
`botlib-fuzzy-weight-runtime-mapping-2026-06-05.md` and promotes the stable
small helper aliases for the selected botlib section. It does not touch the
active `l_struct.c` resource-structure reader lane, `assets/`, or `src/ui/`.

Source owner:

- `src/code/botlib/be_ai_weight.c`

Related wiring:

- `src/code/botlib/be_ai_goal.c`
- `src/code/botlib/be_ai_weap.c`
- `src/code/botlib/be_interface.c`
- `src/code/game/botlib.h`

Retail owner:

- `quakelive_steam.exe`

## Promoted Aliases

The following aliases were added to
`references/analysis/quakelive_symbol_aliases.json`:

| Retail symbol | Promoted owner | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_4A63F0` | `ReadValue` | High | `negative value set to zero` and `invalid return value %s` diagnostics, token-to-float write |
| `sub_4A64D0` | `ReadFuzzyWeight` | High | `balance(...)` grammar, scalar fallback, semicolon requirement |
| `sub_4A65C0` | `FreeFuzzySeperators_r` | High | child/next recursive free then memory release |
| `sub_4A6600` | `FreeWeightConfig2` | High | per-weight separator and name frees followed by config free |
| `sub_4A6670` | `FreeWeightConfig` | High | `bot_reloadcharacters` gate before full free |
| `sub_4A7140` | `FindFuzzyWeight` | High | linear string match over `weightconfig_t` names and `-1` miss return |
| `sub_4A71A0` | `FuzzyWeight_r` | High | recursive child/next traversal and between-case interpolation |
| `sub_4A7260` | `FuzzyWeightUndecided_r` | High | randomized min/max leaf scoring and recursive traversal |
| `sub_4A7390` | `FuzzyWeight` | High | thin wrapper into the recursive evaluator |
| `sub_4A73B0` | `FuzzyWeightUndecided` | High | thin wrapper into the undecided evaluator |
| `sub_4A73D0` | `EvolveFuzzySeperator_r` | High | `0.01` mutation jump, `0.5` normal drift, min/max expansion |
| `sub_4A74B0` | `EvolveWeightConfig` | High | per-weight evolution walk; retail inlines the separator body shape |
| `sub_4A75C0` | `InterbreedFuzzySeperator_r` | High | unequal child/balance/next diagnostics and averaged balance weight |
| `sub_4A76D0` | `InterbreedWeightConfigs` | High | numweights guard and per-weight interbreed calls |

Existing aliases retained from earlier passes:

- `sub_4A66A0 -> ReadFuzzySeperators_r`
- `sub_4A6B40 -> ReadWeightConfig`
- `sub_4A7820 -> BotShutdownWeights`
- item and weapon consumer wrappers such as `BotLoadItemWeights`,
  `BotFreeItemWeights`, `BotLoadWeaponWeights`, and
  `BotChooseBestFightWeapon`

Not promoted in this round:

- `ScaleFuzzySeperator_r`, `ScaleWeight`,
  `ScaleFuzzySeperatorBalanceRange_r`, and `ScaleFuzzyBalanceRange`
  remain source-visible helpers only. The checked-in source preserves them, and
  the focused test guards their shape, but the committed retail function table
  does not expose stable starts for them in this host band. The conservative
  interpretation is that retail dead-stripped or inlined away the unused scale
  lane, so adding aliases would overstate the evidence.

## Evidence Notes

Canonical Binary Ninja HLIL:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part03.txt`
- function starts at `0x004A63F0`, `0x004A64D0`, `0x004A65C0`,
  `0x004A6600`, `0x004A6670`, `0x004A66A0`, `0x004A6B40`,
  `0x004A7140`, `0x004A71A0`, `0x004A7260`, `0x004A7390`,
  `0x004A73B0`, `0x004A73D0`, `0x004A74B0`, `0x004A75C0`,
  `0x004A76D0`, and `0x004A7820`

Companion Ghidra corpus:

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`

Source-shape anchors:

- Parser diagnostics: `negative value set to zero`, `invalid return value %s`,
  `switch already has a default`, `switch without default`,
  `too many fuzzy weights`, and retail's misspelled `counldn't load %s`.
- Runtime scoring: recursive child/next traversal, integer-division
  interpolation, randomized undecided min/max scoring, and the mixed
  `FuzzyWeight_r` call for the next child in `FuzzyWeightUndecided_r`.
- Genetic helpers: unequal child/balance/next/numweights diagnostics and
  source-preserved child-recursion oddity in `InterbreedFuzzySeperator_r`.

## Source Reconstruction Decision

No C body change was made. The source already matches the retail-visible shape
for this section. The reconstruction value in this round is alias promotion and
regression coverage:

- `references/analysis/quakelive_symbol_aliases.json` now names the whole
  fuzzy-weight helper cluster instead of only the two largest parser owners.
- `tests/test_botlib_weight_runtime_parity.py` now verifies the promoted aliases
  alongside raw Ghidra rows, HLIL diagnostics, source-shape details, and
  consumer/export wiring.

Observed facts:

- Ghidra `functions.csv` contains every promoted start address and size.
- HLIL shows the grammar, scoring, mutation, interbreed, cache-free, and export
  behavior used for the aliases.
- The checked-in C source has matching function ownership and control-flow
  shape.

Inference:

- `0x004A74B0` is promoted as `EvolveWeightConfig` even though retail inlines
  the separator evolution logic into the per-weight walk. This is the most
  accurate source owner for the function boundary because the public source
  helper boundary at that point is `EvolveWeightConfig`.

Confidence: high.

## Verification

Commands run:

```powershell
python -m json.tool references/analysis/quakelive_symbol_aliases.json
python -m pytest tests/test_botlib_weight_runtime_parity.py -q
```

Result:

- `tests/test_botlib_weight_runtime_parity.py` passed: `4 passed`

No game launch was performed; this was a static botlib reverse-engineering
mapping pass.

## Parity Estimate

Before this alias-promotion round:

- strict-retail Windows replacement target: `100%`
- repo-wide checked-in tree: approximately `99%`
- selected fuzzy-weight botlib section: approximately `98%`; source shape was
  guarded, but smaller retail helper aliases remained anonymous

After this round:

- strict-retail Windows replacement target: `100%`
- repo-wide checked-in tree: approximately `99%`
- selected fuzzy-weight botlib section: approximately `99%`; the full helper
  band now has stable alias coverage plus static source and wiring guards

The remaining section uncertainty is limited to optional runtime proof with real
retail bot weight files and whether future evidence should split any compiler
inlining artifacts differently.
