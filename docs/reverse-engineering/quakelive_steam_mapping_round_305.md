# Quake Live Steam Host Mapping Round 305

## Scope

This round reconstructs the remaining lightweight `JSBrowser` list callback
identity projections: server-list failure and refresh completion. It keeps
client event publication unchanged, but makes the native wrapper expose the
same event identity a future client-owned `ISteamMatchmakingServerListResponse`
adapter will need.

Evidence order:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `docs/reverse-engineering/quakelive_steam_mapping_round_303.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_304.md`
- `src/code/client/cl_main.c`
- `src/common/platform/platform_steamworks.[ch]`

## Observed Facts

The retained `JSBrowser` server-list vtable has three callback slots:

| Vtable slot | Retail callback | Observed behavior |
| --- | --- | --- |
| `0x00` | `JSBrowser_OnServerResponded` | row response projection, reconstructed in round 304 |
| `0x04` | failed-to-respond callback | publishes `servers.details.%i.failed` |
| `0x08` | `JSBrowser_OnRefreshComplete` | clears the active flag and publishes `servers.refresh.end` |

The failure callback builds a one-field object with `id = serverIndex` and
uses the same integer in the event name format string
`servers.details.%i.failed`. The source compatibility publisher in
`CL_SteamBrowser_PublishServerFailed` already mirrors this event family.

The refresh-complete callback clears the owner active flag at object offset
`+4` and publishes the constant event name `servers.refresh.end`. Round 303
reconstructed the owner active flag transition; this round adds the event
identity projection that travels with that transition.

## Source Reconstruction

`platform_steamworks.[h/c]` now exposes:

- `ql_steam_server_browser_failure_t`
- `ql_steam_server_browser_refresh_complete_t`
- `QL_Steamworks_FormatServerBrowserFailureEventName`
- `QL_Steamworks_BuildServerBrowserFailure`
- `QL_Steamworks_BuildServerBrowserRefreshComplete`

The failure projection preserves the signed integer index, including negative
values, because the retail format string uses `%i`. The refresh-complete
projection carries the constant `servers.refresh.end` event name.

Disabled builds zero the projection structures and return false so default
builds do not report native browser callbacks while Steamworks is disabled.

## Open Questions

- The future native client adapter still needs to publish these projections
  through the retained browser event bridge.
- The source compatibility publisher already emits matching event names; the
  client wiring step needs to avoid double-publishing when native ownership is
  enabled.

## Verification

Focused validation passed:

- `python -m pytest tests/test_steamworks_harness.py::test_server_browser_failure_and_refresh_projections_match_retail_callbacks -q --tb=short`
  reported `2 passed`.
- `python -m pytest tests/test_steamworks_harness.py -q --tb=short`
  reported `70 passed`.
- `python -m pytest tests/test_platform_services.py::test_steamworks_modern_adapter_gaps_stay_explicit_until_owned tests/test_platform_services.py::test_client_browser_server_shims_reconstruct_retail_server_browser_surface -q --tb=short`
  reported `2 passed`.
- `git diff --check -- src/common/platform/platform_steamworks.c src/common/platform/platform_steamworks.h tests/steamworks_harness.c tests/test_steamworks_harness.py docs/plans/steamworks-parity-plan.md docs/steam_platform_abstraction.md docs/reverse-engineering/quakelive_steam_mapping_round_305.md`
  reported no whitespace errors.

No runtime game launch was needed; this pass covered wrapper projection and
harness behavior only.

## Parity Estimate

Before this round, the scoped native server-browser wrapper was about 88%
complete: row responses and owner lifecycle were reconstructed, but failure
and refresh-complete callback identities were still implicit. After this
round, the scoped wrapper is about 90% complete.

For the broader Steamworks subsystem, this keeps the estimate at about 68%
parity with the observed retail Steamworks surface. The native browser callback
projection surface is more complete, but client event publication is still
intentionally open.
