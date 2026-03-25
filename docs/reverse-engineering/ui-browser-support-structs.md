# UI Browser Support Struct Layouts

This note maps the small browser- and catalog-side helper structs that sit
under `uiInfo_t`: `serverFilter_t`, `pinglist_t`, `serverStatus_t`,
`pendingServer_t`, `pendingServerStatus_t`, `serverStatusInfo_t`, and
`modInfo_t`.

These records are structurally stable across the Team Arena baseline and the
current Quake Live-compatible tree. The strongest retail anchors come from the
already-promoted browser/status functions in `uix86.dll`, while a few of the
older ping-scheduler fields are only weakly exercised in the current tree and
are best explained by the preserved Team Arena-era browser logic.

## Method

- Layout facts come from local x86 `sizeof` and `offsetof` probes compiled with
  `clang -m32 -target i686-pc-windows-msvc` against
  `src/code/ui/ui_local.h`.
- Legacy comparison comes from the Team Arena-era
  `assets/quake3/src/code/ui/ui_local.h`.
- Current member roles were cross-checked against the browser and feeder owners
  in `src/code/ui/ui_main.c`.
- Retail parity is strongest for the already-mapped `uix86.dll` helpers
  `UI_BuildServerDisplayList`, `UI_SortServerStatusInfo`,
  `UI_GetServerStatusInfo`, `UI_BuildFindPlayerList`,
  `UI_BuildServerStatus`, `UI_DrawServerRefreshDate`, and
  `UI_DrawServerMOTD`.
- The weak browser scheduler slots in `serverStatus_t` and `pinglist_t` were
  further cross-checked against the preserved classic browser path in
  `assets/quake3/src/code/q3_ui/ui_servers2.c`.

## Hard Layout Facts

- Target layout is 32-bit x86: pointers, handles, and `qboolean` slots are
  `4` bytes.
- All seven requested structs keep the same x86 size and member ordering as the
  Team Arena baseline:
  - `sizeof(serverFilter_t) = 0x8`
  - `sizeof(pinglist_t) = 0x44`
  - `sizeof(serverStatus_t) = 0x2CDC`
  - `sizeof(pendingServer_t) = 0x8C`
  - `sizeof(pendingServerStatus_t) = 0x8C4`
  - `sizeof(serverStatusInfo_t) = 0xD04`
  - `sizeof(modInfo_t) = 0x8`
- `serverStatus_t` is the only large aggregate here. Its top-level bands are:
  - legacy ping scheduler: `0x000-0x8A3`
  - live browser display cache: `0x8A4-0x28BB`
  - selected-server preview and MOTD state: `0x28BC-0x2CDB`

## `serverFilter_t`

Current x86 size: `0x8`

This is the static filter-table row type used by `serverFilters[]` in
`ui_main.c`.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x00` | `description` | `const char *` | Human-readable filter label shown by the server-filter ownerdraws. |
| `0x04` | `basedir` | `const char *` | Expected `game`/basedir token. `UI_BuildServerDisplayList` compares this against the server info string when `ui_serverFilterType > 0`. |

## `pinglist_t`

Current x86 size: `0x44`

This is a single outstanding ping-query slot. In the current Quake Live tree
the engine-facing ping queue is mostly handled through `trap_LAN_ResetPings`
and `trap_LAN_UpdateVisiblePings`, but the Team Arena-era `ArenaServers_DoRefresh`
path still shows the exact original intent of this record.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x00` | `adrstr` | `char[MAX_ADDRESSLENGTH]` | Ping target address. The legacy browser scheduler used an empty first byte as the free-slot marker. |
| `0x40` | `start` | `int` | Dispatch timestamp for timeout and stale-ping detection. |

## `serverStatus_t`

Current x86 size: `0x2CDC`

