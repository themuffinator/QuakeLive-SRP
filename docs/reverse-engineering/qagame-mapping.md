# Qagame Mapping Ledger

This ledger tracks recurring high-confidence passes over the retail
`qagamex86.dll` against `src/code/game/` using the committed Ghidra corpus in
`references/reverse-engineering/ghidra/qagamex86/` and the Binary Ninja HLIL
dump in `references/hlil/quakelive/qagamex86.dll/`.

Observed facts come from exports, `functions.csv`, native dispatch-table slots,
log strings, and call flow. Inferred names are only promoted when the retail
behavior and source analogue align cleanly.

## Latest Coverage Update

- Reference totals: `1027` functions in `functions.csv`, `180` entries in `decompile_top_functions.c`.
- Curated symbol-map totals: `727` -> `731` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: `659/1027` -> `663/1027` mapped functions (`64.17%` -> `64.56%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: `162/180` -> `163/180` mapped functions (`90.00%` -> `90.56%`).
- Delta from this pass: `+4` curated names, `+4` corpus-overlap matches, `+0.39` percentage points on full-corpus parity, and `+1` match on the top-decompiled slice.
- Note: curated overhang stays flat at `68` because every promoted helper in this batch is present in the committed `functions.csv` corpus; the top-slice gain is `BotUpdateTrainingState`.

## Newly Mapped In This Pass

| Area | Recovered functions |
| --- | --- |
| Retail training selectors | `BotGetLocalClient` and `BotGetFirstBotClient` |
| Training-state helpers | `BotSetTrainingBotState` and `BotUpdateTrainingState` |
| Source-side cleanup | `src/code/game/ai_main.c` now drops the dead GPL `BotReportStatus`, `BotTeamplayReport`, `BotSetInfoConfigString`, and `BotUpdateInfoConfigStrings` slab after the earlier `BotAIStartFrame` retail correction |

This pass closes the next retail-only training seam that feeds the late
`BotAIStartFrame` tail. The newly named selectors identify the local player and
the first bot client used by the tutorial flow, while the adjacent state
helpers cover the training-mode entity flag toggle and the broader training
state updater that manages tutorial cvars, starting skill bootstrap, and music.
On the source side, `src/code/game/ai_main.c` now removes the dead GPL
`CS_BOTINFO` report helper slab that no longer has any retail frame-path
callers after the earlier `bot_report` cleanup.

## Previous Coverage Update

- Reference totals: `1027` functions in `functions.csv`, `180` entries in `decompile_top_functions.c`.
- Curated symbol-map totals: `720` -> `727` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: `652/1027` -> `659/1027` mapped functions (`63.49%` -> `64.17%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: `160/180` -> `162/180` mapped functions (`88.89%` -> `90.00%`).
- Delta from this pass: `+7` curated names, `+7` corpus-overlap matches, `+0.68` percentage points on full-corpus parity, and `+2` matches on the top-decompiled slice.
- Note: curated overhang stays flat at `68` because every promoted helper in this batch is present in the committed `functions.csv` corpus; the top-slice gains are `BotFindInstaGibTarget` and `BotPublishDebugInfoString`.

## Newly Mapped In The Previous Pass

| Area | Recovered functions |
| --- | --- |
| Instagib target-goal seam | `BotFindInstaGibTarget`, `BotRefreshInstaGibTargetGoal`, and `BotGetInstaGibTargetGoal` |
| `ai_main` retail telemetry | `BotPublishDebugInfoString`, `BotCanSpawnTourPoint`, `BotUpdateItemDelayTime`, and `BotAppendDynamicSkillSample` |
| Source-side frame correction | `BotAIStartFrame` now matches retail more closely by keeping `bot_report` updated without running the stale GPL `BotUpdateInfoConfigStrings()` / `CS_BOTINFO` publish loop |

This pass closes the next retail-only `ai_main` support seam around the
instagib tutorial node, the selected-bot debug publisher, and the training
tail that sits after `BotAIStartFrame`'s main bot-think loop. The instagib
cluster now has coherent target-finding and goal-refresh names, while the
later `ai_main` helpers cover the exact `bot_itemDelayTime` cvar writer, the
dynamic-skill sample recorder, and the tour-point spawn gate used by the
tutorial flow. On the source side, `src/code/game/ai_main.c` now drops the
stale GPL-era `bot_report` info-configstring publish branch that no longer
appears in the retail `BotAIStartFrame` body.

## Previous Coverage Update

- Reference totals: `1027` functions in `functions.csv`, `180` entries in `decompile_top_functions.c`.
- Curated symbol-map totals: `594` -> `607` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: `526/1027` -> `539/1027` mapped functions (`51.22%` -> `52.48%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: `149/180` -> `152/180` mapped functions (`82.78%` -> `84.44%`).
- Delta from this pass: `+13` curated names, `+13` corpus-overlap matches, `+1.27` percentage points on full-corpus parity, and `+3` matches on the top-decompiled slice.
- Note: curated overhang stays flat at `68` because every promoted helper in this batch is present in the committed `functions.csv` corpus; only `BotUpdateInventory`, `BotUseKamikaze`, and `BotUseInvulnerability` land inside `decompile_top_functions.c`.

## Newly Mapped In The Previous Pass

| Area | Recovered functions |
| --- | --- |
| Inventory and aggression seam | `BotUpdateInventory`, `BotUpdateBattleInventory`, `BotAggression`, `BotCanAndWantsToRocketJump`, and `BotHasPersistantPowerupAndWeapon` |
| Active battle item use | `BotUseKamikaze`, `BotUseInvulnerability`, `BotBattleUseItems`, and `BotIsObserver` |
| Camping and powerup flow | `BotGoCamp`, `BotWantsToCamp`, `BotDontAvoid`, and `BotGoForPowerups` |

This pass closes the next coherent `ai_dmq3.c` utility seam around bot
inventory refresh, consumable use, and long-term camp or powerup decisions. The
recovered set covers the live inventory snapshot, enemy-distance bookkeeping,
aggression scoring, kamikaze and invulnerability activation, and the full camp
spot plus avoid-goal helpers that feed higher-level long-term goal selection.

## Previous Coverage Update

- Reference totals: `1027` functions in `functions.csv`, `180` entries in `decompile_top_functions.c`.
- Curated symbol-map totals: `374` -> `377` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: `342/1027` -> `345/1027` mapped functions (`33.30%` -> `33.59%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: `108/180` -> `110/180` mapped functions (`60.00%` -> `61.11%`).
- Delta from this pass: `+3` curated names, `+3` corpus-overlap matches, `+0.29` percentage points on full-corpus parity, and `+2` matches on the top-decompiled slice.
- Note: `32` curated helper names currently sit outside `functions.csv`, so curated symbol-map totals are tracked separately from corpus-overlap parity.

## Newly Reconstructed In The Previous Pass

| Area | Recovered functions |
| --- | --- |
| Spawn ranking seam | retail-only `G_SelectRankedSpawnPoint`, retail-only `G_SelectClientSpawnPoint`, and retail-only `Team_SelectDominationSpawnPoint` |
| Source-side spawn reconstruction | Domination now selects owned point-linked respawns instead of piggybacking entirely on the CTF path, and `ClientSpawn` now routes through the recovered retail helper split instead of keeping all gametype branching inline |

This pass closes the next high-yield qagame spawn-selection seam around the
ClientSpawn path. The remaining hidden debug-command tail still needs a cleaner
body-to-dispatch match before promotion, but the broader spawn-selection band
is now mapped through the Domination-specific path, the shared ranked picker,
and the ClientSpawn-side wrapper.

## Earlier Coverage Update

- Reference totals: `1027` functions in `functions.csv`, `180` entries in `decompile_top_functions.c`.
- Curated symbol-map totals: `362` -> `370` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: `331/1027` -> `338/1027` mapped functions (`32.23%` -> `32.91%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: `105/180` -> `105/180` mapped functions (`58.33%` -> `58.33%`).
- Delta from this pass: `+8` curated names, `+7` corpus-overlap matches, `+0.68` percentage points on full-corpus parity, and no change on the top-decompiled slice.
- Note: `32` curated helper names currently sit outside `functions.csv`, so curated symbol-map totals are tracked separately from corpus-overlap parity.

## Newly Mapped In The Earlier Pass

| Area | Recovered functions |
| --- | --- |
| Direct command surface | retail-only `Cmd_SetMatchTime_f` |
| Auto-record naming | retail-only `G_SanitizeFilenameToken`, retail-only `G_BuildAutoRecordBasename` |
| Match media automation | retail-only `G_StopAutoRecord`, retail-only `G_StartAutoRecordForClient`, retail-only `G_CheckAutoRecord` |
| Timeout state publication | retail-only `G_UpdateTimeoutConfigStrings` |
| Race respawn flow | retail-only `G_RaceResetClientAndSpawn` |

The remaining highest-yield unmapped seams now skew more toward the hidden
`markstate` / `diffstate` / `dumpentities` / `printentitystates` debug band
and the larger gameplay bootstrap and round-support bodies that still sit
outside the current curated map.

## Prior Coverage Update

- Reference totals: `1027` functions in `functions.csv`, `180` entries in `decompile_top_functions.c`.
- Before this pass: `147` curated mapped functions, `33/180` decompiled-top functions (`18.33%`).
- After this pass: `169` curated mapped functions, `55/180` decompiled-top functions (`30.56%`).
- Delta from this pass: `+22` curated mapped functions and `+12.23` percentage points on the top-decompiled slice.
- Curated string coverage was unchanged at `102/102`; that round widened function naming coverage rather than the string ledger.

## Previously Mapped In The Prior Sweep

| Area | Recovered functions |
| --- | --- |
| Bot chat and state nodes | `BotChatTest`, `BotGetLongTermGoal`, `AINode_Seek_NBG`, `AINode_Seek_LTG`, `AINode_Battle_Fight`, `AINode_Battle_Chase`, `AINode_Battle_Retreat`, `AINode_Battle_NBG` |
| Bot bootstrap and team control | `BotAI`, `BotAISetupClient`, `BotInitLibrary`, `BotSetupDeathmatchAI`, `BotTeamAI` |
| Bot spawn and writable gameplay helpers | `G_AddRandomBot`, `G_AddBot`, `RegisterItem`, `G_Say`, `Cmd_SetViewpos_f` |
| Gameplay utility and objective flow | `G_DroppedPowerupRunFrame`, `G_TryPushingEntity`, `Team_FragBonuses`, `Team_TouchOurFlag` |

The highest-yield remaining seams after that sweep skewed more toward
tutorial-specific bot flows, ranking/stat publishers, and other retail-only
utility helpers outside that widened control surface.

## Earlier Coverage Update

- Reference totals: `1027` functions in `functions.csv`, `180` entries in `decompile_top_functions.c`.
- Before this pass: `169` curated mapped functions, `55/180` decompiled-top functions (`30.56%`).
- After this pass: `185` curated mapped functions, `71/180` decompiled-top functions (`39.44%`).
- Delta from this pass: `+16` curated mapped functions and `+8.89` percentage points on the top-decompiled slice.
- Curated string coverage was unchanged at `102/102`; that pass widened function naming coverage rather than the string ledger.
## Key Mappings

| Retail address | Recovered name | Closest source analogue | Evidence summary | Confidence |
| --- | --- | --- | --- | --- |
| `0x10023400` | `BotAIStartFrame` | `ai_main.c::BotAIStartFrame` | Native dispatch-table slot plus the `memorydump` / `bot_memorydump` bot-debug cvars and the per-bot frame/routing update loop match the source bot frame driver. | High |
| `0x10033800` | `P_DamageFeedback` | `g_active.c::P_DamageFeedback` | Aggregates `damage_blood` and `damage_armor`, emits EV_PAIN and damage yaw/pitch, and clears the damage totals exactly like the client damage-feedback path. | High |
| `0x10033950` | `P_WorldEffects` | `g_active.c::P_WorldEffects` | Anchored by `sound/player/gurp1.wav` / `sound/player/gurp2.wav` plus the drowning, battlesuit, lava, and slime control flow. | High |
| `0x10033B20` | `G_SetClientSound` | `g_active.c::G_SetClientSound` | Selects the proxmine ticking loop sound or the lava/slime fry loop on the outgoing playerstate, matching the source helper. | High |
| `0x10033B80` | `ClientImpacts` | `g_active.c::ClientImpacts` | Walks unique pmove touchents and dispatches bot self-touch plus touched-entity callbacks exactly like the source post-pmove impact helper. | High |
| `0x10033C00` | `G_TouchTriggers` | `g_active.c::G_TouchTriggers` | Uses the `40,40,52` trigger range box, spectator teleporter gating, ET_ITEM proximity checks, and jump-pad frame reset logic from the source trigger-touch path. | High |
| `0x10033E30` | `SpectatorThink` | `g_active.c::SpectatorThink` | Sets `PM_SPECTATOR`, unlinks before `pmove`, relinks for `G_TouchTriggers`, and handles the attack-button follow cycle via `Cmd_FollowCycle_f`, matching the source spectator think flow. | High |
| `0x10033FD0` | `ClientInactivityTimer` | `g_active.c::ClientInactivityTimer` | Anchored by `Dropped due to inactivity`, the inactivity warning centerprint, and the `client:%i inactivity:%i` debug line. | High |
| `0x100341E0` | `G_CheckClientFlood` | Retail-only descriptive helper adjacent to `g_active.c::ClientThink_real` | Reads the client `floodCount` / `floodLastTime` state, decays it against the retail flood-protection cvars, and drops the offender with `Dropped for flooding the server` once the limit is exceeded. | High |
| `0x10034260` | `G_RunFactoryHealthRegen` | Retail-only split of `g_active.c::G_RunFactoryRegen` | Per-frame health regen sidecar tailcalled from `ClientTimerActions`; it waits out the last-damage delay, accumulates the configured regen tick interval, stops once health reaches the target, and applies whole-point health increases to the entity. | High |
| `0x100342F0` | `G_RunFactoryArmorRegen` | Retail-only split of `g_active.c::G_RunFactoryRegen` | Per-frame armor regen sidecar tailcalled after the health helper; it waits out the armor delay, honors the `regenArmorAfterHealth` gate, accumulates the regen tick interval, and applies whole-point armor increases to `ps.stats[STAT_ARMOR]`. | High |
| `0x100343E0` | `ClientTimerActions` | `g_active.c::ClientTimerActions` | Accumulates `timeResidual`, applies once-per-second regeneration and armor decay, and emits the regen event through adjacent Quake Live subhelpers in the same place the source calls `ClientTimerActions`. | High |
| `0x10034860` | `ClientEvents` | `g_active.c::ClientEvents` | Walks the recent playerstate event ring, applies fall damage, fires weapons, and handles teleporter, medkit, kamikaze, portal, invulnerability, and Harvester skull-drop item-use side effects exactly where the source server event switch sits. | High |
| `0x10034B50` | `StuckInOtherClient` | `g_active.c::StuckInOtherClient` | Scans live client entities for AABB overlap against the candidate player's expanded bounds and returns true once invulnerability expansion would still intersect another client. | High |
| `0x10034C00` | `SendPendingPredictableEvents` | `g_active.c::SendPendingPredictableEvents` | Creates temporary ET_EVENTS entities from pending playerstate events, clears/restores `externalEvent`, and targets all clients except the originator. | High |
| `0x10034C90` | `ClientThink_real` | `g_active.c::ClientThink_real` | Driven by the outer `ClientThink` export plus command-time clamping, spectator/inactivity gating, pmove, event dispatch, trigger touch, client impacts, respawn, and timer actions. | High |
| `0x10035410` | `ClientThink` | `g_active.c::ClientThink` | Native dispatch-table slot plus `trap_GetUsercmd`, the `lastCmdTime` write, and the bot-gated tailcall into the deeper think path align with the source export wrapper. | High |
| `0x10035470` | `SpectatorClientEndFrame` | `g_active.c::SpectatorClientEndFrame` | The body handles spectator follow targets, `follow1` / `follow2`, POI camera branches, `ClientBegin` fallback, and scoreboard flag toggling exactly like the source spectator end-frame routine. | High |
| `0x10035600` | `ClientEndFrame` | `g_active.c::ClientEndFrame` | Spectator short-circuit into `SpectatorClientEndFrame`, expired powerup cleanup, world/damage end-frame helpers, EF_CONNECTION handling, and final entity-state sync match the source end-frame path. | High |
| `0x10035960` | `G_CAADRespawnAsSpectator` | Retail-only shared Clan Arena / Attack and Defend respawn helper | Reached from the dead-client respawn gate once those modes push a player back into spectator follow; it copies the corpse into the body queue, forces `PM_SPECTATOR`, reruns `ClientSpawn`, and enters follow mode when both teams still have active players. | High |
| `0x10035780` | `G_ADResolveRoundState` | Retail-only Attack and Defend controller helper | Resolves expired deferred `AD_RoundStateTransition` work and returns the current A/D round-state latch used by damage, objective, and HUD callers. | High |
| `0x100357D0` | `G_ADHandleDamageScore` | Retail-only Attack and Defend damage helper | Reached from the main damage path; it applies the A/D self/team-damage suppression flags, resolves pending round-state work, and converts active-phase enemy damage into score once the accumulated threshold reaches 100. | High |
| `0x10035A20` | `G_ADCheckExitRules` | Retail-only Attack and Defend exit helper | Tie-aware A/D limit checker covering timelimit, side-specific scorelimit, and late mercylimit, with the matching retail print/log side effects. | High |
| `0x10035B70` | `AD_RoundStateTransition` | Retail-only Attack and Defend round-state controller | Anchored by `AD_RoundStateTransition: invalid state`; it updates the A/D match-state configstrings, respawns or releases participants, settles round winners, rotates turns, and schedules the next countdown/restart transition. | High |
| `0x100363E0` | `G_ADResolveAttackingTeam` | Retail-only Attack and Defend side helper | Resolves expired deferred `AD_RoundStateTransition` work and returns the currently attacking side during the active A/D phase. | High |
| `0x10036440` | `G_ADResolveDefendingTeam` | Retail-only Attack and Defend side helper | Resolves expired deferred `AD_RoundStateTransition` work and returns the currently defending side; the defense-award path calls it directly before incrementing `DEFENSE` credit. | High |
| `0x100364A0` | `G_ADResetScoreHistory` | Retail-only Attack and Defend scoreboard helper | Clears the retained A/D round-delta history and publishes the baseline `scores_ad` payload with current team totals and empty history slots. | High |
| `0x100365F0` | `G_ADUpdateScoreHistory` | Retail-only Attack and Defend scoreboard helper | Records the latest per-turn A/D score delta into the 20-entry circular history, rebuilds the ordered history window, and republishes `scores_ad`. | High |
| `0x10038160` | `G_CAADResetClientForRound` | Retail-only shared Clan Arena / Attack and Defend round helper | Reused from both `ClientBegin` and the delayed respawn path for GT_CLAN_ARENA and GT_ATTACK_DEFEND; it respawns immediately in the live release state, respawns into the holding state during the pre-release countdown, and otherwise falls back to the spectator-follow reset path used after round loss. | High |
| `0x10038B60` | `Team_SelectDominationSpawnPoint` | Retail-only Domination spawn helper / `g_team.c` analogue | Reached from the ClientSpawn-side spawn wrapper only for active GT_DOMINATION respawns; it walks `team_dom_point` entities, collects linked `info_player_deathmatch` targets for the owning team, ranks them against live players, and writes the chosen origin/angles. | High |
| `0x10039080` | `G_SelectRankedSpawnPoint` | Retail-only shared spawn helper spanning `g_client.c::SelectRandomFurthestSpawnPoint` and `g_team.c::SelectCTFSpawnPoint` | Anchored by the `info_player_deathmatch`, `team_CTF_redspawn`, `team_CTF_bluespawn`, `team_CTF_redplayer`, and `team_CTF_blueplayer` classnames plus the `FindIntermissionPoint` fallback; it filters telefragging candidates, ranks them against live players, and picks from the best-ranked subset. | High |
| `0x10039730` | `G_SelectClientSpawnPoint` | Retail-only ClientSpawn-side spawn wrapper | Called directly from `ClientSpawn` before the respawn bootstrap continues; it chooses between domination-linked spawns, team/base spawn classes, and the initial non-team spawn path, then falls back through the shared ranked spawn picker. | High |
| `0x1003A270` | `G_UpdateTournamentQueuePositions` | Retail-only duel queue helper | Sorts eligible waiting spectators by the stored queue timestamp, assigns one-based `pq` queue positions, and marks changed entries dirty for the follow-on userinfo republish pass. | High |
| `0x1003A450` | `ClientUserinfoChanged` | `g_client.c::ClientUserinfoChanged` | Native dispatch-table slot plus `ClientUserinfoChanged: %i %s` log string and matching configstring rebuild flow. | High |
| `0x1003AC10` | `ClientConnect` | `g_client.c::ClientConnect` | `ClientConnect: %i` log string, bot masking, session init/read, and platform auth checks match the source connect routine. | High |
| `0x1003B030` | `ClientBegin` | `g_client.c::ClientBegin` | `ClientBegin: %i` log string and the post-connect spawn/bootstrap path align with the source begin routine. | High |
| `0x1003B5A0` | `G_FinalizeSpawnLoadout` | Retail-only spawn/loadout helper | Post-`ClientSpawn` finalizer that honors `selected_spawn_weapon`, parses the configured spawn-grant tokens, seeds the starting ammo and weapon masks through the deeper helper at `0x1003B2A0`, and applies the remaining intermission and live-weapon cleanup for the spawned client. | High |
| `0x1003BC30` | `ClientSpawn` | `g_client.c::ClientSpawn` | Full retail spawn/bootstrap boundary that selects the spawn point, preserves the respawn-persistent client/session state, rebuilds the playerstate/entity defaults for the new life, and then tails into the deeper post-spawn finalization helper. | High |
| `0x1003C7E0` | `ClientDisconnect` | `g_client.c::ClientDisconnect` | Present in `functions.csv`, referenced by the native export table, and anchored by `ClientDisconnect: %i`. | High |
| `0x1003CBF0` | `DeathmatchScoreboardMessage` | `g_cmds.c::DeathmatchScoreboardMessage` | Retail scoreboard sender that dispatches through per-gametype builders, falls back to a compact `smscores` serializer when needed, sends the resulting payload to one client, and during intermission fans into the extra mode-specific stat publishers. | High |
| `0x1003CD70` | `G_BuildCompactScoreboardMessage` | Retail-only compact scoreboard helper | Emits the reduced `smscores` payload that `DeathmatchScoreboardMessage` uses when the richer per-mode payload would exceed the server-command limit or the compact-scoreboard gate is active. | High |
| `0x1003CEC0` | `G_BuildObeliskScoreboardMessage` | Retail-only Overload scoreboard helper | GT_OBELISK/default scoreboard serializer that emits the generic `scores` payload with the extra objective columns preserved in the retail build. | High |
| `0x1003D090` | `G_BuildFFAScoreboardMessage` | Retail-only FFA scoreboard helper | Emits `scores_ffa` with the expanded Quake Live FFA per-client stat block. | High |
| `0x1003D2B0` | `G_BuildDuelScoreboardMessage` | Retail-only duel scoreboard helper | Caches the lower and higher duel client numbers into the `level` tail, builds the viewer-facing weapon/timing summaries, and emits the appropriate `scores_duel` payload shape for one or two players. | High |
| `0x1003DBB0` | `G_BuildRaceScoreboardMessage` | Retail-only Race scoreboard helper / `g_race.c` analogue | Emits the `scores_race` payload with the sorted racer list and timing columns. | High |
| `0x1003DD20` | `G_BuildTeamScoreboardMessage` | Retail-only GT_TEAM scoreboard helper | Emits `scores_tdm` with the red/blue team totals plus the retail TDM per-client stat block. | High |
| `0x1003E1B0` | `G_SendTDMStatsMessage` | Retail-only postgame stats helper | Intermission-only `tdmstats` publisher reused by the TDM and Freeze scoreboard families. | High |
| `0x1003E300` | `G_BuildClanArenaScoreboardMessage` | Retail-only Clan Arena scoreboard helper | Emits the `scores_ca` payload with the retail CA per-client stat block. | High |
| `0x1003E510` | `G_SendCAStatsMessage` | Retail-only postgame stats helper | Intermission-only `castats` publisher for the Clan Arena scoreboard family. | High |
| `0x1003E6D0` | `G_BuildCTFStyleScoreboardMessage` | Retail-only shared CTF-style scoreboard helper | Shared serializer for CTF, One Flag, Harvester, Domination, and Attack and Defend. It emits the `scores_ctf` payload and hides the opposing-team detail block from live viewers when the retail policy requires it. | High |
| `0x1003EC40` | `G_SendCTFStatsMessage` | Retail-only postgame stats helper | Intermission-only `ctfstats` publisher reused by the CTF-style scoreboard families. | High |
| `0x1003EDA0` | `G_BuildFreezeScoreboardMessage` | Retail-only Freeze scoreboard helper | Emits the `scores_ft` payload with the Freeze-specific per-client stat block. | High |
| `0x1003F260` | `G_BuildRedRoverScoreboardMessage` | Retail-only Red Rover scoreboard helper | Emits the `scores_rr` payload with the Red Rover per-client stat block. | High |
| `0x100400F0` | `Cmd_TeamTask_f` | `g_cmds.c::Cmd_TeamTask_f` | Exact `Argc == 2` / `teamtask` userinfo rewrite flow from the stock command handler, ending in `ClientUserinfoChanged`. | High |
| `0x100406D0` | `SetTeam` | `g_cmds.c::SetTeam` | Outer team-change parser that handles `follow1`, `follow2`, spectator/team requests, duel-only spectate enforcement, and then forwards into the deeper retail execution helper. | High |
| `0x100423A0` | `Cmd_CallVote_f` | `g_cmds.c::Cmd_CallVote_f` | Vote-limit enforcement plus the `You have called the maximum number of votes` and `^3Callvote commands` strings. | High |
| `0x10044270` | `Cmd_Vote_f` | `g_cmds.c::Cmd_Vote_f` | Uses the `No vote in progress`, `Vote cast`, and `disable_vote_ui` strings in the source-equivalent vote-cast flow. | High |
| `0x100456B0` | `Cmd_Forfeit_f` | `g_cmds.c::Cmd_Forfeit_f` | Thin forfeit-command wrapper identified by the local pause/timeout and round-countdown rejection strings before the tailcall into the deeper retail forfeit helpers. | High |
| `0x10045BD0` | `Cmd_ReadyUp_f` | `g_cmds.c::Cmd_ReadyUp_f` | Retail ready-up command helper that toggles the per-client ready latch, enforces the minimum-player and team-presence gates, and prints the `Ready` / `Not Ready` warmup centerprint. | High |
| `0x10045DD0` | `ClientCommand` | `g_cmds.c::ClientCommand` | HLIL-visible command dispatch over `say_team`, `vsay_team`, `vosay_team`, `callvote`, `give`, `follow`, `team`, and other retail client commands matches the source dispatcher. | High |
| `0x10046970` | `TossClientCubes` | `g_combat.c::TossClientCubes` | Harvester skull-drop helper backed by the carried-skull count, the `Red Skull` / `Blue Skull` item lookups, and the death-path call that ejects the cubes before corpse cleanup. | High |
| `0x1004BC30` | `G_FreezeResolveRoundState` | Retail-only Freeze controller helper | Resolves any expired deferred round-state transition through `Freeze_RoundStateTransition` and returns the current Freeze controller state for HUD/end-frame callers. | High |
| `0x1004BC80` | `G_FreezeSetClientFrozenState` | Retail-only shared Freeze helper spanning `g_freeze.c::G_FreezeApplyFreezeState` and `g_freeze.c::G_FreezeThawClient` | Shared retail-only mutator that applies frozen or thawed client state, emits the corresponding temp-entity/event path, and refreshes the active-player tally used by the surrounding round controller. | High |
| `0x1004BDE0` | `G_FreezeResetClientForRound` | Retail-only per-client Freeze helper / `g_active.c::G_FreezeResetClientsForRound` analogue | Reused from `ClientBegin` and the delayed active-client reset path; restores clients for warmup or active-round starts and pushes them into the holding state when the controller is not ready to release them. | High |
| `0x1004BF10` | `G_FreezeTeamIsFullyFrozen` | Retail-only Freeze winner predicate | Hidden register-passed team scan used by `G_FreezeEvaluateRoundWinner`; it returns true once no connected members of that team remain unfrozen, letting the outer winner helper distinguish win versus draw. | High |
| `0x1004BF60` | `G_FreezeEvaluateRoundWinner` | Retail-only Freeze result helper / `g_active.c::G_FreezeEvaluateRoundWinner` analogue | Compares the PM_NORMAL living-player tallies and, once the configured draw-delay path is active, the corresponding living-health totals before storing the winning team latch consumed by the adjacent Freeze controller. | High |
| `0x1004C1B0` | `Freeze_RoundStateTransition` | Retail-only Freeze round-state controller | Anchored by `Freeze_RoundStateTransition: invalid state`; it resolves pending transition timers, updates `CS_MATCH_STATE`, resets clients for warmup and active states, and applies the Freeze round-complete transition. | High |
| `0x1004CB80` | `G_FreezeRunFrame` | `g_active.c::G_FreezeRunFrame` | Source-faithful Freeze outer frame boundary. Retail keeps the round-state readback and winner-selection pieces in adjacent helpers, but this function still performs the per-frame freeze update and round-end dispatch. | High |
| `0x1004CD40` | `G_FreezeClientEndFrame` | `g_client.c::G_FreezeClientEndFrame` | Tracks thaw progress, nearby allies, LOS and distance gates, and the auto-thaw timer before fanning into the shared retail Freeze state mutator. | High |
| `0x1004EE20` | `RespawnItem` | `g_items.c::RespawnItem` | Anchored by `RespawnItem: bad teammaster`; it restores grouped item spawns through the teammaster path, reenables item contents and visibility, emits the respawn event, and selects the retail powerup or kamikaze respawn sound. | High |
| `0x1004F020` | `Touch_Item` | `g_items.c::Touch_Item` | Anchored by `Item: %i %s\n`; it validates the touching client, routes by `item->giType` into the deeper pickup helpers, applies the pickup event/sound path, and updates retail per-item pickup telemetry. | High |
| `0x1004FD20` | `Use_Item` | `g_items.c::Use_Item` | Tiny HLIL-visible retail trampoline that preserves the classic use-to-respawn boundary by tailcalling `RespawnItem(ent)`. | High |
| `0x1004FD30` | `G_CheckTeamItems` | `g_items.c::G_CheckTeamItems` | Anchored by the missing red/blue/neutral flag and obelisk warnings; it verifies the active gametype has the required team objective entities in the map. | High |
| `0x100503F0` | `FinishSpawningItem` | `g_items.c::FinishSpawningItem` | Anchored by `FinishSpawningItem: %s startsolid at %s`; it sets ET_ITEM, model indices, touch/use callbacks, the drop-to-floor path, and the delayed powerup spawn gate before linking the entity. | High |
| `0x100507E0` | `G_SpawnItem` | `g_items.c::G_SpawnItem` | Source-faithful outer item spawn helper. It stores the `gitem_t`, parses retail `wait` / `random` overrides, registers assets, seeds persistent-powerup and global-sound flags, and schedules `FinishSpawningItem`. | High |
| `0x10052DC0` | `G_CanClientSeeClient` | Retail-only native export helper | Snapshot-side client-visibility predicate used for client entities: spectators, same-team viewers, the active Red Rover infection phase, and the One Flag bot special case all return true even when the stock PVS path would be the normal gate. | High |
| `0x10052E40` | `G_AreEnemyClients` | Retail-only native export helper | Validates two client slots and returns true only when they are distinct, non-spectators, and not on the same team. | High |
| `0x10052E90` | `G_ShouldSuppressVoiceToClient` | Retail-only native export helper | Steam-voice relay filter that returns true when delivery should be blocked for the candidate recipient, including bots, muted senders, and non-tell self echo; open/all-talk cases return false, otherwise the team/spectator policy falls through `OnSameTeam`. | High |
| `0x10052F40` | `G_IsObjectiveEntity` | Retail-only native export helper | Gametype-aware objective classifier that recognizes CTF/Attack-Defend flag items, One Flag targets, Overload obelisks, and the Quake Live extended item-objective flag path. | High |
| `0x10053020` | `G_FreezeCanSeeThawProgressEvent` | Retail-only Freeze native export helper | Freeze-only visibility predicate for thaw-progress temp entity event `0x58`; it checks the linked entity/player and returns true only for teammates of that linked target. | High |
| `0x100530C0` | `G_IsClientAdmin` | Retail-only native export helper | Native export-tail predicate that validates the client slot and returns true only when `sess.privilege == PRIV_ADMIN`. | High |
| `0x100530F0` | `G_GetClientScore` | Retail-only native export helper | Validates the client slot and returns `gclient->ps.persistant[PERS_SCORE]` from offset `0x100`. | High |
| `0x10053120` | `dllEntry` | Native qagame interface / `g_syscalls.c::dllEntry` analogue | Named export in HLIL and Ghidra. Retail stores the import table pointer, returns the direct-export table, and writes API version `10` through the third out-parameter. | High |
| `0x10053290` | `G_FindTeams` | `g_main.c::G_FindTeams` | Groups entities with matching `team` keys and ends with `%i teams with %i entities`. | High |
| `0x10053400` | `G_UpdateCustomSettingsMaskForCvar` | Retail-only cvar-table helper | Reused from both `G_RegisterCvars` and `G_UpdateCvars`; it recognizes custom-setting CVars such as `weapon_reload_gauntlet` and `g_damage_sg_outer`, then sets or clears the corresponding bits in the published `g_customSettings` mask. | High |
| `0x10054920` | `G_RegisterCvars` | `g_main.c::G_RegisterCvars` | Walks the main game cvar table, tracks `g_customSettings`, clamps `g_gametype`, and explicitly registers `g_version`, matching the retail registration pass. | High |
| `0x100549E0` | `G_InitPublishedCvarState` | Retail-only `G_InitGame` sidecar | Called immediately after `G_RegisterCvars`; it seeds the published factory/custom/loadout configstring slab plus the retail Domination/Red Rover numeric configstrings and snapshots the related cvar mirrors used later in gameplay. | High |
| `0x10054DD0` | `G_UpdateCvars` | `g_main.c::G_UpdateCvars` | Walks the same cvar table with modification-count tracking, refreshes `g_customSettings`, and fans into follow-on update handlers just like the retail cvar update pass. | High |
| `0x10054F00` | `FindIntermissionPoint` | `g_main.c::FindIntermissionPoint` | Anchored by `info_player_intermission` plus the warning fallback and the target-facing intermission-angle adjustment. | High |
| `0x10055000` | `G_CountSpawnPoints` | Retail-only descriptive helper inside `g_main.c::G_InitGame` | Clears the cached spawn counters, then scans all entities for `info_player_deathmatch`, `team_CTF_redspawn`, and `team_CTF_bluespawn` before the rest of `G_InitGame` continues. | High |
| `0x10055110` | `G_InitGame` | `g_main.c::G_InitGame` | `InitGame: %s` log line, cvar/bootstrap flow, entity/client initialization, and the inlined session/spawn setup all match. | High |
| `0x10055610` | `G_ShutdownGame` | `g_main.c::G_ShutdownGame` | `==== ShutdownGame ====` and `ShutdownGame:` strings plus session persistence on teardown. | High |
| `0x10055710` | `G_FindNextTournamentPlayer` | Retail-only descriptive helper split from `g_main.c::AddTournamentPlayer` | Returns the oldest waiting spectator while excluding scoreboard spectators and invalid follow states, matching the inner duel queue selector that the source keeps inline. | High |
| `0x10055780` | `AddTournamentPlayer` | `g_main.c::AddTournamentPlayer` | Duel-only queue promotion path that counts active players, chooses the oldest waiting spectator, calls `SetTeam(..., "f")`, and resets warmup/game-state latches when the second player joins. | High |
| `0x10055900` | `RemoveTournamentLoser` | `g_main.c::RemoveTournamentLoser` | Duel-only queue demotion path that selects `level.sortedClients[1]` when two players are active and calls `SetTeam(..., "s")` to send the loser back to spectator. | High |
| `0x10055950` | `AdjustTournamentScores` | `g_main.c::AdjustTournamentScores` | Tournament intermission helper that increments the winner's wins and loser's losses via `level.sortedClients`, then refreshes both configstrings through `ClientUserinfoChanged`. | High |
| `0x100559E0` | `G_UpdateAwardConfigstrings` | Retail-only award publisher appended to `g_main.c::CalculateRanks` | Tailcalled from both `SendScoreboardMessageToAllClients` and `CalculateRanks`; it selects winning clients for the legacy retail award configstrings at `0x2B4`, `0x2B5`, and `0x2B8-0x2BB` and publishes them through the shared `%i` formatter. | High |
| `0x10055E50` | `SendScoreboardMessageToAllClients` | `g_main.c::SendScoreboardMessageToAllClients` | Loops connected clients through the scoreboard sender exactly like the source wrapper, then falls through into the shared retail award-configstring refresh at `0x100559E0`. | High |
| `0x10055EB0` | `SortRanks` | `g_main.c::SortRanks` | The qsort comparator keeps scoreboard/follow spectators last and otherwise sorts active clients by session/score state exactly like the source rank-ordering helper. | High |
| `0x10056070` | `CalculateRanks` | `g_main.c::CalculateRanks` | Rebuilds connected/non-spectator counts, sorts `level.sortedClients`, assigns rank/tie state, updates score and leader configstrings, resends scoreboards during intermission, and then tails into the shared retail award-configstring refresh. | High |
| `0x10056B30` | `MoveClientToIntermission` | `g_main.c::MoveClientToIntermission` | Moves a client to the intermission origin and angles, switches to `PM_INTERMISSION`, and clears powerups plus transient entity/playerstate flags. | High |
| `0x10056CB0` | `BeginIntermission` | `g_main.c::BeginIntermission` | Intermission bootstrap that latches intermission time, runs tournament score adjustment, walks `MoveClientToIntermission`, and then extends the stock GPL flow with vote clearing and `nextmaps` setup. | High |
| `0x10057000` | `ExitLevel` | `g_main.c::ExitLevel` | Match-end exit path that triggers autoactions, removes the duel loser on tournament restarts, resolves the `nextmaps` or `map_restart` path, writes session data, and pushes connected clients back to `CON_CONNECTING`. | High |
| `0x100573F0` | `G_LogPrintf` | `g_main.c::G_LogPrintf` | Timestamped logfile writer used by init/shutdown, connect/disconnect, and other game log traffic. | High |
| `0x10057510` | `LogExit` | `g_main.c::LogExit` | Anchored by `Exit: %s`, `red:%i  blue:%i`, and the per-client `score:` log line while queueing intermission and single-player win/loss follow-ons. | High |
| `0x10057AD0` | `CheckIntermissionExit` | `g_main.c::CheckIntermissionExit` | Tailcalled from `CheckExitRules` during intermission; the body rebuilds the client ready bitmask, honors the `nextmaps`-extended wait, and exits through `ExitLevel` after the grace window. | High |
| `0x10057C60` | `ScoreIsTied` | `g_main.c::ScoreIsTied` | The body compares either the current duel leaders or the red/blue team scores by gametype and is queried directly from `CheckExitRules` before sudden-death exit handling. | High |
| `0x10057CD0` | `G_CanForfeit` | Retail-only shared helper spanning `g_cmds.c::Cmd_Forfeit_f` and `g_main.c::CheckExitRules` | Anchored by the forfeit rejection strings and used from both the client forfeit command and the automatic missing-player forfeit checks. | High |
| `0x10057F10` | `G_ApplyForfeit` | `g_main.c::G_ApplyForfeit` analogue | Forces the losing side into the forfeited score state, sets the forfeiture latch, prints `Game has been forfeited.`, and logs `Players have forfeited.` | High |
| `0x10058030` | `CheckExitRules` | `g_main.c::CheckExitRules` | Anchored by `Timelimit hit.`, `Fraglimit hit.`, and `Capturelimit hit.` strings. | High |
| `0x10058410` | `G_SyncTournamentQueueTeamTasks` | Retail-only duel queue helper | Watches for dirty queue-position updates, mirrors the one-based `pq` slot back into each waiting spectator's `teamtask` userinfo key, and republishes the affected clients through `ClientUserinfoChanged`. | High |
| `0x10058580` | `G_CheckReadyUpDelayAction` | Retail-only duel warmup helper | Arms `CS_READYUP_STATUS` from `g_warmupReadyDelay`, then applies `g_warmupReadyDelayAction` by forcing players ready or moving unready players to spectate-only when the deadline expires. | High |
| `0x100586E0` | `CheckTournament` | `g_main.c::CheckTournament` | Warmup/game-state transition logic plus the `Warmup:` log line. | High |
| `0x100588F0` | `G_UpdateVoteCounts` | Retail-only vote helper | Walks per-client vote states, updates the public yes/no vote configstrings, and short-circuits explicit player pass/veto outcomes via `%s passed the vote.` and `%s vetoed the vote.` | High |
| `0x10058AB0` | `G_TryExecuteVoteString` | Retail-only vote helper | Parses and executes Quake Live-specific vote strings such as `cointoss`, `random`, `loadouts`, `timers`, `shuffle`, `teamsize`, and `weaprespawn`, then reports whether the string was consumed. | High |
| `0x10059130` | `G_ClearVoteState` | Retail-only vote helper | Clears vote configstrings and each client's vote-status field; this helper is called from both `CheckVote` and the intermission bootstrap. | High |
| `0x100591B0` | `CheckVote` | `g_main.c::CheckVote` | Handles delayed vote execution plus the `Vote passed.`, `Vote failed.`, and Quake Live-specific `Voting time has expired.` outcomes before clearing vote state. | High |
| `0x100592C0` | `CheckCvars` | `g_main.c::CheckCvars` | Watches `g_password` changes, recomputes `g_needpass`, and republishes the paired server configstrings exactly like the source cvar watcher. | High |
| `0x10059370` | `G_RunThink` | `g_main.c::G_RunThink` | Preserves the classic `nextthink` / `ent->think` gate and `NULL ent->think` error while also servicing a neighboring retail callback slot ahead of the think dispatch. | High |
| `0x100593E0` | `G_UpdateTeamCountConfigstrings` | Retail-only HUD/configstring helper | Periodically refreshes the auxiliary team-count configstrings at `0x297` and `0x298`, using raw team rosters in ordinary team states and the active-player counter during round-controller states. | High |
| `0x100594D0` | `G_RunFrame` | `g_main.c::G_RunFrame` | Main frame loop advancing time, stepping entities, and running exit/team/vote helpers. | High |
| `0x10061800` | `Cmd_AllReady_f` | `g_cmds.c::Cmd_AllReady_f` | HLIL-visible admin helper for the `allready` command table entry; it validates access, enforces the duel two-player restriction, and sets every connected client's retail ready latch. | High |
| `0x10064280` | `G_RRResolveRoundState` | Retail-only Red Rover controller helper | Freeze-style pending-transition resolver that advances deferred `RR_RoundStateTransition` work and returns the current Red Rover round state. | High |
| `0x10064380` | `G_RRFinalizeSpawnLoadout` | Retail-only Red Rover spawn helper | Reached from `ClientSpawn` before the generic loadout finalizer; survivors fall through to `G_FinalizeSpawnLoadout`, while infected clients are forced onto the zombie role loadout by seeding the reduced weapon mask, selected weapon, and health/maxHealth directly. | High |
| `0x100643E0` | `G_RRHandleDamageScore` | Retail-only Red Rover infection damage helper / `g_client.c::G_RRHandleDamageScore` analogue | Called from the main damage path after armor resolution; it applies the shared self/team damage suppression policy, clamps survivor-vs-infected damage during the active infection state, accumulates threshold credit on the attacker, and pays out score increments through `CalculateRanks`. | High |
| `0x100645A0` | `G_RRResetClientForRound` | Retail-only Red Rover per-client round helper | Reused from both `ClientBegin` and the delayed respawn path; it reruns `ClientSpawn`, reapplies the Red Rover role-aware spawn finalizer, and pushes the client into the holding state while the round controller is still in its pre-release phase. | High |
| `0x100645E0` | `G_RRInitClient` | `g_client.c::G_RRInitClient` analogue | Spawn/bootstrap helper that seeds the infection-role flags from `sess.sessionTeam`, clears them for survivors when the RR toggles are disabled, and forces the holding-state bit while warmup or the pre-active controller state is still in effect. | High |
| `0x10064670` | `G_RRCheckRoundCompletion` | Retail-only Red Rover completion helper / `g_client.c::G_RRCheckRoundCompletion` analogue | Evaluates connected-team counts, applies the draw-delay gate, and latches the last infected client when infection mode leaves exactly one zombie standing. | High |
| `0x10064710` | `G_RRCheckExitRules` | Retail-only Red Rover exit helper | Suppresses exit while `ScoreIsTied()` is true, otherwise checks timelimit/roundlimit and optionally prints/logs the corresponding match-end messages. | High |
| `0x100647C0` | `G_RRResolveAutoJoinTeam` | Retail-only Red Rover infection helper | Reached from the autojoin path in `SetTeam` when infection mode is active; it resolves any pending controller transition and returns `TEAM_RED` for the preserved or newly selected infected slots and `TEAM_BLUE` for every other client. | High |
| `0x10064820` | `G_RRSeedInfectionTeams` | Retail-only Red Rover infection helper | Reached from the infection branch of `G_RRTrackRoundActivity`; it moves everyone back to `TEAM_BLUE`, restores the latched infected client when one exists, otherwise selects a random connected client from `level.sortedClients`, stores that slot, and returns the chosen infected client number. | High |
| `0x100649F0` | `RR_RoundStateTransition` | Retail-only Red Rover round-state controller | Anchored by `RR_RoundStateTransition: invalid state`; it resolves pending transition timers, updates the match-state configstrings, resets active participants, and drives the Red Rover active, complete, and restart phases. | High |
| `0x100652B0` | `G_RRApplySurvivalBonus` | Retail-only Red Rover infection helper | Anchored by `Survival Bonus! +%i`; when the infection ruleset is active it checks the survival-bonus timer, awards the configured score delta to the connected team-2 participants, emits the matching temp-entity event, and refreshes ranks. | High |
| `0x10065410` | `G_RRCheckInfectionSpread` | Retail-only Red Rover infection helper | Anchored by `Infection spreads in %i second%s!`; it announces the next spread window and, when the timer expires, converts the next eligible connected participant through the deeper team/state mutation helper before rearming the timer. | High |
| `0x100655A0` | `G_RRTrackRoundActivity` | `g_client.c::G_RRTrackRoundActivity` | Source-faithful outer Red Rover per-frame activity monitor; it refreshes the controller state, applies the survival-bonus and infection-spread helpers, evaluates round completion, and advances the controller when the round ends. | High |
| `0x10065680` | `G_RRInitRoundController` | Retail-only Red Rover init helper | Reached from `G_InitGame`; it clears the infection-selection trackers, seeds the first pending controller state, and primes the Red Rover state machine for either normal or infection-enabled starts. | High |
| `0x10065700` | `G_RRHandlePlayerDeath` | `g_client.c::G_RRHandlePlayerDeath` analogue | Retail death-path helper that flips the victim between Red Rover teams, refreshes userinfo, emits the infection temp-entity when applicable, updates infection timers/bonus state, and reevaluates round completion. | High |
| `0x10065F30` | `G_SpawnClassExemptFromSpawnFilter` | Retail-only `g_spawn.c` helper (no direct GPL analogue) | Anchored by `item_armor_shard`, `team_redobelisk`, and `team_blueobelisk`, then used inside `G_SpawnGEntityFromSpawnVars` to bypass the normal `notfree` / `notteam` / `gametype` / `not_gametype` rejection path for specific classes. | High |
| `0x10066230` | `G_ParseSpawnVars` | `g_spawn.c::G_ParseSpawnVars` | Parse/error strings match the brace-bounded entity parser. Retail inlines `G_AddSpawnVarToken` here. | High |
| `0x10066440` | `SP_worldspawn` | `g_spawn.c::SP_worldspawn` | `SP_worldspawn: The first entity isn't 'worldspawn'` string, world metadata parsing, and warmup/configstring setup. | High |
| `0x10066B90` | `ConsoleCommand` | `g_svcmds.c::ConsoleCommand` | HLIL-only boundary dispatching `entitylist`, `forceteam`, `game_memory`, `addbot`, `botlist`, `game_crash`, `forceshuffle`, `dumpvars`, and `reload_access` before the remaining hidden debug/admin fallthrough. | High |
| `0x10067EC0` | `G_ClientsOnSameTeam` | Retail-only native export helper wrapping `g_team.c::OnSameTeam` | Compares two `gclient_t` session teams directly and keeps the retail spectator-equality allowance that survives below `GT_TEAM`. | High |
| `0x10067F00` | `G_ClientNumsOnSameTeam` | Retail-only native export helper wrapping `g_team.c::OnSameTeam` | Validates two client numbers against `level.clients` and then tails into `G_ClientsOnSameTeam`. | High |
| `0x10067F30` | `OnSameTeam` | `g_team.c::OnSameTeam` | Entity-level same-team predicate used across combat, chat, and objective logic; retail keeps the classic client/sessionTeam comparison but treats matching spectators as same-team even outside team gametypes. | High |
| `0x10067F70` | `G_IsClientSpectator` | Retail-only native export helper | Validates the client slot and returns whether `sess.sessionTeam == TEAM_SPECTATOR`. | High |
| `0x100680C0` | `TeamCount` | `g_client.c::TeamCount` | HLIL preserves the classic ignore-client, connected-state, and `sess.sessionTeam` loop even though the committed decomp still drops one register-passed argument. | High |
| `0x10068100` | `Team_CountsBalanced` | Retail-only `g_teamForceBalance` helper | Extracted boolean helper that returns true when the current red/blue spread is at most one player; retail reuses it from both `SetTeam` and `Cmd_ReadyUp_f` before their stricter join/ready gates. | High |
| `0x10068140` | `Team_HasMinimumPlayersForWarmup` | `g_team.c::Team_HasMinimumPlayersForWarmup` | Warmup gate that checks the duel/team minimum-player requirements and the stronger both-teams-present rule used by the retail ready-up flow. | High |
| `0x10068490` | `TeamplayInfoMessage` | `g_team.c::TeamplayInfoMessage` | Uses the `tinfo %i %s` payload while building team overlay info for clients. | High |
| `0x1006AAF0` | `SpawnObelisk` | `g_team.c::SpawnObelisk` | `SpawnObelisk: %s startsolid at %s` diagnostic and the matching overload spawn flow. | High |
| `0x1006B110` | `G_TotalLivingHealthByTeam` | Retail-only Freeze tally helper | Sums entity health for the connected `PM_NORMAL` clients grouped by `sess.sessionTeam`, feeding the freeze round-end health summary and tiebreak path. | High |
| `0x1006B170` | `G_CountActivePlayersByTeam` | Retail-only shared team counter | Counts connected clients whose `ps.pm_type == PM_NORMAL`, grouped by `sess.sessionTeam`; retail reuses it for Freeze, Red Rover, teamsize validation, and the auxiliary team-count configstrings. | High |
| `0x1006B1C0` | `G_CountConnectedClientsByTeam` | Retail-only shared roster counter | Counts all connected clients by `sess.sessionTeam` without the `PM_NORMAL` filter used by `G_CountActivePlayersByTeam`. | High |

## Supporting Helper Aliases Added In The Same Pass

- Active-client helpers: `P_DamageFeedback`, `P_WorldEffects`, `G_SetClientSound`, `ClientImpacts`, `G_TouchTriggers`, `SpectatorThink`, `ClientInactivityTimer`, `G_CheckClientFlood`, `G_RunFactoryHealthRegen`, `G_RunFactoryArmorRegen`, `ClientTimerActions`, `ClientEvents`, `StuckInOtherClient`, `SendPendingPredictableEvents`, `ClientThink_real`, `ClientSpawn`.
- Spawn/reset helpers: `G_CAADRespawnAsSpectator`, `G_CAADResetClientForRound`, `G_FinalizeSpawnLoadout`, `G_RRFinalizeSpawnLoadout`, `G_RRResetClientForRound`.
- Item lifecycle helpers: `RespawnItem`, `Touch_Item`, `Use_Item`, `G_CheckTeamItems`, `FinishSpawningItem`, `G_SpawnItem`.
- Attack and Defend controller helpers: `G_ADResolveRoundState`, `G_ADResolveAttackingTeam`, `G_ADResolveDefendingTeam`, `G_ADHandleDamageScore`, `G_ADCheckExitRules`, `AD_RoundStateTransition`, `G_ADResetScoreHistory`, `G_ADUpdateScoreHistory`.
- Freeze and round-controller helpers: `G_FreezeResolveRoundState`, `G_FreezeSetClientFrozenState`, `G_FreezeResetClientForRound`, `G_FreezeTeamIsFullyFrozen`, `G_FreezeEvaluateRoundWinner`, `Freeze_RoundStateTransition`, `G_FreezeRunFrame`, `G_FreezeClientEndFrame`, `RR_RoundStateTransition`, `G_UpdateTeamCountConfigstrings`, `G_TotalLivingHealthByTeam`, `G_CountActivePlayersByTeam`, `G_CountConnectedClientsByTeam`.
- Red Rover controller helpers: `G_RRResolveRoundState`, `G_RRHandleDamageScore`, `G_RRInitClient`, `G_RRCheckRoundCompletion`, `G_RRCheckExitRules`, `G_RRResolveAutoJoinTeam`, `G_RRSeedInfectionTeams`, `G_RRApplySurvivalBonus`, `G_RRCheckInfectionSpread`, `G_RRTrackRoundActivity`, `G_RRInitRoundController`, `G_RRHandlePlayerDeath`.
- Ready/warmup helpers: `Cmd_ReadyUp_f`, `Cmd_AllReady_f`, `G_CheckReadyUpDelayAction`, `Team_HasMinimumPlayersForWarmup`.
- Command/tournament queue helpers: `Cmd_TeamTask_f`, `SetTeam`, `G_UpdateTournamentQueuePositions`, `G_SyncTournamentQueueTeamTasks`.
- Scoreboard helpers: `DeathmatchScoreboardMessage`, `G_BuildCompactScoreboardMessage`, `G_BuildObeliskScoreboardMessage`, `G_BuildFFAScoreboardMessage`, `G_BuildDuelScoreboardMessage`, `G_BuildRaceScoreboardMessage`, `G_BuildTeamScoreboardMessage`, `G_SendTDMStatsMessage`, `G_BuildClanArenaScoreboardMessage`, `G_SendCAStatsMessage`, `G_BuildCTFStyleScoreboardMessage`, `G_SendCTFStatsMessage`, `G_BuildFreezeScoreboardMessage`, `G_BuildRedRoverScoreboardMessage`.
- Session helpers: `G_WriteClientSessionData`, `G_ReadSessionData`, `G_InitSessionData`, `G_WriteSessionData`.
- Intermission/rank helpers: `FindIntermissionPoint`, `G_CountSpawnPoints`, `G_FindNextTournamentPlayer`, `AddTournamentPlayer`, `RemoveTournamentLoser`, `AdjustTournamentScores`, `G_UpdateAwardConfigstrings`, `SendScoreboardMessageToAllClients`, `SortRanks`, `CalculateRanks`, `MoveClientToIntermission`, `BeginIntermission`, `ExitLevel`.
- Spawn helpers: `G_SpawnString`, `G_NewString`, `G_ParseField`, `G_CallSpawn`, `G_SpawnGEntityFromSpawnVars`.
- Server console helpers: `ClientForString`, `Svcmd_ForceTeam_f`.
- Team helpers: `G_ClientsOnSameTeam`, `G_ClientNumsOnSameTeam`, `OnSameTeam`, `G_IsClientSpectator`, `TeamCount`, `Team_CountsBalanced`, `Team_HasMinimumPlayersForWarmup`, `CheckTeamStatus`, `Team_ReturnFlagSound`, `Team_TakeFlagSound`, `Team_CaptureFlagSound`.
- Retail-only vote/forfeit helpers: `G_CanForfeit`, `G_ApplyForfeit`, `G_UpdateVoteCounts`, `G_TryExecuteVoteString`, `G_ClearVoteState`.
- Native export-tail helpers: `G_AreEnemyClients`, `G_IsObjectiveEntity`, `G_FreezeCanSeeThawProgressEvent`, `G_IsClientAdmin`, `G_GetClientScore`.
- Core wrappers: `G_Printf`, `G_Error`.

## Important Disagreements And Split Paths

- `dllEntry` writes `0xA` through its third out-parameter. In the native Quake Live loader contract this is an API-version handoff, not a reliable export-count field; the returned qagame export table continues past the 10 `VM_CallNativeExports` slots used by the current engine call switch.
- `ClientThink` at `0x10035410` is visible in HLIL and in the native export table, but the committed `functions.csv` still does not emit that function start.
- `G_CheckClientFlood` at `0x100341E0` is a descriptive retail-only split from the broader `ClientThink_real` path. It shares the same `floodCount` / `floodLastTime` state used by the current source tree, but unlike `g_cmds.c::G_FloodLimited` it drops over-limit clients directly from the active-client path instead of only rate-limiting commands.
- `ClientThink_real` is a clean retail boundary at `0x10034C90`, and the surrounding `ClientEvents` (`0x10034860`) plus `StuckInOtherClient` (`0x10034B50`) splits are now settled.
- `G_RunFactoryHealthRegen` at `0x10034260` and `G_RunFactoryArmorRegen` at `0x100342F0` are descriptive retail-only helpers factored out of the current source tree's broader `G_RunFactoryRegen`. Retail keeps separate per-frame health and armor regen timers keyed off the last-damage timestamp and the client-side accumulator/latch fields, while the reconstructed GPL-derived tree currently models the same policy in one helper.
- `ClientSpawn` at `0x1003BC30` is source-faithful on its outer boundary, but retail factors the post-spawn loadout/finalization work into the deeper helper at `0x1003B5A0` instead of keeping the whole spawn bootstrap inside one GPL-shaped function.
- `DeathmatchScoreboardMessage` at `0x1003CBF0` is still source-faithful on its public role, but the retail build factors almost all payload formatting into a helper family: compact fallback, duel, Race, TDM, Clan Arena, shared CTF-style, Freeze, Red Rover, and Overload serializers, plus the intermission-only `tdmstats` / `castats` / `ctfstats` publishers. The duel serializer also caches the lower/higher live duel client numbers in `level + 0x1C08/+0x1C0C` instead of keeping that ordering entirely local.
- `G_CAADRespawnAsSpectator` at `0x10035960` and `G_CAADResetClientForRound` at `0x10038160` are descriptive retail-only shared Clan Arena / Attack and Defend helpers. Retail keeps the per-client round reset and dead-player spectator-follow fallback in standalone helpers that the GPL-derived tree does not preserve with these exact boundaries.
- `G_FinalizeSpawnLoadout` at `0x1003B5A0` is a descriptive retail-only recovery name. The current GPL-derived tree spreads the same selected-weapon, grant-script, and starting-ammo/item work across `ClientSpawn`, `G_GrantConfiguredItems`, and adjacent spawn helpers instead of preserving a standalone post-spawn finalizer.
- Retail keeps the item lifecycle split cleanly across `G_SpawnItem -> FinishSpawningItem -> Touch_Item` with the optional `Use_Item -> RespawnItem` trampoline, while `G_CheckTeamItems` remains a separate objective-validator pass. The current GPL-derived tree preserves the same core behavior, but some map bootstrap and spawn-side item setup is easier to read inline than in this retail helper chain.
- `G_ADResolveRoundState`, `G_ADResolveAttackingTeam`, `G_ADResolveDefendingTeam`, `G_ADHandleDamageScore`, `G_ADCheckExitRules`, `G_ADResetScoreHistory`, and `G_ADUpdateScoreHistory` are descriptive retail-only helper names. The current GPL-derived tree keeps Attack and Defend round-state reads, side selection, damage-credit thresholds, and `scores_ad` publishing distributed across broader mode logic rather than exposing these exact standalone boundaries.
- `AD_RoundStateTransition` at `0x10035B70` is a retail-only controller name recovered directly from the preserved invalid-state diagnostic. The current GPL-derived tree does not preserve an exact standalone Attack and Defend controller with this boundary or the adjacent side-resolver and score-history publisher split.
- `G_InitWorldSession` is inlined into retail `G_InitGame`. The `session` cvar read and the `Gametype changed, clearing session data.` print occur inside `G_InitGame`, not a separate helper boundary.
- The outer `G_SpawnEntitiesFromString` loop is likewise inlined into `G_InitGame`: retail parses the first entity, runs `SP_worldspawn`, then loops `G_SpawnGEntityFromSpawnVars` until `G_ParseSpawnVars` returns false.
- `G_CountSpawnPoints` at `0x10055000` is a descriptive recovery name. The source tree keeps the spawn counter reset and entity scan inside the broader `G_InitGame` setup instead of exposing a standalone helper.
- `G_FindNextTournamentPlayer` at `0x10055710` is also descriptive: the current source keeps the queue-selection logic inline inside `AddTournamentPlayer`, but retail split it into a stable callable helper.
- `G_UpdateAwardConfigstrings` at `0x100559E0` is a descriptive retail-only recovery name. The helper publishes winning client numbers into a legacy award configstring block (`0x2B4`, `0x2B5`, `0x2B8-0x2BB`) that the current source tree no longer preserves as standalone server-side state.
- `SendScoreboardMessageToAllClients` at `0x10055E50` is source-faithful on its outer boundary, but retail makes it slightly fatter by tailcalling `G_UpdateAwardConfigstrings` instead of returning immediately after the scoreboard loop.
- `CalculateRanks` at `0x10056070` is a clean outer boundary, but the retail body appends the same shared `G_UpdateAwardConfigstrings` tail path after the main rank and score-configstring work.
- `G_AddSpawnVarToken` is inlined into `G_ParseSpawnVars`; the error string survives, but the helper body does not exist as a stable standalone function in the current retail build.
- Retail `G_SpawnGEntityFromSpawnVars` also adds a classname-based exemption helper plus a `not_gametype` path around the source-equivalent gametype filters. That logic does not survive as a direct GPL helper name, so `G_SpawnClassExemptFromSpawnFilter` is a descriptive recovery name for the observed retail behavior.
- `ConsoleCommand` at `0x10066B90` is visible in HLIL and in the native export table, but the committed `functions.csv` does not currently list that function start.
- `ClientCommand` at `0x10045DD0` is in the same situation: it is visible in HLIL and the native export table, but not currently emitted as a function start in the committed `functions.csv`.
- `Use_Item` at `0x1004FD20` is also HLIL-visible as a stable standalone thunk, but the committed `functions.csv` does not currently emit that function start.
- `Cmd_AllReady_f` at `0x10061800` is likewise HLIL-visible via the `allready` command table entry, but the committed `functions.csv` does not currently emit that function start.
- `G_FreezeEvaluateRoundWinner` at `0x1004BF60` is a descriptive retail-only helper name. The current source keeps the same winner-selection role inside a simpler `team_t` helper backed by cached level tallies, while retail passes explicit count/health arrays and stores the resolved winner in `data_105df598`.
- `G_FreezeResolveRoundState` at `0x1004BC30` and `G_RRResolveRoundState` at `0x10064280` are descriptive retail-only controller read helpers. The current GPL-derived tree reads `level.roundState` and its timers directly instead of routing callers through standalone pending-transition resolvers.
- `G_FreezeSetClientFrozenState` at `0x1004BC80` is a descriptive retail-only shared helper name. Retail folds the current source tree's separate `G_FreezeApplyFreezeState` and `G_FreezeThawClient` responsibilities into one callable state mutator.
- `G_FreezeResetClientForRound` at `0x1004BDE0` is likewise descriptive. Retail factors a per-client reset helper out of the broader GPL-style `G_FreezeResetClientsForRound` loop and reuses it from both bootstrap and delayed active-client reset paths.
- `G_FreezeTeamIsFullyFrozen` at `0x1004BF10` is a descriptive retail-only helper name. The committed decomp still hides the register-passed team argument, but HLIL shows the connected-client scan that `G_FreezeEvaluateRoundWinner` uses to detect when one side has no unfrozen members left.
- `G_FreezeRunFrame` at `0x1004CB80` is source-faithful on its outer boundary, but retail delegates the detailed round-state transition and winner-selection work to neighboring helpers instead of keeping the whole flow inside one GPL-shaped function.
- `G_FreezeClientEndFrame` at `0x1004CD40` is source-faithful on its outer boundary, but retail delegates the actual freeze/thaw mutation into the shared helper at `0x1004BC80` instead of keeping the whole flow inside one GPL-shaped function.
- `G_CanClientSeeClient` at `0x10052DC0` is a descriptive retail-only native export helper. The current GPL tree does not expose a standalone client-visibility predicate for the snapshot builder, while retail uses this slot from `SV_AddEntitiesVisibleFromPoint` to force-include spectator, teammate, and Red Rover infection client entities outside the ordinary PVS-only path.
- `G_AreEnemyClients` at `0x10052E40` is a descriptive retail-only native export helper. The current source tree does not expose a standalone client-number predicate for "distinct non-spectator opponents", so the recovered name reflects the exact HLIL gate rather than a GPL symbol.
- `G_ShouldSuppressVoiceToClient` at `0x10052E90` is a descriptive retail-only native export helper. The host calls it from the Steam voice relay loop and forwards the packet only when this predicate returns false, so the recovered name follows the real suppression semantics instead of pretending the GPL chat/voice helpers expose an equivalent standalone filter.
- `G_IsObjectiveEntity` at `0x10052F40` is likewise descriptive. Retail centralizes gametype-specific objective detection for flag items, obelisks, and extended Quake Live objective items in this export-tail helper instead of leaving that policy scattered through UI- or engine-facing call sites.
- `G_FreezeCanSeeThawProgressEvent` at `0x10053020` is a descriptive retail-only helper name. The stock GPL tree does not expose a standalone Freeze event-visibility predicate; retail split out the thaw-progress temp-entity filter keyed by event `0x58` and the linked teammate entity.
- The current source bridge still surfaces thaw-complete visuals through `EV_PLAYER_TELEPORT_IN` plus `QL_EVENTPARM_FREEZE_THAW` rather than the raw retail thaw event ordinal. That compatibility marker exists only because the shared GPL event enum has not yet been realigned to the retail `0x57` / `0x58` Freeze temp-entity band recovered from qagame/cgame.
- `G_RunFrame` at `0x100594D0` does not appear to call a standalone `G_RunClient` helper in the current retail build. The entity loop walks client slots inline and dispatches `ClientThink_real` directly, so the classic thin wrapper appears to be inlined or absent.
- `OnSameTeam` at `0x10067F30` is source-faithful on its outer boundary, but retail broadens the non-team-gametype case: matching spectators are treated as same-team instead of immediately returning false whenever `g_gametype < GT_TEAM`.
- `G_GetClientScore` at `0x100530F0` is a synthetic recovery name for a stable retail helper boundary. The body is just a validated getter for `gclient->ps.persistant[PERS_SCORE]`, and the GPL-derived tree does not preserve it as a standalone named function.
- The native export table tail beyond the public `GAME_*` slots now appears fully settled. `G_CanClientSeeClient`, `G_AreEnemyClients`, `G_ShouldSuppressVoiceToClient`, `G_IsObjectiveEntity`, `G_FreezeCanSeeThawProgressEvent`, `G_GetClientScore`, `G_IsClientAdmin`, `G_ClientsOnSameTeam`, `G_ClientNumsOnSameTeam`, `OnSameTeam`, and `G_IsClientSpectator` all have stable HLIL bodies plus host-side consumers.
- `Freeze_RoundStateTransition` at `0x1004C1B0` and `RR_RoundStateTransition` at `0x100649F0` are retail-only controller names recovered directly from preserved invalid-state diagnostics. The current GPL-derived tree spreads the equivalent behavior across `G_Frame_UpdateRoundController`, `G_FreezeResetClientsForRound`, `G_FreezeHandleRoundEnd`, and the Red Rover round helpers instead of preserving these exact standalone boundaries.
- `SetTeam` at `0x100406D0` is source-faithful on its outer boundary, but retail splits the actual session/team mutation and respawn execution into the deeper helper at `0x10040440` instead of keeping the entire flow inside one GPL-shaped function.
- `TeamCount` at `0x100680C0` is source-faithful on its outer boundary, but the committed decomp still drops the register-passed `ignoreClientNum` argument even though HLIL preserves the comparison against the skipped client slot.
- `Team_CountsBalanced` at `0x10068100` is a descriptive retail-only helper name. The underlying logic is the extracted `g_teamForceBalance` spread check, which the GPL-derived tree keeps inline inside `SetTeam` instead of exposing as a stable callable boundary.
- `G_UpdateTeamCountConfigstrings` at `0x100593E0` is a descriptive retail-only helper name. The current GPL-derived tree does not preserve standalone configstring slots at `0x297` and `0x298`, so the best evidence-backed recovery is the observed periodic per-team count publisher rather than a stock source symbol.
- `G_CountActivePlayersByTeam`, `G_TotalLivingHealthByTeam`, and `G_CountConnectedClientsByTeam` are descriptive retail-only helper names. The current GPL-derived tree keeps the same counting logic inside larger Freeze, Red Rover, and match-state routines instead of preserving these standalone helpers.
- `G_RRCheckRoundCompletion` at `0x10064670` is a descriptive retail-only helper name. Retail passes explicit connected-team counts and preserves a separate last-infected latch for infection mode, while the current GPL-derived tree keeps simpler winner logic inline in `G_RRTrackRoundActivity`.
- `G_RRCheckExitRules` at `0x10064710` is a descriptive retail-only helper name. The stock tree keeps Red Rover's time/round limit handling inside broader round-flow code, while retail split the tie-aware RR timelimit and roundlimit gate into a standalone check.
- `G_RRHandleDamageScore` at `0x100643E0` is a descriptive retail-only helper name. The current GPL-derived tree keeps Red Rover's survivor scoring logic in `g_client.c::G_RRHandleDamageScore`, but retail folds the friendly-fire policy, infection-only damage clamping, and threshold score payout into one deeper damage-path helper.
- `G_RRFinalizeSpawnLoadout` at `0x10064380` and `G_RRResetClientForRound` at `0x100645A0` are descriptive retail-only Red Rover spawn helpers. Retail layers an infection-role loadout override and a separate per-client round reset wrapper around `ClientSpawn`, while the GPL-derived tree keeps the corresponding RR spawn/bootstrap work distributed across `ClientSpawn`, `G_RRInitClient`, and adjacent mode helpers.
- `G_RRInitClient` at `0x100645E0` is source-faithful on role but not on exact state shape. The current GPL-derived tree stores richer `rrInfectionState` and timer fields, while the retail helper mostly seeds the infection-role flag bits and the temporary holding-state latch during spawn/bootstrap.
- `G_RRResolveAutoJoinTeam` at `0x100647C0` and `G_RRSeedInfectionTeams` at `0x10064820` are descriptive retail-only infection helpers. The current GPL-derived tree does not preserve these standalone team-seeding boundaries or the latched infected-slot handoff through `SetTeam`; retail keeps both the autojoin resolver and the round-start infected reseed as explicit callable helpers.
- `G_RRApplySurvivalBonus` at `0x100652B0` and `G_RRCheckInfectionSpread` at `0x10065410` are descriptive retail-only Red Rover infection helper names. The current GPL-derived tree does not preserve these standalone timer-driven helpers or their exact score/countdown flow.
- `G_RRTrackRoundActivity` at `0x100655A0` is source-faithful on its outer boundary, but retail folds the round-completion, infection-spread, and controller-transition work into a denser helper chain than the current GPL-derived implementation.
- `G_RRInitRoundController` at `0x10065680` is a descriptive retail-only init helper. The current GPL-derived code seeds Red Rover round and infection state inline during setup instead of preserving a dedicated controller bootstrap boundary.
- `G_RRHandlePlayerDeath` at `0x10065700` is source-faithful on role but not on exact interface. Retail receives the victim's pre-mutation team and means-of-death from the death path, then performs the team swap or infection mutation inside this deeper helper instead of keeping the whole flow inline.
- `Cmd_ReadyUp_f` and `Cmd_AllReady_f` are source-faithful outer command boundaries, but retail toggles and serializes a dedicated Quake Live ready-state field at `client + 0x2E8` rather than relying only on the current source tree's `EF_READY` bit.
- `AddTournamentPlayer` and `RemoveTournamentLoser` are source-faithful queue boundaries, but the surrounding retail tournament flow is still split more aggressively than GPL, including the descriptive selector/helper layer around them and the retail-only award publisher at `0x100559E0`.
- `G_UpdateTournamentQueuePositions` and `G_SyncTournamentQueueTeamTasks` are descriptive retail-only queue helpers. Retail serializes extra duel queue fields (`so` / `pq`) through `ClientUserinfoChanged` and then mirrors queue order back through `teamtask` for HUD/UI compatibility; the GPL-derived tree does not preserve these helpers or fields.
- `G_CheckReadyUpDelayAction` at `0x10058580` is a descriptive retail-only helper. The current GPL-derived tree preserves `CS_READYUP_STATUS` publishing, ready commands, and warmup countdown logic, but not this standalone `g_warmupReadyDelay` / `g_warmupReadyDelayAction` controller that can force-ready players or push unready duel players into spectate-only state after a delay.
- `BeginIntermission` at `0x10056CB0` is broader than the stock GPL helper: in the retail build it also clears vote state through `G_ClearVoteState` and bundles extra `nextmaps` setup/configstring work after the core intermission transition.
- `ExitLevel` at `0x10057000` is likewise broader than the stock GPL helper: the retail build resolves `nextmaps`, falls back to `map_restart 0` when needed, clears extra match-award/intermission state, and still preserves the stock tournament-loser restart path.
- `Cmd_Forfeit_f` at `0x100456B0` is only a thin client-facing gate. Retail keeps the deeper eligibility checks and final forfeit state mutation in the separate helper pair `G_CanForfeit` / `G_ApplyForfeit`, so the current source's `Cmd_Forfeit_f` / `G_HandleForfeit` structure is only an approximate analogue.
- `G_CanForfeit`, `G_UpdateVoteCounts`, `G_TryExecuteVoteString`, and `G_ClearVoteState` are descriptive recovery names for stable retail-only helper boundaries. The current GPL-derived tree does not preserve these exact helpers as separate named functions.
- `CheckVote` at `0x100591B0` is a clean outer boundary, but retail keeps the tally, special-vote execution, and vote-state clearing work split into the adjacent helper trio rather than inlining it all into one GPL-shaped body.
- `G_RunThink` at `0x10059370` is slightly fatter than the stock GPL helper because it services an additional callback slot at `ent + 0x2FC` before the usual `nextthink` / `ent->think` dispatch.
- `Team_HasMinimumPlayersForWarmup` at `0x10068140` is source-faithful on its outer boundary. Retail feeds it through the same `TeamCount` primitive used by `SetTeam`, but the committed decomp still obscures the low-level register-passed ignore-client argument on that helper.

## Open Questions

- No high-confidence unresolved function seams remain in the current curated qagame control surface. The remaining reverse-engineering work is now mostly type/data recovery, especially the client-side regen accumulator/latch fields consumed by `G_RunFactoryHealthRegen` and `G_RunFactoryArmorRegen`.
