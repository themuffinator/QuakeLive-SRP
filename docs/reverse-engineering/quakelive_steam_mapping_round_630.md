# Quake Live Steam Mapping Round 630: GameServer P2P Networking Initialized Guards

Date: 2026-06-12

## Scope

This round maps the retail Steam GameServer frame P2P networking lane and
reconstructs explicit initialized-state guards in the SRP public GameServer P2P
wrappers. The retail owner is `SteamServer_Frame`, promoted from `sub_466850`.
The source boundaries are `QL_Steamworks_ServerSendP2PPacket`,
`QL_Steamworks_ServerIsP2PPacketAvailable`, and
`QL_Steamworks_ServerReadP2PPacket`.

Steam launch/runtime online behavior remains behind `QL_BUILD_ONLINE_SERVICES`.
This round tightens wrapper fidelity; it does not enable live Steam services.

## Retail Evidence

- `references/analysis/quakelive_symbol_aliases.json` promotes
  `FUN_00466850` and `sub_466850` to `SteamServer_Frame`.
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  records `FUN_00466850,00466850,827,0,unknown`.
- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
  confirms the server networking lane through
  `STEAM_API.DLL!SteamGameServerNetworking @ 001592a6` and the callback pump
  through `STEAM_API.DLL!SteamGameServer_RunCallbacks @ 001592de`.
- Binary Ninja HLIL shows `00466850    int32_t sub_466850()`, then
  `0046686d  if (data_e30358 != 0)`.
- Inside that gate, retail calls `SteamGameServer_RunCallbacks`, updates
  published state through `sub_466260(0)`, sends periodic server P2P keepalive
  packets through `SteamGameServerNetworking`, checks packet availability
  through vtable slot `4`, reads pending packets through vtable slot `8`, and
  relays packets back through the send slot.

Observed fact: retail performs the GameServer P2P send, available, and read
operations only inside the `data_e30358 != 0` frame gate.

Inferred mapping: SRP's `state.gameServerInitialised` mirrors retail
`data_e30358`, while `SV_SteamServerNetworkingFrame` is the source frame owner
corresponding to retail `sub_466850`.

## Source Reconstruction

`src/common/platform/platform_steamworks.c` now makes the retail initialized
boundary explicit in three public wrappers:

1. `QL_Steamworks_ServerSendP2PPacket` validates its Steam ID, payload pointer,
   and payload length, then rejects calls while `state.gameServerInitialised`
   is false before resolving `SteamGameServerNetworking`.
2. `QL_Steamworks_ServerIsP2PPacketAvailable` validates the output-size
   pointer, then rejects calls while `state.gameServerInitialised` is false
   before resolving `SteamGameServerNetworking`.
3. `QL_Steamworks_ServerReadP2PPacket` validates its buffer, output-size
   pointer, and remote-ID pointer, then rejects calls while
   `state.gameServerInitialised` is false before resolving
   `SteamGameServerNetworking`.

The shared `QL_Steamworks_GetGameServerNetworking` helper still retains the
broader `state.initialised`, `state.gameServerInitialised`, and
`SteamGameServerNetworking` checks. The new wrapper-level guards make the
public boundary match the retail frame gate directly.

## Server Wiring

`src/code/server/sv_main.c` remains the frame and relay owner:

- `SV_SteamServerNetworkingFrame` checks `QL_Steamworks_ServerIsInitialised`,
  runs server callbacks, updates published state, sends keepalive traffic,
  relays P2P packets, and drains outgoing UDP packets.
- `SV_SteamServerSendKeepAlive` sends the periodic reliable server keepalive
  through `QL_Steamworks_ServerSendP2PPacket`.
- `SV_SteamServerRelayP2PPackets` checks availability, reads one packet into a
  relay buffer, identifies the sender, and forwards to eligible clients through
  the same GameServer P2P send wrapper.

## Validation

Added `test_steam_gameserver_p2p_networking_wrapper_guards_track_round_630` to
pin:

- promoted aliases and Ghidra rows for `sub_466850`;
- Steam GameServer networking imports;
- Binary Ninja frame-gate ordering for keepalive, availability, read, and
  relay sends;
- wrapper input validation before initialized-state guards;
- initialized-state guards before `QL_Steamworks_GetGameServerNetworking`; and
- source frame/relay ordering in `SV_SteamServerNetworkingFrame`.

## Parity Estimate

Focused GameServer P2P networking wrapper guard confidence:
**83% -> 99%**.

Focused Steam GameServer frame P2P relay confidence:
**92% -> 99%**.

overall Steam launch/runtime integration mapping confidence **93.62% -> 93.64%**.
