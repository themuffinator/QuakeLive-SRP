# Quake Live Steam Mapping Round 436

Date: 2026-06-08

## Scope

This round tightens the Steam frame-pump ownership lane after the previous
lazy-refresh guard pass. The focus is reconstructing the retail split between
the explicit `SteamClient_Init` bootstrap owner and frame-time Steam consumers.

## Evidence

- Binary Ninja HLIL for retail `SteamClient_Init` (`sub_461500`) sets the
  retained initialized flag from `SteamAPI_Init()` after the `com_build` guard.
- Binary Ninja HLIL for retail `SteamClient_Frame` (`sub_461d40`) gates the
  whole frame pump on `data_e30218 != 0`.
- Inside that gate, retail calls `SteamAPI_RunCallbacks()`, sends queued voice
  data, drains channel-0 stats-report packets into `game.stats.report`, and
  drains voice packets. There is no `SteamAPI_Init()` path or service-refresh
  equivalent from the frame loop.
- The Ghidra import table also shows `SteamAPI_Init` and
  `SteamAPI_RunCallbacks` as separate Steam API imports, supporting the
  observed owner split.

## Source Reconstruction

- Removed the source-only `QL_RefreshPlatformServices()` call from
  `SteamClient_Frame`.
- Removed frame-time re-latching through `SteamClient_SetInitializedState()`.
- Kept `SteamClient_Frame` as a retained-state consumer: it now returns until
  `SteamClient_IsInitialized()` is already true, then runs callbacks and the
  retained voice/stat packet pumps in retail order.
- Adjusted `SteamClient_RecoverCallbackBootstrap()` so callback retry remains a
  callback-registration retry only. It no longer refreshes platform services or
  turns frame-time work into a second Steam initialization owner.

## Deferred Notes

- Wrapper helpers still retain source-side lazy refreshes for specific
  compatibility surfaces where previous rounds documented the optional dynamic
  platform-service model. The frame pump itself now follows the retail retained
  initialized-flag gate.

## Parity

Focused Steam frame-pump owner confidence moves from 78% to 96%.
The broader Steam launch/runtime integration slice moves from 88% to 89%.
