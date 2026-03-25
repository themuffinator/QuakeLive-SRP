# cgame `score_t` Layout Map

This note maps the retail-compatible x86 layout of `score_t` used by
`cgamex86.dll` onto the current `src/code/cgame/cg_local.h` definition. The
goal is to separate hard layout facts from the two retail score-population
paths and the scoreboard / feeder / ownerdraw consumers that actually read the
payload.

## Method

- Layout facts come from a local x86 record-layout dump of `score_t`,
  `qboolean`, and `cg_t` using
  `clang -target i686-pc-windows-msvc -DID_INLINE=__inline -Xclang -fdump-record-layouts`
  against `src/code/cgame/cg_local.h`.
- Member ownership was cross-checked against the two score-population paths in
  `src/code/cgame/cg_servercmds.c`, the legacy scoreboard in
  `src/code/cgame/cg_scoreboard.c`, the menu/feed bridge in
  `src/code/cgame/cg_main.c`, and the newer endgame / placement HUD paths in
  `src/code/cgame/cg_newdraw.c`.
- Retail parity was cross-checked against the committed HLIL and Ghidra corpus
  for the surrounding scoreboard subsystem, especially the already-recovered
  retail helpers `CG_FeederItemText`, `CG_DrawSelectedPlayerAccuracy`,
  `CG_DrawSelectedPlayerBestWeapon`, and `CG_DrawEndGameScore`, plus the retail
  scoreboard menu/command string family (`scores`, `scores_ffa`,
  `ui/ingame_scoreboard_*.menu`, `ui/end_scoreboard_*.menu`).

## Hard Layout Facts

- `sizeof(score_t) = 0x44` (`68`).
- `qboolean` remains a 32-bit `int` on this target, so `perfect` occupies a
  full four-byte slot at `0x34`.
- `cg_t` embeds `score_t scores[MAX_CLIENTS]` as a flat `64`-entry array at
  offset `0x1B220`.
- The top-level banding is simple:
  - identity and headline scoreboard values at `0x00`
  - carry-over wire/stat fields at `0x10`
  - award and pickup counters at `0x18`
  - placement/endgame summary fields at `0x34`

