# Quake Live Steam Host Mapping Round 310

## Scope

This round reconstructs the retained `JSBrowserDetails` request-owner view
used to launch one server-detail probe bundle. Round 309 modeled the shared
completion counter; this pass adds the base-object callback views that feed
`PingServer`, `ServerRules`, and `PlayerDetails`, then wraps them in a small
native sidecar request state for future client integration.

Evidence order:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `docs/reverse-engineering/quakelive_steam_mapping_round_309.md`
- `src/common/platform/platform_steamworks.[ch]`
- `tests/steamworks_harness.c`
- `tests/test_steamworks_harness.py`

## Observed Facts

`sub_4630b0` allocates `0x58` bytes and installs three retained callback views
before calling `sub_461f70`:

| Base-object offset | Retained callback view |
| --- | --- |
| `+0` | `JSBrowserDetails` rules response |
| `+4` | `JSBrowserDetails` players response |
| `+8` | `JSBrowserDetails` ping response |

`sub_461f70` writes the server identity once at the base object:

| Field | Offset |
| --- | --- |
| server IP | `+0xc` |
| server port | `+0x10` |
| detail id | `+0x14`, formatted as `"%u_%i"` |

It then launches the detail probes in this order:

| Steamworks slot | Retail call | Response pointer |
| --- | --- | --- |
| `0x34` | `PingServer` | `base + 8` |
| `0x3c` | `ServerRules` | `base + 0` |
| `0x38` | `PlayerDetails` | `base + 4` |

The committed HLIL does not show the returned query handles being stored in
the retained `JSBrowserDetails` object. The wrapper-side request struct records
them as sidecar state only, so tests and future client code can observe the
native request bundle without claiming those handles are retail object fields.

## Source Reconstruction

`platform_steamworks.[h/c]` now exposes:

- `QL_STEAM_SERVER_BROWSER_DETAIL_RULES_RESPONSE_OFFSET`
- `QL_STEAM_SERVER_BROWSER_DETAIL_PLAYERS_RESPONSE_OFFSET`
- `QL_STEAM_SERVER_BROWSER_DETAIL_PING_RESPONSE_OFFSET`
- `ql_steam_server_browser_detail_response_views_t`
- `ql_steam_server_browser_detail_request_t`
- `QL_Steamworks_BuildServerBrowserDetailResponseViews`
- `QL_Steamworks_InitServerBrowserDetailRequest`
- `QL_Steamworks_BeginServerBrowserDetailRequest`
- `QL_Steamworks_CompleteServerBrowserDetailRequestCallback`

The response-view builder projects `base`, `base + 4`, and `base + 8` exactly
as the HLIL request path does. The begin helper initializes the detail identity,
builds the three response views, launches `PingServer -> ServerRules ->
PlayerDetails` through the existing slot wrapper, and records the returned
query handles outside the emulated retail object. The completion helper
delegates to the shared three-terminal-callback lifecycle counter from round
309, then clears the sidecar query/base fields once release readiness is
reported.

Disabled builds zero the request/view structures and return false, preserving
the default-offline Steamworks divergence policy.

## Open Questions

- The real `operator new(0x58)` allocation, C++ vtables, and callback method
  dispatch remain unwired in client code.
- The source-browser compatibility publisher still owns client browser events.
  Native detail events need one client owner before publication is enabled.
- Query-handle cancellation remains a low-level wrapper primitive from round
  300, not an observed `JSBrowserDetails` object behavior in this HLIL slice.

## Verification

Focused validation passed:

- `python -m pytest tests/test_steamworks_harness.py::test_server_browser_detail_request_owner_reconstructs_retail_response_views_and_release -q --tb=short`
  reported `2 passed`.

Broader validation also passed:

- `python -m pytest tests/test_steamworks_harness.py -q --tb=short`
  reported `78 passed`.
- `python -m pytest tests/test_platform_services.py::test_msbuild_steamworks_sdk_dependency_stays_external_and_optional tests/test_platform_services.py::test_steamworks_modern_adapter_gaps_stay_explicit_until_owned tests/test_platform_services.py::test_client_browser_server_shims_reconstruct_retail_server_browser_surface -q --tb=short`
  reported `3 passed`.
- `git diff --check -- src/common/platform/platform_steamworks.c src/common/platform/platform_steamworks.h tests/steamworks_harness.c tests/test_steamworks_harness.py docs/plans/steamworks-parity-plan.md docs/steam_platform_abstraction.md docs/reverse-engineering/quakelive_steam_mapping_round_310.md`
  reported no whitespace errors; Git only emitted existing line-ending
  normalization warnings for tracked files.

No runtime game launch is needed for this pass; this is native wrapper and
harness reconstruction only.

## Parity Estimate

Before this round, the scoped native server-browser wrapper was about 95%
complete: the detail completion threshold was explicit, but the callback-view
request bundle was still only implicit in the low-level `RequestServerDetails`
wrapper. After this round, the scoped wrapper is about 96% complete.

For the broader Steamworks subsystem, this keeps the estimate at about 69%
parity with the observed retail Steamworks surface. The detail request bundle
is now modeled, while real callback allocation and client publication remain
open.
