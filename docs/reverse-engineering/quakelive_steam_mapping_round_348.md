# Quake Live Steam Host Mapping Round 348

## Scope

This round tightens the `SetFavoriteServer` lane that sits beside the retained
Steam server-browser and Awesomium `qz_instance` wiring. The platform wrapper
already mapped the retail `SteamMatchmaking` add/remove favorite-game slots;
this pass pins that mapping with executable harness coverage and makes the
client-side local favorites mirror an explicit open-build compatibility
fallback when the opted-in Steam provider cannot update favorites.

Evidence order:

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part07.txt`
- `docs/reverse-engineering/quakelive_steam_mapping_round_09.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_331.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_347.md`
- `src/common/platform/platform_steamworks.c`
- `src/code/client/cl_cgame.c`
- `tests/steamworks_harness.c`
- `tests/test_steamworks_harness.py`
- `tests/test_platform_services.py`

## Observed Facts

The owning retail binary is still `quakelive_steam.exe`. The Ghidra metadata
records an x86 Windows program with `5473` functions, `351` imports, and `4377`
analysis symbols. The import table includes `STEAM_API.DLL!SteamMatchmaking`
and `STEAM_API.DLL!SteamUtils`, which are the two Steam interfaces used by this
favorite-server lane.

The `qz_instance` method table keeps `SetFavoriteServer` as a non-returning
method row:

| Table address | Method id | Returns value | Name |
| --- | --- | --- | --- |
| `0x0055C188` | `0x21` | `0` | `SetFavoriteServer` |

The non-returning dispatcher reaches the inline case at `0x00432681`. The
strongest HLIL signals are:

- the case requires at least three JS arguments;
- argument `2 == 1` selects the add branch;
- the add branch calls `_time64`, reads `SteamUtils()->GetAppID()` through
  vtable slot `0x24`, then calls `SteamMatchmaking` vtable slot `0x08`;
- the remove branch reads the same app ID and calls the paired
  `SteamMatchmaking` vtable slot `0x0c`;
- both branches read argument `0` as the server IP and argument `1` as the
  port-like value; the source wrapper currently uses that value for both the
  connection and query port parameters.

That keeps the round 09 conclusion intact: `SetFavoriteServer` is the
add/remove favorite-game surface, not a separate WebUI source-list owner.

## Source Reconstruction

`QL_Steamworks_SetFavoriteServer` remains the retail-owned platform wrapper:

- it obtains the current app ID via `QL_Steamworks_GetAppID()`;
- add maps to `ISteamMatchmaking` vtable offset `0x08`;
- remove maps to `ISteamMatchmaking` vtable offset `0x0c`;
- both pass `QL_STEAM_FAVORITE_FLAG_FAVORITE`;
- add sends a non-negative `time( NULL )` timestamp;
- remove does not send a timestamp.

The Steamworks harness now mocks and observes those exact slots. The new
coverage proves enabled builds forward app ID, IP, connection port, query port,
favorite flag, and add timestamp, and that disabled builds return `qfalse`
without requiring live online services.

The client `CL_WebHost_SetFavoriteServer` fallback is now explicit. When
`CL_SteamServicesEnabled()` is true but the opted-in Steam provider fails the
favorite add/remove call, the client logs the provider failure and still updates
the inherited local favorites cache through `CL_WebHost_MirrorFavoriteServer`.
This is intentionally a compatibility fallback for the open reconstruction
build, not a claim that the retail inline branch mirrored the source cache.

## Coverage

`tests/test_steamworks_harness.py` now has a focused
`test_favorite_server_helper_uses_mapped_matchmaking_slots` case. It checks:

- disabled builds expose the helper and return false;
- add calls `SteamMatchmaking` slot `0x08`;
- remove calls `SteamMatchmaking` slot `0x0c`;
- app ID comes from the mocked `SteamUtils()->GetAppID()` path;
- server IP and the shared connection/query port are forwarded unchanged;
- the favorite flag is `1`;
- add records a timestamp and remove clears the timestamp field;
- add/remove provider failures propagate as false from the wrapper.

`tests/test_platform_services.py` now also protects the source/client wiring:
the client still calls `QL_Steamworks_SetFavoriteServer` when Steam services are
enabled, but a provider failure no longer suppresses the local cache mirror.

## Open Questions

- The exact retail SDK type names for the `SteamMatchmaking` slots are inferred
  from vtable offsets, call shape, SDK convention, and round 09 evidence. The
  slot mapping is high confidence, but the original inline retail code does not
  name a standalone helper function.
- Live Steam favorite-list persistence still needs runtime comparison against
  retail if the repo ever promotes online services beyond the current
  opt-in/replacement boundary.
- The local favorites mirror is a source compatibility fallback, not strict
  retail behavior. It stays behind the existing `CL_SteamServicesEnabled()`
  policy and does not make online services default-on.

## Verification

Focused and build validation for this pass:

- `python -m pytest tests/test_steamworks_harness.py::test_favorite_server_helper_uses_mapped_matchmaking_slots tests/test_platform_services.py::test_client_browser_favorite_server_lane_reconstructs_retail_steam_matchmaking_owner -q --tb=short`
  reported `3 passed`.
- `python -m pytest tests/test_steamworks_harness.py -q --tb=short` reported
  `82 passed`.
- `"C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe" src\code\quakelive.sln /t:quakelive_steam /p:Configuration=Debug /p:Platform=x86 /p:PlatformToolset=v141`
  completed with `0 Warning(s), 0 Error(s)`.
- `"C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe" src\code\quakelive.sln /t:quakelive_steam /p:Configuration=Debug /p:Platform=x86 /p:PlatformToolset=v141 /p:QLBuildOnlineServices=1 /p:QLBuildSteamworks=1 /p:QLRequireSteamworksSdk=0 /p:QLRequireAwesomiumSdk=0`
  completed with `2 Warning(s), 0 Error(s)`. Both warnings were `BSCMAKE`
  `BK4502` browse-info truncation warnings for
  `platform_backend_steamworks.sbr` and `platform_steamworks.sbr`.

## Parity Estimate

Focused `SetFavoriteServer` wrapper/fallback parity moved from **88%** to
**98%**. The remaining two percent is live Steam favorite persistence and exact
SDK-symbol naming uncertainty rather than source-side call-shape or policy
coverage. Broader Steam server-browser and WebUI bridge parity remains
approximately **99%** because live friends/history/recent-mode evidence remains
the active uncertainty outside this favorite-server lane.
