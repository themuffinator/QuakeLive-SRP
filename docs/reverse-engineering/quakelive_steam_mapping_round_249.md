# quakelive_steam.exe Mapping Round 249

Date: 2026-05-12

Scope: the retained client browser/lobby chat wrapper seam in
`src/code/client/cl_main.c`, focused on reconstructing the retail
engine-owned `SayLobby` handoff contract while avoiding external-library
implementation work.

## Summary

This round removes the stale `"missing lobby message"` rejection from
`CL_Steam_SayLobby(...)`. The checked-in source was still treating a null
message pointer as a client-side failure, but the committed retail browser
owner does not show an equivalent boundary: it checks only that one JS
argument slot exists, stringifies that slot, and forwards the resulting string
into `SteamLobby_SayLobby(...)`. The source now matches that shape more
closely by normalizing a null message pointer to `""` locally and forwarding
that string directly into `QL_Steamworks_SayLobby(...)`.

Classification mix:

- `0` new engine/client aliases
- `0` engine/client alias renames
- `1` engine/client source reconstruction contract fix
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main source-parity win is:

- [`cl_main.c`](../../src/code/client/cl_main.c) no longer imposes a
  source-only null-message rejection in the `SayLobby` browser wrapper lane.

## Evidence Notes

Observed facts from the committed retail corpus:

- The retained browser dispatcher arm for `SayLobby` (case `0x16`) checks only
  that at least one JS argument slot is present.
- That same retained browser owner stringifies the first JS argument and then
  calls `SteamLobby_SayLobby()` directly.
- The committed companion decomp for `SteamLobby_SayLobby`
  (`0x00464AC0`) computes the string length and forwards the current lobby ID,
  the message pointer, and the computed length into the Steam Matchmaking
  `0x68` slot; there is no visible separate `"missing lobby message"` policy
  in that owner.
- The checked-in browser dispatcher already mirrors part of that retained
  shape by calling `CL_Steam_SayLobby( arguments[0] ? arguments[0] : "" )`.

Source-side inference used this round:

- Because the browser-owned call site already normalizes a missing string slot
  to `""`, the extra null-pointer rejection in `CL_Steam_SayLobby(...)` was
  just dead reconstruction baggage rather than a meaningful retained contract.
- I kept the existing provider and current-lobby guards, since the named
  retail owner still depends on initialized Steam state and a valid current
  lobby identity.

## Source Reconstruction

- [`cl_main.c`](../../src/code/client/cl_main.c) now defines a local
  `lobbyMessage` pointer in `CL_Steam_SayLobby(...)`, normalizes it with
  `message ? message : ""`, and forwards that value into
  `QL_Steamworks_SayLobby(...)`.
- [`cl_main.c`](../../src/code/client/cl_main.c) no longer logs or returns
  early for `"missing lobby message"` in that wrapper.
- [`test_platform_services.py`](../../tests/test_platform_services.py) now
  pins the absence of the stale log branch and the presence of the normalized
  `lobbyMessage` forward path.

## Verification

Static/source validation:

- `pytest tests/test_platform_services.py -q --tb=no -k "client_browser_lobby_social_shims_reconstruct_retail_qz_instance_dispatch_surface"`
  passed with `1 passed, 74 deselected`
- `git diff --check -- src/code/client/cl_main.c tests/test_platform_services.py docs/reverse-engineering/quakelive_steam_mapping_round_249.md`
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

- strict-retail client browser/lobby `SayLobby` handoff seam: `99%` before,
  `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

The next nearby engine-only pass is to keep walking the remaining
browser-owned lobby and social wrappers where the checked-in source may still
enforce slightly sharper argument or fallback policies than the named retail
owners actually expose.
