# Quake Live Steam Mapping Round 623: GameServer com_build Bootstrap Guard

Date: 2026-06-12

## Scope

This round maps the retail dedicated GameServer bootstrap skip used during
build-script runs. The owning retail function is `SteamServer_Init` (`sub_466ed0` / `FUN_00466ed0`)
in `quakelive_steam.exe`; the reconstructed source owner is
`Com_InitSteamGameServer` in `src/code/qcommon/common.c`.

## Evidence

- Ghidra metadata identifies the retail owner as `quakelive_steam.exe`,
  x86/Windows, with `5473` functions, `351` imports, and two exports.
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  contains `FUN_00466ed0,00466ed0,495,0,unknown`.
- `references/analysis/quakelive_symbol_aliases.json` promotes
  `FUN_00466ed0`, `sub_466ED0`, and `sub_466ed0` to `SteamServer_Init`.
- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
  contains `STEAM_API.DLL!SteamGameServer_Init @ 00159314`.
- Binary Ninja HLIL in
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
  shows the retail bootstrap reading `net_ip`, registering `net_port`, packing
  the IP bytes, then checking `sub_4ccd80("com_build")`.

## Observed Retail Behavior

- `SteamServer_Init` only performs the live Steam GameServer side effects when
  `data_e30358 == 0` and `sub_4ccd80("com_build") == 0`.
- The `com_build` guard wraps callback allocation, `sv_vac` lookup,
  `SteamGameServer_Init`, the fatal `"Failed to initialize Steam GS API."`
  path, UGC owner selection, `SetDedicated`, logon/logon-anonymous,
  heartbeats disabled, product `"Quake Live"`, game dir `"baseq3"`, and the
  `"Steam Gameserver initialized.\n"` print.
- The guard is a runtime cvar-value probe, not a dependency on a global
  `com_buildScript` pointer.

## Source Reconstruction

- `Com_InitSteamGameServer` now mirrors the retail skip with
  `Cvar_VariableIntegerValue( "com_build" )` after the net-port/IP/version
  setup and before any Steam GameServer debug print or
  `QL_Steamworks_ServerInitWithVersion` call.
- This direct cvar lookup is deliberate: SRP calls `Com_InitSteamGameServer`
  during `Com_Init` before assigning `com_buildScript = Cvar_Get( "com_build",
  "0", 0 );`.
- The same guard applies to network restarts because `NET_Restart` funnels
  through `Com_InitSteamGameServer` after `QL_Steamworks_ServerShutdown` and
  `NET_Config`.

## Compatibility Boundary

Retail fatals if `SteamGameServer_Init` fails. SRP intentionally keeps the
repository policy divergence: Quake Live-only online services remain behind
`QL_BUILD_ONLINE_SERVICES` / `QL_BUILD_STEAMWORKS`, default disabled, and failed
live GameServer bootstrap keeps the compatibility-only publication fallback.
The new `com_build` guard prevents live-service side effects in build-script
mode without changing that fallback policy.

## Validation

- Added
  `tests/test_platform_services.py::test_steam_gameserver_com_build_guard_tracks_round_623`
  to pin the alias, Ghidra row, import row, HLIL guard ordering, source guard,
  startup-order reason for avoiding `com_buildScript`, restart reuse, this note,
  and the implementation-plan entry.
- No game launch was needed; this is static source reconstruction against the
  committed Binary Ninja and Ghidra corpora.

## Parity Estimate

Focused GameServer `com_build` bootstrap guard confidence:
**76% -> 98%**.

Focused dedicated/live-service startup side-effect containment confidence:
**94% -> 99%**.

overall Steam launch/runtime integration mapping confidence **93.48% -> 93.50%**.

## Open Questions

- Round 624 closes this ordering question: `sv_vac`, the source-only
  `sv_steamServerVersion` override, and `sv_setSteamAccount` registration now
  sit behind the `com_build` guard, leaving only the retail-shaped net/IP setup
  ahead of the skip.
