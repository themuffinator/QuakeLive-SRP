# Gameplay CVar Notes

## Custom Settings Digest

Quake Live servers expose `g_customSettings` as a synthesized digest of gameplay overrides so browsers can advertise when a match differs from stock rules. Retail registers the row with default `0` and `CVAR_SERVERINFO`; the VM mirrors that surface while keeping ownership in game code, which rewrites the value whenever tracked CVars deviate and publishes the same payload through `CS_CUSTOM_SETTINGS`.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L718-L721】【F:src/code/game/g_main.c†L2163-L2187】 The server flags any custom-marked CVar in the registration table, flips a shared dirty bit inside `G_UpdateCvars`, and exposes helper functions so future digest rebuilds know when to refresh the string before pushing it to clients.【F:src/code/game/g_main.c†L1698-L1734】【F:src/code/game/g_main.c†L1922-L1942】 Because the value is synthesized from other knobs, admins should treat `g_customSettings` as telemetry rather than a toggle; changing it manually will be overwritten the next time gameplay CVars update.

## Match Timeout Controls

Competitive duel and team modes now expose Quake Live–style match pauses. Players call `timeout` (alias `pause`) to consume one of their team's `g_timeoutCount` allotments, freezing play, logging the owner, and sharing the pause state through `CS_MATCH_STATE` for HUD parity.【F:src/code/game/g_cmds.c†L1593-L1675】【F:src/code/game/g_main.c†L2100-L2149】 The server starts the countdown using `g_timeoutLen` and remembers when the break began so resuming can credit the lost time back to warmup and intermission timers.【F:src/code/game/g_cmds.c†L1657-L1670】【F:src/code/game/g_main.c†L2133-L2149】

`timein` (aliases `resume`, `unpause`) returns the match to live play either on demand or after the configured duration expires. The resume path shifts warmup countdowns, queued exits, and intermission delays by the paused interval so countdowns continue smoothly once action resumes, mirroring Quake Live's behaviour.【F:src/code/game/g_cmds.c†L1678-L1712】【F:src/code/game/g_main.c†L2133-L2149】【F:src/code/game/g_main.c†L2295-L2316】

| Command | Aliases | Notes |
| --- | --- | --- |
| `timeout` | `pause` | Pauses the match if the caller's side has timeouts remaining; sets up `timeoutOwner`, `timeoutStartTime`, and an optional auto-expiry from `g_timeoutLen`.【F:src/code/game/g_cmds.c†L1632-L1670】 |
| `timein` | `resume`, `unpause` | Resumes play for the calling side, reapplies the paused duration to warmup/exit timers, and clears the match state configstring flags.【F:src/code/game/g_cmds.c†L1678-L1712】【F:src/code/game/g_main.c†L2133-L2149】 |

| CVar | Default | Notes |
| --- | --- | --- |
| `g_timeoutCount` | `0` | Number of timeouts each team receives per match; initialised into `level.timeoutRemaining` and published via `CS_MATCH_STATE` for client HUDs.【F:src/code/game/g_main.c†L1093-L1121】【F:src/code/game/g_main.c†L2100-L2131】 |
| `g_timeoutLen` | `60` | Timeout duration in seconds; values ≤0 hold the pause until a manual `timein`, while positive values trigger an automatic resume with broadcast messaging.【F:src/code/game/g_cmds.c†L1657-L1670】【F:src/code/game/g_main.c†L2295-L2316】 |

## Match Flow, Warmup, Timeout, and Spawn Grant Controls

This tranche rechecks the match-state, team-damage, memory-debug, warmup, timeout, and spawn-grant rows against the retail qagame registration slab. Quake Live keeps warmup and timeout values split between archived admin defaults and gamerule-protected match controls: `g_warmup` remains archived with the retail `10` second default, while `g_timeoutCount` defaults to `0` and only becomes active when a factory or server rule explicitly changes it.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L848-L858】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L981-L991】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L2559-L2569】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L2642-L2665】

| CVar | Default | Retail flags | Notes |
| --- | --- | --- | --- |
| `g_gameState` | `PRE_GAME` | `CVAR_SERVERINFO \| CVAR_ROM` | Published by `G_SetGameState` as warmup/intermission state changes so clients and Steam achievement gates can observe match phase.【F:src/code/game/g_main.c†L907-L907】【F:src/code/game/g_main.c†L232-L244】 |
| `g_friendlyFire` | `0` | `CVAR_GAMERULE` | Gates team-damage protection in both generic damage and Attack & Defend round damage paths; the row is no longer archived like the legacy source default.【F:src/code/game/g_main.c†L971-L971】【F:src/code/game/g_combat.c†L1853-L1853】【F:src/code/game/g_team.c†L867-L867】 |
| `g_debugAlloc` | `0` | `0` | Enables the retail game-memory allocation print path without advertising or persisting the toggle.【F:src/code/game/g_main.c†L1058-L1058】【F:src/code/game/g_mem.c†L39-L40】 |
| `g_grantItemOnSpawn` | *(empty)* | `CVAR_GAMERULE` | Parsed by the spawn grant helper each time `ClientSpawn` runs, while the gamerule flag blocks early client-init overrides.【F:src/code/game/g_main.c†L1002-L1002】【F:src/code/game/g_client.c†L2118-L2122】 |
| `g_doWarmup` | `1` | `CVAR_ARCHIVE` | Enables warmup countdown flow and now preserves the retail archived admin default.【F:src/code/game/g_main.c†L1076-L1076】【F:src/code/game/g_spawn.c†L1175-L1180】 |
| `g_warmup` | `10` | `CVAR_ARCHIVE` | Seeds duel/default countdown length and updates active warmup deadlines when changed.【F:src/code/game/g_main.c†L1075-L1075】【F:src/code/game/g_gametype_lifecycle.inc†L207-L213】【F:src/code/game/g_main.c†L7863-L7885】 |
| `g_warmupReadyDelay` | `0` | `0` | Arms the duel ready-up delay deadline after exactly one duelist is ready; `0` leaves the controller disabled.【F:src/code/game/g_main.c†L1077-L1077】【F:src/code/game/g_main.c†L7400-L7417】 |
| `g_warmupReadyDelayAction` | `1` | `0` | Chooses the retail ready-delay consequence: action `1` moves the unready duelist to spectators, while `2` forces ready state.【F:src/code/game/g_main.c†L1078-L1078】【F:src/code/game/g_main.c†L7437-L7444】 |
| `g_timeoutCount` | `0` | `CVAR_SERVERINFO \| CVAR_GAMERULE` | Loads into match config, refills remaining timeout pools on rule changes, and is published through match-state configstrings.【F:src/code/game/g_main.c†L1087-L1087】【F:src/game/g_match_config.c†L242-L243】【F:src/code/game/g_main.c†L7708-L7718】 |
| `g_timeoutLen` | `60` | `CVAR_GAMERULE` | Loads into match config as the finite timeout duration; values at or below zero keep player-called timeouts disabled.【F:src/code/game/g_main.c†L1086-L1086】【F:src/game/g_match_config.c†L242-L242】【F:src/code/game/g_cmds.c†L6139-L6155】 |

## Team Warmup and Shuffle Controls

Public servers often want to keep Clan Arena and TDM warmups idle until both teams are ready, then auto-shuffle if players stack one side. The following CVars expose those Quake Live semantics: warmups watch `g_teamSizeMin` and `g_teamForcePresent` before starting countdowns, and the shuffle suite (`g_shuffle_*`) arms timed shuffles as soon as player deltas exceed the configured thresholds.【F:src/code/game/g_main.c†L2738-L2798】【F:src/code/game/g_team.c†L200-L520】 Auto-shuffle countdowns clamp the warmup timer, emit HUD messages, and cancel themselves if balance returns, matching the original console feedback.【F:src/code/game/g_team.c†L435-L506】

| CVar | Default | Notes |
| --- | --- | --- |
| `g_teamSizeMin` | `1` | Minimum players required per team before warmup timers run in team modes; respawn ratios use this number to report readiness via the match-state configstring.【F:src/code/game/g_team.c†L230-L310】【F:src/code/game/g_match_state.c†L71-L108】 |
| `g_teamForcePresent` | `1` | When non-zero, both teams must individually meet `g_teamSizeMin` before live play begins; otherwise the server only enforces the total minimum across both teams.【F:src/code/game/g_team.c†L474-L520】 |
| `g_shuffle_timedelay` | `5000` | Milliseconds to wait between arming an automatic shuffle and executing it; set to `0` to shuffle instantly once conditions are met.【F:src/code/game/g_team.c†L1503-L1520】 |
| `g_shuffle_minplayers` | `3` | Minimum total players required before shuffle logic will consider arming when the automatic-specific threshold is unset.【F:src/code/game/g_team.c†L1291-L1301】 |
| `g_shuffle_automatic` | `0` | Enables Quake Live-style automatic team shuffles during warmup whenever the configured player difference remains lopsided.【F:src/code/game/g_team.c†L1311-L1330】 |
| `g_shuffle_automatic_minplayers` | `6` | Overrides `g_shuffle_minplayers` for automatic shuffles so admins can require fuller teams before the countdown begins.【F:src/code/game/g_team.c†L1291-L1301】 |

Auto-shuffle state is mirrored to clients through `CS_MATCH_STATE`, letting HUDs display team counts, respawn ratios, and the pending countdown so spectators see when a shuffle will trigger.【F:src/code/game/g_match_state.c†L71-L118】【F:src/code/cgame/cg_servercmds.c†L900-L990】

## Access, Attack & Defend, Flood, Drop, and Knockback Rows

This tranche rechecks ten scattered `g_*` controls that were not part of the prior vote, round-mode, Red Rover, or weapon-specific batches. Retail keeps admin access and flood controls as local runtime rows, publishes Attack & Defend scoring through `CVAR_SERVERINFO | CVAR_GAMERULE`, and treats drop-health, max-knockback, return-on-suicide, and vampiric damage as gamerule-owned gameplay knobs rather than archived legacy settings.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L561-L579】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L1001-L1108】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L1577-L1581】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L1905-L1909】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L2580-L2584】

| CVar | Default | Retail flags | Notes |
| --- | --- | --- | --- |
| `g_accessFile` | `access.txt` | `0` | Names the symbolic admin access list loaded at game init and by `reload_access`, then written back by the same access-file owner.【F:src/code/game/g_main.c†L991-L991】【F:src/code/game/g_main.c†L2356-L2467】 |
| `g_adTouchScoreBonus` | `1` | `CVAR_SERVERINFO \| CVAR_GAMERULE` | Adds the Attack & Defend touch bonus to both player and team score, with the team centerprint announcement preserved.【F:src/code/game/g_main.c†L1030-L1030】【F:src/code/game/g_team.c†L194-L206】【F:src/code/game/g_team.c†L4069-L4069】 |
| `g_adElimScoreBonus` | `2` | `CVAR_SERVERINFO \| CVAR_GAMERULE` | Awards the elimination bonus from both current combat and client obituary paths when A&D is active.【F:src/code/game/g_main.c†L1031-L1031】【F:src/code/game/g_combat.c†L1197-L1197】【F:src/code/game/g_client.c†L323-L323】 |
| `g_adCaptureScoreBonus` | `3` | `CVAR_SERVERINFO \| CVAR_GAMERULE` | Stacks the configured capture bonus on top of the base CTF capture score in Attack & Defend.【F:src/code/game/g_main.c†L1032-L1032】【F:src/code/game/g_team.c†L3970-L3970】 |
| `g_floodprot_maxcount` | `10` | `0` | Sets the shared command/chat burst limit used by active-client decay, command gating, and `floodstatus`.【F:src/code/game/g_main.c†L1016-L1016】【F:src/code/game/g_active.c†L786-L805】【F:src/code/game/g_cmds.c†L3001-L3032】 |
| `g_floodprot_decay` | `1000` | `0` | Controls the millisecond decay threshold for the same flood counter; retail still treats `g_floodprot_maxcount` as the only limiter on/off switch.【F:src/code/game/g_main.c†L1017-L1017】【F:src/code/game/g_active.c†L786-L805】 |
| `g_dropDamagedHealth` | `0` | `CVAR_TEMP \| 0x00040000 \| CVAR_GAMERULE` | Enables dropped health pickups to preserve their stored damaged count; the custom-settings bit now follows non-zero values instead of firing at the retail default.【F:src/code/game/g_main.c†L1026-L1026】【F:src/code/game/g_items.c†L481-L490】【F:src/code/game/g_main.c†L2173-L2174】 |
| `g_max_knockback` | `120` | `CVAR_GAMERULE` | Caps only positive weapon-scaled knockback and uses the same retail fallback in the cached knockback config and damage path.【F:src/code/game/g_main.c†L1078-L1078】【F:src/game/g_config.c†L908-L915】【F:src/code/game/g_combat.c†L1761-L1765】 |
| `g_returnFlagOnSuicide` | `0` | `CVAR_GAMERULE` | Caches into `g_flagConfig.returnOnSuicide`; enabling it restores immediate carried-flag returns on suicide.【F:src/code/game/g_main.c†L1038-L1038】【F:src/code/game/g_main.c†L1442-L1442】 |
| `g_vampiricDamage` | `0` | `0x00040000 \| CVAR_GAMERULE` | Heals attackers for a fraction of dealt health damage and advertises the custom setting/server tag only when the value is positive.【F:src/code/game/g_main.c†L1100-L1100】【F:src/code/game/g_combat.c†L1613-L1656】【F:src/code/server/sv_main.c†L919-L919】 |

