# UI Quake Live Catalog Extension Layouts

This note maps the Quake Live-specific catalog records that widen the older
Team Arena `uiInfo_t` state in `uix86.dll`-compatible builds. It complements
`docs/reverse-engineering/ui-catalog-struct-layouts.md`, which already covers
the older `characterInfo`, `aliasInfo`, `teamInfo`, `gameTypeInfo`, `mapInfo`,
and `tierInfo` records.

The focus here is the newer clan, country, map-rotation, and ruleset state:

- `uiClanInfo_t`
- the flat `countryList[]` feeder bank
- `mapRotationInfo_t`
- `rulesetInfo_t`

## Method

- Layout facts come from a local x86 `clang` record-layout probe using
  `clang -DID_INLINE=__inline -m32 -target i686-pc-windows-msvc
  -Xclang -fdump-record-layouts -fsyntax-only` against `src/code/ui/ui_local.h`.
- Top-level offsets were cross-checked against
  `docs/reverse-engineering/ui-uiinfo.md`.
- Current member roles were cross-checked against the owning source in
  `src/code/ui/ui_main.c` and `src/code/ui/ui_gameinfo.c`.
- Retail parity is strongest around the callvote-map preview path because the
  already-mapped retail helpers `UI_CVMapCountByGameType`,
  `UI_FeederCount`, `UI_FeederItemText`, `UI_FeederItemImage`,
  `UI_FeederSelection`, `UI_DrawMapPreview`, `UI_DrawNetMapCinematic`, and
  `UI_GetCallvoteGametypeToken` all intersect this state.
- Retail parity is also now strong enough to separate file-backed map-pool
  ownership: committed `quakelive_steam.exe` HLIL shows the native host
  registering `sv_mapPoolFile` with default `mappool.txt` and immediately
  dispatching into a dedicated map-pool parser at `0x0045EDD0`.
- Retail parity is weaker for clan, country, and ruleset ownership. Those bands
  are currently source-backed unless otherwise noted below.

## Hard Layout Facts

- Target layout is 32-bit x86: pointers, `qhandle_t`, `qboolean`, and `int`
  slots are `4` bytes.
- `sizeof(uiClanInfo_t) = 0x0C4` (`196`), matching the
  `uiInfo.clanList[MAX_CLANS]` span between `0x0132F8` and `0x01F6F8` in
  `uiInfo_t`.
- `sizeof(mapRotationInfo_t) = 0x1404` (`5124`), matching the
  `uiInfo.mapRotations[MAX_MAP_ROTATIONS]` stride recorded in
  `ui-uiinfo.md`.
- `sizeof(rulesetInfo_t) = 0x0800` (`2048`), matching the
  `uiInfo.rulesets[MAX_RULESETS]` stride recorded in `ui-uiinfo.md`.
- There is no dedicated country struct in the current tree. Country state is a
  flat feeder bank:
  - `uiInfo.countryCount` at `0x01F700`
  - `uiInfo.countryList[256]` at `0x01F704`

## `uiClanInfo_t`

Current x86 size: `0x0C4`

