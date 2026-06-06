# cgame `cgs_t` Layout Map

This note maps the top-level retail `cgs_t` layout used by `cgamex86.dll`
onto the current `src/code/cgame/cg_local.h` definition. The goal is to pin
the struct bands and member roles with hard x86 layout data first, then attach
the strongest retail behavior anchors already recovered in
`docs/reverse-engineering/cgame-mapping.md`.

## Method

- Layout facts come from a local x86 record-layout dump of `cgs_t` using
  `clang -target i686-pc-windows-msvc -DID_INLINE=__inline -Xclang -fdump-record-layouts`
  against `src/code/cgame/cg_local.h`.
- Semantic roles were cross-checked against the committed Ghidra corpus in
  `references/reverse-engineering/ghidra/cgamex86/`, the Binary Ninja HLIL dump
  under `references/hlil/quakelive/cgamex86.dll/`, and the already-promoted
  `cgame` function map in `docs/reverse-engineering/cgame-mapping.md`.
- This pass maps only the top-level `cgs_t` members. Nested payloads such as
  `gameState_t` and `glconfig_t` still deserve their own member-level passes;
  `clientInfo_t` and `cgMedia_t` now have dedicated notes.

## Hard Layout Facts

The nested `clientInfo_t` slab was corrected in the 2026-06-06 clientinfo pass:
retail cgame uses a `0x738` clientinfo stride, not the older source-derived
`0x704` stride. The top-level offsets below remain useful as source-banding
notes, but any retail `cgs_t` byte-offset claim after `clientinfo[]` should be
regenerated after future size-affecting nested repacks. The cgame-only
animation record is now split to the retail `0x18` size, and the source layout
now places the animation block at `0x318`, custom sounds at `0x690`, and the
recovered native identity/voice/avatar tail at `0x710..0x734`; see
`docs/reverse-engineering/cgame-clientinfo.md` for the remaining early-slot map.

- `sizeof(cgs_t) = 0x2C0A0` (`180384`) on the retail-compatible x86 layout.
- The struct tail is:
  - `cgMedia_t media` at `0x2B9E4`
  - `cgAnnouncerProfile_t announcerProfile` at `0x2C09C`
- The retail identity, avatar, and speaking tail recovered at `0x10A42400`
  and adjacent addresses is part of the per-client retail `0x738` slab; see
  `docs/reverse-engineering/cgame-clientinfo.md`.
- The largest top-level embedded slabs are:
  - `clientInfo_t clientinfo[MAX_CLIENTS]` at `0x0F0DC`, retail stride `0x738`
    (`0x704` is a stale source-derived value)
  - `cgMedia_t media` at `0x2B9E4`, size `0x6B8`
  - `gameState_t gameState` at `0x00000`, size `0x4E84`

## Core Bootstrap And Engine Mirror

