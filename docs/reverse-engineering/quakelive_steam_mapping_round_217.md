# quakelive_steam.exe Mapping Round 217

Date: 2026-04-28

Scope: the Windows networking bootstrap and sleep seam in
`src/code/win32/win_net.c`, centered on the retained `NET_OpenIP` /
`NET_Config` / `NET_Sleep` event lifecycle.

## Summary

This round restored the retail Winsock event-backed sleep path in
[win_net.c](</E:/Repositories/QuakeLive-reverse/src/code/win32/win_net.c:1>)
and promoted `4` nearby engine owners in the same evidence lane.

Classification mix:

- `4` engine-owned functions
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main source win is:

- [NET_OpenIP](</E:/Repositories/QuakeLive-reverse/src/code/win32/win_net.c:794>),
  [NET_Config](</E:/Repositories/QuakeLive-reverse/src/code/win32/win_net.c:962>),
  and [NET_Sleep](</E:/Repositories/QuakeLive-reverse/src/code/win32/win_net.c:1082>)
  now mirror the retail host more closely by retaining an IP-socket event
  handle, registering `FD_READ` through `WSAEventSelect(...)`, waiting through
  `WSAWaitForMultipleEvents(...)`, and tearing the event down with
  `WSACloseEvent(...)` before the socket closes.

## Evidence Notes

- `sub_4EE6E0` matches
  [NET_IPSocket](</E:/Repositories/QuakeLive-reverse/src/code/win32/win_net.c:471>):
  the HLIL shows the exact UDP socket open path with the
  `"Opening IP socket: %s:%i\n"` / `"localhost:%i\n"` print split, the
  `FIONBIO` nonblocking setup, `SO_BROADCAST`, the `"localhost"` special case,
  and the `bind(...)` warning path.
- `sub_4EEE60` matches
  [NET_GetLocalAddress](</E:/Repositories/QuakeLive-reverse/src/code/win32/win_net.c:713>):
  the HLIL preserves the `gethostname(...)` -> `gethostbyname(...)` chain, the
  hostname/alias prints, the `AF_INET` guard, and the loop that stores up to
  `MAX_IPS` local addresses while printing each dotted-quad.
- `sub_4EF130` matches
  [NET_GetCvars](</E:/Repositories/QuakeLive-reverse/src/code/win32/win_net.c:911>):
  the HLIL is the exact retained modified-flag accumulator over
  `net_noudp`, `net_noipx`, `net_socksEnabled`, `net_socksServer`,
  `net_socksPort`, `net_socksUsername`, and `net_socksPassword`.
- `sub_4EEFE0` matches
  [NET_OpenIP](</E:/Repositories/QuakeLive-reverse/src/code/win32/win_net.c:794>)
  from the HLIL even though the current committed Ghidra `functions.csv` does
  not expose `0x004EEFE0` as a standalone function row. The HLIL shows the
  `net_strict` branch, the auto-scan loop, and the retained post-open
  `CreateEventA(...)` / `WSAEventSelect(...)` event setup in both success
  paths.
- The retail `NET_Sleep` owner at `0x004EF3F0` is the tiny socket-event wait
  helper rather than a generic stub: the HLIL is just the
  `data_5734ac != 0xffffffff` guard followed by
  `WSAWaitForMultipleEvents( 1, &data_5734ac, 0, timeout, 1 )`.

## Aliases Added

- `sub_4EE6E0` -> `NET_IPSocket`
- `sub_4EEE60` -> `NET_GetLocalAddress`
- `sub_4EEFE0` -> `NET_OpenIP`
- `sub_4EF130` -> `NET_GetCvars`

## Verification

Static/source validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- `pytest tests/test_engine_cvar_retail_parity.py::test_engine_cvar_seventeenth_network_bootstrap_tranche_matches_retail_contracts tests/test_engine_cvar_retail_parity.py::test_engine_network_event_wait_path_matches_retail_contracts -q --tb=no`
  passed (`2 passed`)
- `pytest tests/test_engine_cvar_retail_parity.py -q --tb=no`
  still reports the same `3` dirty-tree failures:
  `test_engine_cvar_third_server_tranche_matches_retail_contracts`,
  `test_engine_cvar_fourteenth_core_timing_tranche_matches_retail_contracts`,
  and
  `test_engine_cvar_fifteenth_server_state_tranche_matches_retail_contracts`
- `git diff --check` passed aside from the repo's existing LF -> CRLF
  normalization warnings on touched text files

Alias accounting for the current dirty worktree:

- before this pass: `2227` raw `quakelive_steam` aliases, `2220` strict
  address-backed aliases
- after this pass: `2231` raw `quakelive_steam` aliases, `2223` strict
  address-backed aliases
- strict Ghidra address-backed coverage after this pass: `40.618%` of `5473`
  committed functions

`NET_OpenIP` is raw-only in that accounting because `0x004EEFE0` is still an
HLIL-backed function boundary without a standalone committed `functions.csv`
row.

Parity estimate after this pass:

- strict-retail Windows replacement target: `100%` before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

The next useful nearby pass is the remaining `win_net.c` IPX/bootstrap gap:
`NET_IPXSocket(...)` and `NET_OpenIPX(...)` still have enough retained source
shape to be good promotion candidates, but I did not force names for them here
without the same direct HLIL extraction I had for the IP socket lane.
