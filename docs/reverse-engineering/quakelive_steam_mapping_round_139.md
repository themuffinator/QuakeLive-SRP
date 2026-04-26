# quakelive_steam.exe Mapping Round 139

Date: 2026-04-26

Scope: refreshed largest-unaliased queue after round 138. This pass consumed
two queue-head-adjacent SteamID STL rebalance helpers, plus a tightly anchored
ZeroMQ `socket_base.cpp` cluster centered on `sub_407790`.

## Summary

This round mapped `8` `quakelive_steam.exe` functions from the refreshed
largest-unaliased queue and exact adjacent platform/support neighbors.
Classification mix:

- `0` engine-owned functions
- `6` platform-service-owned functions
- `2` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

No source debt was opened. This tranche is intentionally conservative: one
exact `socket_base.cpp` ownership lane and two descriptive STL support aliases
for already-bounded SteamID map/set rebalance helpers.

This pass intentionally left `sub_463980`, `sub_4F67A0`, `sub_435070`,
`sub_440AD0`, `sub_4109D0`, `sub_4C6BD0`, `sub_40B050`, `sub_419AD0`,
`sub_4FC460`, and `sub_517340` unresolved. Their ownership is still bounded,
but the exact durable names need tighter local anchors than this round
produced.

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_461170` | `546` | CRT/STL | `std_tree_insert_steamid_node_rebalance` | Medium-high | No engine debt; lower-level red-black-tree rebalance helper beneath the already-mapped SteamID insert wrapper. |
| 2 | `sub_467620` | `546` | CRT/STL | `std_tree_insert_steamid_map_node_rebalance` | Medium-high | No engine debt; lower-level red-black-tree rebalance helper for the second SteamID map/set lane. |
| 3 | `sub_407790` | `542` | platform-service-owned | `zmq_socket_base_t_dtor` | High | No engine debt; exact `socket_base.cpp` destructor with the `destroyed` assertion and full vtable/critical-section teardown. |
| 4 | `sub_4079B0` | `422` | platform-service-owned | `zmq_socket_base_t_parse_uri` | High | No engine debt; exact URI parser splitting `protocol://address` into two strings and returning `EINVAL` on malformed input. |
| 5 | `sub_407D80` | `426` | platform-service-owned | `zmq_socket_base_t_getsockopt` | High | No engine debt; exact virtual-overload plus generic `options.getsockopt` path. |
| 6 | `sub_407B60` | `260` | platform-service-owned | `zmq_socket_base_t_check_protocol` | High | No engine debt; exact transport gate over `inproc/ipc/tcp/pgm/epgm` plus socket-type compatibility checks. |
| 7 | `sub_407C70` | `149` | platform-service-owned | `zmq_socket_base_t_attach_pipe` | High | No engine debt; exact pipe registration/event-sink attach plus terminating-socket fast path. |
| 8 | `sub_407D10` | `102` | platform-service-owned | `zmq_socket_base_t_setsockopt` | High | No engine debt; exact virtual-overload plus generic `options.setsockopt` fallback. |

## Evidence Notes

- `sub_407790`, `sub_4079B0`, `sub_407B60`, `sub_407C70`, `sub_407D10`, and
  `sub_407D80` close a coherent `zmq::socket_base_t` ownership lane. Local
  HLIL already anchors the bodies to `..\..\..\src\socket_base.cpp`; the exact
  method names line up cleanly against upstream libzmq `socket_base.cpp`
  semantics without needing to open new engine debt.
- `sub_407790` is the exact destructor. It reinstalls the
  `socket_base_t`/`own_t`/`object_t` vtables in teardown order, asserts
  `destroyed` at `socket_base.cpp:0x94`, deletes the monitor and command-pipe
  critical sections, frees the last-endpoint string storage, dismantles the
  ypipe, clears both embedded STL trees, and finishes through the inherited
  `object_t` destructor path.
