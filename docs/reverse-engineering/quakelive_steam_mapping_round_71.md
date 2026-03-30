# Quake Live Steam Host Mapping Round 71

## Scope

This round closes the remaining helper-owned Steam lobby control seam that was
left after the earlier lobby bootstrap pass, and it converts the cleanest
retail `QLWebView_PublishGameStart` Steam rich-presence write into writable
client-host source.

The evidence base stayed inside the committed corpus:

- `references/hlil/quakelive/quakelive_steam.exe/`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `docs/reverse-engineering/quakelive_steam_mapping_round_07.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_08.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_02.md`

## `sub_4649E0`: `SteamLobby_LeaveLobby`

The HLIL for `004649E0` is stable:

1. It checks the shared Steam init gate at `sub_460510()`.
2. It calls `SteamMatchmaking()->vtable[0x3C]` with the retained current lobby
   ID at `data_e3033c` / `data_e30340`.
3. It publishes `lobby.%s.left` and clears the retained lobby ID.

The writable source now reconstructs the SteamMatchmaking leave slot directly in
`src/common/platform/platform_steamworks.c` as
`QL_Steamworks_LeaveLobby( idLow, idHigh )`, pinned to
`vtable[0x3c / 4]`. The current-lobby ownership layer is still missing, so the
wrapper takes explicit lobby identity words instead of inventing new retained
state in the host.

## `sub_464B10`: `SteamLobby_SetLobbyServer`

The retail dispatcher and helper pair are also bounded cleanly:

1. The public JS dispatcher case at `004321EB` decodes two integer arguments
   and routes them into `sub_464B10`.
2. `sub_464B10` fetches the local SteamID through `SteamUser()->vtable[0x08]`.
3. It fetches the lobby owner through `SteamMatchmaking()->vtable[0x8C]`.
4. Only when the local user owns the current lobby does it call
   `SteamMatchmaking()->vtable[0x74]`.

The writable source now reconstructs that owner-gated control path as
`QL_Steamworks_SetLobbyServer( idLow, idHigh, serverIp, serverPort )` in the
shared Steamworks layer. The implementation keeps the same retail slot usage:

- `SteamUser()->vtable[0x08]`
- `SteamMatchmaking()->vtable[0x8C]`
- `SteamMatchmaking()->vtable[0x74]`

It also mirrors the retail tail-call shape by passing the lobby identity back
through the trailing game-server SteamID words.

## `sub_4F38F0`: `QLWebView_PublishGameStart`

Round 02 already bounded `004F38F0` as the retail game-start publication seam.
The part that is safest to reconstruct in the writable client host is the Steam
rich-presence status write:

1. After building the game-start payload, the retail code writes
   `SteamFriends()->vtable[0xAC]( "status", "Playing a match" )`.
2. The same function then publishes `game.start`.

The writable source now reconstructs that status transition in
`src/code/client/cl_cgame.c`:

- `CL_Steam_SetMatchRichPresence()` calls
  `QL_Steamworks_SetRichPresence( "status", "Playing a match" )`
- `CL_FirstSnapshot()` invokes that helper as soon as the first active snapshot
  lands, which is the cleanest current host-owned moment for “entered live
  play”

This does not yet reconstruct the full browser-facing `game.start` payload or
the adjacent `lanIp` write; those still belong to the unresolved webview/event
publication ownership layer.

## Verification

The updated source is covered by:

- `tests/test_steamworks_harness.py`
- `tests/test_platform_services.py`
- `tests/test_ui_menu_files.py`

Command run:

```text
python -m pytest tests/test_steamworks_harness.py tests/test_platform_services.py tests/test_ui_menu_files.py -q
```

Result:

- `59 passed`

## Outcome

This round did not add new address aliases. It consumed already-mapped
`quakelive_steam.exe` ownership in two ways:

- the Steam lobby control seam now includes writable `LeaveLobby` and
  owner-gated `SetLobbyServer` wrappers
- the first-active-snapshot path now reconstructs the retail
  `status = "Playing a match"` Steam rich-presence transition
