# quakelive_steam.exe Mapping Round 130

Date: 2026-04-26

Scope: refreshed largest-unaliased queue after round 129, beginning at
`sub_4FBB00`, `sub_409F20`, and `sub_40A3D0`.

## Summary

This round mapped `13` `quakelive_steam.exe` functions from the refreshed queue
and one adjacent support-library correction that became exact while checking the
IJG JPEG cluster. Classification mix:

- `2` engine-owned functions
- `2` platform-service-owned functions
- `9` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

No source debt was opened. Engine-owned rows land in checked-in botlib owners.
Platform-service rows stay inside the bundled ZeroMQ host/runtime lane.
Support-library rows belong to IJG JPEG, CZMQ/libzmq support code, and STL
container scaffolding rather than Quake engine source debt.

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_4FBB00` | `647` | CRT/STL | `zconfig_chunk_load` | High | No engine debt; CZMQ config-chunk parser that builds the node tree from an in-memory buffer. |
| 2 | `sub_409F20` | `645` | CRT/STL | `std_tree_erase_zmq_pending_connection_node_iter` | Medium-high | No engine debt; STL tree-iterator erase helper used by ZeroMQ pending-connection range teardown. |
| 3 | `sub_40A3D0` | `645` | CRT/STL | `std_tree_erase_zmq_endpoint_node_iter` | Medium-high | No engine debt; STL tree-iterator erase helper used by ZeroMQ endpoint range teardown. |
| 4 | `sub_40A660` | `645` | CRT/STL | `std_tree_equal_range_zmq_endpoint_node` | Medium-high | No engine debt; STL equal-range helper used by endpoint lookup/erase paths. |
| 5 | `sub_40A8F0` | `645` | CRT/STL | `std_tree_equal_range_zmq_pending_connection_node` | Medium-high | No engine debt; STL equal-range helper used by pending-connection lookup/erase paths. |
| 6 | `sub_40BF30` | `633` | platform-service-owned | `zmq_select_t_rm_fd` | High | No engine debt; libzmq `select.cpp` file-descriptor removal helper. |
| 7 | `sub_4970E0` | `627` | engine-owned | `BotLoadCachedCharacter` | High | Source owner exists in botlib `be_ai_char.c`; cached/default skill loader with fallback to `bots/default_c.c`. |
| 8 | `sub_476E20` | `617` | CRT/STL | `jpeg_gen_optimal_table` | Very high | No engine debt; IJG JPEG Huffman histogram/code-length optimizer. |
| 9 | `sub_497360` | `555` | engine-owned | `BotLoadCharacterSkill` | High | Source owner exists in botlib `be_ai_char.c`; wraps the default and requested character-skill load path. |
| 10 | `sub_40BE00` | `303` | platform-service-owned | `zmq_select_t_add_fd` | High | No engine debt; libzmq `select.cpp` file-descriptor registration helper. |
| 11 | `sub_4FBD90` | `302` | CRT/STL | `zconfig_load` | High | No engine debt; CZMQ file loader that reads the full config file then dispatches to `zconfig_chunk_load`. |
| 12 | `sub_4FB740` | `285` | CRT/STL | `zconfig_at_depth` | High | No engine debt; CZMQ helper that returns the latest node at a requested indentation depth. |
| 13 | `sub_4FBA60` | `124` | CRT/STL | `zconfig_new` | High | No engine debt; CZMQ node allocator/initializer used by the config parser. |

## Evidence Notes

- The `zconfig_*` cluster resolved as a unit against upstream CZMQ:
  `sub_4FBA60` allocates a node shell, `sub_4FB740` locates the latest node at
  a requested depth, `sub_4FBB00` parses the in-memory chunk into a tree, and
  `sub_4FBD90` is the file-backed loader wrapper.
- The ZeroMQ tree helpers stayed in the support-library lane instead of opening
  engine debt. `sub_408EC0` uses `sub_40A660` and `sub_40A8F0` to gather the
  endpoint and pending-connection ranges before erasing them with the paired
  iterator helpers `sub_40A3D0` and `sub_409F20`.
- The `select.cpp` ownership for `sub_40BE00` and `sub_40BF30` is explicit
  from the retained source path/assertion strings and the exact `add_fd` /
  `rm_fd` load accounting.
- The botlib character loader pair is exact against checked-in engine source:
  `sub_4970E0` matches `BotLoadCachedCharacter`, and `sub_497360` matches
  `BotLoadCharacterSkill`.
- The IJG JPEG pass also exposed a stale alias: `sub_476E20` is the true
  `jpeg_gen_optimal_table`, while the already-named `sub_4770A0` is the
  pass-finalizer `finish_pass_gather`.

## Aliases Added

- `sub_409F20` -> `std_tree_erase_zmq_pending_connection_node_iter`
- `sub_40A3D0` -> `std_tree_erase_zmq_endpoint_node_iter`
- `sub_40A660` -> `std_tree_equal_range_zmq_endpoint_node`
- `sub_40A8F0` -> `std_tree_equal_range_zmq_pending_connection_node`
- `sub_40BE00` -> `zmq_select_t_add_fd`
- `sub_40BF30` -> `zmq_select_t_rm_fd`
- `sub_476E20` -> `jpeg_gen_optimal_table`
- `sub_4970E0` -> `BotLoadCachedCharacter`
- `sub_497360` -> `BotLoadCharacterSkill`
- `sub_4FB740` -> `zconfig_at_depth`
- `sub_4FBA60` -> `zconfig_new`
- `sub_4FBB00` -> `zconfig_chunk_load`
- `sub_4FBD90` -> `zconfig_load`

## Alias Corrections

- `sub_4770A0` -> `finish_pass_gather` (corrected from
  `jpeg_gen_optimal_table`)

## Verification

Alias artifact validation:

- `references/analysis/quakelive_symbol_aliases.json` parses through
  `python -m json.tool`
- duplicate-key scan passed after the alias update
- recount after this pass: `1445` raw alias entries, `1439` address-keyed
  aliases; six support aliases are still non-`sub_...` jump/helper names
- address-keyed coverage: `26.293%` of `5473` functions
- no game/runtime launch was performed; this was a static mapping pass

Parity estimate after this mapping-only pass remains unchanged:

- strict-retail Windows replacement target: `100%` before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

After this round, the refreshed largest-unaliased queue begins with:

| # | Address | Ghidra name | Size |
| ---: | --- | --- | ---: |
| 1 | `0x004728D0` | `FUN_004728d0` | `8865` |
| 2 | `0x00470B40` | `FUN_00470b40` | `7528` |
| 3 | `0x004896E0` | `FUN_004896e0` | `6429` |
| 4 | `0x004FDE10` | `FUN_004fde10` | `5466` |
| 5 | `0x0051E4F0` | `FUN_0051e4f0` | `5099` |
| 6 | `0x005049D0` | `FUN_005049d0` | `4761` |
| 7 | `0x00507DD0` | `FUN_00507dd0` | `4001` |
| 8 | `0x00439E20` | `FUN_00439e20` | `3882` |
| 9 | `0x0048C980` | `FUN_0048c980` | `3809` |
| 10 | `0x00468030` | `FUN_00468030` | `3753` |
| 11 | `0x004872E0` | `FUN_004872e0` | `3752` |
| 12 | `0x00449000` | `FUN_00449000` | `3639` |
| 13 | `0x005181F0` | `FUN_005181f0` | `3610` |
| 14 | `0x00455E10` | `FUN_00455e10` | `3503` |
| 15 | `0x0050A1A0` | `FUN_0050a1a0` | `3327` |
| 16 | `0x004B1100` | `FUN_004b1100` | `3172` |
| 17 | `0x0048B0E0` | `FUN_0048b0e0` | `3155` |
| 18 | `0x0048BD40` | `FUN_0048bd40` | `3118` |
| 19 | `0x0044DCD0` | `FUN_0044dcd0` | `2988` |
| 20 | `0x00514550` | `FUN_00514550` | `2980` |

Refresh the queue before the next mapping pass so ties and newly resolved
aliases are handled from the current JSON corpus.
