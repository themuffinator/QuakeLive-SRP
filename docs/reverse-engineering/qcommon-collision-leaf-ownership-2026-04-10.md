# `qcommon` Collision Leaf Ownership Note

Last updated: 2026-04-10

Scope: bound the `cm_patch.c` / `cm_polylib.c` helper band beneath the already-mapped public `CM_*` ABI in retail `quakelive_steam.exe`.

## Evidence Anchors

- `docs/reverse-engineering/quakelive_steam_mapping_round_25.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_33.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_65.md`
- `references/analysis/quakelive_symbol_aliases.json`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `src/code/qcommon/cm_patch.c`
- `src/code/qcommon/cm_polylib.c`
- `src/code/client/cl_cgame.c`
- `tests/cm_collision_harness.c`
- `tests/test_qcommon_collision_leaf_parity.py`

## Observed Retail Facts

1. Mapping round `33` already closes the public collision setup and trace seam through:
   - `CM_LoadMap`
   - `CM_InlineModel`
   - `CM_TempBoxModel`
   - `CM_PointContents`
   - `CM_TransformedPointContents`
   - `CM_BoxTrace`
   - `CM_TransformedBoxTrace`
2. The committed HLIL still shows the mapped retail trace wrappers immediately above the deeper collision helper band:
   - `0x004C78C0` returns through `sub_4c72a0(...)` and is promoted as `CM_BoxTrace`
   - `0x004C7900` is promoted as `CM_TransformedBoxTrace`
3. Mapping round `25` closes `QLCGImport_CM_MarkFragments` as the raw native cgame import wrapper for mark fragmentation.
4. The current writable source routes `CG_CM_MARKFRAGMENTS` through `re.MarkFragments` in `src/code/client/cl_cgame.c`, so the strict Win32 public `CM_MarkFragments` seam is not a separate `src/code/qcommon/*` owner in the recovered host source.

Observed fact:

- the retail public ABI is already bounded at the `CM_*` wrapper layer, but the committed mapping rounds do not promote per-leaf names for the deeper patch/polylib helper band

## Observed Source Facts

1. `src/code/qcommon/cm_local.h` exposes the patch leaf seam directly beneath the public collision ABI:
   - `CM_GeneratePatchCollide`
   - `CM_TraceThroughPatchCollide`
   - `CM_PositionTestInPatchCollide`
2. `src/code/qcommon/cm_patch.c` owns the patch-construction and patch-trace helper band beneath those entrypoints, including:
   - `CM_PatchCollideFromGrid`
   - `CM_ValidateFacet`
   - `CM_AddFacetBevels`
   - `CM_CheckFacetPlane`
3. `src/code/qcommon/cm_polylib.c` owns the winding/polygon helper family that the patch band depends on directly, including:
   - `BaseWindingForPlane`
   - `ChopWindingInPlace`
   - `WindingArea`
   - `WindingBounds`
   - `AddWindingToConvexHull`
4. The source call graph directly binds those files together:
   - `CM_ValidateFacet` calls `BaseWindingForPlane` and `ChopWindingInPlace`
   - `CM_AddFacetBevels` calls `BaseWindingForPlane`, `ChopWindingInPlace`, `WindingBounds`, and `CopyWinding`
   - `CM_DrawDebugSurface` calls `BaseWindingForPlane` and `ChopWindingInPlace`

Observed fact:

- the retained `cm_polylib.c` helper family is not an adjacent convenience copy; it is part of the active patch-collision ownership band inside `qcommon`

## Focused Validation

`tests/cm_collision_harness.c` now compiles `src/code/qcommon/cm_patch.c` and `src/code/qcommon/cm_polylib.c` as native sources behind focused harness stubs, and `tests/test_qcommon_collision_leaf_parity.py` now guards the leaf band directly.

Current deterministic probes:

1. Curved patch generation:
   - `CM_GeneratePatchCollide` returns `36` planes, `4` facets, and expanded bounds `[-17, -17, -1] -> [17, 17, 33]` for the retained 3x3 bowed patch fixture.
2. Flat patch point trace exactness:
   - `CM_TraceThroughPatchCollide` returns fraction `(32 - 0.125) / 64` and normal `[0, 0, -1]` for the focused point-trace probe.
3. Patch position overlap:
   - `CM_PositionTestInPatchCollide` reports overlap for a centered `[-2, -2, -2] .. [2, 2, 2]` box at `z = 1` and no overlap at `z = 5`.
4. Mark-fragment-style clipping geometry:
   - `BaseWindingForPlane` plus `ChopWindingInPlace` reduce the plane winding to a `[-4, -2, 0] .. [4, 2, 0]` rectangle with area `32`.
5. Representative patch facet helper:
   - `CM_CheckFacetPlane` reports the expected enter fraction `(32 - 0.125) / 64` on the focused crossing probe.

Observed fact:

- the leaf band is no longer only justified by downstream runtime behavior; it is now covered by a dedicated native harness and deterministic assertions

## Ownership Boundary

Observed fact:

- retail `QLCGImport_CM_MarkFragments` remains a thin import wrapper, and the writable source still routes `CG_CM_MARKFRAGMENTS` to `re.MarkFragments`

Inference:

- `QC-P4` closes the “mark-fragment behavior” part of the gap by bounding the retained shared geometry-helper family in `cm_polylib.c`, not by claiming a new qcommon-owned public `CM_MarkFragments` Win32 wrapper that the current source does not implement

Conclusion:

- beneath the already-mapped public `CM_*` ABI, the remaining collision leaf band is now bounded to the retained `cm_patch.c` / `cm_polylib.c` helper family rather than remaining an open-ended confidence bucket
- that is sufficient to close `QC-G02` in the strict `qcommon` audit while keeping the renderer-owned `CM_MarkFragments` import seam documented honestly
