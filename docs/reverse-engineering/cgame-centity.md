# cgame `centity_t` Layout Map

This note maps the retail-compatible x86 layout of `centity_t` used by
`cgamex86.dll` onto the current `src/code/cgame/cg_local.h` definition. The
goal is to separate hard layout facts from the higher-level roles played by the
snapshot, event, interpolation, and player-animation paths.

## Method

- Layout facts come from a local x86 record-layout dump of `centity_t`,
  `playerEntity_t`, `entityState_t`, and `lerpFrame_t` using
  `clang -target i686-pc-windows-msvc -DID_INLINE=__inline -Xclang -fdump-record-layouts`
  against `src/code/cgame/cg_local.h`.
- Member roles were cross-checked against the main entity-transition and render
  paths in `cg_snapshot.c`, `cg_ents.c`, `cg_event.c`, `cg_players.c`,
  `cg_weapons.c`, and `cg_predict.c`.
- This pass maps the top-level `centity_t` members plus the embedded
  `playerEntity_t` block. `entityState_t` is treated here as a known embedded
  wire-format payload rather than being remapped field-by-field again.

## Hard Layout Facts

- `sizeof(entityState_t) = 0x0D0` (`208`).
- `sizeof(lerpFrame_t) = 0x030` (`48`).
- `sizeof(playerEntity_t) = 0x0B8` (`184`).
- `sizeof(centity_t) = 0x2D8` (`728`).
- `centity_t` is used both for snapshot-backed `cg_entities[]` entries and for
  the standalone predicted proxy `cg.predictedPlayerEntity`.
- The high-level banding is:
  - `currentState` at `0x000`
  - `nextState` at `0x0D0`
  - snapshot/event/timer band at `0x1A0`
  - embedded `playerEntity_t pe` at `0x1C4`
  - correction/raw/interpolation tail at `0x27C`

