# Freeze Tag Helper Query Mapping - 2026-06-06

## Scope

This follow-up Freeze Tag pass tightened the helper-search topology inside the
`G_FreezeClientEndFrame` thaw lane. The previous reconstruction had already
corrected the remaining-thaw-time counter and retained-helper latch, but still
used a flat client-slot scan for nearby thaw helpers. Retail uses an entity-box
query first, then applies the same client/team/state/trace gates to the listed
entities.

## Evidence

The committed Ghidra decompile for `FUN_1004CD40` shows the frozen player's
origin expanded by the configured thaw radius on all three axes, followed by a
qagame import-table call at `DAT_104b13ac + 0xa4` with a `0x400` entry limit.
That import is the qagame `trap_EntitiesInBox` bridge, already recovered on the
host side as `QL_G_trap_EntitiesInBox`.

The matching HLIL around `0x1004CEE5` shows the same shape:

- build mins/maxs around the frozen player's origin and radius;
- call the import at `+0xa4` with `0x400`;
- iterate returned entity numbers;
- reject self, non-client entities, wrong team, frozen/dead helpers, and line
  of sight failures unless through-surface thawing is enabled;
- retain the first valid helper client number through the `+0x1f8/+0x1fc`
  latch path before the remaining-time decrement.

## Source Reconstruction

`G_FreezeCountThawHelpers` now builds the thaw-radius AABB, calls
`trap_EntitiesInBox( mins, maxs, entityList, MAX_GENTITIES )`, and validates
only the returned entities through `G_FreezeClientCanHelpThaw`. The public
helper's count-returning signature remains unchanged, but the selected helper
now follows retail's first-valid entity-list behavior instead of the previous
nearest-client scan.

The retained-helper lookup remains slot-based through
`G_FreezeFindThawHelperByClientNum`, matching the small retail lookup sidecar
that revalidates the latched helper once a thaw source has been selected.

The adjacent progress-flag follow-up is tracked in
`docs/reverse-engineering/freeze-tag-thaw-progress-eflags-mapping-2026-06-06.md`.
It covers the low `EF_DEAD`/`EF_TICKING` thaw-progress buckets that retail
updates before entering this helper-query lane.

## Confidence And Open Questions

Confidence is high for the entity-box query topology because Ghidra, HLIL, and
the host import alias all agree on the `+0xa4` / `0x400` call shape.

The remaining open Freeze helper uncertainty is no longer the search topology;
it is field-layout exactness around the reconstructed `gclient_t` thaw fields
and any live retail DLL validation that would compare event ordering in a real
Freeze match.
