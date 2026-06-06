# Botlib Reachability Generation Mapping - 2026-06-06

This pass maps the Quake Live retail AAS reachability-generation support layer
around `be_aas_reach.c`, the jump helper calls in `be_aas_move.c`, and the
runtime `AAS_Optimize` behavior in `be_aas_optimize.c`.

## Evidence Inputs

- Canonical binary: `assets/quakelive/quakelive_steam.exe`
- Binary Ninja HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part03.txt`
- Ghidra function rows:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- Source owners:
  `src/code/botlib/be_aas_move.c`,
  `src/code/botlib/be_aas_optimize.c`,
  and `src/code/botlib/be_aas_reach.c`

## Promoted Names

| Retail address | Promoted name | Evidence summary |
|---|---|---|
| `sub_4881F0` | `AAS_ClientMovementHitBBox` | Thin wrapper into `AAS_ClientMovementPrediction` with `SE_HITBOUNDINGBOX`. |
| `sub_488240` | `AAS_HorizontalVelocityForJump` | Gravity/max-velocity jump arc solver and failure clamps. |
| `sub_488340` | `AAS_JumpReachRunStart` | Reverse reach direction, 400-unit command move, prediction stop-event fallback. |
| `sub_488430` | `AAS_Optimize` | Retail runtime no-op/stub printing `skipped AAS data optimization.` |
| `sub_488450` | `AAS_FaceArea` | Triangulated face-area cross-product sum. |
| `sub_4885A0` | `AAS_AreaVolume` | Tetrahedron accumulation from face plane distances, divided by three. |
| `sub_488AB0` | `AAS_SetupReachabilityHeap` | `0x300000` allocation for `AAS_MAX_REACHABILITYSIZE` linked records. |
| `sub_488B10` | `AAS_AllocReachability` | Free-list pop, max-size fatal guard, and link count increment. |
| `sub_488B90` | `AAS_FaceCenter` | Edge vertex accumulation with `0.5 / face->numedges` scale. |
| `sub_488CA0` | `AAS_FallDamageDistance` | Fall-damage velocity threshold and gravity distance formula. |
| `sub_488CF0` | `AAS_FallDelta` | Distance-to-delta damage conversion. |
| `sub_488D30` | `AAS_MaxJumpDistance` | Max horizontal distance from fall height, gravity, jump velocity, and max velocity. |
| `sub_488D80` | `AAS_AreaCrouch` | Presence-type normal-bit negation. |
| `sub_488DB0` | `AAS_AreaSwim` | `AREA_LIQUID` area-flag test. |
| `sub_488DE0` | `AAS_AreaLava` | `AREACONTENTS_LAVA` contents test. |
| `sub_488E00` | `AAS_AreaSlime` | `AREACONTENTS_SLIME` contents test. |
| `sub_488E20` | `AAS_ReachabilityExists` | Linked reachability scan by target area. |
| `sub_491750` | `AAS_StoreReachability` | Flatten temporary links into `aasworld.reachability` and area first/count metadata. |
| `sub_491B60` | `AAS_BestReachableLinkArea` | Ground/swim link preference followed by non-zero/reachability fallback. |

Existing names for `AAS_AreaReachability`, `AAS_SetWeaponJumpAreaFlags`, and
`AAS_InitReachability` were rechecked as part of the same corridor.

## Source Reconstruction

`AAS_Optimize` was reconstructed for the retail runtime build. The HLIL
function at `0x00488430` is a 17-byte stub that only prints
`skipped AAS data optimization.`. The checked-in GPL body still contained the
old optimizer, so the non-`BSPC` path now matches retail while the previous
optimizer remains under `BSPC` for the map compiler/tooling side.

No other C body change is justified by this pass. The reachability heap,
geometry, area-predicate, store, and initialization source already matches the
retail static shape for the checked anchors.

## Validation

Added `tests/test_botlib_reachability_generation_parity.py` to pin:

1. Alias names, Ghidra function-row sizes, and HLIL function headers for the
   mapped reachability-generation support band.
2. The retail non-`BSPC` `AAS_Optimize` stub and retained `BSPC` optimizer.
3. Jump helper source shape in `be_aas_move.c`.
4. Reachability heap, geometry, predicate, store, weapon-jump area-flag, and
   initialization source shape in `be_aas_reach.c`.

Focused parity estimate for the reachability-generation support corridor:
**before 82% -> after 96%**. Overall botlib plus related movement/route wiring
moves approximately **82% -> 84%** because this pass closes a broad support
layer and one proven runtime source divergence, while live-map `.aas` content
and generated reachability quality remain outside this static mapping round.
