# quakelive_steam.exe Mapping Round 134

Date: 2026-04-26

Scope: refreshed largest-unaliased queue after round 133. This pass closed the
top exact JPEG/libpng/zlib/stb/ZeroMQ candidates headed by `sub_47AE50`,
`sub_443160`, `sub_5026F0`, `sub_47C4F0`, `sub_41E460`, and `sub_41E9A0`,
then harvested the adjacent libpng row-transform helpers needed to keep the
support-library lane coherent.

## Summary

This round mapped `17` `quakelive_steam.exe` functions from the refreshed
largest-unaliased queue and nearby exact support-library neighbors.
Classification mix:

- `0` engine-owned functions
- `2` platform-service-owned functions
- `15` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

No source debt was opened. The only platform-service rows are exact libzmq
fair-queue/load-balancer helpers. Everything else in this tranche is confirmed
JPEG, libpng, zlib, or stb_truetype support code rather than retained Quake
engine reconstruction debt.

This pass intentionally left `sub_4F67A0` unresolved even though it is clearly
the CZMQ `zauth.c` request-dispatch lane, because the exact public function
name still needs a stable local source-level anchor. `sub_411F30` also remains
intentionally unresolved for the previously documented `tcp_address.cpp`
demangle mismatch reason.

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_47AE50` | `639` | CRT/STL | `process_data_context_main` | High | No engine debt; exact IJG JPEG context-row main-controller path from `jdmainct.c`. |
| 2 | `sub_443160` | `626` | CRT/STL | `stbtt_FlattenCurves` | High | No engine debt; exact stb_truetype curve flattener used by the font raster lane. |
| 3 | `sub_5026F0` | `603` | CRT/STL | `send_all_trees` | High | No engine debt; exact zlib dynamic-Huffman tree header emitter from `trees.c`. |
| 4 | `sub_47C4F0` | `588` | CRT/STL | `decompress_data` | High | No engine debt; exact IJG JPEG multi-pass coefficient-buffer output path from `jdcoefct.c`. |
| 5 | `sub_41E460` | `586` | platform-service-owned | `zmq_fq_t_recvpipe` | High | No engine debt; exact libzmq fair-queue receive helper from `fq.cpp`. |
| 6 | `sub_41E9A0` | `581` | platform-service-owned | `zmq_lb_t_sendpipe` | High | No engine debt; exact libzmq load-balancer send helper from `lb.cpp`. |
| 7 | `sub_509190` | `576` | CRT/STL | `png_do_expand_palette` | High | No engine debt; exact libpng palette expansion path from `pngrtran.c`. |
| 8 | `sub_506720` | `139` | CRT/STL | `png_do_invert` | High | No engine debt; exact libpng invert-mono transform from `pngtrans.c`. |
| 9 | `sub_5067F0` | `81` | CRT/STL | `png_do_packswap` | High | No engine debt; exact libpng packed-pixel bit-order swap helper. |
| 10 | `sub_506B00` | `227` | CRT/STL | `png_do_bgr` | High | No engine debt; exact libpng BGR channel-order swap helper. |
| 11 | `sub_506C20` | `318` | CRT/STL | `png_do_unpack` | High | No engine debt; exact libpng sub-byte unpack helper. |
| 12 | `sub_506D60` | `431` | CRT/STL | `png_do_unshift` | High | No engine debt; exact libpng significant-bit unshift helper. |
| 13 | `sub_506F40` | `77` | CRT/STL | `png_do_chop` | High | No engine debt; exact libpng strip-16-to-8 low-byte discard helper. |
| 14 | `sub_506F90` | `374` | CRT/STL | `png_do_read_swap_alpha` | High | No engine debt; exact libpng read-side alpha-position swap helper. |
| 15 | `sub_507110` | `206` | CRT/STL | `png_do_read_invert_alpha` | High | No engine debt; exact libpng read-side alpha inversion helper. |
| 16 | `sub_507510` | `437` | CRT/STL | `png_do_gray_to_rgb` | High | No engine debt; exact libpng grayscale-to-RGB expansion helper. |
| 17 | `sub_509850` | `366` | CRT/STL | `png_do_quantize` | High | No engine debt; exact libpng read-side quantize transform. |

## Evidence Notes

- `sub_47AE50` is an exact `jdmainct.c` ownership hit. The body tracks
  `context_state`, `whichptr`, `rowgroup_ctr`, `rowgroups_avail`, and
  `iMCU_row_ctr`, calls the `coef->decompress_data` callback into
  `xbuffer[whichptr]`, then falls through the same
  `CTX_POSTPONED_ROW -> CTX_PREPARE_FOR_IMCU -> CTX_PROCESS_IMCU` state
  machine as `process_data_context_main`.
- `sub_47C4F0` is an exact `jdcoefct.c` multi-pass hit. It forces
  `consume_input` while output lags input, accesses `whole_image[ci]` through
  `access_virt_barray`, skips unneeded components, runs per-block inverse DCT
  callbacks, and returns the same `JPEG_SUSPENDED`, `JPEG_ROW_COMPLETED`, and
  `JPEG_SCAN_COMPLETED` states as `decompress_data`.
- `sub_443160` exactly matches `stbtt_FlattenCurves`: it counts contours by
  `stbtt_vertex` type, allocates contour-length and point buffers, copies
  move/line vertices directly, and dispatches quadratic tessellation to the
  same helper lane used by stb_truetype.
- `sub_5026F0` is an exact zlib `trees.c` match: it sends `lcodes - 257` on
  5 bits, `dcodes - 1` on 5 bits, `blcodes - 4` on 4 bits, walks the
  `bl_order` table for 3-bit code lengths, then calls the shared `send_tree`
  helper twice.
- `sub_509190` plus its adjacent helpers are an exact libpng transform
  cluster. The body unpacks 1/2/4-bit palette indices to bytes, expands
  palette entries to RGB or RGBA using `palette` plus `trans_alpha`, and
  updates `row_info` to the same channel/rowbytes/color-type state as
  `png_do_expand_palette`.
- `sub_506720`, `sub_5067F0`, `sub_506B00`, `sub_506C20`, `sub_506D60`,
  `sub_506F40`, `sub_506F90`, `sub_507110`, `sub_507510`, and `sub_509850`
  all line up exactly with the `png_do_read_transformations` dispatch lane in
  `pngrtran.c` and `pngtrans.c`, so they were promoted together as a bounded
  support-library cluster rather than left as isolated single-function wins.
- `sub_41E460` and `sub_41E9A0` stay exact libzmq queue helpers. The former
  raises through `fq.cpp` on error, loops active pipes, returns the selected
  pipe through an out parameter, and enforces the `!more` assertion; the
  latter does the corresponding `lb.cpp` multipart-send state machine.

## Aliases Added

- `sub_41E460` -> `zmq_fq_t_recvpipe`
- `sub_41E9A0` -> `zmq_lb_t_sendpipe`
- `sub_443160` -> `stbtt_FlattenCurves`
- `sub_47AE50` -> `process_data_context_main`
- `sub_47C4F0` -> `decompress_data`
- `sub_5026F0` -> `send_all_trees`
- `sub_506720` -> `png_do_invert`
- `sub_5067F0` -> `png_do_packswap`
- `sub_506B00` -> `png_do_bgr`
- `sub_506C20` -> `png_do_unpack`
- `sub_506D60` -> `png_do_unshift`
- `sub_506F40` -> `png_do_chop`
- `sub_506F90` -> `png_do_read_swap_alpha`
- `sub_507110` -> `png_do_read_invert_alpha`
- `sub_507510` -> `png_do_gray_to_rgb`
- `sub_509190` -> `png_do_expand_palette`
- `sub_509850` -> `png_do_quantize`

## Verification

Alias artifact validation:

- `references/analysis/quakelive_symbol_aliases.json` parses through
  `python -m json.tool`
- duplicate-key scan passed after the alias update
- recount after this pass: `1525` raw alias entries, `1519` address-keyed
  aliases; six support aliases are still non-`sub_...` jump/helper names
- address-keyed coverage: `27.754%` of `5473` functions
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
| 1 | `0x00487080` | `FUN_00487080` | `597` |
| 2 | `0x004615E0` | `FUN_004615e0` | `592` |
| 3 | `0x00463670` | `FUN_00463670` | `592` |
| 4 | `0x00463980` | `FUN_00463980` | `592` |
| 5 | `0x004A9C50` | `FUN_004a9c50` | `587` |
| 6 | `0x004BE8A0` | `FUN_004be8a0` | `587` |
| 7 | `0x004C9860` | `FUN_004c9860` | `587` |
| 8 | `0x004F67A0` | `FUN_004f67a0` | `581` |
| 9 | `0x00411F30` | `FUN_00411f30` | `580` |
| 10 | `0x004CF0D0` | `FUN_004cf0d0` | `580` |
| 11 | `0x0046C5C0` | `FUN_0046c5c0` | `575` |
| 12 | `0x00492CD0` | `FUN_00492cd0` | `575` |
| 13 | `0x00493420` | `FUN_00493420` | `575` |
| 14 | `0x004A0CD0` | `FUN_004a0cd0` | `573` |
| 15 | `0x00430AB0` | `FUN_00430ab0` | `572` |
| 16 | `0x004B6330` | `FUN_004b6330` | `570` |
| 17 | `0x0049D180` | `FUN_0049d180` | `568` |
| 18 | `0x004BFF10` | `FUN_004bff10` | `568` |
| 19 | `0x00414050` | `FUN_00414050` | `566` |
| 20 | `0x00435070` | `FUN_00435070` | `566` |

Refresh the queue before the next mapping pass so ties and newly resolved
aliases are handled from the current JSON corpus.
