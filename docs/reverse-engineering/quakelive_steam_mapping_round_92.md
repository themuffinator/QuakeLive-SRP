# Quake Live Steam Host Mapping Round 92

## Scope

This round closes the next adjacent browser-host seam that remained only
partially reconstructed after [Round 91](./quakelive_steam_mapping_round_91.md):

1. the missing `web_zoom` / `web_console` cvar registration owned by
   `QLWebHost_RegisterCommands`
2. the retained session-cache ownership behind `web_clearCache` and `web_reload`

The evidence base stayed the same:

- `references/hlil/quakelive/quakelive_steam.exe/`
- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- earlier browser-host notes in
  [Round 02](./quakelive_steam_mapping_round_02.md) and
  [Round 03](./quakelive_steam_mapping_round_03.md)

## Retail evidence recap

The command registration block at `sub_4F3CD0` was already named in Round 02 as
`QLWebHost_RegisterCommands`. The HLIL now matters for the exact retained cvar
shape:

- `004f3d47  data_12d3060 = sub_4ce0d0(..., "web_zoom", "100", 1)`
- `004f3d60  data_12d3064 = sub_4ce0d0(..., "web_console", "0", 1)`
- `004f3d6d  return sub_4ce0d0(..., "web_browserActive", "0", 0x40)`

Round 03 already closed the ownership around the command handlers:

- `sub_4f2a10` -> `QLWebHost_ClearCache_f`
- `sub_4f2a30` -> `QLWebHost_Reload_f`

The HLIL for those handlers remains compact and stable:

- `QLWebHost_ClearCache_f` does nothing without the backing session object and
  otherwise jumps through the session slot at `+0x1c`
- `QLWebHost_Reload_f` clears that same session state and then reloads the
  active `WebView` with the boolean argument `1`

That proves two things that the retained source still lacked after Round 91:

1. the browser command-registration surface was still incomplete without
   `web_zoom` and `web_console`
2. `web_clearCache` and `web_reload` are not meant to be inert logging hooks;
   they own real browser-session invalidation work

## Source reconstruction

I reconstructed the writable portion of that seam in the existing client host
layers:

- [cl_main.c](../../src/code/client/cl_main.c) now restores the retail cvar
  registration defaults:
  - `web_zoom = "100"` with `CVAR_ARCHIVE`
  - `web_console = "0"` with `CVAR_ARCHIVE`
- [cl_cgame.c](../../src/code/client/cl_cgame.c) now introduces a retained
  `CL_Web_ClearSessionState()` owner so both `web_clearCache` and `web_reload`
  invalidate the current URI-backed browser cache path instead of stopping at
  debug prints
- [cl_steam_resources.c](../../src/code/client/cl_steam_resources.c) now
  exposes `CL_ClearSteamResourceCache( qboolean clearPersisted )`, which walks
  the retained cached URI slots, removes session-owned files, and clears the
  in-memory slot table

This is deliberately scoped to the retained source ownership that exists today.
It does **not** invent a full Awesomium session object or listener graph. The
reconstruction stays inside the writable launcher/URI cache layer that already
stands in for retail browser-backed resource loading.

## Practical result

After this round:

- the browser command-registration surface in the writable host matches the
  documented retail cvar defaults instead of omitting two registered cvars
- `web_clearCache` now clears the retained URI cache owner rather than behaving
  as a visible-but-inert stub
- `web_reload` now follows the same retained invalidation path before restoring
  the active overlay latch when the current online-services provider exists

The remaining browser-host gaps are the real listener/runtime owners behind the
Awesomium view, not this command-registration seam.

## Verification

I added parity assertions in
[tests/test_platform_services.py](../../tests/test_platform_services.py) for:

- retail `web_zoom` / `web_console` registration defaults
- the shared retained `CL_Web_ClearSessionState()` owner
- slot-wise URI cache invalidation in `CL_ClearSteamResourceCache()`

Validation command:

- `python -m pytest tests/test_steamworks_harness.py tests/test_platform_services.py tests/test_ui_menu_files.py -q`

Result:

- `86 passed`

## Completion stats after Round 92

- Ghidra baseline: `5473` functions, `351` imports, `2` exports, `4377`
  analysis symbols
- Current mapping coverage: `944` raw alias entries, `943` address-backed
  aliases
- Address-backed coverage: `17.230%` of `5473` functions
- Alias delta this round: `0`; this pass consumed already-mapped ownership as
  source reconstruction
- Estimated parity for this round: `92% -> 93%`
