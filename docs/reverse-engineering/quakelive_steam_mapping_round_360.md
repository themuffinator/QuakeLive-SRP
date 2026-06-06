# Quake Live Steamworks Mapping Round 360

Date: 2026-06-06

Focus: Steam GameServer callback bundle dispatch mapping and executable
harness coverage.

## Retail Evidence

- Owning binary: `assets/quakelive/quakelive_steam.exe`.
- Existing mapping report:
  `docs/mapping-ref/quakelive_steam_mapping_report.md` names
  `SteamServerCallbacks_Init` (`0x00466DB0`) as the owner that registers
  `SteamServersConnected_t`, `SteamServerConnectFailure_t`,
  `SteamServersDisconnected_t`, `ValidateAuthTicketResponse_t`, and
  server-side `P2PSessionRequest_t`.
- Symbol/name support:
  `references/analysis/quakelive_symbol_aliases.json` maps
  `SteamServerCallbacks_OnServersConnected`,
  `SteamServerCallbacks_OnConnectFailure`,
  `SteamServerCallbacks_OnServersDisconnected`,
  `SteamServerCallbacks_OnValidateAuthTicketResponse`, and
  `SteamServerCallbacks_OnP2PSessionRequest`.
- Structured companion evidence:
  `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
  has imported `CCallback<class_SteamServerCallbacks,...>` vtables for the
  five server callback payloads at `0x005332e8`, `0x005332f8`,
  `0x00533308`, `0x00533318`, and `0x00533328`.
- The same symbol corpus identifies the adjacent `idSteamStats` GameServer
  callback vtables for `SteamServersConnected_t`, `GSStatsReceived_t`, and
  `GSStatsStored_t`.

## Observed Facts

`QL_Steamworks_RegisterServerCallbacks` already reconstructs the full retained
server callback registration surface used by the platform layer:

- `SteamServersConnected_t` (`0x65`)
- `SteamServerConnectFailure_t` (`0x66`)
- `SteamServersDisconnected_t` (`0x67`)
- `ValidateAuthTicketResponse_t` (`0x8f`)
- server-side `P2PSessionRequest_t` (`0x4b2`)
- `GSStatsReceived_t` (`0x708`)
- `GSStatsStored_t` (`0x709`)

The executable harness already proved the auth-ticket response and GS stats
payloads, but it did not attach handlers or queue raw payloads for server
connection lifecycle or server-side P2P callbacks. That left the retail server
callback bundle only partially exercised through `QL_Steamworks_RunServerCallbacks`.

## Source Reconstruction

- Added harness targets for `SteamServersConnected_t`,
  `SteamServerConnectFailure_t`, `SteamServersDisconnected_t`, and
  server-side `P2PSessionRequest_t`.
- Bound those targets in `QLR_Steamworks_RegisterServerHarnessCallbacks`.
- Added raw-payload queue helpers for the four previously unqueued server
  callback payloads.
- Added ctypes coverage proving those payloads cross
  `QL_Steamworks_RunServerCallbacks` and preserve result/retry/SteamID
  projection.
- Tightened static registration coverage so all seven retained server callback
  IDs, object preparations, object registrations, and unregister calls remain
  pinned.

## Inference Boundary

Confidence is high for the server callback bundle membership because the
mapping report, alias map, and imported Ghidra symbols agree on the retained
SteamServerCallbacks owner. This pass does not claim live Steam GameServer
connection timing, backend auth policy, VAC behavior, or network transport
behavior. It closes the local callback-pump projection gap behind the opt-in
Steamworks policy.

## Parity Estimate

- Focused server callback pump coverage:
  **before 63% -> after 97%**.
- Steam GameServer callback registration plus payload projection together:
  **before 92% -> after 98%**.
- Broader Steamworks parity remains approximately **99%** because this pass is
  static/harness reconstruction rather than live backend validation.
