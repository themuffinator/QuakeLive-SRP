# quakelive_steam.exe Mapping Round 224

Date: 2026-05-11

Scope: the retained client browser/query command seam in
`src/code/client/cl_main.c`, focusing on engine-owned server-browser behavior
and avoiding external-library implementation work.

## Summary

This round tightened the checked-in client browser/query path by shrinking a
stale GPL-era command surface and routing the retained Steam browser fallback
through direct helper calls instead of old console-text dispatch.

Classification mix:

- `0` new engine/client aliases
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main source wins are:

- [`CL_Steam_RequestServers`](../../src/code/client/cl_main.c) no longer emits
  `"localservers"` / `"globalservers ..."` command text through
  `Cbuf_ExecuteText`. It now calls direct internal query helpers, which is the
  narrower reconstruction once the retail command-registration evidence is
  taken into account.
- The checked-in client bootstrap surface no longer registers the stale public
  `localservers`, `globalservers`, `ping`, or `serverstatus` commands in
  `CL_Init`.
- The dead public `CL_Ping_f` and `CL_ServerStatus_f` wrappers have been
  removed from the checked-in source.

## Evidence Notes

- In committed retail HLIL, the `CL_Init` registration list around
  `0x004BCC93` cleanly shows retained owners for `cmd`, `configstrings`,
  `clientinfo`, `snd_restart`, `vid_restart`, `postprocess_restart`,
  `disconnect`, `record`, `demo`, `stoprecord`, `connect`, `reconnect`,
  `setenv`, `showip`, the filesystem list commands, `model`, `userinfo`, and
  the Steam overlay commands.
- That same committed retail registration lane does **not** show matching
  `Cmd_AddCommand` owners for `localservers`, `globalservers`, `ping`, or
  `serverstatus`, even though the surrounding registration block is otherwise
  well recovered.
- The committed retail shutdown lane still removes `cinematic`, `localservers`,
  `globalservers`, and `ping`, which strongly suggests a smaller retained
  command-add surface than the inherited GPL client bootstrap path.
- The committed HLIL also does not surface the GPL-only user-facing wrapper
  strings `"usage: ping [server]"` or `"Usage: serverstatus [server]"`, while
  the retained engine query owners around `CL_GetServerStatus`,
  `CL_ServerStatus`, `CL_GetPing`, and `CL_UpdateVisiblePings_f` remain
  address-backed and intact.
- From that evidence, the direct-helper rewrite in `CL_Steam_RequestServers`
  is an inference, but it is a narrower one than keeping a browser path that
  depends on public console commands the retail bootstrap does not appear to
  register.

## Aliases Added

- none

## Verification

Static/source validation:

- `pytest tests/test_engine_client_command_parity.py tests/test_platform_services.py -q --tb=no -k "client_command_registration_matches_retail_cinematic_network_and_browser_surface or client_command_handlers_match_retail_cinematic_network_and_browser_contracts or client_browser_server_shims_reconstruct_retail_server_browser_surface"`
  passed
- `git diff --check -- src/code/client/cl_main.c src/code/client/client.h tests/test_engine_client_command_parity.py tests/test_platform_services.py docs/reverse-engineering/quakelive_steam_mapping_round_224.md`
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

- strict-retail client browser/query command lane: `98%` before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

The next nearby pass is the remaining client command-registration seam around
`cinematic` and `rcon`, which still looks wider than the committed retail
bootstrap list, but that lane should be tightened only after another owner
pass confirms whether those commands are truly absent or simply recovered
through a still-unmapped registration path.
