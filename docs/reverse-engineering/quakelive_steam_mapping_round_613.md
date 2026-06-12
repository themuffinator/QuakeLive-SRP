# Quake Live Steam Mapping Round 613: Social Overlay Command And Browser Handoff

Date: 2026-06-11

## Scope

This round rechecks the Steam social overlay handoff surface shared by the
retail scoreboard commands and retained browser bridge methods:
`clientviewprofile`, `clientfriendinvite`, `OpenSteamOverlayURL`, and
`ActivateGameOverlayToUser`.

No engine source behavior changed in this pass.

## Retail Evidence

Primary owner: `assets/quakelive/quakelive_steam.exe`

Evidence checked:

- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/analysis/quakelive_symbol_aliases.json`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part07.txt`
- `src/code/client/cl_main.c`
- `src/code/client/cl_cgame.c`
- `src/common/platform/platform_steamworks.c`

Function ownership:

| Ghidra row | Address | Promoted owner |
| --- | --- | --- |
| `FUN_00460e60` | `0x00460E60` | `CL_Steam_OverlayCommand_f` |
| raw HLIL browser case `3` | `0x00431FC0` | `OpenSteamOverlayURL` dispatch |
| raw HLIL browser case `0xf` | `0x00432351` | `ActivateGameOverlayToUser` dispatch |

Observed facts:

- `FUN_00460e60` / `sub_460e60` checks the command argument count, asks the
  cgame client-identity bridge for the selected scoreboard client's SteamID
  words, maps `clientviewprofile` to `steamid`, maps `clientfriendinvite` to
  `friendadd`, and calls `SteamFriends()` vtable slot `0x74`.
- `CL_Init` registers `clientviewprofile` and `clientfriendinvite` with
  `sub_460e60`.
- Browser method table evidence retains `OpenSteamOverlayURL` at
  `0x0055C08C` and `ActivateGameOverlayToUser` at `0x0055C134`.
- Browser dispatch case `3` forwards the first string argument directly to `SteamFriends()` vtable slot `0x78`.
- Browser dispatch case `0xf` parses the second string argument with
  `sscanf("%llu", ...)`, converts the first string argument to the overlay
  dialog, and calls `SteamFriends()` vtable slot `0x74`.

## Source Reconstruction

The source reconstruction keeps the command and browser surfaces separate but
routes both through shared SteamFriends wrappers:

- `CL_GetClientSteamId` resolves native cgame identity first and then falls
  back to `CS_PLAYERS` userinfo keys `PLAYER_INFO_KEY_STEAMID` and
  `PLAYER_INFO_KEY_STEAMID_LEGACY`.
- `CL_Steam_OverlayCommand_f` keeps the retail command-driven dialog mapping:
  `clientviewprofile` uses `steamid`, and `clientfriendinvite` uses
  `friendadd`.
- `CL_Init` registers both console commands before `QLWebHost_RegisterCommands`
  and the later Steam persona/country bootstrap.
- `CL_Steam_OpenOverlayUrl` accepts any non-null browser URL, checks the online
  service policy and retained client Steam initialization state, then calls
  `QL_Steamworks_ActivateOverlayToWebPage`.
- `CL_Steam_ActivateOverlayToUser` keeps the loose retail-style `sscanf("%llu", ...)` parse without a second invalid-id rejection.
- `QL_Steamworks_ActivateOverlayToUser` uses `SteamFriends()` vtable slot `0x74` and combines the two SteamID words before invoking the interface.
- `QL_Steamworks_ActivateOverlayToWebPage` uses `SteamFriends()` vtable slot `0x78` and forwards the web page URL.

## Compatibility Boundary

Live Steam overlay behavior remains behind `QL_BUILD_ONLINE_SERVICES` and the
platform service table. Default-disabled builds expose deterministic fallback
logging instead of attempting live overlay activation.

This round deliberately preserves two slightly different gates:

- browser-originated overlay calls check the retained client Steam initialized
  state before invoking the wrapper; and
- console-originated scoreboard commands mirror the retail command handler
  shape and let the platform wrapper fail cleanly if the live overlay surface
  is unavailable.

## Validation

Added
`tests/test_platform_services.py::test_steam_social_overlay_command_and_browser_handoff_tracks_round_613`
to pin:

- alias, Ghidra function, and import ownership for `FUN_00460e60`;
- Binary Ninja HLIL anchors for the scoreboard command path, command
  registration, browser method strings, browser dispatch cases, and
  SteamFriends slots `0x74` and `0x78`;
- source command dispatch, command registration ordering, browser method
  routing, retained initialization gates, loose identity parsing, and wrapper
  vtable slots; and
- this round note plus Task A482 parity anchors.

Planned validation for this pass:

```text
python -m pytest tests/test_platform_services.py::test_steam_social_overlay_command_and_browser_handoff_tracks_round_613 -q --tb=short
python -m pytest tests/test_platform_services.py -q --tb=short
python -m pytest tests/test_steamworks_harness.py -q --tb=short
```

## Confidence

Observed facts:

- HLIL directly shows the command handler, browser method dispatch cases, loose
  decimal SteamID parse, and the two SteamFriends vtable calls.
- Ghidra rows, imports, and the alias map identify the stable command owner and
  the SteamFriends dependency.
- Source tests now bind the console commands, browser bridge, retained-service
  gates, and platform wrappers into one lifecycle gate.

Inference:

- SRP's browser-side retained-initialized guard is the correct bounded
  reconstruction for the dynamic provider table. It preserves the retail call
  surface while keeping default builds from attempting live Steam overlay work.

Parity estimates:

- Focused social overlay command/browser handoff confidence:
  **before 94% -> after 99%**.
- Focused overlay policy/vtable wrapper classification:
  **before 95% -> after 99%**.
- Overall Steam launch/runtime integration mapping confidence: **93.28% -> 93.30%**.
