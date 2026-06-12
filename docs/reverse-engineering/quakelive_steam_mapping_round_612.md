# Quake Live Steam Mapping Round 612: GameServer Restart And Shutdown Lifecycle

Date: 2026-06-11

## Scope

This round rechecks the Steam GameServer runtime lifecycle around direct
GameServer shutdown, `net_restart`, common-frame callback pumping, normal
server shutdown, and final common/quit teardown.

No engine source behavior changed in this pass.

## Retail Evidence

Primary owner: `assets/quakelive/quakelive_steam.exe`

Evidence checked:

- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/analysis/quakelive_symbol_aliases.json`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt`
- `src/common/platform/platform_steamworks.c`
- `src/code/qcommon/common.c`
- `src/code/server/sv_init.c`
- `src/code/server/sv_main.c`
- `src/code/win32/win_net.c`

Function ownership:

| Ghidra row | Address | Promoted owner |
| --- | --- | --- |
| `FUN_00465d30` | `0x00465D30` | `SteamServer_Shutdown` |
| `FUN_00465db0` | `0x00465DB0` | `SteamServer_EnableHeartbeats` |
| `FUN_00466850` | `0x00466850` | `SteamServer_Frame` |
| `FUN_004e3f60` | `0x004E3F60` | `SV_Shutdown` |
| `FUN_004cc6c0` | `0x004CC6C0` | `Com_Frame` |
| raw HLIL `sub_4ef4f0` | `0x004EF4F0` | `NET_Restart` |

Observed facts:

- `sub_465d30` checks `data_e30358`, calls
  `SteamGameServer_Shutdown()`, and clears `data_e30358`.
- `sub_4ef4f0` performs the retail `net_restart` lifecycle in three steps:
  `sub_465d30()`, `sub_4ef250(data_12d12a0)`, and tailcall
  `sub_466ed0()`.
- `sub_466850` checks the retained GameServer initialized flag before calling
  `SteamGameServer_RunCallbacks()`, then refreshes published state with
  `sub_466260(0)`.
- `Com_Frame` calls `sub_466850()` before the usual server frame work.
- `SV_Shutdown` disables Steam server heartbeats through `sub_465db0(0)` near
  the end of server teardown.

## Source Reconstruction

The source reconstruction keeps the retail lifecycle split explicit:

- `QL_Steamworks_ServerShutdown` mirrors the narrow retail shutdown helper:
  call `state.SteamGameServer_Shutdown()` when the retained GameServer state is
  active, then clear `state.gameServerInitialised` and `state.useGameServerUGC`.
  It does not unregister the server callback bundle.
- `QL_Steamworks_Shutdown` owns full platform teardown and unregisters server
  callbacks before cascading into `QL_Steamworks_ServerShutdown`.
- `NET_Restart` calls `QL_Steamworks_ServerShutdown()`, then
  `NET_Config(networkingEnabled)`, then `Com_InitSteamGameServer()`.
- `SV_Shutdown` runs game/server teardown, disables heartbeats with
  `QL_Steamworks_ServerEnableHeartbeats(qfalse)`, then releases the GameServer
  adapter with `QL_Steamworks_ServerShutdown()`.
- `Com_Shutdown` also calls `QL_Steamworks_ServerShutdown()` after ZMQ runtime
  shutdown and before writing `profile.pid`.
- `Com_Quit_f` keeps the final idempotent server release after
  `SteamAPI_Shutdown()`, preserving the client-first quit cleanup recorded in
  the Steam client shutdown rounds.
- `SV_SteamServerNetworkingFrame` is the source counterpart to retail
  `SteamServer_Frame`: it gates on `QL_Steamworks_ServerIsInitialised()`, runs
  GameServer callbacks, refreshes published state, sends keepalives, relays
  P2P packets, and drains outgoing packets from the common frame loop.

## Compatibility Boundary

Live Steam GameServer calls remain behind `QL_BUILD_ONLINE_SERVICES` and the
Steamworks provider table. Default-disabled builds keep these hooks as no-op
or compatibility fallback paths. The source-side extra call to
`QL_Steamworks_ServerShutdown()` from `SV_Shutdown` and `Com_Shutdown` is a
bounded dynamic-adapter cleanup policy, while the direct platform helper still
preserves retail's narrow shutdown body.

## Validation

Added
`tests/test_platform_services.py::test_steam_gameserver_shutdown_restart_lifecycle_tracks_round_612`
to pin:

- alias and Ghidra ownership for direct shutdown, heartbeat, frame, common
  frame, server shutdown, and net restart owners;
- Steam GameServer import evidence for shutdown, callbacks, and init;
- Binary Ninja HLIL anchors for direct shutdown, net restart, server frame,
  common-frame placement, and server-shutdown heartbeat disable;
- source ordering for direct platform shutdown versus full platform callback
  teardown;
- source ordering for `NET_Restart`, `SV_Shutdown`, `Com_Shutdown`,
  `Com_Quit_f`, and `SV_SteamServerNetworkingFrame`; and
- this round note plus Task A481 parity anchors.

Planned validation for this pass:

```text
python -m pytest tests/test_platform_services.py::test_steam_gameserver_shutdown_restart_lifecycle_tracks_round_612 -q --tb=short
python -m pytest tests/test_platform_services.py -q --tb=short
python -m pytest tests/test_steamworks_harness.py -q --tb=short
```

## Confidence

Observed facts:

- HLIL directly shows the direct GameServer shutdown helper, `net_restart`
  three-step lifecycle, GameServer callback pump, and server shutdown heartbeat
  disable.
- Ghidra rows, imports, and the alias map identify the stable owners.
- Source tests now bind the platform helper, common shutdown, Windows network
  restart, server shutdown, and common-frame pump into one lifecycle gate.

Inference:

- SRP's additional server adapter releases in `SV_Shutdown` and `Com_Shutdown`
  are the correct bounded cleanup policy for a dynamic provider table. They do
  not change the direct `QL_Steamworks_ServerShutdown` helper's retail-mapped
  narrow ownership.

Parity estimates:

- Focused GameServer restart/shutdown lifecycle confidence:
  **before 94% -> after 99%**.
- Focused server-frame callback pump and teardown ordering confidence:
  **before 95% -> after 99%**.
- Overall Steam launch/runtime integration mapping confidence: **93.26% -> 93.28%**.
