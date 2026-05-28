# UI Ownerdrawtype Parity Index

Last updated: 2026-05-28

This index tracks the Quake Live UI ownerdraw range defined in
`src/ui/menudef.h`: `UI_OWNERDRAW_BASE` plus ownerdraw IDs `513..558`.
It is intended as the working checklist for which menu ownerdraw indices still
need retail parity review.

Out of scope for this table: local legacy UI IDs defined in
`src/code/ui/ui_local.h` such as `UI_EFFECTS`, `UI_CLANNAME`,
`UI_CLANLOGO`, `UI_BLUETEAMNAME`, `UI_REDTEAM1`, and the other `600..620`
Team Arena carryovers. Those are not ownerdraw IDs in the committed
Quake Live `menudef.h` range and should be tracked separately if they remain
reachable through legacy menus.

Primary evidence anchors:

- Retail dispatcher: `UI_OwnerDraw @ 0x100097B0`.
- Retail key dispatcher: `UI_OwnerDrawHandleKey @ 0x1000A820`.
- Retail width helper: `UI_OwnerDrawWidth @ 0x10006950`.
- Promoted companion names: `references/reverse-engineering/ghidra/uix86/ui_ghidra_reference.h`.
- Canonical control flow: `references/hlil/quakelive/uix86.all/uix86.dll_hlil.txt`.

State legend:

- `Checked`: focused retail parity coverage exists in `tests/test_ui_menu_files.py`.
- `Partial`: some parity behavior is covered, but the ownerdraw still needs a full retail pass.
- `Needs check`: implemented or retail-routed, but not yet locked by a focused parity test.
- `Retail no-op/source legacy`: retail dispatcher falls through/defaults for this ID, while current source still has a legacy draw route.
- `No-op/missing`: no retail draw route and no current source draw route.
- `Sentinel`: numeric base marker, not a drawable ownerdraw.

