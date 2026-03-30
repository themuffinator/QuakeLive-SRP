# Quake Live Steam Host Mapping Round 72

## Scope

This round closes the cleanest remaining server-owned Steam host seam that was
still left in writable source after the earlier lobby and rich-presence passes:

- the direct Steam game-server heartbeat/public-IP wrappers from round 04
- the retail `SteamServer_Frame` owner path in the main server frame loop

The evidence base for this pass stayed inside the committed corpus:

- `references/hlil/quakelive/quakelive_steam.exe/`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `docs/reverse-engineering/quakelive_steam_mapping_round_01.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_04.md`
- `src/code/server/sv_main.c`
- `src/common/platform/platform_steamworks.c`

## `sub_465DB0`: `SteamServer_EnableHeartbeats`

Round 04 already bounded `00465DB0` as the Steam game-server heartbeat toggle:

1. It checks the shared Steam game-server init gate.
2. It calls `SteamGameServer()->vtable[0x9C / 4]` with a boolean enable flag.
3. It updates the retained heartbeat timestamp used by adjacent server helpers.

The writable source now reconstructs the direct interface wrapper as
`QL_Steamworks_ServerEnableHeartbeats( enable )` in
`src/common/platform/platform_steamworks.c`, pinned to
`vtable[0x9c / 4]`.

This round keeps the wrapper host-owned and does not invent the unresolved
retained timestamp/state bookkeeping that still belongs to the broader missing
Steam game-server init/shutdown tranche.

## `sub_465E80`: `SteamServer_GetPublicIP`

The HLIL for `00465E80` is stable and minimal:

1. It checks the same shared server-init gate.
2. It tail-calls `SteamGameServer()->vtable[0x90 / 4]`.

The writable source now reconstructs that wrapper directly as
`QL_Steamworks_ServerGetPublicIP()` in the shared Steamworks layer, pinned to
`vtable[0x90 / 4]`.

This closes the mapped Steam public-IP query seam that the retail
`QLWebView_PublishGameStart` path uses on dedicated/public-server publication
paths, even though the browser-owned `game.start` publisher itself remains
outside the writable host ownership restored in this round.

## `sub_466850`: `SteamServer_Frame`

Round 01 already identified `00466850` as the retail Steam server frame owner:

1. `SteamGameServer_RunCallbacks`
2. periodic published-state / keepalive maintenance
3. Steam P2P relay work
4. outgoing packet drain work

The repo already had the helper body as `SV_SteamServerNetworkingFrame()`, but
`SV_Frame()` was still incorrectly calling the client-side
`QL_Steamworks_RunCallbacks()` path directly instead of routing through the
server-owned helper.

This round fixes that ownership mismatch:

- `SV_Frame()` now calls `SV_SteamServerNetworkingFrame()`
- the helper continues to own
  `QL_Steamworks_RunServerCallbacks()`,
  `SV_SteamServerSendKeepAlive()`,
  `SV_SteamServerRelayP2PPackets()`, and
  `SV_SteamServerDrainOutgoingPackets()`

That restores the retail server/main-loop ownership shape without inventing the
larger missing published-state refresh/auth-drain tranche that still belongs to
the unresolved `SteamServer_UpdatePublishedState` and adjacent game-server
callback ownership.

## Verification

The updated source is covered by:

- `tests/test_steamworks_harness.py`
- `tests/test_platform_services.py`
- `tests/test_ui_menu_files.py`

Command run:

```text
python -m pytest tests/test_steamworks_harness.py tests/test_platform_services.py tests/test_ui_menu_files.py -q
```

## Outcome

This round did not add new address aliases. It consumed already-mapped
`quakelive_steam.exe` ownership in two ways:

- the shared Steamworks layer now includes writable
  `ServerEnableHeartbeats` and `ServerGetPublicIP` wrappers at the mapped
  `SteamGameServer` slots
- the server main loop now routes through the existing
  `SV_SteamServerNetworkingFrame()` helper, matching the retail
  `SteamServer_Frame` ownership instead of pumping the client callback path
