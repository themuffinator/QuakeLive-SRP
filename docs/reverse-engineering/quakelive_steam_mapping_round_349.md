# Quake Live Steamworks Mapping Round 349

Date: 2026-06-05

## Focus

Pin the retained legacy Steam P2P networking surface with executable harness
coverage:

- client `SteamAPI_SteamNetworking`
- server `SteamGameServerNetworking`
- the existing game-server outgoing UDP packet wrapper slot

This round does not add `ISteamNetworkingSockets` or
`ISteamNetworkingMessages`. Those remain the documented modern-adapter gap.

## Evidence

Observed import evidence:

- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
  lists `STEAM_API.DLL!SteamNetworking @ 001591ba`.
- The same import list contains
  `STEAM_API.DLL!SteamGameServerNetworking @ 001592a6`.

Observed HLIL evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
  calls `SteamNetworking()` and uses `*interface + 4` for
  `IsP2PPacketAvailable` at `0x00461a9d`.
- The same client loop reads `*interface + 8` at `0x00461ad8`.
- Additional client reads use the same availability/read slots around
  `0x00461d8f`, `0x00461dc8`, and `0x00461ee2`.
- The server callback path calls `SteamGameServerNetworking()` and uses
  `*interface + 4` / `*interface + 8` for availability/read around
  `0x00466928` and `0x00466961`.
- The server stats bootstrap sends the `hello` payload through the server
  networking interface at `0x00467d2b`, matching the reconstructed
  `SendP2PPacket` slot and channel/type constants already guarded by
  `tests/test_platform_services.py`.

Source evidence already present before this pass:

- `src/common/platform/platform_steamworks.c` maps
  `QL_Steamworks_SendP2PPacket` to vtable slot `0`.
- `QL_Steamworks_IsP2PPacketAvailable` maps to slot `1`.
- `QL_Steamworks_ReadP2PPacket` maps to slot `2`.
- `QL_Steamworks_AcceptP2PSession` maps to slot `0x0c / 4`.
- The server-side equivalents use the same legacy `ISteamNetworking`-shape
  slots through `QL_Steamworks_GetGameServerNetworking`.
- `QL_Steamworks_ServerGetNextOutgoingPacket` maps the retained game-server
  outgoing packet wrapper to the game-server vtable slot `0x98 / 4`.

## Reconstruction

This pass completed the harness side of that mapping:

- Added `SteamAPI_SteamNetworking` symbol resolution to the mock loader.
- Added mock client `ISteamNetworking` send/available/read/accept vtable slots.
- Replaced the null `SteamGameServerNetworking` mock with equivalent server
  send/available/read/accept slots.
- Added capture state, getters, and setters for client/server packet payloads,
  channels, send types, remote Steam IDs, and failure controls.
- Added a one-shot mock for `SteamGameServer::GetNextOutgoingPacket`, including
  IP/port projection and call counting.
- Added exported harness wrappers in both enabled and disabled build modes so
  the ctypes ABI is stable regardless of `QL_BUILD_STEAMWORKS`.
- Added focused Python coverage for the client and server legacy P2P wrappers.

## Inference Boundary

The retail evidence proves the legacy `ISteamNetworking`-shape wrapper slots
and the server bootstrap `hello` packet path. It does not prove a modern
Steam-networking replacement. The correct source status remains:

- retail-faithful legacy path: reconstructed and now harness-pinned
- modern sockets/messages adapter: intentionally absent and still labeled

## Verification

Validation:

```text
python -m pytest tests/test_steamworks_harness.py::test_legacy_p2p_wrappers_use_mapped_steamnetworking_slots tests/test_steamworks_harness.py::test_legacy_game_server_p2p_wrappers_use_mapped_networking_slots -q --tb=short
4 passed

python -m pytest tests/test_steamworks_harness.py -q --tb=short
86 passed

python -m pytest tests/test_platform_services.py::test_steamworks_modern_adapter_gaps_stay_explicit_until_owned tests/test_platform_services.py::test_client_voice_commands_reconstruct_retail_binding_surface -q --tb=short
2 passed

MSBuild src\code\quakelive.sln /t:quakelive_steam /p:Configuration=Debug /p:Platform=x86 /p:PlatformToolset=v141
Build succeeded, 0 warnings, 0 errors

MSBuild src\code\quakelive.sln /t:quakelive_steam /p:Configuration=Debug /p:Platform=x86 /p:PlatformToolset=v141 /p:QLBuildOnlineServices=1 /p:QLBuildSteamworks=1 /p:QLRequireSteamworksSdk=0 /p:QLRequireAwesomiumSdk=0
Build succeeded, 3 BSCMAKE browse-info warnings, 0 errors
```

## Parity Estimate

Focused legacy P2P wrapper/harness parity: **before 82% -> after 96%**.

The remaining 4% is not a slot-mapping gap; it is live Steam runtime and
modern-adapter validation risk. Broader Steamworks parity remains approximately
**99%** because online-service behavior is still opt-in, legacy P2P is retained
for retail parity, and modern `ISteamNetworkingSockets` /
`ISteamNetworkingMessages` replacement design remains explicitly open.
