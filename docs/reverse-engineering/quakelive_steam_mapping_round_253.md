# quakelive_steam.exe Mapping Round 253

Date: 2026-05-12

Scope: the retained client cached-lobby callback-state shape in
`src/code/client/cl_main.c`, focused on removing the last stale
source-owned `currentLobbyValid` boolean while staying inside engine-owned
reconstruction work.

## Summary

This round finishes the current-lobby cleanup that rounds 250 through 252
started. After those passes, the checked-in source no longer read
`cl_steamCallbackState.currentLobbyValid` anywhere, but the callback-state
struct and the set/clear helpers still carried and wrote that extra boolean.
The committed retail HLIL for the surrounding lobby owners keeps only the
cached lobby low/high words, and the reconstructed source now matches that
shape more closely by dropping the dead boolean entirely and treating the
cached `currentLobbyId` words as the sole retained lobby-state owner.

Classification mix:

- `0` new engine/client aliases
- `0` engine/client alias renames
- `1` engine/client source reconstruction contract fix
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main source-parity win is:

- [`cl_main.c`](../../src/code/client/cl_main.c) no longer preserves a dead
  callback-state boolean that the recovered retail lobby owners do not use.

## Evidence Notes

Observed facts from the committed retail corpus:

- The retained leave owner `sub_4649E0` clears only the cached lobby low/high
  globals after publishing `"lobby.%s.left"`.
- The retained wrapper owners `sub_464AC0`, `sub_464B10`, and `sub_464BB0`
  all consult the cached lobby words directly, gated by the recovered
  `sub_464540(...)` `CSteamID` validity helper.
- The retained lobby-enter success owner `sub_464D90` tests that same helper,
  conditionally leaves the previous lobby, and then replaces only the cached
  lobby low/high words with the newly entered identity.

Source-side inference used this round:

- Once rounds 250 through 252 removed every read of
  `cl_steamCallbackState.currentLobbyValid`, keeping the boolean in the local
  callback-state struct became a pure source-only artifact rather than a
  useful compatibility bridge.

## Source Reconstruction

- [`cl_main.c`](../../src/code/client/cl_main.c) removes
  `currentLobbyValid` from `clSteamCallbackState_t`.
- [`cl_main.c`](../../src/code/client/cl_main.c) now has
  `CL_Steam_SetCurrentLobby(...)` and `CL_Steam_ClearCurrentLobby(...)`
  update only `currentLobbyId`.
- [`tests/test_platform_services.py`](../../tests/test_platform_services.py)
  now pins the absence of `currentLobbyValid` from the client lobby/social
  source file and from the set/clear helpers specifically.

## Verification

Static/source validation:

- `pytest tests/test_platform_services.py -q --tb=no -k "client_browser_lobby_social_shims_reconstruct_retail_qz_instance_dispatch_surface or client_lobby_callback_lanes_reconstruct_retail_matchmaking_event_surface"`
  passed with `1 passed, 75 deselected`
- `pytest tests/test_platform_services.py -q --tb=no`
  passed with `76 passed`
- `git diff --check -- src/code/client/cl_main.c tests/test_platform_services.py docs/reverse-engineering/quakelive_steam_mapping_round_253.md`
  reported only the repo's existing LF -> CRLF normalization warnings on the
  touched text files

## Next Queue Head

The next nearby engine-only pass is to keep walking the client browser and
lobby callback owners for any remaining state that is still represented as a
source-side convenience rather than the lower-level cached-word contracts
visible in the retail HLIL.
