# quakelive_steam.exe Mapping Round 237

Date: 2026-05-11

Scope: the retained client browser/details request seam in
`src/code/client/cl_main.c`, focused on retail engine-owned server-browser ID
formatting and event-shape exactness while avoiding external-library
implementation work.

## Summary

This round tightens a small but real retail exactness gap in the reconstructed
browser/details lane: the checked-in source was flattening the signed-port
detail token and the unsigned details-response ID into one shared string, while
retail keeps those two shapes distinct.

Classification mix:

- `0` new engine/client aliases
- `0` engine/client alias renames
- `3` engine/client source reconstruction contract fixes
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main source-parity wins are:

- [`cl_main.c`](../../src/code/client/cl_main.c) now formats the stored detail
  token through `CL_SteamBrowser_FormatDetailId(...)` as `"%u_%i"`, matching
  the retained `JSBrowserDetails_RequestServerDetails` owner.
- [`cl_main.c`](../../src/code/client/cl_main.c) now formats browser detail
  request address strings as `"%u.%u.%u.%u:%i"`, again matching the retained
  request object bootstrap more closely.
- [`cl_main.c`](../../src/code/client/cl_main.c) now publishes
  `servers.details.*.response` with a distinct unsigned response ID
  (`"%u_%u"`), instead of incorrectly reusing the signed detail token that
  retail reserves for the rules/players callback family.

## Evidence Notes

- The committed retail request-object bootstrap at `sub_461F70` shows two
  exact formatting contracts:
  - `_snprintf(..., "%u.%u.%u.%u:%i", ...)`
  - `sprintf(arg1 + 0x14, "%u_%i", arg2, arg3)`
- The committed retail details-response callback at `sub_461FE0` keeps a
  separate unsigned ID shape for the response payload:
  - payload field `id = "%u_%u"`
  - event name `servers.details.%u_%u.response`
- The committed retail rules and players callbacks at `sub_462360`,
  `sub_462490`, `sub_4625A0`, and `sub_4626B0` continue to use the stored
  request-object token (`arg1 + 0x14`) for:
  - `servers.rules.%s.response`
  - `servers.rules.%s.failed`
  - `servers.rules.%s.end`
  - `servers.players.%s.response`
- The checked-in source already had all the right owners, but it was collapsing
  those two retail ID contracts into one shared `%u_%u` string.

## Source Reconstruction

- [`cl_main.c`](../../src/code/client/cl_main.c) now formats the retained
  address string with a signed port in `CL_SteamBrowser_BuildAddressString`.
- [`cl_main.c`](../../src/code/client/cl_main.c) now formats the retained
  rules/players detail token with a signed port in
  `CL_SteamBrowser_FormatDetailId`.
- [`cl_main.c`](../../src/code/client/cl_main.c) now builds a separate
  `responseId` for `CL_SteamBrowser_PublishServerResponse`, preserving the
  retail split between:
  - signed `%u_%i` detail token for rules/players callback state
  - unsigned `%u_%u` details response ID for `servers.details` payloads/events

## Verification

Static/source validation:

- `pytest tests/test_platform_services.py -q --tb=no -k "client_browser_server_shims_reconstruct_retail_server_browser_surface"`
  passed with `1 passed, 74 deselected`
- `pytest tests/test_platform_services.py tests/test_engine_netcode_parity.py -q --tb=no -k "browser_server_shims or requestserverdetails or cl_serverinfopacket or cl_setserverinfo"`
  passed with `3 passed, 77 deselected`
- `git diff --check -- src/code/client/cl_main.c tests/test_platform_services.py docs/reverse-engineering/quakelive_steam_mapping_round_237.md`
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

- strict-retail client browser/details ID-contract seam: `99%` before,
  `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

The next nearby engine-only pass is to keep walking the remaining client
browser/bootstrap seams where retail object-local formatting or helper
boundaries are still slightly flattened in writable source, while continuing to
stay out of Steam matchmaking-server backend internals.
