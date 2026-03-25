# clientPersistant_t layout

## Source-canonical layout

The GPL `clientPersistant_t` is still a `0x27C`-byte record. This pass
promotes that source member order directly in `src/game/ql_game_types.h` so the
retail drift can be described against a stable baseline instead of a stale flat
guess inside `gclient_t`.

| Source offset | Field | Notes |
| ------ | ----- | ----- |
| `0x000` | `connected` | Connection state (`CON_DISCONNECTED` / `CON_CONNECTING` / `CON_CONNECTED`). |
| `0x004` | `cmd` | Source `usercmd_t` snapshot preserved across respawns. |
| `0x01C` | `localClient` | True when the userinfo `"ip"` key is `"localhost"`. |
| `0x020` | `initialSpawn` | First-spawn placement latch. |
| `0x024` | `predictItemPickup` | Source prediction toggle from userinfo. |
| `0x028` | `pmoveFixed` | Source fixed-pmove toggle from userinfo. |
| `0x02C` | `netname[36]` | Cleaned player name. |
| `0x050` | `maxHealth` | Handicap-capped max health. |
| `0x054` | `enterTime` | `level.time` when the client entered the game. |
| `0x058` | `teamState` | Source `playerTeamState_t` sub-struct. |
| `0x088` | `voteCount` | Vote-call throttle count. |
| `0x08C` | `teamVoteCount` | Source team-vote throttle count. |
| `0x090` | `teamInfo` | Team overlay update toggle. |
| `0x094` | `voteDelayTime` | Vote-selection delay timestamp. |
| `0x098` | `voteLastSelection` | Last vote menu selection. |
| `0x09C` | `voteLastEnableFrame` | Last vote-enable frame. |
| `0x0A0` | `killCommandTime` | Anti-spam timer for the `kill` command. |
| `0x0A4` / `0x0A8` | `ratingDamageScale` / `ratingScoreScale` | Rating metadata scales. |
| `0x0AC` | `ratingMetadataLoaded` | Rating metadata load latch. |
| `0x0B0` | `itemProgressionTier` | Item unlock tier. |
| `0x0B4` | `progressionFlags` | Item progression flag bitmask. |
| `0x0B8` / `0x0BC` | `steamIdLow` / `steamIdHigh` | Source-persisted Steam ID pair. |
| `0x0C0` | `steamIdValid` | Steam ID validity latch. |
| `0x0C4` / `0x0C8` | `damageGiven` / `damageReceived` | Per-life damage accounting. |
| `0x0CC` | `weaponFrags[15]` | Per-weapon frag counters. |
| `0x108` | `weaponDamage[15]` | Per-weapon damage totals. |
| `0x144` | `accuracy_shots[15]` | Per-weapon shots fired. |
| `0x180` | `accuracy_hits[15]` | Per-weapon hits landed. |
| `0x1BC` | `teamScoreStats[18]` | Team score-stat totals. |
| `0x204` | `teamHoldStartTime[18]` | Team hold-start timestamps. |
| `0x24C` | `pickupLastTime[4]` | Last pickup timestamps. |
| `0x25C` | `pickupIntervalTotalMs[4]` | Pickup interval accumulators. |
| `0x26C` | `pickupIntervalCount[4]` | Pickup interval sample counts. |

## Retail Quake Live drift

Retail qagame still keeps a persisted client block at `gclient + 0x250`, but it
is only `0xF8` bytes long before the session overlay starts at `gclient +
0x348`.

- `ClientConnect` and `ClientBegin` still treat the block as the persisted part
  of `gclient_t`, but the retail copy/preserve boundaries prove Quake Live no
  longer stores the full GPL `clientPersistant_t` here.
- Retail inserts one extra dword between the source-compatible `usercmd_t`
  prefix and `localClient`, shifting `localClient` from source `+0x1C` to
  retail `+0x20`.
- `netname` still survives at retail `+0x2C`, but the source
  `maxHealth` / `enterTime` / `teamState` chain no longer follows immediately.
- `ClientUserinfoChanged` copies a short string into `gclient + 0x2A4`
  (`pers + 0x54`) and later formats it as the retail configstring tail
  `\\c\\%s`, so Quake Live has added a distinct short userinfo/configstring
  buffer in the middle of the persisted block.
- The Steam ID pair has moved forward to retail `+0x70/+0x74`, ahead of the
  complaint, ready-up, and recording-preference state.
- The classic `playerTeamState_t` is not preserved as a clean contiguous
  sub-struct here. Retail keeps the surviving `state` enum at `pers + 0xA8`,
  then starts the evidence-backed `team_state_runtime` overlay at `pers + 0xAC`
  (`gclient + 0x2FC`).
- The large source stats tail (`damageGiven` onward) does not survive here as a
  source-faithful sub-struct. Retail stores those systems elsewhere in
  `gclient_t` or in Quake Live-specific layouts that still need separate
  recovery.

## Evidence-backed retail overlay

The retail overlay in `ql_game_types.h` is modeled relative to `gclient->pers`.

