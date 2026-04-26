# quakelive_steam.exe Mapping Round 133

Date: 2026-04-26

Scope: refreshed largest-unaliased queue after round 132. This pass resolved
the queue-head libogg/libvorbis tranche around `sub_515EC0` and `sub_51CCA0`,
plus exact ZeroMQ support around `sub_412720` and `sub_423D00`, then harvested
the adjacent support-library neighbors needed to close those clusters cleanly.

## Summary

This round mapped `25` `quakelive_steam.exe` functions from the refreshed
largest-unaliased queue and nearby exact support-library neighbors.
Classification mix:

- `0` engine-owned functions
- `2` platform-service-owned functions
- `23` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

No source debt was opened. The two platform-service rows stay in the bundled
ZeroMQ/libzmq networking lane. The remaining wins are exact libogg and
libvorbis support-library functions rather than Quake engine reconstruction
debt.

This pass also deliberately left `sub_411F30` unresolved. The HLIL gives it a
misleading MSVC filesystem demangle, but the observed body is clearly part of
the `tcp_address.cpp` host/port parsing lane. That row needs one more stable
source-level signal before it should be promoted.

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_515EC0` | `624` | CRT/STL | `ogg_stream_pagein` | High | No engine debt; exact libogg page-in path from `framing.c`. |
| 2 | `sub_51CCA0` | `584` | CRT/STL | `vorbis_staticbook_unpack` | High | No engine debt; exact libvorbis static codebook unpacker from `codebook.c`. |
| 3 | `sub_412720` | `583` | platform-service-owned | `zmq_tcp_address_mask_t_to_string` | High | No engine debt; exact libzmq address-mask formatter from the `tcp_address.cpp` vtable lane. |
| 4 | `sub_423D00` | `580` | platform-service-owned | `zmq_tcp_connecter_t_ctor` | High | No engine debt; exact libzmq TCP connecter constructor from `tcp_connecter.cpp`. |
| 5 | `sub_515970` | `14` | CRT/STL | `ogg_page_version` | High | No engine debt; exact libogg page-header accessor. |
| 6 | `sub_515980` | `17` | CRT/STL | `ogg_page_continued` | High | No engine debt; exact libogg continued-page flag accessor. |
| 7 | `sub_5159A0` | `17` | CRT/STL | `ogg_page_bos` | High | No engine debt; exact libogg BOS flag accessor. |
| 8 | `sub_5159C0` | `17` | CRT/STL | `ogg_page_eos` | High | No engine debt; exact libogg EOS flag accessor. |
| 9 | `sub_5159E0` | `135` | CRT/STL | `ogg_page_granulepos` | High | No engine debt; exact libogg granule-position unpack helper. |
| 10 | `sub_515A70` | `41` | CRT/STL | `ogg_page_serialno` | High | No engine debt; exact libogg serial-number accessor. |
| 11 | `sub_515AA0` | `41` | CRT/STL | `ogg_page_pageno` | High | No engine debt; exact libogg page-number accessor. |
| 12 | `sub_515AD0` | `99` | CRT/STL | `ogg_stream_init` | High | No engine debt; exact libogg stream-state initializer. |
| 13 | `sub_515B40` | `79` | CRT/STL | `ogg_stream_clear` | High | No engine debt; exact libogg stream-state clearer. |
| 14 | `sub_515B90` | `37` | CRT/STL | `_os_body_expand` | High | No engine debt; exact libogg body-buffer growth helper. |
| 15 | `sub_515BC0` | `62` | CRT/STL | `_os_lacing_expand` | High | No engine debt; exact libogg lacing-table growth helper. |
| 16 | `sub_515C00` | `152` | CRT/STL | `ogg_page_checksum_set` | High | No engine debt; exact libogg CRC writer for page headers. |
| 17 | `sub_515CA0` | `34` | CRT/STL | `ogg_sync_init` | High | No engine debt; exact libogg sync-state initializer. |
| 18 | `sub_515CD0` | `40` | CRT/STL | `ogg_sync_clear` | High | No engine debt; exact libogg sync-state clearer. |
| 19 | `sub_515D00` | `119` | CRT/STL | `ogg_sync_buffer` | High | No engine debt; exact libogg sync-buffer grow/compact helper. |
| 20 | `sub_515D80` | `29` | CRT/STL | `ogg_sync_wrote` | High | No engine debt; exact libogg sync write-advance helper. |
| 21 | `sub_515DA0` | `288` | CRT/STL | `ogg_sync_pageseek` | High | No engine debt; exact libogg sync page-seek verifier. |
| 22 | `sub_516160` | `79` | CRT/STL | `ogg_stream_reset` | High | No engine debt; exact libogg stream reset helper. |
| 23 | `sub_5161B0` | `28` | CRT/STL | `ogg_stream_reset_serialno` | High | No engine debt; exact libogg serial-reset helper. |
| 24 | `sub_5161D0` | `267` | CRT/STL | `_packetout` | High | No engine debt; exact libogg packet extraction helper. |
| 25 | `sub_5162E0` | `23` | CRT/STL | `ogg_stream_packetout` | High | No engine debt; exact libogg packet-out wrapper. |

## Evidence Notes

- The queue-head libogg block is exact. `sub_515EC0` matches
  `ogg_stream_pagein`, and the adjacent `sub_515970` through `sub_5162E0`
  helpers match the same `src/libs/_deps/libogg/src/framing.c` accessor,
  initializer, checksum, sync, reset, and packet-extraction cluster.
- `sub_51CCA0` is an exact libvorbis ownership hit from
  `src/libs/_deps/libvorbis/lib/codebook.c`: it checks the `0x564342`
  signature, unpacks ordered and unordered codeword lengths, reads
  `maptype`, `q_min`, `q_delta`, `q_quant`, and `q_sequencep`, allocates the
  quantlist, and destroys the partially built book on failure exactly like
  `vorbis_staticbook_unpack`.
- `sub_412720` is an exact `tcp_address_mask_t` vtable hit from the committed
  RTTI/vtable corpus. It is the `to_string` override for the mask-bearing TCP
  address type and formats the node plus mask width rather than the base
  address alone.
- `sub_423D00` is an exact libzmq constructor hit from `tcp_connecter.cpp`:
  it installs the `own_t` and `io_object_t` vtables, asserts `addr`, asserts
  `addr->protocol == "tcp"`, copies `delayed_start`, and builds the retained
  address string state.
- `sub_411F30` was rechecked while resolving the TCP-address lane and remains
  intentionally unmapped this round. The HLIL demangle is inconsistent with
  the observed `tcp_address.cpp` parsing body, so promoting that printed name
  would lower confidence rather than raise it.

## Aliases Added

- `sub_412720` -> `zmq_tcp_address_mask_t_to_string`
- `sub_423D00` -> `zmq_tcp_connecter_t_ctor`
- `sub_515970` -> `ogg_page_version`
- `sub_515980` -> `ogg_page_continued`
- `sub_5159A0` -> `ogg_page_bos`
- `sub_5159C0` -> `ogg_page_eos`
- `sub_5159E0` -> `ogg_page_granulepos`
- `sub_515A70` -> `ogg_page_serialno`
- `sub_515AA0` -> `ogg_page_pageno`
- `sub_515AD0` -> `ogg_stream_init`
- `sub_515B40` -> `ogg_stream_clear`
- `sub_515B90` -> `_os_body_expand`
- `sub_515BC0` -> `_os_lacing_expand`
- `sub_515C00` -> `ogg_page_checksum_set`
- `sub_515CA0` -> `ogg_sync_init`
- `sub_515CD0` -> `ogg_sync_clear`
- `sub_515D00` -> `ogg_sync_buffer`
- `sub_515D80` -> `ogg_sync_wrote`
- `sub_515DA0` -> `ogg_sync_pageseek`
- `sub_515EC0` -> `ogg_stream_pagein`
- `sub_516160` -> `ogg_stream_reset`
- `sub_5161B0` -> `ogg_stream_reset_serialno`
- `sub_5161D0` -> `_packetout`
- `sub_5162E0` -> `ogg_stream_packetout`
- `sub_51CCA0` -> `vorbis_staticbook_unpack`

## Verification

Alias artifact validation:

- `references/analysis/quakelive_symbol_aliases.json` parses through
  `python -m json.tool`
- duplicate-key scan passed after the alias update
- recount after this pass: `1508` raw alias entries, `1502` address-keyed
  aliases; six support aliases are still non-`sub_...` jump/helper names
- address-keyed coverage: `27.444%` of `5473` functions
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
| 1 | `0x0047AE50` | `FUN_0047ae50` | `639` |
| 2 | `0x00443160` | `FUN_00443160` | `626` |
| 3 | `0x005026F0` | `FUN_005026f0` | `603` |
| 4 | `0x00487080` | `FUN_00487080` | `597` |
| 5 | `0x004615E0` | `FUN_004615e0` | `592` |
| 6 | `0x00463670` | `FUN_00463670` | `592` |
| 7 | `0x00463980` | `FUN_00463980` | `592` |
| 8 | `0x0047C4F0` | `FUN_0047c4f0` | `588` |
| 9 | `0x004A9C50` | `FUN_004a9c50` | `587` |
| 10 | `0x004BE8A0` | `FUN_004be8a0` | `587` |
| 11 | `0x004C9860` | `FUN_004c9860` | `587` |
| 12 | `0x0041E460` | `FUN_0041e460` | `586` |
| 13 | `0x0041E9A0` | `FUN_0041e9a0` | `581` |
| 14 | `0x004F67A0` | `FUN_004f67a0` | `581` |
| 15 | `0x00411F30` | `FUN_00411f30` | `580` |
| 16 | `0x004CF0D0` | `FUN_004cf0d0` | `580` |
| 17 | `0x00509190` | `FUN_00509190` | `576` |
| 18 | `0x0046C5C0` | `FUN_0046c5c0` | `575` |
| 19 | `0x00492CD0` | `FUN_00492cd0` | `575` |
| 20 | `0x00493420` | `FUN_00493420` | `575` |

Refresh the queue before the next mapping pass so ties and newly resolved
aliases are handled from the current JSON corpus.
