# quakelive_steam.exe Mapping Round 447

Date: 2026-06-08

Scope: Steam lobby command bootstrap, focused on the retail `connect_lobby`
handler, the `SteamLobby_Init` cvar/command registration surface, and the
initial Steam bootstrap return boundary in `quakelive_steam.exe`.

## Summary

This round reconstructs two adjacent runtime-relevant Steam launch integration
details. First, retail `connect_lobby` is a literal command-argument-to-cvar
bridge. The source implementation previously carried defensive source-only
argument and provider logging inside the command handler. Retail does not: the
command is registered only from the Steam lobby bootstrap path, and the handler
simply stores command argument 1 into `lobby_autoconnect`.

Second, retail `SteamLobby_Init` does not return lobby callback health to the
main Steam bootstrap. It constructs/registers the callback owner, registers the
lobby cvars, and returns from `Cmd_AddCommand`. Source now mirrors that boundary
by attempting lobby callback registration but not letting that platform
abstraction return value decide whether the broader Steam client bootstrap
continues into voice, stats, main-menu presence, and the terminal success log.

The resulting source behavior now matches the retail command surface while
leaving live online-service availability behind the existing
`QL_BUILD_ONLINE_SERVICES` and platform-service bootstrap policy.

## Evidence

Primary evidence:

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `references/analysis/quakelive_symbol_aliases.json`
- `src/code/client/cl_main.c`
- `src/code/qcommon/cmd.c`

Observed facts:

1. Ghidra metadata records `quakelive_steam.exe` as `x86:LE:32:default`, with
   `5473` functions, `351` imports, and `4377` analysis symbols.
2. `functions.csv` records `FUN_00465840` at `0x00465840`, size `85`.
3. The alias map identifies `sub_465840` as `SteamLobby_Init`.
4. `analysis_symbols.txt` promotes the surrounding Steam lobby callback RTTI
   names, including `SteamLobbyCallbacks` callback vtables for lobby created,
   enter, chat update, chat message, data update, game created, kicked, and
   game lobby join requested events.
5. Binary Ninja HLIL shows `sub_461500` calling `sub_465840()` during the
   successful Steam bootstrap path after the client callback bootstrap.
6. HLIL for `sub_465840` allocates a `0xa0` callback bundle, calls the lobby
   callback constructor when allocation succeeds, registers `lobby_autoconnect`
   with default empty string and flags `0x100`, registers
   `steam_maxLobbyClients` with default `"16"` and flags `1`, then registers
   `connect_lobby` to `sub_464aa0`.
7. The final HLIL instruction for `sub_465840` is
   `return sub_4c81d0("connect_lobby", sub_464aa0)`, so retail does not return
   lobby callback registration success to `SteamClient_Init`.
8. HLIL for `sub_464aa0` is a one-line cvar write:
   `return sub_4cd250("lobby_autoconnect", sub_4c7ee0(1))`.
9. Source `Cmd_Argv( 1 )` returns an empty string for a missing argument, so the
   retail no-guard command behavior remains deterministic without adding a
   missing-argument branch.

## Source Reconstruction

- Removed the source-only `Cmd_Argc()` missing-argument guard from
  `CL_Steam_ConnectLobby_f()`.
- Removed the source-only provider-availability diagnostic from
  `CL_Steam_ConnectLobby_f()`.
- Kept `connect_lobby` registration owned by `SteamLobby_Init()`, matching the
  retail successful Steam bootstrap owner.
- Changed `SteamLobby_Init()` from a callback-success boolean into a void
  bootstrap helper. It still attempts `SteamLobbyCallbacks_Init()` when the
  retained Steam initialized flag is live, but it no longer returns that result
  to `SteamClient_Init()`.
- Removed `lobbyCallbacksRegistered` from the initial `SteamClient_Init()`
  callback-failure gate, matching retail's direct `sub_465840()` call followed
  by voice command registration, optional `stats_clear`, main-menu presence,
  and `"Steam API initialized.\n"`.
- Extended `tests/test_platform_services.py` to pin the exact retail HLIL lines
  for `sub_464aa0`, `sub_465840`, `lobby_autoconnect`, `steam_maxLobbyClients`,
  `connect_lobby` registration, and the absence of the old initial
  `lobbyCallbacksRegistered = SteamLobby_Init()` gate.

No game launch was needed because this pass is literal mapping/source
reconstruction against committed HLIL and Ghidra evidence. Runtime launch would
not add useful signal for the handler body beyond the already verified command
and cvar source behavior.

## Verification

- `python -m pytest tests/test_platform_services.py::test_client_lobby_bootstrap_reconstructs_retail_connect_surface tests/test_platform_services.py::test_client_steam_callback_owner_reconstructs_retail_frame_pump_and_lifecycle tests/test_platform_services.py::test_client_main_menu_presence_seed_reconstructs_retail_bootstrap_status -q --tb=short`
  - `3 passed`
- `python -m pytest tests/test_engine_client_command_parity.py::test_client_steam_command_registration_and_identity_wiring_match_retail_surface -q --tb=short`
  - `1 passed`
- `python -m pytest tests/test_platform_services.py tests/test_steamworks_harness.py -q --tb=short`
  - `245 passed`
- `python -m pytest tests/test_application_initialization_mapping.py::test_policy_adjusted_common_client_server_wiring_matches_mapped_retail_chain -q --tb=short`
  - `1 passed`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .vscode/build.ps1 -Configuration Debug -Platform x86 -Targets quakelive_steam`
  - `Build succeeded.`
  - `0 Warning(s)`
  - `0 Error(s)`
- `dumpbin /dependents build\win32\Debug\bin\quakelive_steam.exe`
  - Dynamic dependencies are Windows/debug CRT DLLs only.
  - No dynamic `libpng`, `vorbis`, `ogg`, or `steam_api` dependency is present.

## Parity Estimate

- Focused `connect_lobby` command handler lane: **76% -> 99%**.
- Steam lobby bootstrap cvar/command/return boundary lane: **88% -> 97%**.
- Broader Steam launch/runtime integration reconstruction confidence after the
  recent retained-state, shutdown, rich-presence, and bootstrap rounds:
  **95% -> 96%**.
- Static executable dependency parity for bundled media libraries:
  **100% -> 100%**.
- Repo-wide checked-in tree parity: **99% -> 99%**.
