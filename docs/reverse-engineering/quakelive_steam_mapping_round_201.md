# quakelive_steam.exe Mapping Round 201

Date: 2026-04-28

Scope: retained `sv_world.c` server-world area-query and trace helpers around
the old queue head `0x004E6730`.

## Summary

This round resolved `4` additional `quakelive_steam.exe` aliases.
Classification mix:

- `4` engine-owned functions
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The useful outcome is that the anonymous server-world seam between the
already-mapped `SV_AreaEntities_r` and `SV_PointContents` owners now reads as
the real retained `sv_world.c` trace lane instead of opaque collision glue.
The key closure is the former queue head `sub_4E6730 -> SV_ClipMoveToEntities`,
and the same pass also closes the public `SV_AreaEntities`, `SV_ClipToEntity`,
and `SV_Trace` owners directly above and below it.

## Evidence Notes

- The decisive source anchors are
  [SV_AreaEntities](</E:/Repositories/QuakeLive-reverse/src/code/server/sv_world.c:431>),
  [SV_ClipToEntity](</E:/Repositories/QuakeLive-reverse/src/code/server/sv_world.c:468>),
  [SV_ClipMoveToEntities](</E:/Repositories/QuakeLive-reverse/src/code/server/sv_world.c:510>),
  [SV_Trace](</E:/Repositories/QuakeLive-reverse/src/code/server/sv_world.c:600>),
  plus the already-mapped neighbors
  [SV_AreaEntities_r](</E:/Repositories/QuakeLive-reverse/src/code/server/sv_world.c:382>)
  and [SV_PointContents](</E:/Repositories/QuakeLive-reverse/src/code/server/sv_world.c:657>).
- `sub_4E6650` is exact as `SV_AreaEntities`. Its HLIL is the tiny public
  wrapper that fills the `areaParms_t` stack object with mins/maxs/list/count,
  calls the recursive `SV_AreaEntities_r`, and returns the final count.
- `sub_4E6690` is exact as `SV_ClipToEntity`. The HLIL zeroes a `trace_t`,
  rejects mismatched contents up front, resolves the entity clip handle via the
  already-mapped `SV_ClipHandleForEntity`, falls back to `vec3_origin` for
  non-bmodels, calls `CM_TransformedBoxTrace`, and writes `trace->entityNum`
  only when `fraction < 1`.
- `sub_4E6730` is exact as `SV_ClipMoveToEntities`. The retained body gathers
  a touch list via `SV_AreaEntities`, derives `passOwnerNum`, skips the pass
  entity and the owner-owned missile cases, performs per-entity transformed box
  traces, preserves prior `startsolid`, and promotes better fractional hits
  into the caller-owned `moveclip_t`.
- `sub_4E6930` is exact as `SV_Trace`. Its HLIL normalizes null mins/maxs to
  `vec3_origin`, clears the local `moveclip_t`, calls `CM_BoxTrace` against the
  world, seeds `ENTITYNUM_WORLD` versus `ENTITYNUM_NONE`, builds the swept
  bounding box with the exact `-1`/`+1` expansion, then hands the clip to
  `SV_ClipMoveToEntities`.
- I deliberately left the renderer-side queue head `sub_4368A0` alone in this
  pass. It is clearly renderer-owned, but the evidence trail points to an
  internal quad-builder/helper rather than a stable public source owner, so the
  server-world lane was the cleaner exact promotion target.

## Aliases Added

- `sub_4E6650` -> `SV_AreaEntities`
- `sub_4E6690` -> `SV_ClipToEntity`
- `sub_4E6730` -> `SV_ClipMoveToEntities`
- `sub_4E6930` -> `SV_Trace`

## Verification

Static mapping validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- scoped duplicate-key scan for the `quakelive_steam` alias block passed with
  `0` duplicates
- recount after this pass: `2147` raw alias entries, `2074` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `37.895%` of `5473` functions
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
| 1 | `0x004B3672` | `FUN_004b3672` | `495` |
| 2 | `0x004368A0` | `FUN_004368a0` | `484` |
| 3 | `0x00429DD0` | `FUN_00429dd0` | `483` |
| 4 | `0x004A4280` | `FUN_004a4280` | `483` |
| 5 | `0x004B6630` | `FUN_004b6630` | `483` |
| 6 | `0x004241C0` | `FUN_004241c0` | `482` |
| 7 | `0x0042A130` | `FUN_0042a130` | `480` |
| 8 | `0x00498890` | `FUN_00498890` | `480` |
| 9 | `0x00480DD0` | `FUN_00480dd0` | `479` |
| 10 | `0x004C84E0` | `FUN_004c84e0` | `479` |

The next pass can keep attacking the lingering `FUN_004b3672` Ghidra split
inside the console neighborhood, pivot back into the renderer-owned
`sub_4368A0` helper seam, or continue down the remaining engine-owned queue in
the nearby `0x00429***` / `0x004A4***` lanes.
