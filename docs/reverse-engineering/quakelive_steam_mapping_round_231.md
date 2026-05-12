# quakelive_steam.exe Mapping Round 231

Date: 2026-05-11

Scope: the retained client browser-host registration seam in
`src/code/client/cl_main.c` and `src/code/client/cl_cgame.c`, staying inside
engine-owned command and cvar wiring rather than external-library code.

## Summary

This round reconstructs the retail `sub_4F3CD0` browser registration helper as
an explicit source owner instead of keeping that work inlined inside
`CL_Init`.

Classification mix:

- `0` new engine/client aliases
- `0` engine/client alias renames
- `1` engine/client source reconstruction boundary fix
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main source-parity wins are:

- restored an explicit `QLWebHost_RegisterCommands()` helper in
  [`cl_cgame.c`](../../src/code/client/cl_cgame.c)
- switched [`CL_Init`](../../src/code/client/cl_main.c) to call that helper
  instead of registering the six `web_*` commands inline
- moved the retail-adjacent `web_zoom`, `web_console`, and
  `web_browserActive` cvar registration into the same helper, matching the
  committed HLIL ownership more closely

## Evidence Notes

- The committed retail `CL_Init` lane still shows the browser registration work
  as a dedicated helper call:
  - `004bcda7  sub_4c81d0("clientviewprofile", sub_460e60)`
  - `004bcdb6  sub_4c81d0("clientfriendinvite", sub_460e60)`
  - `004bcdbe  sub_4f3cd0()`
- The committed retail HLIL for `sub_4F3CD0` shows the exact ownership surface:
  - `004f3cda  sub_4c81d0("web_showBrowser", sub_4f3160)`
  - `004f3ce9  sub_4c81d0("web_changeHash", sub_4f31d0)`
  - `004f3cf8  sub_4c81d0("web_hideBrowser", sub_4f24d0)`
  - `004f3d07  sub_4c81d0("web_showError", sub_4f3cb0)`
  - `004f3d16  sub_4c81d0("web_clearCache", sub_4f2a10)`
  - `004f3d25  sub_4c81d0("web_reload", sub_4f2a30)`
  - `004f3d47  ... "web_zoom", "100", 1`
  - `004f3d60  ... "web_console", "0", 1`
  - `004f3d6d  return ... "web_browserActive", "0", 0x40`
- The checked-in source already had the recovered public command owners
  `CL_Web_ShowBrowser_f`, `CL_Web_ChangeHash_f`, `CL_Web_HideBrowser_f`,
  `CL_Web_ShowError_f`, `CL_Web_ClearCache_f`, and `CL_Web_Reload_f`, but the
  registration boundary was still flattened into `CL_Init`.
- Reconstructing the helper in source keeps the established alias
  `sub_4F3CD0 -> QLWebHost_RegisterCommands` aligned with the checked-in engine
  ownership instead of leaving it as a note-only mapping.

## Source Reconstruction

- [`cl_cgame.c`](../../src/code/client/cl_cgame.c) now defines
  `QLWebHost_RegisterCommands()` with the six retained browser command
  registrations plus the `web_zoom`, `web_console`, and `web_browserActive`
  cvar registrations visible in the retail helper body.
- [`cl_main.c`](../../src/code/client/cl_main.c) now calls
  `QLWebHost_RegisterCommands();` from `CL_Init` and no longer keeps that
  browser-host wiring inlined there.
- [`client.h`](../../src/code/client/client.h) now exposes the helper
  prototype, and the stale direct `CL_Web_*` forward declarations were removed
  from `cl_main.c`.

## Verification

Static/source validation:

- `pytest tests/test_engine_client_command_parity.py tests/test_awesomium_browser_parity.py tests/test_platform_services.py tests/test_engine_cvar_retail_parity.py -q --tb=no -k "browser or web_console or web_zoom or web_browserActive or client_command_registration"`
  passed with `23 passed, 115 deselected`
- `git diff --check -- src/code/client/client.h src/code/client/cl_main.c src/code/client/cl_cgame.c tests/test_engine_client_command_parity.py tests/test_awesomium_browser_parity.py tests/test_platform_services.py tests/test_engine_cvar_retail_parity.py`
  reported only the repo's existing LF -> CRLF normalization warnings on the
  touched text files

Alias accounting for the current dirty worktree:

- before this pass: `2238` raw `quakelive_steam` aliases, `2157` strict
  address-backed aliases
- after this pass: `2238` raw `quakelive_steam` aliases, `2157` strict
  address-backed aliases
- strict Ghidra address-backed coverage after this pass: `39.412%` of `5473`
  committed functions

Parity estimate after this pass:

- strict-retail client browser registration-helper lane: `99%` before,
  `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

The next nearby engine-only pass is to keep walking the remaining browser host
and client command registration seams where the checked-in source still flattens
or overexposes retail helper boundaries.
