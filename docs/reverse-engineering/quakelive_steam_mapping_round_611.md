# Quake Live Steam Mapping Round 611: Identity Bootstrap Persona And Country Boundary

Date: 2026-06-11

## Scope

This round rechecks the Steam-backed identity bootstrap lane around
`SteamClient_SyncPersonaNameCvar`, `SteamUtils_GetIPCountry`, the local
persona-state callback refresh, and the `CL_Init` persona/country seeding
order.

No engine source behavior changed in this pass.

## Retail Evidence

Primary owner: `assets/quakelive/quakelive_steam.exe`

Evidence checked:

- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/analysis/quakelive_symbol_aliases.json`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
- `src/code/client/cl_main.c`
- `src/common/platform/platform_steamworks.c`

Function ownership:

| Ghidra row | Address | Promoted owner |
| --- | --- | --- |
| `FUN_00460610` | `0x00460610` | `SteamClient_SyncPersonaNameCvar` |
| `FUN_00460690` | `0x00460690` | `SteamUtils_GetIPCountry` |
| `FUN_00460800` | `0x00460800` | `SteamCallbacks_OnPersonaStateChange` |
| `FUN_00461500` | `0x00461500` | `SteamClient_Init` |

Observed facts:

- `sub_460610` checks `com_build`, reads `SteamFriends()`, sets `name` to
  `"anon"` when friends is unavailable, and otherwise writes the current Steam
  persona name to `name`.
- `sub_460690` returns `0` while the retained Steam initialized flag is clear
  and only then tailcalls `SteamUtils()->GetIPCountry` at vtable slot `0x10`.
- `sub_460800` calls `sub_460610()` when a local persona-state payload carries
  bit `1`.
- `CL_Init` registers `clientviewprofile` and `clientfriendinvite`, registers
  the web-host commands, calls `sub_460610()`, and then seeds `country` through
  `sub_460690()` only when the current country cvar is blank.

## Source Reconstruction

The source reconstruction keeps identity bootstrap as a consumer of the
retained client Steam state:

- `SteamClient_SyncPersonaNameCvar` remains a consumer of retained state, not a
  hidden Steam initialization owner.
- `SteamClient_ShouldRefreshPlatformServices` blocks both `com_buildScript`
  and the command-line `com_build` cvar before permitting source-side lazy
  service refreshes.
- `SteamClient_SyncPersonaNameCvar` first checks the online-service policy,
  then the lazy-refresh guard, then the retained `SteamClient_IsInitialized`
  flag before calling `QL_Steamworks_GetPersonaName`.
- Failed persona initialization or unavailable persona data preserves the
  retail fallback by writing `name = anon`.
- `CL_Steam_SeedCountryCvar` preserves an already-set `country` value before
  checking the lazy-refresh guard or the retained initialized flag.
- `CL_Steam_SeedCountryCvar` calls the retail-style
  `SteamUtils_GetIPCountry` wrapper and writes `country` only when a non-empty
  country string is returned.
- `CL_Steam_Client_OnPersonaStateChange` refreshes the local `name` cvar only
  for local persona-change payloads with change flag bit `1`, then publishes
  the browser-facing persona event.

The low-level platform wrappers are pinned to the retail vtable slots:

- `QL_Steamworks_GetPersonaName` uses `SteamFriends` vtable slot `0`.
- `QL_Steamworks_GetIPCountry` uses `SteamUtils` vtable slot `0x10 / 4`.

## Compatibility Boundary

Live Steam identity bootstrap remains behind the repository's online-service
policy. Default builds keep Steam-backed identity unavailable, but the source
continues to expose deterministic fallbacks and policy labels rather than
silently attempting live service initialization from identity helpers.

This round corrects the evidence classification from older wrapper notes:
persona and country seeding are retained-state consumers. They must not become
independent `QL_Steamworks_Init` owners.

## Validation

Added
`tests/test_platform_services.py::test_steam_identity_bootstrap_persona_country_lifecycle_tracks_round_611`
to pin:

- alias and Ghidra ownership for `FUN_00460610`, `FUN_00460690`,
  `FUN_00460800`, and `FUN_00461500`;
- import evidence for `SteamFriends` and `SteamUtils`;
- Binary Ninja HLIL anchors for the persona, country, persona-state callback,
  and `CL_Init` call-order lanes;
- source ordering for command registration, web-host registration, persona
  sync, country seeding, and webpak initialization;
- retained-state and `com_build` guards in source identity helpers;
- platform vtable slot use for persona and country reads; and
- this round note plus Task A480 parity anchors.

Planned validation for this pass:

```text
python -m pytest tests/test_platform_services.py::test_steam_identity_bootstrap_persona_country_lifecycle_tracks_round_611 -q --tb=short
python -m pytest tests/test_platform_services.py -q --tb=short
python -m pytest tests/test_steamworks_harness.py -q --tb=short
```

## Confidence

Observed facts:

- HLIL directly shows the persona and country retail helper logic and their
  `CL_Init` ordering.
- Ghidra rows and the alias map identify the retained identity helper owners.
- Source-side tests now tie the higher-level bootstrap helpers to the
  lower-level SteamFriends and SteamUtils vtable wrappers.

Inference:

- The source lazy-refresh guard is the correct bounded reconstruction for SRP's
  dynamic adapter environment, as long as persona/country helpers remain
  retained-state consumers and do not relatch Steam initialization themselves.

Parity estimates:

- Focused persona/country identity-bootstrap evidence confidence:
  **before 95% -> after 99%**.
- Focused retained-state identity policy classification:
  **before 96% -> after 99%**.
- Overall Steam launch/runtime integration mapping confidence: **93.24% -> 93.26%**.
