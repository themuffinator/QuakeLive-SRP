# UI `uiInfo_t` Layout Map

This note maps the retail-compatible x86 layout of `uiInfo_t` used by
`uix86.dll` onto the current `src/code/ui/ui_local.h` definition. The goal is
to pin the top-level member layout first, then separate the strongly
retail-anchored bands from the Quake Live-era extensions that are currently
best explained by the reconstructed source tree.

Unlike the old `q3_ui` qmenu-only front matter, the Team Arena UI already had a
named `uiInfo_t` baseline in `assets/quake3/src/code/ui/ui_local.h`. The
current Quake Live-compatible tree keeps that ancestor but widens it for clan,
country, map-rotation, ruleset, and match-summary state.

## Method

- Layout facts come from local x86 `sizeof` and `offsetof` probes compiled with
  `clang -m32 -target i686-pc-windows-msvc` against
  `src/code/ui/ui_local.h`.
- The historical baseline comes from the Team Arena-era `uiInfo_t` in
  `assets/quake3/src/code/ui/ui_local.h` and the matching
  `displayContextDef_t` in `assets/quake3/src/code/ui/ui_shared.h`.
- Member roles were cross-checked against the current owners in
  `src/code/ui/ui_main.c`, `src/code/ui/ui_gameinfo.c`, and
  `src/code/ui/ui_atoms.c`.
- Retail parity is strongest for the already-mapped `uix86.dll` helpers
  `_UI_Init`, `UI_ParseGameInfo`, `UI_BuildPlayerList`,
  `UI_DrawSelectedPlayer`, `UI_BuildServerDisplayList`,
  `UI_GetServerStatusInfo`, `UI_BuildFindPlayerList`, and
  `UI_BuildServerStatus`, as documented in
  `docs/reverse-engineering/ui-mapping-pass-2026-03-20.md`.
- This pass maps only the top-level `uiInfo_t` members.
- The browser-side nested records
  `serverFilter_t`, `pinglist_t`, `serverStatus_t`, `pendingServer_t`,
  `pendingServerStatus_t`, `serverStatusInfo_t`, and `modInfo_t` are now
  documented separately in `docs/reverse-engineering/ui-browser-support-structs.md`.
- The catalog-side nested records `characterInfo`, `aliasInfo`, `teamInfo`,
  `gameTypeInfo`, `mapInfo`, and `tierInfo` are now documented separately in
  `docs/reverse-engineering/ui-catalog-struct-layouts.md`.
- The Quake Live catalog-extension records `uiClanInfo_t`,
  `mapRotationInfo_t`, `rulesetInfo_t`, and the flat `countryList[]` feeder
  bank are now documented separately in
  `docs/reverse-engineering/ui-quakelive-catalog-struct-layouts.md`.
- The display-context nested records `displayContextDef_t` and
  `cachedAssets_t` are now documented separately in
  `docs/reverse-engineering/ui-display-context-struct-layouts.md`.
- The match-summary nested records `uiMatchPlayerInfo_t`,
  `uiMatchPlayerList_t`, and `uiMatchSummaryCache_t` are now documented
  separately in
  `docs/reverse-engineering/ui-match-summary-struct-layouts.md`.

## Hard Layout Facts

- `sizeof(uiInfo_t) = 0x175424` (`1528868`) on the current retail-compatible
  x86 layout.
- The Team Arena baseline is `sizeof(uiInfo_t) = 0x216D0` (`136912`).
- The front `displayContextDef_t uiDC` slab grew from `0x11EC8` to `0x11ECC`.
  The current shift comes from the extra `playLauncherCinematic` callback added
  to `displayContextDef_t` in `src/code/ui/ui_shared.h`.
- The largest embedded slabs are:
  - `displayContextDef_t uiDC` at `0x000000`, size `0x11ECC`
  - `mapRotations[MAX_MAP_ROTATIONS]` at `0x023F34`, stride `0x1404`
  - `rulesets[MAX_RULESETS]` at `0x164340`, stride `0x800`
  - `serverStatus_t serverStatus` at `0x1690E4`, size `0x2CDC`
  - `serverStatusInfo_t serverStatusInfo` at `0x16BE00`, size `0xD04`
  - `pendingServerStatus_t pendingServerStatus` at `0x16CB08`, size `0x8C4`
  - `uiMatchSummaryCache_t matchSummary` at `0x1723F4`, size `0x3024`
