# CG_Player Mapping Round - 2026-06-06

## Scope

This pass maps and reconstructs the Quake Live `CG_Player()` render path and the immediate media/callsite wiring around player sprites, model validation, and Red Rover infected-player presentation.

Owner binary: `assets/quakelive/baseq3/cgamex86.dll`

Primary evidence:

- `references/reverse-engineering/ghidra/cgamex86/metadata.txt`
- `references/reverse-engineering/ghidra/cgamex86/functions.csv`
- `references/reverse-engineering/ghidra/cgamex86/decompile_top_functions.c`
- `references/analysis/quakelive_symbol_aliases.json`
- `references/symbol-maps/cgame.json`

The Ghidra export reports `program_name=cgamex86.dll`, 751 functions, 2564 analysis symbols, and 180 decompiled functions.

## Function Map

| Retail address | Current name | Size | Notes |
| --- | --- | ---: | --- |
| `1003f020` | `CG_PlayerAnimation` | 275 | Called after `CG_PlayerAngles`, before sprite/shadow work. |
| `1003f350` | `CG_PlayerAngles` | 1389 | Owns legs, torso, and head axis setup. |
| `1003fd70` | `CG_PlayerFlag` | 970 | Carrier flag helper used by the player powerup lane. |
| `100405a0` | `CG_PlayerPowerups` | 937 | Called after weapon handling from `CG_Player`. |
| `10040870` | `CG_PlayerObjectiveSprite` | 1096 | Called after `CG_PlayerPowerups`. |
| `100411a0` | `CG_PlayerSprites` | 750 | Retail callsite is gated by the sprite cvar global. |
| `10041490` | `CG_PlayerShadow` | 407 | Feeds `RF_SHADOW_PLANE`. |
| `10041630` | `CG_PlayerSplash` | 560 | Runs after shadow setup. |
| `10041860` | `CG_AddRefEntityWithPowerups` | 393 | Submits legs, torso, and head. |
| `100419f0` | `CG_ApplyPlayerColors` | 397 | Runs immediately after clearing the three ref entities. |
| `10041b80` | `CG_Player` | 4372 | Main player render function for this pass. |
| `10042ca0` | `CG_ResetPlayerEntity` | 429 | Adjacent reset helper. |

## Observed Retail Flow

`FUN_10041b80` validates `clientNum`, returns for invalid clientinfo, sets `RF_THIRD_PERSON` for the local first-person entity, clears the legs/torso/head ref entities, then calls `CG_ApplyPlayerColors`, `CG_PlayerAngles`, and `CG_PlayerAnimation`.

The retail sprite call is conditional:

- Observed callsite: `if (DAT_10a6cf0c != 0) FUN_100411a0();`
- Source-side match: `cg_drawSprites` is already registered as a protected `0/1` cvar in `cg_main.c`.

After shadow, splash, Harvester token handling, and the player-model bounding-box scale lookup, retail checks all three clientinfo model handles and calls:

```c
CG_Error( "Invalid models for player entity" );
```

This happens before legs are submitted, replacing the older Quake III-style staged early returns for missing legs, torso, or head models.

The player-model bounding-box scale gate is:

- `cg_scalePlayerModelsToBB != 0`
- `ci->headOffset[0] != 1.0f`

Current source initialization already normalizes invalid/default model paths back to `1.0f`, so the helper now follows the observed retail non-default scale check rather than only accepting values above `1.0f`.

The tail of retail `CG_Player()` has a Red Rover infected branch:

- Gate: `gametype == GT_RED_ROVER`
- Gate: `customSettingsMask & CUSTOM_SETTING_INFECTED`
- Gate: `ci->team == TEAM_RED`
- Weapon subgate: `cent->currentState.weapon == WP_GAUNTLET`
- If all weapon gates pass, retail calls `CG_RegisterWeapon(WP_GAUNTLET)` instead of `CG_AddPlayerWeapon`.
- The common tail still calls `CG_PlayerPowerups` and `CG_PlayerObjectiveSprite`.
- For infected players, retail sets the same goo shader on torso, head, and legs, submits those three refs again, then adds a looping nightmare sound at the player origin.

## Media Wiring

The `CG_RegisterGraphics` decompile registers:

- `DAT_10a5f674 = trap_R_RegisterShader("powerups/goo")`

The `CG_RegisterSounds` Red Rover block registers:

- `DAT_10a5fb60 = trap_S_RegisterSound("sound/misc/nightmare.wav")`
- `DAT_10a5fb64 = trap_S_RegisterSound("sound/items/kamikazerespawn.wav")`

The current source already had the kamikaze respawn sound; this pass added the missing `gooShader` and `infectedLoopSound` handles and registrations.

## Source Reconstruction

Files changed in this pass:

- `src/code/cgame/cg_local.h`
  - Added `cgs.media.gooShader`.
  - Added `cgs.media.infectedLoopSound`.
- `src/code/cgame/cg_main.c`
  - Registered `powerups/goo`.
  - Registered `sound/misc/nightmare.wav` in the Red Rover/com_build sound block.
- `src/code/cgame/cg_players.c`
  - Matched the retail `ci->headOffset[0] != 1.0f` player-model scale gate.
  - Gated `CG_PlayerSprites` on `cg_drawSprites.integer`.
  - Added the retail fatal validation for missing legs, torso, or head models.
  - Removed the staged null-model early returns that retail no longer follows.
  - Added a Red Rover infected-player predicate.
  - Added the gauntlet-only `CG_RegisterWeapon(WP_GAUNTLET)` path.
  - Added the goo shell and looping nightmare sound submission at the retail tail point.

## Confidence

High confidence:

- `FUN_10041b80` is `CG_Player` from the symbol alias map, function map, call graph shape, and source-level behavior.
- `DAT_10a5f674` is the goo shader from the exact `powerups/goo` registration string and use as `customShader` on player parts.
- `DAT_10a5fb60` is the infected loop sound from the exact `sound/misc/nightmare.wav` registration string and `trap_S_AddLoopingSound` use.
- The Red Rover infected branch gates match existing source constants: `GT_RED_ROVER`, `CUSTOM_SETTING_INFECTED`, `TEAM_RED`, and `WP_GAUNTLET`.

Medium confidence:

- `DAT_10a6cf0c` is the registered `cg_drawSprites` vmCvar integer. The source cvar and callsite role match, but the data symbol itself is not yet named in the committed map.

Open questions for future passes:

- Validate every remaining `CG_PlayerSprites` award/friend/Red Rover marker branch against `FUN_100411a0`, especially any retail ordering differences.
- Map the remaining player adornment refs in the middle of `CG_Player()` for guard/scout/doubler/ammo/invulnerability/medkit effects at field-offset level.
- Consider promoting `DAT_10a6cf0c`, `DAT_10a5f674`, and `DAT_10a5fb60` in the symbol alias corpus after a dedicated symbol-map update pass.
