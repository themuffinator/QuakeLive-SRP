# cgame `clientInfo_t` Layout Map

This note maps the retail-compatible x86 layout of `clientInfo_t` used by
`cgamex86.dll` onto the current `src/code/cgame/cg_local.h` definition. The
goal is to separate hard layout facts from the main ownership bands: configstring
identity parsing, live scoreboard/team-overlay mirrors, deferred model loading,
and the render/animation cache that `CG_Player`, `CG_DrawHead`, and related
paths reuse.

## Method

- Layout facts come from a local x86 record-layout dump of `clientInfo_t` and
  `animation_t` using
  `clang -target i686-pc-windows-msvc -DID_INLINE=__inline -Xclang -fdump-record-layouts`
  against `src/code/cgame/cg_local.h`.
- Member ownership was cross-checked against the client-info pipeline in
  `src/code/cgame/cg_players.c`, the live mirror writers in
  `src/code/cgame/cg_servercmds.c`, and the main consumers in
  `src/code/cgame/cg_draw.c`, `src/code/cgame/cg_scoreboard.c`,
  `src/code/cgame/cg_newdraw.c`, `src/code/cgame/cg_event.c`, and
  `src/code/cgame/cg_weapons.c`.
- Retail parity was cross-checked against the committed cgame metadata plus the
  HLIL/Ghidra client-load string cluster around the model/sound registration
  path: `models/players/%s/lower.md3`, `models/players/%s/upper.md3`,
  `models/players/%s/head.md3`, `models/players/%s/animation.cfg`,
  `sound/player/%s/%s`, `tag_flag`, and the matching failure/defer strings.
- The surrounding retail subsystem is already anchored by the recovered
  `CG_RegisterClients`, `CG_LoadDeferredPlayers`, and `CG_ServerCommand`
  recoveries in `docs/reverse-engineering/cgame-mapping.md`.

## Hard Layout Facts

- `sizeof(animation_t) = 0x1C` (`28`).
- `sizeof(clientInfo_t) = 0x704` (`1796`).
- `cgs_t` embeds `clientinfo[MAX_CLIENTS]` at `0x0F0DC` with stride `0x704`.
- The top-level banding is:
  - identity, colors, and override provenance at `0x000-0x0B8`
  - live scoreboard/team-overlay mirrors at `0x0BC-0x0F4`
  - source model strings and deferred-load state at `0x0F8-0x244`
  - animation metadata and render/media cache at `0x248-0x704`

## Identity, Colors, And Override Provenance

These members are built primarily by `CG_NewClientInfo`, then normalized by the
override helpers before the finished record is copied into `cgs.clientinfo[]`.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x000` | `infoValid` | `qboolean` | Primary validity gate checked by render, HUD, and scoreboard consumers before any client-specific work happens. |
| `0x004` | `name` | `char[MAX_QPATH]` | Cached display name parsed from the player configstring. |
| `0x044` | `team` | `team_t` | Cached team classification used across scoreboard, crosshair-name, order, and render logic. |
| `0x048` | `botSkill` | `int` | Bot difficulty marker used by scoreboard bot-skill icons. |
| `0x04C` | `color1` | `vec3_t` | Base user color from configstring key `c1`. |
| `0x058` | `color2` | `vec3_t` | Base user color from configstring key `c2`. |
| `0x064` | `headColor` | `vec3_t` | Final resolved head tint after overrides. |
| `0x070` | `upperColor` | `vec3_t` | Final resolved torso/upper-body tint after overrides. |
| `0x07C` | `lowerColor` | `vec3_t` | Final resolved legs/lower-body tint after overrides. |
| `0x088` | `weaponPrimaryColor` | `vec3_t` | Primary weapon/rail color resolved from the same override path. |
| `0x094` | `weaponSecondaryColor` | `vec3_t` | Secondary weapon/rail color resolved from the same override path. |
| `0x0A0` | `headColorForced` | `qboolean` | Live tint latch checked by head/dead-body render paths. |
| `0x0A4` | `upperColorForced` | `qboolean` | Live tint latch checked by torso/dead-body render paths. |
| `0x0A8` | `lowerColorForced` | `qboolean` | Live tint latch checked by legs/dead-body render paths. |
| `0x0AC` | `weaponColorForced` | `qboolean` | Override provenance flag for weapon colors; the render paths consume the resolved colors directly rather than this flag. |
| `0x0B0` | `modelForced` | `qboolean` | Override provenance flag noting that the body model name was forced. |
| `0x0B4` | `headModelForced` | `qboolean` | Override provenance flag noting that the head model name was forced. |
| `0x0B8` | `skinForced` | `qboolean` | Override provenance flag noting that body/head skins were forced. |

## Live Match And Team-Overlay Mirror

This band mixes configstring-derived ladder/team metadata with values mirrored
later by score and team-info server commands.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x0BC` | `score` | `int` | Cached score mirror written by score server commands; used most clearly by the giant FFA scoreboard path. |
| `0x0C0` | `location` | `int` | Team-overlay location index consumed by scoreboard and HUD location displays. |
| `0x0C4` | `health` | `int` | Team-overlay health mirror used by teammate HUDs and spectator overlays. |
| `0x0C8` | `armor` | `int` | Team-overlay armor mirror used by teammate HUDs and spectator overlays. |
| `0x0CC` | `curWeapon` | `int` | Team-overlay current-weapon index used by teammate HUD icon draws. |
| `0x0D0` | `handicap` | `int` | Parsed handicap percentage used by the scoreboard. |
| `0x0D4` | `wins` | `int` | Parsed win count used by tournament/placement HUD displays. |
| `0x0D8` | `losses` | `int` | Parsed loss count used by tournament scoreboard displays. |
| `0x0DC` | `teamTask` | `int` | Team-order/task classification used by scoreboard and HUD status icons. |
| `0x0E0` | `teamLeader` | `qboolean` | Team-leader latch used by order input gating. |
| `0x0E4` | `powerups` | `int` | Cached live powerup bitmask used by scoreboard flag markers, team overlays, and selected-player ownerdraws. |
| `0x0E8` | `medkitUsageTime` | `int` | Effect timer for the medkit usage model. |
| `0x0EC` | `invulnerabilityStartTime` | `int` | Start time for the invulnerability shell scale/fade effect. |
| `0x0F0` | `invulnerabilityStopTime` | `int` | Last active time for invulnerability shell fade-out. |
| `0x0F4` | `breathPuffTime` | `int` | Cooldown timer for cold-breath puff emission. |

