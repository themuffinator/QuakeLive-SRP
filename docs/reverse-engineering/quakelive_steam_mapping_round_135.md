# quakelive_steam.exe Mapping Round 135

Date: 2026-04-26

Scope: refreshed largest-unaliased queue after round 134. This pass resolved
the top exact engine/libzmq/json/libpng candidates headed by `sub_487080`,
`sub_4A9C50`, `sub_4BE8A0`, `sub_4C9860`, and `sub_4CF0D0`, then harvested
the adjacent botlib, renderer, input, collision-model, and support-library
neighbors needed to keep the queue coherent.

## Summary

This round mapped `16` `quakelive_steam.exe` functions from the refreshed
largest-unaliased queue and nearby exact neighbors. Classification mix:

- `12` engine-owned functions
- `2` platform-service-owned functions
- `2` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

No source debt was opened. This tranche is dominated by exact botlib, client,
renderer, and qcommon source owners, with one bounded JsonCpp helper, one
bounded libpng helper, and a small exact libzmq REQ/socket-base pair.

This pass intentionally left `sub_4615E0`, `sub_463670`, and `sub_463980`
unaliased even though their ownership is now clear: all three are compiler STL
red-black-tree iterator-erase helpers. The remaining instability is the exact
container/type naming, and I did not want to bake speculative support-library
names into the corpus. `sub_4F67A0` and `sub_411F30` also remain intentionally
unresolved for the previously documented CZMQ and `tcp_address.cpp` reasons.

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_487080` | `597` | engine-owned | `AAS_ClipToBBox` | High | No engine debt; exact botlib client-movement bbox clip helper from `be_aas_move.c`. |
| 2 | `sub_4A9C50` | `587` | engine-owned | `PC_Directive_include` | High | No engine debt; exact botlib preprocessor `#include` directive handler from `l_precomp.c`. |
| 3 | `sub_4BE8A0` | `587` | engine-owned | `LAN_GetServerInfo` | High | No engine debt; exact client server-browser info-string builder from `cl_ui.c`. |
| 4 | `sub_4C9860` | `587` | engine-owned | `Com_Printf` | High | No engine debt; exact common varargs console/log print path from `common.c`. |
| 5 | `sub_4CF0D0` | `580` | engine-owned | `FS_SV_FOpenFileRead` | High | No engine debt; exact server-side filesystem open helper from `files.c`. |
| 6 | `sub_46C5C0` | `575` | engine-owned | `PrimToString` | High | No engine debt; exact GL primitive-name formatter used by `win_qgl.c` logging. |
| 7 | `sub_492CD0` | `575` | engine-owned | `AAS_CalculateAreaTravelTimes` | High | No engine debt; exact botlib area-travel-time precompute from `be_aas_route.c`. |
| 8 | `sub_493420` | `575` | engine-owned | `AAS_WriteRouteCache` | High | No engine debt; exact botlib `.rcd` route-cache writer from `be_aas_route.c`. |
| 9 | `sub_430AB0` | `572` | CRT/STL | `JsonStyledWriter_isMultineArray` | Medium-high | No engine debt; exact JsonCpp styled-writer multiline-array heuristic. |
| 10 | `sub_4B6330` | `570` | engine-owned | `CL_InitInput` | High | No engine debt; exact client input command/cvar registration path from `cl_input.c`. |
| 11 | `sub_49D180` | `568` | engine-owned | `BotInitInfoEntities` | High | No engine debt; exact botlib map-location/camp-spot loader from `be_ai_goal.c`. |
| 12 | `sub_4BFF10` | `568` | engine-owned | `CMod_LoadPatches` | High | No engine debt; exact collision-model patch loader from `cm_load.c`. |
| 13 | `sub_414050` | `566` | platform-service-owned | `zmq_req_t_xrecv` | High | No engine debt; exact libzmq REQ receive-state machine from `req.cpp`. |
| 14 | `sub_43BCB0` | `565` | engine-owned | `R_LoadEntities` | High | No engine debt; exact renderer worldspawn/entity-string parser from `tr_bsp.c`. |
| 15 | `sub_50C140` | `564` | CRT/STL | `png_write_start_row` | Medium-high | No engine debt; exact libpng write-row startup/row-buffer initializer. |
| 16 | `sub_4074C0` | `563` | platform-service-owned | `zmq_socket_base_t_ctor` | High | No engine debt; exact libzmq socket-base constructor used by derived socket ctors. |

## Evidence Notes

- `sub_487080` is an exact `AAS_ClipToBBox` hit. The body computes the
  presence-type-expanded bbox, rejects segments fully outside it, finds the
  first plane intersection fraction, writes trace-style `fraction/endpos`
  output, and is called from the already-mapped `AAS_ClientMovementPrediction`
  bounding-box stop-event path.
- `sub_492CD0` and `sub_493420` are an exact botlib route-cache cluster.
  `sub_492CD0` frees and rebuilds the three-level `areatraveltimes` table from
  reversed reachability links, while `sub_493420` writes the `"maps/%s.rcd"`
  header and cache chains with the matching route-cache version/CRC layout from
  `be_aas_route.c`.
- `sub_49D180` is an exact `BotInitInfoEntities` match. It walks BSP entities,
  filters `target_location` and `info_camp`, reads `origin/message/range`
  fields, validates camp spots with `AAS_PointAreaNum`, and prints the same
  `%d map locations` / `%d camp spots` developer counters.
- `sub_4A9C50` is an exact `PC_Directive_include` match. The body emits the
  same `#include without file name`, `#include missing trailing >`, and
  `< >` filename diagnostics, then pushes the loaded script through the same
  include-path fallback flow as `l_precomp.c`.
