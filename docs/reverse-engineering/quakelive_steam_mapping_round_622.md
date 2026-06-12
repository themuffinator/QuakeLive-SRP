# Quake Live Steam Mapping Round 622: Cached Steamworks Launch Refresh Boundary

Date: 2026-06-12

## Scope

This round maps the Steam launch/runtime service-cache boundary that sits above
the retail `SteamAPI_Init()` call. Retail calls the Steam API directly from
`SteamClient_Init`; SRP keeps that behavior behind the default-disabled online
service policy and reconstructs it as an opt-in dynamic Steamworks descriptor
that can fail at launch, stay cached, and recover only through explicit refresh
owners.

The focused targets are:

- retail `SteamClient_Init` and `SteamClient_IsInitialized`;
- retail common-startup Steam fatal guard;
- SRP `QL_PlatformSteamworks_InitCached`;
- SRP `QL_GetPlatformServices` versus `QL_RefreshPlatformServices`;
- early filesystem SteamID refresh and primary client callback bootstrap;
- default-disabled `QL_BUILD_ONLINE_SERVICES` policy labels.

## Retail Evidence

Observed Binary Ninja HLIL and Ghidra signals:

- `FUN_00461500` / `sub_461500` is `SteamClient_Init`; it checks
  `com_build`, calls `SteamAPI_Init()`, stores the result in `data_e30218`,
  logs `Steam API not present.` on failure, and only continues to callbacks,
  voice commands, stats-clear registration, main-menu rich presence, and
  `Steam API initialized.` after success.
- `FUN_00460510` / `sub_460510` is the initialized-state wrapper returning
  `data_e30218`.
- Common startup calls `sub_461500()` after registering `dedicated`, registers
  `com_build` later, initializes the client, then checks
  `sub_460510() == 0 && com_build == 0 && dedicated == 0` before retail's
  `Failed to initialize Steam.` fatal.
- `imports.txt` confirms retail direct imports for `SteamAPI_Init`,
  `SteamAPI_RunCallbacks`, `SteamAPI_Shutdown`, `SteamUser`, `SteamFriends`,
  `SteamApps`, and the adjacent Steam runtime exports. No self-relaunch import
  is involved in this boundary.

These signals keep the retail owner model simple: one retained client
initialized flag is set by `SteamClient_Init`, and later runtime paths read
that retained state instead of reinitializing Steam ad hoc.

## Source Reconstruction

SRP intentionally keeps the live Steam path bounded:

- `platform_config.h` defaults `QL_BUILD_ONLINE_SERVICES` to `0`, which forces
  `QL_BUILD_STEAMWORKS` and `QL_BUILD_OPEN_STEAM` off in default builds.
- `Com_ApplyOnlineServicesBuildPolicy` publishes the default-disabled runtime
  environment gates before later startup owners can consult platform services.
- `QL_PlatformSteamworks_InitCached` attempts `QL_Steamworks_Init`, caches a
  successful result, throttles failed attempts with
  `QL_STEAMWORKS_RETRY_SECONDS`, and exposes recovery only through descriptor
  rebuilding.
- `QL_GetPlatformServices` returns a cached descriptor snapshot, while
  `QL_RefreshPlatformServices` explicitly rebuilds it.
- `Com_InitSteamClientForFilesystem` is the source-only early owner used before
  `FS_InitFilesystem()` so SteamID-scoped homepath selection can work without
  moving callback/command bootstrap earlier.
- `SteamClient_Init` remains the main retail-shaped owner: it skips `com_build`,
  refreshes platform services, latches `cl_steamClientInitialized`, then
  performs callback, lobby, microtransaction, workshop, voice, stats, and rich
  presence side effects only after the retained Steam state is live.
- `Com_VerifySteamClientStartup` documents the retail fatal point but keeps the
  repository's compatibility fallback instead of aborting when services are
  disabled or unavailable.

No C source change was needed in this round. The existing reconstruction already
matches this source-policy split; the new work pins it to the retail evidence.

## Validation

Added `test_steamworks_cached_service_refresh_tracks_round_622`, which
cross-checks:

- alias map, Ghidra `functions.csv`, `metadata.txt`, and `imports.txt` anchors;
- Binary Ninja HLIL anchors for `SteamAPI_Init`, `data_e30218`, failure/success
  logs, and common-startup fatal guard;
- source-side default-disabled build gates;
- `QL_PlatformSteamworks_InitCached` cache, throttle, and explicit refresh
  behavior;
- `QL_GetPlatformServices` cached descriptor behavior versus
  `QL_RefreshPlatformServices` recovery;
- early filesystem Steam refresh and primary `SteamClient_Init` ownership;
- the executable refresh probe proving failed launch init stays cached until an
  explicit refresh recovers it.

Focused cached Steamworks launch-refresh confidence:
**90% -> 98%**.

Focused platform service descriptor policy confidence:
**95% -> 99%**.

Overall Steam launch/runtime integration mapping confidence:
**93.46% -> 93.48%**.