- `sub_4079B0` is `zmq_socket_base_t_parse_uri`. The body asserts
  `uri_ != NULL` at `socket_base.cpp:0xa8`, copies the URI into a temporary
  string, searches for the `"://"` delimiter, splits the protocol and address
  substrings, and returns `EINVAL` if either side is empty.
- `sub_407B60` is `zmq_socket_base_t_check_protocol`. The transport literal
  set and compatibility gates match the older libzmq method exactly: it
  validates known protocols, then rejects PGM/EPGM for incompatible socket
  types before returning success.
- `sub_407C70` is `zmq_socket_base_t_attach_pipe`. The body asserts that the
  pipe has no sink, registers the socket as the sink, pushes the pipe into the
  retained pipe vector, calls the derived `xattach_pipe` virtual, and
  terminates the pipe immediately if the socket is already closing.
- `sub_407D10` and `sub_407D80` are the socket option dispatchers. Both first
  try the derived-socket virtual overloads; `sub_407D10` falls back to the
  already-mapped `zmq_options_t_setsockopt`, while `sub_407D80` handles the
  retained generic socket options before falling back to the already-mapped
  `zmq_options_t_getsockopt`.
- `sub_461170` and `sub_467620` are not public upstream names; they are
  descriptive support aliases chosen to reflect what the bodies actually do.
  Each helper increments the owning tree size, links a newly allocated node
  under the parent, and performs the full red-black insert rebalance over the
  existing SteamID node layouts. I kept the names at the lower-level
  `*_rebalance` granularity because the higher-level node-allocation wrappers
  around these helpers are distinct functions.

## Aliases Added

- `sub_407790` -> `zmq_socket_base_t_dtor`
- `sub_4079B0` -> `zmq_socket_base_t_parse_uri`
- `sub_407B60` -> `zmq_socket_base_t_check_protocol`
- `sub_407C70` -> `zmq_socket_base_t_attach_pipe`
- `sub_407D10` -> `zmq_socket_base_t_setsockopt`
- `sub_407D80` -> `zmq_socket_base_t_getsockopt`
- `sub_461170` -> `std_tree_insert_steamid_node_rebalance`
- `sub_467620` -> `std_tree_insert_steamid_map_node_rebalance`

## Verification

Alias artifact validation:

- `references/analysis/quakelive_symbol_aliases.json` parses through
  `python -m json.tool`
- duplicate-key scan passed after the alias update
- recount after this pass: `1582` raw alias entries, `1576` address-keyed
  aliases
- address-keyed coverage: `28.796%` of `5473` functions
- refreshed unresolved queue was recomputed against the committed Ghidra
  function-start corpus after the alias update
- no game/runtime launch was performed; this was a static mapping pass

Parity estimate after this mapping-only pass remains unchanged:

- strict-retail Windows replacement target: `100%` before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

After this round, the refreshed largest-unaliased queue begins with:

| # | Address | Ghidra name | Size |
| ---: | --- | --- | ---: |
| 1 | `0x00463980` | `FUN_00463980` | `592` |
| 2 | `0x004F67A0` | `FUN_004f67a0` | `581` |
| 3 | `0x00435070` | `FUN_00435070` | `566` |
| 4 | `0x00440AD0` | `FUN_00440ad0` | `560` |
| 5 | `0x004109D0` | `FUN_004109d0` | `559` |
| 6 | `0x004C6BD0` | `FUN_004c6bd0` | `558` |
| 7 | `0x0040B050` | `FUN_0040b050` | `555` |
| 8 | `0x00419AD0` | `FUN_00419ad0` | `555` |
| 9 | `0x004FC460` | `FUN_004fc460` | `552` |
| 10 | `0x00517340` | `FUN_00517340` | `552` |

The next pass should start with `sub_463980`, `sub_4F67A0`, and
`sub_435070`, then keep working down the remaining top queue while preserving
the existing classification guardrails on unresolved engine, platform-service,
and support-library rows.