- Relative to the Team Arena baseline, the Quake Live-era top-level growth is:
  - `+0x000004` from the larger `displayContextDef_t`
  - `+0x00C810` inserted after `teamList` for clan and country storage
  - `+0x144510` inserted after `mapList` for map rotations and rulesets
  - `+0x003030` appended after `inGameLoad` for match summary storage and
    selection cursors

## Display Context And Postgame Timers

This front matter is the strongest retail-anchored band. `_UI_Init`
(`FUN_1000fab0`) seeds the `uiDC` callback table and scaling values, while the
best-score and postgame helpers maintain the timing and visibility latches.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x000000` | `uiDC` | `displayContextDef_t` | Master UI display/render context. `_UI_Init` assigns renderer hooks, text helpers, feeder callbacks, cinematic hooks, screen scaling, cursor, white shader, fonts, and cached assets into this block. |
| `0x011ECC` | `newHighScoreTime` | `int` | Real-time deadline for the `UI_SHOW_NEWHIGHSCORE` visibility gate. Written by `UI_CalcPostGameStats` and read by ownerdraw visibility checks. |
| `0x011ED0` | `newBestTime` | `int` | Real-time deadline for the `UI_SHOW_NEWBESTTIME` gate. |
| `0x011ED4` | `showPostGameTime` | `int` | Dormant Team Arena carry-over postgame timing slot. It exists in the older `assets/quake3` `uiInfo_t` baseline too, and neither that baseline nor the current tree exposes a live writer or reader. |
| `0x011ED8` | `newHighScore` | `qboolean` | Postgame high-score latch populated through `UI_SetBestScores`. |
| `0x011EDC` | `demoAvailable` | `qboolean` | Indicates whether a matching recorded demo exists for the current map/gametype. `UI_LoadBestScores` sets it by probing `demos/<map>_<gt>.dm_*`, and ownerdraw visibility uses it for `UI_SHOW_DEMOAVAILABLE`. |
| `0x011EE0` | `soundHighScore` | `qboolean` | One-shot audio latch for the announcer high-score sound. The ownerdraw visibility path clears it after playing `newHighScoreSound`. |

## Character, Team, Clan, And Country Catalogs

This band is mostly content-cache state. Retail evidence is strongest for the
player/team list sub-band via `UI_BuildPlayerList`; the clan and country
extensions are Quake Live additions, but the clan side now reads as a
compatibility-heavy cache with no committed menu consumer and no bounded
host-side `qz_instance` clan-roster contract or clan event family in the
bounded browser publish surface.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x011EE4` | `characterCount` | `int` | Number of active head/character entries in `characterList[]`. |
| `0x011EE8` | `botIndex` | `int` | Current bot/character feeder selection used by addbot and player-setup menu actions. |
| `0x011EEC` | `characterList` | `characterInfo[MAX_HEADS]` | Cached legacy bot/head metadata used by addbot and team setup flows; retail `FEEDER_HEADS` / `FEEDER_Q3HEADS` are backed by the validated player-model catalog instead. |
| `0x0124EC` | `aliasCount` | `int` | Number of alias entries in `aliasList[]`. |
| `0x0124F0` | `aliasList` | `aliasInfo[MAX_ALIASES]` | Alias-to-AI lookup table used by bot and team-setup flows. |
| `0x0127F0` | `teamCount` | `int` | Number of team definitions in `teamList[]`. |
| `0x0127F4` | `teamList` | `teamInfo[MAX_TEAMS]` | Team metadata and icon/cinematic cache used by team-selection ownerdraws and setup flows. |
| `0x0132F4` | `clanCount` | `int` | Historical candidate count for live clan entries in `clanList[]`; no current source field or active retail feeder branch is bounded for this band. |
| `0x0132F8` | `clanList` | `uiClanInfo_t[MAX_CLANS]` | Historical clan roster cache candidate with id/name/tag/emblem metadata. The current source no longer carries this band or exposes feeder paths for it: committed retail `uix86.dll` dispatch falls through for `FEEDER_CLANS`, no committed source or retail menu tree consumes clan UI surfaces, and the bounded host `qz_instance` bridge exposes no clan-roster RPC. The similarly named `UI_CLANNAME` / `UI_CLANLOGO` ownerdraws are older `teamList[]`-backed team-branding carry-overs, not consumers of this cache. |
| `0x01F6F8` | `currentClan` | `int` | Historical candidate selected clan index; absent from the current source after the clan-feeder scaffold was removed. |
| `0x01F6FC` | `clanListLoaded` | `qboolean` | Historical candidate clan-cache guard; absent from the current source after the clan-feeder scaffold was removed. |
| `0x01F700` | `countryCount` | `int` | Number of parsed country-code entries in `countryList[]`. Quake Live-specific addition. |
| `0x01F704` | `countryList` | `const char *[256]` | Country-code feeder table loaded from `ui/country.txt`. |

