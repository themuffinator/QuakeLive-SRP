# quakelive_steam.exe Mapping Round 144

Date: 2026-04-27

Scope: refreshed largest-unaliased queue after round 143. This pass consumed
the deferred qcommon capsule/leaf lane headed by `sub_4C6BD0`, corrected the
older `sub_4C55D0` capsule helper label from round 125, and promoted the exact
adjacent renderer state wrappers around `sub_4357B0`.

## Summary

This round resolved `13` engine-owned `quakelive_steam.exe` rows: `12`
previously unresolved exact aliases plus `1` correction to an earlier alias.
Classification mix:

- `13` engine-owned functions
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

No source debt was opened. The qcommon tranche closes the handle-to-model,
leaf-test, and capsule-vs-capsule split that feeds `CM_Trace`, while the small
renderer tranche closes the exact `GL_*` state wrappers immediately adjacent to
the already-mapped `GL_State` and `RB_BeginDrawingView`.

This round also corrects a prior naming mistake: `sub_4C55D0` is the
position-test helper `CM_TestCapsuleInCapsule`, while the true sweep variant is
the previously unresolved `sub_4C6BD0 -> CM_TraceCapsuleThroughCapsule`.

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_4C6BD0` | `558` | engine-owned | `CM_TraceCapsuleThroughCapsule` | High | No new debt; exact sweep path using `CM_TraceThroughSphere` and `CM_TraceThroughVerticalCylinder`. |
| 2 | `sub_4C6E00` | `291` | engine-owned | `CM_TraceBoundingBoxThroughCapsule` | High | No new debt; exact box-vs-capsule sweep wrapper that converts to a temporary box model and calls `CM_TraceThroughLeaf`. |
| 3 | `sub_4C6080` | `301` | engine-owned | `CM_TraceThroughLeaf` | High | No new debt; exact leaf brush/patch trace loop with `CM_TraceThroughBrush` and `CM_TraceThroughPatchCollide`. |
| 4 | `sub_4C54D0` | `246` | engine-owned | `CM_TestInLeaf` | High | No new debt; exact position-test leaf walker over brushes and patches. |
| 5 | `sub_4C52B0` | `537` | engine-owned | `CM_TestBoxInBrush` | High | No new debt; exact position-test brush helper for box/capsule overlap. |
| 6 | `sub_4C55D0` | `829` | engine-owned | `CM_TestCapsuleInCapsule` | High | No new debt; corrected prior alias after separating position-test and sweep capsule paths. |
| 7 | `sub_4C5910` | `291` | engine-owned | `CM_TestBoundingBoxInCapsule` | High | No new debt; exact box-vs-capsule position-test wrapper that routes through `CM_TestInLeaf`. |
| 8 | `sub_4C0180` | `132` | engine-owned | `CM_ClipHandleToModel` | High | No new debt; exact bad-handle guard and box-model/submodel dispatch helper. |
| 9 | `sub_4C0540` | `56` | engine-owned | `CM_ModelBounds` | High | No new debt; exact mins/maxs copy wrapper over `CM_ClipHandleToModel`. |
| 10 | `sub_4357B0` | `22` | engine-owned | `GL_Bind` | High | No new debt; exact `GL_TEXTURE_2D` wrapper over the generalized texture-target binder. |
| 11 | `sub_4357D0` | `168` | engine-owned | `GL_SelectTexture` | High | No new debt; exact TMU select helper with the canonical unit-0/unit-1 error string. |
| 12 | `sub_435880` | `97` | engine-owned | `GL_Cull` | High | No new debt; exact face-culling state helper next to the already-mapped `GL_State`. |
| 13 | `sub_4358F0` | `129` | engine-owned | `GL_TexEnv` | High | No new debt; exact texture-environment helper with the `GL_MODULATE`/`GL_REPLACE`/`GL_DECAL`/`GL_ADD` switch. |

## Evidence Notes

- `sub_4C0180` is the exact `CM_ClipHandleToModel` owner because the body
  carries both `CM_ClipHandleToModel: bad handle %i` fatal strings and the
  same three-way dispatch as `cm_load.c`: submodel range, `BOX_MODEL_HANDLE` /
  `CAPSULE_MODEL_HANDLE`, then `MAX_SUBMODELS` failure.
- `sub_4C0540` is the exact `CM_ModelBounds` wrapper immediately above the
  collision helpers. It calls `sub_4C0180`, then copies the first three floats
  into `mins` and the next three into `maxs`, matching the `CM_ModelBounds`
  source body exactly.
- `sub_4C52B0` and `sub_4C54D0` are the position-test half of the leaf lane.
  `sub_4C52B0` rejects brushes via the stored bounds/extents tests before
  setting `startsolid/allsolid`, matching `CM_TestBoxInBrush`. `sub_4C54D0`
  walks `leaf->numLeafBrushes` and `leaf->numLeafSurfaces`, calls the already
  mapped `CM_PositionTestInPatchCollide`, and returns early on `allsolid`,
  which is the exact `CM_TestInLeaf` structure.
- `sub_4C6080`, `sub_4C6BD0`, and `sub_4C6E00` are the sweep half of the same
  qcommon cluster. `sub_4C6080` mirrors the leaf walk but calls the already
  mapped `CM_TraceThroughBrush` and patch trace helpers, making it the exact
  `CM_TraceThroughLeaf`. `sub_4C6E00` converts a capsule model into a centered
  temporary box model and immediately calls `sub_4C6080`, which matches
  `CM_TraceBoundingBoxThroughCapsule`.
- The prior round-125 alias on `sub_4C55D0` was too aggressive. Its body never
  calls `CM_TraceThroughSphere`, `CM_TraceThroughVerticalCylinder`, or
  `CM_TraceThroughLeaf`; instead it only compares overlap distances and forces
  zero-fraction solid state, which matches `CM_TestCapsuleInCapsule`. The true
  sweep variant is `sub_4C6BD0`, which calls the already-mapped
  `CM_TraceThroughSphere` and `CM_TraceThroughVerticalCylinder`, updates the
  trace fraction, and sets the collision flags exactly like
  `CM_TraceCapsuleThroughCapsule`.
- `sub_4357B0`, `sub_4357D0`, `sub_435880`, and `sub_4358F0` are exact
  renderer matches from `tr_backend.c`. `sub_4357B0` is the `GL_TEXTURE_2D`
  wrapper over the generalized binder below it, while the latter three are
  anchored by the literal `GL_SelectTexture: unit = %i` and
  `GL_TexEnv: invalid env '%d' passed` strings plus the canonical TMU/cull/env
  state transitions from the source.

## Aliases Added

- `sub_4357B0` -> `GL_Bind`
- `sub_4357D0` -> `GL_SelectTexture`
- `sub_435880` -> `GL_Cull`
- `sub_4358F0` -> `GL_TexEnv`
- `sub_4C0180` -> `CM_ClipHandleToModel`
- `sub_4C0540` -> `CM_ModelBounds`
- `sub_4C52B0` -> `CM_TestBoxInBrush`
- `sub_4C54D0` -> `CM_TestInLeaf`
- `sub_4C5910` -> `CM_TestBoundingBoxInCapsule`
- `sub_4C6080` -> `CM_TraceThroughLeaf`
- `sub_4C6BD0` -> `CM_TraceCapsuleThroughCapsule`
- `sub_4C6E00` -> `CM_TraceBoundingBoxThroughCapsule`

## Alias Corrections

- `sub_4C55D0` -> `CM_TestCapsuleInCapsule`
  Previously labeled as `CM_TraceCapsuleThroughCapsule` in round 125; the
  true sweep owner is `sub_4C6BD0`.

## Verification

Alias artifact validation:

- `references/analysis/quakelive_symbol_aliases.json` parses through
  `python -m json.tool`
- duplicate-key scan passed after the alias update
- recount after this pass: `1660` raw alias entries, `1589` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `29.033%` of `5473` functions
- refreshed unresolved queue was recomputed against the committed Ghidra
  function-start corpus after the alias update
- no game/runtime launch was performed; this was a static mapping pass

Parity estimate after this mapping-only pass remains unchanged:

- strict-retail Windows replacement target: `100%` before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

After this round, the refreshed largest-unaliased queue begins with:

| # | Address | Ghidra name | Size |
| ---: | --- | --- | ---: |
| 1 | `0x00435070` | `FUN_00435070` | `566` |
| 2 | `0x00440AD0` | `FUN_00440ad0` | `560` |
| 3 | `0x0040B050` | `FUN_0040b050` | `555` |
| 4 | `0x00419AD0` | `FUN_00419ad0` | `555` |
| 5 | `0x0040F7E0` | `FUN_0040f7e0` | `549` |
| 6 | `0x0041CFB0` | `FUN_0041cfb0` | `549` |
| 7 | `0x0042BA60` | `FUN_0042ba60` | `549` |
| 8 | `0x004940D0` | `FUN_004940d0` | `547` |
| 9 | `0x004F4410` | `FUN_004f4410` | `546` |
| 10 | `0x00475CA0` | `FUN_00475ca0` | `545` |

The next pass should return to `sub_435070` and `sub_440AD0`, then keep
working down the remaining queue head while preserving the existing
classification guardrails on unresolved engine, platform-service, and
support-library rows.