## Freeze Reset, Last-Man, and Red Rover Zombie Retail Rows

This tranche rechecks ten adjacent round-mode controls that were not closed by the earlier round/Frozen timing or Red Rover infection batches. Retail keeps the Freeze thaw/reset rows and the Red Rover zombie spawn-trait rows on `CVAR_GAMERULE`, while the last-man-standing warning/message rows are plain runtime controls. The default changes are user-visible: winners thaw by default in Freeze (`g_freezeThawWinningTeam=1`), and the retail last-man centerprint is `You are the last standing`.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L1170-L1239】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L1531-L1545】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L2039-L2051】

| CVar | Default | Retail flags | Notes |
| --- | --- | --- | --- |
| `g_freezeThawWinningTeam` | `1` | `CVAR_GAMERULE` | Cached into `level.freezeConfig.thawWinningTeam` and used by every Freeze winner-resolution branch before the next round transition.【F:src/code/game/g_main.c†L938-L938】【F:src/code/game/g_active.c†L2405-L2406】【F:src/code/game/g_active.c†L2705-L2784】 |
| `g_freezeThawThroughSurface` | `0` | `CVAR_GAMERULE` | Cached into `level.freezeConfig.thawThroughSurface` and gates line-of-sight checks for thaw helpers.【F:src/code/game/g_main.c†L939-L939】【F:src/code/game/g_active.c†L2405-L2406】【F:src/code/game/g_freeze.c†L281-L281】 |
| `g_freezeResetWeaponsOnRound` | `1` | `CVAR_GAMERULE` | Respawns active Freeze players with the current factory loadout when a round resets.【F:src/code/game/g_main.c†L944-L944】【F:src/code/game/g_active.c†L2411-L2414】【F:src/code/game/g_active.c†L2512-L2517】 |
| `g_freezeResetHealthOnRound` | `1` | `CVAR_GAMERULE` | Restores player health to max when Freeze round reset does not perform a full respawn.【F:src/code/game/g_main.c†L945-L945】【F:src/code/game/g_active.c†L2411-L2414】【F:src/code/game/g_active.c†L2522-L2524】 |
| `g_freezeResetArmorOnRound` | `1` | `CVAR_GAMERULE` | Restores factory starting armor and refreshes tiered-armor state during Freeze round resets.【F:src/code/game/g_main.c†L946-L946】【F:src/code/game/g_active.c†L2411-L2414】【F:src/code/game/g_active.c†L2526-L2528】 |
| `g_freezeRemovePowerupsOnRound` | `1` | `CVAR_GAMERULE` | Strips active powerups during Freeze reset restores when the player is not fully respawned.【F:src/code/game/g_main.c†L947-L947】【F:src/code/game/g_active.c†L2411-L2414】【F:src/code/game/g_active.c†L2530-L2531】 |
| `g_lastManStandingWarning` | `1` | `0` | Gates CA, Freeze, Attack & Defend, and Red Rover last-alive alerts without persisting the toggle as an archived server option.【F:src/code/game/g_main.c†L967-L967】【F:src/code/game/g_team.c†L573-L820】 |
| `g_lastManStandingMessage` | `You are the last standing` | `0` | Supplies the centerprint payload sent to the lone live player, with the source fallback now matching the retail default string.【F:src/code/game/g_main.c†L968-L968】【F:src/code/game/g_team.c†L594-L604】【F:src/code/game/g_team.c†L683-L685】 |
| `g_rrInfectedZombieHealthBonus` | `50` | `CVAR_GAMERULE` | Adds the retail infected health bonus during Red Rover zombie spawn finalization and clamps the resulting max health.【F:src/code/game/g_main.c†L955-L955】【F:src/code/game/g_client.c†L2371-L2399】 |
| `g_rrInfectedZombieSpeed` | `1.15` | `CVAR_GAMERULE` | Multiplies infected Red Rover player speed each active frame, matching the retail cvar-backed pmove speed adjustment.【F:src/code/game/g_main.c†L956-L956】【F:src/code/game/g_client.c†L3321-L3341】 |

## Red Rover Infection Retail Rows

This tranche rechecks the Red Rover infection controls against the retail qagame cvar slab. The retail rows keep the infection scoring, spread, and survivor-warning knobs as `CVAR_GAMERULE`, while the master `g_rrInfected` switch adds the recovered `CVAR_LATCH | 0x00040000` surface. The default slab also preserves the literal `500.0f` survivor minimum-speed string, which differs from the older integer-looking source default.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L1952-L2029】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L45513-L45554】

| CVar | Default | Retail flags | Notes |
| --- | --- | --- | --- |
| `g_rrAllowNegativeScores` | `0` | `CVAR_GAMERULE` | Clamps Red Rover score deltas so infection penalties cannot drive scores below zero unless explicitly enabled.【F:src/code/game/g_main.c†L966-L966】【F:src/code/game/g_client.c†L2986-L3029】 |
| `g_rrDamageScoreBonus` | `0` | `CVAR_GAMERULE` | Multiplies survivor damage against infected players when damage-based Red Rover scoring is active.【F:src/code/game/g_main.c†L965-L965】【F:src/code/game/g_client.c†L3590-L3629】 |
| `g_rrInfected` | `0` | `CVAR_LATCH \| 0x00040000 \| CVAR_GAMERULE` | Enables the infection ruleset, advertises the custom-settings infected bit, and gates autojoin, infection seeding, round completion, death conversion, and last-alive notification paths.【F:src/code/game/g_main.c†L964-L964】【F:src/code/game/g_main.c†L2143-L2188】【F:src/code/game/g_cmds.c†L2429-L2439】【F:src/code/game/g_client.c†L3496-L3584】 |
| `g_rrInfectedSpreadTime` | `40` | `CVAR_GAMERULE` | Sets the forced-spread delay in seconds for survivor state initialization and the active-round infection spread check.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L46259-L46259】【F:src/code/game/g_client.c†L3144-L3177】【F:src/code/game/g_client.c†L3253-L3312】 |
| `g_rrInfectedSpreadWarningTime` | `10` | `CVAR_GAMERULE` | Starts the survivor warning countdown before forced infection, including the retail seconds/plural message.【F:src/code/game/g_main.c†L962-L962】【F:src/code/game/g_client.c†L3162-L3177】【F:src/code/game/g_client.c†L3278-L3288】 |
| `g_rrInfectedSurvivorMinSpeed` | `500.0f` | `CVAR_GAMERULE` | Minimum planar survivor speed before the slow-movement warning ping path is allowed to fire.【F:src/code/game/g_main.c†L960-L960】【F:src/code/game/g_client.c†L3320-L3353】 |
| `g_rrInfectedSurvivorPingRate` | `2000` | `CVAR_GAMERULE` | Controls survivor warning-ping cadence and is published through `CS_RR_INFECTED_SURVIVOR_PING_RATE` for client-side parity.【F:src/code/game/g_main.c†L961-L961】【F:src/code/game/g_main.c†L2112-L2138】【F:src/code/game/g_client.c†L3233-L3353】 |
| `g_rrInfectedSurvivorScoreBonus` | `1` | `CVAR_GAMERULE` | Score value awarded by timed survival bonuses and the thresholded damage-score mode.【F:src/code/game/g_main.c†L958-L958】【F:src/code/game/g_client.c†L3073-L3126】【F:src/code/game/g_client.c†L3590-L3629】 |
| `g_rrInfectedSurvivorScoreMethod` | `2` | `CVAR_GAMERULE` | Selects the Red Rover survivor scoring mode used by both periodic survival awards and damage-triggered bonuses.【F:src/code/game/g_main.c†L957-L957】【F:src/code/game/g_client.c†L3073-L3126】【F:src/code/game/g_client.c†L3590-L3629】 |
| `g_rrInfectedSurvivorScoreRate` | `30` | `CVAR_GAMERULE` | Sets the survival-bonus interval in seconds and the damage-threshold accumulator used by score method `0`.【F:src/code/game/g_main.c†L959-L959】【F:src/code/game/g_client.c†L3073-L3126】【F:src/code/game/g_client.c†L3590-L3629】 |

## Round and Freeze Timing Retail Rows

This tranche rechecks the round-controller draw gates, Freeze warmup delay, and Freeze thaw/respawn timers against the retail qagame cvar slab. Quake Live registers the draw toggles and most Freeze timing values as `CVAR_GAMERULE`, while `g_roundWarmupDelay` and `g_freezeRoundDelay` also carry `CVAR_SERVERINFO`; the retail defaults also swap several older source assumptions, notably `g_freezeThawTick=1`, `g_freezeProtectedSpawnTime=0`, `g_freezeEnvironmentalRespawnDelay=5000`, and `g_freezeAutoThawTime=120000`.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L1148-L1208】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L1918-L1934】

| CVar | Default | Retail flags | Notes |
| --- | --- | --- | --- |
| `g_roundWarmupDelay` | `10000` | `CVAR_SERVERINFO \| CVAR_GAMERULE` | Reschedules CA/FZ warmup release and Attack & Defend round transitions when changed mid-warmup.【F:src/code/game/g_main.c†L935-L950】【F:src/code/game/g_active.c†L2433-L2467】 |
| `g_roundDrawLivingCount` | `1` | `CVAR_GAMERULE` | Lets timed-out CA/FZ rounds resolve by remaining living player counts and controls the end-round living-count print.【F:src/code/game/g_active.c†L2087-L2091】【F:src/code/game/g_active.c†L2720-L2816】 |
| `g_roundDrawHealthCount` | `1` | `CVAR_GAMERULE` | Lets timed-out CA/FZ rounds resolve by aggregate team health and controls the end-round health print.【F:src/code/game/g_active.c†L2087-L2091】【F:src/code/game/g_active.c†L2720-L2816】 |
| `g_freezeThawTime` | `2000` | `CVAR_GAMERULE` | Cached into `level.freezeConfig.thawTime` and used as the total ally-assist thaw budget.【F:src/code/game/g_active.c†L2390-L2403】【F:src/code/game/g_client.c†L152-L216】 |
| `g_freezeThawTick` | `1` | `CVAR_GAMERULE` | Cached into `level.freezeConfig.thawTick` and added once per helper tick while allies thaw a frozen player.【F:src/code/game/g_active.c†L2390-L2403】【F:src/code/game/g_client.c†L152-L216】 |
| `g_freezeThawRadius` | `96` | `CVAR_GAMERULE` | Sets the helper-search radius in `G_FreezeCountThawHelpers`, including the line-of-sight gate when through-surface thawing is disabled.【F:src/code/game/g_active.c†L2390-L2403】【F:src/code/game/g_freeze.c†L244-L303】 |
| `g_freezeRoundDelay` | `4000` | `CVAR_SERVERINFO \| CVAR_GAMERULE` | Drives the post-round transition delay and the generic Freeze fallback gate in exit-rule handling.【F:src/code/game/g_active.c†L2407-L2409】【F:src/code/game/g_active.c†L2812-L2830】【F:src/code/game/g_main.c†L7012-L7012】 |
| `g_freezeProtectedSpawnTime` | `0` | `CVAR_GAMERULE` | Sets optional post-thaw protection; `0` keeps retail's default unprotected thaw while retaining the damage suppression path when configured.【F:src/code/game/g_active.c†L2415-L2420】【F:src/code/game/g_freeze.c†L185-L196】【F:src/code/game/g_combat.c†L1737-L1737】 |
| `g_freezeEnvironmentalRespawnDelay` | `5000` | `CVAR_GAMERULE` | Schedules auto-release for frozen environmental deaths through `freezeEnvironmentalRespawnTime`.【F:src/code/game/g_active.c†L2415-L2420】【F:src/code/game/g_freeze.c†L146-L152】【F:src/code/game/g_client.c†L220-L226】 |
| `g_freezeAutoThawTime` | `120000` | `CVAR_GAMERULE` | Schedules the general auto-thaw deadline for frozen players, separate from environmental respawn release.【F:src/code/game/g_active.c†L2415-L2420】【F:src/code/game/g_freeze.c†L146-L152】【F:src/code/game/g_client.c†L220-L226】 |

