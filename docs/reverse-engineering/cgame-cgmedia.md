# cgame `cgMedia_t` Layout Map

This note maps the retail-compatible x86 layout of `cgMedia_t` used by
`cgamex86.dll` onto the current `src/code/cgame/cg_local.h` definition. The
goal is to pin the asset-handle slab by offset first, then attach the strongest
ownership signals from the retail registration paths and the main consumers in
`cgame`.

## Method

- Layout facts come from a local x86 record-layout dump of `cgMedia_t` using
  `clang -target i686-pc-windows-msvc -DID_INLINE=__inline -Xclang -fdump-record-layouts`
  against `src/code/cgame/cg_local.h`.
- Member ownership was cross-checked against the concrete registration paths in
  `src/code/cgame/cg_main.c` and `cg_weapons.c`, plus the main consumers in
  `cg_draw.c`, `cg_scoreboard.c`, `cg_newdraw.c`, `cg_players.c`,
  `cg_effects.c`, `cg_event.c`, `cg_ents.c`, and `cg_playerstate.c`.
- Retail parity was anchored against the already-promoted `cgame` recoveries
  for `CG_Init`, `CG_RegisterGraphics`, `CG_RegisterSounds`, and the recovered
  announcer-profile and ownerdraw chains in
  `docs/reverse-engineering/cgame-mapping.md`.
- Array members are mapped as single rows when the array itself is the stable
  member boundary and the element meanings are already obvious from the
  registration names or direct consumer loops.

## Hard Layout Facts

- `sizeof(cgMedia_t) = 0x6B8` (`1720`) on the retail-compatible x86 layout.
- `cgMedia_t` is a pure handle slab:
  - top-level members are `qhandle_t`, `sfxHandle_t`, or the embedded
    `cgAnnouncerSoundSet_t announcerSoundSets[ANNOUNCER_PROFILE_COUNT]`
  - there are no counters, pointers, or transient per-frame flags in this
    struct
- The primary writers are:
  - bootstrap `CG_Init` for the always-needed text/menu/loading handles
  - `CG_RegisterGraphics` for most shader/model/skin fields
  - `CG_RegisterSounds` for the sound fields and the announcer profile table
  - `CG_RegisterWeapon` via `CG_RegisterItemVisuals` for the late weapon/effect
    slots such as lightning, rail, and the explosion shaders
- The top-level active announcer handles at `0x04EC-0x0504` are derived state,
  not source storage: `CG_SetActiveAnnouncerProfile` copies or zeros them from
  `announcerSoundSets`.
- `CG_AssetCache` is not an owner of `cgMedia_t`; it fills the separate
  `cgDC.Assets` menu/UI cache.

## Bootstrap Text, Loading, And Main Menu Media