| ID | Ownerdraw type | Retail dispatcher state | Current source wiring | Parity state | Next action |
| --- | --- | --- | --- | --- | --- |
| 512 | `UI_OWNERDRAW_BASE` | Sentinel base, not dispatched | None | Sentinel | None |
| 513 | `UI_HANDICAP` | `UI_DrawHandicap @ 0x10005100`; key `UI_Handicap_HandleKey @ 0x1000A040`; width helper participates | Draw, width, and key handler wired | Checked | Covered by `test_ui_retail_handicap_netsource_netfilter_ownerdraws_match_ql` |
| 514 | `UI_PLAYERMODEL` | `UI_DrawPlayerModel @ 0x10005690` | Draw wired; no key or width route | Checked | Covered by `test_ui_retail_player_opponent_ownerdraws_match_ql` |
| 515 | `UI_GAMETYPE` | `UI_DrawGameType @ 0x10005220`; key `UI_GameType_HandleKey @ 0x1000A110`; width helper participates | Draw, width, and key handler wired | Checked | Covered by `test_ui_retail_gametype_selector_ownerdraws_match_ql` |
| 516 | `UI_MAPPREVIEW` | `UI_DrawMapPreview @ 0x100053C0` with net-map path | Draw wired as `UI_DrawMapPreview(..., qtrue)` | Checked | Covered by `test_ui_retail_skill_mappreview_maptime_ownerdraws_match_ql` |
| 517 | `UI_SKILL` | `UI_DrawSkill @ 0x10005350`; key `UI_Skill_HandleKey @ 0x1000A390`; width helper participates | Draw, width, and key handler wired | Checked | Covered by `test_ui_retail_skill_mappreview_maptime_ownerdraws_match_ql` |
| 518 | `UI_NETSOURCE` | `UI_DrawNetSource @ 0x10006550`; key `UI_NetSource_HandleKey @ 0x1000A420`; width helper participates | Draw, width, and key handler wired | Checked | Covered by `test_ui_retail_handicap_netsource_netfilter_ownerdraws_match_ql` |
| 519 | `UI_NETMAPPREVIEW` | `UI_DrawNetMapPreview @ 0x100065B0` | Draw wired; no key or width route | Checked | Covered by `test_ui_retail_map_media_ownerdraws_match_ql` |
| 520 | `UI_NETFILTER` | `UI_DrawNetFilter @ 0x100066D0`; key `UI_NetFilter_HandleKey @ 0x1000A4F0`; width helper participates | Draw, width, and key handler wired | Checked | Covered by `test_ui_retail_handicap_netsource_netfilter_ownerdraws_match_ql` |
| 521 | `UI_TIER` | Retail dispatcher default/no-op for this ID | Legacy `UI_DrawTier` draw route exists; width case is empty | Retail no-op/source legacy | Confirm menu reachability, then decide whether to leave as harmless legacy or remove/gate for strict parity |
| 522 | `UI_OPPONENTMODEL` | `UI_DrawOpponent @ 0x10006730` | Draw wired; no key or width route | Checked | Covered by `test_ui_retail_player_opponent_ownerdraws_match_ql` |
| 523 | `UI_TIERMAP1` | Retail dispatcher default/no-op for this ID; `menudef.h` marks unused | Legacy `UI_DrawTierMap(..., 0)` draw route exists | Retail no-op/source legacy | Confirm unused status and document divergence decision |
| 524 | `UI_TIERMAP2` | Retail dispatcher default/no-op for this ID; `menudef.h` marks unused | Legacy `UI_DrawTierMap(..., 1)` draw route exists | Retail no-op/source legacy | Confirm unused status and document divergence decision |
| 525 | `UI_TIERMAP3` | Retail dispatcher default/no-op for this ID; `menudef.h` marks unused | Legacy `UI_DrawTierMap(..., 2)` draw route exists | Retail no-op/source legacy | Confirm unused status and document divergence decision |
| 526 | `UI_TIER_MAPNAME` | Retail dispatcher default/no-op for this ID; `menudef.h` marks unused | Legacy `UI_DrawTierMapName` draw route exists; width case is empty | Retail no-op/source legacy | Confirm unused status and document divergence decision |
| 527 | `UI_TIER_GAMETYPE` | Retail dispatcher default/no-op for this ID; `menudef.h` marks unused | Legacy `UI_DrawTierGameType` draw route exists; width case is empty | Retail no-op/source legacy | Confirm unused status and document divergence decision |
| 528 | `UI_ALLMAPS_SELECTION` | `UI_DrawAllMapsSelection @ 0x10006890` with all-maps/net path | Draw wired as `UI_DrawAllMapsSelection(..., qtrue)`; width case is empty | Checked | Covered by `test_ui_retail_map_selection_ownerdraws_match_ql` |
| 529 | `UI_OPPONENT_NAME` | `UI_DrawOpponentName @ 0x100068F0`; retail key dispatcher has no case for this ID | Draw wired; width case is empty; no key route | Checked | Covered by `test_ui_retail_player_opponent_ownerdraws_match_ql` |
| 530 | `UI_VOTE_KICK` | Retail dispatcher default/no-op for this ID | No draw, key, or width route | No-op/missing | Confirm no shipped menu depends on it as a UI ownerdraw; document as closed no-op if so |
| 531 | `UI_BOTNAME` | `UI_DrawBotName @ 0x10006B30`; key `UI_BotName_HandleKey @ 0x1000A570` | Draw and key handler wired | Checked | Covered by `test_ui_retail_botname_botskill_redblue_ownerdraws_match_ql` |
| 532 | `UI_BOTSKILL` | `UI_DrawBotSkill @ 0x10006BC0`; key `UI_BotSkill_HandleKey @ 0x1000A5D0` | Draw and key handler wired | Checked | Covered by `test_ui_retail_botname_botskill_redblue_ownerdraws_match_ql` |
| 533 | `UI_REDBLUE` | `UI_DrawRedBlue @ 0x10006C10`; key behavior is inline/fallthrough in retail key dispatcher | Draw and key handler wired | Checked | Covered by `test_ui_retail_botname_botskill_redblue_ownerdraws_match_ql` |
| 534 | `UI_CROSSHAIR` | `UI_DrawCrosshair @ 0x10006C60`; key `UI_Crosshair_HandleKey @ 0x1000A640` | Draw and key handler wired | Checked | Covered by `test_ui_retail_crosshair_nextmap_selectedplayer_ownerdraws_match_ql` |
| 535 | `UI_SELECTEDPLAYER` | `UI_DrawSelectedPlayer @ 0x10008E90`; key `UI_SelectedPlayer_HandleKey @ 0x1000A6C0` | Draw and key handler wired | Checked | Covered by `test_ui_retail_crosshair_nextmap_selectedplayer_ownerdraws_match_ql` |
| 536 | `UI_MAPCINEMATIC` | `UI_DrawMapCinematic @ 0x10005560` with current-map path | Draw wired as `UI_DrawMapCinematic(..., qfalse)`; `UI_StopCinematic` handles this ID | Checked | Covered by `test_ui_retail_map_media_ownerdraws_match_ql` |
| 537 | `UI_NETGAMETYPE` | `UI_DrawNetGameType @ 0x10005260`; key `UI_NetGameType_HandleKey @ 0x1000A210` | Draw and key handler wired | Checked | Covered by `test_ui_retail_gametype_selector_ownerdraws_match_ql` |
| 538 | `UI_NETMAPCINEMATIC` | `UI_DrawNetMapCinematic @ 0x10006600` | Draw wired; `UI_StopCinematic` handles this ID | Checked | Covered by `test_ui_retail_map_media_ownerdraws_match_ql` |
| 539 | `UI_SERVERREFRESHDATE` | `UI_DrawServerRefreshDate @ 0x10008F20`; width helper participates | Draw and width route wired | Checked | Covered by `test_ui_retail_server_info_ownerdraws_match_ql` |
| 540 | `UI_SERVERMOTD` | `UI_DrawServerMOTD @ 0x10009080` | Draw wired; no key or width route | Checked | Covered by `test_ui_retail_server_info_ownerdraws_match_ql` |
| 541 | `UI_GLINFO` | `UI_DrawGLInfo @ 0x100093B0` | Draw wired; no key or width route | Checked | Covered by `test_ui_retail_server_info_ownerdraws_match_ql` |
| 542 | `UI_KEYBINDSTATUS` | `UI_DrawKeyBindStatus @ 0x100092F0`; width helper participates | Draw and width route wired | Partial | Existing prompt/width coverage exists; add full normal/pending parity pass |
| 543 | `UI_CLANCINEMATIC` | Retail dispatcher default/no-op for this ID; `menudef.h` marks unused | Legacy `UI_DrawClanCinematic` route exists; `UI_StopCinematic` also handles this ID | Retail no-op/source legacy | Confirm unused status and document divergence decision |
| 544 | `UI_MAP_TIMETOBEAT` | `UI_DrawMapTimeToBeat @ 0x100054A0` | Draw wired; no key or width route | Checked | Covered by `test_ui_retail_skill_mappreview_maptime_ownerdraws_match_ql` |
| 545 | `UI_JOINGAMETYPE` | `UI_DrawJoinGameType @ 0x100052E0`; key `UI_JoinGameType_HandleKey @ 0x1000A300` | Draw and key handler wired | Checked | Covered by `test_ui_retail_gametype_selector_ownerdraws_match_ql` |
| 546 | `UI_PREVIEWCINEMATIC` | Retail dispatcher default/no-op for this ID | Legacy `UI_DrawPreviewCinematic` route exists | Retail no-op/source legacy | Confirm menu reachability and divergence decision |
| 547 | `UI_STARTMAPCINEMATIC` | `UI_DrawMapCinematic @ 0x10005560` with start/net-map path | Draw wired as `UI_DrawMapCinematic(..., qtrue)` | Checked | Covered by `test_ui_retail_map_selection_ownerdraws_match_ql` |
| 548 | `UI_MAPS_SELECTION` | Retail dispatcher handles this ID with current-map display-name paint | Source routes through `UI_DrawAllMapsSelection(..., qfalse)` | Checked | Covered by `test_ui_retail_map_selection_ownerdraws_match_ql` |
| 549 | `UI_ADVERT` | `UI_DrawAdvert @ 0x10009340` | Draw wired through advert bridge; no key or width route | Checked | Covered by `test_ui_retail_advert_runtime_seam_restored` and `test_ui_retail_advert_paint_refresh_and_browser_active_gate_restored` |
| 550 | `UI_CROSSHAIR_COLOR` | `UI_DrawCrosshairColor @ 0x10009660`; key `UI_CrosshairColor_HandleKey @ 0x1000A790` | Draw and gated key handler wired | Checked | Covered by crosshair-color parity tests |
| 551 | `UI_NEXTMAP` | `UI_DrawNextMap @ 0x10006EA0` | Draw wired; no key or width route | Checked | Covered by `test_ui_retail_crosshair_nextmap_selectedplayer_ownerdraws_match_ql` and `test_ui_retail_nextmap_ownerdraw_restored` |
| 552 | `UI_VOTESTRING` | `UI_DrawVoteString @ 0x10006F30` | Draw wired; no key or width route | Checked | Covered by `test_ui_retail_ownerdraw_extensions_restored` |
| 553 | `UI_TEAMPLAYERMODEL` | `UI_DrawTeamPlayerModel @ 0x10005850` | Draw wired; no key or width route | Checked | Covered by `test_ui_ownerdraw_force_model_previews_match_retail_ql` |
| 554 | `UI_ENEMYPLAYERMODEL` | `UI_DrawEnemyPlayerModel @ 0x10005C20` | Draw wired; no key or width route | Checked | Covered by `test_ui_ownerdraw_force_model_previews_match_retail_ql` |
| 555 | `UI_REDTEAMMODEL` | `UI_DrawRedTeamModel @ 0x10005FF0` | Draw wired; no key or width route | Checked | Covered by `test_ui_ownerdraw_force_model_previews_match_retail_ql` |
| 556 | `UI_BLUETEAMMODEL` | `UI_DrawBlueTeamModel @ 0x100062A0` | Draw wired; no key or width route | Checked | Covered by `test_ui_ownerdraw_force_model_previews_match_retail_ql` |
| 557 | `UI_SERVER_SETTINGS` | `UI_DrawServerSettings @ 0x10007030` | Draw wired; no key or width route | Checked | Covered by `test_ui_retail_server_settings_ownerdraw_restored` |
| 558 | `UI_STARTING_WEAPONS` | `UI_DrawStartingWeapons @ 0x10008730` | Draw wired; no key or width route | Checked | Covered by `test_ui_retail_starting_weapons_ownerdraw_restored` |

## Current Counts

| Bucket | Count | IDs |
| --- | ---: | --- |
| Checked | 36 | `513`, `514`, `515`, `516`, `517`, `518`, `519`, `520`, `522`, `528`, `529`, `531`, `532`, `533`, `534`, `535`, `536`, `537`, `538`, `539`, `540`, `541`, `544`, `545`, `547`, `548`, `549`, `550`, `551`, `552`, `553`, `554`, `555`, `556`, `557`, `558` |
| Partial | 1 | `542` |
| Needs check | 0 | None |
| Retail no-op/source legacy | 8 | `521`, `523`, `524`, `525`, `526`, `527`, `543`, `546` |
| No-op/missing | 1 | `530` |
| Sentinel | 1 | `512` |

Next practical sweep order:

1. Complete `UI_KEYBINDSTATUS` from partial coverage to full parity.
2. Separately audit the retail no-op/source legacy set and decide whether each
   source route should stay as harmless compatibility, be gated, or be removed
   for strict retail parity.
3. Confirm `UI_VOTE_KICK` has no shipped UI ownerdraw usage before marking it
   closed as a no-op.
