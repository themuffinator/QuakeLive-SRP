# Quake Live Steam Host Mapping Round 08

## Scope

This round closes the remaining high-confidence gap in the Steam browser surface by resolving the heap-allocated `JSBrowser` server-list response object behind `data_e30334`.

The evidence chain for this pass stayed inside the committed retail corpus:

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- `references/hlil/quakelive/quakelive_steam.exe/`

The strongest new signal is the RTTI/vftable ownership at `00532A88`: the previously generic browser publishers from Round 06 are not just free helpers, they are the three callback legs of a dedicated `JSBrowser` object implementing `ISteamMatchmakingServerListResponse`.

## `JSBrowser` Server-List Response Object

The constructor at `0052AB02` allocates `0x0C` bytes, writes `JSBrowser::vftable{for ISteamMatchmakingServerListResponse}`, clears fields at `+4` and `+8`, and stores the object in `data_e30334`.

That layout now reads cleanly as:

- `+0x00`: `JSBrowser` response-object vfptr
- `+0x04`: active-refresh flag
- `+0x08`: current Steam server-list request handle

The matching vftable at `00532A88` binds:

- `sub_462A50`
- `sub_462DB0`
- `sub_462E60`

That ownership is what makes the following callback names stable rather than merely descriptive publisher labels.

### Promoted `JSBrowser` callbacks and worker

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_462A50` (`0x00462A50`) | `JSBrowser_OnServerResponded` | Observed | Called through `JSBrowser::vftable{for ISteamMatchmakingServerListResponse}`. Fetches a `gameserveritem_t`-style record from `SteamMatchmakingServers()->vtable[0x1C]` using the incoming request/index pair, validates the app ID against `SteamUtils()->GetAppID()`, then publishes `servers.details.%u_%u.response` with `name`, `numPlayers`, `maxPlayers`, `ping`, `map`, `botPlayers`, `password`, `vac`, `ip`, `port`, `id`, `steam_id`, `tags`, `gametype`, and `lastPlayed`. |
| `sub_462DB0` (`0x00462DB0`) | `JSBrowser_OnServerFailedToRespond` | Observed | The Round-06 `SteamBrowser_PublishServerDetailsFailed` read was behaviorally correct but too generic. The vftable ownership at `00532A88` shows this is the failed-response callback leg on the `JSBrowser` object. It builds `{ "id": arg1 }` and publishes `servers.details.%i.failed`. |
| `sub_462E60` (`0x00462E60`) | `JSBrowser_OnRefreshComplete` | Observed | Also owned by the same `JSBrowser` vftable. Clears the active flag at `*(arg1 + 4)` and publishes `servers.refresh.end`, which matches the Steam server-list refresh-complete role rather than only a generic publisher helper. |
| `sub_462EB0` (`0x00462EB0`) | `JSBrowser_RequestServers` | Observed | Stateful request worker for `data_e30334`. If no refresh is already active, it cancels any existing handle through `SteamMatchmakingServers()->vtable[0x18]`, sets the active flag, injects the filter pair `gamedir=baseq3`, selects one of the Steam matchmaking-server request slots (`0`, `+4`, `+8`, `+0xC`, `+0x10`) from the integer mode argument, stores the returned request handle at `+8`, and publishes `servers.refresh.start`. |

### Public wrapper separation

The browser dispatcher still reaches the public JS surface through the same wrapper trio identified in Round 06:

- `004320EF` to `sub_463090` for `RequestServers`
- `0043211D` to `sub_4630B0` for `RequestServerDetails`
- `0043215B` to `sub_462E80` for `RefreshList`

What changed in this round is the ownership model behind `RequestServers`: `sub_463090` is just the public wrapper, while `sub_462EB0` is the object-level worker that drives the actual Steam server-list request and callback state for `data_e30334`.

## Promoted Generic SteamID Helper

One previously lobby-bounded helper is now strong enough to promote generically.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_464540` (`0x00464540`) | `CSteamID_IsValid` | Observed | Checks the packed `CSteamID` account-type nibble, universe bits, account ID, and instance field with the standard Steam validity rules: valid account types only, valid universes only, non-zero account IDs for user/clan/game-server IDs, desktop-instance bounds for account type `1`, and zero instance for clan IDs. The current callsites use it for the cached lobby ID at `data_e3033c` / `data_e30340`, but the helper logic itself is generic `CSteamID` validation rather than a lobby-only rule. |

### Why this is no longer just a lobby helper

Round 07 left `sub_464540` unnamed because all observed callsites were in the lobby cluster. The bitfield rules now line up tightly enough with Steam's generic `CSteamID::IsValid` contract that the broader name is the more accurate promotion.

Current uses are still:

- `sub_464B10` before `SteamLobby_SetLobbyServer`
- `sub_464BB0` before `SteamLobby_ShowInviteOverlay`
- `sub_464D90` before replacing an existing cached lobby

## Inline `GetFriendList` State Remains Open

The dispatcher block at `0043264D` still does not justify a promoted helper alias. The current observed behavior is only:

1. optional boolean argument decode from the Awesomium array
2. writeback into `data_12d306c`

That is enough to bound the method as part of the `GetFriendList` surface from the JS table, but not enough to name a standalone function beyond the dispatcher case itself.

## New High-Confidence Aliases Added Or Corrected This Round

- `sub_462A50`
- `sub_462DB0` corrected to `JSBrowser_OnServerFailedToRespond`
- `sub_462E60` corrected to `JSBrowser_OnRefreshComplete`
- `sub_462EB0`
- `sub_464540`

## Open Questions

1. `sub_462E80` still looks like the public `RefreshList` wrapper even though its body is only the request-handle release step. I am keeping the Round-06 name because the dispatcher string table still points to that public surface, but the exact user-visible refresh semantics would benefit from one more runtime-adjacent pass.
2. The `GetFriendList` dispatcher case at `0043264D` still only exposes a boolean state toggle into `data_12d306c`; the downstream enumeration work remains to be pinned.
3. The later social/browser cases after `GetFriendList` still need one cleanup pass if we want the JS method table at `data_55C008` to be fully annotated end to end.
