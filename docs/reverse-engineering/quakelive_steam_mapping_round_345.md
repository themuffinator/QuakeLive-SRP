# Quake Live Steam Host Mapping Round 345

## Scope

This round tightens the native `ISteamMatchmakingServers` list-owner failure
path after the WebUI server-browser list and detail owners were wired into the
client. Earlier rounds reconstructed the retained request-mode slots, owner
active flag, request handle, row projection, and detail callback owner. This
pass verifies that the current client is now native-first for list modes 0-4
and fixes the remaining case where a failed native list request could leave the
owner active without a live request handle.

Evidence order:

- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
- `references/analysis/quakelive_symbol_aliases.json`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `docs/reverse-engineering/quakelive_steam_mapping_round_297.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_302.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_303.md`
- `src/code/client/cl_main.c`
- `src/common/platform/platform_steamworks.c`

## Observed Facts

The owning binary is still `quakelive_steam.exe`. The Ghidra import table
contains `STEAM_API.DLL!SteamMatchmakingServers`, and the alias map promotes:

- `sub_462E60` -> `JSBrowser_OnRefreshComplete`
- `sub_462E80` -> `SteamBrowser_RefreshList`
- `sub_462EB0` -> `JSBrowser_RequestServers`
- `sub_463090` -> `SteamBrowser_RequestServers`

The retained `JSBrowser_RequestServers` owner checks the active flag at
`this + 4`, releases a previous inactive request handle from `this + 8` through
vtable slot `0x18`, builds the `gamedir=baseq3` filter, sets the active flag,
dispatches the native request by mode, stores the returned handle at
`this + 8`, and publishes `servers.refresh.start`.

The mode dispatch remains the round 302 contract:

| JS mode | Native slot | Native owner | Filter |
| --- | --- | --- | --- |
| `0` or invalid/default | `0x00` | `RequestInternetServerList` | `gamedir=baseq3` |
| `1` | `0x04` | `RequestLANServerList` | none |
| `2` | `0x08` | `RequestFriendsServerList` | `gamedir=baseq3` |
| `3` | `0x0c` | `RequestFavoritesServerList` | `gamedir=baseq3` |
| `4` | `0x10` | `RequestHistoryServerList` | `gamedir=baseq3` |

`SteamBrowser_RefreshList` calls `RefreshQuery` at vtable slot `0x24` only
when the stored request handle is non-zero. `JSBrowser_OnRefreshComplete`
clears only the active flag; it does not clear the request handle.

The current client code maps retained WebUI modes 0-4 to the native wrapper
modes above and calls `QL_Steamworks_BeginServerBrowserOwnerRequest` before it
falls back to the source LAN/global/favorites browser lanes.

## Source Reconstruction

`QL_Steamworks_BeginServerBrowserOwnerRequest` now treats a zero native request
handle as a failed begin. It still keeps the reconstructed release-before-
replace behavior for an old inactive request, but it stores the new handle in a
local `ql_steam_server_list_request_t` first. If the request is zero, the owner
is left idle and handleless and the function returns false.

That return value is significant at the client boundary:
`CL_SteamBrowser_BeginNativeRequest` already logs the native
`ISteamMatchmakingServers` begin failure and returns false, allowing
`CL_Steam_RequestServers` to start the existing source-browser fallback. Before
this round, a zero request handle could be reported as a successful native
begin, setting `nativeRefreshActive` and waiting until timeout with no live
Steam request to refresh or complete.

The Steamworks harness now exposes
`QLR_SteamworksMock_SetServerBrowserRequestResult`, so enabled-build tests can
force the native request slots to return zero. The lifecycle test pins that
mode `2` still reaches the mocked friends-list slot, but the owner remains
inactive with no request handle and cannot refresh.

## Compatibility Labels

The client compatibility labels now describe a fallback boundary instead of a
permanent missing owner for friends/history:

- Native adapter gap:
  `ISteamMatchmakingServers native request handle unavailable; using source-browser fallback`
- Friends fallback reason:
  `friends fallback mapped to global source`
- History fallback reason:
  `history fallback mapped to favorites source`

The low-level wrapper integration label now mirrors that boundary as
`native request handle unavailable; source-browser fallback retained`.

These labels do not change the online-services policy. Steamworks and related
Quake Live online services remain behind `QL_BUILD_ONLINE_SERVICES`, default
disabled.

## Open Questions

- The committed HLIL shows handle storage after request dispatch, but it does
  not show a retail branch for a zero request handle. The zero-handle handling
  in this round is a source-side robustness reconstruction needed by the
  current native-first client fallback contract.
- Retained mode `recent` semantics remain unresolved if a WebUI caller uses a
  value outside the observed 0-4 switch.
- Strong live parity for friends/history list contents still needs a runtime
  comparison against a Steam-enabled retail environment.

## Verification

Focused validation for this pass:

- `python -m pytest tests/test_steamworks_harness.py::test_server_browser_owner_reconstructs_retail_refresh_lifecycle tests/test_platform_services.py::test_steamworks_modern_adapter_gaps_stay_explicit_until_owned tests/test_platform_services.py::test_client_browser_server_shims_reconstruct_retail_server_browser_surface tests/test_netcode_parity_manifest.py::test_ql_server_browser_and_master_heartbeat_related_wiring_parity_recheck -q --tb=short`
  reported `5 passed`.
- `python -m pytest tests/test_steamworks_harness.py -q --tb=short`
  reported `80 passed`.
- `"C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe" src\code\quakelive.sln /t:quakelive_steam /p:Configuration=Debug /p:Platform=x86 /p:PlatformToolset=v141`
  completed with `0 Warning(s), 0 Error(s)`.
- `"C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe" src\code\quakelive.sln /t:quakelive_steam /p:Configuration=Debug /p:Platform=x86 /p:PlatformToolset=v141 /p:QLBuildOnlineServices=1 /p:QLBuildSteamworks=1 /p:QLRequireSteamworksSdk=0 /p:QLRequireAwesomiumSdk=0`
  completed with `2 Warning(s), 0 Error(s)`. Both warnings were existing
  BSCMAKE `BK4502` browse-info truncation warnings for
  `cl_awesomium_win32.sbr` and `platform_backend_steamworks.sbr`.
- `git diff --check` reported no whitespace errors; Git still printed the
  existing CRLF conversion warnings for touched and pre-existing dirty files.

No runtime game launch was needed; this pass covered Steamworks wrapper state,
client fallback wiring, source-bound parity guards, and harness behavior.

## Parity Estimate

Before this round, the focused native server-browser request-owner failure path
was about 88% complete: native list/detail owners were wired, but a zero native
list request handle could suppress the documented source fallback and leave the
client waiting for a handleless native refresh. After this round, the focused
path is about 98% complete.

Broader WebUI server-browser ownership remains about 99% complete in this
tree. The remaining uncertainty is semantic/live parity for less-traveled list
modes and provider environments, not absence of the native list/detail owners.
Repo-wide parity remains about 99%.
