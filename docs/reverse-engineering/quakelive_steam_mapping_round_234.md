# quakelive_steam.exe Mapping Round 234

Date: 2026-05-11

Scope: the retained client Steam per-frame pump in
`src/code/client/cl_main.c`, staying inside engine-owned runtime code and
avoiding external-library implementation work.

## Summary

This round reconstructs the retail `SteamClient_Frame` seam more directly
instead of leaving it flattened as a callback-owned helper. The checked-in
client frame now calls a dedicated `SteamClient_Frame()` owner, and that owner
now includes the missing channel-0 Steam packet drain that feeds
`game.stats.report` into the browser event surface before incoming voice
processing.

Classification mix:

- `0` new engine/client aliases
- `0` engine/client alias renames
- `2` engine/client source reconstruction fixes
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main source-parity wins are:

- [`cl_main.c`](../../src/code/client/cl_main.c) now restores the retail owner
  name and call shape by routing `CL_Frame` through `SteamClient_Frame()`
  instead of the older `CL_Steam_Frame()` helper
- [`SteamClient_Frame`](../../src/code/client/cl_main.c) now drains Steam P2P
  channel `0` into `game.stats.report`, matching the committed retail frame
  lane instead of only running callbacks and voice transport

## Evidence Notes

- The committed retail `SteamClient_Frame` owner at `sub_461D40` shows this
  exact order:
  - `SteamAPI_RunCallbacks()`
  - `sub_460d10()` (`SteamVoice_SendCapturedPacket`)
  - loop on `SteamNetworking()->IsP2PPacketAvailable(..., 0)`
  - `sub_4f3260(..., "game.stats.report", ...)`
  - `sub_461a60()` (`SteamVoice_ProcessIncomingPackets`)
- The committed retail frame caller at `004CC995` reaches `sub_461D40`
  directly from the main client frame.
- Round 06 had already promoted `sub_461D40 -> SteamClient_Frame`, but the
  checked-in source still lagged behind that owner boundary and packet lane.

## Source Reconstruction

- [`cl_main.c`](../../src/code/client/cl_main.c) now defines
  `CL_STEAM_STATS_REPORT_CHANNEL` as the retained channel-0 Steam packet lane.
- Added `CL_Steam_ProcessStatsReportPackets()` to:
  - poll `QL_Steamworks_IsP2PPacketAvailable(..., 0)`
  - read channel-0 packets through `QL_Steamworks_ReadP2PPacket(...)`
  - forward the decoded text payload into
    `CL_Steam_PublishBrowserEvent( "game.stats.report", ... )`
- Renamed the checked-in frame owner from `CL_Steam_Frame()` to
  `SteamClient_Frame()` and updated `CL_Frame()` to call that owner directly.
- `SteamClient_Frame()` now gates on Steam service availability plus
  `QL_Steamworks_Init()`, then runs:
  - `QL_Steamworks_RunCallbacks()`
  - `CL_Steam_SendVoicePacket()`
  - `CL_Steam_ProcessStatsReportPackets()`
  - `CL_Steam_ProcessVoicePackets()`

## Verification

Static/source validation:

- `pytest tests/test_client_sound_voice_parity.py tests/test_client_workshop_bootstrap_parity.py tests/test_platform_services.py -q --tb=no -k "steam_voice_frame or workshop_bootstrap or steam_callback_owner"`
  passed with `3 passed, 34 deselected`
- `git diff --check -- src/code/client/cl_main.c tests/test_client_sound_voice_parity.py tests/test_client_workshop_bootstrap_parity.py tests/test_platform_services.py`
  reported only the repo's existing LF -> CRLF normalization warnings on the
  touched text files

Alias accounting for the current dirty worktree:

- before this pass: `2238` raw `quakelive_steam` aliases, `2157` strict
  address-backed aliases
- after this pass: `2238` raw `quakelive_steam` aliases, `2157` strict
  address-backed aliases
- strict Ghidra address-backed coverage after this pass: `39.412%` of `5473`
  committed functions

Parity estimate after this pass:

- strict-retail client Steam frame/packet lane: `97%` before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

The next nearby engine-only pass is to keep checking the remaining client
Steam runtime helpers for flattened retail owners or missing packet/service
sub-lanes, while staying out of the external-library internals themselves.