## Player Appearance, Lag Rewind, and Instagib Retail Rows

This tranche rechecks player-appearance transport, hidden lag-compensation rewind, and instagib gameplay rows against the retail qagame cvar slab. Quake Live keeps most player-appearance rows on a recovered `0x00010000 | CVAR_GAMERULE` flag surface instead of the older archived admin surface, leaves `g_playerCylinders` as a direct gamerule row, latches both lag rewind sizing controls, and advertises `g_instaGib` with `CVAR_SERVERINFO | 0x00040000 | CVAR_GAMERULE`.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L586-L594】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L1326-L1334】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L1518-L1531】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L1718-L1755】

| CVar | Default | Retail flags | Notes |
| --- | --- | --- | --- |
| `g_allowCustomHeadmodels` | `0` | `0x00010000 \| CVAR_GAMERULE` | Published through `CS_PLAYER_APPEARANCE` so cgame knows whether independent client head models are accepted.【F:src/code/game/g_main.c†L1007-L1013】【F:src/code/game/g_main.c†L2036-L2046】 |
| `g_playerCylinders` | `1` | `CVAR_GAMERULE` | Published as the dedicated `CS_PLAYER_CYLINDERS` numeric configstring and cached in `level.adminConfig`.【F:src/code/game/g_main.c†L1987-L1994】【F:src/code/game/g_main.c†L2246-L2252】 |
| `g_playerheadmodelOverride` | *(empty)* | `0x00010000 \| CVAR_GAMERULE` | Forces connected clients' head model userinfo when configured and is also carried in the player-appearance configstring.【F:src/code/game/g_client.c†L1525-L1570】【F:src/code/game/g_main.c†L2036-L2046】 |
| `g_playerheadScale` | `1.0` | `0x00010000 \| CVAR_GAMERULE` | Carries the primary forced-head scale value for cgame drawing and admin config snapshots.【F:src/code/game/g_main.c†L2036-L2046】【F:src/code/game/g_main.c†L2246-L2252】 |
| `g_playerheadScaleOffset` | `1.0` | `0x00010000 \| CVAR_GAMERULE` | Carries the secondary forced-head scale value layered on top of `g_playerheadScale`.【F:src/code/game/g_main.c†L2036-L2046】【F:src/code/game/g_main.c†L2246-L2252】 |
| `g_playermodelOverride` | *(empty)* | `0x00010000 \| CVAR_GAMERULE` | Forces model and team-model userinfo when configured and shares the same configstring transport as the head override.【F:src/code/game/g_client.c†L1525-L1570】【F:src/code/game/g_main.c†L2036-L2046】 |
| `g_playerModelScale` | `1.1` | `0x00010000 \| CVAR_GAMERULE` | Publishes the retail body-scale multiplier; the `1.1` default is stored immediately before the retail string row.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L45666-L45683】【F:src/code/game/g_main.c†L2036-L2046】 |
| `g_lagHaxHistory` | `4` | `CVAR_LATCH` | Sizes the per-client retail rewind ring allocated at level init, so changes latch until the next restart like retail.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L45797-L45803】【F:src/code/game/g_active.c†L53-L84】 |
| `g_lagHaxMs` | `80` | `CVAR_LATCH` | Sets the maximum rewind window in milliseconds for the hitscan time-shift path.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L46180-L46180】【F:src/code/game/g_active.c†L233-L250】 |
| `g_instaGib` | `0` | `CVAR_SERVERINFO \| 0x00040000 \| CVAR_GAMERULE` | Feeds pmove's no-player-clip cache, resets with factory-managed pmove cvars, and is exported to custom-settings and rank payloads.【F:src/code/game/g_pmove.c†L319-L636】【F:src/code/game/g_main.c†L2149-L2166】【F:src/code/game/g_main.c†L6007-L6008】 |

## Domination and Auto-Shuffle Retail Rows

This tranche rechecks Domination scoring/capture controls and the automatic shuffle controls against the retail qagame cvar slab. Domination's six server-side gameplay knobs are `CVAR_GAMERULE` rows, while the four `g_shuffle_*` rows are plain zero-flag runtime controls. The source now also treats `g_shuffle_timedelay` as the retail millisecond value before handing it to the countdown helper.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L940-L974】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L2076-L2097】

| CVar | Default | Retail flags | Notes |
| --- | --- | --- | --- |
| `g_domCapTime` | `5` | `CVAR_GAMERULE` | Seconds for a single attacker to capture a point; also published as the Domination capture-time configstring.【F:src/code/game/g_team.c†L1932-L1942】【F:src/code/game/g_main.c†L2092-L2105】 |
| `g_domTeammateCapScale` | `0.5` | `CVAR_GAMERULE` | Adds capture speed for each extra teammate assisting at the same point.【F:src/code/game/g_team.c†L1974-L1982】 |
| `g_domDistressThreshold` | `75` | `CVAR_GAMERULE` | Progress percentage at which defenders receive the point-protection warning.【F:src/code/game/g_team.c†L2359-L2362】 |
| `g_domEnableContention` | `1` | `CVAR_GAMERULE` | Lets unequal contested occupants continue progress for the larger side instead of fully blocking capture.【F:src/code/game/g_team.c†L2270-L2279】 |
| `g_domNeutralFlag` | `0` | `CVAR_GAMERULE` | Requires owned points to be neutralized before an enemy can complete capture when enabled.【F:src/code/game/g_team.c†L2317-L2326】 |
| `g_domScoreRate` | `5` | `CVAR_GAMERULE` | Seconds between team score ticks from owned Domination points.【F:src/code/game/g_team.c†L1946-L1956】【F:src/code/game/g_team.c†L2380-L2395】 |
| `g_shuffle_timedelay` | `5000` | `0` | Millisecond delay passed directly to `G_AutoShuffleCountdown_Arm`; UI/log messages round up to seconds for readability.【F:src/code/game/g_team.c†L1503-L1520】 |
| `g_shuffle_minplayers` | `3` | `0` | Fallback total-player threshold when `g_shuffle_automatic_minplayers` is not positive.【F:src/code/game/g_team.c†L1291-L1301】 |
| `g_shuffle_automatic` | `0` | `0` | Master switch for warmup-only automatic shuffles.【F:src/code/game/g_team.c†L1311-L1330】 |
| `g_shuffle_automatic_minplayers` | `6` | `0` | Preferred total-player threshold for automatic shuffles.【F:src/code/game/g_team.c†L1291-L1301】 |

## Flag Physics and Forced Override Retail Rows

This tranche rechecks retail flag-physics, flag-tackle, neutral-flag ping, friendly-fire dampening, and forced override controls against the qagame cvar slab. Quake Live keeps most flag physics toggles as `CVAR_GAMERULE` rows, but stores the two throw-tuning values as plain runtime controls and the dropped-flag bonus as a temporary row. The source now keeps `g_throwFlagForwardMult` as a float so the retail `2.5` multiplier is not truncated, registers the neutral ping cvar under the retail `g_neutralFlagPingRate` name, and wires `g_friendlyFireDampen` into same-team damage when friendly fire remains enabled.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L995-L1125】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L1249-L1679】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L2475-L2552】

| CVar | Default | Retail flags | Notes |
| --- | --- | --- | --- |
| `g_flagBounce` | `0.25` | `CVAR_GAMERULE` | Bounce scale applied to dropped flags when retail flag physics are enabled.【F:src/code/game/g_main.c†L1423-L1432】【F:src/code/game/g_team.c†L3057-L3077】 |
| `g_flagPhysics` | `0` | `CVAR_GAMERULE` | Gates the retail flag-physics path while leaving classic flag tosses untouched when disabled.【F:src/code/game/g_items.c†L344-L355】【F:src/code/game/g_team.c†L3032-L3047】 |
| `g_throwFlagVelocity` | `0` | `0` | Forward launch component used only when `g_flagPhysics` is active.【F:src/code/game/g_items.c†L344-L355】【F:src/code/game/g_team.c†L3032-L3047】 |
| `g_throwFlagForwardMult` | `2.5` | `0` | Multiplies the carrier's velocity into a tossed flag under the retail flag-physics path.【F:src/code/game/g_main.c†L1434-L1438】【F:src/code/game/g_team.c†L3032-L3047】 |
| `g_tackleFlag` | `0` | `CVAR_GAMERULE` | Enables the flag-carrier tackle/drop path and associated bonus messaging when non-zero.【F:src/code/game/g_team.c†L3131-L3149】【F:src/code/game/g_team.c†L3769-L3788】 |
| `g_droppedFlagBonus` | `1` | `CVAR_TEMP` | Bonus score used for tackle drops and enemy-dropped flag recovery.【F:src/code/game/g_team.c†L3143-L3149】【F:src/code/game/g_team.c†L3917-L3921】 |
| `g_neutralFlagPingRate` | `2400` | `CVAR_GAMERULE` | Milliseconds between neutral-flag ground pings, registered under the retail name while cached internally for drop thinks.【F:src/code/game/g_main.c†L1037-L1037】【F:src/code/game/g_team.c†L3836-L3850】 |
| `g_friendlyFireDampen` | `1.00` | `CVAR_GAMERULE` | Scales same-team damage when `g_friendlyFire` allows the hit; non-positive values suppress the damage entirely.【F:src/code/game/g_main.c†L971-L972】【F:src/code/game/g_combat.c†L1852-L1874】 |
| `g_forceDmgThroughSurface` | `0` | `CVAR_GAMERULE` | Publishes the forced damage-through-surface hint in the forced-cosmetics payload.【F:src/code/game/g_main.c†L175-L205】 |
| `g_forceAtmosphericEffects` | *(empty)* | `CVAR_GAMERULE` | Overrides atmosphere selection before falling back to worldspawn or `g_forcedAtmosphere`.【F:src/code/game/g_main.c†L150-L205】 |

## Classic Server Gameplay Controls

This tranche rechecks the classic movement, inactivity, team-admission, and debug CVars against the qagame HLIL registration slab. `g_speed`, `g_gravity`, `g_weaponRespawn`, and `g_teamForceBalance` now carry the same serverinfo/gamerule/archive flag surfaces as retail, while the inactivity warning path consumes the Quake Live `g_inactivityWarning` value instead of the old hardcoded ten-second Quake III message.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L1007-L1315】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L2214-L2678】

| CVar | Default | Retail flags | Notes |
| --- | --- | --- | --- |
| `g_speed` | `320` | `CVAR_GAMERULE` | Feeds active client movement speed and the custom-settings digest when movement deviates from stock.【F:src/code/game/g_active.c†L1368-L1372】【F:src/code/game/g_main.c†L2127-L2136】 |
| `g_gravity` | `800` | `CVAR_SERVERINFO \| CVAR_GAMERULE` | Published to serverinfo/server-settings and consumed by player, trigger, mover, and worldspawn gravity paths.【F:src/code/game/g_active.c†L1368-L1370】【F:src/code/game/g_spawn.c†L1133-L1137】 |
| `g_weaponRespawn` | `5` | `CVAR_SERVERINFO \| CVAR_GAMERULE` | Controls non-team weapon item respawn timing and remains bridged to the legacy lowercase alias.【F:src/code/game/g_items.c†L1534-L1541】【F:src/code/game/g_main.c†L105-L113】 |
| `g_inactivity` | `0` | `0` | Enables inactivity timeouts; changing it clears connected clients' warning latches like the retained retail cvar callback.【F:src/code/game/g_active.c†L724-L760】【F:src/code/game/g_main.c†L1848-L1878】 |
| `g_inactivityWarning` | `10` | `0` | Sets the warning lead time and centerprint seconds/plural text before the inactivity timeout fires.【F:src/code/game/g_active.c†L747-L760】 |
| `g_dropInactive` | `1` | `0` | Drops inactive clients by default; setting it to `0` moves them to spectator instead, matching the retail timeout branch.【F:src/code/game/g_active.c†L742-L750】 |
| `g_debugMove` | `0` | `0` | Feeds `pm.debugLevel` during active pmove setup.【F:src/code/game/g_active.c†L1459-L1460】 |
| `g_debugDamage` | `0` | `0` | Gates retail damage/armor debug prints in `G_Damage`.【F:src/code/game/g_combat.c†L1627-L1937】 |
| `g_teamAutoJoin` | `0` | `CVAR_ARCHIVE` | Seeds automatic team placement for sessions and first client begin paths.【F:src/code/game/g_session.c†L164-L182】【F:src/code/game/g_client.c†L2042-L2046】 |
| `g_teamForceBalance` | `1` | `CVAR_ARCHIVE \| CVAR_SERVERINFO` | Rejects lopsided team joins and now advertises the retail serverinfo bit.【F:src/code/game/g_cmds.c†L3756-L3776】 |

## Team Arena Environment Controls

