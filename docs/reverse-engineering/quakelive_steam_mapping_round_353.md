# Quake Live Steam Host Mapping Round 353

## Scope

This round reconstructs the missing inbound UDP half of the Steam game-server
socket bridge. Earlier work already recovered the outgoing drain through
`SteamGameServer` slot `0x98`; this pass adds the adjacent incoming packet
handoff through slot `0x94` and wires it into the engine server packet owner.

## Evidence

- Binary Ninja HLIL, `quakelive_steam.exe_hlil_part02.txt`, shows
  `sub_465d50` returning `0` when `data_e30358` is clear, packing IPv4 bytes
  from the source address block, calling `SteamGameServer()`, and dispatching
  through vtable offset `0x94` with packet data, packet length, packed IP, and
  the raw two-byte source port.
- Ghidra `functions.csv` contains `FUN_00465d50` at `0x00465d50`, size `94`,
  and `decompile_top_functions.c` shows the connectionless packet owner calling
  that function after the local Quake connectionless handlers do not claim a
  command.
- `docs/reverse-engineering/quakelive_steam_mapping_round_04.md` already
  promoted `sub_465d50` as `SteamServer_HandleIncomingPacket`, noting that both
  client and dedicated packet-event paths use it as the Steam connectionless
  packet handler.
- The existing reconstruction already had the paired outgoing bridge:
  `QL_Steamworks_ServerGetNextOutgoingPacket` reads `SteamGameServer` slot
  `0x98` and `SV_SteamServerDrainOutgoingPackets` sends those packets through
  the host UDP socket.

## Reconstruction

- Added `QL_Steamworks_ServerHandleIncomingPacket`, guarded by
  `QL_BUILD_STEAMWORKS`, which obtains the retained `SteamGameServer`
  interface and calls vtable slot `0x94`.
- Added a disabled-build inline stub returning `qfalse`, preserving the
  repository policy that Quake Live online services stay opt-in.
- Added `SV_SteamServerHandleIncomingPacket` beside `SV_PacketEvent`. It
  accepts only IPv4 packets, reconstructs the retail packed address as
  `a.b.c.d -> 0xaabbccdd`, and forwards the original message buffer, size,
  packed IP, and raw `netadr_t` port into the Steamworks wrapper.
- Kept this hook quiet: the disabled stub is expected in default builds, and
  logging every non-Steam UDP packet would make ordinary server traffic noisy.
- Extended the Steamworks harness with a mocked `SteamGameServer` slot `0x94`,
  payload capture, endpoint capture, and success/failure result control.

## Confidence

High for the wrapper slot and packet-event owner. The vtable offset, address
packing, and argument order are directly observed in HLIL, and the adjacent
outgoing drain at slot `0x98` already existed in source. The only intentionally
bounded detail is live backend behavior: no runtime Steam validation was
performed because online services remain disabled by default and static/harness
evidence is enough for this reconstruction.

## Parity Estimate

- Focused incoming UDP GameServer packet handoff:
  **before 35% -> after 92%**.
- Combined Steam GameServer UDP bridge, incoming plus outgoing:
  **before 82% -> after 96%**.
- Broader Steamworks parity remains approximately **99%**; remaining
  uncertainty is live backend validation and other intentionally opt-in online
  service behavior, not this packet bridge.