- `sub_4BE8A0` is an exact `LAN_GetServerInfo` match. The source switch across
  local/mplayer/global/favorites arrays, info-string key fanout
  (`hostname/mapname/clients/sv_maxclients/ping/.../addr`), and final
  `Q_strncpyz` copy all line up directly with `cl_ui.c`.
- `sub_4C9860` is the common print sink, not just a formatting helper. The
  body `_vsnprintf`s into the local buffer, fans out into console history and
  logfile state, and is called from the same FS/client/server/cvar print sites
  that source routes through `Com_Printf`.
- `sub_4CF0D0` and `sub_4BFF10` are exact qcommon load paths. The first opens
  through `fs_homepath`, `fs_basepath`, then `fs_cdpath` with the matching
  `FS_SV_FOpenFileRead` debug prints; the second validates patch and drawvert
  lump sizes, enforces `MAX_PATCH_VERTS`, and builds `cPatch_t` entries through
  the exact `CMod_LoadPatches` loop.
- `sub_43BCB0` and `sub_46C5C0` are exact checked-in renderer/win32 helpers:
  `R_LoadEntities` parses only worldspawn keys `vertexremapshader`,
  `remapshader`, and `gridsize`, while `PrimToString` maps GL primitive enums
  to the logging strings from `win_qgl.c`.
- `sub_414050` and `sub_4074C0` are exact libzmq names. `sub_414050` carries
  the REQ receive-state assertions against `..\..\..\src\req.cpp`, drains the
  fair queue until the active reply pipe matches, and clears the reply state on
  the final frame. `sub_4074C0` installs the `socket_base_t` vtables, builds
  the internal pipe containers, initializes timing/critical-section state, and
  is called by derived socket constructors.
- `sub_430AB0` is the JsonCpp `StyledWriter` multiline-array heuristic. The
  body counts child elements, inspects child value types/comments/inline sizes,
  and rejects inline layout when the rendered width crosses the writer margin.
- `sub_50C140` is the exact libpng row-startup path immediately after
  `png_write_info`: it validates transform/interlace state, computes
  `pixel_depth` and rowbytes, allocates the row buffers, enables interlace
  compaction when needed, and primes the later `png_write_find_filter` lane.
- `sub_4615E0`, `sub_463670`, and `sub_463980` are now classified as
  CRT/STL-support red-black-tree iterator erasers by their
  `invalid map/set<T> iterator` guard strings, sentinel-byte layouts, and
  rebalance/delete structure, but they remain intentionally unnamed until the
  exact owning container types are anchored locally.

## Aliases Added

- `sub_4074C0` -> `zmq_socket_base_t_ctor`
- `sub_414050` -> `zmq_req_t_xrecv`
- `sub_430AB0` -> `JsonStyledWriter_isMultineArray`
- `sub_43BCB0` -> `R_LoadEntities`
- `sub_46C5C0` -> `PrimToString`
- `sub_487080` -> `AAS_ClipToBBox`
- `sub_492CD0` -> `AAS_CalculateAreaTravelTimes`
- `sub_493420` -> `AAS_WriteRouteCache`
- `sub_49D180` -> `BotInitInfoEntities`
- `sub_4A9C50` -> `PC_Directive_include`
- `sub_4B6330` -> `CL_InitInput`
- `sub_4BE8A0` -> `LAN_GetServerInfo`
- `sub_4BFF10` -> `CMod_LoadPatches`
- `sub_4C9860` -> `Com_Printf`
- `sub_4CF0D0` -> `FS_SV_FOpenFileRead`
- `sub_50C140` -> `png_write_start_row`

## Verification

Alias artifact validation:

- `references/analysis/quakelive_symbol_aliases.json` parses through
  `python -m json.tool`
- duplicate-key scan passed after the alias update
- recount after this pass: `1541` raw alias entries, `1535` address-keyed
  aliases; six support aliases are still non-`sub_...` jump/helper names
- address-keyed coverage: `28.047%` of `5473` functions
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
| 1 | `0x004615E0` | `FUN_004615e0` | `592` |
| 2 | `0x00463670` | `FUN_00463670` | `592` |
| 3 | `0x00463980` | `FUN_00463980` | `592` |
| 4 | `0x004F67A0` | `FUN_004f67a0` | `581` |
| 5 | `0x00411F30` | `FUN_00411f30` | `580` |
| 6 | `0x004A0CD0` | `FUN_004a0cd0` | `573` |
| 7 | `0x00435070` | `FUN_00435070` | `566` |
| 8 | `0x0047F600` | `FUN_0047f600` | `564` |
| 9 | `0x004AD4F0` | `FUN_004ad4f0` | `564` |
| 10 | `0x0042D770` | `FUN_0042d770` | `562` |
| 11 | `0x00440AD0` | `FUN_00440ad0` | `560` |
| 12 | `0x004109D0` | `FUN_004109d0` | `559` |
| 13 | `0x004124E0` | `FUN_004124e0` | `559` |
| 14 | `0x004C6BD0` | `FUN_004c6bd0` | `558` |
| 15 | `0x004A9570` | `FUN_004a9570` | `556` |
| 16 | `0x00523570` | `FUN_00523570` | `556` |
| 17 | `0x0040B050` | `FUN_0040b050` | `555` |
| 18 | `0x00419AD0` | `FUN_00419ad0` | `555` |
| 19 | `0x0049A160` | `FUN_0049a160` | `553` |
| 20 | `0x00413400` | `FUN_00413400` | `552` |

Refresh the queue before the next mapping pass so tie ordering and any newly
stabilized STL/Awesomium/support-library rows are taken from the live JSON
corpus instead of the previous round snapshot.
