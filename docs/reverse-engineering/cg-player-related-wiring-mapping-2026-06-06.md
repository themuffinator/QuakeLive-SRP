# CG_Player Related Wiring Mapping - 2026-06-06

## Scope

This follow-up pass extends the prior `CG_Player()` reconstruction by drilling into the directly adjacent helper bodies that are visible in the committed Binary Ninja HLIL and Ghidra exports:

- `FUN_100405a0` / `0x100405A0`: `CG_PlayerPowerups`
- `FUN_10040870` / `0x10040870`: `CG_PlayerObjectiveSprite`
- `FUN_10040cd0` / `0x10040CD0`: `CG_PlayerFloatSprite`
- `FUN_100411a0` / `0x100411A0`: `CG_PlayerSprites`
- `FUN_10041860` / `0x10041860`: `CG_AddRefEntityWithPowerups`

Owner binary: `cgamex86.dll`.

Evidence used:

- `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil_split/cgamex86.dll_hlil_part01.txt`
- `references/reverse-engineering/ghidra/cgamex86/decompile_top_functions.c`
- `references/reverse-engineering/ghidra/cgamex86/functions.csv`
- `references/analysis/quakelive_symbol_aliases.json`
- `references/symbol-maps/cgame.json`

## Source Reconstruction

### Player Powerup Dynamic Lights

HLIL for `0x100405A0` shows the player powerup helper adding the same `200 + (rand() & 31)` radius dynamic lights as the source path, but with Quake Live color tuning:

- Quad branch: `(0.25f, 0.75f, 1.0f)`
- Battle Suit branch: `(0.75f, 0.75f, 0.0f)`

The current source only had the older Quad color and no Battle Suit player dlight. This pass updates `CG_PlayerPowerups` to match the observed retail values while leaving the existing flag, flight-loop, and haste-trail flow intact.

### Frozen Player Ice Overlay

HLIL for `0x10041860` shows a high-bit player powerup overlay after the normal invis/quad/regen/battlesuit submissions:

- `state->powerups & 0x8000`
- If `state->generic1 & 2`: use `powerups/ice1`
- Else if `state->generic1 & 1`: use `powerups/ice2`
- Else: use `powerups/ice3`

The source already uses `1 << PW_NUM_POWERUPS` as the frozen-player bit for `CG_IsFrozenPlayer` and `CG_PlayerSprites`, which lines up with retail `0x8000`. This pass adds the `ice1`, `ice2`, and `ice3` media handles and registers the matching shaders, then submits the ice overlay from `CG_AddRefEntityWithPowerups`.

## Mapping Notes

`CG_PlayerObjectiveSprite` remains a retail-only marker producer reached after `CG_PlayerPowerups`. HLIL shows it selecting Harvester objective colors/markers and then CTF/1FCTF/Attack and Defend objective markers through the same queued marker allocator family. The current source has Harvester and flag-carry capture marker coverage, but Attack and Defend attack/defend/capture selection still needs a dedicated pass before further source changes.

`CG_PlayerSprites` is still correctly placed as the status-sprite dispatcher reached from `CG_Player` behind `cg_drawSprites`. HLIL confirms the same broad priority lane: connection icon, one-flag carrier/special objective cases, team/friend status, talk/award markers, and Red Rover infected target handling. The exact retail ordering around friend markers and Red Rover survivor suppression remains worth a separate branch-by-branch comparison.

`CG_AddRefEntityWithPowerups` has more retail-only overlay branches than this pass reconstructed:

- `powerups/spawnArmor` / `powerups/spawnArmor2` on raw bit `0x1`
- `noPlayerClipShader` when the custom-settings mask suppresses normal invisibility rendering for non-local players
- The high-bit ice overlay reconstructed here

The spawn-armor and no-player-clip branches are intentionally left open because they touch broader spawn-protection and custom-setting semantics beyond `CG_Player()`.

## Shared Bit-Layout Risk

The retail helper bodies expose raw `entityState_t.powerups` bit tests that do not line up cleanly with every current source enum name in `bg_public.h`. For example, the committed retail bodies test:

- `0x10` for the Quad overlay/dlight path
- `0x20` for the Battle Suit overlay/dlight path
- `0x100` for the Regen pulse overlay
- `0x8000` for the frozen ice overlay

The frozen bit already matches the source's intentional `1 << PW_NUM_POWERUPS` use. The remaining raw bit layout should be audited across qagame, cgame, `BG_PlayerStateToEntityState`, item pickup, HUD, and network serialization before any shared enum reorder is attempted.

## Files Changed In This Pass

- `src/code/cgame/cg_local.h`
  - Added `ice1Shader`, `ice2Shader`, and `ice3Shader`.
- `src/code/cgame/cg_main.c`
  - Registered `powerups/ice1`, `powerups/ice2`, and `powerups/ice3`.
- `src/code/cgame/cg_players.c`
  - Updated Quad player dlight color to retail QL values.
  - Added Battle Suit player dlight.
  - Added the frozen high-bit ice overlay in `CG_AddRefEntityWithPowerups`.

## Confidence

High confidence:

- `CG_PlayerPowerups` color values come directly from Binary Ninja HLIL constants in the `0x100405A0` body.
- `CG_AddRefEntityWithPowerups` ice shader names and selection bits are directly visible in HLIL and Ghidra registration strings.
- The frozen high bit is already used consistently by current source as `1 << PW_NUM_POWERUPS`.

Medium confidence:

- The semantic names for every raw retail powerup bit require a broader shared-state audit. This pass avoids changing shared enum layout for that reason.

Open follow-ups:

- Reconstruct the Attack and Defend branch of `CG_PlayerObjectiveSprite`.
- Audit the spawn armor and no-player-clip overlay branches in `CG_AddRefEntityWithPowerups`.
- Audit retail powerup bit ordering across qagame, cgame, item definitions, and network entity conversion.
