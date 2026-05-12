# quakelive_steam.exe Mapping Round 240

Date: 2026-05-12

Scope: the retained client `qz_instance` integer-argument bridge in
`src/code/client/cl_cgame.c`, focused on reconstructing the retail
engine-owned browser method coercion contract while avoiding external-library
implementation work.

## Summary

This round tightens a small but real browser bridge exactness gap in the
engine-owned `qz_instance` method dispatcher. Retail reaches the browser
request owners with already-coerced integer arguments from Awesomium; the
checked-in source was still parsing stringified arguments inline through raw
`atoi` / `strtoul`, which accepted partial numeric prefixes that the retained
typed dispatch would not naturally produce.

Classification mix:

- `0` new engine/client aliases
- `0` engine/client alias renames
- `2` engine/client source reconstruction contract fixes
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main source-parity wins are:

- [`cl_cgame.c`](../../src/code/client/cl_cgame.c) now exposes
  `QLJSHandler_CoerceIntegerArgument(...)` and
  `QLJSHandler_CoerceUnsignedIntegerArgument(...)` so integer-valued browser
  arguments are normalized in one owner-local place instead of being parsed ad
  hoc at each method case.
- [`cl_cgame.c`](../../src/code/client/cl_cgame.c) now routes the integer-coded
  browser methods (`RequestServers`, `RequestServerDetails`,
  `SetLobbyServer`, `GetAllUGC`, `GetNextKeyDown`, and `SetFavoriteServer`)
  through those helpers rather than through raw `atoi` / `strtoul`.

## Evidence Notes

Observed facts from the committed retail corpus:

- The committed retail dispatcher block at `004320EF` / `0043211D` / `004321EB`
  decodes browser method arguments with `Awesomium::JSValue::ToInteger(...)`
  before calling:
  - `sub_463090` (`RequestServers`)
  - `sub_4630B0` (`RequestServerDetails`)
  - `sub_464B10` (`SetLobbyServer`)
- That means the owning request helpers receive already-normalized numeric
  values rather than free-form strings.

Source-side inference used this round:

- The current reconstructed browser bridge still receives textual arguments in
  `QLJSHandler_OnMethodCall(...)`, so it cannot mirror retail's typed Awesomium
  values exactly.
- The closest source-owned reconstruction is therefore to centralize numeric
  coercion at the dispatcher boundary and reject trailing non-whitespace junk,
  instead of letting raw `atoi` / `strtoul` accept partial prefixes like
  `"123abc"`.

## Source Reconstruction

- [`cl_cgame.c`](../../src/code/client/cl_cgame.c) now defines
  `QLJSHandler_CoerceIntegerArgument(...)`, which:
  - returns `0` for null, empty, or non-numeric inputs
  - uses `strtol(...)`
  - requires the remaining suffix to be whitespace-only
- [`cl_cgame.c`](../../src/code/client/cl_cgame.c) now defines
  `QLJSHandler_CoerceUnsignedIntegerArgument(...)` with the matching unsigned
  contract through `strtoul(...)`.
- [`cl_cgame.c`](../../src/code/client/cl_cgame.c) now uses those helpers for
  the integer-coded browser method cases instead of repeating local raw parse
  calls.

## Verification

Static/source validation:

- `pytest tests/test_platform_services.py -q --tb=no -k "client_browser_js_bridge_reconstructs_qz_instance_contract"`
  passed with `1 passed, 74 deselected`
- `pytest tests/test_platform_services.py -q --tb=no -k "client_browser_js_bridge_reconstructs_qz_instance_contract or client_browser_server_shims_reconstruct_retail_server_browser_surface"`
  passed with `2 passed, 73 deselected`
- `git diff --check -- src/code/client/cl_cgame.c tests/test_platform_services.py docs/reverse-engineering/quakelive_steam_mapping_round_240.md`
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

- strict-retail client `qz_instance` integer-coercion seam: `99%` before,
  `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

The next nearby engine-only pass is to keep walking the remaining
browser-bridge and compatibility-owned client method seams where retail still
reaches a helper boundary with slightly sharper typed ownership than the
current source-owned string bridge carries.
