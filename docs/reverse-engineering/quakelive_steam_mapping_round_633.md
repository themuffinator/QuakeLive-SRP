# Quake Live Steam Mapping Round 633: GameServerStats Initialized Guards

Date: 2026-06-12

## Scope

This round maps the retail Steam GameServerStats request and flush lane, then
reconstructs explicit initialized-state guards in the SRP public
GameServerStats wrapper band. The primary retail owner is
`SteamStats_OnServersConnected`, promoted from `sub_467190`, with supporting
slot evidence from `SteamStats_FlushPendingValues` / `sub_4670c0`.

Steam launch/runtime online behavior remains behind `QL_BUILD_ONLINE_SERVICES`.
This round tightens wrapper fidelity; it does not enable live Steam services.

## Retail Evidence

- `references/analysis/quakelive_symbol_aliases.json` promotes `sub_467190`
  to `SteamStats_OnServersConnected` and `FUN_004670c0` to
  `SteamStats_FlushPendingValues`.
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  records the companion stats rows, including
  `FUN_004670c0,004670c0,208,0,unknown` and
  `FUN_004671d0,004671d0,256,0,unknown`.
- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
  confirms the interfaces through `STEAM_API.DLL!SteamGameServer @ 0015918a`
  and `STEAM_API.DLL!SteamGameServerStats @ 0015932c`.
- Binary Ninja HLIL for `sub_467190` first calls `SteamGameServerStats()`,
  then calls `SteamGameServer()->BLoggedOn` at vtable slot `0x20`, then
  reacquires `SteamGameServerStats()` before dispatching
  `RequestUserStats` through slot `0x00`.
- Binary Ninja HLIL for `sub_4670c0` checks the retained ready flag before
  pushing pending avg-rate, float/int stat, and store operations through
  `SteamGameServerStats()` slots `0x18`, `0x04`, and `0x24`.

Observed fact: retail GameServerStats slot dispatch happens only inside
server-owned stats-session paths that have already established the GameServer
runtime and stats interface.

Inferred mapping: SRP's `state.gameServerInitialised` mirrors the retail
GameServer runtime prerequisite, while `QL_Steamworks_GetGameServerStatsInterface`
is the source interface resolver for retail `SteamGameServerStats()`.

## Source Reconstruction

`src/common/platform/platform_steamworks.c` now makes the GameServer runtime
boundary explicit in the public GameServerStats wrappers:

1. `QL_Steamworks_ServerIsLoggedOn` rejects calls while
   `state.gameServerInitialised` is false before resolving `SteamGameServer`
   and dispatching BLoggedOn slot `0x20`.
2. `QL_Steamworks_ServerRequestUserStats` validates the Steam ID, rejects
   uninitialized GameServer state, probes `SteamGameServerStats`, checks
   `QL_Steamworks_ServerIsLoggedOn`, reacquires `SteamGameServerStats`, and
   dispatches slot `0x00`.
3. The stat-read wrappers validate their Steam ID, name, and output pointers,
   reject uninitialized GameServer state, and dispatch slots `0x08`, `0x04`,
   and `0x0c`.
4. The stat-write wrappers validate their Steam ID and stat/achievement names,
   reject uninitialized GameServer state, and dispatch slots `0x14`, `0x10`,
   `0x18`, `0x1c`, and `0x24`; this includes the final
   `QL_Steamworks_ServerStoreUserStats` store wrapper.

The shared `QL_Steamworks_GetGameServerStatsInterface` helper still retains the
broader `state.initialised`, `state.gameServerInitialised`, and
`SteamGameServerStats` checks. The new wrapper-level guards make the public
stats boundary match the retail server-owned runtime lane directly.

## Server Wiring

`src/code/server/sv_client.c` remains the stats-session owner:

- `SV_SteamStats_RequestCurrentValues` calls
  `QL_Steamworks_ServerRequestUserStats`.
- `SV_SteamStats_CreatePlayerSession` creates retained per-client sessions and
  immediately requests current values for eligible human clients.
- `SV_SteamStats_FlushPendingValues` publishes dirty int/float/avg-rate stat
  values, dirty achievements, and the final `StoreUserStats` request through
  the mapped wrappers.
- `SV_SteamServerGSStatsReceivedCallback` and
  `SV_SteamServerGSStatsStoredCallback` remain the callback owners for
  request/store completion and validation-refresh behavior.

## Validation

Added `test_steam_gameserver_stats_wrapper_guards_track_round_633` to pin:

- promoted aliases and companion Ghidra rows for the stats request/flush lane;
- Steam GameServer and GameServerStats imports;
- Binary Ninja ordering from `SteamGameServerStats()` through BLoggedOn and
  `RequestUserStats`;
- Binary Ninja flush evidence for avg-rate, float/int stat, and store slots;
- wrapper input validation before initialized-state guards;
- initialized-state guards before `QL_Steamworks_GetGameServerStatsInterface`
  or `QL_Steamworks_GetGameServer`; and
- source stats-session request and flush owners in `sv_client.c`.

## Parity Estimate

Focused GameServerStats wrapper guard confidence:
**81% -> 99%**.

Focused Steam GameServerStats request/flush wiring confidence:
**94% -> 99%**.

overall Steam launch/runtime integration mapping confidence **93.68% -> 93.70%**.
