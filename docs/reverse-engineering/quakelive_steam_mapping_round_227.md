# quakelive_steam.exe Mapping Round 227

Date: 2026-05-11

Scope: the retained client shutdown command-surface lane in
`src/code/client/cl_main.c`, focused on engine-owned command cleanup rather
than external-library code.

## Summary

This round restored four removal-only client command names that still appear in
the committed retail `CL_Shutdown` surface but were missing from the checked-in
engine shutdown path:

- `testy`
- `joinqueue`
- `leavequeue`
- `advert_done`

Classification mix:

- `0` new engine/client aliases
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main source win is:

- [`CL_Shutdown`](../../src/code/client/cl_main.c) now mirrors the retained
  retail removal lane by explicitly calling `Cmd_RemoveCommand` for those four
  names before the browser/web command cleanup block.

## Evidence Notes

- In committed retail HLIL, the retained `CL_Shutdown` command-removal lane
  around `0x004B9E82` includes:
  1. `sub_4c8270("testy")`
  2. `sub_4c8270("joinqueue")`
  3. `sub_4c8270("leavequeue")`
  4. `sub_4c8270("advert_done")`
- In committed retail HLIL, the retained `CL_Init` registration lane around
  `0x004BCC93` does not show matching add-command owners for any of those four
  names.
- The checked-in source tree does not currently define those command names in
  native client, cgame, game, or UI source, which makes them a clean
  shutdown-only parity gap in the retained engine lane.
- [`Cmd_RemoveCommand`](../../src/code/qcommon/cmd.c) already returns
  immediately when a command name is not active, so adding the retail-matching
  removals is behaviorally safe in the checked-in tree while still recovering
  the proper shutdown surface.

## Aliases Added

- none

## Verification

Static/source validation:

- `pytest tests/test_engine_client_command_parity.py -q --tb=no -k "client_command_registration_matches_retail_cinematic_network_and_browser_surface or client_command_handlers_match_retail_cinematic_network_and_browser_contracts"`
  passed
- `git diff --check -- src/code/client/cl_main.c tests/test_engine_client_command_parity.py docs/reverse-engineering/quakelive_steam_mapping_round_227.md`
  reported only the repo's existing LF -> CRLF normalization warnings on the
  touched text files

Alias accounting for the current dirty worktree:

- before this pass: `2237` raw `quakelive_steam` aliases, `2157` strict
  address-backed aliases
- after this pass: `2237` raw `quakelive_steam` aliases, `2157` strict
  address-backed aliases
- strict Ghidra address-backed coverage after this pass: `39.412%` of `5473`
  committed functions

Parity estimate after this pass:

- strict-retail client shutdown removal-only command lane: `99%` before,
  `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

The next nearby engine-only pass is to keep walking the retained client
bootstrap/shutdown surface for any other removal-only or wrapper-only stragglers
before moving to a wider subsystem lane.
