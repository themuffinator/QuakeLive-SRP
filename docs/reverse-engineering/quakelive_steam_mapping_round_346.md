# Quake Live Steam Host Mapping Round 346

## Scope

This round tightens the native `ISteamMatchmakingServers`
`RequestServerDetails` lifecycle after the WebUI detail owner was wired into
the client. Earlier rounds reconstructed the retail ping/rules/player dispatch
order, the response-object views, the shared three-terminal-callback lifecycle,
and the native detail callback owner. This pass fixes the source-side failure
boundary where one detail probe could fail to return a valid query handle while
the retained detail owner still reported an active native request.

Evidence order:

- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
- `references/analysis/quakelive_symbol_aliases.json`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `docs/reverse-engineering/quakelive_steam_mapping_round_297.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_300.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_310.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_343.md`
- `src/common/platform/platform_steamworks.c`
- `tests/steamworks_harness.c`

## Observed Facts

The owning binary remains `quakelive_steam.exe`. The Ghidra import table
contains `STEAM_API.DLL!SteamMatchmakingServers`, and the alias map promotes
`sub_461F70` as `JSBrowserDetails_RequestServerDetails`.

The committed HLIL and earlier mapping rounds show that the retained detail
owner starts three native probes in this order:

| Vtable offset | API role | Retail call order | Response object |
| --- | --- | --- | --- |
| `0x34` | `PingServer` | first | `this + 8` |
| `0x3c` | `ServerRules` | second | `this + 0` |
| `0x38` | `PlayerDetails` | third | `this + 4` |

Round 300 also identified the adjacent older-Steamworks
`CancelServerQuery` slot at vtable offset `0x40`. The committed HLIL slice does
not show a retail cancellation branch in `JSBrowserDetails_RequestServerDetails`
or in its terminal callbacks, so cancellation remains a source-side lifecycle
guard for the reconstructed wrapper rather than a claimed retail branch.

The current client detail path calls
`QL_Steamworks_BeginServerBrowserDetailRequest` first in opted-in Steamworks
builds. When that returns false, the client keeps the existing UDP
`CL_ServerStatus` detail fallback path.

## Source Reconstruction

`QL_Steamworks_RequestServerDetails` now treats the native ping/rules/player
bundle as all-or-nothing. It still dispatches in the observed retail order:

1. `PingServer`
2. `ServerRules`
3. `PlayerDetails`

After dispatch, the wrapper validates all three returned query handles. If any
handle is non-positive, the wrapper calls `QL_Steamworks_CancelServerQuery` for
each handle. That helper already ignores non-positive query handles, so only
valid partial handles are canceled. The function then returns false without
writing any output handles, leaving the caller's outputs at the existing zeroed
failure state.

This matters because `QL_Steamworks_BeginServerBrowserDetailRequest` only marks
the retained detail owner active after `QL_Steamworks_RequestServerDetails`
returns true. A partial native allocation now falls through to the source
status-query fallback instead of creating an active native sidecar that cannot
receive all three terminal callbacks.

## Harness Coverage

The Steamworks harness now exposes
`QLR_SteamworksMock_SetServerBrowserDetailQueryResults`, allowing tests to
force ping, players, or rules query handles to fail. The enabled harness path
pins both layers:

- `QLR_Steamworks_RequestServerDetails` returns false with zeroed outputs when
  the mocked player query handle is zero, while canceling the valid ping and
  rules handles.
- `QLR_Steamworks_BeginServerBrowserDetailRequest` leaves the retained request
  inactive and handleless for the same partial native failure.

The source manifest also pins the invariant that the query-handle validation
and partial cancellation happen after the observed ping/rules/player dispatch
order.

## Open Questions

- The committed HLIL does not prove retail explicitly checked invalid detail
  query handles. This round should be read as source-side lifecycle
  reconstruction for the native-first wrapper, grounded in the observed query
  handles and adjacent cancel slot.
- Strong live parity for friends/history browser modes and unusual provider
  failure cases still needs comparison against a Steam-enabled retail
  environment.
- Retained WebUI `recent` or out-of-range mode behavior remains a separate
  browser semantics question.

## Verification

Focused validation for this pass:

- `python -m pytest tests/test_steamworks_harness.py::test_server_browser_helpers_use_mapped_matchmaking_servers_slots tests/test_steamworks_harness.py::test_server_browser_detail_request_owner_reconstructs_retail_response_views_and_release tests/test_netcode_parity_manifest.py::test_ql_server_browser_and_master_heartbeat_related_wiring_parity_recheck -q --tb=short`
  reported `5 passed`.
- `python -m pytest tests/test_steamworks_harness.py -q --tb=short`
  reported `80 passed`.
- `python -m pytest tests/test_platform_services.py::test_steamworks_modern_adapter_gaps_stay_explicit_until_owned tests/test_netcode_parity_manifest.py::test_ql_server_browser_and_master_heartbeat_related_wiring_parity_recheck -q --tb=short`
  reported `2 passed`.
- `"C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe" src\code\quakelive.sln /t:quakelive_steam /p:Configuration=Debug /p:Platform=x86 /p:PlatformToolset=v141`
  completed with `0 Warning(s), 0 Error(s)`.
- `"C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe" src\code\quakelive.sln /t:quakelive_steam /p:Configuration=Debug /p:Platform=x86 /p:PlatformToolset=v141 /p:QLBuildOnlineServices=1 /p:QLBuildSteamworks=1 /p:QLRequireSteamworksSdk=0 /p:QLRequireAwesomiumSdk=0`
  completed with `2 Warning(s), 0 Error(s)`. Both warnings were existing
  BSCMAKE `BK4502` browse-info truncation warnings for
  `cl_awesomium_win32.sbr` and `platform_backend_steamworks.sbr`.
- `git diff --check` reported no whitespace errors; Git still printed the
  existing CRLF conversion warnings for touched and pre-existing dirty files.

No runtime game launch was needed; this pass covered Steamworks wrapper state,
native detail-owner fallback behavior, source-bound parity guards, and harness
behavior.

## Parity Estimate

Before this round, the focused native server-browser detail query-handle
failure path was about 86% complete: the native detail owner was wired and
terminal callbacks were reconstructed, but partial native query allocation
could suppress the UDP status-query fallback and retain an active detail owner
with missing terminal callbacks. After this round, the focused path is about
98% complete.

Broader WebUI server-browser ownership remains about 99% complete in this tree.
The remaining uncertainty is semantic/live parity for less-traveled list modes
and provider environments, not absence of native list/detail owners. Repo-wide
parity remains about 99%.
