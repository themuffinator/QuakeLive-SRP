# quakelive_steam.exe Mapping Round 129

Date: 2026-04-26

Scope: refreshed largest-unaliased queue after round 128, beginning at
`sub_49FC30`, `sub_408EC0`, and `sub_525370`.

## Summary

This round mapped `17` `quakelive_steam.exe` functions from the refreshed queue
and one adjacent ZeroMQ stream-engine cluster that became unambiguous while
classifying the queue head. Classification mix:

- `6` engine-owned functions
- `6` platform-service-owned functions
- `5` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

No source debt was opened. Engine-owned rows land in checked-in botlib,
renderer, and client owners. Platform-service rows stay inside the bundled
ZeroMQ host/runtime lane. Support-library rows belong to IJG JPEG, zlib, and
libvorbis rather than Quake engine source debt.

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_49FC30` | `659` | engine-owned | `AAS_BestReachableArea` | High | Source owner exists in botlib `be_aas_reach.c`; reachable-area search with origin fudging and link fallback. |
| 2 | `sub_408EC0` | `659` | platform-service-owned | `zmq_socket_base_t_term_endpoint` | High | No engine debt; ZeroMQ endpoint teardown/removal path behind the `004014b0` wrapper. |
| 3 | `sub_525370` | `658` | CRT/STL | `floor1_inverse1` | High | No engine debt; libvorbis floor1 inverse stage 1 unpack/decode helper. |
| 4 | `sub_501AD0` | `657` | CRT/STL | `crc32_z` | High | No engine debt; zlib braided CRC32 core. |
| 5 | `sub_47ED10` | `655` | CRT/STL | `get_app0` | High | No engine debt; IJG JPEG APP0/JFIF marker parser. |
| 6 | `sub_4B0CD0` | `654` | engine-owned | `blitVQQuad32fs` | High | Source owner exists in client cinematic decode `cl_cin.c`; 32-bit VQ quad blitter. |
| 7 | `sub_47B710` | `654` | CRT/STL | `h2v2_fancy_upsample` | High | No engine debt; IJG JPEG fancy 2x2 chroma upsampler. |
| 8 | `sub_435FF0` | `647` | engine-owned | `RB_RenderDrawSurfList` | High | Source owner exists in renderer `tr_backend.c`; sorted draw-surface submission/render loop. |
| 9 | `sub_49CD80` | `646` | engine-owned | `BotLoadItemConfig` | High | Source owner exists in botlib `be_ai_goal.c`; item config parser with `max_iteminfo` guards. |
| 10 | `sub_4193B0` | `641` | platform-service-owned | `zmq_stream_t_xrecv` | High | No engine debt; ZeroMQ STREAM receive path returning identity/data frames. |
| 11 | `sub_4B07C0` | `641` | engine-owned | `CL_SetCGameTime` | High | Source owner exists in client `cl_cgame.c`; cgame clock/demo timing gate. |
| 12 | `sub_488E50` | `636` | engine-owned | `AAS_Reachability_Swim` | High | Source owner exists in botlib `be_aas_reach.c`; swim reachability allocator and face overlap checks. |
| 13 | `sub_422260` | `628` | platform-service-owned | `zmq_stream_engine_t_restart_input` | High | No engine debt; restart path for a previously stopped decoder/input stream. |
| 14 | `sub_421E50` | `491` | platform-service-owned | `zmq_stream_engine_t_in_event` | High | No engine debt; ZeroMQ stream-engine read/decode event loop. |
| 15 | `sub_422040` | `469` | platform-service-owned | `zmq_stream_engine_t_out_event` | High | No engine debt; ZeroMQ stream-engine encoder/output event loop. |
| 16 | `sub_419640` | `421` | platform-service-owned | `zmq_stream_t_xhas_in` | High | No engine debt; STREAM prefetch probe that stages the identity frame. |
| 17 | `sub_474D90` | `642` | CRT/STL | `decompress_onepass` | High | No engine debt; IJG JPEG single-pass coefficient decompressor. |

## Evidence Notes

- `sub_408EC0` is the internal ZeroMQ endpoint-teardown path, not a second
  connect routine: the `004014b0` wrapper dispatches here, the body parses the
  endpoint, special-cases `inproc`, finds matching endpoint/pending-connection
  ranges, tears down pipes, and erases the matching tree rows.
- The STREAM socket cluster resolved cleanly once the event lifecycle was read
  as a group:
  - `sub_4193B0` builds the identity frame or drains the prefetched payload,
    matching `xrecv`;
  - `sub_419640` stages the prefetched identity/data state for `xhas_in`;
  - `sub_421E50` is the actual decoder/read `in_event`;
  - `sub_422040` is the encoder/write `out_event`;
  - `sub_422260` is the `restart_input` resume path, not the primary input
    event.
- Engine-owned rows were anchored against checked-in owners:
  `AAS_BestReachableArea`, `AAS_Reachability_Swim`, `BotLoadItemConfig`,
  `RB_RenderDrawSurfList`, `CL_SetCGameTime`, and `blitVQQuad32fs`.
- Support-library rows matched bundled dependency sources directly: IJG JPEG
  (`decompress_onepass`, `h2v2_fancy_upsample`, `get_app0`), zlib (`crc32_z`),
  and libvorbis (`floor1_inverse1`).

## Aliases Added

- `sub_408EC0` -> `zmq_socket_base_t_term_endpoint`
- `sub_4193B0` -> `zmq_stream_t_xrecv`
- `sub_419640` -> `zmq_stream_t_xhas_in`
- `sub_421E50` -> `zmq_stream_engine_t_in_event`
- `sub_422040` -> `zmq_stream_engine_t_out_event`
- `sub_422260` -> `zmq_stream_engine_t_restart_input`
- `sub_435FF0` -> `RB_RenderDrawSurfList`
- `sub_474D90` -> `decompress_onepass`
- `sub_47B710` -> `h2v2_fancy_upsample`
- `sub_47ED10` -> `get_app0`
- `sub_488E50` -> `AAS_Reachability_Swim`
- `sub_49CD80` -> `BotLoadItemConfig`
- `sub_49FC30` -> `AAS_BestReachableArea`
- `sub_4B07C0` -> `CL_SetCGameTime`
- `sub_4B0CD0` -> `blitVQQuad32fs`
- `sub_501AD0` -> `crc32_z`
- `sub_525370` -> `floor1_inverse1`

## Verification

Alias artifact validation:

- `references/analysis/quakelive_symbol_aliases.json` parses through
  `python -m json.tool`
- recount after this pass: `1432` raw alias entries, `1426` address-keyed
  aliases; six support aliases are still non-`sub_...` jump/helper names
- address-keyed coverage: `26.055%` of `5473` functions
- no game/runtime launch was performed; this was a static mapping pass

## Next Queue Head

After this round, the refreshed largest-unaliased queue begins with:

| # | Address | Ghidra name | Size |
| ---: | --- | --- | ---: |
| 1 | `0x004FBB00` | `FUN_004fbb00` | `647` |
| 2 | `0x00409F20` | `FUN_00409f20` | `645` |
| 3 | `0x0040A3D0` | `FUN_0040a3d0` | `645` |
| 4 | `0x0040A660` | `FUN_0040a660` | `645` |
| 5 | `0x0040A8F0` | `FUN_0040a8f0` | `645` |
| 6 | `0x00515250` | `FUN_00515250` | `643` |
| 7 | `0x0047AE50` | `FUN_0047ae50` | `639` |
| 8 | `0x0051D0A0` | `FUN_0051d0a0` | `639` |
| 9 | `0x00506230` | `FUN_00506230` | `636` |
| 10 | `0x0040BF30` | `FUN_0040bf30` | `633` |
| 11 | `0x004970E0` | `FUN_004970e0` | `627` |
| 12 | `0x005206A0` | `FUN_005206a0` | `627` |
| 13 | `0x00435980` | `FUN_00435980` | `626` |
| 14 | `0x00443160` | `FUN_00443160` | `626` |
| 15 | `0x00515EC0` | `FUN_00515ec0` | `624` |
| 16 | `0x004BD790` | `FUN_004bd790` | `622` |
| 17 | `0x00476E20` | `FUN_00476e20` | `617` |
| 18 | `0x00501850` | `FUN_00501850` | `617` |
| 19 | `0x004500B0` | `FUN_004500b0` | `614` |
| 20 | `0x0041BEB0` | `FUN_0041beb0` | `613` |

Refresh the queue before the next mapping pass so ties and newly resolved
aliases are handled from the current JSON corpus.