Retail `CG_Init` writes this entire prefix before the large sound/graphics
passes run. These handles are intentionally early because the loading screen,
console text, and HUD/menu bootstrap can need them before the rest of the map
media is ready.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x0000` | `charsetShader` | `qhandle_t` | Big console/HUD text atlas registered during `CG_Init`. |
| `0x0004` | `charsetProp` | `qhandle_t` | Main proportional menu font atlas. |
| `0x0008` | `charsetPropGlow` | `qhandle_t` | Glowing proportional menu font atlas. |
| `0x000C` | `charsetPropB` | `qhandle_t` | Alternate bold proportional font atlas. |
| `0x0010` | `whiteShader` | `qhandle_t` | Generic white fill shader used across HUD and debug draws. |
| `0x0014` | `loadingBackground` | `qhandle_t` | Loading-screen background image. |
| `0x0018` | `gameTypeBackground` | `qhandle_t` | Main-menu gametype background art. |
| `0x001C` | `logoBackground` | `qhandle_t` | Main-menu logo backing art. |
| `0x0020` | `qlLogo` | `qhandle_t` | Main-menu Quake Live logo art. |
| `0x0024` | `menuSmokeShader` | `qhandle_t` | Back-screen smoke overlay used by the retail menu/HUD bootstrap. |
| `0x0028` | `modifiedIcon` | `qhandle_t` | Modified-pak warning icon. |

## Teamplay, Objective, And Domination Media

This band is mostly `CG_RegisterGraphics` state and is heavily gated by
`cgs.gametype` plus `cg_buildScript`. The early CTF/1FCTF/Harvester/Obelisk
block and the domination block are structurally separate, which is visible in
both the source registration order and the x86 layout.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x002C` | `redCubeModel` | `qhandle_t` | Harvester red skull/orb world model. |
| `0x0030` | `blueCubeModel` | `qhandle_t` | Harvester blue skull/orb world model. |
| `0x0034` | `redCubeIcon` | `qhandle_t` | Harvester red skull HUD icon. |
| `0x0038` | `blueCubeIcon` | `qhandle_t` | Harvester blue skull HUD icon. |
| `0x003C` | `redFlagModel` | `qhandle_t` | Red flag world model. |
| `0x0040` | `blueFlagModel` | `qhandle_t` | Blue flag world model. |
| `0x0044` | `neutralFlagModel` | `qhandle_t` | Neutral one-flag model. |
| `0x0048` | `redFlagShader[3]` | `qhandle_t[3]` | Red flag-state icon strip for score/HUD flag status. |
| `0x0054` | `blueFlagShader[3]` | `qhandle_t[3]` | Blue flag-state icon strip for score/HUD flag status. |
| `0x0060` | `flagShader[4]` | `qhandle_t[4]` | One-flag icon strip used by the older 1F status path. |
| `0x0070` | `flagPoleModel` | `qhandle_t` | Flagpole model for the standing flag entity. |
| `0x0074` | `flagFlapModel` | `qhandle_t` | Flag cloth/flap model shared by team and neutral flags. |
| `0x0078` | `redFlagFlapSkin` | `qhandle_t` | Red flap skin. |
| `0x007C` | `blueFlagFlapSkin` | `qhandle_t` | Blue flap skin. |
| `0x0080` | `neutralFlagFlapSkin` | `qhandle_t` | Neutral flap skin. |
| `0x0084` | `redFlagBaseModel` | `qhandle_t` | Red flag base model. |
| `0x0088` | `blueFlagBaseModel` | `qhandle_t` | Blue flag base model. |
| `0x008C` | `neutralFlagBaseModel` | `qhandle_t` | Neutral flag base model. |
| `0x0090` | `overloadBaseModel` | `qhandle_t` | Obelisk base model. |
| `0x0094` | `overloadTargetModel` | `qhandle_t` | Obelisk target model. |
| `0x0098` | `overloadLightsModel` | `qhandle_t` | Obelisk light-ring model. |
| `0x009C` | `overloadEnergyModel` | `qhandle_t` | Obelisk energy shell model. |
| `0x00A0` | `harvesterModel` | `qhandle_t` | Harvester objective model. |
| `0x00A4` | `harvesterRedSkin` | `qhandle_t` | Harvester red skin. |
| `0x00A8` | `harvesterBlueSkin` | `qhandle_t` | Harvester blue skin. |
| `0x00AC` | `harvesterNeutralModel` | `qhandle_t` | Harvester neutral obelisk model. |
| `0x00B0` | `domPointModel` | `qhandle_t` | Domination control-point model. |
| `0x00B4` | `domPointSkinRed` | `qhandle_t` | Red domination-point skin. |
| `0x00B8` | `domPointSkinBlue` | `qhandle_t` | Blue domination-point skin. |
| `0x00BC` | `domPointSkinNeutral` | `qhandle_t` | Neutral domination-point skin. |
| `0x00C0` | `domCapShaders[5]` | `qhandle_t[5]` | Capture-state shader strip indexed by domination point state. |
| `0x00D4` | `domCapDistressShaders[5]` | `qhandle_t[5]` | Distress variant of the domination capture strip. |
| `0x00E8` | `domDefShaders[5]` | `qhandle_t[5]` | Defense-state shader strip indexed by domination point state. |
| `0x00FC` | `domDefDistressShaders[5]` | `qhandle_t[5]` | Distress variant of the domination defense strip. |

## General HUD, Gib, And Effect Utility Media

