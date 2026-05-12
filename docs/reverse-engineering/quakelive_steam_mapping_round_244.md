# quakelive_steam.exe Mapping Round 244

Date: 2026-05-12

Scope: the retained client browser/social overlay-URL validation seam in
`src/code/client/cl_cgame.c`, `src/code/client/cl_main.c`, and
`src/common/platform/platform_steamworks.c`, focused on reconstructing the
retail engine-owned `OpenSteamOverlayURL` argument contract while avoiding
external-library implementation work.

## Summary

This round relaxes the reconstructed overlay-web-page path so the source no
longer rejects empty-but-present URL strings before the Steam Friends
`ActivateGameOverlayToWebPage` call. The checked-in bridge was still enforcing
three separate empty-string guards:

- the `qz_instance` browser dispatcher rejected `arguments[0][0] == '\0'`
- `CL_Steam_OpenOverlayUrl(...)` rejected `url[0] == '\0'`
- `QL_Steamworks_ActivateOverlayToWebPage(...)` rejected `url[0] == '\0'`

The committed retail dispatcher does not show an equivalent empty-string
filter. It stringifies the first JS argument and forwards the resulting buffer
into the Steam Friends `0x78` slot directly.

Classification mix:

- `0` new engine/client aliases
- `0` engine/client alias renames
- `2` engine/client source reconstruction contract fixes
- `1` platform-service-owned function contract fix
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main source-parity wins are:

- [`cl_cgame.c`](../../src/code/client/cl_cgame.c) now rejects only a missing
  argument slot for `OpenSteamOverlayURL` in `QLJSHandler_OnMethodCall(...)`,
  leaving empty-but-present strings to flow into the client shim.
- [`cl_main.c`](../../src/code/client/cl_main.c) now logs
  `"missing overlay url"` only when the incoming pointer is null in
  `CL_Steam_OpenOverlayUrl(...)`.
- [`platform_steamworks.c`](../../src/common/platform/platform_steamworks.c)
  now mirrors that contract in `QL_Steamworks_ActivateOverlayToWebPage(...)`
  instead of short-circuiting on `url[0] == '\0'` before the retained Steam
  Friends web-overlay call.

## Evidence Notes

Observed facts from the committed retail corpus:

- The retained non-returning browser dispatcher reaches the web-overlay arm
  immediately before the next printed case label at `00432036`.
- In that retail arm:
  - `0043200b` fetches `SteamFriends()`
  - `00432015` through `0043201f` select the UTF-8 buffer produced from the
    first JS argument
  - `00432025` calls the Steam Friends virtual slot `0x78` with that buffer
- No empty-string precheck is visible between the string conversion and the
  retained `0x78` call in that path.

Source-side inference used this round:

- The current reconstructed browser path already centralizes this behavior in
  the `QLJSHandler_OnMethodCall(...)` dispatcher plus the two source-owned
  wrappers `CL_Steam_OpenOverlayUrl(...)` and
  `QL_Steamworks_ActivateOverlayToWebPage(...)`.
- Matching the retail null-versus-empty boundary at those three owners is the
  cleanest local reconstruction, and it keeps the checked-in bridge aligned
  with the retail “argument slot exists, then stringified payload flows
  through” contract.
- The null-pointer guards remain in place because the reconstructed browser
  bridge still uses nullable `const char *` arguments at the source boundary,
  while the retained host path always has a concrete Awesomium value object to
  stringify.

## Source Reconstruction

- [`cl_cgame.c`](../../src/code/client/cl_cgame.c) now checks only
  `argumentCount < 1` before dispatching `OpenSteamOverlayURL`.
- [`cl_main.c`](../../src/code/client/cl_main.c) now treats only a null
  pointer as a missing overlay URL in `CL_Steam_OpenOverlayUrl(...)`.
- [`platform_steamworks.c`](../../src/common/platform/platform_steamworks.c)
  now returns `qfalse` only for a null URL pointer before resolving the Steam
  Friends interface and `0x78` slot.
- [`test_platform_services.py`](../../tests/test_platform_services.py) now
  pins the relaxed `OpenSteamOverlayURL` dispatch and wrapper contracts.
- [`test_steamworks_harness.py`](../../tests/test_steamworks_harness.py) now
  verifies that the platform wrapper still routes an empty-but-present web
  overlay URL into the mock Steam Friends slot when Steamworks is enabled.

## Verification

Static/source validation:

- `pytest tests/test_platform_services.py -q --tb=no -k "client_browser_js_bridge_reconstructs_qz_instance_contract or client_browser_lobby_social_shims_reconstruct_retail_qz_instance_dispatch_surface"`
  passed with `2 passed, 73 deselected`
- `pytest tests/test_steamworks_harness.py -q --tb=no -k "activate_overlay_to_web_page_routes_url"`
  passed with `2 passed, 32 deselected`
- `git diff --check -- src/code/client/cl_cgame.c src/code/client/cl_main.c src/common/platform/platform_steamworks.c tests/test_platform_services.py tests/test_steamworks_harness.py docs/reverse-engineering/quakelive_steam_mapping_round_244.md`
  reported only the repo's existing LF -> CRLF normalization warnings on the
  touched text files

Additional note:

- Pytest still emitted the existing `.pytest_cache` permission warning, but
  the assertions passed.

Alias accounting for the current dirty worktree:

- before this pass: `2238` raw `quakelive_steam` aliases, `2157` strict
  address-backed aliases
- after this pass: `2238` raw `quakelive_steam` aliases, `2157` strict
  address-backed aliases
- strict Ghidra address-backed coverage after this pass: `39.412%` of `5473`
  committed functions

Parity estimate after this pass:

- strict-retail client browser/social overlay URL-validation seam: `99%`
  before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

The next nearby engine-only pass is to keep walking the retained
browser-driven social/matchmaking methods where the reconstructed source still
may impose slightly sharper argument validation than the committed `qz_instance`
dispatcher appears to carry.
