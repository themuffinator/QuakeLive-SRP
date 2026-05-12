# quakelive_steam.exe Mapping Round 230

Date: 2026-05-11

Scope: the retained client browser-command mapping lane in
`src/code/client/cl_cgame.c`, focused on engine-owned browser command wrappers
rather than external-library code.

## Summary

This round cleaned up three browser-command aliases whose promoted names still
described nonexistent `QLWebHost_*_f` wrappers instead of the actual checked-in
client command owners.

Classification mix:

- `0` new engine/client aliases
- `3` engine/client alias renames
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main mapping wins are:

- Renamed `sub_4F2A10` from `QLWebHost_ClearCache_f` to
  `CL_Web_ClearCache_f`
- Renamed `sub_4F2A30` from `QLWebHost_Reload_f` to
  `CL_Web_Reload_f`
- Renamed `sub_4F3CB0` from `QLWebHost_ShowError_f` to
  `CL_Web_ShowError_f`

## Evidence Notes

- In committed retail HLIL, the retained browser command-registration helper
  registers:
  1. `sub_4c81d0("web_showError", sub_4f3cb0)`
  2. `sub_4c81d0("web_clearCache", sub_4f2a10)`
  3. `sub_4c81d0("web_reload", sub_4f2a30)`
- In the checked-in source tree, the direct command-wrapper owners for those
  commands are the explicit client functions in
  [`cl_cgame.c`](../../src/code/client/cl_cgame.c):
  `CL_Web_ShowError_f`, `CL_Web_ClearCache_f`, and `CL_Web_Reload_f`.
- The lower browser-host helpers retained in the same file are named
  `QLWebHost_HideBrowser`, `QLWebHost_NavigateOrOpen`, `QLWebHost_OpenURL`,
  and `QLWebHost_ReloadView`; there is no checked-in
  `QLWebHost_ClearCache_f`, `QLWebHost_Reload_f`, or `QLWebHost_ShowError_f`
  owner corresponding to those three retail command-registration addresses.
- That makes the older `QLWebHost_*_f` aliases stale naming drift from an
  earlier provisional mapping pass rather than the best current retail-owner
  reconstruction.

## Aliases Added

- none

## Verification

Static/source validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- `pytest tests/test_engine_client_command_parity.py -q --tb=no -k "client_command_handlers_match_retail_cinematic_network_and_browser_contracts"`
  passed
- `git diff --check -- references/analysis/quakelive_symbol_aliases.json tests/test_engine_client_command_parity.py docs/reverse-engineering/quakelive_steam_mapping_round_230.md`
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

- strict-retail client browser-command owner naming lane: `99%` before,
  `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

The next nearby engine-only pass is to keep walking the remaining browser and
client command-owner addresses to separate true host helpers from public
command-wrapper owners before widening back out to another subsystem.
