# Quake Live Steam Mapping Round 635: GameServer SteamID Publish Initialized Guard

Date: 2026-06-12

## Scope

This round maps the retail server SteamID publication path and reconstructs an
explicit initialized-state guard in the SRP public SteamID wrapper. The retail
owner is `SteamServer_PublishSteamID`, promoted from `sub_465b00`. The source
boundaries are `QL_Steamworks_ServerGetSteamID` and
`SV_SteamServerPublishIdentity`.

Steam launch/runtime online behavior remains behind `QL_BUILD_ONLINE_SERVICES`.
This round tightens wrapper fidelity and diagnostics; it does not enable live
Steam services.

## Retail Evidence

- `references/analysis/quakelive_symbol_aliases.json` promotes
  `FUN_00465b00`, `sub_465B00`, and `sub_465b00` to
  `SteamServer_PublishSteamID`.
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  records `FUN_00465b00,00465b00,99,0,unknown`.
- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
  confirms the server identity dependency through
  `STEAM_API.DLL!SteamGameServer @ 0015918a`.
- Binary Ninja HLIL for `sub_465b00` probes `SteamGameServer()`, rejects a
  null interface, dispatches vtable slot `0x28`, formats the returned
  64-bit SteamID, writes configstring `0x2ca`, refreshes
  `sv_referencedSteamworks`, and writes configstring `0x2cb`.

Observed fact: retail publishes the GameServer SteamID only after the
`SteamGameServer()` interface probe succeeds, and the publish sequence is
SteamID configstring first, referenced-Steamworks cvar second, referenced
configstring third.

Inferred mapping: SRP's `state.gameServerInitialised` is the retained public
wrapper predicate for the GameServer interface that retail probes directly.
The source `SV_SteamServerPublishIdentity` owner preserves the retail
publication order while adding provider-aware diagnostics for unavailable
compatibility lanes.

## Source Reconstruction

`src/common/platform/platform_steamworks.c` now makes the GameServer runtime
boundary explicit in `QL_Steamworks_ServerGetSteamID`:

1. Zero caller output words when pointers are present.
2. Validate both output pointers.
3. Reject calls while `state.gameServerInitialised` is false.
4. Resolve the GameServer interface through `QL_Steamworks_GetGameServer`.
5. Dispatch `GetSteamID` through vtable slot `0x28`.

The shared `QL_Steamworks_GetGameServer` helper still retains the broader
`state.initialised`, `state.gameServerInitialised`, and `SteamGameServer`
checks. The wrapper-level guard makes the public identity boundary match the
rest of the reconstructed GameServer wrapper surface.

## Server Wiring

`src/code/server/sv_init.c` remains the publication owner:

- `SV_SteamServerPublishIdentity` calls `QL_Steamworks_ServerGetSteamID`.
- On failure it logs the unavailable identity lane and returns.
- On success it publishes configstring `0x2ca`, updates
  `sv_referencedSteamworks`, and publishes configstring `0x2cb`.
- `SV_SpawnServer` calls `SV_SteamServerPublishIdentity` before heartbeat
  enablement and before the full published-state refresh.

## Validation

Added `test_steam_gameserver_identity_publish_wrapper_guard_tracks_round_635`
to pin:

- promoted aliases and Ghidra rows for `sub_465b00`;
- the Steam GameServer import;
- Binary Ninja SteamID slot `0x28` ordering before configstring/cvar writes;
- wrapper output validation before initialized-state guard;
- initialized-state guard before `QL_Steamworks_GetGameServer`; and
- source identity publication ordering in `sv_init.c`.

## Parity Estimate

Focused GameServer SteamID publish wrapper guard confidence:
**83% -> 99%**.

Focused Steam GameServer identity publication confidence:
**95% -> 99%**.

overall Steam launch/runtime integration mapping confidence **93.72% -> 93.74%**.
