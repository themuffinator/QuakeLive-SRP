# Freeze Tag Thaw Progress eFlags Mapping - 2026-06-06

## Scope

This follow-up Freeze Tag pass mapped the retail playerstate `eFlags` writes at
the top of `qagamex86.dll::FUN_1004CD40`, the same body reconstructed locally
as `G_FreezeClientEndFrame`. The earlier rounds had already recovered the
remaining-thaw-time counter, retained helper latch, `trap_EntitiesInBox`
helper query, and `EV_THAW_TICK` transport. This pass closes the adjacent
low-bit thaw-progress buckets.

## Evidence

The committed Ghidra decompile for `FUN_1004CD40` starts by comparing the
client field at `gclient + 500` against `DAT_105a472c / 3` and
`(DAT_105a472c / 3) * 2`. The same body then writes the playerstate `eFlags`
field at `gclient + 0x1c0`:

- when remaining thaw time is above two thirds of the configured total,
  retail clears the low two bits with `& 0xfffffffc`;
- when remaining thaw time is above one third but no longer above two thirds,
  retail ORs bit `1`;
- when remaining thaw time is at or below one third, retail ORs bit `2`.

The shared source constants map those bits to `EF_DEAD` (`0x00000001`) and
`EF_TICKING` (`0x00000002`) in `bg_public.h`. This is an observed retail
bit-level write; the naming is an inferred source reconstruction because the
original retail symbols are not present in the stripped qagame DLL.

Ordering is also pinned by the decompile: the progress flag update precedes
the round-state/timeout gates, helper entity query, helper-retention sidecar,
and the `remaining -= frameMsec` / `remaining += frameMsec` update.

## Source Reconstruction

`G_FreezeUpdateThawProgressFlags` now mirrors the retail bucket logic at the
top of `G_FreezeClientEndFrame`. It uses `level.freezeConfig.thawTime / 3`
as the threshold width and writes the existing low `ps.eFlags` constants
directly:

- `remaining > 2/3 total`: clear `EF_DEAD | EF_TICKING`;
- `remaining > 1/3 total`: set `EF_DEAD`;
- otherwise: set `EF_TICKING`.

The middle and final branches intentionally preserve retail's one-way OR
behavior instead of clearing the other low bit. The high-remaining branch is
the only bucket that clears both bits.

`G_FreezeSetClientFrozenState` now clears those low Freeze progress bits on
freeze entry and thaw exit. That keeps stale progress state from leaking
across separate Freeze state transitions while still allowing
`G_FreezeClientEndFrame` to apply the recovered retail bucket state during the
next frozen frame.

## Related Wiring

The same `FUN_1004CD40` body still owns the recovered remaining-time counter,
the retained helper fields at the adjacent `+0x1f8/+0x1fc` offsets, the
`trap_EntitiesInBox` helper enumeration, and the whole-second `EV_THAW_TICK`
event gate. On the cgame side, event `0x58` is handled as `EV_THAW_TICK`, and
the current source already carries client-side consumers for the low
`EF_DEAD`/`EF_TICKING` bits. This pass did not change cgame rendering or HUD
logic; it only restored the server-side producer shape visible in qagame.

## Confidence And Open Questions

Confidence is high for the producer-side bucket logic because Ghidra, the
shared `eFlags` constants, and the surrounding `FUN_1004CD40` control flow all
agree. Confidence is medium-high for the transition cleanup because retail
sets the remaining-thaw-time field on freeze entry and the reconstructed source
needs a local stale-bit guard when reusing GPL-visible `EF_DEAD` and
`EF_TICKING` names.

The remaining open question is live validation of how the retail client
visually presents each bucket in a real Freeze match. Static evidence is enough
for the qagame producer reconstruction, so no game launch was required for
this pass.
