# Quake Live Steam Host Mapping Round 76

## Scope

This round closes the next bounded `quakelive_steam.exe` Steam game-server
ownership seam that was still mapped in the committed corpus but absent in
writable source after the earlier bootstrap and metadata publication passes:

- `sub_466260`: `SteamServer_UpdatePublishedState`
- the adjacent `SteamGameServer` publication slots that push dynamic
  server/browser state

The evidence base for this pass stayed inside the committed references:

- `references/hlil/quakelive/quakelive_steam.exe/`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `docs/reverse-engineering/quakelive_steam_mapping_round_01.md`
- `docs/mapping-ref/quakelive_steam_mapping_report.md`
- `src/common/platform/platform_steamworks.c`
- `src/code/server/sv_main.c`
- `src/code/server/sv_init.c`

## `sub_466260`: `SteamServer_UpdatePublishedState`

The committed HLIL around `00466260` shows a clean writable owner for Steam
game-server publication state:

1. slot `0x30 / 4` publishes the max-player count on the full refresh path
2. slot `0x40 / 4` publishes password protection when `g_needpass` changes
3. slot `0x38 / 4` publishes the current hostname
4. slot `0x3c / 4` publishes the current map name
5. slot `0x50 / 4` publishes `"g_redScore"` and `"g_blueScore"` during the
   periodic refresh path
6. slot `0x6c / 4` publishes per-player Steam identity, decorated display
   name, and score
7. slot `0x34 / 4` publishes the live bot count after the player pass
8. slot `0x08 / 4` publishes the current game description from the mapped
   gametype label table

The writable source now reconstructs those game-server publication shims in
`src/common/platform/platform_steamworks.c` as:

- `QL_Steamworks_ServerSetGameDescription`
- `QL_Steamworks_ServerSetMaxPlayerCount`
- `QL_Steamworks_ServerSetBotPlayerCount`
- `QL_Steamworks_ServerSetServerName`
- `QL_Steamworks_ServerSetMapName`
- `QL_Steamworks_ServerSetPasswordProtected`
- `QL_Steamworks_ServerSetKeyValue`
- `QL_Steamworks_ServerUpdateUserData`

## Writable Owner In `sv_main.c`

The retained source now reconstructs the mapped owner directly as
`SV_SteamServerUpdatePublishedState( qboolean fullUpdate )` in
`src/code/server/sv_main.c`.

The restored owner:

- publishes the game-server max slots from `sv_maxclients`
- tracks `g_needpass` and mirrors the passworded state to Steam
- republishes hostname, map name, and game description from the live cvars
- refreshes team scores through direct `"g_redScore"` / `"g_blueScore"`
  key-value writes
- walks connected clients, prefixes bot names with `"(Bot) "`, and republishes
  Steam user data from `SV_GetClientSteamId()` plus
  `SV_GameClientNum( i )->persistant[PERS_SCORE]`
- republishes the final live bot count

The retained spawn/frame ownership now matches the mapped retail split:

- `SV_SpawnServer()` performs the full refresh path with
  `SV_SteamServerUpdatePublishedState( qtrue )`
- `SV_Frame()` performs the steady-state owner call with
  `SV_SteamServerUpdatePublishedState( qfalse )`

This keeps the reconstruction bounded to the server-owned Steam publication
surface that the retail HLIL makes explicit, while leaving the larger
unreconstructed game-tags and rule-string tranche in `sub_466260` for a later
pass.

## Verification

The updated source is covered by:

- `tests/test_steamworks_harness.py`
- `tests/test_platform_services.py`
- `tests/test_ui_menu_files.py`

Command run:

```text
python -m pytest tests/test_steamworks_harness.py tests/test_platform_services.py tests/test_ui_menu_files.py -q
```

Result:

- `67 passed`

## Outcome

This round did not add new address aliases. It consumed already-mapped
`quakelive_steam.exe` ownership in three ways:

- the shared Steamworks layer now exposes the mapped dynamic
  `SteamGameServer` publication slots instead of leaving them implicit in HLIL
- the retained server host now owns the mapped full-refresh and steady-state
  `SteamServer_UpdatePublishedState` flow in writable source
- the live Steam publication path now republishes player Steam identities,
  scores, bot count, and score key-values instead of stopping at static
  serverinfo rules
