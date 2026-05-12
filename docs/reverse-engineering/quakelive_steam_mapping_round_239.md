# quakelive_steam.exe Mapping Round 239

Date: 2026-05-12

Scope: the retained client browser server-list failure seam in
`src/code/client/cl_main.c`, focused on reconstructing the retail engine-owned
`JSBrowser_OnServerFailedToRespond` event surface while avoiding external
library implementation work.

## Summary

This round closes the remaining server-list failure hole in the reconstructed
browser refresh lane. The checked-in source already published
`servers.details.*.response` and `servers.refresh.end`, but it still skipped
the retail callback shape for list entries that never answered the visible-ping
refresh.

Classification mix:

- `0` new engine/client aliases
- `0` engine/client alias renames
- `2` engine/client source reconstruction contract fixes
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main source-parity wins are:

- [`cl_main.c`](../../src/code/client/cl_main.c) now exposes
  `CL_SteamBrowser_PublishServerFailed(...)`, which publishes the retained
  `servers.details.%i.failed` event plus `{ "id": <index> }` payload shape.
- [`cl_main.c`](../../src/code/client/cl_main.c) now emits those failure
  events from `CL_SteamBrowser_PublishRefreshEnd(...)` for visible source-list
  slots that finish a browser refresh with `ping == 0`, before it publishes the
  retained `servers.refresh.end`.

## Evidence Notes

Observed facts from the committed retail corpus:

- Round 08 already pinned `sub_462DB0` as
  `JSBrowser_OnServerFailedToRespond`.
- The committed HLIL for that owner shows a one-field payload:
  - `id = arg1`
  - event name `servers.details.%i.failed`
- The same Round-08 evidence binds that owner to the `JSBrowser`
  `ISteamMatchmakingServerListResponse` vftable rather than the separate
  `JSBrowserDetails` object used for rules/players/detail queries.

Source-side inference used this round:

- The retail failed callback's single integer is best explained as the
  per-request server-list index supplied by
  `ISteamMatchmakingServerListResponse::ServerFailedToRespond(...)`.
- The current compatibility source has no retained Steam request handle or
  server-list callback object, so the nearest stable engine-owned analogue is
  the current source browser slot index inside the active visible list.
- In the source ping lane, a visible slot with `server[i].ping == 0` at refresh
  completion represents a server entry that never produced a successful
  `getinfo` reply before timeout, which is the closest source-owned equivalent
  to the retail failed-response callback.

## Source Reconstruction

- [`cl_main.c`](../../src/code/client/cl_main.c) now defines
  `CL_SteamBrowser_PublishServerFailed(...)` for the retained server-list
  failure event shape.
- [`cl_main.c`](../../src/code/client/cl_main.c) now checks the current source
  browser list during `CL_SteamBrowser_PublishRefreshEnd(...)` and publishes
  that failure event for each visible slot that:
  - still has a valid address
  - ended the refresh with `ping == 0`
- [`cl_main.c`](../../src/code/client/cl_main.c) still keeps the actual refresh
  completion publication in the same owner, so the compatibility lane mirrors
  the retail ordering as closely as the source browser permits:
  - per-server failures first
  - `servers.refresh.end` last

## Verification

Static/source validation:

- `pytest tests/test_platform_services.py -q --tb=no -k "client_browser_server_shims_reconstruct_retail_server_browser_surface"`
  passed with `1 passed, 74 deselected`
- `pytest tests/test_platform_services.py tests/test_engine_netcode_parity.py -q --tb=no -k "browser_server_shims or requestserverdetails or cl_serverinfopacket or cl_setserverinfo"`
  passed with `3 passed, 77 deselected`
- `git diff --check -- src/code/client/cl_main.c tests/test_platform_services.py docs/reverse-engineering/quakelive_steam_mapping_round_239.md`
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

- strict-retail client browser server-list failure seam: `99%` before,
  `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

The next nearby engine-only pass is to keep walking the remaining client
browser refresh/details compatibility seams where retail still exposes a
slightly sharper object-local boundary than the current source-owned browser
fallback carries, without drifting into the external matchmaking-server
backend.
