# quakelive_steam.exe Mapping Round 226

Date: 2026-05-11

Scope: the retained client command/bootstrap seam in
`src/code/client/cl_main.c`, focused on engine-owned console-command parity
rather than external-library code.

## Summary

This round removed the stale client-side `cinematic` init registration that
does not appear in the committed retail `CL_Init` command-add surface.

Classification mix:

- `0` new engine/client aliases
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main source win is:

- The checked-in client bootstrap surface no longer registers a public
  `cinematic` command during `CL_Init`, while keeping the retained
  `CL_PlayCinematic_f` implementation and the retail-matching shutdown
  `Cmd_RemoveCommand( "cinematic" )` intact.

## Evidence Notes

- In committed retail HLIL, the retained `CL_Init` registration lane around
  `0x004BCC93` shows:
  `cmd`, `configstrings`, `clientinfo`, `snd_restart`, `vid_restart`,
  `postprocess_restart`, `disconnect`, `record`, `demo`, `stoprecord`,
  `connect`, `reconnect`, `setenv`, `showip`, `fs_openedList`,
  `fs_referencedList`, `model`, `userinfo`, `clientviewprofile`, and
  `clientfriendinvite`.
- That same retail command-add lane does not show
  `sub_4c81d0("cinematic", ...)`.
- In committed retail HLIL, the retained `CL_Shutdown` command-removal lane
  around `0x004B9E82` still does show `sub_4c8270("cinematic")`.
- Inside the checked-in source tree, the only bootstrap mismatch in this
  nearby command surface was the extra
  `Cmd_AddCommand( "cinematic", CL_PlayCinematic_f )` line in
  [`CL_Init`](../../src/code/client/cl_main.c); the handler implementation
  itself remains present in [`cl_cin.c`](../../src/code/client/cl_cin.c).

## Aliases Added

- none

## Verification

Static/source validation:

- `pytest tests/test_engine_client_command_parity.py -q --tb=no -k "client_command_registration_matches_retail_cinematic_network_and_browser_surface or client_command_handlers_match_retail_cinematic_network_and_browser_contracts"`
  passed
- `git diff --check -- src/code/client/cl_main.c tests/test_engine_client_command_parity.py docs/reverse-engineering/quakelive_steam_mapping_round_226.md`
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

- strict-retail client `cinematic` init-registration lane: `99%` before,
  `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

The next nearby engine-only pass is the remaining client command-surface
ownership cleanup around removal-only commands that still appear in retail
shutdown but not in the checked-in bootstrap lane.
