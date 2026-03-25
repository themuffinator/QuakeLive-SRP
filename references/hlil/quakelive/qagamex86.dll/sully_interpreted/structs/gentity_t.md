# gentity_t layout (Quake Live `qagamex86.dll`)

## Observed facts

- The retail `g_entities` array is rooted at `data_104b3fa0` and uses a stride of `0x384` bytes per entity.
- A 32-bit record-layout dump of the current source `gentity_s` is `0x358`, so retail is `0x2c` bytes larger overall.
- The retail drift is not uniform:
  - the `client/inuse/classname` block is source `+0x38`
  - the `target/nextthink/callback` block is source `+0x48`
  - `wait/random` are source `+0x4c`
  - `item` is source `+0x50`
- The earlier note was wrong about `0x240`, `0x27c`, and `0x32c`. `0x240` behaves like source `inuse`, and the old `commandTime` / warmup labels were lifted from client-side evidence rather than entity-side reads.

## Recovered members

| Offset | Field | Confidence | Evidence |
| ------ | ----- | ---------- | -------- |
| `0x000` | `entityState_t s` | High | The entity array is walked as a `0x384`-byte struct and the early scalar/vector slots still match the server snapshot layout used by temp entities, movers, and item entities. |
| `0x068` | `r.svFlags` | High | Retail preserves and mutates this word exactly where source `entityShared_t::svFlags` lives. |
| `0x1E0` | `svFlagsExt` | High | Bot/retail-only entity flagging hits this Quake Live extension word. |
| `0x23C` | `gclient_t *client` | High | `ClientConnect` / `ClientBegin` store the owning client pointer here and active-client paths repeatedly dereference `*(ent + 0x23c)`. |
| `0x240` | `qboolean inuse` | High | `G_FreeEntity`-style code clears `*(ent + 0x240) = 0` while also setting `classname = "freed"` and stamping `freetime`, matching source `inuse`. |
| `0x244` | `char *classname` | High | Free paths assign `"freed"` here; temp entities assign `"tempEntity"`; kamikaze setup assigns `"kamikaze"`. |
| `0x248` | `int spawnflags` | High | Target-print / target-speaker style entities test and combine bits in this slot exactly like QuakeEd spawnflags. |
| `0x24C` | `qboolean neverFree` | High | `G_FreeEntity` first checks `*(ent + 0x24c) == 0` before wiping the struct, matching source `neverFree`. |
| `0x250` | `int flags` | High | Retail repeatedly sets and clears FL-style bits here (`|= 0x10010`, `|= 0x20800`, `|= 0x2000`, `&= ...`). |
| `0x254` | `char *model` | High | Brush/mover spawn helpers call the engine brush-model setter as `(*(data_104b13ac + 0x7c))(ent, *(ent + 0x254))`, matching source `G_SetBrushModel(ent, ent->model)`. |
| `0x258` | `char *model2` | High | The retail mover-init helper first checks `*(ent + 0x258)` and, when non-null, feeds it through the same configstring-index helper used for `s.modelindex2` before parsing mover `"noise"`, `"light"`, and `"color"`, matching source `if (ent->model2) ent->s.modelindex2 = G_ModelIndex(ent->model2);`. |
| `0x25C` | `int freetime` | High | The free path writes current `level.time` here immediately before clearing `inuse`. |
| `0x260` | `int eventTime` | High | `G_TempEntity` stores `level.time` here when it creates a one-frame event entity. |
| `0x264` | `qboolean freeAfterEvent` | High | `G_TempEntity` sets this slot to `1`, and later cleanup paths test it alongside the entity flags. |
| `0x268` | `qboolean unlinkAfterEvent` | High | `Touch_Item` sets this slot when a picked-up item should unlink instead of being freed, and the later event-cleanup path preserves the source `freeAfterEvent` / `unlinkAfterEvent` split by clearing the unlink latch after unlinking those entities. |
| `0x26C` | `qboolean physicsObject` | High | Item/body/drop spawn paths set this slot to `1` together with a bounce factor, and cleanup paths clear it when the entity stops behaving like a tossed physics object, matching source `physicsObject`. |
| `0x270` | `float physicsBounce` | High | Dropped-item and corpse paths write bounce constants here, and later physics code multiplies `trDelta` by the float at `+0x270`, matching source `physicsBounce`. |
| `0x274` | `int clipmask` | High | Trace/move calls pass `*(ent + 0x274)` as the final contents mask, and spawn paths write solid/playerclip style masks (`0x6000001`, `0x4000001`, `MASK_SHOT`-equivalent patterns) here, matching source `clipmask`. |
| `0x278` | `moverState_t moverState` | High | The retail binary-mover controller switches on `*(ent + 0x278)`, emits the preserved `"Reached_BinaryMover: bad moverState"` diagnostic for unknown values, and stores `0/1/2/3` in the same slot exactly like source `MOVER_POS1`, `MOVER_POS2`, `MOVER_1TO2`, and `MOVER_2TO1`. |
| `0x27C` | `int soundPos1` | High | `Reached_BinaryMover`’s return-to-`POS1` path copies `*(ent + 0x27c)` into the outgoing general-sound event slot after setting `moverState = MOVER_POS1`, matching source `soundPos1`. |
| `0x280` | `int sound1to2` | High | `Use_BinaryMover` reads `*(ent + 0x280)` immediately after kicking the mover into the opening state, and the door/plat init helpers seed this slot from the opening/start sound asset, matching source `sound1to2`. |
| `0x284` | `int sound2to1` | High | The return-to-`POS1` helper and reversed mover path emit `*(ent + 0x284)` as the closing transition sound, matching source `sound2to1`. |
| `0x288` | `int soundPos2` | High | `Reached_BinaryMover`’s arrival-at-`POS2` path emits `*(ent + 0x288)` immediately after setting `moverState = MOVER_POS2`, matching source `soundPos2`. |
| `0x28C` | `int soundLoop` | High | Both `Reached_BinaryMover` and `Use_BinaryMover` copy `*(ent + 0x28c)` into `s.loopSound`, matching source `soundLoop`. |
| `0x290` | `gentity_t *parent` | High | Spawned helper entities such as the proxmine trigger store their owner entity in `*(ent + 0x290)`, and later touch/think paths chase that pointer back to update the owner, matching source `parent`. |
| `0x294` | `gentity_t *nextTrain` | High | Train/path-corner movement code advances `*(ent + 0x294)` through a linked path chain and rebuilds `pos1/pos2` from the current and next node origins, matching source `nextTrain`. |
| `0x29C` | `vec3_t pos1` | High | Retail mover setup copies the current origin into `0x29c/0x2a0/0x2a4`, and mover state transitions later restore the entity origin from that same triple when returning to `POS1`, matching source `pos1`. |
| `0x2A8` | `vec3_t pos2` | High | The same setup and movement code computes and stores the destination triple at `0x2a8/0x2ac/0x2b0`, then drives trajectory deltas from `pos1 -> pos2` and back, matching source `pos2`. |
| `0x2B4` | `char *message` | High | Target-print style code feeds `*(ent + 0x2b4)` directly into `cp "%s"` broadcasts. |
| `0x2D0` | `char *target` | High | Link-walk code loads `*(ent + 0x2d0)` and passes it to `G_Find(..., 0x2d4, target)`, matching source `target`. |
| `0x2D4` | `char *targetname` | High | The same `G_Find` call searches other entities by this string slot, matching source `targetname`. |
| `0x2E4` | `float speed` | High | Retail mover setup defaults `*(ent + 0x2e4)` to `100` when zero and then uses that float to compute `trDuration = distance * 1000 / speed`, matching source `speed`. |
| `0x2E8` | `vec3_t movedir` | High | Door/train/mover setup computes and stores a 3-float direction vector at `0x2e8/0x2ec/0x2f0`, then reuses it for movement and plane-projection math, matching source `movedir`. |
| `0x2F4` | `int nextthink` | High | Delayed-use entities schedule a future timestamp here before returning. |
| `0x2F8` | `think` | High | The same delayed-use path stores a callback here after scheduling `nextthink`. |
| `0x300` | `reached` | High | Retail mover init stores the `Reached_BinaryMover` body at this slot, and the same callback emits the preserved `bad moverState` diagnostic while flipping between `pos1` and `pos2`, matching source `reached`. |
| `0x304` | `blocked` | High | Door/mover spawn paths store a two-argument callback at `0x304`, and the recovered body takes `(self, other)` and performs the expected `Blocked_Door` style reverse/damage logic, matching source `blocked`. |
| `0x308` | `touch` | Medium | Item/temp-item spawn helpers assign function pointers here immediately after storing the item pointer, matching source `touch` placement in the retail callback block. |
| `0x30C` | `use` | High | Retail calls this slot as `(*(ent + 0x30c))(ent, 0, 0)` in target-use scans and spawn helpers assign use handlers here. |
| `0x310` | `pain` | High | The retail damage path checks `if (*(targ + 0x320) > 0)` and then calls the function pointer at `0x310` as `(targ, attacker, damage)`, matching source `targ->pain(targ, attacker, take)`. |
| `0x314` | `die` | High | The same damage path clamps negative health, stores the attacker into `*(targ + 0x344)`, and then calls the function pointer at `0x314` as `(targ, inflictor, attacker, damage, mod)`, matching source `targ->die(...)`. |
| `0x318` | `pain_debounce_time` | High | Retail `P_DamageFeedback` / `P_WorldEffects` gate pain sounds and falling/lava/slime/drowning damage on this timestamp, then refresh it with `level.time + 200` or `+700`, matching source `pain_debounce_time`. |
| `0x31C` | `fly_sound_debounce_time` | High | Retail jump-pad / windfly handling compares this slot against `level.time`, refreshes it to `level.time + 1500`, and plays `"sound/world/jumppad.wav"` only when the debounce expires, matching source `fly_sound_debounce_time`. |
| `0x320` | `health` | High | The spawn-key descriptor table binds `"health"` to offset `0x320`, and retail damage/heal paths clamp, decrement, and mirror this slot into `client->ps.stats[STAT_HEALTH]`, matching source `health`. |
| `0x324` | `takedamage` | High | Damage entry points early-out when `*(ent + 0x324) == 0`, spawn helpers set it to `1` for hurtful/interactive entities, and chain toggles clear or set the same slot in bulk, matching source `takedamage`. |
| `0x328` | `damage` | High | The same spawn-key descriptor table binds `"dmg"` to offset `0x328`, and retail drowning/world-damage logic increments this slot by `2`, caps it at `15`, and feeds it into `G_Damage`, matching source `damage`. |
| `0x330` | `splashDamage` | High | Retail grenade / rocket / plasma / BFG constructors write the second missile-damage scalar here immediately after `damage`, and later splash-adjustment helpers rescale the same slot, matching source `splashDamage`. |
| `0x334` | `splashRadius` | High | The same missile constructors populate this slot with the third damage/config scalar, and proximity checks compare distances directly against `*(ent + 0x334)`, matching source `splashRadius`. |
| `0x338` | `methodOfDeath` | High | Retail missile constructors store the primary `MOD_*` enum here (`4`, `6`, `8`, `0xC` for grenade/rocket/plasma/BFG), matching source `methodOfDeath`. |
| `0x33C` | `splashMethodOfDeath` | High | The adjacent missile-constructor slot carries the paired splash `MOD_*` enum (`5`, `7`, `9`, `0xD`), matching source `splashMethodOfDeath`. |
| `0x340` | `count` | High | The retail spawn-key descriptor table binds `"count"` directly to offset `0x340`, matching source `count`. |
| `0x344` | `gentity_t *enemy` | High | The retail damage path stores the attacker here immediately before invoking the `die` callback, and other gameplay helpers reuse the same pointer as the current opposing/linked entity, matching source `enemy`. |
| `0x348` | `gentity_t *activator` | High | Delayed-use and binary-mover paths store the current activator in `*(ent + 0x348)` and later tailcall `G_UseTargets(ent, ent->activator)` through the same pointer, matching source `activator`. |
| `0x350` | `gentity_t *teammaster` | High | Team-slave mover helpers follow `*(ent + 0x350)` while `FL_TEAMSLAVE` is set to recover the owning master entity, matching source `teammaster`. |
| `0x354` | `gentity_t *teamchain` | High | `MatchTeam`-style loops iterate `for (i = ent; i != 0; i = *(i + 0x354))`, matching source `teamchain`. |
| `0x358` | `kamikazeTime` | High | Retail kamikaze setup stamps the spawned `"kamikaze"` entity with `*(ent + 0x358) = level.time`, and the main kamikaze think path only re-applies the radial damage wave when `*(ent + 0x358) <= level.time` before refreshing it to `level.time + 3000`, matching source `kamikazeTime`. |
| `0x35C` | `kamikazeShockTime` | High | The same kamikaze controller keeps a second `<= level.time` gate at `0x35C` for the shockwave/knockback pass and refreshes it to `level.time + 3000`, matching source `kamikazeShockTime`. |
| `0x360` | `watertype` | High | Retail `P_WorldEffects` and `G_SetClientSound` both treat this slot as a contents bitmask, testing `0x8`/`0x10`/`0x18` for lava and slime exactly where the source reads `ent->watertype`. |
| `0x364` | `waterlevel` | High | Retail `ClientSpawn` zeroes this slot, `ClientThink_real` writes pmove waterlevel back into it, and `P_WorldEffects` / `G_SetClientSound` test it as the `0/1/2/3` submersion level, matching source `waterlevel`. |
| `0x368` | `noise_index` | High | Trigger and speaker setup paths load a sound index into this slot with `"sound/world/jumppad.wav"` and `"sound/world/electro.wav"`, then later reuse `*(ent + 0x368)` for `s.loopSound` and `EV_GENERAL_SOUND`/`EV_GLOBAL_SOUND`, matching source `noise_index`. |
| `0x370` | `float wait` | High | Delayed-use / target-speaker paths parse `"wait"` into this slot and use it in `nextthink = level.time + (wait + crandom()*random) * 1000`. |
| `0x374` | `float random` | High | The same helpers parse `"random"` here and use it as the multiplier in the `crandom()` term. |
| `0x378` | `int itemAvailableTime` | High | `RespawnItem` and `FinishSpawningItem` both stamp `level.time` into this slot exactly when the item becomes live, and the retail pickup-stat helpers later accumulate `level.time - itemAvailableTime` into repeated-pickup timing totals. |
| `0x37C` | `gitem_t *item` | High | Item entities store the selected item definition here, and later code dereferences `*(ent + 0x37c)` into item metadata at `+0x34` / `+0x38`. |
| `0x380` | `int itemPickupCount` | High | `Touch_Item` increments this slot on every successful pickup, and the retail pickup-stat helpers use zero versus positive counts to split first-pickup versus repeat-pickup telemetry. |

## Open questions

- `0x298-0x29B` is still open; source suggests a `prevTrain`-style back-link there, but this round did not find a direct retail read/write chain strong enough to promote it.
- `0x2D8-0x2E3` is still only partially understood; it should contain the remaining target/team/shader-adjacent pointers ahead of `speed`.
- `0x2FC-0x2FF` is still open; retail keeps a live 4-byte gap between `think` and the confirmed `reached` callback slot at `0x300`.
- `0x32C-0x32F` is still open; retail missile-scaling helpers touch it as a standalone slot, but this round did not recover a stable source-faithful name for it.
- `0x34C-0x34F` is still open; there are real retail reads in sort/state helpers, but the current corpus does not justify a stable name yet.
- `0x36C-0x36F` is still open; current retail reads show a live boolean/state slot next to the confirmed sound/water block, but not with enough context to promote a source-faithful name.