This is one cached clan-row record used by the Quake Live clan feeder and the
lazy emblem-image path.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x00` | `id` | `char[MAX_QPATH]` | Persistent clan identifier. The current stub loader seeds `"pending"` here. |
| `0x40` | `name` | `char[MAX_NAME_LENGTH]` | User-facing clan name. `FEEDER_CLANS` returns it as the default text column, and selection writes it back to `ui_clanName`. |
| `0x60` | `tag` | `char[MAX_NAME_LENGTH]` | Short clan tag shown in feeder column `1`. The current stub loader seeds `"--"`. |
| `0x80` | `emblemPath` | `char[MAX_QPATH]` | Optional emblem shader path. `UI_FeederItemImage` lazily registers this path when it is non-empty. |
| `0x0C0` | `emblemShader` | `qhandle_t` | Cached emblem image handle. The reset path seeds `-1`; the image feeder preserves that sentinel when no emblem exists. |

Current reconstructed owner flow:

- `UI_ResetClanList` zeroes every row, resets the top-level clan counters, and
  clears the `ui_clanIndex` / `ui_clanName` CVars.
- `UI_LoadClanRoster` currently repopulates a one-entry placeholder roster with
  `"pending"`, `"No clans available"`, and `"--"`, then marks the list loaded.
- `UI_FeederCount`, `UI_FeederItemText`, `UI_FeederItemImage`, and
  `UI_FeederSelection` are the active consumers.

Negative evidence:

- The committed `src/ui/` menu tree contains the `FEEDER_CLANS` definition in
  `menudef.h`, but no live menu item was found using that feeder.
- The retail asset tree matches that shape exactly: `assets/quakelive/baseq3/ui/`
  still defines `FEEDER_CLANS` in `menudef.h`, but no retail `.menu` file was
  found consuming it.
- The misleadingly named `UI_CLANNAME` / `UI_CLANLOGO` ownerdraw ids do not
  anchor the clan roster cache. They already exist in the Team Arena baseline
  `assets/quake3/src/ui/menudef.h`, and both the baseline and current
  `UI_DrawClanName` / `UI_DrawClanLogo` implementations route them through
  `ui_teamName -> UI_TeamIndexFromName -> teamList[]`, not through
  `clanList[]`. Retail `ui_kc.shader` also keeps clan-branded shader names such
  as `clanlogo` and `ui/assets/clan_shader1`, which align with that older
  team-branding vocabulary rather than with a live clan-roster path. The local
  retail asset tree does not contain matching `ui/assets/pagans*.tga`,
  `stroggs*.tga`, `crusaders*.tga`, `intruders*.tga`, `thefallen*.tga`, or
  `chooseclan.tga` files, which makes those shader names read as dormant
  presentation residue rather than active clan-roster art.
- No committed `uix86.dll` HLIL string was found for `ui_clanName`,
  `ui_clanIndex`, or `"No clans available"`.
- No committed `quakelive_steam.exe` HLIL string was found for `ui_clanName` or
  `ui_clanIndex`.
- The committed host `qz_instance` method table at `data_55C008`
  (`0x0055C008-0x0055C17C`) is now bounded strongly enough to use as direct
  negative evidence. It exposes methods such as `IsPakFilePresent`,
  `IsGameRunning`, `SendGameCommand`, `WriteTextFile`, `GetCvar`, `SetCvar`,
  `ResetCvar`, `GetMapList`, `GetFactoryList`, `GetDemoList`, `OpenURL`,
  `GetFriendList`, `GetConfig`, `GetAllUGC`, and `GetNextKeyDown`, but no
  clan-roster getter, setter, invite, or roster-enumeration contract was found
  anywhere in that bounded native/browser bridge.
- The outbound browser event contract is also bounded strongly enough to use as
  direct negative evidence. The committed `QLWebView_PublishEvent` and higher
  level host publishers expose `game.error`, `game.end`, `cvar.%s`,
  `bind.changed`, `game.start`, `game.demo`, `game.screenshot`,
  `web.object.ready`, `web.tooltip`, `web.ugc.results`, `web.ugc.failed`, and
  the `lobby.*` family, but no clan-prefixed event family or roster-publish
  path was found in the local host/browser surface.
- The local retail asset set also lacks the browser payload that the host
  bootstrap expects. Committed HLIL for `QLWebHost_OpenURL` shows the host
  registering `web.pak` through `Awesomium::DataPakSource`, but no `web.pak`
  file exists under `assets/quakelive/`, and the included local
  `assets/quakelive/awesomium.log` records `Unable to load DataPak with path:
  web.pak`. That means the external browser/UI layer is not just unmapped here;
  it is also unrepresented in the local shipped asset corpus.
- The only committed host string mentioning clans directly,
  `"Locked to a clan you are not in"`, sits in the Steam lobby error block next
  to `"Lobby does not exist"`, `"Access denied"`, and other join failures under
  `SteamLobbyCallbacks`, which bounds it as lobby restriction text rather than a
  native clan-roster UI path.
- The unrelated gametype alias `"clanarena"` also appears in host gametype
  tables, but it does not anchor a clan-service surface.

Retail note:

- This band is intentionally weaker than the older menu/catalog records. The
  current source keeps a stub roster until a documented open replacement for
  the original online service path exists, and the committed retail evidence
  now points more strongly to this feeder being compatibility scaffolding:
  there is no committed retail menu consumer, no native `uix86.dll` cvar/string
  anchor, and no host-side JS/export contract for a clan roster in the current
  corpus; the similarly named `UI_CLANNAME` / `UI_CLANLOGO` ownerdraws are now
  better bounded as older `teamList[]`-backed team-branding carry-overs rather
  than as evidence of clan-cache ownership. Within the committed native/browser
  evidence set, the clan band now reads as effectively closed: the only
  remaining uncertainty is whether retail delegated clan roster ownership
  entirely into an external web service layer that is not represented in the
  local corpus.

## Country Feeder Bank

Current x86 layout:

- `uiInfo.countryCount` is an `int`.
- `uiInfo.countryList` is `const char *[256]`.

This bank is a simple token table rather than a nested struct. Each entry is an
interned country-code string.

Observed owner flow:

- `UI_LoadCountries` loads `country.txt` through `GetMenuBuffer`, tokenizes it
  with `COM_ParseExt`, interns each code through `String_Alloc`, and appends the
  resulting pointers into `uiInfo.countryList[]`.
- `UI_ValidateCountryCode` resolves an input code against that table and falls
  back to the first loaded code or the raw input when no match exists.
- `FEEDER_COUNTRIES` exposes the table directly; the current source menu tree
  uses it in `src/ui/ingame_join.menu` for the `country_list` item.
- `UI_FeederSelection` writes the selected code back into the `ui_country`
  CVar.

Retail host/UI split:

- No committed `uix86.dll` HLIL string was found for `country.txt` or
  `ui_country`.
- Committed `quakelive_steam.exe` HLIL instead shows the generic client
  userinfo cvar `"country"` being registered at `0x004BC924` in the same
  initialization block as `"name"`, `"model"`, `"rate"`, and `"color1"`.
- The same host block seeds `"country"` through `sub_4cd250("country",
  SteamUtils_GetIPCountry())` at `0x004BCDE9` when the cvar is blank. That
  helper is already promoted in the committed host alias set
  (`sub_460690` / `0x00460690`) and is documented in
  `quakelive_steam_mapping_round_04.md` as the Steam-backed IP-country wrapper
  used during client bootstrap.
- That makes the retail ownership split concrete: the host owns country
  bootstrap through `SteamUtils_GetIPCountry`, while the reconstructed UI owns
  the `country.txt` token table and dropdown presentation layered over the
  generic `country` userinfo field.
- The retail/source asset audit narrows that further: `ui-strings-assets-audit.md`
  records that the current `src/ui/ingame_join.menu` country dropdown block is
  not present in the retail file, and that the local `FEEDER_COUNTRIES` define
  in `src/ui/menudef.h` is absent from the retail header.

Retail note:

- No direct retail helper in the committed `uix86.dll` map has been promoted
  specifically for the country bank yet. The current country dropdown is best
  understood as a source-only menu/data-table layer built on top of a generic
  host-owned `country` userinfo field.

## `mapRotationInfo_t`

Current x86 size: `0x1404`

This is the Quake Live map-rotation row used by the callvote map-pool preview,
the rotation feeder, and the preset-selection sidecar.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x0000` | `mapName` | `char[MAX_MAP_ROTATION_TOKEN]` | Raw map token from the rotation source. It is the canonical lookup key passed through `UI_MapIndexForRotationToken`. |
| `0x0400` | `mapTitle` | `char[MAX_MAP_ROTATION_TOKEN]` | Friendly display name. `UI_PopulateRotationMetadata` overwrites this with the resolved `mapInfo.mapName` when the map index is known; feeder text falls back to `mapName` when it is empty. |
| `0x0800` | `factoryId` | `char[MAX_MAP_ROTATION_TOKEN]` | Source-side factory token copied from the parsed rotation row. The current reconstructed `voteMap` script path passes this as the second argument in `callvote map %s %s\n` when a rotation entry is active, but committed retail `uix86.dll` evidence instead ties that second token to `ui_cvGameType` through `UI_GetCallvoteGametypeToken`. |
| `0x0C00` | `factoryConfig` | `char[MAX_MAP_ROTATION_TOKEN]` | Optional third-field token copied from the parsed rotation line and exposed by `FEEDER_MAP_ROTATIONS` column `3`. |
| `0x1000` | `factoryGameType` | `char[MAX_MAP_ROTATION_TOKEN]` | Optional explicit gametype token. `UI_GetCallvoteRotationGametype` prefers this field before falling back to `factoryId`. |
| `0x1400` | `mapIndex` | `int` | Resolved backing index into `uiInfo.mapList[]`. This ties the rotation row to levelshots, cinematics, and map-title metadata. |

