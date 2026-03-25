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
- The parse entrypoint is also wired from `UI_SPPostgameMenu_f` in
  `src/code/ui/ui_atoms.c`, which calls `UI_MatchSummaryParseFromPostgame()`
  after unpacking the `postgame` command payload.
- Retail parity is weaker here than for the older UI subsystems. The committed
  `uix86.dll` HLIL still shows the `postgame` command dispatcher, but the
  member-level roles below are primarily current-tree/source-backed until the
  raw retail helper behind this Quake Live-compatible cache is promoted.

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
| `0x18` | `endOfMatch` | `uiMatchPlayerList_t` | Full postgame player list in payload order. Routed to `FEEDER_MATCHSUMMARY_END`, `FEEDER_ENDSCOREBOARD`, and `FEEDER_SCOREBOARD`. |
| `0x101C` | `redTeam` | `uiMatchPlayerList_t` | Red-team subset built from rows whose parsed `team` is `TEAM_RED`. Routed to `FEEDER_MATCHSUMMARY_RED`, `FEEDER_REDTEAM_STATS`, and `FEEDER_REDTEAM_LIST`. |
| `0x2020` | `blueTeam` | `uiMatchPlayerList_t` | Blue-team subset built from rows whose parsed `team` is `TEAM_BLUE`. Routed to `FEEDER_MATCHSUMMARY_BLUE`, `FEEDER_BLUETEAM_STATS`, and `FEEDER_BLUETEAM_LIST`. |

The struct ends immediately after `blueTeam.entryCount`, so:

- `0x3024 = 0x18 + 3 * sizeof(uiMatchPlayerList_t)`
- there is no trailing padding on the current x86 layout

## Current Data Flow

The current tree uses this cache in four stages:

1. `UI_ResetMatchSummaryCache` zeroes the entire `uiInfo.matchSummary` block
   and also resets `uiInfo.currentMatchSummaryEnd`,
   `uiInfo.currentMatchSummaryRed`, and `uiInfo.currentMatchSummaryBlue`.
2. `UI_MatchSummaryParseFromPostgame` decodes the `postgame` command payload,
   fills the metadata header, clears the three lists, builds one
   `uiMatchPlayerInfo_t` per valid client, and appends that row into the full
   list plus the matching team subset.
3. `UI_MatchSummaryListForFeeder` converts a feeder ID into one of the three
   cached lists, but only while `valid` is true.
4. `UI_FeederCount`, `UI_FeederItemText`, and `UI_FeederSelection` expose the
   cached rows to menu scripts, including the separate selection cursors for the
   end-of-match, red-team, and blue-team feeders.

## Open Questions

1. Promote the raw `uix86.dll` helper that owns the Quake Live-compatible
   `postgame` summary cache so these member roles can be upgraded from
   source-backed to directly retail-backed.
2. Determine whether `localClientNum`, `redScore`, `blueScore`, and
   `matchTimeSeconds` ever feed script/native UI paths directly in retail, or
   whether they are compatibility carry-overs currently retained only for
   future scoreboard work.