## Model Source Strings And Deferred-Load State

These members describe the source assets that should be loaded, then support the
deferred-load and handle-sharing path.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x0F8` | `modelName` | `char[MAX_QPATH]` | Body model token parsed from the player configstring, possibly rewritten by override logic. |
| `0x138` | `skinName` | `char[MAX_QPATH]` | Body skin token paired with `modelName`. |
| `0x178` | `headModelName` | `char[MAX_QPATH]` | Head model token used both for model loading and voice-chat list resolution. |
| `0x1B8` | `headSkinName` | `char[MAX_QPATH]` | Head skin token paired with `headModelName`. |
| `0x1F8` | `redTeam` | `char[MAX_TEAMNAME]` | Cached red-team label used by team skin matching and deferred reuse checks. |
| `0x218` | `blueTeam` | `char[MAX_TEAMNAME]` | Cached blue-team label used by team skin matching and deferred reuse checks. |
| `0x238` | `deferred` | `qboolean` | Marks records currently borrowing cached handles instead of owning a fully loaded model set. |

## Animation Metadata And Render Cache

This tail is the reusable presentation payload copied between matching clients
and consumed directly by player rendering, head drawing, rail effects, and
custom-sound playback.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x23C` | `newAnims` | `qboolean` | Tag-capability flag set when the torso model exposes `tag_flag`; drives attached flag rendering instead of fallback trail items. |
| `0x240` | `fixedlegs` | `qboolean` | Animation-config latch forcing legs yaw/pitch/roll to follow the torso. |
| `0x244` | `fixedtorso` | `qboolean` | Animation-config latch forcing torso pitch to stay neutral. |
| `0x248` | `headOffset` | `vec3_t` | Per-model head icon offset used by 3D head draws. |
| `0x254` | `footsteps` | `footstep_t` | Footstep sound family selected from animation config. |
| `0x258` | `gender` | `gender_t` | Gender classification used by obituary grammar and voice-chat fallback selection. |
| `0x25C` | `legsModel` | `qhandle_t` | Registered legs model handle. |
| `0x260` | `legsSkin` | `qhandle_t` | Registered legs skin handle. |
| `0x264` | `torsoModel` | `qhandle_t` | Registered torso model handle. |
| `0x268` | `torsoSkin` | `qhandle_t` | Registered torso skin handle. |
| `0x26C` | `headModel` | `qhandle_t` | Registered head model handle. |
| `0x270` | `headSkin` | `qhandle_t` | Registered head skin handle. |
| `0x274` | `modelIcon` | `qhandle_t` | Cached portrait/icon shader for scoreboards, HUDs, and endgame panels. |
| `0x278` | `animations[MAX_TOTALANIMATIONS]` | `animation_t[37]` | Full animation table used by lerp-frame evaluation and weapon-frame mapping. |
| `0x684` | `sounds[MAX_CUSTOM_SOUNDS]` | `sfxHandle_t[32]` | Custom player sound cache addressed by `CG_CustomSound`. |

