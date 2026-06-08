# quakelive_steam.exe Mapping Round 440

Date: 2026-06-08

Scope: client Steam API shutdown ownership for the SteamDataSource avatar
callback and the retained client callback/ticket bundle.

## Summary

This round tightens the source-side Steam shutdown reconstruction. Retail's
public `SteamAPI_Shutdown` wrapper at `0x00460540` is only a tiny tailcall into
the imported Steam API, but the retail client also owns C++ callback objects
whose destructors unregister before that platform shutdown path is released.

The source tree cannot recreate those C++ object destructors exactly, so
`SteamAPI_Shutdown()` now explicitly drains the source `CL_ShutdownSteamResources()`
owner before `CL_Steam_ShutdownCallbacks()` and `QL_Steamworks_Shutdown()`.
That brings the avatar `SteamDataSource` callback owner into the same public
Steam quit thunk that already owns the client callback bundle and auth-ticket
cleanup.

## Evidence

Primary evidence:

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
- `src/code/client/cl_main.c`
- `src/code/client/cl_steam_resources.c`
- `src/common/platform/platform_steamworks.c`

Observed facts:

1. Ghidra keeps the owning binary as `quakelive_steam.exe`, and its import table
   includes `STEAM_API.DLL!SteamAPI_Shutdown`.
2. `functions.csv` records `SteamAPI_Shutdown,00460540,6,1,unknown`, matching
   the six-byte retail shutdown thunk.
3. Binary Ninja HLIL part 02 shows `0x00460540` as a direct
   `return SteamAPI_Shutdown() __tailcall`.
4. HLIL part 04 shows the common quit path calling that thunk after filesystem
   shutdown and before Steam GameServer shutdown.
5. HLIL part 02 maps `SteamDataSource_Shutdown` at `0x00464440`; it restores
   the embedded `CCallback<class SteamDataSource, struct AvatarImageLoaded_t, 0>`
   vtable and calls `SteamAPI_UnregisterCallback` when the callback is active.
6. The source platform layer already has the primitive parity owner:
   `QL_Steamworks_UnregisterAvatarCallbacks()` unregisters and clears the
   retained avatar callback object.
7. `CL_ShutdownSteamResources()` is the source owner for that avatar callback
   and resource bookkeeping, while `CL_Steam_ShutdownCallbacks()` owns workshop,
   microtransaction, lobby, client callback, and auth-ticket teardown.

## Source Reconstruction

`src/code/client/cl_main.c` now calls `CL_ShutdownSteamResources()` at the start
of `SteamAPI_Shutdown()`, before `CL_Steam_ShutdownCallbacks()` and
`QL_Steamworks_Shutdown()`.

This is intentionally a source-owned lifecycle reconstruction rather than a
claim that retail's six-byte thunk itself knew about SteamDataSource. Retail's
C++ destructors own those callback objects; the reconstructed C source makes
the same release boundary explicit so every client Steam callback owner is
drained before the platform Steam API is shut down.

## Verification

Commands run:

- `python -m pytest tests/test_platform_services.py::test_client_steam_api_shutdown_wrapper_reconstructs_retail_quit_thunk tests/test_platform_services.py::test_steam_resource_bridge_reconstructs_avatar_url_fetches -q --tb=short`
  -> `2 passed`
- `python -m pytest tests/test_platform_services.py tests/test_steamworks_harness.py -q --tb=short`
  -> `245 passed`
- `python -m pytest tests/test_application_initialization_mapping.py::test_policy_adjusted_common_client_server_wiring_matches_mapped_retail_chain -q --tb=short`
  -> `1 passed`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .vscode/build.ps1 -Configuration Debug -Platform x86 -Targets quakelive_steam`
  -> build succeeded with `0 Warning(s)` and `0 Error(s)`
- `C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.16.27023\bin\HostX86\x86\dumpbin.exe /dependents build\win32\Debug\bin\quakelive_steam.exe`
  -> only Windows system/debug CRT DLLs were listed; no dynamic libpng, vorbis,
  ogg, or Steam API DLL dependency was present
- `git diff --check`
  -> passed with only existing LF-to-CRLF working-copy warnings

## Parity Estimate

- Focused Steam client shutdown/resource callback ownership: **78% -> 95%**.
- Broader Steam launch/runtime integration source confidence: **91% -> 92%**.
- Strict retail Windows replacement target: **100% -> 100%**.
- Repo-wide checked-in tree parity: **99% -> 99%**.
