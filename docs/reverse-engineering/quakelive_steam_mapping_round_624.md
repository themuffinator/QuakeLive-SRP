# Quake Live Steam Mapping Round 624: GameServer Guarded Cvar Side-Effect Wiring

Date: 2026-06-12

## Scope

This round tightens the `SteamServer_Init` (`sub_466ed0` / `FUN_00466ed0`)
source reconstruction after the round-623 `com_build` guard. The focus is the
side-effect boundary around cvar registration and live Steam GameServer startup
inputs in `Com_InitSteamGameServer`.

## Evidence

- Ghidra metadata still identifies the owner binary as `quakelive_steam.exe`.
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  contains `FUN_00466ed0,00466ed0,495,0,unknown`.
- `references/analysis/quakelive_symbol_aliases.json` maps `FUN_00466ed0`,
  `sub_466ED0`, and `sub_466ed0` to `SteamServer_Init`.
- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
  contains `STEAM_API.DLL!SteamGameServer_Init @ 00159314`.
- Binary Ninja HLIL for `sub_466ed0` shows `net_ip` and `net_port` setup before
  `sub_4ccd80("com_build")`, then `sv_vac`, `SteamGameServer_Init`, and
  `sv_setSteamAccount` usage only inside the `com_build == 0` path.

## Observed Retail Behavior

- Retail performs the pre-guard network setup with `net_ip` and `net_port`.
- Retail checks `com_build` before allocating callbacks, reading `sv_vac`,
  calling `SteamGameServer_Init`, choosing the UGC owner, setting dedicated
  state, reading `sv_setSteamAccount`, disabling heartbeats, and publishing
  product/game-dir metadata.
- Retail passes the fixed `data_5674d4` version literal to
  `SteamGameServer_Init`; there is no observed `sv_steamServerVersion` cvar in
  this function.

## Source Reconstruction

- `Com_InitSteamGameServer` now keeps only `net_ip`, `net_port`, IP packing, and
  the `com_build` probe ahead of the guard.
- `sv_vac` and SRP's `sv_steamServerVersion` compatibility override are
  registered only after `com_build` is false and before
  `QL_Steamworks_ServerInitWithVersion`.
- `sv_setSteamAccount` is now registered after successful GameServer init and
  dedicated-state publication, immediately before reading the account string
  and calling `QL_Steamworks_ServerLogOn`.
- `sv_steamServerVersion` remains a source compatibility override for the
  retained dynamic Steamworks adapter; the default path still resolves to the
  retail `data_5674d4` value.

## Compatibility Boundary

The repository keeps the intentional online-service divergence: live Steam
GameServer publication remains opt-in under `QL_BUILD_ONLINE_SERVICES` /
`QL_BUILD_STEAMWORKS`, and failure to initialise the dynamic Steamworks adapter
uses the compatibility-only fallback instead of retail's fatal path. This round
only reduces build-script side effects before that divergence begins.

## Validation

- Added
  `tests/test_platform_services.py::test_steam_gameserver_guarded_cvar_side_effect_wiring_tracks_round_624`
  to pin the retail HLIL ordering, the absence of `sv_steamServerVersion` in
  retail, the source-side post-guard cvar registrations, this note, the
  round-623 closure note, and the implementation-plan entry.
- No game launch was needed; the reconstruction is static and directly backed
  by committed Binary Ninja/Ghidra evidence.

## Parity Estimate

Focused guarded GameServer cvar side-effect confidence:
**88% -> 99%**.

Focused live GameServer version/VAC/account wiring confidence:
**94% -> 99%**.

overall Steam launch/runtime integration mapping confidence **93.50% -> 93.52%**.
