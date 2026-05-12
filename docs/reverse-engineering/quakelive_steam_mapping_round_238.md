# quakelive_steam.exe Mapping Round 238

Date: 2026-05-11

Scope: the retained client browser/details timeout seam in
`src/code/client/cl_main.c`, focused on reconstructing retail engine-owned
failure event publication while avoiding external-library implementation work.

## Summary

This round closes a small but meaningful browser parity gap in the details
timeout path. The checked-in source was clearing active detail requests
silently when the timeout expired; retail exposes explicit rules/players
failure notifications for that request family, so the reconstructed engine now
publishes those engine-owned browser events before it clears request state.

Classification mix:

- `0` new engine/client aliases
- `0` engine/client alias renames
- `3` engine/client source reconstruction contract fixes
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main source-parity wins are:

- [`cl_main.c`](../../src/code/client/cl_main.c) now has a dedicated
  `CL_SteamBrowser_FailDetailRequest(...)` owner for timeout cleanup, instead
  of collapsing the path into a raw `CL_SteamBrowser_ClearDetailRequest()`.
- [`cl_main.c`](../../src/code/client/cl_main.c) now publishes
  `servers.rules.%s.failed` with retail-shaped `{"id","ip","port"}` payloads
  before clearing an expired detail request.
- [`cl_main.c`](../../src/code/client/cl_main.c) now publishes
  `servers.players.%s.failed` with the same request-local payload contract
  before timeout cleanup completes.

## Evidence Notes

- The committed retail rules failure callback at `sub_462490` publishes
  `servers.rules.%s.failed` using the request-local detail token and a payload
  containing:
  - `id`
  - `ip`
  - `port`
- The committed retail players failure callback at `sub_462830` publishes
  `servers.players.%s.failed` with the same request-local payload shape.
- The committed retail rules response/end owners at `sub_462360` and
  `sub_4625A0`, plus the players response/end owners at `sub_4626B0` and
  `sub_462940`, show that rules/players lifecycle events are consistently keyed
  off the stored request detail token rather than the separate details-response
  ID.
- The checked-in compatibility source still drives this lane through the
  engine-side `CL_ServerStatus` request/response path rather than retail's
  original matchmaking-server callback graph, so the timeout owner is the right
  place to synthesize the retained failure notifications without inventing
  external-library behavior.
- Retail also has a separate details-failure owner at `sub_462DB0`, but that
  callback's opaque numeric argument contract is not modeled cleanly by the
  current compatibility lane, so this round intentionally avoids forcing a
  speculative `servers.details.*.failed` reconstruction.

## Source Reconstruction

- [`cl_main.c`](../../src/code/client/cl_main.c) now exposes
  `CL_SteamBrowser_PublishRulesFailed(...)` for the retained browser failure
  event contract.
- [`cl_main.c`](../../src/code/client/cl_main.c) now exposes
  `CL_SteamBrowser_PublishPlayersFailed(...)` for the matching players failure
  contract.
- [`cl_main.c`](../../src/code/client/cl_main.c) now routes detail timeout
  expiry through `CL_SteamBrowser_FailDetailRequest(...)`, which:
  - publishes retained rules/players failed events
  - preserves the active request's detail token, packed IP, and port long
    enough to build those payloads
  - clears request state only after the failure events are emitted

## Verification

Static/source validation:

- `pytest tests/test_platform_services.py -q --tb=no -k "client_browser_server_shims_reconstruct_retail_server_browser_surface"`
  passed with `1 passed, 74 deselected`
- `pytest tests/test_platform_services.py tests/test_engine_netcode_parity.py -q --tb=no -k "browser_server_shims or requestserverdetails or cl_serverinfopacket or cl_setserverinfo"`
  passed with `3 passed, 77 deselected`
- `git diff --check -- src/code/client/cl_main.c tests/test_platform_services.py docs/reverse-engineering/quakelive_steam_mapping_round_238.md`
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

- strict-retail client browser/details timeout-failure seam: `99%` before,
  `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

The next nearby engine-only pass is to keep walking the remaining client
browser/details lifecycle seams where retail still exposes a slightly sharper
request-local helper boundary or failure contract than the checked-in
compatibility source currently carries, while continuing to stay out of Steam
matchmaking backend internals.
