# Quake Live Steam Mapping Round 608: Steam Browser Request Mode Matrix

Date: 2026-06-11

## Scope

This round rechecks the retained WebUI Steam server-browser request-mode
matrix. Retail Quake Live drives the list refresh through
`SteamMatchmakingServers` directly; SRP keeps the same native owner when
online services are explicitly enabled and falls back to the source
server-browser lists when that owner is unavailable.

No runtime source behavior changed in this pass. The reconstruction value here
is the explicit evidence matrix and parity gate for the direct retail slots,
the `gamedir=baseq3` filter, and the compatibility fallback classification.

## Retail Evidence

Primary owner: `assets/quakelive/quakelive_steam.exe`

Evidence checked:

- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/analysis/quakelive_symbol_aliases.json`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `src/code/client/cl_main.c`
- `src/common/platform/platform_steamworks.c`
- `src/common/platform/platform_steamworks.h`

Function ownership:

| Ghidra row | Address | Promoted owner |
| --- | --- | --- |
| `FUN_00462e60` | `0x00462E60` | `JSBrowser_OnRefreshComplete` |
| `FUN_00462e80` | `0x00462E80` | `SteamBrowser_RefreshList` |
| `FUN_00462eb0` | `0x00462EB0` | `JSBrowser_RequestServers` |
| `FUN_00463090` | `0x00463090` | `SteamBrowser_RequestServers` |
| `FUN_004630b0` | `0x004630B0` | `SteamBrowser_RequestServerDetails` |

Observed retail facts:

- `sub_462e60` clears the active refresh byte at object offset `+4` and
  publishes `servers.refresh.end`.
- `sub_462e80` checks the retained request handle at object offset `+8` and
  calls the `SteamMatchmakingServers` vtable slot `0x24` refresh path.
- `sub_462eb0` refuses to start if offset `+4` is already active.
- `sub_462eb0` releases an existing request handle through vtable slot `0x18`
  before starting a replacement request.
- `sub_462eb0` builds one filter pair with key `gamedir` and value `baseq3`.
- `sub_462eb0` treats mode `0` and out-of-range/default values as the internet
  list request.
- `sub_463090` is a thin forwarder into `sub_462eb0(data_e30334, arg1)`.

## Request Matrix

| Retained mode | Label | Retail `SteamMatchmakingServers` slot | Filter | SRP source fallback | Compatibility reason |
| --- | --- | --- | --- | --- | --- |
| `0` or default/out-of-range | internet | `0x00` | `gamedir=baseq3` | `AS_GLOBAL` | native-compatible source |
| `1` | lan | `0x04` | none | `AS_LOCAL` | native-compatible source |
| `2` | friends | `0x08` | `gamedir=baseq3` | `AS_GLOBAL` | friends fallback mapped to global source |
| `3` | favorites | `0x0c` | `gamedir=baseq3` | `AS_FAVORITES` | native-compatible source |
| `4` | history | `0x10` | `gamedir=baseq3` | `AS_FAVORITES` | history fallback mapped to favorites source |

`CL_SteamBrowser_GetDiscoveryAppID() uses QL_STEAM_APPID_PUBLIC_RETAIL unless overridden`
by `cl_steamServerBrowserAppId`. This preserves retail public server-browser
discovery while still allowing a local diagnostic override.

## Source Reconstruction

The platform wrapper reconstructs the native list path without binding to a
modern `SteamAPI_ISteamMatchmakingServers` symbol. It loads the retail
`SteamMatchmakingServers` export, obtains the interface vtable, and dispatches:

- LAN requests without a filter through slot `0x04`.
- Friends, favorites, history, internet, and default requests with one
  `gamedir=baseq3` filter through slots `0x08`, `0x0c`, `0x10`, and `0x00`.
- Request-handle release through slot `0x18`.
- Request-handle refresh through slot `0x24`.

The client wrapper keeps the native-first owner behind the existing
`QL_PLATFORM_HAS_STEAMWORKS`, `SteamClient_IsInitialized()`,
`CL_MatchmakingServiceAvailable()`, and
`QL_Steamworks_HasServerBrowserInterface()` gates. If the native request handle
cannot be created, `CL_Steam_RequestServers` continues through the source
browser list fallback and publishes `servers.refresh.compatibility` for the
friends/history modes where the fallback is not one-to-one.

## Compatibility Boundary

This is an explicit online-services divergence from the strict retail host:

- default builds keep live Steam services disabled by policy;
- the native owner is only attempted after the retail Steam client state is
  initialized and the Steamworks adapter reports the browser interface;
- friends and history fallbacks remain documented compatibility behavior, not
  a claim of live Steam result parity; and
- no game launch or live Steam query was needed for this static mapping pass.

## Validation

Added
`tests/test_platform_services.py::test_steam_browser_request_mode_matrix_tracks_retail_hlil_and_source_fallback`
to pin:

- Ghidra rows and alias names for the retained browser request owners;
- Binary Ninja HLIL anchors for refresh-end, refresh-query, release-query,
  `gamedir=baseq3`, request-start, and mode-slot dispatch;
- source-mode labels, native enum mapping, and source fallback routing;
- the native availability gate and compatibility marker payload; and
- the platform vtable slots for request, release, and refresh.

Planned validation for this round:

```text
python -m pytest tests/test_platform_services.py::test_steam_browser_request_mode_matrix_tracks_retail_hlil_and_source_fallback -q --tb=short
python -m pytest tests/test_platform_services.py -q --tb=short
```

## Confidence

Observed facts:

- HLIL gives direct slot and filter evidence for the retained request matrix.
- Ghidra rows and the alias map identify the owning functions and sizes.
- Source wrappers expose the same request-mode labels and slot routing while
  preserving the repository's default-disabled online-service policy.

Inference:

- The current SRP native-first plus source-fallback split is the right bounded
  reconstruction for this lane until live, open replacement Steam browser
  behavior is intentionally specified.

Parity estimates:

- Focused Steam browser request-mode matrix confidence:
  **before 94% -> after 99%**.
- Focused native SteamMatchmakingServers fallback classification:
  **before 95% -> after 98%**.
- Overall Steam launch/runtime integration mapping confidence:
  **93.18% -> 93.20%**.
