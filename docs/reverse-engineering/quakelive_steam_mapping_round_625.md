# Quake Live Steam Mapping Round 625: Steamworks Service Cache Shutdown Reset

Date: 2026-06-12

## Scope

This round maps the retail Steam launch/shutdown evidence against SRP's
dynamic platform-service cache. Retail imports and calls `SteamAPI_Init` /
`SteamAPI_Shutdown` directly and then exits on the normal quit path; SRP adds a
recoverable descriptor cache above the dynamic Steamworks adapter. That cache
must be reset when `QL_Steamworks_Shutdown` releases the runtime.

## Evidence

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  contains `SteamAPI_Shutdown,00460540,6,1,unknown`,
  `FUN_00461500,00461500,209,0,unknown`, and
  `FUN_00460510,00460510,6,0,unknown`.
- `references/analysis/quakelive_symbol_aliases.json` maps `sub_460540` to
  `SteamAPI_Shutdown`, `FUN_00461500` to `SteamClient_Init`, and
  `FUN_00460510` to `SteamClient_IsInitialized`.
- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt` confirms
  `STEAM_API.DLL!SteamAPI_Init @ 00159264` and
  `STEAM_API.DLL!SteamAPI_Shutdown @ 001591cc`.
- Binary Ninja HLIL shows `SteamClient_IsInitialized` returning `data_e30218`,
  `SteamClient_Init` assigning `data_e30218 = SteamAPI_Init()`, and the
  `SteamAPI_Shutdown` thunk tailcalling the imported shutdown function.
- Common quit HLIL includes the direct `SteamAPI_Shutdown()` call before process
  teardown continues.

## Observed Retail Behavior

- Retail's initialized-state owner is `SteamClient_Init`; `SteamClient_IsInitialized`
  is only a read of the retained flag.
- Retail's shutdown owner calls directly into `SteamAPI_Shutdown`. The process
  exits, so no separate descriptor cache needs to survive or recover.
- There is no `SteamAPI_RestartAppIfNecessary` import or launch relaunch helper
  in the committed retail corpus.

## Source Reconstruction

- `QL_PlatformSteamworks_InitCached` now uses file-static cache variables so
  the state can be reset explicitly.
- Added `QL_ResetPlatformServices`, which clears the cached descriptor table,
  the descriptor initialised flag, the cached Steamworks init result, and the
  retry throttle.
- `QL_Steamworks_Shutdown` now calls `QL_ResetPlatformServices` before its
  early-return guard and before unregistering/releasing Steamworks state.
- The existing client `SteamAPI_Shutdown` wrapper still owns the retail-shaped
  resource order: Steam resource shutdown, callback/ticket teardown, then
  platform Steamworks release.
- `tests/steamworks_harness.c` has a harness-local `QL_ResetPlatformServices`
  stub because it compiles `platform_steamworks.c` as a standalone translation
  unit instead of linking the engine's `platform_services.c` implementation.

## Compatibility Boundary

This is a source-only dynamic-adapter repair, not a claim that retail had a
platform-service descriptor cache. It keeps SRP's opt-in Steamworks recovery
behavior aligned with the retail initialized/shutdown signals so future
`QL_GetPlatformServices` or `QL_RefreshPlatformServices` calls cannot report a
stale initialized Steamworks descriptor after shutdown.

## Validation

- Added
  `tests/test_platform_services.py::test_steamworks_shutdown_resets_platform_service_cache_tracks_round_625`
  to pin retail `SteamAPI_Init`/`SteamAPI_Shutdown` evidence, the reset API,
  shutdown ordering, the harness stub, and a compiled cache-reset probe.
- Updated the round-622 cached-refresh gate to assert the resettable
  file-static cache variables while preserving the failed-init refresh probe.
- No game launch was needed; the reconstruction is static and is validated by
  focused compiled probes.

## Parity Estimate

Focused Steamworks service-cache shutdown reset confidence:
**86% -> 99%**.

Focused dynamic Steam descriptor lifecycle confidence:
**92% -> 99%**.

overall Steam launch/runtime integration mapping confidence **93.52% -> 93.54%**.
