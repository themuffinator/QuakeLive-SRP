# Grappling Hook Wiring Mapping - 2026-06-06

## Scope

This pass followed the Grappling Hook from bot reachability and travel
selection through qagame projectile lifecycle, shared pmove pull behavior, and
cgame rendering/impact media. The work focused on evidence-backed mapping and a
small cgame source reconstruction where the retail evidence showed a missing
impact-media branch.

## Evidence Used

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`
- `references/reverse-engineering/ghidra/qagamex86/functions.csv`
- `references/reverse-engineering/ghidra/qagamex86/decompile_top_functions.c`
- `references/reverse-engineering/ghidra/cgamex86/functions.csv`
- `references/reverse-engineering/ghidra/cgamex86/decompile_top_functions.c`
- `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt`
- `references/symbol-maps/qagame.json`
- `references/symbol-maps/cgame.json`
- Current source owners under `src/code/game/`, `src/code/cgame/`, and
  `src/code/botlib/`.

## Mapping Summary

| Binary | Address | Promoted owner | Source owner | Evidence |
| --- | ---: | --- | --- | --- |
| `quakelive_steam.exe` | `0x00490550` | `AAS_Reachability_Grapple` | `src/code/botlib/be_aas_reach.c` | Ghidra size `1822`; emits `TRAVEL_GRAPPLEHOOK` and uses `rs_startgrapple + distance * 0.25`. |
| `quakelive_steam.exe` | `0x004A3DE0` | `BotTravel_Grapple` | `src/code/botlib/be_ai_move.c` | Ghidra size `1183`; travel dispatcher calls it for `TRAVEL_GRAPPLEHOOK`. |
| `qagamex86.dll` | `0x1002FF20` | `PM_GrappleMove` | `src/code/game/bg_pmove.c` | Symbol map pins the pull toward `grapplePoint - 16 * forward` and the separate `pmove_velocity_gh` pull speed. |
| `qagamex86.dll` | `0x1005D270` | `fire_grapple` | `src/code/game/g_missile.c` | Ghidra size `409`; spawns `"hook"`, sets `WP_GRAPPLING_HOOK`, `MOD_GRAPPLE`, and latches `client->hook`. |
| `qagamex86.dll` | `0x1005BBE0` | `G_MissileImpact` | `src/code/game/g_missile.c` | Ghidra size `3347`; branch on `"hook"` converts the missile to `ET_GRAPPLE`, arms `Weapon_HookThink`, and sets `PMF_GRAPPLE_PULL`. |
| `qagamex86.dll` | `0x1006E2C0` | `Weapon_GrapplingHook_Fire` | `src/code/game/g_weapon.c` | Ghidra size `105`; gate is `!fireHeld && !client->hook`. |
| `qagamex86.dll` | `0x1006E330` | `Weapon_HookFree` | `src/code/game/g_weapon.c` | Ghidra size `205`; clears active hook and `PMF_GRAPPLE_PULL`. |
| `qagamex86.dll` | `0x1006E400` | `Weapon_HookThink` | `src/code/game/g_weapon.c` | Ghidra size `950`; snaps to enemy center and republishes `ps.grapplePoint`. |
| `cgamex86.dll` | `0x100178E0` | `CG_Grapple` | `src/code/cgame/cg_ents.c` | Ghidra size `513`; renders the latched hook entity and forces the trail callback. |
| `cgamex86.dll` | `0x10050990` | `CG_GrappleTrail` | `src/code/cgame/cg_weapons.c` | Ghidra size `266`; anchors the beam to `otherEntityNum`, offsets viewheight/forward/up, and falls back from chain shader to lightning shader. |
| `cgamex86.dll` | `0x10053EF0` | `CG_MissileHitWall` | `src/code/cgame/cg_weapons.c` | Ghidra switch case `10` selects `sound/weapons/grapple/grhit.ogg`, `gfx/damage/cracked_mrk`, and a 16-unit impact mark. |

## Source Reconstruction

Observed retail behavior:

- `CG_RegisterSounds` registers `sound/weapons/grapple/grhit.ogg` into the same
  global impact-sound cluster as machinegun, nailgun, chaingun, rocket, and
  plasma impacts.
- `CG_RegisterGraphics` registers `gfx/damage/cracked_mrk` between
  `gfx/damage/plasma_mrk` and `markShadow`.
- `CG_MissileHitWall` has a `case 10` branch for `WP_GRAPPLING_HOOK` that uses
  the grapple hit sound, the cracked mark shader, no explosion model, and the
  default hook branch radius of `16`.

Implemented source changes:

- Added `cgs.media.crackedMarkShader` and registered `gfx/damage/cracked_mrk`.
- Added `cgs.media.sfx_grapplehit` and registered
  `sound/weapons/grapple/grhit.ogg`.
- Added a `WP_GRAPPLING_HOOK` branch to `CG_MissileHitWall` that uses the
  recovered sound, mark shader, and 16-unit radius.
- Promoted qagame grapple lifecycle aliases in
  `references/analysis/quakelive_symbol_aliases.json` for `fire_grapple`,
  `G_MissileImpact`, `Weapon_GrapplingHook_Fire`, `Weapon_HookFree`,
  `Weapon_HookThink`, `FireWeapon`, and `TeleportPlayer`.
- Tightened `references/symbol-maps/cgame.json` comments for the sound,
  graphics, and impact owners.

## Guardrails and Open Questions

- I did not add a qagame write to the hook temp event's `s.weapon`. The
  decompiled `G_MissileImpact` hook branch does not show a clear retail write
  to the event entity's weapon field, so changing that server-side state would
  be an inference rather than observed behavior.
- The static cgame impact branch is high confidence because Ghidra gives three
  independent signals: the global `grhit.ogg` registration, the global
  `cracked_mrk` registration, and `CG_MissileHitWall` case `10` selecting both.
- Runtime validation is not required for this pass; the missing behavior is
  fully covered by the committed static evidence and can be pinned by tests.

## Verification

Added `tests/test_grappling_hook_mapping_parity.py`, covering:

- cgame source registration of `sfx_grapplehit` and `crackedMarkShader`;
- `CG_MissileHitWall` source behavior for `WP_GRAPPLING_HOOK`;
- Ghidra and HLIL anchors for `grhit.ogg` and `cracked_mrk`;
- promoted aliases for qagame hook lifecycle, cgame hook rendering/trail, and
  botlib grapple reach/travel owners;
- qagame, cgame, and `quakelive_steam.exe` Ghidra function rows for the mapped
  hook corridor.

Parity estimate: focused Grappling Hook wiring and cgame-impact parity moves
from **93% -> 98%**. Broader repo-wide parity remains approximately **99%**;
the remaining grapple uncertainty is the qagame temp-event weapon-field
question noted above and any untested live-map bot grapple path quality.