## Gametype, Player Selection, Map, Rotation, Ruleset, And Tier Cache

This is the main selection/catalog slab for offline and browser menus. Retail
anchors are strongest for `UI_ParseGameInfo` and `UI_BuildPlayerList`; the
map-rotation cache now reads as a retail split between host-side map-pool
loading and UI-side preview/filter consumers, with the retail callvote submit
token tied to `ui_cvGameType` rather than to rotation rows, while the ruleset
cache now reads as compatibility staging over game/host-owned
ruleset-factory state rather than as a retail UI-owned menu band.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x01FB04` | `numGameTypes` | `int` | Number of populated start-server/offline gametype entries. |
| `0x01FB08` | `gameTypes` | `gameTypeInfo[MAX_GAMETYPES]` | Cached primary gametype table parsed by `UI_ParseGameInfo`. |
| `0x01FB88` | `numJoinGameTypes` | `int` | Number of populated join/browser gametype entries. |
| `0x01FB8C` | `joinGameTypes` | `gameTypeInfo[MAX_GAMETYPES]` | Cached join/browser gametype table. |
| `0x01FC0C` | `redBlue` | `int` | Red-vs-blue selection latch used mainly by addbot and team-assignment flows. |
| `0x01FC10` | `playerCount` | `int` | Number of valid names in `playerNames[]`. Built by `UI_BuildPlayerList`. |
| `0x01FC14` | `myTeamCount` | `int` | Number of valid names in the local-team subset `teamNames[]`. |
| `0x01FC18` | `teamIndex` | `int` | Selected teammate index for team-vote/leadership actions. |
| `0x01FC1C` | `playerRefresh` | `int` | Next rebuild deadline for the player/team cache. `UI_DrawSelectedPlayer` and the feeder count path refresh when `realTime > playerRefresh`. |
| `0x01FC20` | `playerIndex` | `int` | Selected all-player index for kick/admin style actions. |
| `0x01FC24` | `playerNumber` | `int` | Local client number cached by `UI_BuildPlayerList`. |
| `0x01FC28` | `teamLeader` | `qboolean` | Local team-leader latch used to gate team-order and selected-player actions. |
| `0x01FC2C` | `playerNames` | `char[MAX_CLIENTS][MAX_NAME_LENGTH]` | Flat all-player name cache for feeders and vote text. |
| `0x02042C` | `teamNames` | `char[MAX_CLIENTS][MAX_NAME_LENGTH]` | Local-team-only name cache. |
| `0x020C2C` | `teamClientNums` | `int[MAX_CLIENTS]` | Client-number mirror aligned with `teamNames[]`. |
| `0x020D2C` | `mapCount` | `int` | Number of valid `mapList[]` entries. |
| `0x020D30` | `mapList` | `mapInfo[MAX_MAPS]` | Cached map metadata, levelshots, cinematics, and time-to-beat values populated by `UI_LoadArenas` / `UI_ParseGameInfo`. |
| `0x023F30` | `mapRotationCount` | `int` | Number of valid `mapRotations[]` entries. Quake Live-specific addition. |
| `0x023F34` | `mapRotations` | `mapRotationInfo_t[MAX_MAP_ROTATIONS]` | Parsed map-rotation/factory cache exposed through the reconstructed callvote and feeder flows. Retail `uix86.dll` clearly consumes equivalent preview/filter state, while committed `quakelive_steam.exe` HLIL shows the file-backed `sv_mapPoolFile` bootstrap and parser living in the native host; the retail `voteMap` submit token itself is now better bounded to `ui_cvGameType -> UI_GetCallvoteGametypeToken` rather than to a rotation-row field. |
| `0x164334` | `currentMapRotation` | `int` | Selected map-rotation index for the callvote rotation feeder. |
| `0x164338` | `rulesetCount` | `int` | Number of valid ruleset entries in `rulesets[]`. Quake Live-specific addition. |
| `0x16433C` | `rulesetIndex` | `int` | Selected ruleset entry index. |
| `0x164340` | `rulesets` | `rulesetInfo_t[MAX_RULESETS]` | Cached ruleset token/description table loaded by `UI_LoadRulesets`. The current best reading is a compatibility cache layered over game/host-owned ruleset-factory state rather than a retail UI-owned menu record. |
| `0x168340` | `activeRuleset` | `char[MAX_CVAR_VALUE_STRING]` | Raw `g_ruleset` token used to seed and match the ruleset feeder cache from authoritative game state. |
| `0x168440` | `tierCount` | `int` | Number of single-player tiers in `tierList[]`. |
| `0x168444` | `tierList` | `tierInfo[MAX_TIERS]` | Single-player tier metadata reused by level/tier ownerdraws. |
| `0x1686C4` | `skillIndex` | `int` | Current skill selection index for addbot and offline setup menus. |

## Mods, Demos, Movies, And Preview State

This band is a simple filesystem-fed catalog and selection cache.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x1686C8` | `modList` | `modInfo_t[MAX_MODS]` | Discovered mod directory/description table. |
| `0x1688C8` | `modCount` | `int` | Number of valid `modList[]` entries. |
| `0x1688CC` | `modIndex` | `int` | Selected mod index. |
| `0x1688D0` | `demoList` | `const char *[MAX_DEMOS]` | Demo filename feeder cache loaded from `demos/`. |
| `0x168CD0` | `demoCount` | `int` | Number of demo filenames cached in `demoList[]`. |
| `0x168CD4` | `demoIndex` | `int` | Selected demo index. |
| `0x168CD8` | `movieList` | `const char *[MAX_MOVIES]` | Cinematic filename feeder cache loaded from `video/`. |
| `0x1690D8` | `movieCount` | `int` | Number of movie filenames cached in `movieList[]`. |
| `0x1690DC` | `movieIndex` | `int` | Selected movie index. |
| `0x1690E0` | `previewMovie` | `int` | Active preview cinematic handle. The draw path uses negative sentinels (`-1`, `-2`) for not-yet-started and failed states. |