Observed owner flow:

- `UI_ClearMapRotations` zeroes the full cache and resets
  `uiInfo.mapRotationCount`.
- `UI_AddMapRotationFromLine` parses one `map|factory|config|gametype` row,
  validates it, resolves `mapIndex`, and appends it.
- `UI_LoadMapRotations` populates the cache from inline CVars first
  (`ui_mapRotation`, `sv_mapRotation`, `g_mapRotation`), then from file CVars
  (`ui_mapPoolFile`, `sv_mapPoolFile`), then from `mappool.txt`.
- `FEEDER_CVMAPS` exposes the filtered callvote-visible subset through
  `UI_CountVisibleCallvoteRotations` and
  `UI_GetCallvoteRotationEntryForDisplay`.
- `FEEDER_MAP_ROTATIONS` exposes the full backing cache, including the raw
  factory/config/gametype columns.
- `UI_SelectCallvoteRotation` writes the resolved selection into
  `uiInfo.callvoteRotationIndex` and refreshes `ui_currentNetMap` through the
  shared net-map preview path.

Retail anchors:

- The already-mapped retail `UI_CVMapCountByGameType` helper proves that the
  native UI owns a distinct callvote-map filter layered on top of the same
  `mapList[].active` visibility slab.
- The already-mapped retail `UI_SelectedMap` helper resolves a visible row back
  into the active backing `mapList[]` index. The committed retail
  `UI_FeederSelection` body uses that exact helper after rebuilding the
  callvote-visible map set, which tightens the FEEDER_CVMAPS selection chain to
  `UI_CVMapCountByGameType -> UI_SelectedMap -> UI_FeederSelection ->
  ui_currentNetMap`.
