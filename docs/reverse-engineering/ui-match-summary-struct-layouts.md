# UI Match Summary Struct Layouts

This note maps the Quake Live-compatible end-of-match summary structs that sit
under `uiInfo_t`: `uiMatchPlayerInfo_t`, `uiMatchPlayerList_t`, and
`uiMatchSummaryCache_t`.

Unlike the older browser, qmenu, and catalog helper records, this family is a
Quake Live-era extension rather than a Team Arena carry-over. The top-level
`uiInfo_t` placement is already pinned in `docs/reverse-engineering/ui-uiinfo.md`;
this pass closes the nested member layout and the current owner semantics.

## Method

- Layout facts come from a local x86 `sizeof` and `offsetof` probe compiled
  with `clang -m32 -target i686-pc-windows-msvc` against
  `src/code/ui/ui_local.h`, using the Win32 preprocessor path expected by
  `q_shared.h`.
- Current member roles were cross-checked against the owners in
  `src/code/ui/ui_main.c`:
  `UI_ResetMatchSummaryCache`, `UI_MatchSummaryAppend`,
  `UI_MatchSummaryParseFromPostgame`, `UI_MatchSummaryListForFeeder`,
  `UI_FeederCount`, `UI_FeederItemText`, and `UI_FeederSelection`.
- The current parse entrypoint is wired through `UI_CalcPostGameStats` in
  `src/code/ui/ui_atoms.c`, which still owns the `postgame` command flow and
  now calls `UI_MatchSummaryParseFromPostgame()` as one step inside that work.
- Retail parity is mixed rather than uniformly weak here. The committed
  `uix86.dll` corpus already promotes the `postgame` console-command target as
  `UI_CalcPostGameStats`, but that retail helper still reads like the older
  best-score / postgame-file core. The dedicated `matchSummary` cache and its
  feeder-facing row materialization remain primarily current-tree/source-backed
  unless stronger retail-only anchors appear later.

## Hard Layout Facts

- Target layout is 32-bit x86: `int`, `qboolean`, `team_t`, and pointers are
  `4` bytes.
- `MAX_NAME_LENGTH = 32`.
- `MAX_CLIENTS = 64`.
- `MAX_MATCH_SUMMARY_PLAYERS` is an alias of `MAX_CLIENTS`, so each cached
  player-list slab stores `64` entries.
- Current x86 sizes are:
  - `sizeof(uiMatchPlayerInfo_t) = 0x40`
  - `sizeof(uiMatchPlayerList_t) = 0x1004`
  - `sizeof(uiMatchSummaryCache_t) = 0x3024`
- The three player-list slabs inside `uiMatchSummaryCache_t` are tightly packed:
  - `endOfMatch` at `0x0018`
  - `redTeam` at `0x101C`
  - `blueTeam` at `0x2020`

## `uiMatchPlayerInfo_t`

Current x86 size: `0x40`

This is one cached scoreboard row built from the `postgame` player triples plus
the corresponding `CS_PLAYERS + clientNum` configstring.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x00` | `clientNum` | `int` | Client slot index from the `postgame` payload. Used to fetch `CS_PLAYERS + clientNum`, exposed again through feeder column `4`, and retained as the stable row identity. |
| `0x04` | `team` | `team_t` | Team token parsed from the player configstring key `"t"`. Used to split rows into the red/blue sub-lists and to format feeder column `3` through `UI_MatchSummaryTeamString`. |
| `0x08` | `rank` | `int` | Raw rank value from the `postgame` payload. Exposed through feeder column `2`. |
| `0x0C` | `score` | `int` | Raw score value from the `postgame` payload. Exposed through feeder column `1`. |
| `0x10` | `name` | `char[MAX_NAME_LENGTH]` | Clean display name copied from configstring key `"n"` or synthesized as `Player %i` when absent. `Q_CleanStr` normalizes it before the feeder returns the string. |
| `0x30` | `country` | `char[16]` | Validated ISO-style country code copied from configstring key `"country"`. Exposed through feeder column `0`. |

## `uiMatchPlayerList_t`

Current x86 size: `0x1004`

This is a bounded cached row list. The same layout is reused for the overall
end-of-match standings and the red/blue team subsets.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x00` | `entries` | `uiMatchPlayerInfo_t[MAX_MATCH_SUMMARY_PLAYERS]` | Fixed-capacity row store. `UI_MatchSummaryAppend` copies a full `uiMatchPlayerInfo_t` into `entries[entryCount]` when capacity remains. |
| `0x1000` | `entryCount` | `int` | Number of valid rows currently stored. Guarded against `MAX_MATCH_SUMMARY_PLAYERS` in `UI_MatchSummaryAppend`, returned by `UI_FeederCount`, checked by `UI_FeederItemText`, and used to gate row-selection updates in `UI_FeederSelection`. |

