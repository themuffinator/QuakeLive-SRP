# Quake Live Steam Mapping Round 426

Date: 2026-06-08

## Scope

This round reconstructs the Steam client initialized-state helper as a
cross-module launch/runtime boundary and carries the retail common-startup
Steam guard into source as a documented compatibility divergence.

## Evidence

- `references/analysis/quakelive_symbol_aliases.json` promotes
  `sub_460510` as `SteamClient_IsInitialized`.
- Binary Ninja HLIL for `sub_460510` is a direct return of the retained Steam
  client initialized flag at `data_e30218`.
- Retail common startup calls `SteamClient_Init()` early in `sub_4CBFD0`, then
  later checks `sub_460510() == 0 && Cvar_Find("com_build") == 0 &&
  Cvar_Find("dedicated") == 0`.
- The failure side of that guard calls `Com_Error("Failed to initialize Steam.")`
  in retail.
- The repository policy keeps Steam integration behind
  `QL_BUILD_ONLINE_SERVICES` and allows offline/default-disabled fallback, so
  source must not make normal development startup fatal simply because live
  Steam is unavailable.

## Source Reconstruction

- Promoted `SteamClient_IsInitialized()` from a private `cl_main.c` static to a
  public client helper declared in `qcommon.h`, matching the retail
  cross-module helper surface.
- Added a deterministic null-client implementation returning `qfalse`.
- Added a common-side `Com_VerifySteamClientStartup()` guard that mirrors the
  retail condition shape:
  - already initialized: no action;
  - `com_build` active: no action;
  - dedicated startup: no action;
  - otherwise log the exact retail fatal edge as a compatibility divergence.
- Called the guard after `SteamClient_Init()` and `CL_Init()` in `Com_Init`.
  This is slightly later than retail's exact check but uses the source's
  retained full callback/bootstrap split and preserves deterministic offline
  launch behavior.

## Deferred Notes

- The exact retail startup ordering still differs: retail runs the full
  `SteamClient_Init()` before filesystem startup, while source keeps a smaller
  pre-filesystem refresh in `Com_InitSteamClientForFilesystem()` and runs the
  full callback/command bootstrap later.
- A future dedicated startup-order pass can reduce that gap, but it should
  first isolate SteamID-scoped filesystem selection, callback registration, and
  cvar availability so the change does not regress retail replacement launches.

## Parity

Focused Steam initialized-state guard confidence moves from 65% to 86%.
The broader Steam launch/runtime integration slice moves from 78% to 79%.
