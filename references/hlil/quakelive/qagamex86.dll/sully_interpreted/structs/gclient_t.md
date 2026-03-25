# gclient_t layout (Quake Live `qagamex86.dll`)

The retail client array lives at `data_105ad180` with a stride of `0xBD8`
bytes. This pass keeps `gclient_t` focused on the stable top-level block
boundaries while the new `clientPersistant_t.md`, `clientSession_t.md`, and
`playerTeamState_t.md` notes carry the per-member recovery for the nested
overlays.

## Mapped members

| Offset | Field | Notes |
| ------ | ----- | ----- |
| `0x000` | `player_state_and_linkage[0x250]` | `ClientBegin` clears the leading `0x250` bytes before rebuilding the live player state, preserving the classic `ps`-first rule while still covering Quake Live’s adjacent linkage/state. |
| `0x250-0x347` | `pers` | Retail `clientPersistant_t` overlay. The evidence-backed members now include `connected`, `localClient`, `initialSpawn`, `predictItemPickup`, `netname`, the short `userinfo_c_string`, `steam_id_low/high`, `maxHealth`, `voteCount`, `complaint_count`, `complaint_client`, `complaint_end_time`, `complaint_damage_received`, `complaint_damage_given`, `ready_latch`, `recording_preferences`, `enterTime`, `team_state_state`, `team_state_runtime`, and the inactivity/flood counters. See `clientPersistant_t.md` for the per-member breakdown. |
| `0x348-0x37F` | `sess` | Retail `clientSession_t` overlay. The evidence-backed members are `sessionTeam`, `spectatorTime`, `spectatorState`, `spectatorClient`, `selected_spawn_weapon`, `wins`, `losses`, `teamLeader`, `privilege`, `spectate_only`, `spectator_queue_position`, `spectator_queue_position_dirty`, `muted`, and the unresolved serialized tail at `+0x34`. See `clientSession_t.md` for the per-member breakdown. |
| `0x380` | `noclip` | Noclip cheat state toggled by the `noclip` command path and consulted by combat/stat code. |
| `0x3B8` | `last_hurt_client` | Victim-side last-attacker tracker. The combat path stores the attacker client number here. |
| `0x3BC` | `last_killed_client` | Attacker-side last-kill tracker. The combat path stores the killed client number here. |
| `0x3E4` | `revenge_kill_streaks[64]` | Per-opponent revenge counters. The combat path increments `client[other]`, checks the opposite direction for the `REVENGE` award threshold, and clears the opposing counter after the award or death flow. |
| `0x504` / `0x508` | `factory_regen_armor_accumulator_ms` / `factory_regen_health_accumulator_ms` | Per-frame regeneration accumulators consumed by the retail-only `G_RunFactoryArmorRegen` and `G_RunFactoryHealthRegen` helpers. Both fields accumulate incoming `msec` until the matching regen interval expires. |
| `0x514` / `0x518` | `factory_regen_health_pending` / `factory_regen_armor_pending` | Damage-driven regen latches. The damage path sets them when factory regen is enabled, and the retail regen helpers clear them once health or armor reaches the configured target. |
| `0x568` | `command_time_seed` | Randomised command clock seed populated on connect and reused by the Quake Live backend event/stat publishers. |
| `0x56C` | `command_time_base` | `level.time` snapshot paired with the command seed. |
| `0x570` | `command_time_delta` | Delta between the current server time and the prior command window. |
| `0x578` / `0x57C` | `restart_queue_position` / `restart_queue_rejoin` | Team rebuild / restart queue metadata already recovered in the prior qagame tournament pass. |
| `0x580` / `0x584` | `team_seed_rank` / `team_seed_reused` | Team seeding metadata already recovered in the prior tournament/team reconstruction pass. |
| `0x588` / `0x58C` | `kill_count` / `death_count` | Running kill/death totals incremented from the obituary path and later emitted through the retail stat/back-end publishers. |
| `0x594` / `0x598` | `team_damage_events_given` / `team_damage_events_received` | Team-damage incident counters. The team-damage complaint path increments the attacker's slot at `0x594` and the victim's slot at `0x598` once per friendly-fire event. |

## Important corrections

- `0x250-0x347` is no longer treated as a generic persisted blob. Retail keeps
  a real `clientPersistant_t` overlay here, but it is not source-faithful after
  the early `cmd`/userinfo seam.
- `0x2E8` is the dedicated Quake Live ready/continue latch inside `pers`, not a
  complaint or session field.
- `0x2FC-0x32B` is the retail `team_state_runtime` overlay inside `pers`, not a
  clean carryover of source `playerTeamState_t`.
- `0x348-0x37F` is a retail `clientSession_t` overlay, not a flat GPL session
  copy.
- `0x358` is a persisted starting-weapon/loadout selection, `0x35C/0x360` are
  wins/losses, `0x364` is `teamLeader`, `0x368` is `privilege`, and
  `0x36C/0x370/0x374` are the Quake Live `so` / `pq` queue fields plus the live
  dirty bit.
- `0x378` is the mute latch and `0x380` is the noclip flag.
- `0x2E0/0x2E4` inside `pers` are no longer treated as unknown complaint
  metadata. Retail uses them as pending friendly-fire damage received/given
  accumulators toward the complaint prompt threshold, not the current source
  tree's `complaintTarget`-style target latch.
- `0x504/0x508/0x514/0x518` are no longer part of an undifferentiated stat pad.
  Retail keeps the factory health/armor regen accumulators and pending latches
  as standalone client fields consumed by the recovered regen sidecars.
- `0x588/0x58C/0x594/0x598` are no longer left entirely inside the generic
  weapon/stat block. The obituary and complaint paths prove these slots carry
  kill/death totals plus team-damage event counters.

## Open spans

- `pers.cmd_field_18`, `pers.field_50`, `pers.field_6c`,
  `pers.field_a0`, and the trailing `pers.tail_pad` bytes still need cleaner
  promotion work.
- `sess.field_34` at `gclient + 0x37C` remains unresolved inside the retail
  session tail.
- `0x384-0x3B7`, most of `0x3C0-0x503`, `0x50C-0x513`, `0x51C-0x587`, and the
  remaining `0x59C+` span still hold the broader combat, award, and weapon-stat
  expansions that Quake Live layered on top of the GPL layout.
