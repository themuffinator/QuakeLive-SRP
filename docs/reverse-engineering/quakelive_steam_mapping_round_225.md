# quakelive_steam.exe Mapping Round 225

Date: 2026-05-11

Scope: the retained client command/bootstrap seam in
`src/code/client/cl_main.c`, focused on dead engine-owned console-command
surface rather than external-library code.

## Summary

This round removed the stale client-side `rcon` command lane that does not
appear in the committed retail client bootstrap or shutdown surfaces.

Classification mix:

- `0` new engine/client aliases
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main source wins are:

- [`CL_Rcon_f`](../../src/code/client/cl_main.c) has been removed from the
  checked-in client source.
- The dead client-only `rconPassword` and `rconAddress` cvar bootstrap in
  [`CL_Init`](../../src/code/client/cl_main.c) has been removed with it.
- The checked-in client bootstrap/shutdown surface no longer registers or
  removes a public `rcon` client command.

## Evidence Notes

- In committed retail HLIL, the retained `CL_Init` registration lane around
  `0x004BCC93` does not show `sub_4c81d0("rcon", ...)` anywhere in the
  recovered client command-add surface.
- In committed retail HLIL, the retained `CL_Shutdown` command-removal lane
  around `0x004B9E82` also does not show `sub_4c8270("rcon")`.
- The committed retail HLIL does not surface the GPL-era client wrapper
  strings used by the checked-in `CL_Rcon_f` body:
  1. `"You must set 'rconpassword' before\nissuing an rcon command.\n"`
  2. `"or set the 'rconAddress' cvar\nto issue rcon commands\n"`
- Inside the checked-in source tree, `rcon_client_password` and `rconAddress`
  were only used by `CL_Rcon_f`, and `CL_Rcon_f` itself was only referenced by
  the stale `Cmd_AddCommand( "rcon", ... )` line.
- Server-side remote-console support remains present and unaffected. This pass
  only removes the dead client command wrapper lane.

## Aliases Added

- none

## Verification

Static/source validation:

- `pytest tests/test_engine_client_command_parity.py -q --tb=no -k "client_command_registration_matches_retail_cinematic_network_and_browser_surface or client_command_handlers_match_retail_cinematic_network_and_browser_contracts"`
  passed
- `git diff --check -- src/code/client/cl_main.c tests/test_engine_client_command_parity.py docs/reverse-engineering/quakelive_steam_mapping_round_225.md`
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

- strict-retail client `rcon` command/bootstrap lane: `98%` before, `100%`
  after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

The next nearby command-surface pass is still the unresolved `cinematic`
registration seam, since retail clearly removes it during shutdown but the
committed bootstrap lane still does not show a matching add-command owner.
