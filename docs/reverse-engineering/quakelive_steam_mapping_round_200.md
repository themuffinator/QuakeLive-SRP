# quakelive_steam.exe Mapping Round 200

Date: 2026-04-28

Scope: retained `cm_patch.c` patch-collision plane/grid preprocessing helpers
around the old queue head `0x004C12F0`.

## Summary

This round resolved `10` additional `quakelive_steam.exe` aliases.
Classification mix:

- `10` engine-owned functions
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The useful outcome is that the anonymous patch-collision slab from
`0x004C0840` through `0x004C12F0` now reads as the real retained
`cm_patch.c` plane/grid preprocessing lane instead of a mix of opaque helper
bodies. The most important closure is the old queue head
`sub_4C12F0 -> CM_FindPlane`, which also makes the already-mapped
`CM_SubdivideGridColumns`, `CM_SetBorderInward`, `CM_AddFacetBevels`, and
`CM_PatchCollideFromGrid` neighborhood read as one coherent patch-collision
ownership chain.

## Evidence Notes

- The decisive source anchors are
  [CM_PlaneFromPoints](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/cm_patch.c:127>),
  [CM_NeedsSubdivision](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/cm_patch.c:158>),
  [CM_TransposeGrid](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/cm_patch.c:207>),
  [CM_SetGridWrapWidth](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/cm_patch.c:258>),
  [CM_ComparePoints](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/cm_patch.c:357>),
  [CM_RemoveDegenerateColumns](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/cm_patch.c:382>),
  [CM_PlaneEqual](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/cm_patch.c:431>),
  [CM_SnapVector](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/cm_patch.c:465>),
  [CM_FindPlane2](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/cm_patch.c:490>),
  and [CM_FindPlane](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/cm_patch.c:518>).
- `sub_4C12F0` is decisively `CM_FindPlane`, not an edge/border wrapper. Its
  retained HLIL first builds a plane from three points via `sub_4C0840`, then
  performs the exact `PLANE_TRI_EPSILON` triangle-vertex comparison against
  existing patch planes before allocating a new plane/signbits entry. That is
  the checked-in `CM_FindPlane` body line-for-line.
- `sub_4C1210` is the sibling `CM_FindPlane2` helper rather than the old queue
  head. Its HLIL walks the existing patch plane array, delegates comparison to
  `sub_4C1090`, returns the previously matched plane index on success, and
  appends a new plane/signbits pair only when no existing plane matches.
- `sub_4C08F0`, `sub_4C09E0`, `sub_4C0B50`, `sub_4C0F10`, and `sub_4C0FA0`
  close the retained grid-prep seam exactly as the checked-in source presents
  it: subdivision-distance midpoint testing, width/height transposition,
  wrap-width detection, per-point epsilon comparison, and degenerate-column
  removal.
- I deliberately left the adjacent
  [CM_GridPlane](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/cm_patch.c:597>)
  /
  [CM_EdgePlaneNum](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/cm_patch.c:619>)
  seam deferred. The source ordering and HLIL context make both neighbors
  obvious, but the committed Ghidra corpus still does not expose a stable,
  separately promotable function-row split for that local wrapper boundary.

## Aliases Added

- `sub_4C0840` -> `CM_PlaneFromPoints`
- `sub_4C08F0` -> `CM_NeedsSubdivision`
- `sub_4C09E0` -> `CM_TransposeGrid`
- `sub_4C0B50` -> `CM_SetGridWrapWidth`
- `sub_4C0F10` -> `CM_ComparePoints`
- `sub_4C0FA0` -> `CM_RemoveDegenerateColumns`
- `sub_4C1090` -> `CM_PlaneEqual`
- `sub_4C1190` -> `CM_SnapVector`
- `sub_4C1210` -> `CM_FindPlane2`
- `sub_4C12F0` -> `CM_FindPlane`

## Verification

Static mapping validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- scoped duplicate-key scan for the `quakelive_steam` alias block passed with
  `0` duplicates
- recount after this pass: `2143` raw alias entries, `2070` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `37.822%` of `5473` functions
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
| 1 | `0x004E6730` | `FUN_004e6730` | `504` |
| 2 | `0x004B3672` | `FUN_004b3672` | `495` |
| 3 | `0x004368A0` | `FUN_004368a0` | `484` |
| 4 | `0x00429DD0` | `FUN_00429dd0` | `483` |
| 5 | `0x004A4280` | `FUN_004a4280` | `483` |
| 6 | `0x004B6630` | `FUN_004b6630` | `483` |
| 7 | `0x004241C0` | `FUN_004241c0` | `482` |
| 8 | `0x0042A130` | `FUN_0042a130` | `480` |
| 9 | `0x00498890` | `FUN_00498890` | `480` |
| 10 | `0x00480DD0` | `FUN_00480dd0` | `479` |

The next pass can return to the still-heavy engine-owned seam at
`sub_4E6730`, keep trimming the residual `FUN_004b3672` Ghidra split inside
the now-mapped console neighborhood, or continue down the remaining
patch-collision lane toward the deferred `CM_GridPlane` / `CM_EdgePlaneNum`
boundary once the wrapper split is stable enough to promote cleanly.
