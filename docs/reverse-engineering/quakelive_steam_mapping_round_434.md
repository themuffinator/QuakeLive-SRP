# Quake Live Steam Mapping Round 434

Date: 2026-06-08

## Scope

This round tightens the split source startup path used before filesystem
initialization. The focus is the early Steam refresh that lets source builds
select a SteamID-scoped `fs_homepath` before native DLL loading.

## Evidence

- Retail `Com_Init` registers `dedicated` and calls `SteamClient_Init()` early
  at `0x004cc16e` before the later filesystem and VM startup work.
- Binary Ninja HLIL for `SteamClient_Init` starts with
  `sub_4ccd80("com_build")`; the `SteamAPI_Init()` call and all downstream
  callback/lobby/voice/stat/rich-presence bootstrap work sit inside the
  `result == 0` branch.
- Source startup deliberately splits that retail call: `Com_InitSteamClientForFilesystem()`
  performs a pre-filesystem service refresh so `FS_Startup` can derive
  `fs_homepath` from `SteamClient_GetSteamID()`, while the full
  `SteamClient_Init()` callback/command bootstrap runs later.
- Because command-line startup variables are processed before
  `Com_InitSteamClientForFilesystem()`, `Cvar_VariableIntegerValue("com_build")`
  is available even though `com_buildScript` is not registered until later.

## Source Reconstruction

- Added a `com_build` command-line guard to
  `Com_InitSteamClientForFilesystem()` before `QL_RefreshPlatformServices()`.
- Kept the existing `dedicated` guard and the later `SteamClient_Init`
  `com_buildScript` guard intact.
- Added parity assertions that bind the source guard to the HLIL
  `com_build`/`SteamAPI_Init` ordering and require the early filesystem refresh
  to skip Steam when `com_build` is active.

## Deferred Notes

- This does not move the full source `SteamClient_Init()` call back to retail's
  exact early `Com_Init` location. That larger reorder remains deferred because
  source uses the split to keep filesystem SteamID selection available while
  preserving the existing client callback/bootstrap order.

## Parity

Focused pre-filesystem Steam startup guard confidence moves from 70% to 91%.
The broader Steam launch/runtime integration slice moves from 86% to 87%.
