# quakelive_steam.exe Mapping Round 233

Date: 2026-05-11

Scope: the retained client Steam/browser shutdown and bootstrap lifetime seam
in `src/code/client/cl_main.c` and `src/code/qcommon/common.c`, staying inside
engine-owned lifecycle code and avoiding external-library implementation work.

## Summary

This round tightens the follow-through from the previous Steam bootstrap pass:
`SteamClient_Init` is now a one-call startup owner again, and `CL_Shutdown`
stops removing the late browser/Steam command block that the committed retail
shutdown lane does not touch.

Classification mix:

- `0` new engine/client aliases
- `0` engine/client alias renames
- `2` engine/client source reconstruction lifetime fixes
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main source-parity wins are:

- [`common.c`](../../src/code/qcommon/common.c) now calls
  `SteamClient_Init()` only from the primary client-startup path, matching the
  single committed retail call site instead of re-running it from the
  dedicated-toggle reentry lane
- [`CL_Shutdown`](../../src/code/client/cl_main.c) now stops removing the
  retail-persistent late command block after `advert_done`, including:
  - `web_showBrowser`
  - `web_changeHash`
  - `web_hideBrowser`
  - `web_showError`
  - `web_clearCache`
  - `web_reload`
  - `+voice`
  - `-voice`
  - `connect_lobby`
  - `clientviewprofile`
  - `clientfriendinvite`
  - `stats_clear`

## Evidence Notes

- The committed retail common startup lane shows one bounded `SteamClient_Init`
  call site:
  - `004cc16e  sub_461500()`
- The committed retail `CL_Init` owner still has multiple call sites, including
  the dedicated-toggle restart path, so the one-time Steam bootstrap call and
  the repeatable client bootstrap call are not the same lifecycle seam.
- The committed retail `CL_Shutdown` lane around `sub_4B9E10` removes commands
  only through:
  - `sub_4c8270("advert_done")`
  - then `sub_4cd250("cl_running", "0")`
- There are no committed retail shutdown-side `Cmd_RemoveCommand` calls for the
  browser-host command block, `+voice` / `-voice`, `connect_lobby`,
  `clientviewprofile`, `clientfriendinvite`, or `stats_clear`.
- The committed retail init-side evidence for those commands remains explicit:
  - `sub_4f3cd0()` registers the six `web_*` commands
  - `sub_461500` registers `+voice`, `-voice`, and conditional `stats_clear`
  - `sub_465840` registers `connect_lobby`
  - `CL_Init` registers `clientviewprofile` and `clientfriendinvite`

## Source Reconstruction

- [`common.c`](../../src/code/qcommon/common.c) no longer re-runs
  `SteamClient_Init()` from the `com_dedicated->modified` client restart lane.
- [`cl_main.c`](../../src/code/client/cl_main.c) now matches the retail
  shutdown surface more closely by ending the explicit remove-command list at
  `advert_done`.

## Verification

Static/source validation:

- `pytest tests/test_engine_client_command_parity.py tests/test_platform_services.py -q --tb=no -k "shutdown or steam_client_init or steam_lobby_init or connect_lobby or voice or stats_clear or browser or clientviewprofile or clientfriendinvite"`
  passed with `13 passed, 77 deselected`
- `git diff --check -- src/code/qcommon/common.c src/code/client/cl_main.c tests/test_engine_client_command_parity.py tests/test_platform_services.py`
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

- strict-retail client Steam/browser shutdown-lifetime lane: `99%` before,
  `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

The next nearby engine-only pass is to keep separating one-time process
bootstrap from repeatable client bootstrap in the remaining client runtime
owners, while resisting speculative moves into external-library packet or UI
runtime internals.
