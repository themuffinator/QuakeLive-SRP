# Quake Live Steam Mapping Round 432

Date: 2026-06-08

## Scope

This round tightens the `SteamClient_Frame` runtime pump order. The focus is
keeping the normal initialized frame path aligned with retail while retaining
the source-only launch recovery shim for late Steam availability.

## Evidence

- `references/analysis/quakelive_symbol_aliases.json` maps `sub_461d40` to
  `SteamClient_Frame`.
- Binary Ninja HLIL for `sub_461d40` gates the whole pump on
  `data_e30218 != 0`, the retained Steam initialised flag.
- Inside that branch the HLIL order is:
  - `SteamAPI_RunCallbacks()`
  - `sub_460d10()` for captured voice send
  - channel `0` packet drain into `"game.stats.report"`
  - `sub_461a60()` for incoming voice packet processing
- Earlier mapping rounds identify `sub_460d10` as
  `SteamVoice_SendCapturedPacket` and `sub_461a60` as
  `SteamVoice_ProcessIncomingPackets`.

## Source Reconstruction

- Moved the source-only `SteamClient_RecoverCallbackBootstrap()` call to the
  tail of `SteamClient_Frame` after `QL_Steamworks_RunCallbacks()`,
  `CL_Steam_SendVoicePacket()`, `CL_Steam_ProcessStatsReportPackets()`, and
  `CL_Steam_ProcessVoicePackets()`.
- Kept the launch recovery shim itself, since source builds can run with
  delayed Steam runtime availability while the retail binary links directly to
  `steam_api.dll`.
- Added parity assertions that pin the HLIL frame-pump sequence and the source
  ordering, including recovery after the retail-equivalent pump.

## Deferred Notes

- Retail has no retry/recovery call in `SteamClient_Frame`; the source shim is
  a documented compatibility divergence for optional Steamworks loading.
- The current source still refreshes platform service descriptors before the
  retained initialized gate, so failed launch-time probes can recover without a
  full process restart.

## Parity

Focused `SteamClient_Frame` pump-order confidence moves from 86% to 94%.
The broader Steam launch/runtime integration slice moves from 84% to 85%.