## Embedded `animation_t`

Each animation entry is a full `animation_t` record:

| Offset in `animation_t` | Member | Type | Role in `clientInfo_t` |
| --- | --- | --- | --- |
| `0x00` | `firstFrame` | `int` | First MD3 frame for the sequence. |
| `0x04` | `numFrames` | `int` | Frame count; negative source values normalize into `reversed`. |
| `0x08` | `loopFrames` | `int` | Number of looping tail frames. |
| `0x0C` | `frameLerp` | `int` | Milliseconds per frame during steady playback. |
| `0x10` | `initialLerp` | `int` | Initial interpolation delay when the animation starts. |
| `0x14` | `reversed` | `int` | Reverse-playback flag synthesized by `CG_ParseAnimationFile`. |
| `0x18` | `flipflop` | `int` | Flipflop playback flag; structurally present but weak in the current player set. |

## Active Custom Sound Slots

`CG_CustomSound` indexes `sounds[]` through the static `cg_customSoundNames`
table. The first `13` slots are actively named; the remaining slots stay
structural/unused in the current tree unless future retail evidence says
otherwise.

| Slot | Name |
| --- | --- |
| `0` | `*death1.wav` |
| `1` | `*death2.wav` |
| `2` | `*death3.wav` |
| `3` | `*jump1.wav` |
| `4` | `*pain25_1.wav` |
| `5` | `*pain50_1.wav` |
| `6` | `*pain75_1.wav` |
| `7` | `*pain100_1.wav` |
| `8` | `*falling1.wav` |
| `9` | `*gasp.wav` |
| `10` | `*drown.wav` |
| `11` | `*fall1.wav` |
| `12` | `*taunt.wav` |

## Ownership Notes

### Configstring Build Path

- `CG_NewClientInfo` builds a temporary `clientInfo_t`, not the live record
  directly.
- The strongest parsed keys are:
  - `n` -> `name`
  - `c1` / `c2` -> `color1` / `color2`
  - `skill` -> `botSkill`
  - `hc` -> `handicap`
  - `w` / `l` -> `wins` / `losses`
  - `t` -> `team`
  - `tt` -> `teamTask`
  - `tl` -> `teamLeader`
  - `g_redteam` / `g_blueteam` -> `redTeam` / `blueTeam`
  - `model` -> `modelName` + `skinName`
  - `hmodel` -> `headModelName` + `headSkinName`
- `CG_ApplyClientModelOverrides` mutates the source model/skin strings and
  records override provenance through `modelForced`, `headModelForced`, and
  `skinForced`.
- `CG_ApplyClientColorOverrides` resolves the final tint vectors and sets the
  live body/head color latches.
- `infoValid` is only raised after the load/defer resolution completes and the
  finished temp record is copied back into `cgs.clientinfo[clientNum]`.

### Live Mirror Writers

- `score` is mirrored by score server commands, not by the configstring path.
- `powerups` has two active writers:
  - score parsing mirrors it from the full score payload
  - `CG_ParseTeamInfo` mirrors the live teammate/team-overlay value
- `location`, `health`, `armor`, and `curWeapon` are team-info mirrors.
- `medkitUsageTime` is stamped by `CG_UseItem`.
- `invulnerabilityStartTime` and `invulnerabilityStopTime` are maintained by
  the live player render path when the invulnerability shell becomes active or
  fades out.
- `breathPuffTime` is maintained by `CG_BreathPuffs` as a simple cooldown.

### Deferred Load And Handle Sharing

- `CG_ScanForExistingClientInfo` compares the source string set
  (`modelName`, `skinName`, `headModelName`, `headSkinName`, `redTeam`,
  `blueTeam`, plus `team` in team modes) to reuse existing model/animation/sound
  payloads.
- `CG_CopyClientInfoModel` copies the reusable render tail:
  `headOffset`, `footsteps`, `gender`, the model/skin/icon handles,
  `newAnims`, `animations`, and `sounds`.
- `CG_SetDeferredClientInfo` marks `deferred = qtrue` when a client is
  temporarily borrowing another client's loaded render tail.
