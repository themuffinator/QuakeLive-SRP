# cgame `leType_t` Enum Map

This note maps the retail-compatible x86 `leType_t` enum used by
`cgamex86.dll` onto the current `src/code/cgame/cg_local.h` definition and the
local-entity dispatcher in `cg_localents.c`. The goal is to pin the ordinal
values, the dispatch targets, and the observed producer coverage without
flattening the weaker carry-over slots into false certainty.

## Method

- The enum definition and owning field placement come from
  `src/code/cgame/cg_local.h`, cross-checked with a local x86 record-layout dump
  of `localEntity_t` using
  `clang -target i686-pc-windows-msvc -DID_INLINE=__inline -Xclang -fdump-record-layouts`
  against `src/code/cgame/cg_local.h`.
- Source-side dispatch and producer coverage come from
  `src/code/cgame/cg_localents.c`, `src/code/cgame/cg_effects.c`,
  `src/code/cgame/cg_weapons.c`, and `src/code/cgame/cg_players.c`.
- Retail parity was cross-checked against the HLIL local-entity dispatcher at
  `0x10020790` and the committed Ghidra function inventory in
  `references/reverse-engineering/ghidra/cgamex86/functions.csv`.

## Hard Facts

- On retail-compatible x86, `leType_t` occupies `4` bytes and lives at
  `localEntity_t + 0x08`.
- `sizeof(localEntity_t) = 0x12C` (`300`) in the recovered retail-compatible
  x86 layout.
- `CG_AddLocalEntities` is the central consumer. It frees expired local
  entities first, then dispatches on `leType`.
- The retail dispatcher at `0x10020790` matches the source switch structure and
  throws `Bad leType: %i` for out-of-range values above `0x10`.
- Ordinals `0x03`, `0x0E`, and `0x10` share the same base fragment handler in
  both source and retail, with `0x0E` and `0x10` carrying their own auxiliary
  trail hooks around that shared physics/render path.
- The current reconstructed tree actively produces `15` of the `17` retail
  ordinal slots. Two values remain unproduced in source:
  `LE_MARK` and `LE_FRAGMENT_16`.

## Member Map

