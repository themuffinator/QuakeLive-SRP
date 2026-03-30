# Quake Live Steam Host Mapping Round 75

## Scope

This round closes the next bounded Steam game-server bootstrap seam that was
still mapped in the HLIL but missing in writable source after the earlier
identity and metadata publication passes:

- the default `sv_hostname` bootstrap helper from round 01
- the Steam account logon choice inside the one-time game-server bootstrap
- the adjacent dedicated/product/game-dir Steam game-server metadata writes

The evidence base for this pass stayed inside the committed corpus:

- `references/hlil/quakelive/quakelive_steam.exe/`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `docs/reverse-engineering/quakelive_steam_mapping_round_01.md`
- `docs/reverse-engineering/quakelive_steam_parity_plan.md`
- `src/common/platform/platform_steamworks.c`
- `src/code/server/sv_init.c`

## `sub_465E30`: `SteamServer_InitDefaultHostname`

Round 01 already bounded `00465E30` as a clean helper:

1. It exits early when the build-harness cvar is present.
2. It queries the Steam persona name through `SteamFriends()`.
3. It falls back to `"anon"` when Steam persona data is unavailable.
4. It registers `sv_hostname` with the default format `"%s's Match"`.

The writable source now reconstructs that behavior in `sv_init.c` as
`SV_SteamServerInitDefaultHostname()`. The retained source uses
`com_buildScript` as the closest build-harness gate available in-tree, which
matches the same intent without inventing a new host-global.

## `sub_466ED0`: Server Bootstrap Metadata Surface

The larger `SteamServer_Init` block in the HLIL does more than the unresolved
`SteamGameServer_Init(...)` call. After a successful init it also performs a
stable one-time metadata bootstrap on the `SteamGameServer` interface:

1. it writes the dedicated/non-dedicated state through slot `0x10 / 4`
2. it reads `sv_setSteamAccount`
3. it chooses `LogOnAnonymous` at slot `0x18 / 4` for the empty-string path
4. it chooses `LogOn( account )` at slot `0x14 / 4` otherwise
5. it writes `"Quake Live"` through slot `0x04 / 4`
6. it writes `"baseq3"` through slot `0x0c / 4`

The writable source now reconstructs those interface shims directly in
`src/common/platform/platform_steamworks.c` as:

- `QL_Steamworks_ServerSetDedicated`
- `QL_Steamworks_ServerLogOn`
- `QL_Steamworks_ServerSetProduct`
- `QL_Steamworks_ServerSetGameDir`

## Writable Owner In `SV_Init`

The retained source base still does not have a distinct server-only
`SteamGameServer_Init(...)` owner separate from the broader executable
bootstrap, so this round reconstructs the stable adjacent bootstrap work in
the closest writable one-time server owner:

- `SV_Init()`

`SV_Init()` now:

- seeds `sv_hostname` through `SV_SteamServerInitDefaultHostname()`
- registers `sv_setSteamAccount`
- applies the observed dedicated/account/product/game-dir bootstrap writes
  through `SV_SteamServerConfigureBootstrap()`

This keeps the reconstruction bounded to the host bootstrap surface that the
retail HLIL makes explicit, while leaving the larger unresolved
`SteamGameServer_Init(...)` ownership seam for a later pass.

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

- `66 passed`

## Outcome

This round did not add new address aliases. It consumed already-mapped
`quakelive_steam.exe` ownership in three ways:

- the shared Steamworks layer now includes writable wrappers for the retail
  dedicated/logon/product/game-dir game-server bootstrap slots
- the retained server init path now seeds the retail Steam-based default
  hostname instead of always defaulting to `"noname"`
- the retained server init path now owns the mapped `sv_setSteamAccount`
  bootstrap and adjacent Steam game-server metadata writes
