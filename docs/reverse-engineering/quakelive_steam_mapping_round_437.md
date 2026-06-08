# Quake Live Steam Mapping Round 437

Date: 2026-06-08

## Scope

This round reconstructs the client identity bootstrap lane so persona and
country seeding remain consumers of the retained Steam initialized state rather
than hidden Steam initialization owners.

## Evidence

- Binary Ninja HLIL for `SteamClient_SyncPersonaNameCvar` (`sub_460610`) first
  checks `com_build`, then consumes `SteamFriends()`. If the friends interface
  is unavailable, retail sets `name` to `anon`.
- Binary Ninja HLIL for `SteamUtils_GetIPCountry` (`sub_460690`) returns `0`
  while `data_e30218` is clear, and only jumps to `SteamUtils()->GetIPCountry`
  after the retained Steam initialized flag is set.
- Binary Ninja HLIL for client initialization calls `sub_460610()` after
  web-host command registration and seeds `country` through `sub_460690()` only
  when the country cvar is still empty.
- The Ghidra symbol alias map promotes `sub_460610` as
  `SteamClient_SyncPersonaNameCvar` and `sub_460690` as
  `SteamUtils_GetIPCountry`, matching the owning source functions.

## Source Reconstruction

- Removed direct `QL_Steamworks_Init()` calls from
  `SteamClient_SyncPersonaNameCvar()` and `CL_Steam_SeedCountryCvar()`.
- Reused the source-side `SteamClient_ShouldRefreshPlatformServices()` guard so
  identity seeding respects the retail `com_build` skip and early command-line
  `com_build` value.
- Gated persona and country seeding on `SteamClient_IsInitialized()` before
  consuming Steam identity helpers.
- Kept the retail persona fallback by setting `name` to `anon` when the
  retained Steam identity state is unavailable.

## Deferred Notes

- The lower platform wrappers still support documented source compatibility
  lazy-refresh behavior for non-startup helper surfaces. The client identity
  seeders no longer participate in that compatibility bootstrap.

## Parity

Focused client identity bootstrap owner confidence moves from 74% to 95%.
The broader Steam launch/runtime integration slice moves from 89% to 90%.