Retail `CG_Init` (`0x10029820`) seeds this front matter with the game state,
renderer config, and the initial command/snapshot counters. `CG_ConfigString`
(`0x100252F0`) reads directly out of `gameState`; `CG_ProcessSnapshots`
(`0x1004C4D0`) advances `processedSnapshotNum`; and the HUD draw helpers use
the screen-scale triplet as the canonical 640-to-pixel transform.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x00000` | `gameState` | `gameState_t` | Raw configstring store used by `CG_ConfigString` and every configstring-driven parse path. |
| `0x04E84` | `glconfig` | `glconfig_t` | Renderer configuration loaded during `CG_Init` and used by HUD coordinate conversion. |
| `0x07AC8` | `screenXScale` | `float` | Horizontal 640-space scale factor. |
| `0x07ACC` | `screenYScale` | `float` | Vertical 480-space scale factor. |
| `0x07AD0` | `screenXBias` | `float` | Widescreen horizontal bias used when translating HUD rects. |
| `0x07AD4` | `serverCommandSequence` | `int` | Reliable server-command counter consumed by `CG_ExecuteNewServerCommands`. |
| `0x07AD8` | `processedSnapshotNum` | `int` | Snapshot pump cursor advanced by `CG_ProcessSnapshots`. |
| `0x07ADC` | `localServer` | `qboolean` | Startup-side flag used by HUD/network displays such as the lagometer path. |

## Serverinfo, Team Identity, And Vote Mirror

This band holds the durable configstring-derived match identity. Retail
`CG_ConfigStringModified` (`0x10049980`) updates these members, while the vote
HUD draws and serverinfo panels read them back directly.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x07AE0` | `gametype` | `gametype_t` | Current game type; consumed across ownerdraw, event, and render paths. |
| `0x07AE4` | `dmflags` | `int` | Serverinfo gameplay flag mirror. |
| `0x07AE8` | `teamflags` | `int` | Team-rules flag mirror. |
| `0x07AEC` | `fraglimit` | `int` | Match frag limit used by HUD summaries and limit checks. |
| `0x07AF0` | `capturelimit` | `int` | Team-mode cap/score limit used by HUD summaries and end-condition text. |
| `0x07AF4` | `timelimit` | `int` | Match time limit used by timers and end-condition helpers. |
| `0x07AF8` | `voteFlags` | `int` | Vote-capability mask mirrored from server state. |
| `0x07AFC` | `maxclients` | `int` | Client-table bound used by scoreboard, social, and entity-side loops. |
| `0x07B00` | `mapname` | `char[MAX_QPATH]` | Current map name used by intro/endgame ownerdraws. |
| `0x07B40` | `loadout` | `char[MAX_INFO_VALUE]` | Retail loadout string consumed by the starting-weapons intro panel. |
| `0x07F40` | `redTeam` | `char[MAX_QPATH]` | Raw red-team configstring token. |
| `0x07F80` | `blueTeam` | `char[MAX_QPATH]` | Raw blue-team configstring token. |
| `0x07FC0` | `redTeamName` | `char[MAX_TEAMNAME]` | Display name for the red team. |
| `0x07FE0` | `blueTeamName` | `char[MAX_TEAMNAME]` | Display name for the blue team. |
| `0x08000` | `playermodelOverride` | `char[MAX_QPATH]` | Forced player model override parsed from server-side cosmetics/config. |
| `0x08040` | `playerheadmodelOverride` | `char[MAX_QPATH]` | Forced head model override parsed alongside the player model override. |
| `0x08080` | `voteTime` | `int` | Global vote start time shown in the vote HUD line. |
| `0x08084` | `voteYes` | `int` | Global vote yes count. |
| `0x08088` | `voteNo` | `int` | Global vote no count. |
| `0x0808C` | `voteModified` | `qboolean` | Beep/flash latch for vote-state changes. |
| `0x08090` | `voteString` | `char[MAX_STRING_TOKENS]` | Active vote text shown by retail vote ownerdraws. |
| `0x08490` | `teamVoteTime[2]` | `int[2]` | Per-team vote start times. |
| `0x08498` | `teamVoteYes[2]` | `int[2]` | Per-team vote yes counts. |
| `0x084A0` | `teamVoteNo[2]` | `int[2]` | Per-team vote no counts. |
| `0x084A8` | `teamVoteModified[2]` | `qboolean[2]` | Per-team vote change latches. |
| `0x084B0` | `teamVoteString[2]` | `char[2][MAX_STRING_TOKENS]` | Per-team vote text buffers. |

## Match Score, Overtime, Factory, And Freeze-Tip State

Retail `CG_ConfigStringModified` and the match-state parser under
`CG_ServerCommand` feed this entire slab. The already-mapped status ownerdraws
`CG_GetMatchStatusText`, `CG_DrawMatchStatus`, `CG_DrawGameLimit`,
`CG_DrawGameTypeMap`, `CG_DrawMatchDetails`, `CG_DrawMatchEndCondition`,
`CG_DrawEndGameScore`, and the scoreboard helpers all consume data from here.

