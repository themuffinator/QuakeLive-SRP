# quakelive_steam.exe Mapping Round 245

Date: 2026-05-12

Scope: the retained client browser/social SteamID zero-value parse seam in
`src/code/client/cl_main.c`, focused on reconstructing the retail
engine-owned string-to-identity contract while avoiding external-library
implementation work.

## Summary

This round relaxes the shared browser/social SteamID parse helper so the
source no longer rejects a successfully parsed decimal identity value of
`0ull`. The checked-in helper was still enforcing an extra
`sscanf(...) != 1 || steamId == 0ull` guard, while the committed retail
browser dispatcher arms consistently stringify the relevant JS value, parse it
through `sscanf("%llu", ...)`, and forward the resulting words directly into
the backend call with no visible zero-value rejection.

Classification mix:

- `0` new engine/client aliases
- `0` engine/client alias renames
- `1` engine/client source reconstruction contract fix
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main source-parity win is:

- [`cl_main.c`](../../src/code/client/cl_main.c) no longer treats a parsed
  `0ull` identity as invalid inside `CL_Steam_ParseIdentityArgument(...)`,
  which brings the shared `JoinLobby` / `Invite` / `RequestUserStats` /
  `ActivateGameOverlayToUser` browser helper closer to the retained host
  contract.

## Evidence Notes

Observed facts from the committed retail corpus:

- The retained `RequestUserStats` browser arm stringifies its first argument,
  parses it with `sscanf("%llu", ...)` at `00432306`, and then immediately
  calls the Steam User Stats `0x40` slot.
- The retained `ActivateGameOverlayToUser` browser arm stringifies the target
  user argument, parses it with `sscanf("%llu", ...)` at `004323b5`, and then
  continues directly into the Steam Friends overlay-to-user call path.
- The retained `Invite` browser arm stringifies its first argument, parses it
  with `sscanf("%llu", ...)` at `004324b7`, and then forwards the resulting
  identity into either the lobby-invite or direct-game invite lane.
- None of those retained browser arms show a second-stage `steamId == 0`
  rejection between the `sscanf(...)` parse and the backend call.

Source-side inference used this round:

- The reconstructed source already centralizes the browser-side decimal
  SteamID parse in `CL_Steam_ParseIdentityArgument(...)`, so removing the
  extra zero-value rejection there is the smallest source-side change that
  aligns all of those browser methods at once.
- Null and empty-string rejection remain intact because the retained host
  still requires a string value to be present before `sscanf(...)` can
  succeed, and the current source boundary still uses nullable `const char *`
  inputs.

## Source Reconstruction

- [`cl_main.c`](../../src/code/client/cl_main.c) now returns `qfalse` from
  `CL_Steam_ParseIdentityArgument(...)` only when the source string is missing
  or `sscanf("%llu", ...)` fails, not when the parsed identity value is
  `0ull`.
- [`test_platform_services.py`](../../tests/test_platform_services.py) now
  pins that the shared parse helper still initializes `steamId = 0ull` and
  still uses `sscanf("%llu", ...)`, while no longer containing a hard
  `steamId == 0ull` rejection check.

## Verification

Static/source validation:

- `pytest tests/test_platform_services.py -q --tb=no -k "client_browser_lobby_social_shims_reconstruct_retail_qz_instance_dispatch_surface"`
  passed with `1 passed, 74 deselected`
- `git diff --check -- src/code/client/cl_main.c tests/test_platform_services.py docs/reverse-engineering/quakelive_steam_mapping_round_245.md`
  reported only the repo's existing LF -> CRLF normalization warnings on the
  touched text files

Additional note:

- Pytest still emitted the existing `.pytest_cache` permission warning, but
  the assertion passed.

Alias accounting for the current dirty worktree:

- before this pass: `2238` raw `quakelive_steam` aliases, `2157` strict
  address-backed aliases
- after this pass: `2238` raw `quakelive_steam` aliases, `2157` strict
  address-backed aliases
- strict Ghidra address-backed coverage after this pass: `39.412%` of `5473`
  committed functions

Parity estimate after this pass:

- strict-retail client browser/social SteamID zero-value parse seam: `99%`
  before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

The next nearby engine-only pass is to keep walking the retained
browser-driven social/matchmaking helpers where the reconstructed source may
still add a slightly sharper validation boundary than the committed
`qz_instance` dispatcher appears to carry.
