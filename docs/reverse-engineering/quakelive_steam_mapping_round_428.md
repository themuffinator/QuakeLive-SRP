# Quake Live Steam Mapping Round 428

Date: 2026-06-08

## Scope

This round tightens the Steam launch/runtime app-id surface around
`SteamClient_Init` and the retained `stats_clear` command registration gate.

## Evidence

- `references/analysis/quakelive_symbol_aliases.json` maps `sub_460520` to
  `CL_Steam_ClearStats_f` and `sub_461500` to `SteamClient_Init`.
- Binary Ninja HLIL for `sub_460520` is the direct
  `SteamUserStats()->ResetAllStats(1)` wrapper.
- Binary Ninja HLIL for `SteamClient_Init` registers `stats_clear` only when
  `SteamUtils()->GetAppID()` returns `0x54100`.
- The source already names the public Steam launch app id as
  `QL_STEAM_APPID_PUBLIC_RETAIL` (`282440`) and the retail reference app id as
  `QL_STEAM_APPID_REFERENCE_RETAIL` (`0x54100`).

## Source Reconstruction

- Replaced the raw `0x54100u` stats-clear gate in
  `CL_Steam_ShouldRegisterStatsClear()` with
  `QL_STEAM_APPID_REFERENCE_RETAIL`.
- Updated parity gates to assert the named constant while still checking the
  HLIL-backed app-id value.

## Deferred Notes

- `QL_STEAM_APPID_PUBLIC_RETAIL` remains the app id used for public Steam
  server-browser discovery and normal `steam://rungameid/282440` launches.
- `QL_STEAM_APPID_REFERENCE_RETAIL` remains a narrow retail-reference gate for
  the stats reset command, not a replacement for the public app id.

## Parity

Focused Steam app-id gate source clarity moves from 88% to 95%.
The broader Steam launch/runtime integration slice remains 80%, but with lower
future-regression risk around magic app-id literals.
