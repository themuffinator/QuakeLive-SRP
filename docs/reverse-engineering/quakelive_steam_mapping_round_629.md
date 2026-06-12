# Quake Live Steam Mapping Round 629: GameServer Outgoing Packet Drain Guard

Date: 2026-06-12

## Scope

This round maps the retail Steam GameServer frame owner that drains queued
outgoing Steam UDP packets and reconstructs the initialized-state boundary in
SRP's public outgoing-packet wrapper. The retail owner is `SteamServer_Frame`,
promoted from `sub_466850`; the source boundary is
`QL_Steamworks_ServerGetNextOutgoingPacket`.

This is a fidelity repair inside the default-disabled Steam launch/runtime
surface. It does not enable live Steam behavior outside `QL_BUILD_ONLINE_SERVICES`.

## Retail Evidence

- `references/analysis/quakelive_symbol_aliases.json` promotes
  `FUN_00466850` and `sub_466850` to `SteamServer_Frame`.
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  records `FUN_00466850,00466850,827,0,unknown`.
- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
  confirms the Steam GameServer import lane through
  `STEAM_API.DLL!SteamGameServer @ 0015918a` and the callback pump
  `STEAM_API.DLL!SteamGameServer_RunCallbacks @ 001592de`.
- Binary Ninja HLIL shows `00466850    int32_t sub_466850()`, then
  `0046686d  if (data_e30358 != 0)`, followed by
  `SteamGameServer_RunCallbacks()`, `sub_466260(0)`, and the outgoing packet
  loop through `SteamGameServer()` vtable slot `0x98`.
- The same loop copies the packed address bytes from `var_42c` before sending
  the payload through the server socket path.

Observed fact: retail drains outgoing Steam GameServer packets only inside the
`data_e30358 != 0` frame gate.

Inferred mapping: SRP's `state.gameServerInitialised` mirrors retail
`data_e30358`, while `SV_SteamServerNetworkingFrame` owns the source-side
frame sequence that corresponds to retail `sub_466850`.

## Source Reconstruction

`src/common/platform/platform_steamworks.c` now makes the initialized-state gate
explicit inside `QL_Steamworks_ServerGetNextOutgoingPacket`:

1. Reject invalid buffers and output pointers.
2. Reject calls while `state.gameServerInitialised` is false.
3. Resolve the GameServer interface through `QL_Steamworks_GetGameServer`.
4. Dispatch vtable slot `0x98` through
   `QL_SteamGameServer_GetNextOutgoingPacketFn`.

The shared `QL_Steamworks_GetGameServer` helper still retains its own
`state.initialised`, `state.gameServerInitialised`, and `SteamGameServer`
checks. The wrapper-level guard matches the retail frame gate more directly
for this public SRP boundary.

## Server Wiring

`src/code/server/sv_main.c` remains the host-socket owner:

- `SV_SteamServerNetworkingFrame` checks `QL_Steamworks_ServerIsInitialised`
  before running server callbacks, updating published state, sending keepalive
  traffic, relaying P2P packets, and draining outgoing packets.
- `SV_SteamServerDrainOutgoingPackets` calls
  `QL_Steamworks_ServerGetNextOutgoingPacket`, rebuilds the `NA_IP` address
  from the packed little-endian byte order, preserves the returned port, and
  sends the payload through `NET_SendPacket( NS_SERVER, ... )`.

## Validation

Added `test_steam_gameserver_outgoing_packet_drain_guard_tracks_round_629` to
pin:

- promoted aliases for `sub_466850`;
- the Ghidra frame function row;
- Binary Ninja frame gate, callback pump, published-state update, and vtable
  `0x98` outgoing-packet loop;
- source wrapper guard order;
- packed address byte expansion in `SV_SteamServerDrainOutgoingPackets`; and
- source frame order in `SV_SteamServerNetworkingFrame`.

## Parity Estimate

Focused GameServer outgoing-packet wrapper guard confidence:
**84% -> 99%**.

Focused Steam GameServer frame outgoing-packet drain confidence:
**92% -> 99%**.

overall Steam launch/runtime integration mapping confidence **93.60% -> 93.62%**.
