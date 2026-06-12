# Quake Live Steam Mapping Round 636: GameServer Utility Initialized Guards

Date: 2026-06-12

## Scope

This round maps the small GameServer utility accessors used by server stats and
local invite/connect publication, then reconstructs explicit initialized-state
guards in the SRP public wrappers. The retail anchors are
`SteamServer_GetPublicIP`, promoted from `sub_465e80`, and the
`SteamStats_Init` AppID fetch from `sub_467850`. The source boundaries are
`QL_Steamworks_ServerGetAppID`, `QL_Steamworks_ServerGetPublicIP`,
`SV_SteamStats_CreatePlayerSession`, and the local web/invite connect
publishers.

Steam launch/runtime online behavior remains behind `QL_BUILD_ONLINE_SERVICES`.
This round tightens wrapper boundaries; it does not enable live Steam services.

## Retail Evidence

- `references/analysis/quakelive_symbol_aliases.json` promotes
  `FUN_00465e80`, `sub_465E80`, and `sub_465e80` to
  `SteamServer_GetPublicIP`.
- The same alias map promotes `FUN_00467850` and `sub_467850` to
  `SteamStats_Init`.
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  records `FUN_00465e80,00465e80,18,0,unknown` and
  `FUN_00467850,00467850,454,0,unknown`.
- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
  confirms the utility dependencies through `STEAM_API.DLL!SteamGameServer`
  and `STEAM_API.DLL!SteamGameServerUtils`.
- Binary Ninja HLIL for `sub_465e80` is a direct public-IP thunk through
  `SteamGameServer()` vtable slot `0x90`.
- Binary Ninja HLIL for `sub_467850` reads the GameServer AppID through
  `SteamGameServerUtils()` vtable slot `0x24`, stores it into the stats owner,
  and later gates initial stats requests on `SteamGameServerStats()` plus
  `SteamGameServer()->BLoggedOn()`.

Observed fact: retail treats public-IP as a direct GameServer slot dispatch and
captures the server AppID during the stats owner initialization before issuing
GameServerStats requests.

Inferred mapping: SRP's public wrappers keep the retail slot mapping, but must
return `0` when the retained GameServer lane is unavailable. The explicit
`state.gameServerInitialised` guards make that compatibility boundary visible
at the wrapper entry, while the shared interface helpers still carry the
broader `state.initialised` and optional-symbol checks.

## Source Reconstruction

`src/common/platform/platform_steamworks.c` now makes the GameServer runtime
boundary explicit in both utility wrappers:

1. `QL_Steamworks_ServerGetAppID` rejects calls while
   `state.gameServerInitialised` is false.
2. It then resolves `QL_Steamworks_GetGameServerUtilsInterface` and dispatches
   slot `0x24`.
3. `QL_Steamworks_ServerGetPublicIP` rejects calls while
   `state.gameServerInitialised` is false.
4. It then resolves `QL_Steamworks_GetGameServer` and dispatches slot `0x90`.

Both wrappers retain `0` as the unavailable return value, matching existing
source callers that already treat zero AppID/public-IP values as an inert
fallback rather than live service success.

## Wiring

- `SV_SteamStats_CreatePlayerSession` stores
  `QL_Steamworks_ServerGetAppID()` into the retained stats session before the
  session lifecycle log and current-value request.
- `CL_WebView_PublishGameStart` uses `QL_Steamworks_ServerGetPublicIP()` only
  as the fallback for a local server whose LAN address cannot be discovered.
- `CL_Steam_BuildInviteConnectString` uses
  `QL_Steamworks_ServerGetPublicIP()` for non-LAN local invite commands and
  aborts the command when the wrapper returns `0`.

## Validation

Added `test_steam_gameserver_utility_public_ip_wrapper_guards_track_round_636`
to pin:

- promoted aliases and Ghidra rows for `sub_465e80` and `sub_467850`;
- the Steam GameServer and GameServerUtils imports;
- Binary Ninja slot `0x90` public-IP and slot `0x24` AppID evidence;
- wrapper initialized-state guards before interface lookup;
- source `0` fallback behavior for unavailable utility values; and
- local web/invite and server stats session wiring.

## Parity Estimate

Focused GameServer utility wrapper guard confidence:
**80% -> 99%**.

Focused Steam GameServer public-IP and AppID wiring confidence:
**92% -> 99%**.

overall Steam launch/runtime integration mapping confidence **93.74% -> 93.76%**.