This band is mostly `CG_RegisterGraphics`, but the rail/lightning members are
special: they are late-owned by `CG_RegisterWeapon`, so a zero handle is legal
when the map never registers the corresponding weapon/item.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x0110` | `armorModel` | `qhandle_t` | Yellow armor world model used by pickup draws. |
| `0x0114` | `armorIcon` | `qhandle_t` | Armor HUD/pickup icon. |
| `0x0118` | `teamStatusBar` | `qhandle_t` | Team-color bar used by team HUD/status displays. |
| `0x011C` | `deferShader` | `qhandle_t` | Deferred-player placeholder image. |
| `0x0120` | `gibAbdomen` | `qhandle_t` | Gib chunk model. |
| `0x0124` | `gibArm` | `qhandle_t` | Gib chunk model. |
| `0x0128` | `gibChest` | `qhandle_t` | Gib chunk model. |
| `0x012C` | `gibFist` | `qhandle_t` | Gib chunk model. |
| `0x0130` | `gibFoot` | `qhandle_t` | Gib chunk model. |
| `0x0134` | `gibForearm` | `qhandle_t` | Gib chunk model. |
| `0x0138` | `gibIntestine` | `qhandle_t` | Gib chunk model. |
| `0x013C` | `gibLeg` | `qhandle_t` | Gib chunk model. |
| `0x0140` | `gibSkull` | `qhandle_t` | Gib chunk model. |
| `0x0144` | `gibBrain` | `qhandle_t` | Gib chunk model. |
| `0x0148` | `smoke2` | `qhandle_t` | Legacy shell/explode model slot preserved in the source media slab; the recovered retail-aligned gib fallback now uses standalone sphere/death-effect handles instead. |
| `0x014C` | `machinegunBrassModel` | `qhandle_t` | Machinegun brass ejection model. |
| `0x0150` | `shotgunBrassModel` | `qhandle_t` | Shotgun shell ejection model. |
| `0x0154` | `railRingsShader` | `qhandle_t` | Rail-disc ring shader written by weapon registration and consumed by rail/plasma trails. |
| `0x0158` | `railCoreShader` | `qhandle_t` | Rail core beam shader written by weapon registration. |
| `0x015C` | `lightningShader` | `qhandle_t` | Default lightning beam shader fallback when the active style slot is empty. |
| `0x0160` | `lightningStyleShaders[5]` | `qhandle_t[5]` | Cached lightning-style shader table; retail `CG_LightningBoltBeam` and the weapon beam path both index this from the active style and fall back to `lightningShader` only if the chosen slot is empty. |
| `0x0174` | `friendShader` | `qhandle_t` | Friendly-player float sprite. |
| `0x0178` | `frozenPlayerShader` | `qhandle_t` | Freeze-tag overlay shader for frozen players. |
| `0x017C` | `balloonShader` | `qhandle_t` | Chat balloon sprite. |
| `0x0180` | `connectionShader` | `qhandle_t` | Connection/interruption indicator shader. |
| `0x0184` | `selectShader` | `qhandle_t` | Generic HUD selection highlight shader. |
| `0x0188` | `viewBloodShader` | `qhandle_t` | Full-screen blood overlay. |
| `0x018C` | `tracerShader` | `qhandle_t` | Machinegun tracer shader. |
| `0x0190` | `crosshairShader[10]` | `qhandle_t[10]` | Crosshair atlas family indexed by `cg_drawCrosshair`. |
| `0x01B8` | `lagometerShader` | `qhandle_t` | Lagometer background/plot shader. |
| `0x01BC` | `backTileShader` | `qhandle_t` | Repeating 2D background tile shader. |
| `0x01C0` | `noammoShader` | `qhandle_t` | No-ammo icon shader. |
| `0x01C4` | `healthBar100` | `qhandle_t` | 100-health HUD bar art. |
| `0x01C8` | `healthBar200` | `qhandle_t` | 200-health HUD bar art. |
| `0x01CC` | `armorBar100` | `qhandle_t` | 100-armor HUD bar art. |
| `0x01D0` | `armorBar200` | `qhandle_t` | 200-armor HUD bar art. |
| `0x01D4` | `healthTick100` | `qhandle_t` | 100-health tick overlay. |
| `0x01D8` | `healthTick200` | `qhandle_t` | 200-health tick overlay. |
| `0x01DC` | `armorTick100` | `qhandle_t` | 100-armor tick overlay. |
| `0x01E0` | `armorTick200` | `qhandle_t` | 200-armor tick overlay. |
| `0x01E4` | `smokePuffShader` | `qhandle_t` | Generic smoke puff shader. |
| `0x01E8` | `smokePuffRageProShader` | `qhandle_t` | Alternate smoke puff shader. |
| `0x01EC` | `shotgunSmokePuffShader` | `qhandle_t` | Shotgun impact puff shader. |
| `0x01F0` | `plasmaBallShader` | `qhandle_t` | Plasmagun projectile sprite shader. |
| `0x01F4` | `waterBubbleShader` | `qhandle_t` | Water bubble particle shader. |
| `0x01F8` | `bloodTrailShader` | `qhandle_t` | Blood trail particle shader. |
| `0x01FC` | `nailPuffShader` | `qhandle_t` | Nailgun trail puff shader. |
| `0x0200` | `blueProxMine` | `qhandle_t` | Prox mine model/shader handle used by the blue mine path. |
| `0x0204` | `numberShaders[11]` | `qhandle_t[11]` | Numeric HUD/scoreboard digit strip including minus. |
| `0x0230` | `shadowMarkShader` | `qhandle_t` | Blob shadow/decal shader. |
| `0x0234` | `botSkillShaders[5]` | `qhandle_t[5]` | Bot skill icon strip. |

## Marks, Powerups, Weapon Effects, Scoreboard Art, And Medal Art

The front half of this band is mostly render/effect media. The explosion and
beam subset is partly item-gated through `CG_RegisterWeapon`, while the
scoreboard and medal art is unconditional `CG_RegisterGraphics` state.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x0248` | `wakeMarkShader` | `qhandle_t` | Water wake decal shader. |
| `0x024C` | `bloodMarkShader` | `qhandle_t` | Blood splat decal shader. |
| `0x0250` | `bulletMarkShader` | `qhandle_t` | Bullet impact decal shader. |
| `0x0254` | `burnMarkShader` | `qhandle_t` | Burn/scorch decal shader. |
| `0x0258` | `holeMarkShader` | `qhandle_t` | Large hole decal shader. |
| `0x025C` | `energyMarkShader` | `qhandle_t` | Plasma/energy impact decal shader. |
| `0x0260` | `quadShader` | `qhandle_t` | Quad damage player shader. |
| `0x0264` | `redQuadShader` | `qhandle_t` | Team-mode alternate quad-style shader. |
| `0x0268` | `quadWeaponShader` | `qhandle_t` | Quad damage weapon glow shader. |
| `0x026C` | `invisShader` | `qhandle_t` | Invisibility powerup shader. |
| `0x0270` | `regenShader` | `qhandle_t` | Regeneration player shader. |
| `0x0274` | `battleSuitShader` | `qhandle_t` | Battlesuit player shader. |
| `0x0278` | `battleWeaponShader` | `qhandle_t` | Battlesuit weapon shader. |
| `0x027C` | `hastePuffShader` | `qhandle_t` | Haste smoke-puff shader. |
| `0x0280` | `redKamikazeShader` | `qhandle_t` | Team-colored kamikaze effect shader. |
| `0x0284` | `blueKamikazeShader` | `qhandle_t` | Team-colored kamikaze effect shader. |
| `0x0288` | `bulletFlashModel` | `qhandle_t` | Generic weapon-hit flash model. |
| `0x028C` | `ringFlashModel` | `qhandle_t` | Ring-style hit flash model. |
| `0x0290` | `dishFlashModel` | `qhandle_t` | Dish-style hit flash model. |
| `0x0294` | `lightningExplosionModel` | `qhandle_t` | Lightning impact/crackle model registered by the lightning weapon path. |
| `0x0298` | `railExplosionShader` | `qhandle_t` | Rail explosion shader written by weapon registration. |
| `0x029C` | `plasmaExplosionShader` | `qhandle_t` | Plasma explosion shader written by weapon registration. |
| `0x02A0` | `bulletExplosionShader` | `qhandle_t` | Bullet explosion shader written by weapon registration. |
| `0x02A4` | `rocketExplosionShader` | `qhandle_t` | Rocket explosion shader written by weapon registration. |
| `0x02A8` | `grenadeExplosionShader` | `qhandle_t` | Grenade/prox explosion shader written by weapon registration. |
| `0x02AC` | `bfgExplosionShader` | `qhandle_t` | BFG explosion shader written by weapon registration. |
| `0x02B0` | `bloodExplosionShader` | `qhandle_t` | Blood explosion effect shader. |
| `0x02B4` | `teleportEffectModel` | `qhandle_t` | Teleport pop model. |
| `0x02B8` | `teleportEffectShader` | `qhandle_t` | Legacy teleport shader slot; present in layout but not strongly revalidated in the current tree. |
| `0x02BC` | `kamikazeEffectModel` | `qhandle_t` | Kamikaze explosion model. |
| `0x02C0` | `kamikazeShockWave` | `qhandle_t` | Kamikaze shockwave model. |
| `0x02C4` | `kamikazeHeadModel` | `qhandle_t` | Kamikaze head model. |
| `0x02C8` | `kamikazeHeadTrail` | `qhandle_t` | Kamikaze trail model. |
| `0x02CC` | `guardPowerupModel` | `qhandle_t` | Guard powerup attachment model. |
| `0x02D0` | `scoutPowerupModel` | `qhandle_t` | Scout powerup attachment model. |
| `0x02D4` | `doublerPowerupModel` | `qhandle_t` | Doubler powerup attachment model. |
| `0x02D8` | `ammoRegenPowerupModel` | `qhandle_t` | Ammo-regen powerup attachment model. |
| `0x02DC` | `invulnerabilityImpactModel` | `qhandle_t` | Invulnerability impact model. |
| `0x02E0` | `invulnerabilityJuicedModel` | `qhandle_t` | Invulnerability juiced model. |
| `0x02E4` | `medkitUsageModel` | `qhandle_t` | Medkit/regen usage model. |
| `0x02E8` | `dustPuffShader` | `qhandle_t` | Dust puff shader; currently registered to the same asset as `hastePuffShader`. |
| `0x02EC` | `heartShader` | `qhandle_t` | Selected-health/heart HUD icon. |
| `0x02F0` | `invulnerabilityPowerupModel` | `qhandle_t` | Main invulnerability shield model. |
| `0x02F4` | `scoreboardName` | `qhandle_t` | Legacy scoreboard name-column header art. |
| `0x02F8` | `scoreboardPing` | `qhandle_t` | Legacy scoreboard ping-column header art. |
| `0x02FC` | `scoreboardScore` | `qhandle_t` | Legacy scoreboard score-column header art. |
| `0x0300` | `scoreboardTime` | `qhandle_t` | Legacy scoreboard time-column header art. |
| `0x0304` | `scoreboxSpecShader` | `qhandle_t` | Spectator scorebox background art. |
| `0x0308` | `scoreboxFollowShader` | `qhandle_t` | Follow scorebox background art. |
| `0x030C` | `inkFadeLeftShader` | `qhandle_t` | Left scoreboard ink-fade overlay. |
| `0x0310` | `inkFadeRightShader` | `qhandle_t` | Right scoreboard ink-fade overlay. |
| `0x0314` | `medalImpressive` | `qhandle_t` | Reward medal icon. |
| `0x0318` | `medalExcellent` | `qhandle_t` | Reward medal icon. |
| `0x031C` | `medalGauntlet` | `qhandle_t` | Reward medal icon. |
| `0x0320` | `medalDefend` | `qhandle_t` | Reward medal icon. |
| `0x0324` | `medalAssist` | `qhandle_t` | Reward medal icon. |
| `0x0328` | `medalCapture` | `qhandle_t` | Reward medal icon. |
| `0x032C` | `medalMidair` | `qhandle_t` | Reward medal icon. |
| `0x0330` | `medalPerfect` | `qhandle_t` | Reward medal icon. |
| `0x0334` | `medalQuadGod` | `qhandle_t` | Reward medal icon. |
| `0x0338` | `medalRampage` | `qhandle_t` | Reward medal icon. |
| `0x033C` | `medalRevenge` | `qhandle_t` | Reward medal icon. |
| `0x0340` | `medalPerforated` | `qhandle_t` | Reward medal icon. |
| `0x0344` | `medalHeadshot` | `qhandle_t` | Reward medal icon. |
| `0x0348` | `medalFirstFrag` | `qhandle_t` | Reward medal icon used by the first-frag queue. |