## Server Browser, Server Status, And Find-Player State

This tail is strongly retail-anchored by `UI_BuildServerDisplayList`,
`UI_GetServerStatusInfo`, `UI_BuildFindPlayerList`, and `UI_BuildServerStatus`.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x1690E4` | `serverStatus` | `serverStatus_t` | Main browser cache: ping list, visible display servers, sort state, MOTD scroll state, and selected-server preview handles. |
| `0x16BDC0` | `serverStatusAddress` | `char[MAX_ADDRESSLENGTH]` | Address string for the currently selected server-status target. |
| `0x16BE00` | `serverStatusInfo` | `serverStatusInfo_t` | Tokenized cvar/player status lines for the active server. `UI_GetServerStatusInfo` fills this record. |
| `0x16CB04` | `nextServerStatusRefresh` | `int` | Next scheduled refresh time for the selected-server status probe. |
| `0x16CB08` | `pendingServerStatus` | `pendingServerStatus_t` | Outstanding asynchronous status requests used by the find-player worker. |
| `0x16D3CC` | `findPlayerName` | `char[MAX_STRING_CHARS]` | Scrubbed target name for the find-player search flow. |
| `0x16D7CC` | `foundPlayerServerAddresses` | `char[MAX_FOUNDPLAYER_SERVERS][MAX_ADDRESSLENGTH]` | Result-address cache for find-player hits. |
| `0x16DBCC` | `foundPlayerServerNames` | `char[MAX_FOUNDPLAYER_SERVERS][MAX_ADDRESSLENGTH]` | Result-label cache for find-player hits and progress/error text. |
| `0x16DFCC` | `currentFoundPlayerServer` | `int` | Selected row in the find-player result feeder. |
| `0x16DFD0` | `numFoundPlayerServers` | `int` | Number of currently valid find-player result rows. |
| `0x16DFD4` | `nextFindPlayerRefresh` | `int` | Next scheduled polling time for the asynchronous find-player workflow. |

## Crosshair, Q3 Head Bank, And Match Summary Tail

This final band mixes older Team Arena carry-over selectors with newer Quake
Live additions for end-of-match scoreboards.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x16DFD8` | `currentCrosshair` | `int` | Current crosshair selection index mirrored to `cg_drawCrosshair`. |
| `0x16DFDC` | `startPostGameTime` | `int` | Dormant Team Arena carry-over postgame anchor. It is already present in the older `assets/quake3` `uiInfo_t` baseline, and neither that baseline nor the current tree exposes a live owner. |
| `0x16DFE0` | `newHighScoreSound` | `sfxHandle_t` | Registered announcer sound handle used when a new high score is shown. |
| `0x16DFE4` | `q3HeadCount` | `int` | Number of fallback Quake III player-model heads discovered by `UI_BuildQ3Model_List`. |
| `0x16DFE8` | `q3HeadNames` | `char[MAX_PLAYERMODELS][64]` | Fallback Q3 head/model name table. |
| `0x171FE8` | `q3HeadIcons` | `qhandle_t[MAX_PLAYERMODELS]` | Registered icon handles aligned with `q3HeadNames[]`. |
| `0x1723E8` | `q3SelectedHead` | `int` | Selected fallback Q3 head index. |
| `0x1723EC` | `effectsColor` | `int` | Current effects-color/cosmetics selection mirrored to `color1`. |
| `0x1723F0` | `inGameLoad` | `qboolean` | In-game-load mode latch. The original `_UI_Init(inGameLoad)` assignment is currently commented out, but later menu flow still checks this slot. |
| `0x1723F4` | `matchSummary` | `uiMatchSummaryCache_t` | Quake Live-specific cached end-of-match summary: overall, red-team, and blue-team player lists plus match score/time metadata. In the current tree it also backs compatibility aliases for scoreboard-style feeders, but the retail scoreboard/team feeder family is already better anchored on the cgame `cgDC` side. |
| `0x175418` | `currentMatchSummaryEnd` | `int` | Selected row index for the end-of-match feeder. |
| `0x17541C` | `currentMatchSummaryRed` | `int` | Selected row index for the red-team summary feeder. |
| `0x175420` | `currentMatchSummaryBlue` | `int` | Selected row index for the blue-team summary feeder. |

