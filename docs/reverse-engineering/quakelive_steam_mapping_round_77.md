# `quakelive_steam.exe` Mapping Round 77

## Scope

This round closes the cvar-owned Steam game-tags tranche inside retail
`sub_466260` / `SteamServer_UpdatePublishedState`.

## Evidence

- HLIL shows `sub_466260` fetching `g_instagib`, `g_gravity`,
  `g_rrInfected`, `g_vampiricDamage`, `g_quadhog`, `sv_tags`,
  `g_gametype`, and `sv_cheats`, then building a comma-delimited game-tags
  string and publishing it through `SteamGameServer()->vtable[0x54 / 4]`.
- The same retail owner registers `sv_tags` in `SV_Init` through
  `Cvar_Get( "sv_tags", "", CVAR_ARCHIVE )`.
- The cvar-driven literals recovered from the binary are:
  `cheats`, `instagib`, `lowgrav`, `highgrav`, `vampiric`, `infected`,
  `quadhog`, and the short gametype tags `ffa`, `duel`, `race`, `tdm`,
  `clanarena`, `ctf`, `oneflag`, `overload`, `harvester`, `freezetag`,
  `domination`, `a&d`, `redrover`.

## Reconstruction

- Added `QL_Steamworks_ServerSetGameTags()` in the shared Steamworks host
  layer and bound it to the mapped `SteamGameServer` string slot at
  `vtable[0x54 / 4]`.
- Registered `sv_tags` in `SV_Init` and exposed it as a retained server cvar.
- Reconstructed the cvar-owned retail tag builder in `sv_main.c`:
  gametype short tag, `sv_cheats`, `g_instagib`, gravity mode,
  `g_vampiricDamage`, `g_rrInfected` in Red Rover, `g_quadhog` in FFA, and
  the appended `sv_tags` payload with retail comma handling.
- Wired the rebuilt tag string into `SV_SteamServerUpdatePublishedState()`
  so Steam publication now covers the mapped tag seam as well as the round-76
  description, rules, and per-player publication work.

## Explicitly Deferred

Retail appends an additional descriptor-owned tag tail from the
`data_13e17d8 + 0x14 .. +0x30` range after the cvar-owned tranche. That owner
is still only mapped in the host binary, so this round intentionally stops at
the stable writable cvar surface instead of inventing placeholder state.

## Verification

- `python -m pytest tests/test_steamworks_harness.py tests/test_platform_services.py tests/test_ui_menu_files.py -q`
