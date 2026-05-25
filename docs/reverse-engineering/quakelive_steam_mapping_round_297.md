# Quake Live Steam Host Mapping Round 297

## Scope

This round reconstructs the low-level native Steam server-browser owner around
`ISteamMatchmakingServers`. It does not wire the retained client browser
fallback path over to the native owner yet; that remains a separate integration
task because the current `CL_SteamBrowser_*` code deliberately labels
friends/history as source-browser compatibility behavior.

Evidence order:

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- `references/analysis/quakelive_symbol_aliases.json`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt`

## Observed Facts

The owning binary is still `quakelive_steam.exe`; the Ghidra metadata reports
5473 functions, 351 imports, and 4377 promoted analysis symbols. The Steam API
import table includes `STEAM_API.DLL!SteamMatchmakingServers @ 0015928c`, and
the HLIL import data repeats the imported name `SteamMatchmakingServers`.

The alias map promotes the browser owners used in this pass:

- `sub_461F70` -> `JSBrowserDetails_RequestServerDetails`
- `sub_462A50` -> `JSBrowser_OnServerResponded`
- `sub_462E80` -> `SteamBrowser_RefreshList`
- `sub_462EB0` -> `JSBrowser_RequestServers`

`JSBrowserDetails_RequestServerDetails` stores the requested IP/port, builds
the `"%u_%i"` detail id, and issues detail probes through three
`SteamMatchmakingServers` vtable slots:

| Vtable offset | Inferred API | Evidence |
| --- | --- | --- |
| `0x34` | `PingServer` | Called with the server IP, port, and the response object at `this + 8`. |
| `0x3c` | `ServerRules` | Called immediately after ping with the response object at `this + 0`. |
| `0x38` | `PlayerDetails` | Called last with the response object at `this + 4`. |

The order is notable: retail starts ping, then rules, then players. The harness
now pins that order instead of sorting it into the public SDK declaration order.

`JSBrowser_OnServerResponded` uses vtable slot `0x1c` to read one server row
from a retained request/index pair. The generated browser payload includes
`name`, `numPlayers`, `maxPlayers`, `ping`, `map`, `botPlayers`, `password`,
`vac`, `ip`, `port`, `id`, `steam_id`, `tags`, `gametype`, and `lastPlayed`.
This round does not promote the full `gameserveritem_t` layout; it only adds
the low-level row pointer helper needed before that source-level struct can be
introduced safely.

`SteamBrowser_RefreshList` checks the retained request handle and dispatches
slot `0x24`, matching `RefreshQuery`.

`JSBrowser_RequestServers` releases an existing request through slot `0x18`,
builds one filter pair (`"gamedir" = "baseq3"`), reads `SteamUtils()->GetAppID`,
and dispatches the list request by mode:

| Retail mode | Slot | Inferred API | Filter use |
| --- | --- | --- | --- |
| default / `0` | `0x00` | `RequestInternetServerList` | `gamedir=baseq3` |
| `1` | `0x04` | `RequestLANServerList` | no filter array |
| `2` | `0x08` | `RequestFriendsServerList` | `gamedir=baseq3` |
| `3` | `0x0c` | `RequestFavoritesServerList` | `gamedir=baseq3` |
| `4` | `0x10` | `RequestHistoryServerList` | `gamedir=baseq3` |

After the request handle is stored, the browser publishes
`"servers.refresh.start"`.

The vtable data in HLIL part 06 supports the owner assignments: the
`JSBrowser` vtable contains server-list response callbacks at `0x00532a88`,
and the `JSBrowserDetails` vtables contain ping, players, and rules response
callback owners at `0x00532b0c`, `0x00532b18`, and `0x00532b28`.

## Source Reconstruction

The platform wrapper now loads the optional `SteamMatchmakingServers` import and
exposes a small native server-browser surface:

- `QL_Steamworks_HasServerBrowserInterface`
- `QL_Steamworks_RequestServerList`
- `QL_Steamworks_GetServerListDetails`
- `QL_Steamworks_RefreshServerListRequest`
- `QL_Steamworks_ReleaseServerListRequest`
- `QL_Steamworks_RequestServerDetails`

The wrapper keeps the online-services boundary intact. When
`QL_BUILD_STEAMWORKS` is disabled, every new entry point compiles to a harmless
stub. When enabled, the wrapper dispatches exactly the observed retail vtable
offsets listed above and keeps the filter key/value buffer local to the request
call, matching the HLIL stack-local filter construction.

The Steamworks harness gained a `SteamMatchmakingServers` mock interface with
the same vtable slots. The Python harness test covers disabled stubs, all five
list modes, filter construction, app id forwarding, request detail lookup,
refresh/release handles, and the retail detail-probe order
`PingServer -> ServerRules -> PlayerDetails`.

## Open Questions

- The source-level layout for the server-list row returned by slot `0x1c`
  remains unpromoted. The HLIL field offsets are visible, but this round only
  needed the retained pointer handoff.
- The client browser still publishes friends/history through the current
  source-browser compatibility lane. A future task can replace or bridge that
  lane with the native wrapper, but it should update the compatibility telemetry
  and tests deliberately.
- Canceling individual ping/player/rules query handles is not reconstructed in
  this pass. The observed request path stores the handles, but the immediate
  source need was request creation and callback routing.

## Parity Estimate

Before this round, the native Steam server-browser wrapper layer was roughly
20% reconstructed: the evidence and compatibility labels existed, but there was
no callable `ISteamMatchmakingServers` wrapper. After this round, the scoped
wrapper layer is about 70% reconstructed. The remaining 30% is mostly the
server-row struct promotion, detail-query cancellation, and client browser
integration.

For the broader Steamworks subsystem, this moves the estimate from about 63% to
66% parity with the observed retail Steamworks surface. It is a meaningful
server-browser advance, but not a claim of full Steamworks or UI browser parity.
