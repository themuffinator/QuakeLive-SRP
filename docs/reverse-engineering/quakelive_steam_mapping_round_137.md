# quakelive_steam.exe Mapping Round 137

Date: 2026-04-26

Scope: refreshed largest-unaliased queue after round 136. This pass consumed
the queue-head shared SteamID STL helpers around `sub_4615E0` and
`sub_463670`, then harvested the adjacent IJG/libjpeg marker-reader lane
headed by `sub_47F600`.

## Summary

This round mapped `15` `quakelive_steam.exe` functions from the refreshed
largest-unaliased queue and nearby exact support-library neighbors.
Classification mix:

- `0` engine-owned functions
- `0` platform-service-owned functions
- `15` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

No source debt was opened. This tranche is entirely support code: generic
MSVC STL tree helpers shared by SteamID-keyed host containers, plus an exact
IJG/libjpeg marker-reader cluster.

This pass intentionally left `sub_463980` unresolved because the second
`SteamDataSource` `0x15`-layout tree still lacks a stable, specific owner
name. I also left `sub_4F67A0` unresolved for the previously documented
`zauth.c` source-anchor reason, and `sub_4109D0` unresolved pending one more
exact `pipe.cpp` public-name verification pass.

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_4615E0` | `592` | CRT/STL | `std_tree_erase_steamid_node_iter` | Medium-high | No engine debt; shared MSVC red-black-tree iterator erase helper reused by Steam voice mute/auth-session SteamID sets. |
| 2 | `sub_463670` | `592` | CRT/STL | `std_tree_erase_steamid_map_node_iter` | Medium-high | No engine debt; shared MSVC red-black-tree iterator erase helper reused by Steam stats and SteamDataSource SteamID maps. |
| 3 | `sub_47F600` | `564` | CRT/STL | `get_dqt` | High | No engine debt; exact IJG/libjpeg DQT marker parser from `jdmarker.c`. |
| 4 | `sub_461880` | `268` | CRT/STL | `std_tree_insert_steamid_node` | Medium-high | No engine debt; shared MSVC red-black-tree insert helper for SteamID-keyed set containers. |
| 5 | `sub_47F840` | `252` | CRT/STL | `get_dri` | High | No engine debt; exact IJG/libjpeg DRI marker parser from `jdmarker.c`. |
| 6 | `sub_47F9F0` | `282` | CRT/STL | `next_marker` | High | No engine debt; exact IJG/libjpeg next-marker scanner with discarded-byte warning path. |
| 7 | `sub_47F940` | `172` | CRT/STL | `skip_variable` | High | No engine debt; exact IJG/libjpeg variable-length marker skip helper. |
| 8 | `sub_47FB10` | `168` | CRT/STL | `first_marker` | High | No engine debt; exact IJG/libjpeg SOI bootstrap marker reader. |
| 9 | `sub_47FBC0` | `144` | CRT/STL | `read_markers` | High | No engine debt; exact IJG/libjpeg marker dispatch loop. |
| 10 | `sub_47FFA0` | `143` | CRT/STL | `read_restart_marker` | High | No engine debt; exact IJG/libjpeg restart-marker recovery entrypoint. |
| 11 | `sub_480250` | `52` | CRT/STL | `reset_marker_reader` | High | No engine debt; exact IJG/libjpeg marker-reader state reset helper. |
| 12 | `sub_480290` | `173` | CRT/STL | `jinit_marker_reader` | High | No engine debt; exact IJG/libjpeg marker-reader vtable/init constructor. |
| 13 | `sub_461CA0` | `158` | CRT/STL | `std_tree_erase_steamid_node` | Medium-high | No engine debt; shared MSVC red-black-tree range erase wrapper for SteamID-keyed set containers. |
| 14 | `sub_4638D0` | `170` | CRT/STL | `std_tree_equal_range_steamid_map_node` | Medium-high | No engine debt; shared MSVC red-black-tree equal-range helper for SteamID-keyed map containers. |
| 15 | `sub_463F20` | `158` | CRT/STL | `std_tree_erase_steamid_map_node` | Medium-high | No engine debt; shared MSVC red-black-tree range erase wrapper for SteamID-keyed map containers. |

## Evidence Notes

- `sub_4615E0`, `sub_461880`, and `sub_461CA0` are now stable as generic
  SteamID set helpers. The `invalid map/set<T> iterator` guard, the shared
  `0x19` sentinel-byte layout, and direct callers in
  `SteamVoice_ToggleClientMute`, `SteamServer_EndAuthSession`, and the Steam
  auth cleanup lane show that these helpers are reused across multiple
  `CSteamID`-keyed set containers, so the generic `steamid_node` naming is the
  least misleading stable promotion.
- `sub_463670`, `sub_4638D0`, and `sub_463F20` are the matching generic
  SteamID map helpers. They are shared between
  `SteamStats_RemovePlayerSession` and the `SteamDataSource` avatar-request
  map at `arg1 + 0xc`, so I promoted them as generic
  `steamid_map_node` helpers rather than falsely pinning them to just Steam
  stats or just browser-host ownership.
- `sub_463980` remains intentionally unresolved. Its `0x15` sentinel-byte
  tree is clearly support-library STL and clearly owned by `SteamDataSource`
  lifecycle code, but the exact container role inside that second browser-host
  tree is not yet anchored tightly enough for a durable public alias.
- `sub_47F600` is the exact `get_dqt` parser. The body reads the DQT info
  byte as `prec` plus table index, allocates `quant_tbl_ptrs[n]` when needed,
  reads `DCTSIZE2` one- or two-byte quantization entries, and emits the same
  eight-value `JTRC_QUANTVALS` trace blocks as `jdmarker.c`.
- `sub_47F840`, `sub_47F940`, `sub_47F9F0`, `sub_47FB10`, `sub_47FBC0`,
  `sub_47FFA0`, `sub_480250`, and `sub_480290` close the surrounding marker
  lane exactly. The restart-interval length check, variable-marker length
  skip, discarded-byte warning loop, strict SOI bootstrap check, marker
  dispatch switch, restart-marker resync path, reset-state zeroing, and
  marker-reader initialization table all line up directly with the checked-in
  IJG source in `jdmarker.c`.
- `sub_4F67A0` remains classified as platform-service-owned CZMQ auth/ZAP
  dispatch, and `sub_4109D0` remains classified as platform-service-owned
  libzmq `pipe.cpp` termination support, but neither exact public name is
  stable enough yet to promote in this round.

## Aliases Added

- `sub_4615E0` -> `std_tree_erase_steamid_node_iter`
- `sub_461880` -> `std_tree_insert_steamid_node`
- `sub_461CA0` -> `std_tree_erase_steamid_node`
- `sub_463670` -> `std_tree_erase_steamid_map_node_iter`
- `sub_4638D0` -> `std_tree_equal_range_steamid_map_node`
- `sub_463F20` -> `std_tree_erase_steamid_map_node`
- `sub_47F600` -> `get_dqt`
- `sub_47F840` -> `get_dri`
- `sub_47F940` -> `skip_variable`
- `sub_47F9F0` -> `next_marker`
- `sub_47FB10` -> `first_marker`
- `sub_47FBC0` -> `read_markers`
- `sub_47FFA0` -> `read_restart_marker`
- `sub_480250` -> `reset_marker_reader`
- `sub_480290` -> `jinit_marker_reader`

## Verification

Alias artifact validation:

- `references/analysis/quakelive_symbol_aliases.json` parses through
  `python -m json.tool`
- duplicate-key scan passed after the alias update
- recount after this pass: `1563` raw alias entries, `1557` address-keyed
  aliases
- address-keyed coverage: `28.449%` of `5473` functions
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
| 7 | `0x00523570` | `FUN_00523570` | `556` |
| 8 | `0x0040B050` | `FUN_0040b050` | `555` |
| 9 | `0x00419AD0` | `FUN_00419ad0` | `555` |
| 10 | `0x00413400` | `FUN_00413400` | `552` |

The next pass should start with `sub_463980`, `sub_4F67A0`, and
`sub_435070`, keeping the existing classification guardrails on the remaining
platform-service and unanchored engine/support rows before any new debt is
opened.
