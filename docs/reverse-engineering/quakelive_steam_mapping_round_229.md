# quakelive_steam.exe Mapping Round 229

Date: 2026-05-11

Scope: the retained client command-owner mapping lane in
`src/code/client/cl_main.c`, focused on engine-owned client wrapper aliases
rather than external-library code.

## Summary

This round cleaned up the alias map around the retained client command
registration surface so the promoted retail owner names now match the checked-in
client wrappers instead of older generic Steam helper labels.

Classification mix:

- `1` new engine/client alias
- `5` engine/client alias renames
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main mapping wins are:

- Added `sub_4B9060 -> CL_PostProcessRestart_f`
- Renamed `sub_4603F0` from `SteamVoice_StartRecording_f` to
  `CL_VoiceStartRecording_f`
- Renamed `sub_460490` from `SteamVoice_StopRecording_f` to
  `CL_VoiceStopRecording_f`
- Renamed `sub_460520` from `SteamCmd_ClearStats_f` to
  `CL_Steam_ClearStats_f`
- Renamed `sub_460E60` from `SteamOverlay_Command_f` to
  `CL_Steam_OverlayCommand_f`
- Renamed `sub_464AA0` from `SteamLobby_ConnectLobby_f` to
  `CL_Steam_ConnectLobby_f`

## Evidence Notes

- In committed retail HLIL, the retained `CL_Init` registration lane shows the
  direct command-owner pairs:
  1. `sub_4c81d0("postprocess_restart", sub_4b9060)`
  2. `sub_4c81d0("+voice", sub_4603f0)`
  3. `sub_4c81d0("-voice", sub_460490)`
  4. `sub_4c81d0("stats_clear", sub_460520)` under the app-id gate
  5. `sub_4c81d0("connect_lobby", sub_464aa0)`
  6. `sub_4c81d0("clientviewprofile", sub_460e60)`
  7. `sub_4c81d0("clientfriendinvite", sub_460e60)`
- The checked-in source owners for those retail commands are the explicit
  client wrappers in [`cl_main.c`](../../src/code/client/cl_main.c):
  `CL_PostProcessRestart_f`, `CL_VoiceStartRecording_f`,
  `CL_VoiceStopRecording_f`, `CL_Steam_ClearStats_f`,
  `CL_Steam_OverlayCommand_f`, and `CL_Steam_ConnectLobby_f`.
- The older generic `Steam*` alias names were useful provisional labels, but
  the retained command-registration evidence is now strong enough to promote
  these addresses to the concrete client command-wrapper owners.
- Committed Ghidra companion output also preserves the `postprocess_restart`
  registration edge as `FUN_004c81d0("postprocess_restart",&LAB_004b9060)`,
  which supports promoting `0x004B9060` as a raw command-owner alias even
  though the committed `functions.csv` inventory still does not materialize it
  as its own address-backed function row.

## Aliases Added

- `sub_4B9060 -> CL_PostProcessRestart_f`

## Verification

Static/source validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- `pytest tests/test_engine_client_command_parity.py -q --tb=no -k "client_command_handlers_match_retail_forward_restart_and_info_contracts or client_steam_command_registration_and_identity_wiring_match_retail_surface or client_steam_command_handlers_match_retail_voice_stats_and_model_contracts"`
  passed
- `git diff --check -- references/analysis/quakelive_symbol_aliases.json tests/test_engine_client_command_parity.py docs/reverse-engineering/quakelive_steam_mapping_round_229.md`
  reported only the repo's existing LF -> CRLF normalization warnings on the
  touched text files

Alias accounting for the current dirty worktree:

- before this pass: `2237` raw `quakelive_steam` aliases, `2157` strict
  address-backed aliases
- after this pass: `2238` raw `quakelive_steam` aliases, `2157` strict
  address-backed aliases
- strict Ghidra address-backed coverage after this pass: `39.412%` of `5473`
  committed functions

Parity estimate after this pass:

- strict-retail client command-owner mapping lane: `99%` before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

The next nearby engine-only pass is to keep walking the client bootstrap and
restart ownership seam for any remaining address-backed wrapper promotions
before moving back out to a wider subsystem lane.
