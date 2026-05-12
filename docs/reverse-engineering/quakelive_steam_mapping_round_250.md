# quakelive_steam.exe Mapping Round 250

Date: 2026-05-12

Scope: the retained client browser/lobby leave wrapper seam in
`src/code/client/cl_main.c`, focused on reconstructing the retail
engine-owned `LeaveLobby` handoff contract while avoiding external-library
implementation work.

## Summary

This round removes the source-only current-lobby validity gate from the
explicit `LeaveLobby` browser lane. The checked-in source was still rejecting
`CL_Steam_LeaveLobby(...)` with `"no active lobby"` and short-circuiting the
shared `CL_Steam_LeaveCurrentLobby(...)` owner when
`cl_steamCallbackState.currentLobbyValid` was false. The committed retail
`SteamLobby_LeaveLobby` owner does not show an equivalent validity boundary:
it checks only that Steam is initialized, forwards the cached lobby ID words
into the leave call, publishes the `.left` event, and clears the cached lobby
identity. The source now follows that shape more closely by letting
`CL_Steam_LeaveLobby(...)` always route into `CL_Steam_LeaveCurrentLobby()`
when Steam services are available, and by letting the shared leave helper act
on the cached ID words directly without a separate current-lobby guard.

Classification mix:

- `0` new engine/client aliases
- `0` engine/client alias renames
- `2` engine/client source reconstruction contract fixes
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main source-parity win is:

- [`cl_main.c`](../../src/code/client/cl_main.c) no longer imposes an extra
  `"no active lobby"` refusal in the explicit browser `LeaveLobby` path.

## Evidence Notes

Observed facts from the committed retail corpus:

- The retained browser dispatcher arm for `LeaveLobby` (case `0x12`) calls
  `SteamLobby_LeaveLobby()` directly with no argument checks or wrapper-local
  current-lobby validity guard.
- The committed companion decomp for `SteamLobby_LeaveLobby`
  (`0x004649E0`) checks only `SteamClient_IsInitialized()`.
- That same retail owner then calls the Steam Matchmaking `0x3c` leave slot
  with the cached lobby ID words, publishes the `"lobby.%s.left"` event using
  those same cached words, and clears the cached lobby ID state.
- There is no visible `CSteamID_IsValid()` or nonzero cached-lobby check in
  that named retail owner before the leave call and event publication.

Source-side inference used this round:

- The source still keeps the outer `CL_SteamServicesEnabled()` gate because the
  checked-in architecture centralizes Steam availability behind that wrapper,
  and that maps cleanly onto the retail `SteamClient_IsInitialized()` owner
  boundary.
- I intentionally limited this round to the explicit leave path rather than
  broadening it to the other lobby wrappers that still depend on
  `CL_Steam_GetCurrentLobbyIdentityWords(...)`, because those owners have
  different retail evidence and should be revisited individually.

## Source Reconstruction

- [`cl_main.c`](../../src/code/client/cl_main.c) no longer early-returns from
  `CL_Steam_LeaveCurrentLobby(...)` when
  `cl_steamCallbackState.currentLobbyValid` is false.
- [`cl_main.c`](../../src/code/client/cl_main.c) no longer logs or returns
  early for `"no active lobby"` in `CL_Steam_LeaveLobby(...)`.
- [`test_platform_services.py`](../../tests/test_platform_services.py) now
  pins the absence of that stale log branch and the absence of the old
  `currentLobbyValid` guard inside `CL_Steam_LeaveCurrentLobby(...)`.

## Verification

Static/source validation:

- `pytest tests/test_platform_services.py -q --tb=no -k "client_browser_lobby_social_shims_reconstruct_retail_qz_instance_dispatch_surface or client_lobby_callback_lanes_reconstruct_retail_matchmaking_event_surface"`
  passed with `2 passed, 73 deselected`
- `git diff --check -- src/code/client/cl_main.c tests/test_platform_services.py docs/reverse-engineering/quakelive_steam_mapping_round_250.md`
  reported only the repo's existing LF -> CRLF normalization warnings on the
  touched text files

Additional note:

- Pytest still emitted the existing `.pytest_cache` permission warning, but
  the assertions passed.

Alias accounting for the current dirty worktree:

- before this pass: `2238` raw `quakelive_steam` aliases, `2157` strict
  address-backed aliases
- after this pass: `2238` raw `quakelive_steam` aliases, `2157` strict
  address-backed aliases
- strict Ghidra address-backed coverage after this pass: `39.412%` of `5473`
  committed functions

Parity estimate after this pass:

- strict-retail client browser/lobby leave-owner seam: `99%` before, `100%`
  after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

The next nearby engine-only pass is to keep walking the remaining
browser-owned lobby and social wrappers where the checked-in source may still
carry slightly sharper validity or fallback policies than the named retail
owners actually expose.