## Top-Level Member Map

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x000` | `currentState` | `entityState_t` | Snapshot-owned current entity state used by rendering, events, sounds, and prediction. |
| `0x0D0` | `nextState` | `entityState_t` | Forward snapshot state used when interpolation is legal. |
| `0x1A0` | `interpolate` | `qboolean` | Marks whether `nextState` is valid for interpolation. |
| `0x1A4` | `currentValid` | `qboolean` | Marks whether the entity exists in the current snapshot. |
| `0x1A8` | `muzzleFlashTime` | `int` | Short-lived weapon flash timer. |
| `0x1AC` | `previousEvent` | `int` | Event deduplication scratch used by `CG_CheckEvents`. |
| `0x1B0` | `teleportFlag` | `int` | Present in the layout, but not strongly revalidated by current live consumers in this pass. |
| `0x1B4` | `trailTime` | `int` | Missile/player trail cursor used to bridge dropped packets and spawn spaced trail segments. |
| `0x1B8` | `dustTrailTime` | `int` | Dust-trail emission cursor for player movement effects. |
| `0x1BC` | `miscTime` | `int` | Multi-purpose scratch timer used by several entity-specific paths. |
| `0x1C0` | `snapShotTime` | `int` | Last snapshot server time in which the entity was seen. |
| `0x1C4` | `pe` | `playerEntity_t` | Embedded player-only animation and weapon presentation state. |
| `0x27C` | `errorTime` | `int` | Prediction/error-correction band; only partially revalidated in the current tree. |
| `0x280` | `errorOrigin` | `vec3_t` | Prediction/error-correction origin scratch; present but not strongly revalidated. |
| `0x28C` | `errorAngles` | `vec3_t` | Prediction/error-correction angle scratch; present but not strongly revalidated. |
| `0x298` | `extrapolated` | `qboolean` | Indicates whether the current raw pose came from extrapolation rather than interpolation. |
| `0x29C` | `rawOrigin` | `vec3_t` | Unsmoothed/raw pose origin used when resetting player animation state. |
| `0x2A8` | `rawAngles` | `vec3_t` | Unsmoothed/raw pose angles used when resetting player animation state. |
| `0x2B4` | `beamEnd` | `vec3_t` | Present in the layout, but no strong active consumer was revalidated in this pass. |
| `0x2C0` | `lerpOrigin` | `vec3_t` | Final render/event/sound origin for the current frame. |
| `0x2CC` | `lerpAngles` | `vec3_t` | Final render/event/sound angles for the current frame. |

## Embedded `playerEntity_t` Map

`playerEntity_t` is the `centity_t`-local animation and weapon presentation
slab. It is only meaningful for player-like entities, but retail keeps it
inside every `centity_t` instance for simplicity.

| Offset in `pe` | Member | Type | Role |
| --- | --- | --- | --- |
| `0x000` | `legs` | `lerpFrame_t` | Legs animation lerp state. |
| `0x030` | `torso` | `lerpFrame_t` | Torso animation lerp state. |
| `0x060` | `flag` | `lerpFrame_t` | Flag attachment animation/orientation state. |
| `0x090` | `painTime` | `int` | Pain twitch / pain-sound debounce anchor. |
| `0x094` | `painDirection` | `int` | Left/right pain twitch direction toggle. |
| `0x098` | `lightningFiring` | `int` | Latched continuous-fire state for lightning/gauntlet style weapons. |
| `0x09C` | `railgunImpact` | `vec3_t` | Stored rail impact point for deferred rail trail spawning. |
| `0x0A8` | `railgunFlash` | `qboolean` | Latch controlling whether a rail flash/trail is pending. |
| `0x0AC` | `barrelAngle` | `float` | Current machinegun/chaingun barrel angle. |
| `0x0B0` | `barrelTime` | `int` | Last barrel spin update time. |
| `0x0B4` | `barrelSpinning` | `qboolean` | Whether the barrel is actively spinning. |

## Ownership Notes

### Snapshot Ownership

- `CG_SetInitialSnapshot` seeds `currentState`, clears `interpolate`, sets
  `currentValid`, then resets the entity before firing any startup events.
- `CG_SetNextSnap` fills `nextState` and decides whether `interpolate` can stay
  true based on `currentValid` and teleport-bit transitions.
- `CG_TransitionEntity` promotes `nextState` into `currentState`, sets
  `currentValid`, clears `interpolate`, and immediately runs `CG_CheckEvents`.
- `snapShotTime` is refreshed when the transitioned entity is present in the new
  snapshot; `CG_ResetEntity` uses that timestamp to decide when `previousEvent`
  can be safely cleared.

### Event And Effect Timers

- `previousEvent` is the main event dedupe latch used by `CG_CheckEvents`.
- `muzzleFlashTime` is written in `CG_FireWeapon` and read in the weapon draw
  path to suppress stale flashes once `MUZZLE_FLASH_TIME` has elapsed.
- `trailTime` is reset in `CG_ResetEntity` and then consumed by rocket, nail,
  plasma, and grapple trail builders to cover packet gaps without re-emitting
  the whole trail every frame.
- `dustTrailTime` is a separate emission cursor for player dust effects.
- `miscTime` is intentionally multi-purpose. In the current reconstruction it is
  reused by speaker timing, item scale-up timing, predicted item pickup
  suppression, Domination distress cadence, and several entity-specific visual
  timers.
- `teleportFlag` still exists in the retail-compatible layout, but this pass did
  not find a strong active owner in the reconstructed tree, so it stays
  documented as a carry-over field rather than a fully revalidated one.

### Embedded `playerEntity_t`

- `pe.legs` and `pe.torso` are driven by `CG_PlayerAnimation`,
  `CG_PlayerAngles`, and `CG_ResetPlayerEntity`.
- `pe.flag` is used by the flag attachment path in `CG_PlayerFlag`.
- `pe.painTime` and `pe.painDirection` are written by `CG_PainEvent` and read by
  `CG_AddPainTwitch`.
- `pe.lightningFiring` is the continuous-fire latch used by
  `CG_AddPlayerWeapon`.
- `pe.railgunImpact` and `pe.railgunFlash` are fed by the predicted and
  non-predicted rail paths before `CG_SpawnRailTrail` consumes them.
- `pe.barrelAngle`, `pe.barrelTime`, and `pe.barrelSpinning` are owned by
  `CG_MachinegunSpinAngle`.

### Correction / Raw / Interpolation Tail

- `lerpOrigin` and `lerpAngles` are the live outputs of
  `CG_ResetEntity`, `CG_InterpolateEntityPosition`, and
  `CG_CalcEntityLerpPositions`. They are then reused everywhere:
  rendering, sound positioning, event dispatch, mover adjustment, player
  attachments, and weapon effects.
- `rawOrigin` and `rawAngles` are explicitly refreshed in
  `CG_ResetPlayerEntity` and then used to seed the torso/legs animation state.
- `errorTime` and `extrapolated` still have some live evidence in
  `CG_ResetPlayerEntity`, which forces `errorTime = -99999` and
  `extrapolated = qfalse`. The rest of the old error-decay band
  (`errorOrigin`, `errorAngles`) is present in the layout but not strongly
  exercised by the current reconstructed code.
- `beamEnd` is also present in the layout but did not surface as a strong live
  field in this pass. The active beam rendering path currently reads directly
  from `currentState.pos.trBase` and `currentState.origin2` instead.

## Practical Reading Guide

- If the question is "what did the server send?", start at `currentState` /
  `nextState`.
- If the question is "what should be drawn or sounded this frame?", start at
  `lerpOrigin` / `lerpAngles`.
- If the question is "why did a player animate or wobble this way?", start at
  `pe`.
- If the question is "why did a timer-like entity effect repeat or suppress?",
  check `trailTime`, `dustTrailTime`, `miscTime`, and `muzzleFlashTime`.

## Open Questions

1. Revalidate the dormant correction band against retail HLIL to determine
   whether `errorOrigin` and `errorAngles` still participate in the Quake Live
   client’s smoothing logic or are only inherited baggage from the GPL layout.
2. Determine whether `beamEnd` is still a real retail scratch field or just a
   preserved-but-unused carry-over.
3. Expand `entityState_t` as its own reverse-engineering note if field-level VM
   wire-format mapping becomes necessary for future protocol work.
