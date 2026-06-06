# Botlib Genetic Selection Mapping - 2026-06-06

## Scope

This pass maps the small botlib genetic-selection helper pair and its qagame
interbreed wiring:

- `src/code/botlib/be_ai_gen.c`
- `src/code/botlib/be_interface.c`
- `src/code/game/be_ai_gen.h`
- `src/code/game/botlib.h`
- `src/code/game/ai_main.c`
- `src/code/game/g_local.h`
- `src/code/game/g_public.h`
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
  `src/code/botlib/be_ai_gen.c`,
  `src/code/botlib/be_interface.c`,
  `src/code/game/be_ai_gen.h`,
  `src/code/game/botlib.h`,
  `src/code/game/ai_main.c`,
  `src/code/game/g_local.h`,
  `src/code/game/g_public.h`,
  `src/code/game/g_syscalls.c`,
  `src/code/server/sv_game.c`,
  and `src/code/server/ql_game_imports.inc`

## Promoted Names

| Retail address | Promoted name | Evidence summary |
|---|---|---|
| `sub_49C6C0` | `GeneticSelection` | Private rank selector: skips negative ranks, sums valid weights, calls `random`, falls back to a wrapped random valid index, and is called three times by `GeneticParentsAndChildSelection`. |

The existing `sub_49C810 -> GeneticParentsAndChildSelection` alias was
rechecked in the same pass. The retail row is `1047` bytes, carries the
`too many bots` / `too few valid bots` warnings, copies the 256-rank stack
buffer, selects two parents, reverses remaining rankings, and selects the
child by calling `GeneticSelection`.

## Source Reconstruction

No C source body change is justified for this tranche. The checked-in
`be_ai_gen.c` source already matches the observed retail static shape:

- `GeneticSelection` skips negative ranks while summing, performs the weighted
  selection pass when the sum is positive, and otherwise performs the wrapped
  random fallback over non-negative rankings.
- `GeneticParentsAndChildSelection` enforces the retail `256` rank limit,
  requires at least three valid bots, zeroes all output indexes on failure,
  copies the rank buffer, selects parent one and parent two, writes `-1` into
  consumed parent slots, reverses the remaining positive rankings, and selects
  the child through the same helper.
- `Init_AI_Export` exposes only `GeneticParentsAndChildSelection`, matching the
  public `ai_export_t` surface; `GeneticSelection` remains a private helper.
- Qagame `BotInterbreedBots` consumes the export by ranking bots as
  `num_kills * 2 - num_deaths`, interbreeding the selected parent goal fuzzy
  logic into the selected child, mutating the child, and then clearing kill and
  death counters.
- Legacy syscall dispatch, the Quake Live native import id `184`, and
  `QL_G_trap_GeneticParentsAndChildSelection` all route back to
  `BOTLIB_AI_GENETIC_PARENTS_AND_CHILD_SELECTION`.

## Validation

Added `tests/test_botlib_genetic_selection_parity.py` to pin:

1. The new `GeneticSelection` alias, existing `GeneticParentsAndChildSelection`
   alias, Ghidra function sizes, HLIL helper headers, helper call sites, and
   export-table slot `0x4a`.
2. Source shape for the private weighted/fallback selector and the exported
   parent/child selector.
3. Public AI export order, `Init_AI_Export` assignment order, legacy syscall
   mapping, server VM dispatch, Quake Live native import slab, and direct
   native import wrapper.
4. Qagame `BotInterbreedBots` and `BotInterbreedEndMatch` source shape around
   rank generation, selected parent/child usage, mutation, counter reset, and
   cycle/write gating.

Focused validation:

```text
python -m pytest tests/test_botlib_genetic_selection_parity.py -q
```

Observed result:

```text
4 passed in 0.16s
```

Broader botlib validation:

```text
$files = Get-ChildItem tests -Filter test_botlib_*.py | ForEach-Object { $_.FullName }; python -m pytest $files -q
```

Observed result:

```text
84 passed in 2.62s
```

Mixed botlib/native/exit-rule validation:

```text
python -m pytest tests/test_botlib_genetic_selection_parity.py tests/test_botlib_weight_runtime_parity.py tests/test_botlib_internal_parity.py tests/test_game_native_export_helper_parity.py tests/test_game_exit_rules_parity.py -q
```

Observed result:

```text
61 passed in 1.31s
```

## Parity Estimate

- Focused genetic-selection helper/export mapping: approximately `72% -> 96%`.
- Overall botlib plus fuzzy/genetic interbreed wiring: approximately `86% -> 87%`.
- Remaining uncertainty is live interbreed behavior quality and map/bot-data
  effects, not the static selector ownership or import/export routing covered
  by this pass.