This record mixes three levels of browser state: the old ping scheduler, the
live visible-server display cache, and the currently selected server's preview
and MOTD scroll state.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x0000` | `pingList` | `pinglist_t[MAX_PINGREQUESTS]` | Legacy outstanding-ping slots. The old browser scheduler used this to track active `ping` commands and their start times. |
| `0x0880` | `numqueriedservers` | `int` | Legacy count of servers currently under ping/query consideration. Weak in the current tree, but explicit in the old `ArenaServers_DoRefresh` path. |
| `0x0884` | `currentping` | `int` | Legacy next server index to issue a ping against. Weak in the current tree; explicit in the old browser scheduler. |
| `0x0888` | `nextpingtime` | `int` | Legacy 10 Hz throttle for issuing another burst of ping requests. Weak in the current tree. |
| `0x088C` | `maxservers` | `int` | Legacy cap for the active server source (local, global, favorites, MPlayer). Weak in the current tree. |
| `0x0890` | `refreshtime` | `int` | Next browser refresh gate. `UI_BuildServerDisplayList`, `UI_DoServerRefresh`, and `UI_StartServerRefresh` all use this timer. |
| `0x0894` | `numServers` | `int` | Legacy total-server-count mirror. Structurally present, but the current tree does not expose an active owner. |
| `0x0898` | `sortKey` | `int` | Active browser sort column. Used by `UI_ServersQsortCompare`, `UI_ServersSort`, and `UI_BinaryServerInsertion`. |
| `0x089C` | `sortDir` | `int` | Browser sort direction toggle. |
| `0x08A0` | `lastCount` | `int` | Legacy browser count scratch slot. Structurally present, but no active owner was found in the committed current or Team Arena trees. |
| `0x08A4` | `refreshActive` | `qboolean` | Refresh-in-progress latch used by `UI_DrawServerRefreshDate`, `UI_StopServerRefresh`, `UI_DoServerRefresh`, and `UI_StartServerRefresh`. |
| `0x08A8` | `currentServer` | `int` | Selected visible-server row. Used when previewing, connecting to, or requesting status for a server. |
| `0x08AC` | `displayServers` | `int[MAX_DISPLAY_SERVERS]` | Sorted visible-server index table exposed through `FEEDER_SERVERS`. |
| `0x28AC` | `numDisplayServers` | `int` | Number of valid entries in `displayServers[]`. |
| `0x28B0` | `numPlayersOnServers` | `int` | Aggregate visible-player count across the current display list. |
| `0x28B4` | `nextDisplayRefresh` | `int` | Next time `UI_BuildServerDisplayList` may rebuild the visible list. |
| `0x28B8` | `nextSortTime` | `int` | Legacy sort-throttle scratch slot. Structurally present, but no active current owner was found. |
| `0x28BC` | `currentServerPreview` | `qhandle_t` | Registered levelshot shader for the selected server. |
| `0x28C0` | `currentServerCinematic` | `int` | Active cinematic handle for the selected server preview, or a negative sentinel when inactive. |
| `0x28C4` | `motdLen` | `int` | Length of the active MOTD string. `UI_BuildServerDisplayList` updates it when `cl_motdString` changes. |
| `0x28C8` | `motdWidth` | `int` | MOTD scroll initialization sentinel/cache. `UI_BuildServerDisplayList` sets it to `-1` when the MOTD changes, and `UI_DrawServerMOTD` re-seeds the paint state from that marker. |
| `0x28CC` | `motdPaintX` | `int` | Primary X position of the visible MOTD segment. |
| `0x28D0` | `motdPaintX2` | `int` | Secondary wrapped-segment X position, or `-1` when no wrapped segment is active. |
| `0x28D4` | `motdOffset` | `int` | Character offset into `motd[]` for the scrolled text window. |
| `0x28D8` | `motdTime` | `int` | Next scroll tick deadline for `UI_DrawServerMOTD`. |
| `0x28DC` | `motd` | `char[MAX_STRING_CHARS]` | Cached MOTD string loaded from `cl_motdString`, with `"Welcome to Team Arena!"` as the fallback text. |

## `pendingServer_t`

Current x86 size: `0x8C`

This is a single pending find-player status probe.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x00` | `adrstr` | `char[MAX_ADDRESSLENGTH]` | Target server address for the outstanding status probe. |
| `0x40` | `name` | `char[MAX_ADDRESSLENGTH]` | Cached hostname copied from the server info string so results can be displayed without another lookup. |
| `0x80` | `startTime` | `int` | Probe dispatch time used for timeout recycling in `UI_BuildFindPlayerList`. |
| `0x84` | `serverNum` | `int` | Legacy server-index scratch slot. Structurally present, but the current tree does not actively write it. |
| `0x88` | `valid` | `qboolean` | Occupancy flag for the slot. `UI_BuildFindPlayerList` reuses slots by clearing this latch. |

## `pendingServerStatus_t`

Current x86 size: `0x8C4`

This is the small fixed-capacity queue used by the asynchronous find-player
worker.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x00` | `num` | `int` | Number of display-list rows already assigned into the pending probe queue. |
| `0x04` | `server` | `pendingServer_t[MAX_SERVERSTATUSREQUESTS]` | Fixed probe-slot array used by `UI_BuildFindPlayerList`. |

## `serverStatusInfo_t`

Current x86 size: `0xD04`

This is the parsed display form of one `trap_LAN_ServerStatus` response.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x000` | `address` | `char[MAX_ADDRESSLENGTH]` | Stable copy of the queried server address, exposed as the first `Address` line in the rendered table. |
| `0x040` | `lines` | `char *[MAX_SERVERSTATUS_LINES][4]` | Parsed table of display columns. Each row stores up to four pointers into `address`, `text`, `pings`, or string literals. |
| `0x840` | `text` | `char[MAX_SERVERSTATUS_TEXT]` | Mutable raw server-status response buffer. `UI_GetServerStatusInfo` tokenizes this string in place. |
| `0xC40` | `pings` | `char[MAX_CLIENTS * 3]` | Inline storage for the synthetic player row-number strings written by `UI_GetServerStatusInfo`. |
| `0xD00` | `numLines` | `int` | Number of valid rows in `lines[][]`. |

## `modInfo_t`

Current x86 size: `0x8`

This is the simplest catalog row in the set: a discovered mod directory plus an
optional description string.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x00` | `modName` | `const char *` | Mod directory token loaded by `UI_LoadMods`. Also used as the `fs_game` value when launching the selected mod. |
| `0x04` | `modDescr` | `const char *` | Human-readable mod description. `FEEDER_MODS` prefers this string and falls back to `modName` when it is empty. |

## Open Questions

1. Promote any remaining retail browser-side helpers that still sit below the
   committed naming threshold, especially if they directly explain the weak
   carry-over scheduler fields in `serverStatus_t`.
2. Revisit `serverStatus_t.lastCount`, `serverStatus_t.nextSortTime`,
   `serverStatus_t.numServers`, and `pendingServer_t.serverNum` if later retail
   evidence shows they still have active owners in the Quake Live binary.
