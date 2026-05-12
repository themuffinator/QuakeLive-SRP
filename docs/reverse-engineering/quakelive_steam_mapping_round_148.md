# quakelive_steam.exe Mapping Round 148

Date: 2026-04-27

Scope: queue-head STL/support-library mapping for the repeated red-black-tree
insert/rebalance helpers around the current `quakelive_steam.exe` host backlog.
This pass stayed mapping-only and focused on the ZMQ pointer/string map lanes
plus the Json object-member map helpers.

## Summary

This round resolved `12` additional `quakelive_steam.exe` rows and corrected
`1` older over-specific alias. Classification mix:

- `0` engine-owned functions
- `0` platform-service-owned functions
- `12` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main outcome is that the queue-head helper cluster is no longer anonymous:

- the repeated ZMQ pointer-set insert lane is now named and no longer pretends
  to be outpipe-specific
- the `poller_base.cpp` timer-tree insert path now has exact insert and
  rebalance labels
- the Json object-member insert/find/rebalance trio now reads cleanly as the
  retained `Json::Value` object-map helper lane
- the socket-base string wrappers for endpoint and pending-connection inserts
  are now explicit, with the shared larger-string rebalance helper left generic
  because it is reused by both the endpoint wrapper and the router/stream
  outpipe wrapper

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_40F7E0` | `549` | support-library | `std_tree_insert_zmq_ptr_node_rebalance` | High | Closed; this rebalance core is shared by the ZMQ pointer-set family used by `own.cpp`, `router.cpp`, `session_base.cpp`, and `mtrie.cpp`. |
| 2 | `sub_416700` | `204` | support-library | `std_tree_find_or_insert_zmq_ptr_node` | High | Closed; duplicate-eliding pointer-set insert wrapper now matches the shared pointer-node family instead of any single owner. |
| 3 | `sub_416020` | `426` | support-library | `std_tree_erase_zmq_ptr_node_iter` | High | Corrected; earlier `out_pipe` wording was too narrow for the helper actually reused by `owned`, `anonymous_pipes`, `terminating_pipes`, and `mtrie` subscription sets. |
| 4 | `sub_40AEB0` | `208` | support-library | `std_tree_insert_zmq_endpoint_node` | Medium-High | Closed from the socket-base endpoint insertion path and the already-promoted endpoint equal-range/erase helpers. |
| 5 | `sub_40AF80` | `206` | support-library | `std_tree_insert_zmq_pending_connection_node` | Medium-High | Closed from the socket-base pending-connection insertion path and the existing pending-connection equal-range/erase helpers. |
| 6 | `sub_40B050` | `555` | support-library | `std_tree_insert_zmq_pending_connection_node_rebalance` | High | Closed; this core is only reached from the pending-connection wrapper. |
| 7 | `sub_4167D0` | `360` | support-library | `std_tree_find_or_insert_zmq_out_pipe_node` | High | Closed; direct caller evidence comes from the router/stream `outpipes` paths. |
| 8 | `sub_419AD0` | `555` | support-library | `std_tree_insert_zmq_string_pair_node_rebalance` | Medium-High | Closed with a generic core name because the same rebalance body is used by both socket-base endpoint insertion and the router/stream outpipe wrapper. |
| 9 | `sub_41CF40` | `103` | support-library | `std_tree_insert_zmq_timer_node` | High | Closed from the `poller_base.cpp` add-timer path and the existing timer erase helper. |
| 10 | `sub_41CFB0` | `549` | support-library | `std_tree_insert_zmq_timer_node_rebalance` | High | Closed; timer-node rebalance core now matches the add/remove timer family. |
| 11 | `sub_42B760` | `392` | support-library | `std_tree_insert_json_object_member_node` | High | Closed from the `Json::Value` object-member insert path that returns `&node[6]` as the child value. |
| 12 | `sub_42B8F0` | `360` | support-library | `std_tree_find_or_insert_json_object_member_node` | High | Closed; duplicate-aware object-member insert wrapper now has an exact Json object-map name. |
| 13 | `sub_42BA60` | `549` | support-library | `std_tree_insert_json_object_member_node_rebalance` | High | Closed; rebalance core is tied directly to the Json object-member node destructor and compare helpers. |

## Evidence Notes

- `sub_40f3c0`, `sub_414f20`, `sub_41c320`, and `sub_41ef10` all build nodes
  through `sub_40fae0`, compare a pointer key at `node[3]`, and route insert
  or erase through the same `0x10/0x11` sentinel-color layout. The associated
  source-file strings are `own.cpp` (`owned.empty ()`), `router.cpp`
  (`anonymous_pipes.empty ()`), `session_base.cpp`
  (`terminating_pipes.count (pipe_) == 1`), and `mtrie.cpp`, which is why the
  corrected family name had to move from `out_pipe` to the generic `ptr` lane.
- `sub_41c7f0` constructs a deadline/id pair, probes `sub_41d210`, and then
  inserts through `sub_41cf40`; `sub_41c8a0` and `sub_41ca80` already owned the
  matching timer removal path under `poller_base.cpp` and the
  `linger_timer_id` assertions in `session_base.cpp`.
- `sub_415c30` (`zmq_router_t_identify_peer`) and the matching stream-side
  outpipe path at `0x004198F0` both construct `0x34` string-plus-two-word nodes
  via `sub_4169c0` and then call `sub_4167d0`. That wrapper therefore resolves
  exactly to the `outpipes` family, while the shared rebalance body
  `sub_419ad0` stays generic because `sub_40aeb0` also reuses it from the
  socket-base endpoint lane.
- `sub_408d90` inserts an endpoint-keyed node through `sub_40aeb0` after
  copying the address string, while `sub_408340` builds the smaller
  `0x30` pending-connection node and inserts it through `sub_40af80`. The
  existing endpoint/pending-connection erase/equal-range aliases anchor those
  wrapper names.
- `sub_42a130` and its sibling object accessor path at `0x00429F36` ensure the
  `Json::Value` is an object, find a member with `sub_42b1f0`, allocate a new
  member node with `sub_42b680`, and insert through `sub_42b760`. The duplicate
  cleanup path frees the trailing `Json::Value` payload through `sub_429fd0`,
  which ties `sub_42ba60` directly to the Json object-member map lane.

## Aliases Added

- `sub_40AEB0` -> `std_tree_insert_zmq_endpoint_node`
- `sub_40AF80` -> `std_tree_insert_zmq_pending_connection_node`
- `sub_40B050` -> `std_tree_insert_zmq_pending_connection_node_rebalance`
- `sub_40F7E0` -> `std_tree_insert_zmq_ptr_node_rebalance`
- `sub_416700` -> `std_tree_find_or_insert_zmq_ptr_node`
- `sub_4167D0` -> `std_tree_find_or_insert_zmq_out_pipe_node`
- `sub_419AD0` -> `std_tree_insert_zmq_string_pair_node_rebalance`
- `sub_41CF40` -> `std_tree_insert_zmq_timer_node`
- `sub_41CFB0` -> `std_tree_insert_zmq_timer_node_rebalance`
- `sub_42B760` -> `std_tree_insert_json_object_member_node`
- `sub_42B8F0` -> `std_tree_find_or_insert_json_object_member_node`
- `sub_42BA60` -> `std_tree_insert_json_object_member_node_rebalance`

Alias correction:

- `sub_416020` -> `std_tree_erase_zmq_ptr_node_iter`
  Previously labeled `std_tree_erase_zmq_out_pipe_node_iter`, which was too
  narrow for the shared pointer-set helper family.

## Verification

Static mapping validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- duplicate-key scan passed after the alias update
- recount after this pass: `1682` raw alias entries, `1611` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `29.435%` of `5473` functions
- `git diff --check` passed aside from the repo's existing LF -> CRLF
  normalization warnings on touched text files
- no build or runtime launch was needed; this was mapping-only work on the
  committed evidence corpus

Parity estimate after this pass:

- strict-retail Windows replacement target: `100%` before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

After this round, the refreshed largest-unaliased queue begins with:

| # | Address | Ghidra name | Size |
| ---: | --- | --- | ---: |
| 1 | `0x004940D0` | `FUN_004940d0` | `547` |
| 2 | `0x004F4410` | `FUN_004f4410` | `546` |
| 3 | `0x00475CA0` | `FUN_00475ca0` | `545` |
| 4 | `0x004999C0` | `FUN_004999c0` | `541` |
| 5 | `0x00403BB0` | `FUN_00403bb0` | `537` |
| 6 | `0x00480030` | `FUN_00480030` | `537` |
| 7 | `0x004FC240` | `FUN_004fc240` | `537` |
| 8 | `0x00477930` | `FUN_00477930` | `536` |
| 9 | `0x00466B90` | `FUN_00466b90` | `535` |
| 10 | `0x0051FF40` | `FUN_0051ff40` | `535` |

The next pass can stay in the support-library queue with `sub_4940D0` and the
adjacent unresolved host leftovers, or pivot back to source reconstruction now
that the top red-black-tree helper slab is largely named.
