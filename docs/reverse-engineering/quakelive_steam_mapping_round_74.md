# Quake Live Steam Host Mapping Round 74

## Scope

This round closes the next bounded Steam game-server metadata seam that was
still mapped in the notes but missing in writable source after the earlier
identity/bootstrap work:

- the direct `SteamGameServer()->SetKeyValue` wrapper from round 05
- the spawn-time Steam game-server serverinfo publication path
- the dirty-`CVAR_SERVERINFO` Steam republish path in `SV_Frame`

The evidence base for this pass stayed inside the committed corpus:

- `references/hlil/quakelive/quakelive_steam.exe/`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `docs/reverse-engineering/quakelive_steam_mapping_round_05.md`
- `src/common/platform/platform_steamworks.c`
- `src/code/server/sv_init.c`
- `src/code/server/sv_main.c`

## `sub_465A60`: `SteamServer_SetKeyValuesFromInfoString`

Round 05 already bounded `00465A60` as a clean helper:

1. It checks the shared Steam game-server availability gate.
2. It walks the current server info string pair-by-pair.
3. It forwards each parsed `key` / `value` pair into
   `SteamGameServer()->vtable[0x50 / 4]`.

The writable source now reconstructs that helper directly as
`QL_Steamworks_ServerSetKeyValuesFromInfoString( infoString )` in
`src/common/platform/platform_steamworks.c`, pinned to the mapped
`SteamGameServer` slot and using the retained `Info_NextPair()` parser.

## Startup Publication Ownership

The HLIL for `sub_466800` already showed the retail connect-success sequence:

1. publish the server SteamID
2. enable the server heartbeat state
3. rebuild the serverinfo block
4. push that block through `sub_465A60`

The retained source base already had the closest writable owner in
`SV_SpawnServer()`, where the serverinfo configstring is created and the
earlier round-73 Steam identity/bootstrap helpers now run.

This round restores the missing metadata publication there:

- `serverInfo = Cvar_InfoString( CVAR_SERVERINFO )`
- `SV_SetConfigstring( CS_SERVERINFO, serverInfo )`
- `QL_Steamworks_ServerSetKeyValuesFromInfoString( serverInfo )`

That keeps the reconstruction tied to the existing server-owned startup path
instead of inventing a separate Steam-only metadata builder.

## Dirty Serverinfo Refresh Ownership

Round 05 also noted a second owner at the retail dirty-serverinfo path around
`004E4B36`, where the executable rebuilds the same info block, republishes it
to Steam, and then refreshes configstring `0`.

The retained source already had the matching owner in `SV_Frame()`:

- the `if ( cvar_modifiedFlags & CVAR_SERVERINFO )` branch

This round now mirrors the retail order there:

1. rebuild the current serverinfo string with `Cvar_InfoString( CVAR_SERVERINFO )`
2. republish it through
   `QL_Steamworks_ServerSetKeyValuesFromInfoString( serverInfo )`
3. refresh `CS_SERVERINFO`

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

- `65 passed`

## Outcome

This round did not add new address aliases. It consumed already-mapped
`quakelive_steam.exe` ownership in three ways:

- the shared Steamworks layer now includes a writable
  `ServerSetKeyValuesFromInfoString` wrapper at the mapped
  `SteamGameServer` `SetKeyValue` slot
- the retained server bootstrap now republishes serverinfo metadata into the
  retail Steam game-server surface during spawn
- the retained dirty-serverinfo path now mirrors the retail Steam republish
  order instead of only updating Quake-side configstrings