## Top-Level Member Map

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x00` | `client` | `int` | Owning client slot for this scoreboard row; primary lookup key into `cgs.clientinfo[]`. |
| `0x04` | `score` | `int` | Main scoreboard value used for placement, rank, and score-column display. |
| `0x08` | `ping` | `int` | Network latency shown in scoreboard and team aggregate views. |
| `0x0C` | `time` | `int` | Match time / race time payload used by scoreboard timers and endgame summaries. |
| `0x10` | `scoreFlags` | `int` | Structurally present scoreboard flag word parsed from the full score command, but not strongly revalidated by the current HUD consumers. |
| `0x14` | `powerUps` | `int` | Structurally present carry-over field; cold in the current tree because retail/source consumers read `cgs.clientinfo[client].powerups` instead. |
| `0x18` | `accuracy` | `int` | Accuracy percentage used by selected-player and placement HUD paths. |
| `0x1C` | `impressiveCount` | `int` | Medal/stat counter used by placement and award summaries. |
| `0x20` | `excellentCount` | `int` | Medal/stat counter used by placement and award summaries. |
| `0x24` | `guantletCount` | `int` | Gauntlet medal counter; the source typo is part of the shipped layout, so the field name is kept as-is. |
| `0x28` | `defendCount` | `int` | Defense-event counter used by placement and team pickup summaries. |
| `0x2C` | `assistCount` | `int` | Assist counter used by placement and team pickup summaries. |
| `0x30` | `captures` | `int` | Capture / objective counter used by placement, awards, and CTF-style summaries. |
| `0x34` | `perfect` | `qboolean` | Perfect-medal boolean consumed by newer endgame/placement ownerdraws. |
| `0x38` | `team` | `int` | Locally derived team classification used for feeder grouping and spectator filtering. |
| `0x3C` | `damage` | `int` | Damage total used by newer placement and endgame summaries. |
| `0x40` | `deaths` | `int` | Death total used by newer placement and endgame summaries. |

## Population Ownership

### Full Score Command Path

`CG_ParseScores` is the main population path. It clears the entire `cg.scores`
array, parses `cg.numScores`, parses `cg.teamScores[0]` and `cg.teamScores[1]`,
then fills each row from a `16`-field score payload after the header.

Per row, the current source-side field order is:

| Command token | Destination |
| --- | --- |
| `+4` | `client` |
| `+5` | `score` |
| `+6` | `ping` |
| `+7` | `time` |
| `+8` | `scoreFlags` |
| `+9` | temporary `powerups` local |
| `+10` | `accuracy` |
| `+11` | `impressiveCount` |
| `+12` | `excellentCount` |
| `+13` | `guantletCount` |
| `+14` | `defendCount` |
| `+15` | `assistCount` |
| `+16` | `perfect` |
| `+17` | `captures` |
| `+18` | `damage` |
| `+19` | `deaths` |

Important caveats from this path:

- `powerUps` is not repopulated into `cg.scores[i].powerUps` here. The parsed
  value is stored in a temporary local and mirrored to
  `cgs.clientinfo[cg.scores[i].client].powerups`.
- `team` is not parsed from its own score token. It is derived after client
  sanitization from `cgs.clientinfo[cg.scores[i].client].team`.
- `client` is sanitized into `[0, MAX_CLIENTS)` before the `clientinfo` mirror
  writes happen.

### Abbreviated Score Path

Retail/source also keeps an older abbreviated score path that only populates the
headline scoreboard fields. That path:

- clears `cg.scores`
- fills only `client` and `score`
- explicitly zeroes `ping`, `time`, `scoreFlags`, `powerUps`, `accuracy`,
  `impressiveCount`, `excellentCount`, `guantletCount`, `defendCount`,
  `assistCount`, `perfect`, `captures`, `damage`, and `deaths`
- mirrors `score` into `cgs.clientinfo[client].score`
- clears `cgs.clientinfo[client].powerups`
- derives `team` from `cgs.clientinfo[client].team`
- clears `cg.scoreStats` and `cg.teamScoreStats`

That older path matters because it confirms the same stable top-level layout
even when the server only sends a reduced scoreboard payload.

## Consumer Bands

### Legacy Scoreboard

`cg_scoreboard.c` treats `score_t` as the row model for the classic scoreboard.
The strong fields there are:

- `client` for `clientInfo_t` lookup and local-player matching
- `score`, `ping`, and `time` for the visible scoreboard columns
- `team` for per-team row grouping

The important non-use is `powerUps`: the scoreboard icon/status path reads
`clientInfo_t.powerups`, not `score_t.powerUps`.

### Menu / Feeder Bridge

The `cgDC` scoreboard feeders in `cg_main.c` use the same rows as UI-facing
data:

- `CG_FeederCount` groups by `team`
- `CG_SetScoreSelection` matches the local player through `client` and moves
  selection inside the team-filtered row family
- `CG_InfoFromScoreIndex` resolves `clientInfo_t` through `client`
- `CG_FeederItemText` formats names, score, time, ping, ready state, and team
  grouping from `client`, `score`, `time`, `ping`, and `team`

This band is one of the strongest retail anchors because the surrounding
callback bridge and `CG_FeederItemText` itself are already mapped in the retail
ledger.

### Newer Endgame / Placement HUD

`cg_newdraw.c` exercises the broader stat tail that the legacy scoreboard barely
touches. Strong fields here include:

- `accuracy` for selected-player accuracy
- `client` for selected-player weapon/best-weapon resolution
- `score`, `damage`, `deaths`, and `time` for placement/endgame summaries
- `captures`, `assistCount`, and `defendCount` for objective and pickup
  summaries
- `excellentCount`, `impressiveCount`, `guantletCount`, and `perfect` for
  medal/award summaries
- `team` for spectator filtering and team aggregate views

This is the main reason `score_t` should be read as more than a legacy
scoreboard row: retail uses it as the shared scalar payload for old scoreboard
rendering, feeder/UI selection, and the newer placement/endgame ownerdraw
family.

## Field-Strength Notes

### Strongly Owned Fields

The following members have direct write ownership in the score-population paths
and at least one strong current consumer:

- `client`
- `score`
- `ping`
- `time`
- `accuracy`
- `impressiveCount`
- `excellentCount`
- `guantletCount`
- `defendCount`
- `assistCount`
- `captures`
- `perfect`
- `team`
- `damage`
- `deaths`

### Weak Or Cold Fields

- `scoreFlags` is parsed and preserved by the full score path, but I did not
  find a strong current HUD/scoreboard consumer in `src/code/cgame/`.
- `powerUps` is present in the shipped struct layout, but the live tree routes
  that information through `cgs.clientinfo[].powerups` instead of reading or
  repopulating `cg.scores[i].powerUps`.

## Practical Reading Guide

- If the question is "which client does this row belong to?", start at
  `client`.
- If the question is "what does the visible scoreboard row show?", start at
  `score`, `ping`, `time`, and `team`.
- If the question is "which fields drive the selected-player or endgame HUD?",
  start at `accuracy`, `captures`, `assistCount`, `defendCount`, `damage`,
  `deaths`, `excellentCount`, `impressiveCount`, `guantletCount`, and
  `perfect`.
- If the question is "where did the team or powerup state come from?", check
  the mirror path through `cgs.clientinfo[]` before assuming those values are
  directly owned by `score_t`.

## Open Questions

1. Recover the exact retail `CG_ParseScores` boundary in the committed HLIL or
   refreshed Ghidra corpus so the full per-token write order can be grounded in
   a direct binary write trace instead of the current source-side analogue plus
   surrounding retail subsystem evidence.
2. Revalidate whether retail still has any dormant consumers for `scoreFlags`
   or `score_t.powerUps` outside the currently reconstructed scoreboard, feeder,
   and ownerdraw paths.
