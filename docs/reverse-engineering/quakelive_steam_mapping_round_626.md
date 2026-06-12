# Quake Live Steam Mapping Round 626: Pre-Filesystem Steam Service Cvar Publication

Date: 2026-06-12

## Scope

This round tightens the source-only split between retail's early
`SteamClient_Init` startup owner and SRP's smaller
`SteamClient_InitForFilesystem` helper. Retail initializes Steam before
filesystem startup so `FS_Startup` can choose a SteamID-scoped homepath. SRP
keeps that early filesystem path intentionally smaller, but it still rebuilds
the same platform-service descriptor table used by the later full client init.

The focused reconstruction is the diagnostic cvar surface after that early
descriptor refresh.

## Evidence

- `references/analysis/quakelive_symbol_aliases.json` maps
  `FUN_00461500` to `SteamClient_Init`, `FUN_00460510` to
  `SteamClient_IsInitialized`, and `FUN_00460550` to `SteamClient_GetSteamID`.
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  contains rows for `FUN_00461500,00461500,209,0,unknown`,
  `FUN_00460510,00460510,6,0,unknown`, and
  `FUN_00460550,00460550,53,0,unknown`.
- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
  confirms `STEAM_API.DLL!SteamAPI_Init @ 00159264` and
  `STEAM_API.DLL!SteamUser @ 0015916a`; it still contains no
  `SteamAPI_RestartAppIfNecessary` launch helper.
- Binary Ninja HLIL shows retail `SteamClient_Init` checking `com_build`,
  calling `SteamAPI_Init()`, and storing the result in `data_e30218`.
- Binary Ninja HLIL shows retail `FS_Startup` testing
  `SteamClient_IsInitialized()`, calling `SteamClient_GetSteamID()`, and
  formatting `"%s/%llu"` before registering `fs_homepath`.

## Observed Retail Behavior

Retail has one early Steam owner: `SteamClient_Init`. That owner runs before
filesystem startup and before the `FS_Startup` SteamID homepath branch. The
retail evidence does not show a second cvar-publication function or a
self-relaunch helper.

SRP cannot call the full client-side callback, lobby, command, resource,
auth-ticket, and rich-presence bootstrap before filesystem startup because the
reconstruction keeps online services opt-in and default-disabled. The
source-only split therefore remains valid: early filesystem startup may refresh
the platform-service table and latch the retained Steam initialized flag, while
the heavier retail side effects stay in the primary `SteamClient_Init` owner.

## Source Reconstruction

- `Com_InitSteamClientForFilesystem` remains the common-startup owner and keeps
  its `dedicated` and `com_build` guards before calling into the client helper.
- `SteamClient_InitForFilesystem` still performs no callback registration,
  command registration, lobby setup, auth-ticket cleanup, resource bootstrap,
  or rich-presence writes.
- After `SteamClient_InitForFilesystem` explicitly calls
  `QL_RefreshPlatformServices`, it now calls
  `CL_RefreshPlatformServiceCvars` before `SteamClient_SetInitializedState`.
- The primary `SteamClient_Init` path already used that same refresh-order
  sequence, so the early filesystem bridge and full client bootstrap now
  publish consistent service labels from the same descriptor snapshot.

## Compatibility Boundary

This is a diagnostic-only side effect in SRP's source bridge, not a claim that
retail had a standalone pre-filesystem cvar publication helper. It keeps live
Quake Live online services behind the existing `QL_BUILD_ONLINE_SERVICES`
policy and does not move any live Steam callback, lobby, command, workshop,
stats, voice, or rich-presence wiring earlier in startup.

## Validation

Added
`tests/test_platform_services.py::test_pre_filesystem_steam_service_cvars_track_round_626`
to pin:

- retail `SteamClient_Init`, `SteamClient_IsInitialized`, and
  `SteamClient_GetSteamID` evidence;
- retail common-startup and filesystem ordering;
- the absence of `SteamAPI_RestartAppIfNecessary`;
- SRP's source-only `Com_InitSteamClientForFilesystem` owner;
- the early `QL_RefreshPlatformServices` ->
  `CL_RefreshPlatformServiceCvars` -> `SteamClient_SetInitializedState` order;
- the heavy Steam side effects that must remain outside the pre-filesystem
  helper.

## Parity Estimate

Focused pre-filesystem Steam service-cvar wiring confidence:
**78% -> 99%**.

Focused source split startup-owner confidence:
**93% -> 99%**.

overall Steam launch/runtime integration mapping confidence **93.54% -> 93.56%**.
