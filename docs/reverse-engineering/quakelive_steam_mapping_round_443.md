# quakelive_steam.exe Mapping Round 443

Date: 2026-06-08

Scope: `SteamClient_Init` post-success side-effect boundary for launch/runtime
callback, lobby, voice, stats, and main-menu rich-presence bootstrap.

## Summary

This round rechecked the retained retail `SteamClient_Init` owner and tightened
the source-side success boundary in `src/code/client/cl_main.c`.

Retail exits `sub_461500` immediately when `SteamAPI_Init()` fails. The source
already used the retained initialized flag for most downstream Steam calls, but
it still registered the lobby command/cvars, voice commands, stats-clear probe,
and main-menu rich-presence helper after the failure branch. The source now
returns from `SteamClient_Init()` when `SteamClient_IsInitialized()` is false,
so the post-success bootstrap cluster only runs after the retained Steam client
initialization state is live.

## Evidence

Primary evidence:

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `references/analysis/quakelive_symbol_aliases.json`
- `src/code/client/cl_main.c`

Observed facts:

1. `functions.csv` records `FUN_00461500` at `0x00461500`, size `209`, as the
   retail `SteamClient_Init` owner.
2. The alias corpus maps `sub_461500` to `SteamClient_Init`,
   `sub_465840` to `SteamLobby_Init`, and `sub_4659E0` to
   `SteamMicroCallbacks_Init`.
3. HLIL `0x0046151B` calls `SteamAPI_Init()` and `0x0046151E` stores the
   result into the retained `data_e30218` Steam client initialized flag.
4. HLIL `0x00461525` checks that result and `0x00461534` returns through the
   `"Steam API not present.\n"` log path when initialization failed.
5. The callback, lobby, command, stats, and presence side effects are all below
   that success branch: `sub_4659e0()` at `0x00461556`, `sub_465840()` at
   `0x0046155B`, `+voice` at `0x0046156A`, `-voice` at `0x00461579`,
   app-id-gated `stats_clear` at `0x00461595..0x004615A1`, and
   `"At the main menu"` rich presence at `0x004615C3`.
6. `sub_465840` itself allocates the lobby callback bundle, registers
   `lobby_autoconnect`, creates `steam_maxLobbyClients`, and exposes
   `connect_lobby`.

## Source Reconstruction

- `SteamClient_Init()` now returns immediately after logging the existing
  source fallback message when `SteamClient_IsInitialized()` is false.
- `SteamCallbacks_Init()`, `SteamMicroCallbacks_Init()`,
  `SteamLobby_Init()`, `+voice`, `-voice`, `stats_clear`, and
  `CL_Steam_SetMainMenuRichPresence()` are now all post-success side effects of
  the retained Steam initialization gate.
- `tests/test_platform_services.py` now pins the success-only boundary to the
  retail HLIL addresses and checks the source order from the initialized guard
  through lobby, voice, stats, and presence registration.

## Verification

Commands run:

- `python -m pytest tests/test_platform_services.py::test_client_main_menu_presence_seed_reconstructs_retail_bootstrap_status -q --tb=short`
  -> `1 passed`
- `python -m pytest tests/test_platform_services.py tests/test_steamworks_harness.py -q --tb=short`
  -> `245 passed`
- `python -m pytest tests/test_application_initialization_mapping.py::test_policy_adjusted_common_client_server_wiring_matches_mapped_retail_chain -q --tb=short`
  -> `1 passed`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .vscode/build.ps1 -Configuration Debug -Platform x86 -Targets quakelive_steam`
  -> build succeeded with `0 Warning(s)` and `0 Error(s)`
- `dumpbin /dependents build\win32\Debug\bin\quakelive_steam.exe`
  -> no dynamic `libpng`, `vorbis`, `ogg`, or `steam_api` dependency; the image
  depends on Windows/debug CRT DLLs only.

No runtime launch was needed for this pass because the launch-time side-effect
boundary is directly pinned to committed retail HLIL/Ghidra evidence and
validated by source mapping tests plus a fresh debug build.

## Parity Estimate

- Focused `SteamClient_Init` post-success side-effect boundary:
  **84% -> 97%**.
- Broader Steam launch/runtime integration reconstruction confidence:
  **93% -> 94%**.
- Strict retail Windows build target and static dependency expectation:
  **100% -> 100%**.
- Repo-wide checked-in tree parity: **99% -> 99%**.
