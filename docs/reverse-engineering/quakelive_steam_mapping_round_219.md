# quakelive_steam.exe Mapping Round 219

Date: 2026-05-11

Scope: the retained Win32 network transport/bootstrap lane in
`src/code/win32/win_net.c`, plus the engine-owned local-server discovery caller
in `src/code/client/cl_main.c`.

## Summary

This round did not add new `quakelive_steam.exe` aliases, but it did tighten
the checked-in Win32 engine networking code against the smaller retail host
contract that the committed HLIL shows around packet send/receive and network
bootstrap.

Classification mix:

- `0` engine-owned functions newly aliased
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main source wins are:

- [`Sys_GetPacket`](../../src/code/win32/win_net.c),
  [`Sys_SendPacket`](../../src/code/win32/win_net.c),
  [`Sys_IsLANAddress`](../../src/code/win32/win_net.c),
  [`NET_GetCvars`](../../src/code/win32/win_net.c), and
  [`NET_Config`](../../src/code/win32/win_net.c) now follow the retail
  AF_INET-only Win32 transport shape instead of keeping the broader Quake III
  IPX socket lane.
- [`CL_LocalServers_f`](../../src/code/client/cl_main.c) now only emits the
  retained UDP broadcast query, which keeps the caller coherent with the retail
  `Sys_SendPacket` contract.

## Evidence Notes

- The decisive retail owners were already mapped in the committed alias corpus:
  `sub_4EE260` (`Sys_GetPacket`), `sub_4EE460` (`Sys_SendPacket`),
  `sub_4EE570` (`Sys_IsLANAddress`), `sub_4EF130` (`NET_GetCvars`), and
  `sub_4EF250` (`NET_Config`).
- `sub_4EE260` reads from the single retained IP socket (`data_5734a8`) and
  does not show the older Quake III protocol loop that alternated between UDP
  and IPX sockets.
- `sub_4EE460` only accepts the retained broadcast/IP address types before
  converting through `NetadrToSockadr(...)`; the HLIL no longer shows a Win32
  IPX send branch.
- `sub_4EE570` preserves the loopback and IPv4 LAN classification logic, but
  it does not carry the old unconditional `NA_IPX` LAN fast path.
- `sub_4EF130` registers only `net_noudp` plus the SOCKS cvars
  (`net_socksEnabled`, `net_socksServer`, `net_socksPort`,
  `net_socksUsername`, `net_socksPassword`). The committed HLIL does not show a
  retained `net_noipx` cvar in this bootstrap block.
- `sub_4EF250` gates networking from the retained UDP toggle, closes only the
  IP and SOCKS sockets, and reopens only the IP path through `NET_OpenIP()`.
- Caller-side coherence note: once the retail `Sys_SendPacket` contract is
  AF_INET-only, the checked-in `CL_LocalServers_f` cannot keep sending an
  extra `NA_BROADCAST_IPX` probe without diverging from the host path.

## Aliases Added

- None in this round. Alias ownership stayed stable; the work here was source
  reconstruction against already-mapped retail functions.

## Verification

Static/source validation:

- `pytest tests/test_engine_cvar_retail_parity.py tests/test_engine_client_command_parity.py -q --tb=no -k "network or localservers"`
  passed (`6 passed, 45 deselected`)
- `git diff --check -- src/code/win32/win_net.c src/code/client/cl_main.c tests/test_engine_cvar_retail_parity.py tests/test_engine_client_command_parity.py docs/reverse-engineering/quakelive_steam_mapping_round_219.md`
  reported only the repo's existing LF -> CRLF normalization warnings on the
  touched text files

Alias accounting for the current dirty worktree:

- before this pass: `2235` raw `quakelive_steam` aliases, `2156` strict
  address-backed aliases
- after this pass: `2235` raw `quakelive_steam` aliases, `2156` strict
  address-backed aliases
- strict Ghidra address-backed coverage after this pass: `39.393%` of `5473`
  committed functions

Parity estimate after this pass:

- strict-retail Windows replacement target: `99%` before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

The next useful nearby pass is to keep following the retail engine-owned
server-browser lane around the `"getinfo xxx"` callers and response bookkeeping
so the remaining client/browser helpers can be tied more directly to the
committed HLIL owners instead of inferred only from shared GPL structure.
