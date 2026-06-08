# Quake Live Steam Mapping Round 430

Date: 2026-06-08

## Scope

This round tightens the Steam initialization/app-id ownership split. The goal
is to keep `QL_Steamworks_Init()` from probing `SteamUtils()->GetAppID()` as a
logging side effect, leaving app-id reads to the retail-mapped owners that
actually need them.

## Evidence

- Binary Ninja HLIL for `SteamClient_Init` (`sub_461500`) calls
  `SteamAPI_Init()`, initializes callback/lobby/micro owners, registers voice
  commands, and probes `SteamUtils()->GetAppID()` only for the `stats_clear`
  command gate.
- Binary Ninja HLIL for the retained app-id wrapper uses the
  `SteamUtils` vtable slot at `0x24 / 4`.
- Round 428 names the `stats_clear` gate as
  `QL_STEAM_APPID_REFERENCE_RETAIL` (`0x54100`) while leaving
  `QL_STEAM_APPID_PUBLIC_RETAIL` (`282440`) as the public Steam launch app id.
- The Steamworks harness counts wrapper-level `GetAppID` calls, so an
  init-time logging probe obscures the real app-id owners.

## Source Reconstruction

- Changed `QL_Steamworks_Init()` to log successful initialization without
  calling `QL_Steamworks_GetAppID()`.
- Added a parity gate asserting that `QL_Steamworks_Init()` does not invoke
  `QL_Steamworks_GetAppID()` and that app-id reads stay in the named wrapper
  and the retail-mapped caller surfaces.

## Deferred Notes

- This keeps the source's provider-level diagnostic log, but avoids adding a
  non-retail SteamUtils call during the core init path.
- Live online services remain opt-in under the existing build/runtime policy.

## Parity

Focused Steam initialization/app-id ownership confidence moves from 82% to
91%. The broader Steam launch/runtime integration slice moves from 82% to 83%.
