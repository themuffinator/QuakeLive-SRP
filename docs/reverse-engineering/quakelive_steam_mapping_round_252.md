# quakelive_steam.exe Mapping Round 252

Date: 2026-05-12

Scope: the retained client lobby-enter cached-lobby handoff seam in
`src/code/client/cl_main.c`, focused on reconstructing the retail
engine-owned pre-enter leave policy while avoiding external-library
implementation work.

## Summary

This round removes one last source-only callback-state dependency from the
current-lobby wrapper family. The checked-in source was still deciding whether
`CL_Steam_Lobby_OnLobbyEnter(...)` should leave the previous lobby by checking
`cl_steamCallbackState.currentLobbyValid`. The committed retail lobby-enter
owner instead tests the cached current-lobby words through the same retained
`CSteamID` validity helper used by the other browser lobby wrappers, then
invokes the shared leave owner only when that cached identity is valid. The
source now mirrors that shape more closely by reusing
`CL_Steam_GetCurrentLobbyIdentityWords(...)` as the pre-enter leave gate.

Classification mix:

- `0` new engine/client aliases
- `0` engine/client alias renames
- `1` engine/client source reconstruction contract fix
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main source-parity win is:

- [`cl_main.c`](../../src/code/client/cl_main.c) no longer lets
  `CL_Steam_Lobby_OnLobbyEnter(...)` depend on the extra
  `currentLobbyValid` boolean before leaving a previously cached lobby.

## Evidence Notes

Observed facts from the committed retail corpus:

- The committed HLIL for the retained lobby-enter owner `sub_464D90`
  success path first checks `sub_464540(&data_e3033c)`.
- That same success path calls `sub_4649E0()` only when the cached lobby
  identity passes that helper, and only then replaces `data_e3033c` /
  `data_e30340` with the newly entered lobby words.
- Round 251 already tied `sub_464540(...)` to the retail cached-identity
  `CSteamID` validity contract used by `SetLobbyServer`,
  `ShowInviteOverlay`, and the current-lobby wrapper family.

Source-side inference used this round:

- Reusing `CL_Steam_GetCurrentLobbyIdentityWords(...)` in the lobby-enter
  callback is narrower and more faithful than continuing to consult the
  source-owned `currentLobbyValid` flag, because that helper already encodes
  the retail validity boundary recovered from `sub_464540(...)`.

## Source Reconstruction

- [`cl_main.c`](../../src/code/client/cl_main.c) now gates the pre-enter
  `CL_Steam_LeaveCurrentLobby()` call with
  `CL_Steam_GetCurrentLobbyIdentityWords( NULL, NULL )`.
- [`tests/test_platform_services.py`](../../tests/test_platform_services.py)
  now pins the absence of `currentLobbyValid` in the lobby-enter success path
  and the presence of the shared cached-lobby validity helper at that gate.

## Verification

Static/source validation:

- `pytest tests/test_platform_services.py -q --tb=no -k "client_browser_lobby_social_shims_reconstruct_retail_qz_instance_dispatch_surface or client_lobby_callback_lanes_reconstruct_retail_matchmaking_event_surface"`
  passed with `1 passed, 75 deselected`
- `pytest tests/test_platform_services.py -q --tb=no`
  passed with `76 passed`
- `git diff --check -- src/code/client/cl_main.c tests/test_platform_services.py docs/reverse-engineering/quakelive_steam_mapping_round_252.md`
  reported only the repo's existing LF -> CRLF normalization warnings on the
  touched text files

## Next Queue Head

The next nearby engine-only pass is to keep walking the lobby callback/event
owners for any remaining places where the checked-in source still prefers
callback-state booleans over the recovered cached-identity contracts visible
in the retail HLIL.
