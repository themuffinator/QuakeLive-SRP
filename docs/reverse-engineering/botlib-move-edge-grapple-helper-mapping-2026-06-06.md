# Botlib Move Edge And Grapple Helper Mapping - 2026-06-06

## Scope

This pass covers the remaining source-visible botlib helper rows outside the
already documented libjpeg false lead and route-runtime/prelude corridors:

- `src/code/botlib/be_aas_reach.c`
- `src/code/botlib/be_aas_move.c`
- `src/code/botlib/be_ai_move.c`
- `references/analysis/quakelive_symbol_aliases.json`

The owning retail binary is `quakelive_steam.exe`. Evidence comes from the
committed Binary Ninja HLIL split and Ghidra `functions.csv`.

## Retail Evidence

Primary anchors:

- `VectorDistance @ 0x0048B010`
- `VectorBetweenVectors @ 0x0048B060`
- `AngleDiff @ 0x0049FBC0`
- `GrappleState @ 0x004A3C80`
- `BotResetGrapple @ 0x004A3D40`

Observed retail facts:

- `VectorDistance` subtracts two vectors and returns the square-rooted length.
  Retail calls it repeatedly from `AAS_ClosestEdgePoints` when choosing the
  closest ranges between edge pairs.
- `VectorBetweenVectors` subtracts the candidate point from each endpoint and
  returns the `DotProduct(dir1, dir2) <= 0` between-ness test used by
  `AAS_ClosestEdgePoints`.
- `AngleDiff` computes `ang1 - ang2` and wraps into the `[-180, 180]` lane.
  Retail uses it from grapple aim activation and the rocket/BFG jump travel
  aim checks.
- `GrappleState` returns `2` when `MFL_GRAPPLEPULL` is set, scans AAS
  entities for a missile whose weapon equals `weapindex_grapple`, returns `1`
  for a visible grapple missile, and returns `0` otherwise.
- `BotResetGrapple` reads the previous reachability, checks for
  non-`TRAVEL_GRAPPLEHOOK`, optionally emits `cmd_grappleoff`, clears
  `MFL_ACTIVEGRAPPLE`, and zeroes `grapplevisible_time`.
- `BotTravel_Grapple` calls `GrappleState`, uses `AngleDiff` for the two-axis
  `2` degree activation threshold, and toggles `MFL_ACTIVEGRAPPLE` /
  `MFL_GRAPPLERESET` exactly where the source does.

## Changes

- Promoted aliases in `references/analysis/quakelive_symbol_aliases.json`:
  - `sub_48B010 -> VectorDistance`
  - `sub_48B060 -> VectorBetweenVectors`
  - `sub_49FBC0 -> AngleDiff`
  - `sub_4A3C80 -> GrappleState`
  - `sub_4A3D40 -> BotResetGrapple`
- Added `tests/test_botlib_move_edge_grapple_helper_parity.py`, covering:
  - alias rows and Ghidra function sizes,
  - HLIL helper bodies and call-site anchors,
  - source-side edge math and grapple helper bodies,
  - `AAS_ClosestEdgePoints`, `BotTravel_Grapple`, rocket/BFG jump travel, and
    `BotMoveToGoal` consumers,
  - the folded weapon-jump wrapper negative check.

## Negative Checks

- No C source body changed. The existing source already matches the retail
  helper behavior.
- `sub_486F40` is still intentionally unpromoted. Source has both
  `AAS_RocketJumpZVelocity` and `AAS_BFGJumpZVelocity`, and both wrappers call
  `AAS_WeaponJumpZVelocity(origin, 120)`. Retail exposes one tiny folded thunk
  that calls `sub_486D40(..., 120)`, so a single stable source-owner name would
  overstate the evidence.
- The adjacent `0x00482150..0x004829A0` block remains excluded as libjpeg
  memory-manager code rather than botlib.

## Validation

Focused validation:

```text
python -m pytest tests/test_botlib_move_edge_grapple_helper_parity.py -q
```

Observed result:

```text
4 passed in 0.08s
```

Broader botlib validation:

```text
$botlibTests = rg --files tests | Where-Object { $_ -match 'test_botlib_.*\.py$' }; python -m pytest $botlibTests -q
```

Observed result:

```text
103 passed in 3.75s
```

## Parity Estimate

- Focused AAS edge helper mapping: approximately `70% -> 97%`.
- Focused move-AI angle/grapple helper mapping: approximately `78% -> 97%`.
- Overall botlib plus movement/reachability helper wiring: approximately
  `81% -> 82%`.
- Repo-wide parity remains approximately `99%`; this pass closes static helper
  ownership without claiming live-map movement quality or dynamic bot behavior.