This tranche rechecks older Team Arena and arena-presentation CVars against the retail qagame registration slab. Quake Live keeps the podium, Obelisk, Cube, and map-dust rows as gamerule or local qagame controls rather than the legacy serverinfo/archive mix, while `g_motd` remains a plain row published through `CS_MOTD`.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L623-L713】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L1042-L1769】

| CVar | Default | Retail flags | Notes |
| --- | --- | --- | --- |
| `g_allTalk` | `0` | `0` | Gates cross-team and spectator chat restrictions without advertising the toggle through serverinfo.【F:src/code/game/g_team.c†L2819-L2819】【F:src/code/game/g_cmds.c†L4206-L4215】 |
| `g_motd` | *(empty)* | `0` | Published at worldspawn via `CS_MOTD` and centerprinted to joining clients when non-empty.【F:src/code/game/g_spawn.c†L1133-L1133】【F:src/code/game/g_client.c†L2037-L2039】 |
| `g_podiumDist` | `80` | `CVAR_GAMERULE` | Controls winner podium distance from the intermission camera in both podium placement paths.【F:src/code/game/g_arenas.c†L229-L230】【F:src/code/game/g_arenas.c†L295-L296】 |
| `g_podiumDrop` | `70` | `CVAR_GAMERULE` | Controls the vertical drop applied when placing podium entities.【F:src/code/game/g_arenas.c†L229-L230】【F:src/code/game/g_arenas.c†L295-L296】 |
| `g_obeliskHealth` | `2500` | `CVAR_GAMERULE` | Seeds Obelisk health, clamps regeneration, and drives the client modelindex health meter.【F:src/code/game/g_team.c†L4441-L4452】【F:src/code/game/g_team.c†L4542-L4574】 |
| `g_obeliskRegenAmount` | `15` | `CVAR_GAMERULE` | Amount restored on each Obelisk regeneration tick.【F:src/code/game/g_team.c†L4447-L4449】 |
| `g_obeliskRegenPeriod` | `1` | `CVAR_GAMERULE` | Seconds between Obelisk regeneration thinks after spawn and each regen pulse.【F:src/code/game/g_team.c†L4441-L4462】【F:src/code/game/g_team.c†L4570-L4574】 |
| `g_obeliskRespawnDelay` | `10` | `CVAR_GAMERULE` | Seconds before a destroyed Obelisk respawns; cgame keeps a matching zero-flag mirror for the respawn effect countdown.【F:src/code/game/g_team.c†L4479-L4479】【F:src/code/cgame/cg_ents.c†L1828-L1828】 |
| `g_cubeTimeout` | `30` | `CVAR_GAMERULE` | Seconds before a dropped Harvester cube expires.【F:src/code/game/g_combat.c†L634-L634】 |
| `g_enableDust` | `0` | `0` | Worldspawn's `enableDust` key writes the qagame cvar, while cgame retains the retail serverinfo-facing mirror consumed by player dust effects.【F:src/code/game/g_spawn.c†L1136-L1139】【F:src/code/cgame/cg_players.c†L2379-L2379】 |

## Server Access, Factory, and Match Flow Controls

This tranche rechecks the server access, ban/filter, factory selection, overtime, mercy, automatic action, and malformed-userinfo CVars against the retail qagame registration slab. The rows keep Quake Live's split between externally visible serverinfo/ROM values (`g_needpass`, `g_factory`, `g_factoryTitle`, `g_overtime`), admin-local archive values (`g_banIPs`, `g_filterBan`), and plain runtime-only toggles (`g_autoAction`, `g_kickBadUserinfo`).【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L652-L672】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L1056-L1072】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L1610-L1718】

| CVar | Default | Retail flags | Notes |
| --- | --- | --- | --- |
| `g_password` | *(empty)* | `CVAR_USERINFO` | Drives `CheckCvars`, which mirrors password state into the ROM/serverinfo `g_needpass` value for browser visibility.【F:src/code/game/g_main.c†L8221-L8229】 |
| `g_needpass` | `0` | `CVAR_SERVERINFO \| CVAR_ROM` | Read-only published password indicator controlled by `g_password` changes.【F:src/code/game/g_main.c†L8221-L8229】 |
| `g_banIPs` | *(empty)* | `CVAR_ARCHIVE` | Stores IP masks built by the add/remove/list IP server commands.【F:src/code/game/g_svcmds.c†L55-L170】 |
| `g_filterBan` | `1` | `CVAR_ARCHIVE` | Selects whether matching masks deny or allow packets in `G_FilterPacket`.【F:src/code/game/g_svcmds.c†L184-L204】 |
| `g_factory` | *(empty)* | `CVAR_SERVERINFO \| CVAR_ROM` | Names the active factory selection; game code updates it internally while external writes are blocked like retail.【F:src/code/game/g_factory.c†L1151-L1173】 |
| `g_factoryTitle` | *(empty)* | `CVAR_SERVERINFO \| CVAR_ROM` | Publishes the active factory title and is cleared when factory application falls back to no selection.【F:src/code/game/g_factory.c†L1100-L1136】 |
| `g_overtime` | `120` | `CVAR_SERVERINFO \| CVAR_GAMERULE` | Feeds match config and the tied-score exit path that starts or extends overtime instead of ending immediately.【F:src/game/g_match_config.c†L239-L247】【F:src/code/game/g_main.c†L7019-L7034】 |
| `g_mercytime` | `0` | `CVAR_NORESTART \| CVAR_GAMERULE` | Delays mercy-rule evaluation by whole minutes after match start; the retail default evaluates immediately once the score spread exceeds `mercylimit`.【F:src/code/game/g_main.c†L922-L922】【F:src/code/game/g_main.c†L7019-L7019】 |
| `g_autoAction` | `0` | `0` | Parses event-command pairs only when explicitly configured; the retail `0` default now behaves as the no-op state.【F:src/code/game/g_utils.c†L873-L947】 |
| `g_kickBadUserinfo` | `1` | `0` | Drops malformed userinfo by default, with a warning-and-repair fallback when disabled.【F:src/code/game/g_client.c†L1431-L1462】 |

## Mercy Rule Controls

