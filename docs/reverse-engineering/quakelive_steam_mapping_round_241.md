# quakelive_steam.exe Mapping Round 241

Date: 2026-05-12

Scope: the retained client `GetNextKeyDown` browser-dispatch seam in
`src/code/client/cl_cgame.c`, focused on reconstructing the retail
engine-owned default-argument contract while avoiding external-library
implementation work.

## Summary

This round closes a narrow `qz_instance` dispatch exactness gap in the
`GetNextKeyDown` arm/disarm path. The checked-in source was defaulting the
capture flag to armed both when the browser supplied no argument and when it
supplied an empty string argument. The committed retail evidence is tighter:
the flag defaults to `1` only when no argument is supplied at all.

Classification mix:

- `0` new engine/client aliases
- `0` engine/client alias renames
- `1` engine/client source reconstruction contract fix
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main source-parity win is:

- [`cl_cgame.c`](../../src/code/client/cl_cgame.c) now defaults
  `GetNextKeyDown` to `qtrue` only when `argumentCount <= 0`; if the browser
  supplies an argument slot, the dispatcher now always routes that slot through
  the local integer-coercion helper instead of treating an empty string as if
  the argument were absent.

## Evidence Notes

Observed facts from the committed retail corpus:

- Round 09 pinned the `GetNextKeyDown` inline dispatcher body at `0043264D`.
- That evidence already established the contract as:
  - write the capture flag from the boolean/integer argument when one is
    supplied
  - default the flag to `1` only when no argument is supplied
- The same round tied that flag directly to the one-shot `game.key` capture
  publication path, so this is a public browser-surface contract rather than a
  private implementation detail.

Source-side inference used this round:

- The current source bridge receives stringified arguments rather than retail's
  typed Awesomium values, but argument presence vs absence is still observable
  through `argumentCount`.
- Treating an empty string as “no argument supplied” is therefore looser than
  the retail contract and should be avoided.

## Source Reconstruction

- [`cl_cgame.c`](../../src/code/client/cl_cgame.c) now checks only
  `argumentCount <= 0` for the default-arm path in the
  `CL_WEB_METHOD_GET_NEXT_KEY_DOWN` case.
- [`cl_cgame.c`](../../src/code/client/cl_cgame.c) still uses
  `QLJSHandler_CoerceIntegerArgument(...)` for supplied arguments, so present
  empty strings now resolve through the normal coercion path instead of being
  promoted to the default-arm case.

## Verification

Static/source validation:

- `pytest tests/test_platform_services.py -q --tb=no -k "client_browser_js_bridge_reconstructs_qz_instance_contract"`
  passed with `1 passed, 74 deselected`
- `pytest tests/test_platform_services.py -q --tb=no -k "client_browser_js_bridge_reconstructs_qz_instance_contract or client_browser_server_shims_reconstruct_retail_server_browser_surface"`
  passed with `2 passed, 73 deselected`
- `git diff --check -- src/code/client/cl_cgame.c tests/test_platform_services.py docs/reverse-engineering/quakelive_steam_mapping_round_241.md`
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

- strict-retail client `GetNextKeyDown` default-argument seam: `99%` before,
  `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

The next nearby engine-only pass is to keep walking the remaining browser
dispatcher method cases where the source string bridge still carries a slightly
looser argument-presence contract than the retained typed Awesomium dispatch.
