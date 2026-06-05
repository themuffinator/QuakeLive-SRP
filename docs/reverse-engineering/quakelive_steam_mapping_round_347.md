# Quake Live Steam Host Mapping Round 347

## Scope

This round closes a narrow client-side mismatch in the retained Steam
server-browser request-mode labels. The platform wrapper already followed the
retail `JSBrowser_RequestServers` contract for invalid/default modes, but the
client telemetry helper still labeled an out-of-range retained mode as
`unknown` even though both native and source fallback dispatch route that mode
through the internet list path.

Evidence order:

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/analysis/quakelive_symbol_aliases.json`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `docs/reverse-engineering/quakelive_steam_mapping_round_302.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_345.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_346.md`
- `src/code/client/cl_main.c`
- `tests/test_platform_services.py`

## Observed Facts

The owning binary remains `quakelive_steam.exe`. The Ghidra import table keeps
`STEAM_API.DLL!SteamMatchmakingServers` in the retail host, and the alias map
promotes the browser owner around `JSBrowser_RequestServers`.

The committed HLIL for `sub_462eb0` builds one filter pair before dispatch:

| Filter key | Filter value |
| --- | --- |
| `gamedir` | `baseq3` |

The request-mode branch is explicit:

| Retained mode | Retail dispatch |
| --- | --- |
| `0`, default, or out-of-range | `ISteamMatchmakingServers` vtable slot `0x00`, internet list, with `gamedir=baseq3` |
| `1` | vtable slot `0x04`, LAN list, without the `gamedir=baseq3` filter |
| `2` | vtable slot `0x08`, friends list, with `gamedir=baseq3` |
| `3` | vtable slot `0x0c`, favorites list, with `gamedir=baseq3` |
| `4` | vtable slot `0x10`, history list, with `gamedir=baseq3` |

The key HLIL signal is `if (arg2 - 1 u> 3)`, which sends mode `0` and any
out-of-range retained value into the internet request slot. Round 302 already
reconstructed this at the platform wrapper level by labeling invalid/default
modes as `internet` and keeping the internet filter behavior.

Before this pass, `src/code/client/cl_main.c` agreed on behavior but not on the
diagnostic label:

- `CL_SteamBrowser_RequestModeToSource` sent invalid/default modes to
  `AS_GLOBAL`, the source-browser internet/global fallback.
- `CL_SteamBrowser_RequestModeToNativeMode` sent invalid/default modes to
  `QL_STEAM_SERVER_BROWSER_INTERNET`.
- `CL_SteamBrowser_RequestModeLabel` still returned `unknown` for the same
  default path.

## Source Reconstruction

`CL_SteamBrowser_RequestModeLabel` now treats the retained default case as
`internet`. This aligns the client-facing label with both dispatch helpers and
with the retail HLIL branch that routes default/out-of-range values through the
internet request slot.

This is intentionally a label-only reconstruction. It does not change the
native-first request path, the source-browser fallback path, the
friends/history fallback reasons, or the default disabled-online-services
policy. It only prevents fallback logs and browser telemetry from presenting a
retail internet-default request as an unknown mode.

## Coverage

`tests/test_platform_services.py` now pins the client helper contract:

- the label helper has two `internet` returns, one for explicit mode `0` and
  one for the retained default case;
- the helper no longer contains an `unknown` label for request modes;
- the native and source request-mode helpers remain pinned to the same
  internet default dispatch behavior.

## Open Questions

- Live Steam-enabled result parity for friends/history list contents still
  needs comparison against retail.
- If a WebUI layer exposes a separate `recent` mode distinct from the observed
  `RequestServers` 0-4 switch, that path still needs its own evidence. This
  pass only closes the invalid/default behavior for the observed retail
  `JSBrowser_RequestServers` dispatcher.

## Verification

Focused validation for this pass:

- `python -m pytest tests/test_platform_services.py::test_client_browser_server_shims_reconstruct_retail_server_browser_surface tests/test_netcode_parity_manifest.py::test_ql_server_browser_and_master_heartbeat_related_wiring_parity_recheck -q --tb=short`
  reported `2 passed`.
- `python -m pytest tests/test_platform_services.py::test_steamworks_modern_adapter_gaps_stay_explicit_until_owned -q --tb=short`
  reported `1 passed`.
- `"C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe" src\code\quakelive.sln /t:quakelive_steam /p:Configuration=Debug /p:Platform=x86 /p:PlatformToolset=v141`
  completed with `0 Warning(s), 0 Error(s)`.
- `"C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe" src\code\quakelive.sln /t:quakelive_steam /p:Configuration=Debug /p:Platform=x86 /p:PlatformToolset=v141 /p:QLBuildOnlineServices=1 /p:QLBuildSteamworks=1 /p:QLRequireSteamworksSdk=0 /p:QLRequireAwesomiumSdk=0`
  completed with `3 Warning(s), 0 Error(s)`. All three were `BSCMAKE`
  `BK4502` browse-info truncation warnings for `cl_awesomium_win32.sbr`,
  `platform_backend_steamworks.sbr`, and `platform_steamworks.sbr`.
- `git diff --check` reported no whitespace errors; Git still printed the
  existing CRLF conversion warnings for dirty working-tree files.

No runtime game launch was needed; this pass covered source-bound browser-mode
labeling and static parity guards only.

## Parity Estimate

Before this round, the focused invalid/default browser request-mode labeling
path was about 85% complete: dispatch already matched the retail internet
default, but the retained client label could still describe that path as
unknown. After this round, the focused labeling path is about 99% complete.

Broader WebUI server-browser ownership remains about 99% complete in this
tree. The remaining uncertainty is live result parity for less-traveled list
modes and any distinct WebUI recent-mode path, not absence of native
list/detail owners. Repo-wide parity remains about 99%.
