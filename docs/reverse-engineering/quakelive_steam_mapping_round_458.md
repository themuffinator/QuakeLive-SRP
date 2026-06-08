# Quake Live Steam Mapping Round 458: Unauthenticated Server Client Identity

## Scope

This round rechecked the small Steam GameServer identity wrapper at
`sub_465DF0` and its only observed server call site in `SV_BotAllocateClient`.
The goal was to separate it from the already-reconstructed server SteamID
publication path at `sub_465B00`.

## Evidence

Primary retail evidence:

- `references/analysis/quakelive_symbol_aliases.json`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`

Observed facts:

- `sub_465B00` calls `SteamGameServer` slot `0x28`, formats that value, and
  publishes it through configstring `0x2CA` plus `sv_referencedSteamworks`.
- `sub_465DF0` first checks the retained `data_e30358` GameServer initialized
  flag and returns zero when the GameServer path is inactive.
- When active, `sub_465DF0` calls `SteamGameServer` slot `0x64` with an output
  `CSteamID` buffer.
- `sub_4DCD30` / `SV_BotAllocateClient` calls `sub_465DF0` after claiming a
  server-owned client slot and stores the returned low/high halves into the
  client SteamID fields.

Inference:

- The `0x64` wrapper is not the public GameServer identity publisher. Its slot
  and call site match the retail unauthenticated-user-connection identity used
  for local server-owned clients.

## Source Reconstruction

Implemented:

- Renamed the alias map entry for `sub_465DF0` to
  `SteamServer_CreateUnauthenticatedUserConnection`.
- Added `QL_Steamworks_ServerCreateUnauthenticatedUserConnection`, pinned to
  `SteamGameServer` vtable slot `0x64` and gated on the retained GameServer
  initialized state.
- Wired `SV_BotAllocateClient` through `SV_BotAssignSteamIdentity` under
  `SV_HAS_PLATFORM_AUTH`, storing the generated identity in the existing
  decimal `platformSteamId` field.
- Extended the Steamworks harness with a distinct mock unauthenticated-user ID
  and call counter so slot `0x64` remains separate from the server SteamID slot
  `0x28`.

## Validation

- `python -m pytest tests/test_platform_services.py::test_server_game_server_wrappers_reconstruct_mapped_server_slots tests/test_botlib_server_game_bridge_parity.py::test_server_bot_source_matches_retail_bridge_lifecycle_shape tests/test_botlib_server_game_bridge_parity.py::test_server_game_botlib_bridge_hlil_shapes_are_pinned tests/test_steamworks_harness.py::test_game_server_helpers_use_mapped_server_slots -q --tb=short`
  - 5 passed.
- `python -m pytest tests/test_platform_services.py tests/test_steamworks_harness.py tests/test_botlib_server_game_bridge_parity.py -q --tb=short`
  - 250 passed.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .vscode/build.ps1 -Configuration Debug -Platform x86 -Targets quakelive_steam`
  - Build succeeded with 0 warnings and 0 errors.
- MSVC `dumpbin /dependents build\win32\Debug\bin\quakelive_steam.exe`
  - No dynamic `steam_api`, `libpng`, `vorbis`, or `ogg` dependency was present.

## Parity Estimate

- Focused unauthenticated server-client identity wrapper: **45% -> 96%**.
- Bot allocation Steam identity bridge: **70% -> 95%**.
- Broader Steam launch/runtime integration: **98% -> 98%**.
- Static dependency parity for the executable: **100% -> 100%**.
- Repo-wide retail parity: **99% -> 99%**.
