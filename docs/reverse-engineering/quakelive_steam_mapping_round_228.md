# quakelive_steam.exe Mapping Round 228

Date: 2026-05-11

Scope: the retained client bootstrap/shutdown command-surface lane in
`src/code/client/cl_main.c`, focused on engine-owned command parity rather
than external-library code.

## Summary

This round removed the stale checked-in shutdown removal for
`postprocess_restart`, which does not appear in the committed retail
`CL_Shutdown` command-removal lane.

Classification mix:

- `0` new engine/client aliases
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main source win is:

- [`CL_Shutdown`](../../src/code/client/cl_main.c) no longer calls
  `Cmd_RemoveCommand( "postprocess_restart" )`, bringing the checked-in
  shutdown surface back into line with the retained retail owner sequence.

## Evidence Notes

- In committed retail HLIL, the retained `CL_Init` registration lane around
  `0x004BCC93` includes
  `sub_4c81d0("postprocess_restart", sub_4b9060)`.
- In committed retail HLIL, the retained `CL_Shutdown` command-removal lane
  around `0x004B9E82` does not show `sub_4c8270("postprocess_restart")`.
- That same retail shutdown lane also does not show removals for
  `clientinfo` or `reconnect`, which matches the checked-in source once the
  stale `postprocess_restart` removal is dropped.
- The remaining postprocess restart behavior is still preserved through the
  retained command wrapper and through the `vid_restart` path’s explicit
  `Cbuf_AddText( "postprocess_restart\n" )` enqueue.

## Aliases Added

- none

## Verification

Static/source validation:

- `pytest tests/test_engine_client_command_parity.py -q --tb=no -k "client_command_registration_matches_retail_cl_init_surface or client_command_handlers_match_retail_forward_restart_and_info_contracts or postprocess_restart_routes_through_renderer_export_not_renderer_cmd_registration"`
  passed
- `git diff --check -- src/code/client/cl_main.c tests/test_engine_client_command_parity.py docs/reverse-engineering/quakelive_steam_mapping_round_228.md`
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

- strict-retail client postprocess shutdown-command lane: `99%` before,
  `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

The next nearby engine-only pass is to keep walking the retained client
command/bootstrap ownership surface for remaining shutdown asymmetries before
moving back out to a wider subsystem lane.