- The already-mapped retail `UI_FeederSelection` body updates
  `ui_currentNetMap` on the net-map branch, which is the same preview latch
  reused by the current `FEEDER_CVMAPS` rotation selection path.
- The already-mapped retail command branch at `0x1000C34A` formats
  `callvote map %s %s\n`, and the committed HLIL shows that second token coming
  from `UI_GetCallvoteGametypeToken(data_10741c6c)`, where `data_10741c6c` is
  the registered `ui_cvGameType` cvar state. When that state is `-1`, retail
  falls back to the empty string at `data_100239ab` rather than to a
  rotation-row `factoryId`, which makes the current Quake Live-compatible
  `factoryId` route best understood as compatibility scaffolding rather than a
  proven retail match.
- The already-mapped `UI_DrawMapPreview` and `UI_DrawNetMapCinematic` helpers
  consume the preview state that this rotation cache ultimately drives.

Retail host/UI split:

- No committed `uix86.dll` HLIL string was found for `ui_mapRotation`,
  `sv_mapRotation`, `g_mapRotation`, `ui_mapPoolFile`, `sv_mapPoolFile`, or
  `mappool.txt`.
- Committed `quakelive_steam.exe` HLIL instead shows `sub_4e3ad0` registering
  `sv_mapPoolFile` with default `mappool.txt` at `0x004E3B10`, then calling
  `sub_45edd0(*(data_13e181c + 4))` at `0x004E3B28`.
- `sub_45edd0` is a native map-pool file loader, not a thin cvar wrapper. The
  committed HLIL shows it:
  - loading the requested file path
  - enforcing the same `0x8000` size cap and `"^1rotations file too large"`
    warning string used by the current reconstructed source
  - tokenizing line-by-line and splitting rows on `'|'`
  - validating the factory token, map existence, and map-versus-factory
    gametype compatibility with the same `"invalid factory"` /
    `"map doesn't exist"` / `"map isn't valid for factory gametype"` warning
    strings used by `UI_LoadMapRotationsFromFile`
  - copying accepted rows into a host-owned `0x1000`-byte-per-entry cache at
    `0x6111F8` and logging `"loaded %i maps into the map pool\n"`
- The retail host cache width is therefore `0x1000`, matching the four copied
  `0x400` token slabs in `sub_45edd0` and stopping short of the reconstructed
  `mapRotationInfo_t` `mapIndex` tail at `0x1400`.
- That means the current UI-side file/CVar loader is best understood as a
  compatibility reconstruction of retail host-side map-pool loading, while the
  retail UI DLL still owns the preview, filtering, feeder, and submission
  behavior layered on top of that pool.