## Core Sounds And Weapon Impact Sounds

This prefix sound block is almost entirely `CG_RegisterSounds`. It mixes always
present UI/item sounds, the material footstep matrix, weapon impact variants,
and the basic world/player sounds.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x034C` | `quadSound` | `sfxHandle_t` | Quad pickup/activation sound. |
| `0x0350` | `tracerSound` | `sfxHandle_t` | Near-miss tracer flyby sound. |
| `0x0354` | `selectSound` | `sfxHandle_t` | Weapon selection sound. |
| `0x0358` | `useNothingSound` | `sfxHandle_t` | Empty-use feedback sound. |
| `0x035C` | `wearOffSound` | `sfxHandle_t` | Powerup wear-off sound. |
| `0x0360` | `footsteps[FOOTSTEP_TOTAL][4]` | `sfxHandle_t[7][4]` | Material/variant footstep matrix. |
| `0x03D0` | `sfx_lghit1` | `sfxHandle_t` | Lightning hit variant. |
| `0x03D4` | `sfx_lghit2` | `sfxHandle_t` | Lightning hit variant. |
| `0x03D8` | `sfx_lghit3` | `sfxHandle_t` | Lightning hit variant. |
| `0x03DC` | `sfx_ric1` | `sfxHandle_t` | Bullet ricochet variant. |
| `0x03E0` | `sfx_ric2` | `sfxHandle_t` | Bullet ricochet variant. |
| `0x03E4` | `sfx_ric3` | `sfxHandle_t` | Bullet ricochet variant. |
| `0x03E8` | `sfx_railg` | `sfxHandle_t` | Railgun impact sound. |
| `0x03EC` | `sfx_rockexp` | `sfxHandle_t` | Rocket explosion sound. |
| `0x03F0` | `sfx_plasmaexp` | `sfxHandle_t` | Plasma explosion sound. |
| `0x03F4` | `sfx_proxexp` | `sfxHandle_t` | Prox-mine explosion sound. |
| `0x03F8` | `sfx_nghit` | `sfxHandle_t` | Nail impact sound. |
| `0x03FC` | `sfx_nghitflesh` | `sfxHandle_t` | Nail flesh-hit sound. |
| `0x0400` | `sfx_nghitmetal` | `sfxHandle_t` | Nail metal-hit sound. |
| `0x0404` | `sfx_chghit` | `sfxHandle_t` | Chaingun impact sound. |
| `0x0408` | `sfx_chghitflesh` | `sfxHandle_t` | Chaingun flesh-hit sound. |
| `0x040C` | `sfx_chghitmetal` | `sfxHandle_t` | Chaingun metal-hit sound. |
| `0x0410` | `kamikazeExplodeSound` | `sfxHandle_t` | Kamikaze explosion sound. |
| `0x0414` | `kamikazeImplodeSound` | `sfxHandle_t` | Kamikaze implode sound. |
| `0x0418` | `kamikazeFarSound` | `sfxHandle_t` | Far kamikaze detonation sound. |
| `0x041C` | `useInvulnerabilitySound` | `sfxHandle_t` | Invulnerability activation sound. |
| `0x0420` | `invulnerabilityImpactSound1` | `sfxHandle_t` | Invulnerability impact variant. |
| `0x0424` | `invulnerabilityImpactSound2` | `sfxHandle_t` | Invulnerability impact variant. |
| `0x0428` | `invulnerabilityImpactSound3` | `sfxHandle_t` | Invulnerability impact variant. |
| `0x042C` | `invulnerabilityJuicedSound` | `sfxHandle_t` | Invulnerability juiced sound. |
| `0x0430` | `obeliskHitSound1` | `sfxHandle_t` | Obelisk hit variant. |
| `0x0434` | `obeliskHitSound2` | `sfxHandle_t` | Obelisk hit variant. |
| `0x0438` | `obeliskHitSound3` | `sfxHandle_t` | Obelisk hit variant. |
| `0x043C` | `obeliskRespawnSound` | `sfxHandle_t` | Obelisk respawn sound. |
| `0x0440` | `winnerSound` | `sfxHandle_t` | Win/intermission voice cue. |
| `0x0444` | `loserSound` | `sfxHandle_t` | Loss/intermission voice cue. |
| `0x0448` | `youSuckSound` | `sfxHandle_t` | Losing taunt voice cue. |
| `0x044C` | `gibSound` | `sfxHandle_t` | Gib burst sound. |
| `0x0450` | `gibBounce1Sound` | `sfxHandle_t` | Gib bounce variant. |
| `0x0454` | `gibBounce2Sound` | `sfxHandle_t` | Gib bounce variant. |
| `0x0458` | `gibBounce3Sound` | `sfxHandle_t` | Gib bounce variant. |
| `0x045C` | `teleInSound` | `sfxHandle_t` | Teleport-in sound. |
| `0x0460` | `teleOutSound` | `sfxHandle_t` | Teleport-out sound. |
| `0x0464` | `noAmmoSound` | `sfxHandle_t` | No-ammo feedback sound. |
| `0x0468` | `respawnSound` | `sfxHandle_t` | Respawn sound. |
| `0x046C` | `talkSound` | `sfxHandle_t` | Chat/talk indicator sound. |
| `0x0470` | `landSound` | `sfxHandle_t` | Landing sound. |
| `0x0474` | `fallSound` | `sfxHandle_t` | Fall damage sound. |
| `0x0478` | `jumpPadSound` | `sfxHandle_t` | Jumppad launch sound. |

## Announcer Profile Cache And Active Mirrors

The embedded profile table is the persistent storage. The seven scalar handles
after it are the currently active resolved voices for the selected announcer.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x047C` | `announcerSoundSets[ANNOUNCER_PROFILE_COUNT]` | `cgAnnouncerSoundSet_t[4]` | Persistent per-profile countdown/frag announcer table. |
| `0x04EC` | `oneMinuteSound` | `sfxHandle_t` | Active one-minute warning voice handle. |
| `0x04F0` | `fiveMinuteSound` | `sfxHandle_t` | Active five-minute warning voice handle. |
| `0x04F4` | `suddenDeathSound` | `sfxHandle_t` | Active sudden-death voice handle. |
| `0x04F8` | `overtimeSound` | `sfxHandle_t` | Active overtime voice handle. |
| `0x04FC` | `threeFragSound` | `sfxHandle_t` | Active three-frags-left voice handle. |
| `0x0500` | `twoFragSound` | `sfxHandle_t` | Active two-frags-left voice handle. |
| `0x0504` | `oneFragSound` | `sfxHandle_t` | Active one-frag-left voice handle. |

