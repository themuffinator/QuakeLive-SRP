# Quake Live Steam Mapping Round 435

Date: 2026-06-08

## Scope

This round closes the lazy Steam refresh gap left by the split source startup
path. The focus is making wrapper and frame paths obey the same retained
initialization flag semantics as retail after `SteamClient_Init` is skipped.

## Evidence

- Binary Ninja HLIL for retail `SteamClient_GetSteamID` (`sub_460550`) returns
  `0` while `data_e30218` is clear, and only calls `SteamUser()->GetSteamID()`
  when the retained Steam initialized flag is already set.
- Binary Ninja HLIL for `SteamApps_BIsSubscribedApp` (`sub_460590`) follows the
  same pattern: if `data_e30218` is clear it returns `0`; otherwise it calls
  `SteamApps()->BIsSubscribedApp(...)`.
- Binary Ninja HLIL for `SteamClient_Frame` (`sub_461d40`) gates the whole
  frame pump on `data_e30218 != 0`; it does not attempt to initialize Steam
  from the frame loop.
- Source builds intentionally use dynamic/optional platform services, so
  wrapper calls previously used `QL_RefreshPlatformServices()` to recover from
  launch-time unavailability. Without a `com_build` guard, those lazy refreshes
  could still probe Steam after the source-only pre-filesystem guard and full
  `SteamClient_Init` guard had skipped Steam.

## Source Reconstruction

- Added `SteamClient_ShouldRefreshPlatformServices()` as the common source-side
  guard for lazy Steam refreshes outside the explicit `SteamClient_Init` owner.
- The helper rejects both the registered `com_buildScript` cvar and the early
  command-line `com_build` value.
- Applied the guard before `QL_RefreshPlatformServices()` in:
  - `SteamClient_GetSteamID`
  - `SteamClient_GetAuthSessionTicket`
  - `SteamApps_BIsSubscribedApp`
  - `SteamUGC_GetItemDownloadInfo`
  - `SteamUtils_GetIPCountry`
  - `SteamClient_RecoverCallbackBootstrap`
  - `SteamClient_Frame`
- Kept `SteamClient_Init` as the explicit bootstrap path; its own retail-mapped
  `com_build` guard remains the authority for normal launch initialization.

## Deferred Notes

- Source still intentionally supports recovery from launch-time Steam
  unavailability in non-`com_build` launches. This is a documented
  compatibility divergence from retail's direct `steam_api.dll` import model.

## Parity

Focused lazy Steam refresh guard confidence moves from 67% to 93%.
The broader Steam launch/runtime integration slice moves from 87% to 88%.
