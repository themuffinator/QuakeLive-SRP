# Quake Live Steam Host Mapping Round 07

## Scope

This round focuses on the Steam lobby and social browser surface that sits immediately after the server-browser methods in the JS dispatch table.

The strongest new mapping seam combines three signals:

- the public JS method table at `data_55c008`
- the dispatcher bodies in the `00432165` to `00432616` range
- the Steam lobby helper cluster around `sub_4649B0` through `sub_465630`

I kept the same evidence sources as in earlier rounds:

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- `references/hlil/quakelive/quakelive_steam.exe/`

## Lobby Wrapper Surface

Five previously unnamed helpers can now be promoted, and one older tentative alias needs to be corrected.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4649B0` (`0x004649B0`) | `SteamLobby_CreateLobby` | Observed | Checks Steam client init, then calls `SteamMatchmaking()->vtable[0x34]` with lobby type `2` and `steam_maxLobbyClients`. The callback path at `sub_464BF0` publishes `lobby.%s.create` / `lobby.error` for the resulting request. |
| `sub_465630` (`0x00465630`) | `SteamLobby_JoinLobby` | Observed | Parses a decimal SteamID string with `sscanf("%llu", ...)` and forwards the resulting 64-bit ID into `SteamMatchmaking()->vtable[0x38]`. |
| `sub_464B10` (`0x00464B10`) | `SteamLobby_SetLobbyServer` | Observed | Validates the cached current lobby, fetches the local SteamID, reads the lobby owner through `SteamMatchmaking()->vtable[0x8C]`, and only when the local user owns the lobby does it call `SteamMatchmaking()->vtable[0x74]` with the supplied server fields. The JS method table exposes the matching public surface as `SetLobbyServer`. |
| `sub_464BB0` (`0x00464BB0`) | `SteamLobby_ShowInviteOverlay` | Observed | Validates the cached current lobby and then calls `SteamFriends()->vtable[0x84]` with that lobby ID. The method-table name `ShowInviteOverlay` matches the wrapper-level behavior exactly. |
| `sub_464AC0` (`0x00464AC0`) | `SteamLobby_SayLobby` | Observed | Computes the string length manually and forwards the current lobby plus the chat payload into `SteamMatchmaking()->vtable[0x68]`. The public JS table exposes the exact surface as `SayLobby`. |

### Corrected read

`sub_464AC0` was previously carried as `SteamLobby_SetData`. The retail HLIL does not support that interpretation: the wrapper walks the outgoing text to compute `strlen + 1` and sends the bytes through the Steam matchmaking chat-message slot, which is a lobby-chat path, not a key/value lobby-data update.

## Supporting Lobby State

The surrounding state use now reads cleanly enough to explain the wrapper cluster.

1. `data_e30338` is initialized from cvar `steam_maxLobbyClients` at `00465887`, and `sub_4649B0` reads `*(data_e30338 + 0x30)` as the requested lobby size.
2. `data_e3033c` / `data_e30340` hold the cached current lobby SteamID. `sub_4649E0` clears that cached pair after leaving a lobby, while `sub_464D90` replaces it when a new lobby enter succeeds.
3. `sub_464540` is a bounded `CSteamID`-style validity check over the cached lobby ID and is used by `sub_464B10`, `sub_464BB0`, and the lobby-enter callback path before replacing an old lobby. I am still leaving it unnamed because the helper is one layer lower than the public lobby surface and the current evidence does not prove a stable retail symbol name.

## Inlined Social JS Methods

Not every public JS method in this area has its own helper function. Three notable social methods are still implemented inline inside the main dispatcher:

| Dispatcher body | Public surface | Observed role |
| --- | --- | --- |
| `004322A5` to `00432348` | `RequestUserStats` | Parses a decimal SteamID string and calls `SteamUserStats()->vtable[0x40]` directly. |
| `00432351` to `0043244C` | `ActivateGameOverlayToUser` | Parses the dialog string plus target SteamID and calls `SteamFriends()->vtable[0x74]` directly. |
| `00432459` to `00432616` | `Invite` | Parses a target SteamID, then either invites into the current lobby through `SteamMatchmaking()->vtable[0x40]` or, in the Steam P2P path, builds a `+connect` string and calls `SteamFriends()->vtable[0xC4]` to invite directly into game. |

Those flows are useful for parity notes, but because they are inlined into the dispatcher rather than owned by standalone helpers, I did not add new symbol aliases for them in this round.

## Method-Table Evidence

The public JS table at `data_55c008` exposes the relevant lobby/social surfaces in one contiguous block:

- `CreateLobby`
- `LeaveLobby`
- `JoinLobby`
- `SetLobbyServer`
- `ShowInviteOverlay`
- `SayLobby`
- `RequestUserStats`
- `GetFriendList`
- `ActivateGameOverlayToUser`
- `Invite`

That table is what makes the wrapper-level names above stable instead of merely generic Steam API guesses.

## New High-Confidence Aliases Added This Round

- `sub_4649B0`
- `sub_464AC0` corrected to `SteamLobby_SayLobby`
- `sub_464B10`
- `sub_464BB0`
- `sub_465630`

## Open Questions

1. `sub_464540` is now tightly bounded as a cached-lobby SteamID validity gate, but I am still leaving it unnamed until I can tie it to a stable retail naming pattern instead of only to its bitfield behavior.
2. The JS method table includes `GetFriendList`, but the nearby dispatcher path still needs one more pass before it can be promoted with confidence.
3. `sub_462A50` and `sub_462EB0` remain the main browser-worker leftovers from Round 06. They are behaviorally bounded, but this round stayed on the cleaner lobby/social seam rather than forcing those internal names early.