Observed versus inferred:

- Observed: the retail UI has a real callvote-map filter, a real
  `ui_currentNetMap` preview latch, and a real `callvote map %s %s\n`
  submission path whose second token comes from the `ui_cvGameType` ->
  `UI_GetCallvoteGametypeToken` path with an empty-string fallback.
- Inferred: the exact Quake Live-compatible source helpers
  `UI_SetCallvotePresetState`, `UI_SelectCallvoteRotation`, and
  `UI_GetCallvoteRotationEntryForDisplay` are the current best source-side
  decomposition of the broader preview/filter flow, but those helper boundaries
  should now be read as source decomposition around an already-bounded retail
  inline dispatcher path rather than as missing native helpers waiting to be
  rediscovered.

### Callvote Preview And Preset Control Flow

The committed retail HLIL is strong enough to separate the retail-owned
callvote-preview path from the newer source-side preset scaffolding:

- `UI_RunMenuScript` in retail contains literal string branches for
  `"updateCallvoteMapPreview"` and `"voteMap"`.
- Retail native bootstrap also touches the same filter state before menu
  scripts run: `_UI_Init` seeds `ui_cvGameType` to `-1`, and
  `_UI_SetActiveMenu(UIMENU_INGAME)` resets `ui_cvGameType` to `-1` again
  immediately before the ingame-menu activation path.
- The retail `assets/quakelive/baseq3/ui/ingame_callvote.menu` file wires the
  same path together at the script level: it binds the gametype control to
  `ui_cvGameType`, uses `action { uiScript updateCallvoteMapPreview }`, drives
  the preview list through `feeder FEEDER_CVMAPS`, and submits through
  `action { uiScript voteMap ; uiScript closeingame }`.
- The `"updateCallvoteMapPreview"` branch dispatches directly into the already
  mapped `UI_FeederSelection` path with feeder id `19`, which is the same
  `FEEDER_CVMAPS` callvote-map preview route already anchored by
  `UI_CVMapCountByGameType`.
- The committed `UI_RunMenuScript` HLIL does not expose an additional retail
  helper between that script branch and `UI_FeederSelection`; the preview jump
  is already inline at the dispatcher level.
- Inside that retail selection branch, the committed HLIL rebuilds the
  callvote-visible set through `UI_CVMapCountByGameType`, resolves the selected
  visible row through `UI_SelectedMap`, writes the resulting backing index into
  `ui_mapIndex`, and then refreshes `ui_currentNetMap` for the preview.
- The `"voteMap"` branch reads the currently selected net-map state and formats
  the retail command string `callvote map %s %s\n`.
- That submit branch is likewise inline in the committed `UI_RunMenuScript`
  body rather than delegated to a separate retail helper.
- That second retail `%s` is no longer opaque in the committed corpus: the same
  branch reads `ui_cvGameType` from `data_10741c6c`, calls
  `UI_GetCallvoteGametypeToken` when the value is not `-1`, and otherwise
  falls back to the empty string at `data_100239ab`.
- The token table returned by `UI_GetCallvoteGametypeToken` matches the retail
  callvote gametype menu choices rather than the current source-side
  `mapRotationInfo_t.factoryId` field: `ffa`, `duel`, `race`, `tdm`, `ca`,
  `ctf`, `oneflag`, `har`, `ft`, `dom`, `ad`, and `rr`.
- Retail also exposes `ui_cvGameType` as a real CVar string in the active-menu
  setup path, which matches the current source's callvote-gametype filter role.

Negative evidence matters here too:

- No committed `uix86.dll` HLIL string was found for `applyCallvotePreset`.
- No committed `uix86.dll` HLIL string was found for `ui_cvPresetRotation`,
  `ui_cvPresetGameType`, or `ui_cvPresetActive`.
- No committed `uix86.dll` HLIL string was found for `ui_mapPoolFile`,
  `sv_mapPoolFile`, or `mappool.txt`; those file-backed pool anchors sit in the
  native host instead.

