# quakelive_steam.exe Mapping Round 242

Date: 2026-05-12

Scope: the retained client browser/social SteamID parse seam in
`src/code/client/cl_main.c`, focused on reconstructing the retail
engine-owned string-to-identity contract while avoiding external-library
implementation work.

## Summary

This round tightens the shared SteamID parse helper used by the browser-driven
social and lobby methods. The checked-in source was still enforcing a strict
full-string `strtoull(...)` parse, while the committed retail dispatcher hands
those string arguments through `sscanf("%llu", ...)` after
`Awesomium::JSValue::ToString(...)`.

Classification mix:

- `0` new engine/client aliases
- `0` engine/client alias renames
- `1` engine/client source reconstruction contract fix
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main source-parity win is:

- [`cl_main.c`](../../src/code/client/cl_main.c) now parses browser-supplied
  Steam identity strings with `sscanf("%llu", ...)` inside
  `CL_Steam_ParseIdentityArgument(...)`, which is closer to the retained host
  contract used by `JoinLobby`, `Invite`, `RequestUserStats`, and
  `ActivateGameOverlayToUser`.

## Evidence Notes

Observed facts from the committed retail corpus:

- The retained non-returning browser dispatcher converts the relevant social
  method arguments to strings with `Awesomium::JSValue::ToString(...)`.
- The same dispatcher then parses the resulting SteamID text with
  `sscanf("%llu", ...)` in the corresponding method arms:
  - `00432306` (`RequestUserStats`)
  - `004323B5` (`ActivateGameOverlayToUser` user target)
  - `004324B7` (`Invite`)
- That means the retail string-to-identity conversion is not a strict
  full-string `strtoull(...)` validation contract.

Source-side inference used this round:

- The current reconstructed browser/social helpers already centralize SteamID
  parsing in `CL_Steam_ParseIdentityArgument(...)`, so aligning that owner is
  the cleanest source-side way to match the retained browser contract.
- The existing non-zero identity guard remains intact because the surrounding
  source-owned social wrappers still treat zero as invalid input and the
  current writable source has no stronger contrary signal for those paths.

## Source Reconstruction

- [`cl_main.c`](../../src/code/client/cl_main.c) now initializes the local
  identity value to `0ull` and parses through `sscanf( value, "%llu", ... )`
  inside `CL_Steam_ParseIdentityArgument(...)`.
- [`cl_main.c`](../../src/code/client/cl_main.c) no longer rejects trailing
  non-numeric suffixes through the older `strtoull(...)` end-pointer check in
  that shared browser/social helper.

## Verification

Static/source validation:

- `pytest tests/test_platform_services.py -q --tb=no -k "client_browser_lobby_social_shims_reconstruct_retail_qz_instance_dispatch_surface or client_browser_js_bridge_reconstructs_qz_instance_contract"`
  passed with `2 passed, 73 deselected`
- `git diff --check -- src/code/client/cl_main.c tests/test_platform_services.py docs/reverse-engineering/quakelive_steam_mapping_round_242.md`
  reported only the repo's existing LF -> CRLF normalization warnings on the
  touched text files

Alias accounting for the current dirty worktree:

- before this pass: `2238` raw `quakelive_steam` aliases, `2157` strict
  address-backed aliases
- after this pass: `2238` raw `quakelive_steam` aliases, `2157` strict
  address-backed aliases
- strict Ghidra address-backed coverage after this pass: `39.412%` of `5473`
  committed functions

Parity estimate after this pass:

- strict-retail client browser/social SteamID parse seam: `99%` before,
  `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

The next nearby engine-only pass is to keep walking the remaining browser
method cases where the reconstructed source still imposes a slightly sharper
validation boundary than the retained `qz_instance` dispatch path appears to
carry.