| Retail offset | gclient offset | Field | Confidence | Evidence |
| ------ | ----- | ----- | ---------- | -------- |
| `0x00` | `0x250` | `connected` | High | `ClientConnect` seeds this slot with `1`, `ClientBegin` upgrades it to `2`, and disconnect clears it. |
| `0x04` | `0x254` | `cmd` | Medium | Retail still preserves the source-compatible `usercmd_t` prefix here; the extra dword after it is what shifts `localClient`. |
| `0x1C` | `0x26C` | `cmd_field_18` | Low | The early command/persist seam extends through `0x26B-0x26D`, but no stable retail name is promoted for the final dword yet. |
| `0x20` | `0x270` | `localClient` | High | `ClientUserinfoChanged` sets this when userinfo `"ip"` equals `"localhost"`, and levelshot/local-client helpers read the same slot. |
| `0x24` | `0x274` | `initialSpawn` | Medium | Spawn/bootstrap code toggles this in the first-spawn path, matching the source role closely enough to promote the classic name. |
| `0x28` | `0x278` | `predictItemPickup` | High | `ClientUserinfoChanged` seeds this slot directly from the `"cg_predictItems"` userinfo key, and the retail item-pickup path reads the same dword as the prediction toggle before deciding whether to emit the immediate pickup event or queue the predictable client-side path.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L40677-L40677】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L56082-L56082】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L55807-L55807】 |
| `0x2C` | `0x27C` | `netname[36]` | High | Name-cleaning, chat, print, and configstring code all pass `gclient + 0x27C` as the canonical player name buffer. |
| `0x50` | `0x2A0` | `field_50` | Low | The dword between `netname` and the retail short string is structurally required but still unnamed. |
| `0x54` | `0x2A4` | `userinfo_c_string[24]` | High | `ClientUserinfoChanged` copies a 23-character string here, terminates it locally, and later feeds it into the `\\c\\%s` configstring fragment. |
| `0x6C` | `0x2BC` | `field_6c` | Low | The four-byte seam before the Steam ID pair is still open. |
| `0x70` / `0x74` | `0x2C0` / `0x2C4` | `steam_id_low` / `steam_id_high` | High | `ClientConnect` receives the Steam64 pair from the engine callback and stores it here. |
| `0x78` | `0x2C8` | `maxHealth` | High | `ClientUserinfoChanged` computes the handicap-capped max health here and mirrors it into `ps.stats`; `ClientSpawn` reuses it when seeding health. |
| `0x7C` | `0x2CC` | `voteCount` | High | Vote command handling rejects additional calls when this counter reaches the retail vote limit. |
| `0x80` | `0x2D0` | `voteState` | Medium | Vote setup assigns connected clients `0`, `1`, or `2` here depending on eligibility/caller state, but the exact stock name is still open. |
| `0x84` | `0x2D4` | `complaint_count` | High | Complaint handling increments this slot on accepted complaints and compares it against the punishment threshold. |
| `0x88` | `0x2D8` | `complaint_client` | High | Victim-side complaint target client index. Disconnect clears matching pending complaints. |
| `0x8C` | `0x2DC` | `complaint_end_time` | High | Victim-side complaint expiry time paired with `complaint_client`. |
| `0x90` | `0x2E0` | `complaint_damage_received` | High | The retail team-damage complaint path increments this slot on the victim by the friendly-fire damage amount, checks it against `g_complaintDamageThreshold`, and clears it once a complaint prompt is issued. |
| `0x94` | `0x2E4` | `complaint_damage_given` | High | The same path increments this slot on the attacker by the friendly-fire damage amount, checks it against the same threshold, and clears it when the complaint prompt or spectator rejection path resolves. |
| `0x98` | `0x2E8` | `ready_latch` | High | `Cmd_ReadyUp_f`, `Cmd_AllReady_f`, and `CheckIntermissionExit` all use this as the retail ready/continue latch. |
| `0x9C` | `0x2EC` | `recording_preferences` | Medium | `ClientUserinfoChanged` seeds bitflags here and the match-start/end autoaction helpers check bits `1` and `2` to drive `record` / `screenshot` behavior. |
| `0xA0` | `0x2F0` | `field_a0` | Low | Persisted timer/state slot still open. |
| `0xA4` | `0x2F4` | `enterTime` | High | `ClientBegin` stores `level.time` here, and award/rank logic later uses elapsed time from the same slot. |
| `0xA8` | `0x2F8` | `team_state_state` | High | `ClientBegin` and `SetTeam` both reset this slot to `0`, matching source `client->pers.teamState.state = TEAM_BEGIN`; the retail `ClientSpawn` path then reads the same slot during CTF/team spawn selection and later stores `1`, matching source `TEAM_ACTIVE`.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41214-L41214】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L45260-L45260】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L39980-L39980】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41820-L41820】 |
| `0xAC` | `0x2FC` | `team_state_runtime` | High | Retail teamplay counters and timer stamps live here; see `playerTeamState_t.md` for the per-member breakdown. |
| `0xDC` | `0x32C` | `inactivity_accumulator_ms` | High | `ClientInactivityTimer` accumulates `level.msec` here while the player is idle. |
| `0xE0` | `0x330` | `inactivity_warning` | High | Warning latch used by the inactivity centerprint path. |
| `0xE4` | `0x334` | `flood_last_time` | High | Retail flood-decay timestamp consumed by `G_CheckClientFlood`. |
| `0xE8` | `0x338` | `flood_count` | High | Retail client-flood counter compared against the flood limit. |
| `0xEC` | `0x33C` | `tail_pad[12]` | Low | The last persisted/session-adjacent bytes before `sess` are still unresolved. |

## Open questions

- `userinfo_c_string` is structurally solid, but its gameplay meaning beyond
  “the short string emitted as `\\c\\%s` in the player configstring” is still
  open.
- `field_a0` and the trailing `0x33C-0x347` span still need cleaner promotion
  work.
- The source statistics tail from `damageGiven` onward has not been relocated
  one-for-one in retail yet; it should be handled as a separate follow-up once
  the broader combat/stat blocks later in `gclient_t` are mapped more fully.
