# Quake Live Steam Host Mapping Round 303

## Scope

This round reconstructs the retained `JSBrowser` request-owner lifecycle at
the Steamworks wrapper boundary. It still does not replace the client
source-browser compatibility lane, but it gives future client wiring a
retail-shaped owner for active refresh state, previous request release, manual
refresh, and refresh completion.

Evidence order:

- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt`
- `docs/reverse-engineering/quakelive_steam_mapping_round_297.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_302.md`

## Observed Facts

The `JSBrowser` vtable contains three server-list callbacks:

| Vtable slot | Retail owner | Meaning |
| --- | --- | --- |
| `0x00` | `JSBrowser_OnServerResponded` | read one row and publish `servers.details.<id>.response` |
| `0x04` | failed callback | publish `servers.details.%i.failed` |
| `0x08` | `JSBrowser_OnRefreshComplete` | clear refresh-active state and publish `servers.refresh.end` |

The request owner stores a refresh-active flag at object offset `+4` and the
Steam server-list request handle at `+8`.

`JSBrowser_RequestServers` only starts a new request when the active flag is
clear. If an old request handle is still present, it calls
`ISteamMatchmakingServers::ReleaseRequest` at vtable offset `0x18`, clears the
stored handle, sets the active flag, starts the requested list query, stores
the new handle, and publishes `servers.refresh.start`.

`SteamBrowser_RefreshList` checks the stored request handle and calls
`RefreshQuery` at vtable offset `0x24` when a handle is live.

`JSBrowser_OnRefreshComplete` clears only the active flag. The request handle
remains available until the next request start releases/replaces it.

## Source Reconstruction

`platform_steamworks.[ch]` now exposes a small owner type and lifecycle helpers:

- `ql_steam_server_browser_owner_t`
- `QL_Steamworks_InitServerBrowserOwner`
- `QL_Steamworks_BeginServerBrowserOwnerRequest`
- `QL_Steamworks_RefreshServerBrowserOwnerRequest`
- `QL_Steamworks_CompleteServerBrowserOwnerRequest`

The enabled wrapper behavior mirrors the observed owner contract:

- init clears active state and request handle;
- begin returns false if the owner is already active;
- begin releases an old inactive request before storing the new request;
- begin marks the owner active before/while storing the request handle;
- refresh dispatches through the existing request handle; and
- complete clears the active flag without clearing the request handle.

The disabled inline path stays inert and clears owner state on begin, so
default builds do not accidentally create live Steam browser state while
`QL_BUILD_ONLINE_SERVICES` / `QL_BUILD_STEAMWORKS` are disabled.

## Open Questions

- The future client owner still needs to allocate or embed this state alongside
  a native `ISteamMatchmakingServerListResponse` callback object.
- The wrapper does not publish browser events; the retained client still owns
  event names and source-browser compatibility publication.
- A destructor/shutdown owner may need stronger retail evidence before adding
  automatic final release outside the observed release-before-replace path.

## Verification

Focused validation passed:

- `python -m pytest tests/test_steamworks_harness.py::test_server_browser_owner_reconstructs_retail_refresh_lifecycle -q --tb=short`
  reported `2 passed`.
- `python -m pytest tests/test_steamworks_harness.py -q --tb=short`
  reported `66 passed`.
- `python -m pytest tests/test_platform_services.py::test_steamworks_modern_adapter_gaps_stay_explicit_until_owned tests/test_platform_services.py::test_client_browser_server_shims_reconstruct_retail_server_browser_surface -q --tb=short`
  reported `2 passed`.
- `git diff --check -- src/common/platform/platform_steamworks.c src/common/platform/platform_steamworks.h tests/steamworks_harness.c tests/test_steamworks_harness.py docs/plans/steamworks-parity-plan.md docs/steam_platform_abstraction.md docs/reverse-engineering/quakelive_steam_mapping_round_303.md`
  reported no whitespace errors.

No runtime game launch was needed; this pass covered wrapper lifecycle state
and harness behavior only.

## Parity Estimate

Before this round, the scoped native server-browser wrapper was about 81%
complete: request modes, row projection, detail queries, display fallback, and
query cancellation were present, but the retained `JSBrowser` active/request
state machine was still missing. After this round, the scoped native
server-browser wrapper is about 85% complete.

For the broader Steamworks subsystem, this nudges the estimate from about 67%
to about 68% parity with the observed retail Steamworks surface. The gain is
small but real: native browser ownership is still not client-wired, but the
state/lifecycle object needed for that wiring now exists and is test-pinned.
