# Quake Live Steam Mapping Round 634: GameServer P2P Accept Initialized Guard

Date: 2026-06-12

## Scope

This round maps the retail server-side Steam P2P session accept callback and
reconstructs an explicit initialized-state guard in the SRP public accept
wrapper. The retail owner is `SteamServerCallbacks_OnP2PSessionRequest`,
promoted from `sub_465b70`. The source boundaries are
`QL_Steamworks_ServerAcceptP2PSession`,
`SV_SteamServerP2PSessionRequestCallback`, and the server callback bootstrap
binding.

Steam launch/runtime online behavior remains behind `QL_BUILD_ONLINE_SERVICES`.
This round tightens wrapper fidelity; it does not enable live Steam services.

## Retail Evidence

- `references/analysis/quakelive_symbol_aliases.json` promotes
  `FUN_00465b70`, `sub_465B70`, and `sub_465b70` to
  `SteamServerCallbacks_OnP2PSessionRequest`.
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  records `FUN_00465b70,00465b70,146,0,unknown`.
- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
  confirms the server-side P2P networking dependency through
  `STEAM_API.DLL!SteamGameServerNetworking @ 001592a6`.
- Binary Ninja HLIL for `sub_465b70` scans active client slots, matches the
  incoming low/high SteamID pair, and only then calls
  `SteamGameServerNetworking()` before dispatching vtable slot `0x0c`.
- Binary Ninja HLIL for the server callback bundle constructor wires
  `sub_465b70` into the server-side `P2PSessionRequest_t` callback entry.

Observed fact: retail accepts server-side P2P sessions only from the server
callback owner after a live active-client match, and the accept dispatch uses
the GameServer networking interface at slot `0x0c`.

Inferred mapping: SRP's `state.gameServerInitialised` mirrors the retail
server callback/runtime prerequisite, while
`QL_Steamworks_GetGameServerNetworking` is the source interface resolver for
retail `SteamGameServerNetworking()`.

## Source Reconstruction

`src/common/platform/platform_steamworks.c` now makes the GameServer runtime
boundary explicit in `QL_Steamworks_ServerAcceptP2PSession`:

1. Validate the incoming `CSteamID` pointer.
2. Reject calls while `state.gameServerInitialised` is false.
3. Resolve the GameServer networking interface through
   `QL_Steamworks_GetGameServerNetworking`.
4. Dispatch `AcceptP2PSessionWithUser` through vtable slot `0x0c`.

The shared `QL_Steamworks_GetGameServerNetworking` helper still retains the
broader `state.initialised`, `state.gameServerInitialised`, and
`SteamGameServerNetworking` checks. The wrapper-level guard makes the public
accept boundary match the retained server callback runtime lane directly.

## Server Wiring

`src/code/server/sv_client.c` remains the admission owner:

- `SV_SteamServerP2PSessionRequestCallback` ignores null callback payloads.
- It looks up an active client by the remote SteamID.
- It logs ignored, accepted, and failed accept outcomes with the retained
  provider/policy labels.
- It calls `QL_Steamworks_ServerAcceptP2PSession` only after the active-client
  match succeeds.
- `SV_SteamServerInitCallbacks` binds this owner into
  `QL_Steamworks_RegisterServerCallbacks`.

## Validation

Added `test_steam_gameserver_p2p_accept_wrapper_guard_tracks_round_634` to pin:

- promoted aliases and Ghidra rows for `sub_465b70`;
- the Steam GameServer networking import;
- Binary Ninja active-client match ordering before slot `0x0c` accept;
- server callback constructor wiring for `sub_465b70`;
- wrapper input validation before initialized-state guard;
- initialized-state guard before `QL_Steamworks_GetGameServerNetworking`; and
- source callback admission and bootstrap binding in `sv_client.c`.

## Parity Estimate

Focused GameServer P2P accept wrapper guard confidence:
**82% -> 99%**.

Focused Steam GameServer P2P callback admission confidence:
**94% -> 99%**.

overall Steam launch/runtime integration mapping confidence **93.70% -> 93.72%**.