`0x1000 = 64 * sizeof(uiMatchPlayerInfo_t)`, so there is no padding between the
entry array and `entryCount`.

## `uiMatchSummaryCache_t`

Current x86 size: `0x3024`

This is the top-level cache embedded at `uiInfo.matchSummary`. It stores both
small match metadata and the three materialized player-list views consumed by
the end-of-match feeders.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x00` | `valid` | `qboolean` | Overall cache-validity latch. `UI_MatchSummaryParseFromPostgame` sets it true only when `endOfMatch.entryCount > 0`, and `UI_MatchSummaryListForFeeder` refuses all match-summary feeders while it is false. |
| `0x04` | `totalClients` | `int` | Player-triple count parsed from `UI_Argv(1)`. Used as the loop bound when unpacking the `postgame` payload. No later consumer was found in the current tree. |
| `0x08` | `localClientNum` | `int` | Local player slot parsed from `UI_Argv(2)`. Structurally retained in the cache, but no current reader was found. |
| `0x0C` | `redScore` | `int` | Team-red score parsed from `UI_Argv(11)`. Stored in the cache for match-summary consumers, but no direct reader was found in the current tree; the older postgame cvar update path in `ui_atoms.c` separately tracks the same payload. |
| `0x10` | `blueScore` | `int` | Team-blue score parsed from `UI_Argv(12)`. Same ownership story as `redScore`. |
| `0x14` | `matchTimeSeconds` | `int` | Match duration in seconds, derived from `UI_Argv(13) / 1000`. Stored with the summary metadata, but no current reader was found. |
| `0x18` | `endOfMatch` | `uiMatchPlayerList_t` | Full postgame player list in payload order. In the current UI tree it feeds `FEEDER_MATCHSUMMARY_END` and also the compatibility aliases `FEEDER_ENDSCOREBOARD` / `FEEDER_SCOREBOARD`, but the committed retail scoreboard feeder family is owned by cgame rather than `uix86.dll`. |
| `0x101C` | `redTeam` | `uiMatchPlayerList_t` | Red-team subset built from rows whose parsed `team` is `TEAM_RED`. In the current UI tree it feeds `FEEDER_MATCHSUMMARY_RED` and the compatibility aliases `FEEDER_REDTEAM_STATS` / `FEEDER_REDTEAM_LIST`, while retail ownership of those scoreboard feeders sits on the cgame side. |
| `0x2020` | `blueTeam` | `uiMatchPlayerList_t` | Blue-team subset built from rows whose parsed `team` is `TEAM_BLUE`. In the current UI tree it feeds `FEEDER_MATCHSUMMARY_BLUE` and the compatibility aliases `FEEDER_BLUETEAM_STATS` / `FEEDER_BLUETEAM_LIST`, while retail ownership of those scoreboard feeders sits on the cgame side. |

The struct ends immediately after `blueTeam.entryCount`, so:

- `0x3024 = 0x18 + 3 * sizeof(uiMatchPlayerList_t)`
- there is no trailing padding on the current x86 layout

## Current Data Flow

The current tree uses this cache in six stages:

1. `UI_ConsoleCommand` still dispatches the `postgame` command into
   `UI_CalcPostGameStats`, matching the committed retail `uix86.dll` command
   path.
2. `UI_CalcPostGameStats` preserves the retail-aligned postgame core
   (best-score file load/save, bonus computation, `ui_score*` cvar updates, and
   `UI_ShowPostGame`) and now calls `UI_MatchSummaryParseFromPostgame()` as a
   Quake Live-compatible sidecar before that older flow finishes.
3. `UI_ResetMatchSummaryCache` zeroes the entire `uiInfo.matchSummary` block
   and also resets `uiInfo.currentMatchSummaryEnd`,
   `uiInfo.currentMatchSummaryRed`, and `uiInfo.currentMatchSummaryBlue`.
4. `UI_MatchSummaryParseFromPostgame` decodes the `postgame` command payload,
   fills the metadata header, clears the three lists, builds one
   `uiMatchPlayerInfo_t` per valid client, and appends that row into the full
   list plus the matching team subset.
5. `UI_MatchSummaryListForFeeder` converts a feeder ID into one of the three
   cached lists, but only while `valid` is true.
6. `UI_FeederCount`, `UI_FeederItemText`, and `UI_FeederSelection` expose the
   cached rows to menu scripts, including the separate selection cursors for
   the end-of-match, red-team, and blue-team match-summary feeders plus the
   current UI-side compatibility aliases for scoreboard-style lists.

## Retail Core Versus Current Sidecar

The committed retail evidence is strong enough to bound what is and is not
already retail-backed:

- `UI_ConsoleCommand` in retail dispatches the literal `"postgame"` command
  directly into the already-promoted `UI_CalcPostGameStats`.
- Retail `UI_CalcPostGameStats` still shows the older per-map
  `games/%s_%i.game` file path, the same `UI_Argv(3..14)` stat unpacking used
  by the current source, the same `ui_matchStartTime` / `g_spSkill` flow, the
  same cvar restore band, and the same `UI_SetBestScores` tail.
- The retail asset tree definitely consumes the scoreboard feeders themselves:
  `assets/quakelive/baseq3/ui/end_scoreboard_*.menu`,
  `endscorenoteam.menu`, `endscoreteam.menu`, and the
  `ingame_scoreboard_*.menu` family all reference `FEEDER_SCOREBOARD`,
  `FEEDER_REDTEAM_LIST`, `FEEDER_BLUETEAM_LIST`, `FEEDER_REDTEAM_STATS`, or
  `FEEDER_BLUETEAM_STATS`.
- Those scoreboard feeders no longer read as unresolved `uix86.dll` ownership.
  The retail menu assets themselves include comments such as
  `CG_FeederSelection in cg_main.c`, the current `cg_main.c` assigns
  `CG_FeederCount`, `CG_FeederItemImage`, `CG_FeederItemText`, and
  `CG_FeederSelection` into `cgDC`, and the committed cgame mapping already
  promotes that feeder bridge. The scoreboard/team-list family is therefore a
  cgame/HUD ownership seam, not a remaining UI-DLL seam.
- The committed retail `uix86.dll` feeder callbacks also stop short of that
  scoreboard family. `UI_FeederCount` and `UI_FeederItemText` show committed
  retail branches for the older UI feeder set, but not for
  `FEEDER_SCOREBOARD`, `FEEDER_ENDSCOREBOARD`, `FEEDER_REDTEAM_STATS`, or
  `FEEDER_BLUETEAM_STATS`.
- No committed `uix86.dll` HLIL string was found for `matchSummary`,
  `FEEDER_MATCHSUMMARY_END`, `FEEDER_MATCHSUMMARY_RED`,
  `FEEDER_MATCHSUMMARY_BLUE`, or the newer row-cache helper names in the
  current source tree.

That means the current `matchSummary` cache is best understood as a
Quake Live-compatible reconstruction layered inside a retail-backed
`UI_CalcPostGameStats` command path. The retail scoreboard/team feeder family
already has a stronger home in the cgame `cgDC` bridge, while any direct
UI-owned `matchSummary`-style feeder layer beyond `postgame ->
UI_CalcPostGameStats` remains unpromoted in the committed `uix86.dll` map.

## Open Questions

1. Determine whether retail ever exposed any direct UI-owned
   `matchSummary`-style feeder or row cache beyond the older
   `UI_CalcPostGameStats` postgame core, or whether the current
   `matchSummary` family should remain documented as a compatibility-only
   staging layer now that the scoreboard/team feeder family is tied to cgame.
2. Determine whether `localClientNum`, `redScore`, `blueScore`, and
   `matchTimeSeconds` ever feed script/native UI paths directly in retail, or
   whether they are compatibility carry-overs currently retained only for
   future scoreboard work. The separate top-level timing slots
   `showPostGameTime` and `startPostGameTime` no longer look like live gaps:
   they are already present in the older Team Arena `uiInfo_t` baseline and no
   reader/writer has been found there or in the current tree.
