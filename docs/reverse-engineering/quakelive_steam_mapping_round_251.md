# quakelive_steam.exe Mapping Round 251

Date: 2026-05-12

Scope: the retained client browser/current-lobby validity seam in
`src/code/client/cl_main.c`, focused on reconstructing the retail cached
`CSteamID` gate that the lobby/social wrappers use before consuming the stored
current lobby words, while avoiding external-library implementation work.

## Summary

This round removes one more source-only lobby policy layer from the retained
browser wrapper lane. The checked-in source was still using
`cl_steamCallbackState.currentLobbyValid` plus a zero-ID check inside
`CL_Steam_GetCurrentLobbyIdentityWords(...)`, which made every wrapper that
depends on the cached current lobby stricter than the named retail owners.
The committed retail browser helpers for `SayLobby`, `SetLobbyServer`, and
`ShowInviteOverlay` instead route the cached low/high words through a shared
`CSteamID` validity helper before calling into Steam. The source now mirrors
that shape more closely by validating the cached `currentLobbyId` bitfields
with the same account-type / universe / instance rules rather than by
consulting the extra source-owned `currentLobbyValid` flag.

Classification mix:

- `0` new engine/client aliases
- `0` engine/client alias renames
- `1` engine/client source reconstruction contract fix
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main source-parity win is:

- [`cl_main.c`](../../src/code/client/cl_main.c) now gates cached-lobby use
  with the retail-shaped `CSteamID` validity contract instead of the source-only
  `currentLobbyValid` boolean.

## Evidence Notes

Observed facts from the committed retail corpus:

- The retained browser dispatcher arm for the two-integer lobby-server method
  (`004321EB -> sub_464B10(...)`) does not perform a wrapper-local current-lobby
  boolean check before entering the named owner.
- The retained browser dispatcher arm for the no-argument invite-overlay method
  (`00432229 -> sub_464BB0()`) likewise enters the named owner directly.
- The committed HLIL for `sub_464B10` and `sub_464BB0` shows both owners first
  checking `sub_460510()` and then calling `sub_464540(&data_e3033c)` before
  using the cached lobby low/high globals.
- The committed HLIL for `sub_464540` is a `CSteamID` validity check on the
  cached low/high words themselves:
  - account type = `(idHigh >> 20) & 0xf`
  - universe = `idHigh >> 24`
  - account instance = `idHigh & 0xfffff`
  - special-case constraints for account types `1`, `3`, and `7`
- The retained `SayLobby` owner `sub_464AC0` also uses those same cached lobby
  globals after only the Steam-initialized gate, which makes the shared
  cached-identity validity helper the sharpest stable source boundary here.

Source-side inference used this round:

- The source still keeps `cl_steamCallbackState.currentLobbyValid` because the
  callback lane publishes it for broader client state, but the committed retail
  wrappers do not appear to consult an equivalent boolean before reusing the
  cached lobby ID.
- Reconstructing the retail validity logic inside
  `CL_Steam_GetCurrentLobbyIdentityWords(...)` is narrower and more faithful
  than deleting the helper outright or broadening this pass into unrelated
  callback-state cleanup.

## Source Reconstruction

- [`cl_main.c`](../../src/code/client/cl_main.c) now reconstructs
  `CL_Steam_GetCurrentLobbyIdentityWords(...)` with the retail-style
  cached-identity validity checks derived from `sub_464540(...)`.
- [`cl_main.c`](../../src/code/client/cl_main.c) no longer rejects cached-lobby
  use solely because `cl_steamCallbackState.currentLobbyValid` is false.
- [`tests/test_platform_services.py`](../../tests/test_platform_services.py)
  now pins the absence of the stale boolean gate and the presence of the
  retail-shaped account-type / universe / account-instance checks.

## Verification

Static/source validation:

- `pytest tests/test_platform_services.py -q --tb=no -k "client_browser_lobby_social_shims_reconstruct_retail_qz_instance_dispatch_surface"`
  passed with `1 passed, 75 deselected`
- `git diff --check -- src/code/client/cl_main.c tests/test_platform_services.py docs/reverse-engineering/quakelive_steam_mapping_round_251.md`
  reported only the repo's existing LF -> CRLF normalization warnings on the
  touched text files

## Next Queue Head

The next nearby engine-only pass is to keep walking the cached-lobby wrapper
family for any remaining helper boundaries that still overfit the current
source callback state rather than the named retail owners.