That makes the current preset-state helpers in `src/code/ui/ui_main.c`
best understood as source-backed reconstruction around a retail-owned preview
and submission core whose bootstrap starts natively at `_UI_Init` and
`_UI_SetActiveMenu`, with the FEEDER_CVMAPS selection leg already bounded down
to `UI_CVMapCountByGameType`, `UI_SelectedMap`, and `UI_FeederSelection`, and
with the submit token now bounded through `ui_cvGameType` and
`UI_GetCallvoteGametypeToken`. The committed retail corpus does not presently
show a higher-level native wrapper above those inline `UI_RunMenuScript`
branches, so the newer preset/rotation helpers remain source-side
reconstruction rather than missing named retail helpers.

## `rulesetInfo_t`

Current x86 size: `0x0800`

This is the compact ruleset-cache row embedded in `uiInfo.rulesets[]`.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x0000` | `name` | `char[MAX_TOKEN_CHARS]` | Ruleset token copied from `ui_rulesets` or from the fallback list. |
| `0x0400` | `description` | `char[MAX_STRING_CHARS]` | User-facing description string. The current loader mirrors the raw token here instead of parsing a richer descriptor format. |

Observed owner flow:

- `UI_ClearRulesets` zeroes the cache, clears `rulesetCount`, resets
  `rulesetIndex`, and clears `activeRuleset`.
- `UI_AddRulesetFromToken` appends one row and updates `rulesetIndex` when the
  token matches `activeRuleset`.
- `UI_LoadRulesets` seeds `activeRuleset` from `g_ruleset`, falls back to
  `"standard"` when empty, then loads `ui_rulesets` or the default trio
  `"standard"`, `"classic"`, and `"pql"`.

Current usage note:

- In the committed tree, this cache currently stops at load-time population.
  No direct feeder, image path, or ownerdraw consumer was found in the current
  `src/code/ui/` tree beyond the top-level bookkeeping fields.
- No `ruleset`, `ui_rulesets`, or `g_ruleset` consumer was found in the
  committed `src/ui/` menu tree.

Observed ownership split:

- The current UI cache is seeded from the game-owned `g_ruleset` token and the
  optional UI-side `ui_rulesets` list.
- The open-source game module already treats `g_ruleset` as authoritative:
  `g_main.c` registers it as a serverinfo/archive cvar, mirrors it into
  `level.rulesetName`, and uses it to seed `g_factory`; `g_cmds.c` also owns
  the `"ruleset %s"` vote command and `"Current ruleset: %s"` status print.
- No committed `uix86.dll` HLIL string was found for `ui_rulesets` or
  `g_ruleset`, and no committed `quakelive_steam.exe` HLIL string was found for
  those UI-facing ruleset names either.
- The already-documented host `GetFactoryList` JS surface in
  `quakelive_steam_mapping_round_10.md` returns factory descriptors containing
  `sysname`, `title`, `basegt`, optional author/description fields, and a
  lowercased `settings` map. That host-side factory catalog is a stronger home
  for ruleset/factory descriptor services than the UI DLL, even though the
  exact native loader behind that JS surface is still unnamed.

Retail note:

- The cache is clearly a Quake Live-era addition, but the committed `uix86.dll`
  map does not expose a retail menu-side owner for it, while the qagame and
  host evidence already place the authoritative ruleset/factory state outside
  `uix86.dll`. The best current reading is therefore stable rather than merely
  tentative: `rulesetInfo_t` is a reconstructed UI compatibility cache layered
  over game/host-owned ruleset-factory state, not a directly anchored retail
  menu-data record.

## Coverage Outcome

With this note in place, every major `uiInfo_t` nested-record family now has a
dedicated layout note:

1. Browser/support records
2. Legacy catalog records
3. Display-context records
4. Quake Live catalog-extension records
5. Match-summary records

That closes the remaining large documentation gap inside the UI data model even
though a small number of Quake Live-only online-service ownership seams still
rest on negative retail evidence rather than direct native anchors.

## Open Questions

1. Determine whether retail ever populated `uiClanInfo_t` from an online path
   outside the committed native/browser corpus. Within the local retail
   evidence set, the question is already effectively closed by negative
   evidence across all three surfaces: no menu consumer in the asset tree, no
   `uix86.dll` cvar/string anchor, no clan method in the bounded host
   `qz_instance` contract, and no clan event family in the bounded
   `EnginePublish` browser vocabulary. The misleading `UI_CLANNAME` /
   `UI_CLANLOGO` labels are already bounded to the older `teamList[]` band, and
   the host's expected `web.pak` browser payload is not present in the local
   retail asset set.
