# quakelive_steam.exe Mapping Round 143

Date: 2026-04-27

Scope: refreshed largest-unaliased queue after round 142. This pass consumed
the long-deferred SteamID STL queue head at `sub_463980` and promoted the
adjacent shared helper families around `sub_463C20`, `sub_467510`, and
`sub_467C50`.

## Summary

This round mapped `14` `quakelive_steam.exe` functions from the refreshed
largest-unaliased queue and exact adjacent support-library neighbors.
Classification mix:

- `0` engine-owned functions
- `0` platform-service-owned functions
- `14` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

No source debt was opened. This tranche stays entirely inside retained MSVC
STL support: the missing lower-bound/find/clear/insert helpers for the shared
`0x21` SteamID map family, plus the previously deferred `0x15` SteamID-to-value
tree reused by both `SteamDataSource` pending avatar requests and the Steam
stats player-session cache.

This round also closes the previously bounded `sub_463980` ownership/name gap.
The new generic `steamid_value_*` aliases intentionally describe what the
second tree actually stores: a SteamID key plus one mapped machine-word value
slot, not a browser-only or stats-only owner.

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_463980` | `592` | CRT/STL | `std_tree_erase_steamid_value_node_iter` | Medium-high | No engine debt; exact iterator-erase helper for the second SteamID keyed value tree. |
| 2 | `sub_463C20` | `268` | CRT/STL | `std_tree_insert_steamid_map_node` | High | No engine debt; exact unique-insert wrapper over the already-mapped `std_tree_insert_steamid_map_node_rebalance`. |
| 3 | `sub_463D30` | `77` | CRT/STL | `std_tree_clear_steamid_value_map` | Medium-high | No engine debt; exact clear/reset wrapper for the second SteamID keyed value tree. |
| 4 | `sub_463D80` | `403` | CRT/STL | `std_tree_insert_steamid_value_node` | Medium-high | No engine debt; exact unique-insert wrapper for the second SteamID keyed value tree, with fast-path hint checks before the fallback insert walk. |
| 5 | `sub_463FC0` | `158` | CRT/STL | `std_tree_erase_steamid_value_node` | Medium-high | No engine debt; exact range-erase wrapper for the second SteamID keyed value tree. |
| 6 | `sub_465EB0` | `170` | CRT/STL | `std_tree_equal_range_steamid_node` | High | No engine debt; exact equal-range helper for the SteamID set family used by auth-session ownership. |
| 7 | `sub_465F60` | `110` | CRT/STL | `std_tree_create_steamid_node` | High | No engine debt; exact SteamID set-node allocator/initializer beneath the already-mapped insert helpers. |
| 8 | `sub_467510` | `65` | CRT/STL | `std_tree_lower_bound_steamid_map_node` | High | No engine debt; exact lower-bound tree walk for the shared SteamID map family. |
| 9 | `sub_467A20` | `56` | CRT/STL | `std_tree_destroy_steamid_map_subtree` | High | No engine debt; exact recursive subtree-destroy helper for the shared SteamID map family. |
| 10 | `sub_467A60` | `83` | CRT/STL | `std_tree_find_steamid_map_node` | High | No engine debt; exact find helper built on the lower-bound walk with an end-node fallback. |
| 11 | `sub_467AC0` | `77` | CRT/STL | `std_tree_clear_steamid_map` | High | No engine debt; exact clear/reset wrapper for the shared SteamID map family. |
| 12 | `sub_467BD0` | `116` | CRT/STL | `std_tree_create_steamid_value_node` | Medium-high | No engine debt; exact allocator/initializer for the second SteamID keyed value-tree nodes. |
| 13 | `sub_467C50` | `113` | CRT/STL | `std_tree_find_or_insert_steamid_value_node` | Medium-high | No engine debt; exact helper that returns the mapped value slot after either finding or inserting the SteamID key. |
| 14 | `sub_463BE0` | `56` | CRT/STL | `std_tree_destroy_steamid_value_subtree` | Medium-high | No engine debt; exact recursive subtree-destroy helper for the second SteamID keyed value tree. |

## Evidence Notes

- `sub_463C20`, `sub_467510`, `sub_467A20`, `sub_467A60`, and
  `sub_467AC0` close the remaining generic `0x21` SteamID map helpers that
  sit beside the already-mapped `std_tree_insert_steamid_map_node_rebalance`,
  `std_tree_equal_range_steamid_map_node`,
  `std_tree_erase_steamid_map_node_iter`, and
  `std_tree_erase_steamid_map_node`. The lower-bound walk in `sub_467510`,
  the exact-match gate in `sub_467A60`, the duplicate-reject path in
  `sub_463C20`, and the recursive clear/reset split in
  `sub_467A20` / `sub_467AC0` all match the retained MSVC tree helper shapes
  directly.
- `sub_465EB0` and `sub_465F60` close the adjacent SteamID set support that
  remained unnamed after round 137. `sub_465EB0` is the same pair-returning
  equal-range walk pattern already landed for the map family, but with the
  `0x19` sentinel layout used by Steam auth-session ownership. `sub_465F60`
  is the corresponding node constructor: it allocates `0x20` bytes, wires the
  parent/left/right links to the tree sentinel, clears the color/state field,
  and copies the two-dword SteamID key.
- The previously deferred `sub_463980`, `sub_463BE0`, `sub_463D30`,
  `sub_463D80`, `sub_463FC0`, `sub_467BD0`, and `sub_467C50` now have a
  stable generic owner name because the call graph proves the second tree is
  not browser-only. `sub_4640C0 -> SteamDataSource_OnRequest` inserts a
  pending avatar-request owner into `arg1 + 0xc`; `sub_464290 ->
  SteamDataSource_OnAvatarImageLoaded` looks up that same key, erases the
  node, and forwards the stored mapped value to
  `SteamDataSource_StartResponseThread`; and `sub_467CD0 ->
  SteamStats_CreatePlayerSession` uses the same `sub_467C50` helper against
  `data_e30390` to store a per-player session pointer. The shared node
  constructor `sub_467BD0` copies the two-dword SteamID key plus one mapped
  word initialized to zero, so `steamid_value_node` is the least misleading
  durable alias family for the whole lane.
- `sub_463980` is therefore the exact iterator-erase counterpart for that
  second value-tree family, and `sub_463FC0` is its range-erase wrapper. The
  bodies mirror the already-mapped `std_tree_erase_steamid_node_iter` and
  `std_tree_erase_steamid_map_node_iter` logic, but they operate on the
  distinct `0x15` sentinel layout and the `sub_463D30` clear-all fast path.

## Aliases Added

- `sub_463BE0` -> `std_tree_destroy_steamid_value_subtree`
- `sub_463C20` -> `std_tree_insert_steamid_map_node`
- `sub_463D30` -> `std_tree_clear_steamid_value_map`
- `sub_463D80` -> `std_tree_insert_steamid_value_node`
- `sub_463980` -> `std_tree_erase_steamid_value_node_iter`
- `sub_463FC0` -> `std_tree_erase_steamid_value_node`
- `sub_465EB0` -> `std_tree_equal_range_steamid_node`
- `sub_465F60` -> `std_tree_create_steamid_node`
- `sub_467510` -> `std_tree_lower_bound_steamid_map_node`
- `sub_467A20` -> `std_tree_destroy_steamid_map_subtree`
- `sub_467A60` -> `std_tree_find_steamid_map_node`
- `sub_467AC0` -> `std_tree_clear_steamid_map`
- `sub_467BD0` -> `std_tree_create_steamid_value_node`
- `sub_467C50` -> `std_tree_find_or_insert_steamid_value_node`

## Verification

Alias artifact validation:

- `references/analysis/quakelive_symbol_aliases.json` parses through
  `python -m json.tool`
- duplicate-key scan passed after the alias update
- recount after this pass: `1648` raw alias entries, `1577` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `28.814%` of `5473` functions
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
| 1 | `0x00435070` | `FUN_00435070` | `566` |
| 2 | `0x00440AD0` | `FUN_00440ad0` | `560` |
| 3 | `0x004C6BD0` | `FUN_004c6bd0` | `558` |
| 4 | `0x0040B050` | `FUN_0040b050` | `555` |
| 5 | `0x00419AD0` | `FUN_00419ad0` | `555` |
| 6 | `0x0040F7E0` | `FUN_0040f7e0` | `549` |
| 7 | `0x0041CFB0` | `FUN_0041cfb0` | `549` |
| 8 | `0x0042BA60` | `FUN_0042ba60` | `549` |
| 9 | `0x004940D0` | `FUN_004940d0` | `547` |
| 10 | `0x004F4410` | `FUN_004f4410` | `546` |

The next pass should return to `sub_435070`, `sub_440AD0`, and
`sub_4C6BD0`, then keep working down the remaining top queue while preserving
the existing classification guardrails on unresolved engine, platform-service,
and support-library rows.
