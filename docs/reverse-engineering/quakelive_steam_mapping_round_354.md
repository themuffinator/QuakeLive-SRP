# Quake Live Steamworks Mapping Round 354

Date: 2026-06-06

Focus: `idSteamStats` GameServer logged-on gating for server-side user stat
requests.

## Retail Evidence

- Owning binary: `assets/quakelive/quakelive_steam.exe`.
- Primary HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`.
- Symbol support:
  `references/analysis/quakelive_symbol_aliases.json` maps `sub_467190` to
  `SteamStats_OnServersConnected`.
- Ghidra companion rows in
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  identify the adjacent stats handlers `FUN_004670c0`,
  `FUN_004671d0`, `FUN_004672d0`, and `FUN_00467360`, but the small
  `0x00467190` callback thunk is carried by the HLIL and alias evidence.

## Observed Facts

`SteamStats_OnServersConnected` at `0x00467190` performs a narrow request
gate:

- It first checks that `SteamGameServerStats()` returns a non-null interface.
- It then calls `SteamGameServer()` vtable offset `0x20`.
- Only when that call returns true does it fetch `SteamGameServerStats()` again
  and dispatch through vtable slot `0x00`, passing the retained low/high
  SteamID halves from the `idSteamStats` object.
- If either interface lookup or logged-on check fails, it returns without
  issuing the request.

The constructor/bootstrap path repeats the same pattern at `0x004679d9`: after
copying the stat descriptor table and clearing the value cache, retail checks
`SteamGameServerStats() != 0 && (*(*SteamGameServer() + 0x20))() != 0` before
calling `SteamGameServerStats` slot `0x00` for the initial request.

## Source Reconstruction

- Added `QL_Steamworks_ServerIsLoggedOn`, backed by `SteamGameServer` vtable
  offset `0x20`.
- Exposed the wrapper through `platform_steamworks.h` with a disabled-build
  inline stub returning `qfalse`, preserving the repository policy that Quake
  Live online services remain opt-in.
- Updated `QL_Steamworks_ServerRequestUserStats` so the logged-on gate runs
  before the `SteamGameServerStats` request slot `0x00`.
- Extended the Steamworks harness with a mocked `SteamGameServer::BLoggedOn`
  slot, call counting, result control, and enabled/disabled exports for the new
  wrapper.
- Added executable coverage proving the logged-off path suppresses
  `SteamGameServerStats::RequestUserStats`, while the logged-on path reaches
  the retail request slot.

## Inference Boundary

Confidence is high for the vtable offset and request gate because both the
server-connected callback and constructor/bootstrap path use the same
`SteamGameServer` slot `0x20` check immediately before the same
`SteamGameServerStats` request slot. The remaining uncertainty is live backend
timing and callback cadence, which stays intentionally bounded until online
services have an explicit opt-in validation pass or documented open
replacement path.

## Parity Estimate

- Focused GameServerStats logged-on request gate:
  **before 40% -> after 94%**.
- Combined `idSteamStats` callback/value/descriptor/request-bootstrap lane:
  **before 97% -> after 98%**.
- Broader Steamworks parity remains approximately **99%**; remaining
  uncertainty is live backend behavior and other intentionally opt-in online
  service validation, not this static request gate.
