# quakelive_steam.exe Mapping Round 140

Date: 2026-04-26

Scope: refreshed largest-unaliased queue after round 139. This pass consumed
the queue-head-adjacent libvorbisfile/libvorbis support cluster around
`sub_4FC460` and `sub_517340`, then promoted exact neighboring open/clear/init
helpers that share the same local source anchors.

## Summary

This round mapped `13` `quakelive_steam.exe` functions from the refreshed
largest-unaliased queue and exact adjacent support-library neighbors.
Classification mix:

- `0` engine-owned functions
- `0` platform-service-owned functions
- `13` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

No source debt was opened. Every alias promoted in this pass is anchored
directly against the bundled libvorbis/libvorbisfile source tree under
`src/libs/_deps/libvorbis/lib/`.

This pass intentionally left `sub_463980`, `sub_4F67A0`, `sub_435070`,
`sub_440AD0`, `sub_4109D0`, `sub_4C6BD0`, `sub_40B050`, and `sub_419AD0`
unresolved. Their ownership is bounded, but the exact durable names still need
tighter anchors than this round produced.

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_4FC460` | `552` | CRT/STL/support-library | `_fetch_headers` | High | No engine debt; exact `vorbisfile.c` header-fetch helper that discovers the first Vorbis BOS stream and consumes the two follow-up setup headers. |
| 2 | `sub_517340` | `552` | CRT/STL/support-library | `vorbis_dsp_clear` | High | No engine debt; exact libvorbis DSP teardown that frees backend lookups, per-channel PCM storage, header buffers, and zeroes the `vorbis_dsp_state`. |
| 3 | `sub_4FCA10` | `102` | CRT/STL/support-library | `_make_decode_ready` | High | No engine debt; exact decode-machine loader that calls `vorbis_synthesis_init`, `vorbis_block_init`, zeroes bitrate/sample tracking, and moves the file state to `INITSET`. |
| 4 | `sub_4FCA80` | `35` | CRT/STL/support-library | `_decode_clear` | High | No engine debt; exact `vorbisfile.c` helper that clears the DSP/block state and returns the file to the opened-but-not-decoding state. |
| 5 | `sub_4FCDE0` | `265` | CRT/STL/support-library | `ov_clear` | High | No engine debt; exact `OggVorbis_File` teardown path including `vorbis_block_clear`, `vorbis_dsp_clear`, `ogg_stream_clear`, logical-link cleanup, callback close, and full struct reset. |
| 6 | `sub_4FD780` | `299` | CRT/STL/support-library | `_open_seekable2` | High | No engine debt; exact second-stage seekable open that measures the stream end, bisects logical links, computes PCM lengths, and tail-calls `ov_raw_seek`. |
| 7 | `sub_4FD8B0` | `254` | CRT/STL/support-library | `_ov_open1` | High | No engine debt; exact partial-open initializer that seeds the sync state, copies optional initial bytes, allocates the first logical-link structures, and calls `_fetch_headers`. |
| 8 | `sub_4FD9B0` | `72` | CRT/STL/support-library | `_ov_open2` | High | No engine debt; exact second-stage opener that transitions from `PARTOPEN` to `OPENED` and selects the seekable or streaming path. |
| 9 | `sub_4FDA00` | `70` | CRT/STL/support-library | `ov_open_callbacks` | High | No engine debt; exact public wrapper over `_ov_open1` plus `_ov_open2`. |
| 10 | `sub_516DB0` | `221` | CRT/STL/support-library | `vorbis_block_init` | High | No engine debt; exact libvorbis block initializer that binds the block to its DSP state and seeds packetblob write buffers on the analysis path. |
| 11 | `sub_516F10` | `125` | CRT/STL/support-library | `vorbis_block_clear` | High | No engine debt; exact block teardown that rips the temporary allocation chain, clears packetblob write buffers, frees analysis internals, and zeroes the block. |
| 12 | `sub_517580` | `93` | CRT/STL/support-library | `vorbis_synthesis_restart` | High | No engine debt; exact synthesis-state restart that resets window centers, PCM cursor, granule position, sequence, and sample count. |
| 13 | `sub_5175F0` | `47` | CRT/STL/support-library | `vorbis_synthesis_init` | High | No engine debt; exact public initializer that calls `_vds_shared_init`, clears on failure, then restarts synthesis on success. |

## Evidence Notes

- `sub_4FC460`, `sub_4FCA10`, `sub_4FCA80`, `sub_4FCDE0`, `sub_4FD780`,
  `sub_4FD8B0`, `sub_4FD9B0`, and `sub_4FDA00` close a coherent
  `vorbisfile.c` lifecycle lane. The local HLIL already shows the same
  `ogg_sync_*`, `ogg_stream_*`, `vorbis_synthesis_*`, and `ov_*` call graph as
  the bundled source file `src/libs/_deps/libvorbis/lib/vorbisfile.c`.
- `sub_4FC460` matches `_fetch_headers` exactly: it optionally pulls the next
  page, initializes the `vorbis_info`/`vorbis_comment` pair, walks BOS pages,
  resets the stream serial number, validates the ID header, and then loops
  until the remaining two setup headers are consumed or a bad-header path is
  hit.
- `sub_4FD8B0` and `sub_4FD9B0` are the `_ov_open1` / `_ov_open2` split used
  by upstream libvorbisfile. `sub_4FD8B0` seeds the first logical-link
  scaffolding and leaves the file in `PARTOPEN`; `sub_4FD9B0` then transitions
  to `OPENED` and dispatches either to `_open_seekable2` or the streaming
  `STREAMSET` path.
- `sub_4FCA10` is `_make_decode_ready`, not a public `ov_*` entry point. The
  tell is the exact sequence `vorbis_synthesis_init` ->
  `vorbis_block_init` -> zero `bittrack`/`samptrack` -> set `ready_state` to
  `INITSET`.
- `sub_517340`, `sub_517580`, and `sub_5175F0` are anchored directly by the
  bundled `block.c` source. The field layouts line up cleanly with
  `vorbis_dsp_state`, `vorbis_info::codec_setup`, and the private backend
  state used by libvorbis.
- `sub_516DB0` and `sub_516F10` were promoted because the neighboring
  `ov_clear` / `_make_decode_ready` bodies already proved their identities.
  `sub_516DB0` allocates the analysis packetblob array when `analysisp` is set;
  `sub_516F10` tears the same structures back down.

## Aliases Added

- `sub_4FC460` -> `_fetch_headers`
- `sub_4FCA10` -> `_make_decode_ready`
- `sub_4FCA80` -> `_decode_clear`
- `sub_4FCDE0` -> `ov_clear`
- `sub_4FD780` -> `_open_seekable2`
- `sub_4FD8B0` -> `_ov_open1`
- `sub_4FD9B0` -> `_ov_open2`
- `sub_4FDA00` -> `ov_open_callbacks`
- `sub_516DB0` -> `vorbis_block_init`
- `sub_516F10` -> `vorbis_block_clear`
- `sub_517340` -> `vorbis_dsp_clear`
- `sub_517580` -> `vorbis_synthesis_restart`
- `sub_5175F0` -> `vorbis_synthesis_init`

## Verification

Alias artifact validation:

- `references/analysis/quakelive_symbol_aliases.json` parses through
  `python -m json.tool`
- duplicate-key scan passed after the alias update
- recount after this pass: `1595` raw alias entries, `1589` address-keyed
  aliases
- address-keyed coverage: `29.033%` of `5473` functions
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
| 7 | `0x0040B050` | `FUN_0040b050` | `555` |
| 8 | `0x00419AD0` | `FUN_00419ad0` | `555` |
| 9 | `0x0050D220` | `FUN_0050d220` | `550` |
| 10 | `0x0040F7E0` | `FUN_0040f7e0` | `549` |

The next pass should start with `sub_463980`, `sub_4F67A0`, and
`sub_435070`, then keep working down the remaining top queue while preserving
the existing classification guardrails on unresolved engine, platform-service,
and support-library rows.
