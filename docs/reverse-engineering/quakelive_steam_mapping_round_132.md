# quakelive_steam.exe Mapping Round 132

Date: 2026-04-26

Scope: refreshed largest-unaliased queue after round 131. This pass continued
from the corrected queue head, then harvested adjacent exact matches from the
same zlib, libpng, libvorbis, engine, and ZeroMQ evidence clusters.

## Summary

This round mapped `23` `quakelive_steam.exe` functions from the refreshed
largest-unaliased queue and nearby exact support-library neighbors.
Classification mix:

- `5` engine-owned functions
- `1` platform-service-owned function
- `17` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

No source debt was opened. The engine-owned rows already have checked-in
owners in renderer, botlib, common, and Win32 startup code. The single
platform-service row stays in the bundled ZeroMQ host/runtime lane. The
remaining wins belong to zlib, libpng, and libvorbis support code rather than
Quake engine reconstruction debt.

This round also corrected one stale support-library alias:
`sub_501AD0` is `crc32_little`, not `crc32_z`.

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_40C200` | `595` | platform-service-owned | `zmq_select_t_loop` | High | No engine debt; exact ZeroMQ poll loop from `select.cpp`. |
| 2 | `sub_4374B0` | `602` | engine-owned | `RB_ShowImages` | High | Source owner exists in `tr_backend.c`; retained image-grid layout, `qglFinish`, and diagnostic text match exactly. |
| 3 | `sub_491EA0` | `606` | engine-owned | `AAS_BestReachableArea` | High | Source owner exists in `be_aas_reach.c`; exact reachability scan and travel-time selection logic. |
| 4 | `sub_4CA4E0` | `609` | engine-owned | `Com_Meminfo_f` | High | Source owner exists in `common.c`; exact zone/hunk memory report path with the same console text. |
| 5 | `sub_4CA750` | `410` | engine-owned | `Com_TouchMemory` | High | Source owner exists in `common.c`; adjacent exact helper used by the memory-info path. |
| 6 | `sub_4ED830` | `598` | engine-owned | `WinMain` | High | Source owner exists in `win_main.c`; exact Windows bootstrap and restart loop owner. |
| 7 | `sub_501850` | `617` | CRT/STL | `adler32` | High | No engine debt; exact zlib checksum implementation. |
| 8 | `sub_501D70` | `280` | CRT/STL | `crc32` | High | No engine debt; exact zlib top-level CRC dispatcher adjacent to `crc32_little`. |
| 9 | `sub_504710` | `96` | CRT/STL | `png_create_info_struct` | High | No engine debt; exact libpng info-struct allocator. |
| 10 | `sub_504750` | `604` | CRT/STL | `png_create_read_struct_2` | High | No engine debt; exact libpng read-struct constructor with version and callback validation. |
| 11 | `sub_510630` | `606` | CRT/STL | `png_handle_tRNS` | High | No engine debt; exact libpng transparency-chunk handler. |
| 12 | `sub_510890` | `572` | CRT/STL | `png_handle_bKGD` | High | No engine debt; exact libpng background-chunk handler. |
| 13 | `sub_510AD0` | `448` | CRT/STL | `png_handle_hIST` | High | No engine debt; exact libpng histogram-chunk handler. |
| 14 | `sub_510C70` | `288` | CRT/STL | `png_handle_pHYs` | High | No engine debt; exact libpng physical-pixel-dimensions handler. |
| 15 | `sub_510D90` | `298` | CRT/STL | `png_handle_oFFs` | High | No engine debt; exact libpng image-offset chunk handler. |
| 16 | `sub_510EC0` | `599` | CRT/STL | `png_handle_pCAL` | High | No engine debt; exact libpng pixel-calibration chunk handler. |
| 17 | `sub_51C880` | `445` | CRT/STL | `bitreverse` | High | No engine debt; exact libvorbis codebook bit-reversal helper. |
| 18 | `sub_51CF40` | `328` | CRT/STL | `decode_packed_entry_number` | High | No engine debt; exact libvorbis packed-entry decoder. |
| 19 | `sub_51D070` | `46` | CRT/STL | `vorbis_book_decode` | High | No engine debt; exact libvorbis codebook decode wrapper. |
| 20 | `sub_51D0A0` | `639` | CRT/STL | `vorbis_book_decodevs_add` | High | No engine debt; exact libvorbis vector-scalar decode/add helper from the refreshed queue head. |
| 21 | `sub_51D320` | `402` | CRT/STL | `vorbis_book_decodev_add` | High | No engine debt; exact libvorbis vector decode/add helper. |
| 22 | `sub_51D470` | `417` | CRT/STL | `vorbis_book_decodev_set` | High | No engine debt; exact libvorbis vector decode/set helper. |
| 23 | `sub_51D610` | `540` | CRT/STL | `vorbis_book_decodevv_add` | High | No engine debt; exact libvorbis multichannel vector decode/add helper. |

## Evidence Notes

- The refreshed queue head yielded exact wins across several already-promoted
  evidence lanes rather than opening new opaque engine debt.
- `sub_40C200` is an exact ZeroMQ ownership hit from `select.cpp`:
  the FD-set assembly, timeout handling, retired-FD cleanup, and dispatch loop
  match `zmq::select_t::loop`.
- `sub_4374B0`, `sub_491EA0`, `sub_4CA4E0`, `sub_4CA750`, and `sub_4ED830`
  all match checked-in engine source with retained strings, identical control
  flow, and the same owning call sites.
- The zlib tranche is exact: `sub_501850` is `adler32`, `sub_501AD0` is the
  endian-specific helper `crc32_little`, and `sub_501D70` is the public
  `crc32` wrapper/dispatcher.
- The libpng tranche centers on read-side construction and chunk parsing:
  `png_create_info_struct`, `png_create_read_struct_2`, and the chunk handlers
  for `tRNS`, `bKGD`, `hIST`, `pHYs`, `oFFs`, and `pCAL`.
- The libvorbis tranche is exact as well: `bitreverse`,
  `decode_packed_entry_number`, `vorbis_book_decode`, and the adjacent vector
  decode helpers `vorbis_book_decodevs_add`, `vorbis_book_decodev_add`,
  `vorbis_book_decodev_set`, and `vorbis_book_decodevv_add`.
- `sub_5049D0` was rechecked while resolving the libpng cluster and remains
  correctly mapped as `png_read_info`; the HLIL continues past signature reads
  into the full chunk-dispatch loop, so no correction was needed there.

## Aliases Added

- `sub_40C200` -> `zmq_select_t_loop`
- `sub_4374B0` -> `RB_ShowImages`
- `sub_491EA0` -> `AAS_BestReachableArea`
- `sub_4CA4E0` -> `Com_Meminfo_f`
- `sub_4CA750` -> `Com_TouchMemory`
- `sub_4ED830` -> `WinMain`
- `sub_501850` -> `adler32`
- `sub_501D70` -> `crc32`
- `sub_504710` -> `png_create_info_struct`
- `sub_504750` -> `png_create_read_struct_2`
- `sub_510630` -> `png_handle_tRNS`
- `sub_510890` -> `png_handle_bKGD`
- `sub_510AD0` -> `png_handle_hIST`
- `sub_510C70` -> `png_handle_pHYs`
- `sub_510D90` -> `png_handle_oFFs`
- `sub_510EC0` -> `png_handle_pCAL`
- `sub_51C880` -> `bitreverse`
- `sub_51CF40` -> `decode_packed_entry_number`
- `sub_51D070` -> `vorbis_book_decode`
- `sub_51D0A0` -> `vorbis_book_decodevs_add`
- `sub_51D320` -> `vorbis_book_decodev_add`
- `sub_51D470` -> `vorbis_book_decodev_set`
- `sub_51D610` -> `vorbis_book_decodevv_add`

## Alias Corrections

- `sub_501AD0`: `crc32_z` -> `crc32_little`

## Verification

Alias artifact validation:

- `references/analysis/quakelive_symbol_aliases.json` parses through
  `python -m json.tool`
- duplicate-key scan passed after the alias update
- recount after this pass: `1483` raw alias entries, `1477` address-keyed
  aliases; six support aliases are still non-`sub_...` jump/helper names
- address-keyed coverage: `26.987%` of `5473` functions
- no game/runtime launch was performed; this was a static mapping pass

Parity estimate after this mapping-only pass remains unchanged:

- strict-retail Windows replacement target: `100%` before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

After this round, the refreshed largest-unaliased queue begins with:

| # | Address | Ghidra name | Size |
| ---: | --- | --- | ---: |
| 1 | `0x0047AE50` | `FUN_0047ae50` | `639` |
| 2 | `0x00443160` | `FUN_00443160` | `626` |
| 3 | `0x00515EC0` | `FUN_00515ec0` | `624` |
| 4 | `0x005026F0` | `FUN_005026f0` | `603` |
| 5 | `0x00487080` | `FUN_00487080` | `597` |
| 6 | `0x004615E0` | `FUN_004615e0` | `592` |
| 7 | `0x00463670` | `FUN_00463670` | `592` |
| 8 | `0x00463980` | `FUN_00463980` | `592` |
| 9 | `0x0047C4F0` | `FUN_0047c4f0` | `588` |
| 10 | `0x004A9C50` | `FUN_004a9c50` | `587` |
| 11 | `0x004BE8A0` | `FUN_004be8a0` | `587` |
| 12 | `0x004C9860` | `FUN_004c9860` | `587` |
| 13 | `0x0041E460` | `FUN_0041e460` | `586` |
| 14 | `0x0051CCA0` | `FUN_0051cca0` | `584` |
| 15 | `0x00412720` | `FUN_00412720` | `583` |
| 16 | `0x0041E9A0` | `FUN_0041e9a0` | `581` |
| 17 | `0x004F67A0` | `FUN_004f67a0` | `581` |
| 18 | `0x00411F30` | `FUN_00411f30` | `580` |
| 19 | `0x00423D00` | `FUN_00423d00` | `580` |
| 20 | `0x004CF0D0` | `FUN_004cf0d0` | `580` |

Refresh the queue before the next mapping pass so ties and newly resolved
aliases are handled from the current JSON corpus.