| Value | Member | Retail/source dispatch | Observed producers | Role |
| --- | --- | --- | --- | --- |
| `0x00` | `LE_MARK` | No-op slot in `CG_AddLocalEntities` and the retail `0x10020790` switch. | None in the current tree. | Dormant carry-over slot. The current persistent mark path uses `markPoly_t` instead of `localEntity_t`. |
| `0x01` | `LE_EXPLOSION` | `CG_AddExplosion`; retail case `0x01` maps to the same dedicated explosion path. | `CG_MakeExplosion` non-sprite path. | Model or sprite-backed explosion shell with optional dynamic light fade. |
| `0x02` | `LE_SPRITE_EXPLOSION` | `CG_AddSpriteExplosion`; retail case `0x02` maps to the longer sprite-specific explosion path. | `CG_MakeExplosion` sprite path. | Billboard explosion sprite that expands, alpha-fades, and optionally emits dynamic light. |
| `0x03` | `LE_FRAGMENT` | `CG_AddFragment`; retail case `0x03` shares the fragment handler with `0x0E` and `0x10`. | `CG_LaunchGib`, `CG_ThawPlayer` shards, `CG_GibPlayer` shards, machinegun/shotgun brass ejectors, shotgun pellet debris. | Physics-driven fragment entity with bounce, optional tumble, impact marks, and impact sounds; the retail producer family also splits the recovered `fragmentMarkType` / `fragmentBounceSoundType` slots into blood, brass, electrogib, ice-trail, and ice-mark variants. |
| `0x04` | `LE_MOVE_SCALE_FADE` | `CG_AddMoveScaleFade`; retail case `0x04` maps to the same moving sprite fade path. | `CG_BubbleTrail`, `CG_SmokePuff` default path, rail ring puffs, plasma trail puffs. | Moving sprite that alpha-fades, can grow, and is culled when the camera enters it. |
| `0x05` | `LE_05` | `CG_AddType05`; retail case `0x05` maps to the moving RGB fade path at `sub_1001f180`. | `CG_BigExplode`, `CG_BigExplodeJuiced`. | Moving or stationary sprite shell that evaluates `pos`, modulates RGBA, and optionally grows unless `LEF_PUFF_DONT_SCALE` is set; the recovered no-DLC gib fallback uses it for short-lived `gfx/misc/tracer` sprite streaks around the `deathEffect` shell, and that retail fallback is not suppressed by `cg_blood`. Retail seeds these tracer shells with the cgame-only custom trajectory type `6` plus `posTrajExtra = -240`. |
| `0x06` | `LE_FALL_SCALE_FADE` | `CG_AddFallScaleFade`; retail case `0x06` maps to the optimized falling-fade path. | `CG_BloodTrail`, `CG_Bleed`. | Optimized blood-mist style sprite that drifts downward while growing and fading; retail also uses it for the blood-hit burst after seeding the entity through the shared smoke-puff builder with one of the DLC `bloodSpray` shaders. |
| `0x07` | `LE_FADE_RGB` | `CG_AddFadeRGB`; retail case `0x07` maps to the RGB-fade path at `sub_1001f080`. | `CG_SpawnEffect`, `CG_RailTrail` core beam shell. | Entity that fades by modulating RGBA rather than by changing sprite size. |
| `0x08` | `LE_SCALE_FADE` | `CG_AddScaleFade`; retail case `0x08` maps to the stationary scale-fade path at `sub_1001f4e0`. | Rocket, nail, and haste smoke trails that overwrite the default `CG_SmokePuff` type. | Mostly stationary puff that grows and alpha-fades until culled or expired. |
| `0x09` | `LE_SCOREPLUM` | `CG_AddScorePlum`; retail case `0x09` maps to the score-plum renderer at `sub_10020470`. | `CG_ScorePlum`. | Floating score-number sprite stack colored by score magnitude and sign; the retail producer only nudges overlapping plums when the new Z lies in the previous plum's `[z - 20, z]` band. |
| `0x0A` | `LE_10` / `LE_KAMIKAZE` | `CG_AddKamikaze`; retail case `0x0A` maps to `FUN_1001fc50` in Ghidra and the matching large HLIL handler. | `CG_KamikazeEffect` via the compatibility alias `LE_KAMIKAZE`. | Timed kamikaze boomsphere/shockwave/light composite with gated explode and implode sounds. |
| `0x0B` | `LE_INVULIMPACT` | `CG_AddInvulnerabilityImpact`; retail case `0x0B` is inlined to a direct `trap_R_AddRefEntityToScene` call rather than a separate helper boundary. | `CG_InvulnerabilityImpact`. | Short-lived invulnerability impact model with sound. |
| `0x0C` | `LE_INVULJUICED` | `CG_AddInvulnerabilityJuiced`; retail case `0x0C` maps to the juiced-player effect path. | `CG_InvulnerabilityJuiced` when DLC gib media is present. Retail `EV_JUICED` bypasses this slot in the no-DLC fallback and goes straight to the immediate `CG_BigExplode` breakup path. | Expanding invulnerability model that eventually forces a gib burst; in retail it is a DLC-only long-lived path rather than the universal `EV_JUICED` producer. |
| `0x0D` | `LE_SHOWREFENTITY` | `CG_AddRefEntity`; retail case `0x0D` maps to the plain ref-entity submit path. | `CG_LightningBoltBeam`. | Thin wrapper for short-lived render entities that need no extra fade logic; the recovered lightning-event producer fills `RT_LIGHTNING`, `radius = 256`, and the active lightning-style shader slot before submission. |
| `0x0E` | `LE_FRAGMENT_14` | `CG_AddFragment14`; retail case `0x0E` runs the shared fragment path and then emits tracer-shell puffs through `sub_1001d860`. | `CG_BigExplode`, `CG_BigExplodeJuiced` retail no-DLC fallback reached from `CG_GibPlayer` and the juiced timeout. | Distinct fragment ordinal preserved in retail/source dispatch; the recovered fallback producer uses it for short-lived sphere fragments with a post-add tracer puff trail, a downward 10-step ring-style launch basis, the smaller burn-mark family, and the electrogib-style bounce sound slot. Retail seeds these fragments with the same cgame-only custom trajectory type `6`, using `posTrajExtra = 425` instead of the stock Quake III gravity constant. |
| `0x0F` | `LE_0F` / `LE_SCALE_FADE_OUT` | `CG_AddType0F`; retail case `0x0F` maps to `sub_1001f730`, which mirrors `0x05` and then adds a fading dynamic light. | `CG_SpawnDeathEffect` via the compatibility alias `LE_SCALE_FADE_OUT`. | Sprite-shell fade path used by the recovered death-effect fallback; retail seeds it with `LEF_PUFF_DONT_SCALE` so the shell stays fixed-size and drives a short 400-unit orange fading light through the shared `light` / `lightColor` payload. |
| `0x10` | `LE_FRAGMENT_16` | `CG_AddFragment16`; retail case `0x10` emits an iceball puff trail through `sub_1001d930` before running the shared fragment path. | None in the current tree. | Distinct fragment ordinal preserved in retail/source dispatch, with a pre-add iceball puff trail wrapped around the common fragment physics/render logic. |