### Scoreboard And Flag Core

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x08CB0` | `levelStartTime` | `int` | Match start anchor for live timers and overtime math. |
| `0x08CB4` | `scores1` | `int` | Primary team/player score mirror. |
| `0x08CB8` | `scores2` | `int` | Secondary team/player score mirror. |
| `0x08CBC` | `redflag` | `int` | CTF red-flag status mirror. |
| `0x08CC0` | `blueflag` | `int` | CTF blue-flag status mirror. |
| `0x08CC4` | `flagStatus` | `int` | One-flag/aggregate flag-state mirror. |

### Overtime, Timeout, And Round State

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x08CC8` | `matchOvertimeActive` | `qboolean` | Overtime-active latch used by status text, sounds, and HUD timers. |
| `0x08CCC` | `matchOvertimeStartTime` | `int` | Overtime start timestamp. |
| `0x08CD0` | `matchOvertimeEndTime` | `int` | Overtime end timestamp when the server provides one. |
| `0x08CD4` | `matchOvertimeCount` | `int` | Overtime ordinal used by the retail `Overtime %i` label. |
| `0x08CD8` | `matchSuddenDeathActive` | `qboolean` | Sudden-death state latch. |
| `0x08CDC` | `matchTimeoutActive` | `qboolean` | Active timeout latch. |
| `0x08CE0` | `matchTimeoutTeam` | `int` | Team currently owning the timeout. |
| `0x08CE4` | `matchTimeoutExpireTime` | `int` | Timeout end time used by countdown ownerdraws. |
| `0x08CE8` | `matchTimeoutOwner` | `int` | Timeout owner/client side identifier. |
| `0x08CEC` | `matchTimeoutRemaining[TEAM_NUM_TEAMS]` | `int[TEAM_NUM_TEAMS]` | Per-team timeout counts/remaining allowance. |
| `0x08CFC` | `matchRoundTransitionTime` | `int` | Round transition timestamp. |
| `0x08D00` | `matchRoundNumber` | `int` | Current round ordinal. |
| `0x08D04` | `matchRoundTurn` | `int` | Round-turn marker used by round HUD logic. |
| `0x08D08` | `matchRoundState` | `int` | Warmup/active/complete round-state enum mirror. |
| `0x08D0C` | `matchTeamCount[TEAM_NUM_TEAMS]` | `int[TEAM_NUM_TEAMS]` | Per-team live-player count used by CA/FT displays. |
| `0x08D1C` | `matchTeamRespawnRatio[TEAM_NUM_TEAMS]` | `int[TEAM_NUM_TEAMS]` | Per-team respawn ratio mirror for round-based modes. |
| `0x08D2C` | `matchAutoShuffleArmed` | `qboolean` | Autoshuffle pending latch. |
| `0x08D30` | `matchAutoShuffleSecondsRemaining` | `int` | Autoshuffle countdown. |
| `0x08D34` | `matchTimeoutLengthSeconds` | `int` | Configured timeout length. |
| `0x08D38` | `matchTimeoutCountPerTeam` | `int` | Timeout quota per team. |
| `0x08D3C` | `matchOvertimeLengthSeconds` | `int` | Configured overtime length. |
| `0x08D40` | `matchSuddenDeathRespawnsEnabled` | `qboolean` | Sudden-death respawn mode flag. |
| `0x08D44` | `matchSuddenDeathStartSeconds` | `int` | Sudden-death start offset. |
| `0x08D48` | `matchSuddenDeathTickSeconds` | `int` | Sudden-death tick interval. |
| `0x08D4C` | `matchSuddenDeathMaxSeconds` | `int` | Sudden-death cap length. |
| `0x08D50` | `matchSuddenDeathIncrementSeconds` | `int` | Sudden-death growth increment. |
| `0x08D54` | `matchSuddenDeathPrintAnnouncements` | `qboolean` | Retail announcement gate for sudden death. |
| `0x08D58` | `matchSuddenDeathSpawnDelayActive` | `qboolean` | Spawn-delay latch for sudden death / freeze transitions. |
| `0x08D5C` | `matchReadyUpDeadline` | `int` | Ready-up deadline. |
| `0x08D60` | `matchWarmupReadyPercent` | `int` | Warmup ready threshold percentage. |
| `0x08D64` | `matchWarmupReadyCount` | `int` | Current ready count. |
| `0x08D68` | `matchWarmupReadyEligible` | `int` | Number of clients eligible to ready up. |