- `CG_LoadDeferredPlayers` later promotes deferred records by calling
  `CG_LoadClientInfo`.

### Render, HUD, And Event Consumption

- `CG_RegisterClientModelname` and `CG_LoadClientInfo` populate
  `legsModel`, `legsSkin`, `torsoModel`, `torsoSkin`, `headModel`, `headSkin`,
  `modelIcon`, `animations`, `sounds`, and `newAnims`.
- `CG_ParseAnimationFile` owns `footsteps`, `headOffset`, `gender`,
  `fixedlegs`, `fixedtorso`, and the bulk of `animations[]`.
- `CG_Player` consumes the model handles directly, applies
  `headColorForced` / `upperColorForced` / `lowerColorForced`, and updates the
  medkit/invulnerability effect timers.
- `CG_PlayerAngles` consumes `fixedlegs` and `fixedtorso`.
- `CG_PlayerPowerups` consumes `newAnims` to choose attached flag models versus
  fallback trailing flag items.
- `CG_RailTrail` and weapon-flash paths consume
  `weaponPrimaryColor` / `weaponSecondaryColor`.
- `CG_DrawHead` and the newer HUD head/icon paths consume `headModel`,
  `headSkin`, `headOffset`, `modelIcon`, and `deferred`.
- `CG_EntityEvent` and obituary/voice-chat helpers consume `footsteps`,
  `gender`, `medkitUsageTime`, and `sounds[]`.
- Scoreboard and HUD code consume `botSkill`, `handicap`, `wins`, `losses`,
  `teamTask`, `teamLeader`, `score`, `location`, `health`, `armor`,
  `curWeapon`, and `powerups`.

## Field-Strength Notes

### Strongly Owned Fields

The highest-confidence live fields are:

- `infoValid`, `name`, `team`
- `color1`, `color2`, `headColor`, `upperColor`, `lowerColor`
- `weaponPrimaryColor`, `weaponSecondaryColor`
- `headColorForced`, `upperColorForced`, `lowerColorForced`
- `score`, `location`, `health`, `armor`, `curWeapon`
- `handicap`, `wins`, `losses`, `teamTask`, `teamLeader`, `powerups`
- `medkitUsageTime`, `invulnerabilityStartTime`, `invulnerabilityStopTime`,
  `breathPuffTime`
- `modelName`, `skinName`, `headModelName`, `headSkinName`,
  `redTeam`, `blueTeam`, `deferred`
- `newAnims`, `fixedlegs`, `fixedtorso`, `headOffset`, `footsteps`, `gender`
- `legsModel`, `legsSkin`, `torsoModel`, `torsoSkin`, `headModel`,
  `headSkin`, `modelIcon`, `animations`, `sounds`

### Weaker Or Provenance-Only Fields

- `weaponColorForced` is a bookkeeping flag for override selection, but the
  current render code reads the resolved weapon colors directly.
- `modelForced`, `headModelForced`, and `skinForced` are clear override
  provenance markers, but I did not find strong current render/HUD consumers
  that branch on them after setup.
- `score` is live, but much narrower than `score_t`: it acts as a convenient
  client mirror for specific scoreboard/UI paths rather than as the primary
  match-stat record.

## Practical Reading Guide

- If the question is "is this client record usable at all?", start at
  `infoValid`.
- If the question is "why does this player have this name, team, color, or
  forced model?", start at `name`, `team`, `color1`, `color2`, the resolved
  tint fields, and the source model/skin strings.
- If the question is "why is the HUD showing this teammate status?", start at
  `location`, `health`, `armor`, `curWeapon`, `teamTask`, `teamLeader`, and
  `powerups`.
- If the question is "why is this player still using borrowed art?", start at
  `deferred` plus the model/source string band.
- If the question is "why do the player model, head icon, rails, or flag
  attachments look different?", start at `newAnims`, `headOffset`,
  the model/skin handles, and the weapon color pair.
- If the question is "why did obituary/audio choose this phrasing or sound?",
  start at `gender`, `footsteps`, and `sounds[]`.

## Open Questions

1. Recover the exact retail function boundaries for the client-info load/build
   helpers around the `0x1003D3BA-0x1003DD0D` HLIL string cluster so the note
   can cite stabilized function addresses instead of surrounding behavior
   anchors.
2. Revalidate whether `weaponColorForced`, `modelForced`,
   `headModelForced`, and `skinForced` participate in any retail-only debug or
   HUD path, or whether they are purely write-side provenance markers in the
   shipped client.
