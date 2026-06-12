# Quake Live Steam Mapping Round 627: GameServer Incoming Packet Initialized Guard

Date: 2026-06-12

## Scope

This round maps the retail Steam GameServer incoming UDP packet wrapper and
reconstructs its initialized-state gate in the SRP platform wrapper. The target
is the retail `SteamServer_HandleIncomingPacket` owner, promoted from
`sub_465d50`, and its source-side mirror
`QL_Steamworks_ServerHandleIncomingPacket`.

Steam launch/runtime service behavior remains behind `QL_BUILD_ONLINE_SERVICES`.
This round does not enable live Steam behavior; it tightens the explicit guard
boundary used by the offline-compatible wrapper.

## Retail Evidence

- `references/analysis/quakelive_symbol_aliases.json` promotes
  `FUN_00465d50`, `sub_465D50`, and `sub_465d50` to
  `SteamServer_HandleIncomingPacket`.
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  records `FUN_00465d50,00465d50,94,0,unknown`.
- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
  confirms the Steam GameServer import lane through
  `STEAM_API.DLL!SteamGameServer @ 0015918a` and the adjacent callback pump
  `STEAM_API.DLL!SteamGameServer_RunCallbacks @ 001592de`.
- Binary Ninja HLIL in
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
  shows `00465d50    uint32_t sub_465d50(void* arg1, void* arg2)`, then
  `00465d5a  if (data_e30358 == 0)`, `00465d5f      return 0`,
  `00465d84  int32_t eax_2 = SteamGameServer()`, and the final
  `00465dad` dispatch through SteamGameServer vtable slot `0x94`.

Observed fact: the retail wrapper checks the retained GameServer initialized
flag with `data_e30358 == 0` before it calls `SteamGameServer()` and dispatches
the incoming packet vtable method.

Inferred mapping: SRP's `state.gameServerInitialised` is the source-side mirror
for retail `data_e30358`, because it is set by the reconstructed
`SteamGameServer_Init` owner, cleared by the reconstructed
`SteamGameServer_Shutdown` owner, and already guards adjacent GameServer
wrappers such as heartbeat, unauthenticated-user, and key-value publication.

## Source Reconstruction

`src/common/platform/platform_steamworks.c` now makes the retail gate explicit
inside `QL_Steamworks_ServerHandleIncomingPacket`:

1. Reject null or empty packet payloads.
2. Reject calls when `state.gameServerInitialised` is false.
3. Resolve the GameServer interface through `QL_Steamworks_GetGameServer`.
4. Dispatch vtable slot `0x94` through
   `QL_SteamGameServer_HandleIncomingPacketFn`.

The source already had a secondary helper-level guard in
`QL_Steamworks_GetGameServer`; retaining that helper guard and adding the
wrapper-level guard matches the retail control-flow boundary more directly and
keeps the public wrapper contract self-contained.

`src/code/server/sv_main.c` remains the host-socket owner. `SV_PacketEvent`
hands every candidate UDP packet to `SV_SteamServerHandleIncomingPacket` before
the connectionless packet path, and that helper still checks `NA_IP`, validates
`QL_Steamworks_ServerIsInitialised`, packs the IPv4 bytes, and forwards the
packet bytes plus source port into the platform wrapper.

## Compatibility Boundary

This is a fidelity/readability repair, not a new online-services feature. The
existing `QL_BUILD_ONLINE_SERVICES` default-disabled policy is unchanged, and
offline builds continue to use the stubs/fallbacks instead of live Steam
runtime behavior.

## Validation

Added `test_steam_gameserver_incoming_packet_wrapper_guard_tracks_round_627` to
pin:

- the promoted aliases for `sub_465d50`;
- the `functions.csv` size row;
- the SteamGameServer import lane;
- the Binary Ninja guard-to-vtable-slot ordering;
- the source wrapper guard order; and
- the server packet-event handoff order.

## Parity Estimate

Focused GameServer incoming-packet wrapper guard confidence:
**88% -> 99%**.

Focused Steam GameServer UDP handoff owner confidence:
**94% -> 99%**.

overall Steam launch/runtime integration mapping confidence **93.56% -> 93.58%**.