### Factory And Freeze Tips

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x08D6C` | `factoryTitle` | `char[MAX_STRING_CHARS]` | Factory title shown in score/status overlays. |
| `0x0916C` | `factoryFlags` | `unsigned int` | Factory behavior flag mask. |
| `0x09170` | `factorySpawnHints` | `char[MAX_STRING_CHARS]` | Spawn-hint text block for the scoreboard/help overlays. |
| `0x09570` | `itemTimersEnabled` | `qboolean` | Server-side HUD item-timer enable flag. |
| `0x09574` | `itemTimerHeight` | `int` | HUD line height for item timers. |
| `0x09578` | `forceSmallScoreboardMessage` | `qboolean` | Small-scoreboard message override. |
| `0x0957C` | `forceHudHints` | `qboolean` | HUD hint visibility override. |
| `0x09580` | `forceDmgThroughSurface` | `qboolean` | Damage-plum / effects override for through-surface hits. |
| `0x09584` | `forcedAtmosphere` | `char[MAX_QPATH]` | Forced atmosphere/sky token mirrored from server state. |
| `0x095C4` | `freezeTipObjective` | `char[MAX_STRING_CHARS]` | Freeze-tag objective tip. |
| `0x099C4` | `freezeTipThaw` | `char[MAX_STRING_CHARS]` | Freeze-tag thaw tip. |
| `0x09DC4` | `freezeTipFreeze` | `char[MAX_STRING_CHARS]` | Freeze-tag freeze tip. |
| `0x0A1C4` | `freezeTipShoot` | `char[MAX_STRING_CHARS]` | Freeze-tag shooting tip. |
| `0x0A5C4` | `freezeTipSummary` | `char[MAX_STRING_CHARS]` | Freeze-tag summary/help text. |

## HUD Mode And Race State

The retail `CG_LoadHudMenu` bootstrap, race configstring parsing, and race
HUD/render helpers use this band. The strongest recovered anchors are the race
server-command parsing paths, the HUD draw helpers in `cg_draw.c`, and the race
ownership/summary ownerdraw code in `cg_newdraw.c`.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x0A9C4` | `hudState` | `int` | Retail HUD/layout state latch. Committed HLIL compares this slot against concrete mode values such as `2`, `3`, and `5`; value `5` drives the match-summary banner and the narrower native chat-field layout. |
| `0x0A9C8` | `racePointCount` | `int` | Number of active race points/checkpoints. |
| `0x0A9CC` | `raceLeaderSplitCount` | `int` | Number of leader split entries currently valid. |
| `0x0A9D0` | `racePoints[MAX_RACE_POINTS]` | `cgRacePointInfo_t[64]` | Race point origin/target table. |
| `0x0CDD0` | `raceLeaderSplits[MAX_RACE_POINTS]` | `int[64]` | Leader split times by point index. |
| `0x0CED0` | `raceProgress[MAX_CLIENTS]` | `cgRaceClientProgress_t[64]` | Per-client checkpoint/run progress. |
| `0x0D2D0` | `raceStatus[MAX_CLIENTS]` | `cgRaceClientStatus_t[64]` | Per-client race timing summary. |
| `0x0D8D0` | `raceStatusSequence` | `int` | Race status update sequence. |
| `0x0D8D4` | `raceLeaderClientNum` | `int` | Current race leader client index. |

## Registered Models, Sounds, And Client Cache