## Reading The Enum

- If the question is "which code path renders this local entity?", start with
  `CG_AddLocalEntities`: it is the authoritative switch owner for `leType_t`.
- If the question is "which values are still actively created by the current
  source?", focus on `LE_EXPLOSION`, `LE_SPRITE_EXPLOSION`, `LE_FRAGMENT`,
  `LE_MOVE_SCALE_FADE`, `LE_FALL_SCALE_FADE`, `LE_FADE_RGB`, `LE_SCALE_FADE`,
  `LE_SCOREPLUM`, `LE_10` / `LE_KAMIKAZE`, `LE_INVULIMPACT`,
  `LE_INVULJUICED`, `LE_SHOWREFENTITY`, `LE_FRAGMENT_14`,
  `LE_0F` / `LE_SCALE_FADE_OUT`, and `LE_05`.
- If the question is "which enum members remain weak or dormant?", focus on
  `LE_MARK` and `LE_FRAGMENT_16`.

## Practical Notes

- `leType_t` is only the dispatcher key. Bounce behavior, impact marks, sounds,
  and camera-cull behavior still come from the rest of `localEntity_t`
  (`leFlags`, `fragmentMarkType`, `fragmentBounceSoundType`, `pos`, `angles`,
  `color`, `radius`, and `refEntity`).
- `LE_MARK` should not be confused with `markPoly_t`. In the current tree the
  persistent wall-mark system is owned by `cg_marks.c` and the standalone
  `markPoly_t` pool rather than the local-entity pool.
- The fragment-family split is real at the ordinal level in retail. `LE_FRAGMENT`
  still owns the shared base physics/render path, while `LE_FRAGMENT_14` and
  `LE_FRAGMENT_16` wrap it with tracer and iceball puff trails respectively.

## Open Questions

1. Recover the remaining retail producer sites for `LE_FRAGMENT_16` to
   determine whether Quake Live still instantiates it or merely preserves the
   dispatch slot.
2. Revalidate whether `LE_MARK` is truly dead in retail or just moved behind a
   currently unrecovered producer path. The current evidence only shows that the
   dispatcher slot is a no-op and that present source uses `markPoly_t` instead.
3. Expand the related `localEntity_t` note in
   `docs/reverse-engineering/cgame-localentity.md` if future work needs deeper
   field-level recovery of the shared fragment and render payload behind each
   `leType_t` value.
