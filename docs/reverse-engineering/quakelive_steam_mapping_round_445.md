# quakelive_steam.exe Mapping Round 445

Date: 2026-06-08

Scope: `SteamClient_Init` terminal success diagnostic after the retail
launch/runtime bootstrap cluster.

## Summary

This round rechecked the tail of retail `sub_461500` and reconstructed the
client-owner `"Steam API initialized.\n"` success marker in
`src/code/client/cl_main.c`.

The platform wrapper already logs its own lower-level
`"Steamworks: SteamAPI_Init succeeded"` message when the source dynamic
Steamworks shim initializes. Retail also emits a separate client bootstrap
marker after callback allocation, micro and lobby bootstrap, voice command
registration, `stats_clear` registration, and the initial main-menu
rich-presence write. The source now mirrors that final client-owner marker
without adding the retail failure text to default policy-disabled launches.

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
2. The alias corpus maps `sub_461500` to `SteamClient_Init`.
3. HLIL `0x0046151B` calls `SteamAPI_Init()` and `0x00461525` returns through
   `"Steam API not present.\n"` when that call fails.
4. The success path continues through micro callback bootstrap at
   `0x00461556`, lobby bootstrap at `0x0046155B`, `+voice` and `-voice`
   registration at `0x0046156A` and `0x00461579`, app-id gated
   `stats_clear` at `0x00461595..0x004615A1`, and initial main-menu rich
   presence at `0x004615C3`.
5. HLIL `0x004615CA` logs `"Steam API initialized.\n"` after the
   `"At the main menu"` rich-presence write.

## Source Reconstruction

- `SteamClient_Init()` now calls `Com_Printf( "Steam API initialized.\n" );`
  after `CL_Steam_SetMainMenuRichPresence()`.
- The failure path remains the existing source diagnostic rather than printing
  the exact retail `"Steam API not present.\n"` line, because default source
  builds keep online services disabled by policy and should not report a live
  Steam API failure when no live Steam API was intended.
- `tests/test_platform_services.py` now pins the terminal marker to HLIL
  `0x004615CA` and checks that the source print follows
  `CL_Steam_SetMainMenuRichPresence()`.

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

No runtime launch was needed for this pass because the diagnostic owner and
ordering are pinned to committed retail HLIL/Ghidra evidence and validated by
source mapping tests plus a fresh debug build.

## Parity Estimate

- Focused `SteamClient_Init` terminal success diagnostic:
  **90% -> 99%**.
- Broader Steam launch/runtime integration reconstruction confidence:
  **94% -> 95%**.
- Strict retail Windows build target and static dependency expectation:
  **100% -> 100%**.
- Repo-wide checked-in tree parity: **99% -> 99%**.
