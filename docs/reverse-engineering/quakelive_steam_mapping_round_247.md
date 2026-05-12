# quakelive_steam.exe Mapping Round 247

Date: 2026-05-12

Scope: the retained client browser/lobby wrapper seam in
`src/code/client/cl_main.c`, focused on reconstructing the retail
engine-owned `CreateLobby` and `JoinLobby` contracts while avoiding
external-library implementation work.

## Summary

This round removes two source-side policy layers from the client lobby wrapper
lane. First, `CL_Steam_CreateLobby(...)` no longer clamps the archived
`steam_maxLobbyClients` value back to `16` when it is non-positive; it now
forwards the current cvar value directly into the shared matchmaking wrapper,
which matches the named retail owner more closely. Second, `CL_Steam_JoinLobby(...)`
no longer routes the incoming decimal lobby ID through the stricter shared
identity parser. Instead, it now mirrors the retail `SteamLobby_JoinLobby`
owner more closely by zero-initializing a local 64-bit ID, applying
`sscanf("%llu", ...)` when a source string is present, and forwarding the
resulting split words directly into `QL_Steamworks_JoinLobby(...)`.

Classification mix:

- `0` new engine/client aliases
- `0` engine/client alias renames
- `2` engine/client source reconstruction contract fixes
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main source-parity wins are:

- [`cl_main.c`](../../src/code/client/cl_main.c) no longer invents a
  client-side positive-member-count clamp in the `CreateLobby` browser lane.
- [`cl_main.c`](../../src/code/client/cl_main.c) no longer rejects
  `JoinLobby` inputs just because the shared source parser would fail them; it
  now follows the same looser parse-and-forward shape the retained retail
  wrapper uses.

## Evidence Notes

Observed facts from the committed retail corpus:

- The retained `qz_instance` dispatcher calls `SteamLobby_CreateLobby()` for
  method case `0x11` with no additional argument massaging in the browser
  owner.
- The committed companion decomp for `SteamLobby_CreateLobby`
  (`0x004649B0`) shows it checking `SteamClient_IsInitialized()` and then
  calling the Steam Matchmaking `0x34` slot with the current lobby-size value
  loaded from the retained global state; there is no visible `<= 0` clamp in
  that owner.
- The retained `qz_instance` dispatcher calls `SteamLobby_JoinLobby()` for
  method case `0x13` after only confirming that at least one JS argument is
  present and stringifying that argument.
- The committed companion decomp for `SteamLobby_JoinLobby`
  (`0x00465630`) zero-initializes the split lobby ID words, calls
  `sscanf(param_1, "%llu", &local_c)`, and immediately forwards the resulting
  low/high words into the Steam Matchmaking `0x38` slot with no parse-success
  check in between.

Source-side inference used this round:

- Retaining a null-pointer guard around the local `sscanf(...)` in
  `CL_Steam_JoinLobby(...)` is a small source-safety concession for the public
  `const char *` wrapper signature; the browser-owned dispatch path already
  provides a string slot before this owner is reached.
- I intentionally left the stricter shared identity parser in place for the
  other browser/social helpers until each owner is revalidated individually,
  rather than broadening this round into a speculative cross-cutting change.

## Source Reconstruction

- [`cl_main.c`](../../src/code/client/cl_main.c) now forwards
  `cl_steamMaxLobbyClients->integer` directly into `QL_Steamworks_CreateLobby(...)`
  without the older `maxMembers <= 0` fallback rewrite.
- [`cl_main.c`](../../src/code/client/cl_main.c) now implements
  `CL_Steam_JoinLobby(...)` with a local `parsedLobbyId` word that is
  zero-initialized, optionally parsed via `sscanf("%llu", ...)`, and split
  directly into the shared `QL_Steamworks_JoinLobby(...)` wrapper.
- [`test_platform_services.py`](../../tests/test_platform_services.py) now
  pins the absence of the stale `CreateLobby` clamp and the new retail-shaped
  `JoinLobby` parse-and-forward contract.

## Verification

Static/source validation:

- `pytest tests/test_platform_services.py -q --tb=no -k "client_browser_lobby_social_shims_reconstruct_retail_qz_instance_dispatch_surface"`
  passed with `1 passed, 74 deselected`
- `git diff --check -- src/code/client/cl_main.c tests/test_platform_services.py docs/reverse-engineering/quakelive_steam_mapping_round_247.md`
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

- strict-retail client browser/lobby `CreateLobby` and `JoinLobby` contract
  seam: `99%` before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

The next nearby engine-only pass is to keep walking the retained lobby/social
wrappers where the current source may still enforce a slightly stronger
validity policy than the named retail owners actually carry.
