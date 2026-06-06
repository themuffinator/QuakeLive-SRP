# Quake Live Steamworks Mapping Round 355

Date: 2026-06-06

Focus: server-side `P2PSessionRequest_t` admission policy for the Steam
GameServer networking callback.

## Retail Evidence

- Owning binary: `assets/quakelive/quakelive_steam.exe`.
- Primary HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`.
- Ghidra companion row:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  lists `FUN_00465b70` at `0x00465b70`.
- String support:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt`
  retains `Accepting P2P connection with %llu` and
  `^1WARNING: Not accepting P2P connection, couldn't find player %llu!`.

## Observed Facts

`SteamServerCallbacks_OnP2PSessionRequest` at `0x00465B70` performs a narrow
client-slot scan:

- It reads the current max-client count from the server globals.
- It walks the retained `client_t` array with stride `0x25b68`.
- Each candidate must have `*client == 4`, which matches `CS_ACTIVE` in the
  reconstructed `clientState_t` enum.
- The callback compares the two stored SteamID words against the low/high
  halves in the incoming session request payload.
- On a match, it logs the accepted P2P connection, obtains
  `SteamGameServerNetworking()`, and dispatches through vtable offset `0x0c`.
- If no active SteamID match is found, it logs the retail warning and does not
  call the accept slot.

No separate `platformAuthSucceeded`-style field appears in this callback's
admission gate. Authentication still owns the SteamID lifecycle elsewhere:
`ValidateAuthTicketResponse_t` needs to find connected clients before they have
fully entered the world, but the P2P request owner is active-slot gated.

## Source Reconstruction

- Added `SV_FindActiveClientBySteamId` beside the broader
  `SV_FindClientBySteamId` helper. The existing helper remains available for
  auth-ticket responses and other pre-active lookups.
- Updated `SV_SteamServerP2PSessionRequestCallback` to use the active-only
  SteamID helper, matching the retail `*client == 4` gate.
- Removed the extra `platformAuthSucceeded` check from the P2P callback.
- Added provider-aware acceptance logging before
  `QL_Steamworks_ServerAcceptP2PSession`, preserving the observed retail
  accept-before-dispatch diagnostic order while keeping the modern
  compatibility labels.
- Tightened static parity coverage so the callback is pinned to
  `SV_FindActiveClientBySteamId`, rejects missing active matches, no longer
  checks `platformAuthSucceeded`, and still reaches the retained server P2P
  accept wrapper.

## Inference Boundary

Confidence is high for the callback admission policy because the HLIL exposes
the state comparison, SteamID word comparisons, success/failure strings, and
the final `SteamGameServerNetworking` vtable slot in one compact function.
Live Steam P2P backend behavior, callback timing, and NAT traversal remain
intentionally unvalidated while online services stay opt-in behind
`QL_BUILD_ONLINE_SERVICES`.

## Parity Estimate

- Focused server-side `P2PSessionRequest_t` admission gate:
  **before 72% -> after 96%**.
- Server callback bundle wiring:
  **before 98% -> after 99%**.
- Broader Steamworks parity remains approximately **99%**; remaining
  uncertainty is live backend behavior and other intentionally opt-in online
  service validation, not this static callback policy.