Retail `CG_RegisterGraphics` (`0x10022F40`), `CG_RegisterSounds`
(`0x10020E70`), and `CG_RegisterClients` (`0x10025260`) are the main evidence
anchors for this slab. The entity/event/render code uses these arrays directly,
which makes the overall band structurally stable even before diving into the
separate nested `clientInfo_t` and `cgMedia_t` member notes.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x0D8D8` | `gameModels[MAX_MODELS]` | `qhandle_t[256]` | Configstring-registered world and entity models. |
| `0x0DCD8` | `gameSounds[MAX_SOUNDS]` | `sfxHandle_t[256]` | Configstring-registered sounds used by entity and event playback. |
| `0x0E0D8` | `numInlineModels` | `int` | Count of inline BSP models cached for rendering. |
| `0x0E0DC` | `inlineDrawModel[MAX_MODELS]` | `qhandle_t[256]` | Registered inline model handles. |
| `0x0E4DC` | `inlineModelMidpoints[MAX_MODELS]` | `vec3_t[256]` | Cached inline-model bounds midpoints. |
| `0x0F0DC` | `clientinfo[MAX_CLIENTS]` | `clientInfo_t[64]` | Durable per-client presentation/state cache used across HUD, events, and rendering. |

## Buffered Team Chat, HUD Cursor State, And Order UI

This is the most retail-specific tail before `media`. The buffered team-chat
stack is anchored directly by `CG_InitTeamChat` (`0x100068E0`),
`CG_PushPrintString` (`0x10006910`), and `CG_DrawNewChatArea` (`0x10006A10`).
The cursor/event/order members are likewise anchored by `CG_MouseEvent`
(`0x100208F0`), `CG_KeyEvent` (`0x1003C6F0`), `CG_EventHandling`
(`0x1003C620`), and the team-order ownerdraw/console-command paths.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x2B1DC` | `teamChatMsgs[TEAMCHAT_HEIGHT][TEAMCHAT_WIDTH * 3 + 1]` | `char[8][241]` | Timed buffered team-chat text ring. |
| `0x2B964` | `teamChatMsgTimes[TEAMCHAT_HEIGHT]` | `int[8]` | Per-entry timestamps for the chat ring. |
| `0x2B984` | `teamChatPos` | `int` | Current write cursor into the chat ring. |
| `0x2B988` | `teamLastChatPos` | `int` | Previous visible/read cursor for chat history. |
| `0x2B98C` | `cursorX` | `int` | HUD cursor X position in 640-space. |
| `0x2B990` | `cursorY` | `int` | HUD cursor Y position in 480-space. |
| `0x2B994` | `eventHandling` | `cgameEvent_t` | Current HUD/event handling mode. |
| `0x2B998` | `mouseCaptured` | `qboolean` | Mouse-capture latch for HUD editing/menus. |
| `0x2B99C` | `sizingHud` | `qboolean` | HUD sizing/edit mode latch. |
| `0x2B9A0` | `capturedItem` | `void *` | Live HUD item pointer captured by mouse interaction. |
| `0x2B9A4` | `activeCursor` | `qhandle_t` | Current cursor shader handle. |
| `0x2B9A8` | `currentOrder` | `int` | Active team-order enum/value. |
| `0x2B9AC` | `orderPending` | `qboolean` | Team-order pending latch. |
| `0x2B9B0` | `orderTime` | `int` | Order UI timestamp. |
| `0x2B9B4` | `currentVoiceClient` | `int` | Current voice/order target client. |
| `0x2B9B8` | `acceptOrderTime` | `int` | Time window for accepting an order. |
| `0x2B9BC` | `acceptTask` | `int` | Pending accepted task id. |
| `0x2B9C0` | `acceptLeader` | `int` | Client index of the accepting leader. |
| `0x2B9C4` | `acceptVoice` | `char[MAX_NAME_LENGTH]` | Voice command token/text for the accept-order path. |

## Media Tail

This tail is stable at the top level. Retail `CG_RegisterGraphics` and
`CG_RegisterSounds` fill `media`, while the announcer/reward voice logic reads
`announcerProfile` directly in the playerstate and view paths; see
`docs/reverse-engineering/cgame-cgmedia.md` for the nested member map.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x2B9E4` | `media` | `cgMedia_t` | Registered HUD, model, shader, and sound handle slab. |
| `0x2C09C` | `announcerProfile` | `cgAnnouncerProfile_t` | Active announcer voice/profile selection. |

## Notably Outside `cgs_t`

- The retail tracked-player notifier timestamps remain separate cgame globals,
  but mute/social identity, speaking state, and avatar handle storage are now
  mapped to the retail `clientInfo_t` tail around `0x10A42400`.
- Frame-local prediction, view, and transient HUD state still lives in `cg_t`;
  see `docs/reverse-engineering/cgame-cg.md`.
- The native entry-table exports (`CG_CopyClientIdentity`,
  `CG_SetClientSpeakingState`, tracked-player notifiers, and the remaining tiny
  layout getters) are better understood as interfaces around `cgs_t`, the
  `clientInfo_t` slab, and a few cgame globals rather than as standalone public
  structs.

## Follow-Up Struct Passes

1. Revisit the retail HUD/menu bridge once `cgDC` and `displayContextDef_t`
   members are mapped at the same level of detail.