## Reward, Vote, Teamplay, And Countdown Sounds

This tail is still `CG_RegisterSounds`, but it is behaviorally more diverse:
reward queues, hit feedback, vote cues, water/item loops, teamplay callouts,
race beeps, and the standard countdown voices all live here.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x0508` | `hitSound` | `sfxHandle_t` | Generic hit confirmation sound. |
| `0x050C` | `hitSoundHighArmor` | `sfxHandle_t` | High-armor hit confirmation sound. |
| `0x0510` | `hitSoundLowArmor` | `sfxHandle_t` | Low-armor hit confirmation sound. |
| `0x0514` | `hitTeamSound` | `sfxHandle_t` | Friendly-fire/team-hit confirmation sound. |
| `0x0518` | `impressiveSound` | `sfxHandle_t` | Reward voice cue. |
| `0x051C` | `impressiveSound2` | `sfxHandle_t` | Reward voice cue variant. |
| `0x0520` | `impressiveSound3` | `sfxHandle_t` | Reward voice cue variant. |
| `0x0524` | `excellentSound` | `sfxHandle_t` | Reward voice cue. |
| `0x0528` | `deniedSound` | `sfxHandle_t` | Reward voice cue. |
| `0x052C` | `humiliationSound` | `sfxHandle_t` | Reward voice cue. |
| `0x0530` | `assistSound` | `sfxHandle_t` | Reward voice cue. |
| `0x0534` | `defendSound` | `sfxHandle_t` | Reward voice cue. |
| `0x0538` | `firstImpressiveSound` | `sfxHandle_t` | First-event reward voice cue. |
| `0x053C` | `firstExcellentSound` | `sfxHandle_t` | First-event reward voice cue. |
| `0x0540` | `firstHumiliationSound` | `sfxHandle_t` | First-event reward voice cue. |
| `0x0544` | `midairSound` | `sfxHandle_t` | Midair reward voice cue. |
| `0x0548` | `midairSound2` | `sfxHandle_t` | Midair reward voice cue variant. |
| `0x054C` | `midairSound3` | `sfxHandle_t` | Midair reward voice cue variant. |
| `0x0550` | `perfectSound` | `sfxHandle_t` | Reward voice cue. |
| `0x0554` | `quadGodSound` | `sfxHandle_t` | Reward voice cue. |
| `0x0558` | `rampageSound` | `sfxHandle_t` | Reward voice cue. |
| `0x055C` | `revengeSound` | `sfxHandle_t` | Reward voice cue. |
| `0x0560` | `perforatedSound` | `sfxHandle_t` | Reward voice cue. |
| `0x0564` | `headshotSound` | `sfxHandle_t` | Reward voice cue. |
| `0x0568` | `firstFragSound` | `sfxHandle_t` | First-frag reward voice cue. |
| `0x056C` | `takenLeadSound` | `sfxHandle_t` | Lead-change voice cue. |
| `0x0570` | `tiedLeadSound` | `sfxHandle_t` | Lead-change voice cue. |
| `0x0574` | `lostLeadSound` | `sfxHandle_t` | Lead-change voice cue. |
| `0x0578` | `voteNow` | `sfxHandle_t` | Vote-start sound. |
| `0x057C` | `votePassed` | `sfxHandle_t` | Vote-passed sound. |
| `0x0580` | `voteFailed` | `sfxHandle_t` | Vote-failed sound. |
| `0x0584` | `watrInSound` | `sfxHandle_t` | Water enter sound. |
| `0x0588` | `watrOutSound` | `sfxHandle_t` | Water exit sound. |
| `0x058C` | `watrUnSound` | `sfxHandle_t` | Underwater ambient sound. |
| `0x0590` | `flightSound` | `sfxHandle_t` | Flight powerup loop/active sound. |
| `0x0594` | `medkitSound` | `sfxHandle_t` | Medkit use sound. |
| `0x0598` | `weaponHoverSound` | `sfxHandle_t` | Weapon-hover ambient sound. |
| `0x059C` | `captureAwardSound` | `sfxHandle_t` | Team capture reward sound. |
| `0x05A0` | `redScoredSound` | `sfxHandle_t` | Red team scored callout. |
| `0x05A4` | `blueScoredSound` | `sfxHandle_t` | Blue team scored callout. |
| `0x05A8` | `redLeadsSound` | `sfxHandle_t` | Red team leads callout. |
| `0x05AC` | `blueLeadsSound` | `sfxHandle_t` | Blue team leads callout. |
| `0x05B0` | `teamsTiedSound` | `sfxHandle_t` | Teams tied callout. |
| `0x05B4` | `captureYourTeamSound` | `sfxHandle_t` | Your team captured callout. |
| `0x05B8` | `captureOpponentSound` | `sfxHandle_t` | Opponent captured callout. |
| `0x05BC` | `returnYourTeamSound` | `sfxHandle_t` | Your team returned callout. |
| `0x05C0` | `returnOpponentSound` | `sfxHandle_t` | Opponent returned callout. |
| `0x05C4` | `takenYourTeamSound` | `sfxHandle_t` | Your team took flag callout. |
| `0x05C8` | `takenOpponentSound` | `sfxHandle_t` | Opponent took flag callout. |
| `0x05CC` | `redFlagReturnedSound` | `sfxHandle_t` | Red flag returned callout. |
| `0x05D0` | `blueFlagReturnedSound` | `sfxHandle_t` | Blue flag returned callout. |
| `0x05D4` | `neutralFlagReturnedSound` | `sfxHandle_t` | Neutral flag returned callout. |
| `0x05D8` | `enemyTookYourFlagSound` | `sfxHandle_t` | Enemy took your flag callout. |
| `0x05DC` | `enemyTookTheFlagSound` | `sfxHandle_t` | Enemy took the neutral flag callout. |
| `0x05E0` | `yourTeamTookEnemyFlagSound` | `sfxHandle_t` | Your team took enemy flag callout. |
| `0x05E4` | `yourTeamTookTheFlagSound` | `sfxHandle_t` | Your team took the neutral flag callout. |
| `0x05E8` | `youHaveFlagSound` | `sfxHandle_t` | Local flag carrier callout. |
| `0x05EC` | `yourBaseIsUnderAttackSound` | `sfxHandle_t` | Obelisk/base under attack callout. |
| `0x05F0` | `holyShitSound` | `sfxHandle_t` | Holy-shit reward voice cue. |
| `0x05F4` | `dominationDistressSound` | `sfxHandle_t` | Domination distress callout. |
| `0x05F8` | `raceStartBeep` | `sfxHandle_t` | Race start cue. |
| `0x05FC` | `raceCheckpointBeep` | `sfxHandle_t` | Race checkpoint cue. |
| `0x0600` | `raceFinishBeep` | `sfxHandle_t` | Race finish cue. |
| `0x0604` | `count3Sound` | `sfxHandle_t` | Countdown voice cue. |
| `0x0608` | `count2Sound` | `sfxHandle_t` | Countdown voice cue. |
| `0x060C` | `count1Sound` | `sfxHandle_t` | Countdown voice cue. |
| `0x0610` | `countFightSound` | `sfxHandle_t` | Fight callout. |
| `0x0614` | `countPrepareSound` | `sfxHandle_t` | Prepare callout. |

## Order, Race, Cursor, And Hazard Tail

The final band mixes team-order/statusbar art, race HUD art, the menu-edit
cursor triplet, the small extra item/weapon sounds, and the damage/hazard
icons used by the modern HUD.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x0618` | `patrolShader` | `qhandle_t` | Team-order/statusbar icon. |
| `0x061C` | `assaultShader` | `qhandle_t` | Team-order/statusbar icon. |
| `0x0620` | `campShader` | `qhandle_t` | Team-order/statusbar icon. |
| `0x0624` | `followShader` | `qhandle_t` | Team-order/statusbar icon. |
| `0x0628` | `defendShader` | `qhandle_t` | Team-order/statusbar icon. |
| `0x062C` | `teamLeaderShader` | `qhandle_t` | Team leader/status icon. |
| `0x0630` | `retrieveShader` | `qhandle_t` | Team-order/statusbar icon. |
| `0x0634` | `escortShader` | `qhandle_t` | Team-order/statusbar icon. |
| `0x0638` | `flagShaders[3]` | `qhandle_t[3]` | Modern statusbar flag-state icon strip. |
| `0x0644` | `raceStartShader` | `qhandle_t` | Race HUD start marker art. |
| `0x0648` | `raceCheckpointShader` | `qhandle_t` | Race HUD checkpoint marker art. |
| `0x064C` | `raceFinishShader` | `qhandle_t` | Race HUD finish marker art. |
| `0x0650` | `countPrepareTeamSound` | `sfxHandle_t` | Team-mode prepare callout. |
| `0x0654` | `ammoregenSound` | `sfxHandle_t` | Ammo regeneration powerup sound. |
| `0x0658` | `doublerSound` | `sfxHandle_t` | Doubler powerup sound. |
| `0x065C` | `guardSound` | `sfxHandle_t` | Guard powerup sound. |
| `0x0660` | `scoutSound` | `sfxHandle_t` | Scout powerup sound. |
| `0x0664` | `cursor` | `qhandle_t` | Primary HUD/menu edit cursor. |
| `0x0668` | `selectCursor` | `qhandle_t` | Selection cursor art. |
| `0x066C` | `sizeCursor` | `qhandle_t` | Resize cursor art. |
| `0x0670` | `regenSound` | `sfxHandle_t` | Regeneration pickup/activation sound. |
| `0x0674` | `protectSound` | `sfxHandle_t` | Protection pickup/activation sound. |
| `0x0678` | `n_healthSound` | `sfxHandle_t` | Mega/health item pickup sound. |
| `0x067C` | `hgrenb1aSound` | `sfxHandle_t` | Grenade bounce sound variant. |
| `0x0680` | `hgrenb2aSound` | `sfxHandle_t` | Grenade bounce sound variant. |
| `0x0684` | `wstbimplSound` | `sfxHandle_t` | Prox-mine impact sound variant. |
| `0x0688` | `wstbimpmSound` | `sfxHandle_t` | Prox-mine impact sound variant. |
| `0x068C` | `wstbimpdSound` | `sfxHandle_t` | Prox-mine impact sound variant. |
| `0x0690` | `wstbactvSound` | `sfxHandle_t` | Prox-mine activation sound. |
| `0x0694` | `waterIcon` | `qhandle_t` | Water damage/hazard icon. |
| `0x0698` | `slimeIcon` | `qhandle_t` | Slime damage/hazard icon. |
| `0x069C` | `lavaIcon` | `qhandle_t` | Lava damage/hazard icon. |
| `0x06A0` | `crushIcon` | `qhandle_t` | Crush damage icon. |
| `0x06A4` | `telefragIcon` | `qhandle_t` | Telefrag damage icon. |
| `0x06A8` | `fallingIcon` | `qhandle_t` | Falling damage icon. |
| `0x06AC` | `suicideIcon` | `qhandle_t` | Suicide/skull damage icon. |
| `0x06B0` | `kamikazeIcon` | `qhandle_t` | Kamikaze damage/status icon. |
| `0x06B4` | `juicedIcon` | `qhandle_t` | Juiced/invulnerability status icon. |

