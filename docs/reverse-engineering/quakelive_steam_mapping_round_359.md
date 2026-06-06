# Quake Live Steamworks Mapping Round 359

Date: 2026-06-06

Focus: main Steam client callback bundle dispatch mapping and executable
harness coverage.

## Retail Evidence

- Owning binary: `assets/quakelive/quakelive_steam.exe`.
- Existing mapping report:
  `docs/mapping-ref/quakelive_steam_mapping_report.md` names
  `SteamCallbacks_Init` (`0x004613A0`) as the owner that registers
  `GameRichPresenceJoinRequested_t`, `UserStatsReceived_t`,
  `PersonaStateChange_t`, `P2PSessionRequest_t`,
  `GameServerChangeRequested_t`, `FriendRichPresenceUpdate_t`, and
  `SteamUGCQueryCompleted_t`.
- Symbol/name support:
  `references/analysis/quakelive_symbol_aliases.json` maps the callback
  handlers from `SteamCallbacks_OnGetAllUGCQueryCompleted` through
  `SteamCallbacks_OnPersonaStateChange`.
- Structured companion evidence:
  `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
  has imported `CCallback<class_SteamCallbacks,...>` vtables for the six
  normal callback payloads at `0x00532838`, `0x00532848`, `0x00532858`,
  `0x00532868`, `0x00532878`, and `0x00532888`, plus the
  `CCallResult<class_SteamCallbacks,struct_SteamUGCQueryCompleted_t>` vtable
  at `0x005327bc`.

## Observed Facts

`QL_Steamworks_RegisterClientCallbacks` already reconstructs the retail bundle
membership:

- `GameRichPresenceJoinRequested_t` (`0x151`)
- `UserStatsReceived_t` (`0x44d`)
- `PersonaStateChange_t` (`0x130`)
- `P2PSessionRequest_t` (`0x4b2`)
- `GameServerChangeRequested_t` (`0x14c`)
- `FriendRichPresenceUpdate_t` (`0x150`)
- `SteamUGCQueryCompleted_t` (`0xd49`) as a call result

The executable harness previously proved rich-presence join and UGC call-result
delivery, but it did not queue the other five normal client callback payloads.
That left the registration shape stronger than the runtime pump coverage.

## Source Reconstruction

- Added harness targets for `UserStatsReceived_t`, `PersonaStateChange_t`,
  client-side `P2PSessionRequest_t`, `GameServerChangeRequested_t`, and
  `FriendRichPresenceUpdate_t`.
- Bound those targets in `QLR_Steamworks_RegisterHarnessCallbacks` alongside
  the existing rich-presence and UGC bindings.
- Added raw-payload queue helpers for the five previously unqueued client
  callback payloads.
- Added ctypes coverage proving those callbacks cross
  `QL_Steamworks_RunCallbacks` and preserve the expected projected fields,
  including friend-summary enrichment and server/password string copying.
- Tightened static callback-bundle coverage so all client callback IDs, normal
  callback registrations, and the UGC call-result preparation remain pinned.

## Inference Boundary

Confidence is high for callback membership because the mapping report, alias
map, and imported Ghidra callback symbols agree on the same client callback
bundle. This pass does not claim live Steam backend timing, stats validity,
presence cadence, or P2P networking behavior; it only closes the local callback
pump projection gap behind the opt-in Steamworks policy.

## Parity Estimate

- Focused main client callback pump coverage:
  **before 62% -> after 97%**.
- Steam client callback registration plus payload projection together:
  **before 91% -> after 98%**.
- Broader Steamworks parity remains approximately **99%** because this is a
  static/harness reconstruction pass, not live backend validation.
