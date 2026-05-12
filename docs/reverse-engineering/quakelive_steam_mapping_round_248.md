# quakelive_steam.exe Mapping Round 248

Date: 2026-05-12

Scope: the retained client browser/social wrapper seam in
`src/code/client/cl_main.c`, focused on reconstructing the retail
engine-owned `Invite`, `RequestUserStats`, and
`ActivateGameOverlayToUser` handoff contracts while avoiding external-library
implementation work.

## Summary

This round removes the last shared source-only SteamID parse helper from the
browser/social lane. The checked-in source was still routing `Invite`,
`RequestUserStats`, and `ActivateGameOverlayToUser` through
`CL_Steam_ParseIdentityArgument(...)`, which imposed a stricter
parse-success boundary than the committed retail dispatcher appears to carry.
The source now matches that retail shape more closely: each wrapper
zero-initializes a local 64-bit identity, applies `sscanf("%llu", ...)` only
when a source string pointer is present, and forwards the split low/high words
directly into the shared Steamworks wrapper without a separate
`"invalid user id"` rejection path.

Classification mix:

- `0` new engine/client aliases
- `0` engine/client alias renames
- `3` engine/client source reconstruction contract fixes
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main source-parity wins are:

- [`cl_main.c`](../../src/code/client/cl_main.c) no longer uses a shared
  stricter parser for `Invite`, `RequestUserStats`, and
  `ActivateGameOverlayToUser`.
- [`cl_main.c`](../../src/code/client/cl_main.c) no longer keeps the
  `CL_Steam_ParseIdentityArgument(...)` helper at all, which is closer to the
  retail per-owner parse shape visible in the committed dispatcher evidence.

## Evidence Notes

Observed facts from the committed retail corpus:

- The retained browser dispatcher arm for `RequestUserStats` (case `0x17`)
  checks only that one JS argument is present, stringifies that argument,
  zero-initializes the target identity words, applies `sscanf("%llu", ...)`,
  and then immediately calls the Steam User Stats `0x40` slot.
- The retained browser dispatcher arm for `ActivateGameOverlayToUser`
  (case `0x19`) checks only that two JS arguments are present, parses the
  target user string with `sscanf("%llu", ...)`, stringifies the dialog
  argument, and then calls the Steam Friends `0x74` slot directly.
- The retained browser dispatcher arm for `Invite` (case `0x1A`) also
  zero-initializes the target identity words, parses the first argument with
  `sscanf("%llu", ...)`, and then routes either to the Steam Friends game
  invite call or the Steam Matchmaking lobby invite call without a separate
  parse-success rejection.
- None of those retained browser arms shows a second-stage `"invalid user id"`
  boundary between the `sscanf(...)` parse and the backend call.

Source-side inference used this round:

- The removed `CL_Steam_ParseIdentityArgument(...)` helper was a source-side
  convenience abstraction, not a retail-shaped owner. Once `JoinLobby` moved
  to its own local parse lane in the previous round, these three remaining
  wrappers were the only live users.
- I kept the null-pointer-safe `if ( steamId )` boundary in each source
  wrapper because the source signatures are public `const char *` helpers, but
  the browser-owned dispatch path still provides the stronger runtime context:
  those owners are only reached after the required argument slots are present.

## Source Reconstruction

- [`cl_main.c`](../../src/code/client/cl_main.c) no longer defines
  `CL_Steam_ParseIdentityArgument(...)`.
- [`cl_main.c`](../../src/code/client/cl_main.c) now reconstructs
  `CL_Steam_Invite(...)` with a local `parsedSteamId` word that is
  zero-initialized, optionally parsed with `sscanf("%llu", ...)`, and split
  directly for both the lobby-invite and direct-game-invite backends.
- [`cl_main.c`](../../src/code/client/cl_main.c) now reconstructs
  `CL_Steam_RequestUserStats(...)` with the same local parse-and-forward
  contract instead of a shared parser rejection.
- [`cl_main.c`](../../src/code/client/cl_main.c) now reconstructs
  `CL_Steam_ActivateOverlayToUser(...)` with the same local parse-and-forward
  contract instead of a shared parser rejection.
- [`test_platform_services.py`](../../tests/test_platform_services.py) now
  pins that the shared parser helper is gone and that the three affected
  wrappers use the retail-shaped local `parsedSteamId` handoff instead.

## Verification

Static/source validation:

- `pytest tests/test_platform_services.py -q --tb=no -k "client_browser_lobby_social_shims_reconstruct_retail_qz_instance_dispatch_surface"`
  passed with `1 passed, 74 deselected`
- `git diff --check -- src/code/client/cl_main.c tests/test_platform_services.py docs/reverse-engineering/quakelive_steam_mapping_round_248.md`
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

- strict-retail client browser/social SteamID handoff seam: `99%` before,
  `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

The next nearby engine-only pass is to keep walking the retained
browser-owned matchmaking and social wrappers where the checked-in source may
still preserve a slightly stronger validity or fallback policy than the named
retail owners actually expose.
