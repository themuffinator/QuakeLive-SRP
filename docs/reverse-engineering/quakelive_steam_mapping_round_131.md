# quakelive_steam.exe Mapping Round 131

Date: 2026-04-26

Scope: corrected refreshed largest-unaliased queue after round 130. This pass
recomputed the queue with normalized integer address matching between
`functions.csv` entries and `sub_...` alias keys, then started from the true
queue head: `sub_515250`, `sub_47AE50`, and `sub_51D0A0`.

## Summary

This round mapped `14` `quakelive_steam.exe` functions from the corrected
refreshed queue and one adjacent render helper that became exact while
resolving the renderer state cluster. Classification mix:

- `8` engine-owned functions
- `1` platform-service-owned function
- `6` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

No source debt was opened. Engine-owned rows land in checked-in renderer,
client, common, and Win32 owners. The single platform-service row stays in the
bundled ZeroMQ host/runtime lane. The remaining rows belong to libpng, libvorbis
MDCT support, and STL container scaffolding rather than Quake engine source
debt.

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_515250` | `643` | CRT/STL | `png_do_shift` | High | No engine debt; libpng write-transform bit-depth shifter with the exact grayscale/color-channel masks and per-channel shift tables. |
| 2 | `sub_506230` | `636` | CRT/STL | `png_read_destroy` | High | No engine debt; libpng read-side teardown that frees read buffers, gamma tables, palettes, alpha tables, and resets the struct before outer destruction. |
| 3 | `sub_5206A0` | `627` | CRT/STL | `mdct_forward` | High | No engine debt; libvorbis MDCT forward transform immediately adjacent to the already-mapped `mdct_backward`. |
| 4 | `sub_435980` | `626` | engine-owned | `GL_State` | High | Source owner exists in renderer `tr_backend.c`; exact GL blend/depth/cull state setter with retained diagnostic strings. |
| 5 | `sub_4BD790` | `622` | engine-owned | `CL_ParseGamestate` | High | Source owner exists in client `cl_parse.c`; configstring/baseline/gamestate parser with the exact bad-command and overflow guards. |
| 6 | `sub_4500B0` | `614` | engine-owned | `RBPP_CreateRenderTarget` | High | Source owner exists in renderer `tr_backend.c`; post-process FBO/texture render-target creator. |
| 7 | `sub_41BEB0` | `613` | platform-service-owned | `zmq_session_base_t_attach_pipe` | High | No engine debt; exact libzmq session pipe-attach path from `session_base.cpp`. |
| 8 | `sub_4BE110` | `613` | engine-owned | `SCR_DrawScreenField` | High | Source owner exists in client `cl_scrn.c`; exact screen-field dispatcher with UI/WebHost gating. |
| 9 | `sub_514200` | `611` | CRT/STL | `png_write_finish_row` | High | No engine debt; libpng row/pass finalizer for write-side interlace progression and final zlib flush. |
| 10 | `sub_4EB830` | `609` | engine-owned | `IN_RawInputMouse` | High | Source owner exists in `win_input.c`; raw-input mouse accumulation and queued event path. |
| 11 | `sub_416020` | `607` | CRT/STL | `std_tree_erase_zmq_out_pipe_node_iter` | Medium-high | No engine debt; STL map erase helper used by libzmq routing-socket outbound-pipe teardown. |
| 12 | `sub_41CA80` | `607` | CRT/STL | `std_tree_erase_zmq_timer_node_iter` | Medium-high | No engine debt; STL multimap erase helper used by libzmq poller timer cancellation/execution. |
| 13 | `sub_435D90` | `607` | engine-owned | `RB_BeginDrawingView` | High | Source owner exists in renderer `tr_backend.c`; view-begin path with fastsky clear, portal clip-plane, and hyperspace handling. |
| 14 | `sub_4C8C00` | `607` | engine-owned | `Com_Filter` | High | Source owner exists in common/shared code; wildcard matcher immediately adjacent to the already-mapped `Com_FilterPath`. |
| 15 | `sub_435D20` | `99` | engine-owned | `SetViewportAndScissor` | High | Adjacent exact helper from the same render-state cluster; no new debt. |

## Evidence Notes

- The refreshed queue from round 130 was stale because Ghidra `entry` values
  such as `004728d0` were being compared to alias keys such as
  `sub_4728D0` without normalizing leading zeroes. This round fixed the queue
  recomputation by comparing integer addresses on both sides.
- The renderer quartet resolved as a single exact cluster against
  `src/code/renderer/tr_backend.c`: `GL_State`, `SetViewportAndScissor`,
  `RB_BeginDrawingView`, and `RBPP_CreateRenderTarget`.
- The client/common exacts were similarly straightforward against checked-in
  source: `CL_ParseGamestate`, `SCR_DrawScreenField`, `Com_Filter`, and
  `IN_RawInputMouse`.
- `sub_41BEB0` is an exact libzmq ownership hit from `session_base.cpp`:
  the asserts, `_pipe` assignment, endpoint-pair propagation, and engine attach
  path all line up with `zmq::session_base_t::attach_pipe`.
- `sub_416020` and `sub_41CA80` remain in the support-library lane. Their
  callers, retained assertion strings, and upstream headers identify them as
  STL erase helpers for libzmq `out_pipes_t` and `timers_t` containers.
- The libpng tranche is exact:
  - `png_read_destroy` from `pngread.c`
  - `png_write_finish_row` from `pngwutil.c`
  - `png_do_shift` from `pngwtran.c`
- The Vorbis mapping is exact as well: `sub_5206A0` is `mdct_forward`, paired
  with the already-mapped `mdct_backward`.

## Aliases Added

- `sub_416020` -> `std_tree_erase_zmq_out_pipe_node_iter`
- `sub_41BEB0` -> `zmq_session_base_t_attach_pipe`
- `sub_41CA80` -> `std_tree_erase_zmq_timer_node_iter`
- `sub_435980` -> `GL_State`
- `sub_435D20` -> `SetViewportAndScissor`
- `sub_435D90` -> `RB_BeginDrawingView`
- `sub_4500B0` -> `RBPP_CreateRenderTarget`
- `sub_4BD790` -> `CL_ParseGamestate`
- `sub_4BE110` -> `SCR_DrawScreenField`
- `sub_4C8C00` -> `Com_Filter`
- `sub_4EB830` -> `IN_RawInputMouse`
- `sub_506230` -> `png_read_destroy`
- `sub_514200` -> `png_write_finish_row`
- `sub_515250` -> `png_do_shift`
- `sub_5206A0` -> `mdct_forward`

## Verification

Alias artifact validation:

- `references/analysis/quakelive_symbol_aliases.json` parses through
  `python -m json.tool`
- duplicate-key scan passed after the alias update
- recount after this pass: `1460` raw alias entries, `1454` address-keyed
  aliases; six support aliases are still non-`sub_...` jump/helper names
- address-keyed coverage: `26.567%` of `5473` functions
- no game/runtime launch was performed; this was a static mapping pass

Parity estimate after this mapping-only pass remains unchanged:

- strict-retail Windows replacement target: `100%` before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

After this round, the corrected refreshed largest-unaliased queue begins with:

| # | Address | Ghidra name | Size |
| ---: | --- | --- | ---: |
| 1 | `0x0047AE50` | `FUN_0047ae50` | `639` |
| 2 | `0x0051D0A0` | `FUN_0051d0a0` | `639` |
| 3 | `0x00443160` | `FUN_00443160` | `626` |
| 4 | `0x00515EC0` | `FUN_00515ec0` | `624` |
| 5 | `0x00501850` | `FUN_00501850` | `617` |
| 6 | `0x004CA4E0` | `FUN_004ca4e0` | `609` |
| 7 | `0x00491EA0` | `FUN_00491ea0` | `606` |
| 8 | `0x00510630` | `FUN_00510630` | `606` |
| 9 | `0x00504750` | `FUN_00504750` | `604` |
| 10 | `0x005026F0` | `FUN_005026f0` | `603` |
| 11 | `0x004374B0` | `FUN_004374b0` | `602` |
| 12 | `0x00510EC0` | `FUN_00510ec0` | `599` |
| 13 | `0x004ED830` | `FUN_004ed830` | `598` |
| 14 | `0x00487080` | `FUN_00487080` | `597` |
| 15 | `0x0040C200` | `FUN_0040c200` | `595` |
| 16 | `0x004615E0` | `FUN_004615e0` | `592` |
| 17 | `0x00463670` | `FUN_00463670` | `592` |
| 18 | `0x00463980` | `FUN_00463980` | `592` |
| 19 | `0x0047C4F0` | `FUN_0047c4f0` | `588` |
| 20 | `0x004A9C50` | `FUN_004a9c50` | `587` |

Refresh the queue before the next mapping pass so ties and newly resolved
aliases are handled from the current JSON corpus.