## Delta From Team Arena `uiInfo_t`

The Team Arena baseline already contained most of the classic UI catalogs:
characters, aliases, teams, gametypes, maps, tiers, mods, demos, movies, the
server browser, find-player state, and the Q3 head bank.

The Quake Live-era top-level additions are the following:

- Clan roster cache:
  - `clanCount`
  - `clanList[MAX_CLANS]`
  - `currentClan`
  - `clanListLoaded`
- Country feeder cache:
  - `countryCount`
  - `countryList[256]`
- Map-rotation and ruleset caches:
  - `mapRotationCount`
  - `mapRotations[MAX_MAP_ROTATIONS]`
  - `currentMapRotation`
  - `rulesetCount`
  - `rulesetIndex`
  - `rulesets[MAX_RULESETS]`
  - `activeRuleset`
- End-of-match summary tail:
  - `matchSummary`
  - `currentMatchSummaryEnd`
  - `currentMatchSummaryRed`
  - `currentMatchSummaryBlue`

## Open Questions

1. Determine whether retail ever exposed any clan-roster ownership outside the
   committed native/browser corpus. Within the local retail evidence set, the
   native answer is already effectively "no": `FEEDER_CLANS` has no menu
   consumer, `ui_clanName` / `ui_clanIndex` have no committed UI or host
   anchors, the bounded host `qz_instance` table exposes map/factory/demo/
   config, lobby, friend-list, and UGC helpers but no clan-roster contract,
   and the bounded `EnginePublish` event vocabulary exposes lobby/game/web
   event families but no clan event family. The misleading `UI_CLANNAME` /
   `UI_CLANLOGO` ownerdraw labels are already accounted for in the older
   `teamList[]` band, not in `clanList[]`. The host bootstrap also expects a
   `web.pak` browser payload that is not present in the local retail asset set,
   so the external browser layer remains unrepresented in this corpus.