## Embedded `cgAnnouncerSoundSet_t`

The nested announcer entry is small enough to map directly here. The x86 layout
is stable and `CG_SetActiveAnnouncerProfile` copies these members into the
active mirrors at `0x04EC-0x0504`.

- `sizeof(cgAnnouncerSoundSet_t) = 0x1C`
- `announcerSoundSets` starts at `cgMedia_t + 0x047C`
- The four retail entries are:
  - `ANNOUNCER_PROFILE_DISABLED`
  - `ANNOUNCER_PROFILE_DEFAULT`
  - `ANNOUNCER_PROFILE_VADRIGAR`
  - `ANNOUNCER_PROFILE_DAEMIA`

| Relative offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x00` | `oneMinuteSound` | `sfxHandle_t` | Per-profile one-minute warning voice handle. |
| `0x04` | `fiveMinuteSound` | `sfxHandle_t` | Per-profile five-minute warning voice handle. |
| `0x08` | `suddenDeathSound` | `sfxHandle_t` | Per-profile sudden-death voice handle. |
| `0x0C` | `overtimeSound` | `sfxHandle_t` | Per-profile overtime voice handle. |
| `0x10` | `oneFragSound` | `sfxHandle_t` | Per-profile one-frag-left voice handle. |
| `0x14` | `twoFragSound` | `sfxHandle_t` | Per-profile two-frags-left voice handle. |
| `0x18` | `threeFragSound` | `sfxHandle_t` | Per-profile three-frags-left voice handle. |

## Ownership Notes And Weak Fields

- `cgMedia_t` is a registration cache, not a live gameplay-state struct. The
  handles are usually written once during init or item registration, then read
  by render/event/HUD code for the rest of the session.
- The weapon/effect subset is deliberately later than the rest of the graphics
  slab. `lightningShader`, `lightningStyleShaders`, `lightningExplosionModel`,
  `railRingsShader`, `railCoreShader`, and the main explosion shaders are
  owned by `CG_RegisterWeapon` through `CG_RegisterItemVisuals`, so they only
  become non-zero for weapons/items that the current map actually registers.
- `announcerSoundSets` is the durable profile store. The top-level
  `oneMinuteSound`, `fiveMinuteSound`, `suddenDeathSound`, `overtimeSound`,
  `threeFragSound`, `twoFragSound`, and `oneFragSound` are just the active
  resolved handles for the currently selected announcer profile.
- `flagShader[4]` and `flagShaders[3]` are different bands on purpose:
  - `flagShader[4]` is the older one-flag/legacy icon strip near the early CTF
    media
  - `flagShaders[3]` is the later statusbar/team HUD strip
- `CG_AssetCache` is a separate UI concern. It fills `cgDC.Assets` rather than
  any part of `cgs.media`.
- The cold or inherited members should stay explicit instead of being renamed
  away:
  - `bloodSprayShaders[4]` is the DLC-gated blood-hit shader fanout consumed by
    retail `CG_Bleed`; `bloodExplosionShader` stays registered as a separate
    media slot and is not the retail blood-hit burst path
  - `smoke2` is still structurally live, but it now sits alongside a more
    accurate retail gib fallback that uses `models/gibs/sphere.md3` plus
    `deathEffect` and `gfx/misc/tracer` rather than the old source-only smoke
    burst
  - `teleportEffectShader` is present in the layout but currently lacks a
    strong writer/consumer chain in the open tree
  - `dustPuffShader` currently aliases the same registered asset as
    `hastePuffShader`