Team games can optionally end early when one side builds an insurmountable lead. The HLIL uses `g_mercytime` to delay any mercy evaluation until a minimum number of minutes has elapsed, then checks whether the absolute score spread exceeds `mercylimit` (ignoring warmup periods, pauses, and Attack & Defend's bespoke flow). When triggered, the server prints which team hit the limit and logs a `Mercylimit hit.` exit so demos match Quake Live's console text.【F:src/code/game/g_main.c†L2088-L2144】【F:src/code/game/g_main.c†L2146-L2184】

| CVar | Default | Notes |
| --- | --- | --- |
| `mercylimit` | `0` | Absolute score difference that ends team-based matches once the grace window expires; `0` disables the mercy rule entirely.【F:src/code/game/g_main.c†L352-L356】【F:src/code/game/g_main.c†L2088-L2144】 |
| `g_mercytime` | `0` | Minutes to wait after match start before evaluating `mercylimit`; the retail default has no extra grace window beyond normal warmup/overtime exclusions.【F:src/code/game/g_main.c†L922-L922】【F:src/code/game/g_main.c†L7019-L7019】 |

## Attack & Defend Scorelimit

`g_scorelimit` mirrors Quake Live's Attack & Defend score win condition so leagues can end maps early once a team banks enough objective points. The VM registers it alongside the classic frag/capture limits, advertises help text for `cvarlist`, and polls the value every frame through the standard `G_UpdateCvars` pass.【F:src/code/game/g_main.c†L167-L182】【F:src/code/game/g_main.c†L338-L399】 `CheckExitRules` watches the Team Arena scoreboard in `GT_ATTACK_DEFEND` and triggers the usual `LogExit("Scorelimit hit.")` path with the `Red/Blue hit the scorelimit.` server prints when the configured threshold is reached.【F:src/code/game/g_main.c†L2058-L2181】 Setting the limit to `0` disables the check.

| CVar | Default | Notes |
| --- | --- | --- |
| `g_scorelimit` | `0` | Attack & Defend team score threshold; once either side reaches the value the round ends immediately with the scorelimit broadcast and exit log.【F:src/code/game/g_main.c†L167-L182】【F:src/code/game/g_main.c†L2058-L2181】 |

## Vote Administration Controls

Quake Live exposes additional vote governance CVars alongside the base `g_allowVote` toggle. These parameters gate when votes may be started, throttle repeat attempts, and cap how many proposals a player may issue per match. The HLIL registration table lists `g_allowVoteMidGame`, `g_voteDelay`, and `g_voteLimit` beside the stock vote knobs, each defaulting to `0` so dedicated servers begin with the legacy behaviour disabled.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L600-L744】 The vote fixtures exercise these toggles in isolation to confirm their impact on a running match.【F:src/game/tests/vote_control_fixtures.c†L165-L223】

| CVar | Default | Notes |
| --- | --- | --- |
| `g_allowVoteMidGame` | `0` | When set, allows `callvote` to be issued while a match is live instead of limiting votes to warmup/intermission states. The fixtures verify mid-game calls are rejected until this toggle flips on.【F:src/game/tests/vote_control_fixtures.c†L165-L189】 |
| `g_voteDelay` | `0` | Minimum number of seconds between vote proposals and the elapsed time since match start before the first callvote. Raising the value forces additional waiting; lowering it mid-match immediately relaxes the throttle.【F:src/game/tests/vote_control_fixtures.c†L195-L216】 |
| `g_voteLimit` | `0` | Maximum number of votes a single player may initiate per map (0 keeps the legacy hardcoded limit). Increasing the limit mid-match allows further votes after the counter is exhausted.【F:src/game/tests/vote_control_fixtures.c†L205-L216】 |

## Self-Kill and Forfeit Controls

Quake Live retains the Quake III self-kill command but wraps it in a server-configurable cooldown so admins can suppress griefing macros. The binary's registration table seeds `g_allowKill` with a `1000` millisecond window and `g_allowForfeit` with the shared `1` default; both rows carry the recovered `CVAR_GAMERULE` flag so initialization-time rule overrides reject console `set` writes until the game rules are ready.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L592-L604】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L40045-L40046】 The fixtures assert that both toggles gate their respective commands as expected.【F:src/game/tests/vote_control_fixtures.c†L218-L252】

| CVar | Default | Notes |
| --- | --- | --- |
| `g_allowKill` | `1000` | Minimum milliseconds between successful `kill` commands. Also enforces a spawn grace period; setting the value to `0` restores instant kills.【F:src/game/tests/vote_control_fixtures.c†L218-L240】 |
| `g_allowForfeit` | `1` | Enables the `forfeit` console command when non-zero so duel/CA leagues can permit early surrenders.【F:src/game/tests/vote_control_fixtures.c†L242-L253】 |

## Friendly Fire Complaint Controls

Team-damage complaints mirror the retail DLL: attackers accrue infractions once they exceed the configured damage threshold and are kicked when the limit is reached. The registration block seeds `g_complaintDamageThreshold` with `400` and `g_complaintLimit` with `5`, matching the retail string pointers and archived flags in the HLIL table.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L697-L707】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L46219-L46283】 The fixtures drive repeated complaints to ensure both the threshold and limit are honoured.【F:src/game/tests/vote_control_fixtures.c†L255-L298】

| CVar | Default | Notes |
| --- | --- | --- |
| `g_complaintDamageThreshold` | `400` | Minimum friendly-fire damage required before the victim can register a complaint.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L697-L700】 |
| `g_complaintLimit` | `5` | Number of recorded complaints that triggers an automatic kick for the attacker.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L704-L707】 |

## Cosmetic, Training, and HUD Overrides

Quake Live layers a set of server CVars that gate coaching affordances and force client-facing HUD hints. The registration table seeds the toggles below and routes their change handlers through the same broadcast shim that prints a `Server: %s changed to %s` message and pushes configstring `0x2B3` when administrators flip the override.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L1100-L1138】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L7980-L8033】 Votes that attempt to toggle the training helpers inherit Quake Live's console messaging so players are told when the server forbids the action or restricts it to warmup.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L14137-L14171】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L44217-L44224】

| CVar | Default | Notes |
| --- | --- | --- |
| `g_itemTimers` | `1` | Retail registers the timer gate as `CVAR_SERVERINFO | CVAR_GAMERULE`. Votes accept `ON`/`OFF`, call directly into the `trap_Cvar_Set` handler shown in the HLIL, and broadcast the updated `itemcfg` payload. Warmup-only or disabled servers print the retail guidance strings before rejecting the vote so players see why the change failed.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L1338-L1351】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L14137-L14171】【F:src/code/game/g_vote.c†L400-L413】 |
| `g_itemHeight` | `35` | Retail stores the default height string as `35` and registers the row with `CVAR_SERVERINFO | CVAR_GAMERULE`. The server clamps invalid values before sending the `itemcfg` command to connected clients and late joiners.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L1339-L1344】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L45896-L45900】【F:src/code/game/g_main.c†L1444-L1465】【F:src/code/game/g_cmds.c†L2959-L2980】 |
| `g_training` | `0` | The single-player onboarding path drives this CVar to `1`, which in turn blocks match management commands—`addbot` emits *Addbot not allowed during training* and the vote system refuses new proposals until training finishes.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L2557-L2577】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt†L25148-L25178】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L43338-L43338】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L43925-L43925】 |
| `g_specItemTimers` | `1` | Retail exposes this qagame cvar as a plain registration-only surface with no extra flags in the recovered table. The source keeps that row present for config/factory parity while the existing item timer transport continues to run through `g_itemTimers` and `g_itemHeight`.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L2207-L2212】 |
| `g_forceSmallScoreboardMessage` | `0` | Retail registers this row with default `0` and no flags. Changes feed the forced-cosmetics configstring payload so clients receive the compact scoreboard hint alongside other forced HUD keys.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L1134-L1138】【F:src/code/game/g_main.c†L175-L205】 |
| `g_forceSendConfigstring` | `0` | Retail registers this row with default `0` and no flags. It shares the same forced-cosmetics broadcast shim, letting the server deliberately resend HUD/config metadata to clients even if nothing changed locally.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L1128-L1132】【F:src/code/game/g_main.c†L175-L205】 |
| `g_forceAtmosphericEffects` | *(empty)* | Retail stores the override string in `data_1007c414` and flags the cvar as `CVAR_GAMERULE`. The server publishes a non-empty value through the same forced-cosmetics payload, falling back to worldspawn and `g_forcedAtmosphere` tokens when the override is empty.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L1120-L1125】【F:src/code/game/g_main.c†L150-L205】 |
| `g_forceDmgThroughSurface` | `0` | Retail registers this row as `CVAR_GAMERULE` with default `0`. The VM advertises the damage-through-surface override through the forced-cosmetics change hook so clients receive the flag alongside the other forced HUD hints.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L1113-L1118】【F:src/code/game/g_main.c†L175-L205】 |

### Usage notes

* Training servers set `g_training` to `1` when the scripted tutorial runs, so harnesses that replay the onboarding sequence should expect `addbot`, voting, and similar admin commands to be rejected until the tutorial releases the block.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt†L25148-L25178】
* `g_itemTimers` votes must pass the warmup and server policy checks baked into the callvote handler; invalid options trigger the same Quake Live console guidance captured in the HLIL dump.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L14137-L14171】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L44224-L44224】
* When `g_factory` is unset or invalid, the server now resolves the retail factory id that matches the current `g_gametype`, avoiding stale archived selectors such as `standard` from bypassing the intended item-spawn policy.【F:src/code/game/g_factory.c】【F:src/code/game/g_main.c】
* The enforced timer broadcast registers `g_itemHeight` with Quake Live's `35` default, then clamps invalid runtime values to the local fallback before delivering the sanitized payload to every client (and to new joiners) using the `itemcfg` command.【F:src/code/game/g_main.c†L989-L998】【F:src/code/game/g_cmds.c†L2959-L2980】

## Starting Health and Armor Controls

Quake Live publishes spawn stat knobs for the base health, bonus health stack, armor, and weapon mask granted to players when they respawn. The retail DLL registers `g_startingHealth` as `CVAR_SERVERINFO | CVAR_GAMERULE`, while `g_startingHealthBonus`, `g_startingArmor`, and `g_startingWeapons` are `CVAR_GAMERULE` rows; the VM mirrors those flags so factory scripts and votes can adjust the opening survivability without source edits.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L2401-L2428】【F:src/code/game/g_main.c†L1012-L1015】【F:src/game/g_config.c†L238-L239】

| CVar | Default | Notes |
| --- | --- | --- |
| `g_startingHealth` | `100` | Base health applied before handicap clamping when a player spawns; if the cvar is invalid, the factory config cache falls back to the retail `100` default.【F:src/game/g_config.c†L593-L595】【F:src/code/game/g_client.c†L2621-L2628】 |
| `g_startingHealthBonus` | `25` | Additional health granted on top of the base value after handicap, read through the same factory config cache as the other spawn stat knobs.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L2416-L2421】【F:src/game/g_config.c†L593-L595】 |
| `g_startingArmor` | `0` | Armor seeded on spawn when positive, matching Quake Live factory defaults and falling back to the cached factory value when the direct cvar is unset.【F:src/game/g_config.c†L593-L595】【F:src/code/game/g_client.c†L2357-L2362】 |
| `g_startingWeapons` | `3` | Retail default mask grants Gauntlet and Machinegun. The factory cache parses symbolic or numeric masks, rebuilds the stat mask, and feeds warmup weapon grants and spawn ammo seeding.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L2423-L2428】【F:src/game/g_config.c†L576-L580】【F:src/code/game/g_client.c†L2204-L2355】 |

### Usage notes

* `G_LoadFactoryCvarConfig` caches the values alongside the other factory knobs, clamping invalid entries to safe fallbacks and logging any corrections for administrators.【F:src/game/g_config.c†L429-L563】
* `ClientSpawn` applies the cached values, respecting player handicap limits before adding the configured bonus health and optional armor.【F:src/code/game/g_client.c†L1433-L1512】

## Sudden Death Respawn Controls

Retail exposes the sudden-death respawn controller as six `CVAR_GAMERULE` rows. The reconstructed game keeps the same defaults and feeds them through both the factory config cache and the match-state cache so item respawns, death respawn delays, centerprint announcements, and HUD configstrings all observe the same values.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L2430-L2469】【F:src/game/g_match_config.c†L245-L254】

| CVar | Default | Notes |
| --- | --- | --- |
| `g_suddenDeathRespawn` | `0` | Enables respawns during sudden death. The value gates death-path respawn delay, item respawn suppression, and the match-state `suddenRespawns` key.【F:src/code/game/g_combat.c†L45-L48】【F:src/code/game/g_items.c†L1476-L1478】【F:src/code/game/g_match_state.c†L62-L62】 |
| `g_suddenDeathRespawnStart` | `3` | Initial respawn delay in seconds once overtime sudden death begins.【F:src/game/g_match_config.c†L245-L254】【F:src/code/game/g_main.c†L7558-L7582】 |
| `g_suddenDeathRespawnTick` | `60` | Number of elapsed sudden-death seconds per delay increase step; invalid non-positive values are clamped by the match config reader.【F:src/game/g_match_config.c†L245-L254】【F:src/code/game/g_main.c†L7558-L7582】 |
| `g_suddenDeathRespawnMax` | `10` | Maximum respawn delay in seconds, clamped upward to at least the configured start delay.【F:src/game/g_match_config.c†L245-L254】【F:src/code/game/g_main.c†L7558-L7582】 |
| `g_suddenDeathRespawnIncrement` | `1` | Seconds added to the respawn delay at each tick while overtime continues.【F:src/game/g_match_config.c†L245-L254】【F:src/code/game/g_main.c†L7558-L7582】 |
| `g_suddenDeathRespawnPrint` | `1` | Controls the retail centerprint/log announcements when sudden-death respawns become disabled or change delay.【F:src/game/g_match_config.c†L245-L254】【F:src/code/game/g_main.c†L8130-L8170】 |

## Starting Ammo Controls

The server now registers the full Quake Live `g_startingAmmo_*` family so per-weapon spawn loadouts can be tuned without touching code. Each cvar exposes the amount of ammunition players receive when a weapon is granted through `g_startingWeapons`, factories, or scripted loadouts, and publishes a `helptext_*` mirror for in-console discovery. The defaults are defined once in `g_main.c`, ensuring the archived fallback used by `G_InitStartingAmmoConfig` matches the string advertised to administrators and mirrors the retail Quake Live DLL when no overrides are present.

| CVar | Default | Notes |
| --- | --- | --- |
| `g_startingAmmo_bfg` | `10` | BFG cells granted on spawn when the weapon is enabled. |
| `g_startingAmmo_cg` | `100` | Chaingun bullet count applied at spawn. |
| `g_startingAmmo_g` | `-1` | Gauntlet swings; `-1` keeps the melee weapon infinite. |
| `g_startingAmmo_gh` | `-1` | Grappling hook ammo; `-1` preserves Quake Live's unlimited grapple. |
| `g_startingAmmo_gl` | `10` | Grenade launcher rounds granted on spawn. |
| `g_startingAmmo_hmg` | `50` | Heavy machinegun bullet stack for supported mods. |
| `g_startingAmmo_lg` | `100` | Lightning gun cell pool on spawn. |
| `g_startingAmmo_mg` | `100` | Machinegun bullets; aligns with the stock FFA start. |
| `g_startingAmmo_ng` | `10` | Nailgun spikes for spawn loadouts. |
| `g_startingAmmo_pg` | `50` | Plasma gun cell count on spawn. |
| `g_startingAmmo_pl` | `5` | Proximity launcher mines granted when enabled. |
| `g_startingAmmo_rg` | `5` | Railgun slugs granted on spawn. |
| `g_startingAmmo_rl` | `5` | Rocket launcher rockets applied on spawn. |
| `g_startingAmmo_sg` | `10` | Shotgun shell count on spawn. |

### Usage notes

* `G_InitStartingAmmoConfig` reads every `g_startingAmmo_*` value into `g_startingAmmoConfig`, so factory scripts and spawn handlers resolve the configured counts without requiring per-weapon code edits.【F:src/code/game/g_main.c†L564-L596】
* Values persist via archived CVars, allowing event scripts and competitive configs to pre-bake spawn stacks for tournaments while still matching Quake Live's default numbers when unset.【F:src/code/game/g_main.c†L347-L380】【F:src/code/game/g_main.c†L564-L596】

## Weapon Reload Controls

Quake Live exposes a `weapon_reload_*` family that lets operators retime each gun's refire delay in milliseconds. The VM loads Quake Live's defaults into `g_weaponReloadConfig` on startup, ensuring the runtime table always matches the shipping DLL even if the archive is missing or malformed.【F:src/code/game/g_main.c†L52-L66】【F:src/code/game/g_main.c†L494-L508】

| CVar | Default (ms) | Notes |
| --- | --- | --- |
| `weapon_reload_gauntlet` | `400` | Melee swing delay; higher values slow successive punches.【F:src/code/game/g_main.c†L52-L66】【F:src/code/game/g_main.c†L494-L498】 |
| `weapon_reload_mg` | `100` | Machinegun refire duration, impacting both spawn weapons and pickups.【F:src/code/game/g_main.c†L52-L66】【F:src/code/game/g_main.c†L494-L501】 |
| `weapon_reload_sg` | `1000` | Shotgun pump cycle between blasts.【F:src/code/game/g_main.c†L52-L66】【F:src/code/game/g_main.c†L494-L501】 |
| `weapon_reload_gl` | `800` | Grenade launcher refire gate for direct grenades.【F:src/code/game/g_main.c†L52-L66】【F:src/code/game/g_main.c†L494-L501】 |
| `weapon_reload_rl` | `800` | Rocket launcher refire delay; applies to splash and direct hits.【F:src/code/game/g_main.c†L52-L66】【F:src/code/game/g_main.c†L494-L501】 |
| `weapon_reload_lg` | `50` | Lightning gun tick spacing for continuous fire.【F:src/code/game/g_main.c†L52-L66】【F:src/code/game/g_main.c†L494-L501】 |
| `weapon_reload_rg` | `1500` | Railgun cooldown between slugs.【F:src/code/game/g_main.c†L52-L66】【F:src/code/game/g_main.c†L494-L501】 |
| `weapon_reload_pg` | `100` | Plasma gun cooldown driving bolt cadence.【F:src/code/game/g_main.c†L52-L66】【F:src/code/game/g_main.c†L494-L502】 |
| `weapon_reload_bfg` | `300` | BFG refire delay before another tracer can be launched.【F:src/code/game/g_main.c†L52-L66】【F:src/code/game/g_main.c†L502-L504】 |
| `weapon_reload_gh` | `100` | Grappling hook firing delay; negative knockback pairs well with this cadence.【F:src/code/game/g_main.c†L52-L66】【F:src/code/game/g_main.c†L502-L505】 |
| `weapon_reload_hook` | `100` | Hook pull rate for movement mods that separate pull timing.【F:src/code/game/g_main.c†L52-L66】【F:src/code/game/g_main.c†L502-L505】 |
| `weapon_reload_ng` | `1000` | Nailgun bolt spacing used in missionpack modes.【F:src/code/game/g_main.c†L52-L66】【F:src/code/game/g_main.c†L505-L507】 |
| `weapon_reload_prox` | `800` | Proximity launcher mine placement delay.【F:src/code/game/g_main.c†L52-L66】【F:src/code/game/g_main.c†L505-L507】 |
| `weapon_reload_cg` | `50` | Chaingun refire rate for Team Arena loadouts.【F:src/code/game/g_main.c†L52-L66】【F:src/code/game/g_main.c†L505-L507】 |
| `weapon_reload_hmg` | `75` | Heavy machinegun spin-up cadence as seen in PQL/CA variants.【F:src/code/game/g_main.c†L52-L66】【F:src/code/game/g_main.c†L505-L508】 |

### Usage notes

* `G_InitWeaponReloadConfig` refreshes the reload table whenever CVars change, so weapon think code can re-query during warmup or between rounds without a restart.【F:src/code/game/g_main.c†L494-L508】
* `G_PmoveStoreWeaponReloads` copies the parsed durations into `g_pmoveSettings.weaponReloadTimes`, keeping server prediction and client pmove in sync after reload CVars change.【F:src/game/g_config.c†L303-L315】【F:src/code/game/g_pmove.c†L170-L259】
* Tuning refire timings is most visible in spawn loadouts from `g_startingWeapons` and in weapon pickup dominance during duel/CA rotations, making it a complementary knob to the spawn ammo controls documented above.【F:docs/gameplay/cvars.md†L5-L34】

## Ammo Pack Pickup Controls

The Quake Live VM reads `g_ammoPack_*` values to determine how much ammunition each pickup grants. The defaults below mirror the retail DLL so that arenas with scripted factories or `ammo_pack` entities award the same payloads players expect.【F:src/code/game/g_main.c†L88-L99】【F:src/code/game/g_main.c†L369-L380】【F:src/code/game/g_main.c†L539-L556】

| CVar | Default (rounds) | Notes |
| --- | --- | --- |
| `g_ammoPack_mg` | `50` | Machinegun bullet box pickup value.【F:src/code/game/g_main.c†L88-L99】【F:src/code/game/g_main.c†L369-L380】【F:src/code/game/g_main.c†L539-L546】 |
| `g_ammoPack_sg` | `10` | Shotgun shell pickup from shell boxes.【F:src/code/game/g_main.c†L88-L99】【F:src/code/game/g_main.c†L369-L380】【F:src/code/game/g_main.c†L539-L546】 |
| `g_ammoPack_gl` | `5` | Grenade launcher ammo pack payload.【F:src/code/game/g_main.c†L88-L99】【F:src/code/game/g_main.c†L369-L380】【F:src/code/game/g_main.c†L539-L546】 |
| `g_ammoPack_rl` | `5` | Rockets awarded by rocket ammo boxes.【F:src/code/game/g_main.c†L88-L99】【F:src/code/game/g_main.c†L369-L380】【F:src/code/game/g_main.c†L539-L546】 |
| `g_ammoPack_lg` | `60` | Lightning gun cell pickup amount.【F:src/code/game/g_main.c†L88-L99】【F:src/code/game/g_main.c†L369-L380】【F:src/code/game/g_main.c†L539-L546】 |
| `g_ammoPack_rg` | `10` | Railgun slug quantity from rail ammo.【F:src/code/game/g_main.c†L88-L99】【F:src/code/game/g_main.c†L369-L380】【F:src/code/game/g_main.c†L539-L546】 |
| `g_ammoPack_pg` | `30` | Plasma gun cell stack delivered by plasma packs.【F:src/code/game/g_main.c†L88-L99】【F:src/code/game/g_main.c†L369-L380】【F:src/code/game/g_main.c†L539-L546】 |
| `g_ammoPack_bfg` | `15` | BFG cell reserve per ammo canister.【F:src/code/game/g_main.c†L88-L99】【F:src/code/game/g_main.c†L369-L380】【F:src/code/game/g_main.c†L539-L546】 |
| `g_ammoPack_hmg` | `50` | Heavy machinegun belt pickup amount for Clan Arena and instagib mods.【F:src/code/game/g_main.c†L88-L99】【F:src/code/game/g_main.c†L372-L379】【F:src/code/game/g_main.c†L539-L556】 |
| `g_ammoPack_ng` | `20` | Nailgun spikes provided per pickup.【F:src/code/game/g_main.c†L88-L99】【F:src/code/game/g_main.c†L375-L378】【F:src/code/game/g_main.c†L553-L556】 |
| `g_ammoPack_pl` | `10` | Proximity launcher mines from ammo packs.【F:src/code/game/g_main.c†L88-L99】【F:src/code/game/g_main.c†L376-L378】【F:src/code/game/g_main.c†L553-L556】 |
| `g_ammoPack_cg` | `100` | Chaingun bullet reserve delivered by Team Arena ammo belts.【F:src/code/game/g_main.c†L88-L99】【F:src/code/game/g_main.c†L369-L380】【F:src/code/game/g_main.c†L553-L556】 |

### Usage notes

* `G_InitAmmoPackConfig` copies these CVars into `g_ammoPackConfig.weaponPickup[]`, which item pickups and factories consult when calling `G_AddAmmo` so gameplay scripts can adjust drop sizes without touching code.【F:src/code/game/g_main.c†L515-L556】
* Pair ammo pack tuning with spawn ammo overrides to balance weapon sustain across duel, TDM, and Clan Arena—lower pickup values encourage map control, while higher stacks reduce dry-fire downtime after respawns.【F:docs/gameplay/cvars.md†L5-L34】【F:src/code/game/g_main.c†L515-L556】

## Factory Item Spawn and Respawn Controls

The retail qagame CVar table keeps the global ammo-pack toggles latched and gamerule-scoped, keeps ammo and powerup respawn timing as gamerule inputs, and gives the six `g_spawnItem*` toggles the recovered `0x00040000 | CVAR_GAMERULE` flag pair.【F:src/game/g_config.c†L11-L252】【F:src/code/game/g_main.c†L1149-L1149】【F:tests/test_game_factory_regen_parity.py†L168-L344】

| CVar | Default | Retail flags | Wiring |
| --- | --- | --- | --- |
| `g_ammoPack` | `0` | `CVAR_LATCH | CVAR_GAMERULE` | Enables global `ammo_pack` entities and suppresses weapon-specific ammo spawns when active.【F:src/game/g_config.c†L235-L237】【F:src/code/game/g_items.c†L162-L191】 |
| `g_ammoPackHack` | `0` | `CVAR_LATCH | CVAR_GAMERULE` | Preserves the legacy global-ammo factory path used by older scripts.【F:src/game/g_config.c†L235-L237】【F:src/code/game/g_items.c†L1280-L1357】 |
| `g_ammoRespawn` | `40` | `CVAR_GAMERULE` | Supplies the cached ammo pickup respawn time, falling back to the retail 40 second default for invalid values.【F:src/game/g_config.c†L584-L590】【F:src/code/game/g_items.c†L1291-L1305】 |
| `g_powerupRespawn` | `120` | `CVAR_GAMERULE` | Overrides map powerup respawns when the factory cache provides a positive value.【F:src/code/game/g_main.c†L1149-L1149】【F:src/code/game/g_items.c†L1308-L1329】 |
| `g_spawnItemPowerup` | `1` | `0x00040000 | CVAR_GAMERULE` | Gates normal map powerup spawning separately from the `g_runes` persistent-powerup lane.【F:src/game/g_config.c†L247-L252】【F:src/code/game/g_items.c†L162-L191】 |
| `g_spawnItemHoldable` | `1` | `0x00040000 | CVAR_GAMERULE` | Controls holdable item spawn acceptance in factory-aware item paths.【F:src/game/g_config.c†L247-L252】【F:src/code/game/g_items.c†L162-L191】 |
| `g_spawnItemWeapons` | `1` | `0x00040000 | CVAR_GAMERULE` | Allows or suppresses world weapon entities while the legacy singular alias mirrors value changes.【F:src/game/g_config.c†L247-L252】【F:src/code/game/g_main.c†L108-L113】 |
| `g_spawnItemHealth` | `1` | `0x00040000 | CVAR_GAMERULE` | Gates map health pickups for regen-heavy factories.【F:src/game/g_config.c†L247-L252】【F:src/code/game/g_items.c†L162-L191】 |
| `g_spawnItemArmor` | `1` | `0x00040000 | CVAR_GAMERULE` | Gates map armor pickups when loadout factories want armor availability under script control.【F:src/game/g_config.c†L247-L252】【F:src/code/game/g_items.c†L162-L191】 |
| `g_spawnItemAmmo` | `1` | `0x00040000 | CVAR_GAMERULE` | Gates ammo entities, then switches between global ammo packs and per-weapon ammo families based on `g_ammoPack` / `g_ammoPackHack`.【F:src/game/g_config.c†L247-L252】【F:src/code/game/g_items.c†L162-L191】 |

## Weapon Damage Controls

The audited damage, splash, velocity, acceleration, weapon-special, Quad Hog, and prox-mine tranches match the retail qagame registration table for default strings and flags. The server reads the active gameplay rows into `g_weaponConfig`, refreshes that cache when CVars or factories change, and uses the cached values from weapon fire, missile spawn, acceleration-think, Quad Hog frame, and damage-clamp paths.【F:src/code/game/g_main.c†L1099-L1173】【F:src/code/game/g_main.c†L1322-L1398】【F:tests/test_game_weapon_parity.py†L290-L1244】

| CVar | Default | Notes |
| --- | --- | --- |
| `g_damage_bfg` | `100` | BFG projectile direct damage; splash damage remains controlled by `g_splashdamage_bfg`.【F:src/code/game/g_missile.c†L829-L856】 |
| `g_damage_cg` | `8` | Chaingun bullet damage routed through the chaingun spread/fire path.【F:src/code/game/g_weapon.c†L379-L383】【F:src/code/game/g_weapon.c†L1354-L1354】 |
| `g_damage_g` | `50` | Gauntlet melee damage before quad scaling.【F:src/code/game/g_weapon.c†L296-L309】 |
| `g_damage_gh` | `10` | Grappling hook impact damage used when the hook projectile hits a target.【F:src/code/game/g_missile.c†L940-L966】 |
| `g_damage_hmg` | `8` | Heavy machinegun bullet damage for supported game modes.【F:src/code/game/g_weapon.c†L379-L383】【F:src/code/game/g_weapon.c†L1327-L1327】 |
| `g_damage_gl` | `100` | Grenade launcher direct-hit damage; splash damage remains separate.【F:src/code/game/g_missile.c†L784-L817】 |
| `g_damage_lg` | `6` | Lightning gun beam tick damage and discharge damage multiplier.【F:src/code/game/g_weapon.c†L1042-L1070】 |
| `g_damage_lg_falloff` | `0` | Per-step lightning damage subtraction after the configured falloff range; retail default keeps constant damage.【F:src/code/game/g_weapon.c†L150-L177】 |
| `g_damage_mg` | `5` | Machinegun bullet damage outside team-specific overrides.【F:src/code/game/g_weapon.c†L379-L383】【F:src/code/game/g_weapon.c†L1324-L1324】 |
| `g_damage_ng` | `12` | Nailgun projectile damage before quad scaling in the firing wrapper.【F:src/code/game/g_missile.c†L977-L1004】【F:src/code/game/g_weapon.c†L1146-L1162】 |
| `g_damage_pg` | `20` | Plasmagun direct bolt damage before quad scaling.【F:src/code/game/g_main.c†L1343-L1345】【F:src/code/game/g_missile.c†L736-L762】 |
| `g_damage_pl` | `0` | Proximity launcher direct impact damage before mine arming.【F:src/code/game/g_main.c†L1378-L1380】【F:src/code/game/g_missile.c†L1015-L1052】 |
| `g_damage_rg` | `80` | Railgun shot damage before quad scaling and headshot adjustments.【F:src/code/game/g_main.c†L1353-L1353】【F:src/code/game/g_weapon.c†L735-L780】 |
| `g_damage_rl` | `100` | Rocket direct-hit damage, separate from splash damage.【F:src/code/game/g_main.c†L1336-L1338】【F:src/code/game/g_missile.c†L875-L918】 |
| `g_damage_sg` | `5` | Inner shotgun pellet-ring damage.【F:src/code/game/g_main.c†L1328-L1331】【F:src/code/game/g_weapon.c†L498-L539】 |
| `g_damage_sg_falloff` | `0` | Per-step shotgun pellet damage subtraction after `g_range_sg_falloff`; retail default keeps constant damage.【F:src/code/game/g_main.c†L1328-L1331】【F:src/code/game/g_weapon.c†L508-L539】 |
| `g_damage_sg_outer` | `5` | Outer shotgun pellet-ring damage for Quake Live's 20-pellet pattern.【F:src/code/game/g_main.c†L1328-L1331】【F:src/code/game/g_weapon.c†L498-L539】 |
| `g_splashdamage_gl` | `100` | Retail lowercase grenade splash damage cvar; source variable remains `g_splashDamage_gl` while the registered name matches retail.【F:src/code/game/g_main.c†L1108-L1110】【F:src/code/game/g_missile.c†L784-L817】 |
| `g_splashdamage_pg` | `15` | Retail lowercase plasma splash damage cvar feeding plasma missile impact damage.【F:src/code/game/g_main.c†L1118-L1119】【F:src/code/game/g_missile.c†L736-L762】 |
| `g_splashdamage_rl` | `84` | Retail lowercase rocket splash damage cvar; Quake Live uses `84`, not the classic `100`, as the default splash payload.【F:src/code/game/g_main.c†L1111-L1113】【F:src/code/game/g_missile.c†L875-L918】 |
| `g_splashdamage_bfg` | `100` | BFG splash damage payload, registered under the retail lowercase cvar name.【F:src/code/game/g_main.c†L1122-L1124】【F:src/code/game/g_missile.c†L829-L856】 |
| `g_splashdamage_pl` | `100` | Proximity mine splash damage payload, registered under the retail lowercase cvar name.【F:src/code/game/g_main.c†L1115-L1117】【F:src/code/game/g_missile.c†L1015-L1067】 |
| `g_splashradius_bfg` | `80` | BFG splash radius; Quake Live's retail default is `80`, not the classic `120`.【F:src/code/game/g_main.c†L1122-L1124】【F:src/code/game/g_missile.c†L829-L856】 |
| `g_splashradius_gl` | `150` | Grenade splash radius around the impact point.【F:src/code/game/g_main.c†L1108-L1110】【F:src/code/game/g_missile.c†L784-L817】 |
| `g_splashradius_pg` | `20` | Plasma bolt splash radius.【F:src/code/game/g_main.c†L1118-L1119】【F:src/code/game/g_missile.c†L736-L762】 |
| `g_splashradius_pl` | `150` | Proximity mine splash radius after detonation.【F:src/code/game/g_main.c†L1115-L1117】【F:src/code/game/g_missile.c†L1015-L1067】 |
| `g_splashradius_rl` | `120` | Rocket splash radius around the adjusted impact point.【F:src/code/game/g_main.c†L1111-L1113】【F:src/code/game/g_missile.c†L875-L918】 |
| `g_range_lg_falloff` | `768` | Lightning falloff interval paired with `g_damage_lg_falloff`; the default range is present even though default falloff damage is zero.【F:src/code/game/g_main.c†L1349-L1351】【F:src/code/game/g_weapon.c†L150-L177】 |
| `g_range_sg_falloff` | `768` | Shotgun falloff interval paired with `g_damage_sg_falloff`; default falloff damage keeps stock constant pellet damage.【F:src/code/game/g_main.c†L1328-L1331】【F:src/code/game/g_weapon.c†L508-L539】 |
| `g_rocketsplashOffset` | `-10.0` | Rocket splash-origin offset along the impact normal before radius damage runs.【F:src/code/game/g_main.c†L1154-L1154】【F:src/code/game/g_missile.c†L470-L519】 |
| `g_accelFactor_bfg` | `1` | BFG acceleration multiplier registered as `0x00040000 | CVAR_GAMERULE`; values above the retail default compound projectile velocity on each acceleration think.【F:src/code/game/g_main.c†L1133-L1134】【F:src/code/game/g_missile.c†L384-L423】 |
| `g_accelFactor_pg` | `1` | Plasmagun acceleration multiplier registered as `0x00040000 | CVAR_GAMERULE`; default `1` keeps the retail constant-velocity bolt path.【F:src/code/game/g_main.c†L1131-L1132】【F:src/code/game/g_missile.c†L371-L383】 |
| `g_accelFactor_rl` | `1` | Rocket acceleration multiplier registered as `0x00040000 | CVAR_GAMERULE` and shared by the guided-rocket synchronization helper.【F:src/code/game/g_main.c†L1129-L1130】【F:src/code/game/g_missile.c†L537-L577】 |
| `g_accelRate_bfg` | `16` | BFG acceleration think interval in milliseconds, registered with plain `CVAR_GAMERULE` like retail.【F:src/code/game/g_main.c†L1133-L1134】【F:src/code/game/g_missile.c†L384-L423】 |
| `g_accelRate_pg` | `16` | Plasmagun acceleration think interval in milliseconds, registered with plain `CVAR_GAMERULE` like retail.【F:src/code/game/g_main.c†L1131-L1132】【F:src/code/game/g_missile.c†L371-L383】 |
| `g_accelRate_rl` | `16` | Rocket acceleration think interval in milliseconds, registered with plain `CVAR_GAMERULE` like retail.【F:src/code/game/g_main.c†L1129-L1130】【F:src/code/game/g_missile.c†L562-L577】 |
| `g_velocity_bfg` | `1800` | BFG projectile speed registered as `0x00040000 | CVAR_GAMERULE` and applied in the BFG projectile constructor.【F:src/code/game/g_main.c†L1138-L1138】【F:src/code/game/g_missile.c†L829-L856】 |
| `g_velocity_gl` | `700` | Grenade launcher projectile speed registered as `0x00040000 | CVAR_GAMERULE` and applied to the gravity projectile path.【F:src/code/game/g_main.c†L1135-L1135】【F:src/code/game/g_missile.c†L784-L817】 |
| `g_velocity_pg` | `2000` | Plasmagun projectile speed registered as `0x00040000 | CVAR_GAMERULE` and used for both networked speed and trajectory delta.【F:src/code/game/g_main.c†L1137-L1137】【F:src/code/game/g_missile.c†L736-L762】 |
| `g_velocity_rl` | `1000` | Rocket projectile speed registered as `0x00040000 | CVAR_GAMERULE` and routed through `G_SynchronizeRocketConfig` so guided and accelerated rockets share the same base speed.【F:src/code/game/g_main.c†L1136-L1136】【F:src/code/game/g_missile.c†L537-L577】 |
| `g_velocity_gh` | `1800` | Grappling hook projectile speed registered as `0x00040000 | CVAR_GAMERULE` and routed through `G_SynchronizeGrappleConfig`.【F:src/code/game/g_main.c†L1139-L1139】【F:src/code/game/g_missile.c†L928-L971】 |
| `g_guidedRocket` | `0` | Guided rocket toggle registered with retail `CVAR_GAMERULE`; when enabled, rockets arm `G_RunGuidedRocketThink`.【F:src/code/game/g_main.c†L1153-L1153】【F:src/code/game/g_missile.c†L592-L620】 |
| `g_lightningDischarge` | `0` | Lightning discharge toggle registered as `0x00040000 | CVAR_GAMERULE` and mirrored into the custom-settings mask when non-zero.【F:src/code/game/g_main.c†L1140-L1140】【F:src/code/game/g_weapon.c†L923-L926】 |
| `g_railJump` | `0` | Rail jump impulse strength registered as `0x00040000 | CVAR_GAMERULE` and applied when a rail shot finds nearby solid geometry.【F:src/code/game/g_main.c†L1141-L1141】【F:src/code/game/g_weapon.c†L185-L214】 |
| `g_gauntletSpeedFactor` | `1.0` | Gauntlet swing timing factor registered with retail `CVAR_GAMERULE` and copied into the pmove settings cache.【F:src/code/game/g_main.c†L1142-L1142】【F:src/code/game/g_pmove.c†L379-L386】 |
| `g_headShotDamage_rg` | `0` | Railgun headshot bonus registered as `0x00040000 | CVAR_GAMERULE` and advertised through `CUSTOM_SETTING_HEADSHOTS` when active.【F:src/code/game/g_main.c†L1143-L1143】【F:src/code/game/g_main.c†L2145-L2146】 |
| `g_ironsights_mg` | `1.0` | Machinegun ironsight scale registered with retail `CVAR_TEMP | 0x00040000 | CVAR_GAMERULE` and cached for pmove prediction.【F:src/code/game/g_main.c†L1144-L1144】【F:src/code/game/g_pmove.c†L369-L376】 |
| `g_midAirMinHeight` | `96` | Minimum air height used by splash midair awards, registered with retail `CVAR_GAMERULE` and cached for missile-side ground traces.【F:src/code/game/g_main.c†L1145-L1145】【F:src/code/game/g_missile.c†L37-L68】 |
| `g_nailbounce` | `1` | Nailgun bounce count registered as `0x00040000 | CVAR_GAMERULE` and used by the missile bounce guard.【F:src/code/game/g_main.c†L1146-L1146】【F:src/code/game/g_missile.c†L641-L659】 |
| `g_nailbouncepercentage` | `65` | Nailgun bounce chance registered as `0x00040000 | CVAR_GAMERULE`, clamped to `100`, and sampled when each nail is spawned.【F:src/code/game/g_main.c†L1147-L1147】【F:src/code/game/g_missile.c†L1008-L1016】 |
| `g_nailcount` | `10` | Nailgun shot count registered as `0x00040000 | CVAR_GAMERULE` and used for both projectile emission and accuracy accounting.【F:src/code/game/g_main.c†L1148-L1148】【F:src/code/game/g_weapon.c†L1152-L1162】 |
| `g_nailspeed` | `1000` | Random span added to Nailgun bolt velocity, registered as `0x00040000 | CVAR_GAMERULE` and sampled for each spawned nail.【F:src/code/game/g_main.c†L1150-L1150】【F:src/code/game/g_missile.c†L1023-L1032】 |
| `g_nailspread` | `400` | Nailgun direction spread scalar, registered as `0x00040000 | CVAR_GAMERULE` and applied before bolt direction normalization.【F:src/code/game/g_main.c†L1151-L1151】【F:src/code/game/g_missile.c†L1020-L1032】 |
| `g_damagePlums` | `2` | Retail registers this row as `CVAR_GAMERULE`; the recovered qagame corpus shows no extra server-side gate, so damage-plum transport stays on the restored event path.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L848-L851】【F:src/code/game/g_combat.c†L274-L293】 |
| `g_quadDamageFactor` | `3` | Quad damage multiplier registered as `CVAR_SERVERINFO | CVAR_GAMERULE`, cached for weapon/combat scaling, and mirrored in the server-settings UI slab.【F:src/code/game/g_main.c†L1156-L1156】【F:src/code/game/g_main.c†L1974-L1982】 |
| `g_quadHog` | `0` | Quad Hog toggle registered as `CVAR_LATCH | 0x00040000 | CVAR_GAMERULE`; when enabled in FFA, quad pickups arm the retail-style carrier timers.【F:src/code/game/g_main.c†L1157-L1157】【F:src/code/game/g_main.c†L8595-L8701】 |
| `g_quadHogIdle` | `20` | Seconds of inactivity before a Quad Hog carrier is stripped of Quad, registered with retail `CVAR_GAMERULE`.【F:src/code/game/g_main.c†L1158-L1158】【F:src/code/game/g_main.c†L8676-L8681】 |
| `g_quadHogTime` | `60` | Seconds a Quad Hog carrier may hold Quad before expiry; the source multiplies this seconds value to milliseconds just like the retail timer path.【F:src/code/game/g_main.c†L1159-L1159】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L5424-L5429】 |
| `g_quadHogPingRate` | `1500` | Milliseconds between Quad Hog pings; unlike the seconds-based time and idle rows, retail stores and applies this value directly as milliseconds.【F:src/code/game/g_main.c†L1160-L1160】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L6150-L6157】 |
| `g_proxMineTimeout` | `20` | Seconds before an armed proximity mine auto-explodes, registered as `0x00040000 | CVAR_GAMERULE` and multiplied by `1000` when the mine arms.【F:src/code/game/g_main.c†L1173-L1173】【F:src/code/game/g_missile.c†L213-L218】 |

### Usage notes

* `G_ClampModDamage` rechecks active MOD damage against `g_weaponConfig`, so mid-match cvar changes cannot leave stale higher damage values on already-wired attack paths.【F:src/code/game/g_combat.c†L378-L449】
* `G_UpdateWeaponConfig` is reached from regular `G_UpdateCvars` polling and factory refreshes, keeping admin changes and scripted factory overrides on the same cached damage path.【F:src/code/game/g_main.c†L1398-L1400】【F:src/code/game/g_main.c†L1877-L1880】【F:src/code/game/g_factory.c†L920-L928】
* The audited velocity, acceleration, Nailgun speed/spread, prox timeout, and Quad Hog toggle rows participate in the custom-settings mask, so factory scripts and server info can identify non-retail projectile and powerup tuning alongside damage and splash changes.【F:src/game/g_config.c†L761-L859】【F:src/code/game/g_main.c†L2134-L2138】
* `g_quadHogTime`, `g_quadHogIdle`, and `g_proxMineTimeout` are seconds-based rows, while `g_quadHogPingRate` is already milliseconds. Keep that unit split when writing factories; using `1500` for ping rate means 1.5 seconds, not 25 minutes.【F:tests/test_game_weapon_parity.py†L1131-L1244】

## Knockback Controls

`g_knockback` remains the global scalar, but Quake Live extends it with per-weapon `g_knockback_*` hooks that influence how far targets (and players who self-damage) are launched. Defaults mirror the shipping DLL and are loaded into `g_knockbackConfig` during `G_InitKnockbackConfig`.【F:src/game/g_config.c†L45-L63】【F:src/game/g_config.c†L257-L276】【F:src/game/g_config.c†L887-L917】

| CVar | Default | Notes |
| --- | --- | --- |
| `g_knockback` | `1000` | Global scalar applied after the per-weapon knockback value is computed.【F:src/code/game/g_main.c†L1077-L1077】【F:src/code/game/g_combat.c†L1807-L1807】 |
| `g_max_knockback` | `120` | Retail gamerule cap applied only to positive weapon-scaled knockback; invalid non-positive values fall back to `120`.【F:src/code/game/g_main.c†L1078-L1078】【F:src/game/g_config.c†L908-L915】【F:src/code/game/g_combat.c†L1761-L1765】 |
| `g_knockback_g` | `1` | Gauntlet knockback multiplier applied to melee hits.【F:src/game/g_config.c†L257-L257】 |
| `g_knockback_mg` | `1` | Machinegun knockback scaling for bullet hits.【F:src/game/g_config.c†L258-L258】 |
| `g_knockback_sg` | `1` | Shotgun pellet knockback multiplier.【F:src/game/g_config.c†L259-L259】 |
| `g_knockback_gl` | `1.10` | Grenade launcher knockback scaling for direct and splash damage.【F:src/game/g_config.c†L260-L260】 |
| `g_knockback_rl` | `0.90` | Rocket launcher enemy knockback multiplier.【F:src/game/g_config.c†L261-L261】 |
| `g_knockback_rl_self` | `1.10` | Self-inflicted rocket knockback used for rocket jumps.【F:src/game/g_config.c†L262-L262】 |
| `g_knockback_lg` | `1.75` | Lightning gun knockback multiplier per beam tick.【F:src/game/g_config.c†L263-L263】 |
| `g_knockback_rg` | `0.85` | Railgun knockback scaling, affecting enemy displacement after hits.【F:src/game/g_config.c†L264-L264】 |
| `g_knockback_pg` | `1.10` | Plasmagun enemy knockback multiplier.【F:src/game/g_config.c†L265-L265】 |
| `g_knockback_pg_self` | `1.30` | Self-inflicted plasmagun knockback for plasma climbing.【F:src/game/g_config.c†L266-L266】 |
| `g_knockback_bfg` | `1` | BFG knockback scalar across splash and tracer hits.【F:src/game/g_config.c†L267-L267】 |
| `g_knockback_gh` | `-5` | Grappling hook pull strength; negative values reel players inward.【F:src/game/g_config.c†L268-L268】 |
| `g_knockback_ng` | `1` | Nailgun knockback multiplier for Team Arena modes.【F:src/game/g_config.c†L269-L269】 |
| `g_knockback_pl` | `1` | Proximity mine knockback scalar for explosions.【F:src/game/g_config.c†L270-L270】 |
| `g_knockback_cg` | `1` | Chaingun knockback multiplier.【F:src/game/g_config.c†L271-L271】 |
| `g_knockback_hmg` | `1` | Heavy machinegun knockback control for PQL/CA weapons.【F:src/game/g_config.c†L272-L272】 |
| `g_knockback_z` | `24` | Retail table cvar retained and cached for parity; the committed `G_Damage` HLIL slice does not read it.【F:src/game/g_config.c†L273-L273】【F:src/game/g_config.c†L904-L904】 |
| `g_knockback_z_self` | `24` | Retail self-knockback table cvar retained and cached for parity; the committed `G_Damage` HLIL slice does not read it.【F:src/game/g_config.c†L274-L274】【F:src/game/g_config.c†L905-L905】 |
| `g_knockback_cripple` | `0` | Minimum `PMF_TIME_KNOCKBACK` `pm_time` floor when damage newly latches knockback movement blocking.【F:src/game/g_config.c†L276-L276】【F:src/code/game/g_combat.c†L1816-L1830】 |

### Usage notes

* `G_KnockbackScaleForMOD` in `g_combat.c` consumes the `g_knockbackConfig` weapon scalars for both enemy and self-damage cases, tying the CVars directly to rocket jumping, plasma climbing, and grapple pulls while preserving negative grapple-style knockback.【F:src/code/game/g_combat.c†L1481-L1538】
* The first ten weapon-specific rows (`g_knockback_g` through `g_knockback_pg_self`) match the retail qagame table for default spelling and flags: `0x00040000 | CVAR_GAMERULE`.【F:src/game/g_config.c†L257-L266】【F:tests/test_game_weapon_parity.py†L23-L178】
* The second knockback tranche keeps global `g_knockback`, BFG/grapple/Team Arena weapon scalars, table-retained z rows, max clamp, and the cripple timer floor on their retail defaults and flags.【F:src/code/game/g_main.c†L1077-L1078】【F:tests/test_game_weapon_parity.py†L178-L326】
* Damage-side blocking is a playerstate contract: `G_Damage` latches `PMF_TIME_KNOCKBACK`, `PM_Friction` suppresses normal ground friction while it is set, `PM_WalkMove` uses the slick/knockback air-acceleration path, and `PM_DropTimers` clears `PMF_ALL_TIMES` when `pm_time` expires.【F:src/code/game/g_combat.c†L1812-L1830】【F:src/code/game/bg_pmove.c†L691-L691】【F:src/code/game/bg_pmove.c†L1740-L1753】【F:src/code/game/bg_pmove.c†L2776-L2783】
* No-knockback callers still land damage without movement blocking: target lasers pass `DAMAGE_NO_KNOCKBACK`, juiced proximity mine discharge uses the same flag, and null-direction damage is converted to `DAMAGE_NO_KNOCKBACK` inside `G_Damage`.【F:src/code/game/g_target.c†L342-L343】【F:src/code/game/g_missile.c†L260-L262】【F:src/code/game/g_combat.c†L1750-L1754】
* Damage feedback is separate from movement blocking: Quake Live's retail feedback record keeps armor, blood, `damage_from`, and `damage_fromWorld`, with no surviving `damage_knockback` field.【F:src/code/game/g_combat.c†L1949-L1952】【F:src/code/game/g_active.c†L424-L430】

### Regression checklist

* Use `cvarlist helptext_*` after the VM loads to confirm each help string registered with the expected description.
* Include a weapon in `g_startingWeapons` (for example `set g_startingWeapons RL`) and run `map_restart` to verify the spawn ammo mirrors `g_startingAmmo_rl`.
* Tweak `g_startingHealth`, `g_startingHealthBonus`, and `g_startingArmor`, issue a `map_restart`, and confirm the spawn health/armor reflect the new values while handicap clamping and respawn announcements remain intact.【F:src/code/game/g_client.c†L1433-L1512】
* Tweak a selection of cvars (for example `g_startingAmmo_rl` and `g_startingAmmo_pg`) and restart the map to confirm the new values drive the spawn stack.
* Persist a modified value (e.g. `seta g_startingAmmo_rl 25`) and restart the server to ensure the archived setting survives a relaunch.
* Ensure gauntlet and grapple defaults remain infinite (`-1`) after a `cvar_restart`.
* Change multiple `weapon_reload_*` CVars, issue a `map_restart`, and observe the new refire cadence in a live match to confirm `g_weaponReloadConfig` picked up the overrides.【F:src/code/game/g_main.c†L494-L508】
* Adjust `weapon_reload_rl` and `weapon_reload_lg`, trigger a `map_restart`, and ensure rockets and lightning ticks adopt the new delays immediately via `PM_GetWeaponReloadTime` and the pmove cache.【F:src/code/game/bg_pmove.c†L211-L250】【F:src/code/game/bg_pmove.c†L2398-L2417】【F:src/code/game/g_pmove.c†L170-L259】
* Override `g_ammoPack_*` values, pick up the corresponding ammo entities, and verify the awarded counts match the configured integers across base maps and factory scripts.【F:src/code/game/g_main.c†L515-L556】
* Adjust `g_knockback_*` scalars (including the self variants), perform rocket and plasma jumps, and check that `G_KnockbackScaleForMOD` applies the updated force for both enemy hits and self-damage before `G_Damage` applies the signed knockback path.【F:src/code/game/g_combat.c†L1481-L1538】【F:src/code/game/g_combat.c†L1756-L1830】

## Spawn Grant and Spectator Controls

Quake Live exposes server-only knobs for tuning spawn loadouts and controlling how spectators behave in live matches. Administrators can pre-seed inventory by mirroring the `give` console syntax, limit how many delayed respawns are queued at once, and force players into spectator roles with either free-cam access or scoreboard-only views. The VM reads the CVars below at runtime so toggling them during a match takes effect without restarts.【F:src/code/game/g_main.c†L402-L405】【F:src/code/game/g_client.c†L1760-L2140】【F:src/code/game/g_spawn.c†L692-L894】【F:src/code/game/g_cmds.c†L560-L950】【F:src/code/game/g_session.c†L40-L120】

| CVar | Default | Notes |
| --- | --- | --- |
| `g_grantItemOnSpawn` | *(empty)* | Parsed by `G_GrantConfiguredItems`, allowing whitespace/comma-delimited `give` tokens (`ammo`, weapon names, etc.) to run every time `ClientSpawn` executes so duel servers can inject armor or health buffs without enabling cheats.【F:src/code/game/g_main.c†L402-L405】【F:src/code/game/g_client.c†L1760-L2140】【F:src/code/game/g_cmds.c†L276-L360】 |
| `g_loadout` | `0` | Retail registers the loadout advert as `CVAR_SERVERINFO | CVAR_GAMERULE`. Votes flip it between `ON` and `OFF`, the server mirrors it to clients through serverinfo, and cgame copies the value into `cg_loadout` for HUD decisions.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L1556-L1561】【F:src/game/g_config.c†L229-L235】【F:src/code/game/g_vote.c†L328-L340】【F:src/code/cgame/cg_servercmds.c†L2917-L2917】 |
| `g_infiniteAmmo` | `0` | Retail registers this factory cvar as `CVAR_GAMERULE`. The game config cache reads it with the other factory bools, spawn loadouts convert configured ammo to infinite stacks when enabled, and weapon consumption keeps lightning discharge from draining finite ammo while the toggle is active.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L1317-L1323】【F:src/game/g_config.c†L229-L235】【F:src/code/game/g_client.c†L2058-L2063】【F:src/code/game/g_weapon.c†L944-L1069】 |
| `g_respawn_delay_min` | `2100` | Minimum milliseconds added to `client->respawnTime` on death before attack/use can respawn the player.【F:src/game/g_config.c†L92-L93】【F:src/code/game/g_combat.c†L41-L1269】【F:src/code/game/g_active.c†L1530-L1535】 |
| `g_respawn_delay_max` | `2400` | Extra post-minimum grace window in milliseconds; once elapsed, the dead-client think path respawns automatically even without attack/use input.【F:src/game/g_config.c†L92-L93】【F:src/code/game/g_active.c†L1530-L1535】 |
| `g_maxDeferredSpawns` | `4` | Caps how many delayed respawns may queue simultaneously; once the limit is hit, `G_RequestClientSpawn` falls back to instant spawns so scripts that stall respawns can't starve new requests.【F:src/code/game/g_main.c†L480-L483】【F:src/code/game/g_spawn.c†L692-L894】 |
| `g_teamSpawnAsSpec` | `0` | When non-zero in team modes, both `SetTeam` and `ClientSpawn` divert joiners into spectator slots and print the retail warning until administrators clear the flag.【F:src/code/game/g_main.c†L402-L405】【F:src/code/game/g_cmds.c†L560-L710】【F:src/code/game/g_client.c†L1850-L1930】 |
| `g_teamSpecFreeCam` | `0` | Governs whether spectators may free-fly during team/session handoffs; ranking handoffs and session persistence clamp to scoreboard-only states when the toggle is off, while retail `StopFollowing` itself always restores `SPECTATOR_FREE`.【F:src/code/game/g_main.c†L403-L404】【F:src/code/game/g_cmds.c†L700-L840】【F:src/code/game/g_active.c†L1039-L1083】【F:src/code/game/g_session.c†L40-L120】【F:src/code/game/g_rankings.c†L40-L130】 |
| `g_teamSpecSayEnable` | `1` | Blocks spectator chat unless enabled, matching Quake Live's retail messaging while still allowing tells to themselves so clients understand why their text was discarded.【F:src/code/game/g_main.c†L404-L405】【F:src/code/game/g_cmds.c†L880-L950】 |
