# quakelive_steam.exe Mapping Round 221

Date: 2026-05-11

Scope: the retained client ping/status helper lane in
`src/code/client/cl_main.c`, staying within the engine-owned server-browser
path and avoiding external-library work.

## Summary

This round did not add new aliases. Instead, it tightened the checked-in
client ping-helper lane by removing one dead GPL-era wrapper that does not
appear in the retained retail owner set.

Classification mix:

- `0` engine/qcommon support function aliases
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main source win is:

- [`CL_UpdateServerInfo`](../../src/code/client/cl_main.c) has been removed
  from the checked-in source. It was unreferenced in the tree, and the retail
  `CL_GetPing` / `CL_GetPingInfo` owner sequence in the committed HLIL and
  Ghidra function corpus does not preserve a standalone wrapper in that slot.

## Evidence Notes

- In the current checked-in source, `CL_UpdateServerInfo` sat between
  `CL_GetPing` and `CL_GetPingInfo`, but no other code path referenced it.
- In the committed retail function corpus, the recovered owner sequence around
  this lane is:
  1. `sub_4BACB0` -> `CL_GetPing`
  2. `sub_4BADB0` -> `CL_GetPingInfo`
  3. `sub_4BADF0` -> `CL_ClearPing`
  4. `sub_4BAE10` -> `CL_GetPingQueueCount`
  5. `sub_4BAE60` -> `CL_UpdateVisiblePings_f`
- There is no committed retail function owner between `0x004BACB0` and
  `0x004BADB0` for an extra `CL_UpdateServerInfo`-style wrapper, and HLIL
  search over the same lane does not show a separate status-update helper.
- The retained retail `CL_GetPing` body already performs the
  `CL_SetServerInfoByAddress(...)` update directly before returning the ping
  time, so keeping a second uncalled wrapper in the source only widens the
  checked-in lane away from the recovered owner set.

## Aliases Added

- none

## Verification

Static/source validation:

- `pytest tests/test_engine_netcode_parity.py -q --tb=no -k "cl_serverinfopacket or ping_helper_lane or cl_setserverinfo"`
  passed
- `git diff --check -- src/code/client/cl_main.c tests/test_engine_netcode_parity.py docs/reverse-engineering/quakelive_steam_mapping_round_221.md`
  reported only the repo's existing LF -> CRLF normalization warnings on the
  touched text files

Alias accounting for the current dirty worktree:

- before this pass: `2236` raw `quakelive_steam` aliases, `2157` strict
  address-backed aliases
- after this pass: `2236` raw `quakelive_steam` aliases, `2157` strict
  address-backed aliases
- strict Ghidra address-backed coverage after this pass: `39.412%` of `5473`
  committed functions

Parity estimate after this pass:

- strict-retail client ping/helper lane: `99%` before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

The next useful nearby pass is still the unresolved client command-wrapper seam
around `localservers`, `globalservers`, `ping`, and `serverstatus`, but only
after stable address-backed evidence ties those wrappers to explicit retail
owners instead of inferring from inherited Quake III command text alone.
