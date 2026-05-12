# Quake Live Steam Mapping Round 180

## Scope

This round is source-only and closes the remaining high-confidence
`qz_instance` browser-method seam for `OpenSteamOverlayURL` and
`SetClipboardText` in `src/` without changing the host alias corpus.

The target gap was the small retained method slice left intentionally deferred
in round 179:

- round 177 reconstructed the `game.start` and local-address publication lane
- round 178 restored the richer Steam lobby enter/leave callback payloads
- round 179 rebuilt the stable lobby/social `qz_instance` dispatch surface
- the browser-facing `OpenSteamOverlayURL` and `SetClipboardText` verbs were
  still absent from the live source bridge even though their retail HLIL bodies
  were already bounded

Primary evidence stayed inside the committed retail corpus and reconstructed
source tree:

- `docs/reverse-engineering/quakelive_steam_mapping_round_09.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_179.md`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `src/code/client/cl_cgame.c`
- `src/code/client/cl_main.c`
- `src/common/platform/platform_steamworks.c`
- `src/code/win32/win_main.c`

## Reconstructed Source Closures

### `qz_instance` now exports the retained overlay/clipboard browser methods

`cl_cgame.c` now binds the two remaining high-confidence browser verbs back
into the live `qz_instance` surface with their retail numeric IDs:

- `OpenSteamOverlayURL` (`11`)
- `SetClipboardText` (`13`)

`QLJSHandler_OnMethodCall` now dispatches them through source-owned helpers
instead of leaving them unbound:

- `OpenSteamOverlayURL` forwards to `CL_Steam_OpenOverlayUrl`
- `SetClipboardText` forwards to `Sys_SetClipboardData`

I still left the larger browser/matchmaking leftovers deferred:

- `RequestServers`
- `RequestServerDetails`
- `RefreshList`
- `Invite`
- `NoOp`

Those need a broader server-browser reconstruction pass rather than a small
exact wrapper closure.

### `cl_main.c` now owns the retained overlay URL shim

This round reconstructs a dedicated `CL_Steam_OpenOverlayUrl` helper in
`cl_main.c` so the browser bridge does not need to reach into provider details
directly.

The source shape matches the retained behavior pattern already used by the
other browser-owned Steam shims:

- reject empty URLs
- reject disabled/unavailable Steam social-overlay service
- call the platform wrapper
- log bounded ignore reasons on each failure path

### Steam Friends slot `0x78` is now source-backed

`platform_steamworks.c` now exposes
`QL_Steamworks_ActivateOverlayToWebPage`, which resolves the retained Steam
Friends web-overlay slot at `vtable[0x78 / 4]` and forwards the browser URL.

This mirrors the retail HLIL body in the `QLJSHandler_OnMethodCall` case:

- fetch Steam Friends interface
- load the `0x78` slot
- call it with the incoming URL

### Clipboard write ownership is now restored in the platform layer

The browser `SetClipboardText` path now lands on a real source-owned
`Sys_SetClipboardData` seam:

- `win_main.c` uses the retained Win32 flow:
  `OpenClipboard`, `EmptyClipboard`, `GlobalAlloc`, `GlobalLock`, copy bytes,
  `SetClipboardData( CF_TEXT, ... )`, `CloseClipboard`
- `unix_main.c` adds a bounded best-effort clipboard writer for
  `wl-copy`, `xclip`, and `xsel`
- `null_main.c` adds the matching no-op compatibility stub
- `qcommon.h` now exports the shared declaration

This keeps the strict-retail Windows target accurate while still leaving the
Unix/null owners explicitly bounded compatibility lanes.

## Verification

Static/source verification only:

- `python -m pytest tests/test_platform_services.py tests/test_steamworks_harness.py -q`
- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
- `MSBuild` of `Debug|Win32` using
  `WindowsTargetPlatformVersion=10.0.26100.0`
- `git diff --check`

The updated tests pin:

- the retail `qz_instance` method IDs for `OpenSteamOverlayURL` and
  `SetClipboardText`
- the `QLJSHandler_OnMethodCall` dispatch cases in `cl_cgame.c`
- the new `CL_Steam_OpenOverlayUrl` source shim in `cl_main.c`
- the `QL_Steamworks_ActivateOverlayToWebPage` wrapper and Steam Friends slot
  `0x78 / 4`
- the Win32/Unix/null clipboard-writer seams
- the runtime harness route for `ActivateOverlayToWebPage`

## Coverage Impact

This round is source-only. Host alias totals stay unchanged:

- raw aliases: `2038`
- strict Ghidra address-backed aliases: `1970`
- strict Ghidra address-backed coverage: `35.995%`

The largest-unaliased host queue is therefore unchanged as well:

1. `0x004FC240`
2. `0x0041AD70`
3. `0x004E6730`

## Parity Estimate

- strict-retail Windows target: `100% -> 100%`
- repo-wide reconstructed source base: `98% -> 98%`
