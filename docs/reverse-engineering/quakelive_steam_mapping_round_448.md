# quakelive_steam.exe Mapping Round 448

Date: 2026-06-08

Scope: Steam lobby chat-message callback publication, focused on retail
`SteamLobbyCallbacks_OnLobbyChatMessage` and its `lobby.%s.chat` browser-event
gate.

## Summary

This round reconstructs the retail lobby chat-message entry-type filter. Retail
reads the Steam lobby chat entry and publishes `lobby.%s.chat` only when the
returned entry type is `1`. The source callback previously published every
lobby chat-message callback payload, including non-chat entry types.

The source now gates `CL_Steam_Lobby_OnLobbyChatMessage()` on
`event->chatEntryType == 1` before formatting the friend summary, JSON payload,
and browser event. Non-chat entries are logged through the existing lifecycle
diagnostic and do not emit `lobby.%s.chat`.

## Evidence

Primary evidence:

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `references/analysis/quakelive_symbol_aliases.json`
- `src/code/client/cl_main.c`
- `src/common/platform/platform_steamworks.c`

Observed facts:

1. Ghidra `functions.csv` records `FUN_004645a0` at `0x004645A0`, size `377`.
2. The alias map identifies `sub_4645A0` as
   `SteamLobbyCallbacks_OnLobbyChatMessage`.
3. `analysis_symbols.txt` identifies the surrounding
   `CCallback<class_SteamLobbyCallbacks,struct_LobbyChatMsg_t,0>` vtable, RTTI
   descriptor, and class-hierarchy metadata.
4. Retail HLIL for `sub_4645a0` calls SteamMatchmaking vtable slot `0x6c` to
   read the lobby chat entry.
5. Retail HLIL then checks `00464626  if (var_860 == 1)` before formatting the
   chatter name, id, message, and browser-event payload.
6. Retail HLIL publishes `lobby.%s.chat` only under that branch:
   `004646e2      sub_4f3260(arg1, eax_5, sub_4d9220("lobby.%s.chat"), &var_870)`.
7. `sub_4656a0` registers the lobby chat-message callback object at callback
   id `0x1fb` and binds it to `sub_4645a0`.
8. The source platform wrapper already forwards the possibly updated
   `entryType` from `QL_Steamworks_ReadLobbyChatMessage()` into
   `event.chatEntryType`, so the client callback can reconstruct the retail
   publish gate without changing the shared Steamworks dispatch ABI.

## Source Reconstruction

- Added the `event->chatEntryType != 1` early return in
  `CL_Steam_Lobby_OnLobbyChatMessage()`.
- Kept a concise source diagnostic for ignored non-chat entry types through the
  existing `CL_LogMatchmakingCallbackLifecycle()` path.
- Extended `tests/test_platform_services.py` to pin the retail HLIL function,
  entry-type branch, and `lobby.%s.chat` publish instruction, plus the source
  guard order before friend-summary lookup and browser-event publication.

No game launch was needed because this pass is literal source reconstruction
against committed HLIL/Ghidra evidence and does not require renderer or live
Steam behavior to disambiguate.

## Verification

- `python -m pytest tests/test_platform_services.py::test_client_lobby_bootstrap_reconstructs_retail_connect_surface -q --tb=short`
  - `1 passed`
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

- Focused lobby chat-message publish gate: **82% -> 99%**.
- Focused Steam lobby callback browser-event lane: **91% -> 95%**.
- Broader Steam launch/runtime integration reconstruction confidence after the
  recent bootstrap and lobby-command rounds: **96% -> 96%**.
- Static executable dependency parity for bundled media libraries:
  **100% -> 100%**.
- Repo-wide checked-in tree parity: **99% -> 99%**.
