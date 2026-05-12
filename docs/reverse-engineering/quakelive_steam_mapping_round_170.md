# quakelive_steam.exe Mapping Round 170

Date: 2026-04-27

Scope: exact `botlib` `be_aas_main.c` / `be_aas_move.c` helper recovery in the
old `0x00486D40` queue-head corridor. This pass stayed mapping-only and used
the committed HLIL corpus plus the checked-in botlib sources as the naming
anchor.

## Summary

This round resolved `8` additional `quakelive_steam.exe` rows.
Classification mix:

- `8` engine-owned functions
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The useful outcome is that the anonymous AAS movement-physics seam around the
old queue head `0x00486D40` now reads as real botlib ownership instead of a
mix of unnamed geometry helpers between the already-mapped reachability
functions. The tranche closes the shutdown/setup leaves, the grounded and
swimming probes, the weapon-jump vertical-velocity helper, and the small
movement integrators that `AAS_ClientMovementPrediction` depends on.

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_486D40` | `504` | engine-owned | `AAS_WeaponJumpZVelocity` | High | Closed from the exact `90` degree look-down setup, `rocketoffset`, `500`-unit trace, `radiusdamage - 0.5 * VectorLength(v)` damage falloff, `1600 * knockback / mass` scale, and `+ aassettings.phys_jumpvel` tail in `be_aas_move.c`. |
| 2 | `sub_486A60` | `434` | engine-owned | `AAS_AgainstLadder` | High | Closed from the exact `AAS_PointAreaNum` retry offsets, ladder-area and presence checks, ladder-face scan, and `abs(DotProduct(...) - plane->dist) < 3` / `AAS_PointInsideFace` test. |
| 3 | `sub_486C20` | `201` | engine-owned | `AAS_OnGround` | High | Closed from the exact `end[2] -= 10` trace, `startsolid`/`fraction >= 1.0` rejection, `origin[2] - trace.endpos[2] > 10` check, and max-steepness plane test. |
| 4 | `sub_4866A0` | `156` | engine-owned | `AAS_DropToFloor` | High | Closed from the exact `end[2] -= 100` trace and the `trace.startsolid` / `VectorCopy(trace.endpos, origin)` success path. |
| 5 | `sub_486FF0` | `142` | engine-owned | `AAS_ApplyFriction` | High | Closed from the exact horizontal-speed `sqrt`, `control = speed < stopspeed ? stopspeed : speed`, `newspeed` clamp, and XY rescale. |
| 6 | `sub_486F60` | `132` | engine-owned | `AAS_Accelerate` | High | Closed from the exact q2-style `currentspeed`, `addspeed`, `accelspeed = accel * frametime * wishspeed`, clamp-to-addspeed, and three-component velocity update. |
| 7 | `sub_486640` | `92` | engine-owned | `AAS_Shutdown` | High | Closed from the exact shutdown ordering: alternative routing, BSP/routing/link/entity/AAS frees, optional entity free, `Com_Memset(&aasworld, 0, sizeof(aas_t))`, and `"AAS shutdown.\n"` print. |
| 8 | `sub_486CF0` | `78` | engine-owned | `AAS_Swimming` | High | Closed from the exact `testorg[2] -= 2` probe and `AAS_PointContents(testorg) & (CONTENTS_LAVA|CONTENTS_SLIME|CONTENTS_WATER)` test. |

## Evidence Notes

- The decisive source anchors are the checked-in
  [be_aas_move.c](</E:/Repositories/QuakeLive-reverse/src/code/botlib/be_aas_move.c:56>)
  helpers
  [AAS_DropToFloor](</E:/Repositories/QuakeLive-reverse/src/code/botlib/be_aas_move.c:56>),
  [AAS_AgainstLadder](</E:/Repositories/QuakeLive-reverse/src/code/botlib/be_aas_move.c:123>),
  [AAS_OnGround](</E:/Repositories/QuakeLive-reverse/src/code/botlib/be_aas_move.c:185>),
  [AAS_Swimming](</E:/Repositories/QuakeLive-reverse/src/code/botlib/be_aas_move.c:215>),
  [AAS_WeaponJumpZVelocity](</E:/Repositories/QuakeLive-reverse/src/code/botlib/be_aas_move.c:290>),
  [AAS_Accelerate](</E:/Repositories/QuakeLive-reverse/src/code/botlib/be_aas_move.c:364>),
  and [AAS_ApplyFriction](</E:/Repositories/QuakeLive-reverse/src/code/botlib/be_aas_move.c:403>),
  plus
  [AAS_Shutdown](</E:/Repositories/QuakeLive-reverse/src/code/botlib/be_aas_main.c:406>)
  in `be_aas_main.c`.
- The committed HLIL for `0x004866A0` through `0x00486FF0` preserves the same
  constants and control flow directly: `100`-unit floor drop, `10`-unit ground
  probe, `2`-unit swim probe, the `90` / `8` / `500` / `1600` / `200`
  weapon-jump constants, and the exact acceleration/friction formulas used by
  `AAS_ClientMovementPrediction`.
- I intentionally did not promote `sub_486F40` in this pass. The retail build
  only exposes one tiny `120`-damage wrapper around `AAS_WeaponJumpZVelocity`,
  while the checked-in GPL source carries two semantically different public
  names, `AAS_RocketJumpZVelocity` and `AAS_BFGJumpZVelocity`, that currently
  compile to the same body because the historical BFG path still forwards
  `120`. The merged retail row is real, but forcing one of the two public
  names onto it would overstate the exactness of the match.

## Aliases Added

- `sub_486640` -> `AAS_Shutdown`
- `sub_4866A0` -> `AAS_DropToFloor`
- `sub_486A60` -> `AAS_AgainstLadder`
- `sub_486C20` -> `AAS_OnGround`
- `sub_486CF0` -> `AAS_Swimming`
- `sub_486D40` -> `AAS_WeaponJumpZVelocity`
- `sub_486F60` -> `AAS_Accelerate`
- `sub_486FF0` -> `AAS_ApplyFriction`

## Verification

Static mapping validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- scoped duplicate-key scan for the `quakelive_steam` alias block passed with
  `0` duplicates
- recount after this pass: `1990` raw alias entries, `1918` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `35.045%` of `5473` functions
- `git diff --check` passed aside from the repo's existing LF -> CRLF
  normalization warnings on touched text files
- no build or runtime launch was needed; this was mapping-only work on the
  committed evidence corpus

Parity estimate after this pass:

- strict-retail Windows replacement target: `100%` before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

After this round, the refreshed largest-unaliased queue begins with:

| # | Address | Ghidra name | Size |
| ---: | --- | --- | ---: |
| 1 | `0x004FC240` | `FUN_004fc240` | `537` |
| 2 | `0x0041AD70` | `FUN_0041ad70` | `517` |
| 3 | `0x004E6730` | `FUN_004e6730` | `504` |
| 4 | `0x004B4100` | `FUN_004b4100` | `502` |
| 5 | `0x00475200` | `FUN_00475200` | `497` |
| 6 | `0x0047DA20` | `FUN_0047da20` | `497` |
| 7 | `0x00409670` | `FUN_00409670` | `496` |
| 8 | `0x004B3672` | `FUN_004b3672` | `495` |
| 9 | `0x0051A990` | `FUN_0051a990` | `493` |
| 10 | `0x0041C400` | `FUN_0041c400` | `492` |

The next pass can return to the still-transformed `vorbisfile.c` search helper
at `sub_4FC240`, take the persistent STL/iostream queue head at
`sub_41AD70`, or keep working through the engine-owned host leftovers now that
the AAS movement corridor around `sub_486D40` is no longer anonymous.
