# Botlib Libvar Runtime Mapping - 2026-06-05

## Scope

This pass selects `src/code/botlib/l_libvar.c` as the next non-conflicting
botlib slice. It covers botlib's private library-variable runtime plus the
related bridge wiring that exposes `BotLibVarSet` and `BotLibVarGet` to qagame.

This deliberately avoids:

- `019e97e9-ddaa-7e53-81bb-6511a54422c2`, which is actively working the
  `l_precomp.c` public source-handle/token wrapper lane.
- `019e97ee-3333-7331-b55e-3c659db32255`, which moved into the elementary
  actions (`be_ea.c`) slice.
- Shared, busy files such as `tests/test_botlib_internal_parity.py` and
  `references/analysis/quakelive_symbol_aliases.json`.

The result is proof-oriented source reconstruction: no C body change was needed,
and the alias ledger was left untouched because the internal libvar helpers are
not currently promoted there.

## Owning Retail Binary

Owning binary:

- `assets/quakelive/quakelive_steam.exe`

Primary references:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part03.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/analysis/quakelive_symbol_aliases.json`
- `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt`
- `references/reverse-engineering/ghidra/qagamex86/decompile_top_functions.c`
- `src/code/botlib/l_libvar.c`
- `src/code/botlib/l_libvar.h`
- `src/code/botlib/be_interface.c`
- `src/code/botlib/be_aas_main.c`
- `src/code/botlib/be_aas_move.c`
- `src/code/game/ai_main.c`
- `src/code/game/botlib.h`
- `src/code/game/g_public.h`
- `src/code/game/g_syscalls.c`
- `src/code/server/sv_game.c`
- `src/code/server/ql_game_imports.inc`

## Retail Function Map

Observed retail rows from `functions.csv`:

| Address | Size | Source owner | Notes |
| --- | ---: | --- | --- |
| `0x004A8500` | 137 | `LibVarStringValue` | Decimal-only string-to-float parser. |
| `0x004A8590` | 94 | `LibVarAlloc` | Allocates `sizeof(libvar_t) + strlen(name) + 1`; `sizeof(libvar_t)` is `0x18`. |
| `0x004A85F0` | 68 | `LibVarDeAllocAll` | Retail inlines the per-node free behavior. |
| `0x004A8640` | 57 | `LibVarGetString` | Returns the variable string or the static empty string. |
| `0x004A8680` | 54 | `LibVarGetValue` | Returns the cached float value or `0`. |
| `0x004A86C0` | 134 | `LibVar` | Find-or-create, string allocation, value cache, modified flag. |
| `0x004A8750` | 24 | `LibVarString` | Thin wrapper returning `LibVar(...)->string`. |
| `0x004A8770` | 24 | `LibVarValue` | Thin wrapper returning `LibVar(...)->value`. |
| `0x004A8790` | 145 | `LibVarSet` | Find-or-create, frees previous string, updates value and modified flag. |
| `0x004A7E40` | 23 | `Export_BotLibVarSet` | Export wrapper calling `LibVarSet`, returns `BLERR_NOERROR`. |
| `0x004A7E60` | 46 | `Export_BotLibVarGet` | Export wrapper copies `LibVarGetString` into caller buffer and terminates. |

Source-visible helpers without stable promoted retail starts in this pass:

- `LibVarDeAlloc`
- `LibVarGet`
- `LibVarChanged`
- `LibVarSetNotModified`

The source bodies are still guarded for reconstruction value, but this pass does
not promote aliases for them because the committed retail function rows do not
show separate stable starts for those helpers in the host executable.

## Consumer Wiring Map

Second-round source/retail cross-checks pin the libvar consumers that make this
runtime meaningful at startup and during AAS updates:

| Address or span | Source owner | Libvar role | Evidence |
| --- | --- | --- | --- |
| `0x004A7CE0` | `Export_BotLibSetup` | Reads `bot_developer`, `bot_showPath`, `maxclients`, and `maxentities`, then calls `AAS_Setup`. | Binary Ninja HLIL at `004a7cf4`, `004a7d03`, `004a7d53`, `004a7d65`, `004a7d6a`. |
| `0x004A7DC0` | `Export_BotLibShutdown` | Runs the shutdown chain and frees every libvar through `LibVarDeAllocAll`. | Binary Ninja HLIL at `004a7e02`, `004a7e07`, `004a7e0c`. |
| `0x00486210` | `AAS_ContinueInit` | Reads `forcewrite` and `aasoptimize` to decide whether to optimize/write AAS data. | `functions.csv` row `FUN_00486210,00486210,200`; HLIL at `0048625f`, `00486281`. |
| `0x004862E0` | `AAS_StartFrame` | Reads one-shot debug toggles and resets them through `LibVarSet`; reloads `bot_showPath`; consumes and clears `saveroutingcache`. | `functions.csv` row `FUN_004862e0,004862e0,276`; HLIL at `00486321`, `00486343`, `00486350`, `00486372`, `0048637f`, `004863a1`, `004863bb`, `004863e2`. |
| `0x004865B0` | `AAS_Setup` | Reads `maxclients`/`maxentities` and creates the `saveroutingcache` libvar node. | `functions.csv` row `FUN_004865b0,004865b0,134`; HLIL at `004865ce`, `004865e7`, `004865f1`. |
| `0x00486740` | `AAS_InitSettings` | Loads the retail movement/reachability default table with `LibVarValue`. | `functions.csv` row `FUN_00486740,00486740,798`; HLIL at `00486769..00486a4f`. |
| `0x10023C61..0x10024180` | `qagamex86::BotInitLibrary` | Pushes cvars and defaults into botlib through native import slot `DAT_104b13ac + 0xcc`. | qagame HLIL and Ghidra both show the `BotLibVarSet` chain from `maxclients` through `cddir`. |

`0x004A7CC0` was explicitly left out of the setup map after review: its HLIL is
the small clock/millisecond helper immediately preceding `Export_BotLibSetup`.

## Observed Facts

- `libvar_t` is a six-field `0x18`-byte node: `name`, `string`, `flags`,
  `modified`, `value`, and `next`.
- `LibVarStringValue` accepts only digits and one decimal point. Any second
  decimal point or non-digit byte returns `0`. Negative values and signs are not
  parsed here.
- The decimal parser preserves the GPL/source quirk where seeing `.` advances
  to the next byte and immediately processes that byte as the first fractional
  digit.
- `LibVarAlloc` zeroes only `sizeof(libvar_t)`, stores the name at node offset
  `+0x18`, and pushes the new node at the head of `libvarlist`.
- `LibVarDeAllocAll` walks `libvarlist`, frees each non-null value string, frees
  the node, and then clears the global list pointer.
- `LibVarGetString` and `LibVarGetValue` perform case-insensitive name lookup.
  Missing strings return the retail empty-string object; missing values return
  float `0`.
- `LibVar` returns an existing variable unchanged. For new variables it allocates
  the value string, caches `LibVarStringValue`, and marks the node modified.
- `LibVarSet` replaces an existing value string when present or allocates a new
  node when absent, then updates the cached value and modified flag.
- `Export_BotLibVarSet` and `Export_BotLibVarGet` are stable aliases in
  `quakelive_symbol_aliases.json` (`sub_4A7E40` and `sub_4A7E60`).
- Retail qagame uses the native import-table slot `DAT_104b13ac + 0xcc` for
  `BotLibVarSet` in `BotInitLibrary`, startup/debug toggles, and chat test
  flows. The committed qagame HLIL/Ghidra corpora do not show direct calls
  through `DAT_104b13ac + 0xd0`; `BotLibVarGet` remains exported/wired for VM
  compatibility and generated native imports.
- `BotInitLibrary` seeds `maxclients`, `maxentities`, map checksum, AAS limits,
  gametype, bot developer/debug toggles, routing-cache controls, character reload
  behavior, and filesystem path libvars before calling `BotLibSetup`.
- The retail `bot_nochat` bridge preserves the source quirk: if the cvar string
  is non-empty, qagame sets botlib `nochat` to the constant `"0"`.
- `AAS_ContinueInit` and `AAS_StartFrame` prove that libvars are live runtime
  controls, not just startup defaults. `showcacheupdates`, `showmemoryusage`,
  `memorydump`, and `saveroutingcache` are one-shot toggles that self-clear with
  `LibVarSet(..., "0")`.
- `AAS_InitSettings` keeps the Quake Live retail movement/reachability defaults
  from the GPL base: `phys_friction=6`, `phys_gravity=800`, `phys_jumpvel=270`,
  `rs_rocketjump=500`, `rs_bfgjump=500`, and `rs_maxjumpfallheight=450`, among
  the full guarded table.

## Source Confirmation

The checked-in source matches the recovered retail shape:

- `l_libvar.c::LibVarStringValue` matches the HLIL decimal parser and its
  strict non-negative grammar.
- `LibVarAlloc`, `LibVarDeAllocAll`, `LibVarGetString`, `LibVarGetValue`,
  `LibVar`, `LibVarString`, `LibVarValue`, and `LibVarSet` match the retail
  allocation sizes, offsets, return behavior, and modified-flag writes.
- `LibVarDeAlloc`, `LibVarGet`, `LibVarChanged`, and
  `LibVarSetNotModified` are still present in source and are guarded as source
  contracts, even though this pass does not assign standalone retail starts.
- `be_interface.c::GetBotLibAPI` assigns `BotLibVarSet` and `BotLibVarGet`
  immediately after setup/shutdown exports, matching the stable wrapper slab at
  `0x004A7E40..0x004A7E60`.
- `g_syscalls.c::G_MapNativeImport` maps `BOTLIB_LIBVAR_SET/GET` to
  `G_QL_IMPORT_BOTLIB_LIBVAR_SET/GET`.
- `sv_game.c` preserves both the legacy syscall switch and the compatibility
  plus generated native import tables for `QL_G_trap_BotLibVarSet/Get`.
- `game/ai_main.c::BotInitLibrary` matches the retail qagame native-import set
  chain and its default fallbacks for empty `sv_maxclients`, `g_gametype`, and
  `bot_reloadcharacters`.
- `be_aas_main.c` matches the retail host reads and one-shot reset pattern for
  `forcewrite`, `aasoptimize`, debug memory/cache toggles, `bot_showPath`, and
  `saveroutingcache`.
- `be_aas_move.c::AAS_InitSettings` matches the retail HLIL `LibVarValue`
  default table for the physics and reachability settings sampled above.

## Changes

- Added and then extended `tests/test_botlib_libvar_parity.py`.
- Added this mapping note.
- No C source body change was needed.
- No alias promotion was attempted, to avoid conflicting with the active
  sessions' symbol/test lanes.

## Follow-On Work

- Promote internal libvar aliases only after the current alias-file work settles,
  if the project wants names such as `LibVarStringValue` and `LibVarSet` in
  `quakelive_symbol_aliases.json`.
- Add a tiny native C unit probe for `LibVarStringValue` edge cases if future
  source changes touch parser behavior, especially malformed numeric strings.
- Recheck whether `LibVarChanged` and `LibVarSetNotModified` are dead-stripped
  in retail or folded into other helpers before assigning names.

## Validation

Targeted validation for this pass:

- `python -m pytest tests/test_botlib_libvar_parity.py -q` - `3 passed`
- `python -m pytest tests/test_botlib_libvar_parity.py tests/test_botlib_chat_parity.py tests/test_botlib_weight_runtime_parity.py -q` - `12 passed`

No game launch was performed. The committed retail HLIL/Ghidra references and
source-level static tests fully answer this slice.

## Parity Estimate

- Focused `l_libvar.c` runtime, export bridge, and consumer propagation:
  `94% -> 97%` this round, cumulative `76% -> 97%`. The remaining gap is mostly
  unpromoted internal aliases and absence of a tiny compiled parser probe.
- Overall botlib plus related wiring: approximately `77% -> 78%`.
- Strict-retail Windows replacement target: unchanged at `100%`.
