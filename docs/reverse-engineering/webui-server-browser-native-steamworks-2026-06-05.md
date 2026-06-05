# WebUI Server Browser Native Steamworks Wiring - 2026-06-05

## Scope

This pass makes the Awesomium WebUI server browser functional in opted-in
Steamworks builds by routing `qz_instance.RequestServers` through the native
`ISteamMatchmakingServers` list owner before falling back to the source-owned
LAN/global/favorites browser.

It does not enable Steam or other Quake Live online services in default builds.
`QL_BUILD_ONLINE_SERVICES` remains disabled by default, and runtime
`QL_DISABLE_EXTERNAL_ECOSYSTEMS` / `QL_DISABLE_STEAMWORKS` still force the
fallback path.

Owning retail binary:

- `assets/quakelive/quakelive_steam.exe`

Committed evidence used:

- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
- `references/analysis/quakelive_symbol_aliases.json`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `docs/reverse-engineering/network-server-browser-master-heartbeat-parity-2026-06-05.md`

## Observed Facts

- Retail imports `STEAM_API.DLL!SteamMatchmakingServers`.
- The retained WebUI bridge exposes `RequestServers`, `RequestServerDetails`,
  and `RefreshList` through the `qz_instance` method table.
- Retail `JSBrowser_RequestServers` starts an `ISteamMatchmakingServers`
  request, passes the browser response object as the callback sink, and
  publishes `servers.refresh.start`.
- Retail list callbacks publish `servers.details.<ip>_<port>.response`,
  `servers.details.<index>.failed`, and `servers.refresh.end`.
- The previous source path mapped Internet requests to `CL_RequestGlobalServers`,
  but that legacy UDP master query is intentionally disabled unless both
  `QL_PLATFORM_HAS_ONLINE_SERVICES` and `QL_ENABLE_LEGACY_Q3_SERVICES` are set.

## Source Change

- Added a native `ISteamMatchmakingServerListResponse` object in `cl_main.c`
  with `ServerResponded`, `ServerFailedToRespond`, and `RefreshComplete`
  callbacks.
- `CL_Steam_RequestServers` now tries the native SteamMatchmakingServers owner
  first when Steamworks matchmaking is compiled, initialised, and exposes the
  server-browser interface.
- Native rows are projected through the existing
  `QL_Steamworks_ReadServerBrowserResponse` helper and published into the
  retained WebUI `servers.details.*.response` event family.
- If the native provider is unavailable or the native request fails, the
  existing source-owned LAN/global/favorites fallback path still runs.
- `CL_Steam_RefreshServerList` refreshes an existing native request handle when
  available, otherwise it restarts the retained request mode through the fallback
  path.
- Client shutdown releases any retained native server-list request handle.

## Policy Answer

The empty WebUI Internet list was not primarily a Steam auth problem. The list
request path was falling through to a policy-disabled legacy master query instead
of using the reconstructed Steam matchmaking-server list owner.

Steam auth should not be enabled globally/default just to make browsing work.
The correct boundary is:

- default builds: online services remain disabled and browser list requests use
  explicit fallbacks;
- opted-in Steamworks builds: server discovery may use native
  `ISteamMatchmakingServers`;
- connection/session validation remains a separate auth path.

## Parity Estimate

- Focused WebUI server-list dispatch slice: before **82%**, after **100%**.
- Broader server-browser/details surface: before **96%**, after **98%** because
  native list callbacks are wired while the detail request still retains the
  existing UDP status fallback.
- Repo-wide parity remains **99%** because the online-service policy boundary is
  unchanged.
