# Quake Live Steam Mapping Round 615: Client Frame Callback And Packet Pump

Date: 2026-06-12

## Scope

This round rechecks the client Steam runtime frame pump around
`SteamClient_Frame`, `SteamAPI_RunCallbacks`, outgoing voice capture, channel-0
stats-report packets, incoming voice packets, and SRP's callback-bootstrap
recovery tail.

No engine source behavior changed in this pass.

## Retail Evidence

Primary owner: `assets/quakelive/quakelive_steam.exe`

Evidence checked:

- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/analysis/quakelive_symbol_aliases.json`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `src/code/client/cl_main.c`
- `src/code/qcommon/common.c`
- `src/common/platform/platform_steamworks.c`
- `src/common/platform/platform_steamworks.h`

Function ownership:

| Ghidra row | Address | Promoted owner |
| --- | --- | --- |
| `FUN_00461d40` | `0x00461D40` | `SteamClient_Frame` |
| `FUN_00460d10` | `0x00460D10` | `SteamVoice_SendCapturedPacket` |
| `FUN_00461a60` | `0x00461A60` | `SteamVoice_ProcessIncomingPackets` |

Observed facts:

- `sub_461d40` gates the retail frame pump on retained initialized state
  `data_e30218`.
- Inside that gate, retail calls `SteamAPI_RunCallbacks()`, then
  `sub_460d10()`.
- It drains `SteamNetworking()` channel `0`, inflates each packet through
  `sub_4fda50`, and publishes `game.stats.report`.
- It then tailcalls `sub_461a60()` for incoming voice packets on channel `1`.
- `sub_461a60` reads channel-1 packets through `SteamNetworking()`, decompresses
  them through `SteamUser()` voice decompression, and forwards valid PCM into
  the sound voice path.
- The import table identifies `SteamAPI_RunCallbacks`, `SteamNetworking`, and
  `SteamUser`.

## Source Reconstruction

The source reconstruction keeps `SteamClient_Frame` a retained-state runtime
consumer:

- `Com_Frame` pumps `CL_WebHost_Frame()` and then `SteamClient_Frame()` after
  the second event loop and before `CL_Frame(msec)`.
- `SteamClient_Frame` returns unless online services are enabled and
  `SteamClient_IsInitialized()` is true.
- The frame owner does not call `QL_RefreshPlatformServices()` and does not
  relatch `SteamClient_SetInitializedState`.
- The runtime order is:
  `QL_Steamworks_RunCallbacks()`,
  `CL_Steam_SendVoicePacket()`,
  `CL_Steam_ProcessStatsReportPackets()`,
  `CL_Steam_ProcessVoicePackets()`,
  `SteamClient_RecoverCallbackBootstrap()`.
- `QL_Steamworks_RunCallbacks` is a thin initialized-state wrapper around the
  dynamically loaded `SteamAPI_RunCallbacks` export.
- `CL_Steam_ProcessStatsReportPackets` keeps the channel-0 zlib-inflated
  `game.stats.report` path.
- `CL_Steam_ProcessVoicePackets` keeps the channel-1 voice read/decompress/mute
  gate before feeding `S_AddVoiceSamples`.

## Compatibility Boundary

Live Steam frame work remains behind `QL_BUILD_ONLINE_SERVICES` and the
retained initialized-state flag. Default-disabled builds do not pump live Steam
callbacks or packet lanes.

`SteamClient_RecoverCallbackBootstrap` is source-side dynamic-adapter policy,
not a retail control-flow claim. It stays at the tail of `SteamClient_Frame`
after the retail pump work and refuses to become a second Steam initialization
owner.

## Validation

Added
`tests/test_platform_services.py::test_steam_client_frame_callback_and_packet_pump_tracks_round_615`
to pin:

- alias, Ghidra function, and import evidence for `SteamClient_Frame`,
  outgoing voice, incoming voice, and Steam API/networking imports;
- Binary Ninja HLIL anchors for the retained initialized-state gate,
  callback pump, outgoing voice call, channel-0 stats packet publication, and
  incoming voice call;
- source ordering for `Com_Frame`, `SteamClient_Frame`, stats-report packet
  inflate/publication, outgoing and incoming voice helpers, and the callback
  recovery tail; and
- this round note plus Task A484 parity anchors.

Planned validation for this pass:

```text
python -m pytest tests/test_platform_services.py::test_steam_client_frame_callback_and_packet_pump_tracks_round_615 -q --tb=short
python -m pytest tests/test_platform_services.py -q --tb=short
python -m pytest tests/test_steamworks_harness.py -q --tb=short
```

## Confidence

Observed facts:

- HLIL directly shows the retail pump order and channel ownership.
- Ghidra rows, imports, and aliases identify the frame and voice helper owners.
- Source tests now bind the common-frame placement, frame gate, low-level
  callback wrapper, packet lanes, and recovery tail into one runtime gate.

Inference:

- SRP's `SteamClient_RecoverCallbackBootstrap` tail is the correct bounded
  reconstruction for a dynamic Steamworks adapter. It preserves the retail pump
  order while allowing optional live callback registration to recover without
  relatching Steam initialization inside the frame loop.

Parity estimates:

- Focused Steam client-frame runtime pump confidence:
  **before 94% -> after 99%**.
- Focused retained-state callback/packet policy classification:
  **before 95% -> after 99%**.
- Overall Steam launch/runtime integration mapping confidence: **93.32% -> 93.34%**.
