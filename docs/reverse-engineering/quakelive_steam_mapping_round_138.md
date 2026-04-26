# quakelive_steam.exe Mapping Round 138

Date: 2026-04-26

Scope: refreshed largest-unaliased queue after round 137. This pass consumed
the queue-head libvorbis residue row `sub_523570`, the top-20 STL iostream
support row `sub_413400`, and a tightly adjacent ZeroMQ `plain_mechanism`
handshake cluster centered on `sub_427130`.

## Summary

This round mapped `11` `quakelive_steam.exe` functions from the refreshed
largest-unaliased queue and nearby exact support/platform-service neighbors.
Classification mix:

- `0` engine-owned functions
- `7` platform-service-owned functions
- `4` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

No source debt was opened. This tranche is an ownership-clean support pass:
one exact libvorbis residue2 cluster, one exact STL iostream insertion helper,
and the retained ZeroMQ PLAIN HELLO/WELCOME/INITIATE/READY handshake lane.

This pass intentionally left `sub_463980`, `sub_4F67A0`, `sub_435070`,
`sub_440AD0`, `sub_4109D0`, and `sub_4C6BD0` unresolved. Their ownership is
already bounded, but the exact durable names still need tighter local anchors
than this round produced.

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_523570` | `556` | CRT/STL | `res2_forward` | High | No engine debt; exact libvorbis residue2 encoder wrapper from `res0.c`. |
| 2 | `sub_413400` | `552` | CRT/STL | `std_ostream_insert_cstr` | Medium-high | No engine debt; MSVC iostream `char const*` insertion helper with width/fill padding. |
| 3 | `sub_427130` | `548` | platform-service-owned | `zmq_plain_mechanism_t_produce_hello` | High | No engine debt; retained libzmq PLAIN client HELLO command builder. |
| 4 | `sub_427740` | `412` | platform-service-owned | `zmq_plain_mechanism_t_produce_ready` | High | No engine debt; retained libzmq PLAIN READY command builder with basic metadata. |
| 5 | `sub_427530` | `409` | platform-service-owned | `zmq_plain_mechanism_t_produce_initiate` | High | No engine debt; retained libzmq PLAIN INITIATE metadata command builder. |
| 6 | `sub_5237A0` | `384` | CRT/STL | `res2_inverse` | High | No engine debt; exact libvorbis residue2 decoder path from `res0.c`. |
| 7 | `sub_427360` | `378` | platform-service-owned | `zmq_plain_mechanism_t_process_hello` | High | No engine debt; retained libzmq server-side HELLO parser plus ZAP dispatch. |
| 8 | `sub_4276D0` | `109` | platform-service-owned | `zmq_plain_mechanism_t_process_initiate` | High | No engine debt; retained libzmq INITIATE prefix validator plus metadata parser call. |
| 9 | `sub_4278E0` | `83` | platform-service-owned | `zmq_plain_mechanism_t_process_ready` | High | No engine debt; retained libzmq READY prefix validator plus metadata parser call. |
| 10 | `sub_4274E0` | `71` | platform-service-owned | `zmq_plain_mechanism_t_process_welcome` | High | No engine debt; retained libzmq WELCOME command validator. |
| 11 | `sub_523530` | `61` | CRT/STL | `res2_class` | High | No engine debt; exact libvorbis residue2 nonzero-channel classifier wrapper. |

## Evidence Notes

- `sub_523530`, `sub_523570`, and `sub_5237A0` close the libvorbis
  residue2 lane exactly against `src/libs/_deps/libvorbis/lib/res0.c`.
  `sub_523530` counts nonzero channels and tail-calls the already-mapped
  `_2class`; `sub_523570` interleaves channel samples into a temporary work
  vector before calling the already-mapped `vorbis_residue_01forward`; and
  `sub_5237A0` decodes phrasebook partition words, then feeds stagebooks
  through the already-mapped `vorbis_book_decodevv_add`. The signatures,
  control flow, and neighboring export bundle order all match
  `res2_class`, `res2_forward`, and `res2_inverse`.
- `sub_413400` is the STL/CRT `char const*` ostream insertion helper. The
  body computes the input string length, consults stream width and fill
  fields, flushes the tied stream when needed, emits left or right padding via
  `std::streambuf::sputc`, writes the payload via `std::streambuf::sputn`,
  resets width, sets stream state, and calls `std::ostream::_Osfx`.
  I promoted it as the descriptive support alias `std_ostream_insert_cstr`
  rather than preserving the bogus HLIL `__vcasan` demangle.
- The `sub_427130` through `sub_4278E0` cluster is a stable ZeroMQ PLAIN
  handshake lane. Local HLIL anchors it to `..\..\..\src\plain_mechanism.cpp`
  and `..\..\..\src\mechanism.cpp`; the exact method names were cross-checked
  against current upstream libzmq `plain_client.cpp`, `plain_server.cpp`, and
  `mechanism.cpp`, while preserving the older binary's committed
  `plain_mechanism_t` naming convention already established by
  `zmq_plain_mechanism_t_send_zap_request` and
  `zmq_plain_mechanism_t_receive_and_process_zap_reply`.
- `sub_427130` is `zmq_plain_mechanism_t_produce_hello`. The body bounds the
  username and password lengths to `< 256`, allocates `username + password +
  8` bytes, writes the `HELLO` prefix, then serializes one-byte username and
  password lengths followed by their payloads.
- `sub_427360` is `zmq_plain_mechanism_t_process_hello`. It validates the
  `HELLO` prefix and exact username/password framing, builds temporary strings,
  invokes the already-mapped `zmq_session_base_t_zap_connect`, then calls the
  already-mapped `zmq_plain_mechanism_t_send_zap_request` and
  `zmq_plain_mechanism_t_receive_and_process_zap_reply`.
- `sub_4274E0` is `zmq_plain_mechanism_t_process_welcome`. The function is a
  compact exact validator: it requires an 8-byte command and bytewise compares
  it against the `WELCOME` prefix before returning success; otherwise it sets
  `EINVAL`.
- `sub_427530` is `zmq_plain_mechanism_t_produce_initiate`. The body writes
  the `INITIATE` prefix, appends the `Socket-Type` property using the
  `mechanism.cpp` socket-type string table, conditionally appends the
  `Identity` property for routing-id socket types, then copies the finished
  metadata block into the message buffer.
- `sub_4276D0` is `zmq_plain_mechanism_t_process_initiate`. The function
  validates the `INITIATE` prefix and tail-calls the already-mapped
  `zmq_mechanism_t_parse_metadata` on the remaining payload.
- `sub_427740` is `zmq_plain_mechanism_t_produce_ready`. The body mirrors the
  INITIATE builder but emits the `READY` prefix before appending the same
  basic metadata properties.
- `sub_4278E0` is `zmq_plain_mechanism_t_process_ready`. Like the INITIATE
  parser, it validates the `READY` prefix and forwards the trailing metadata
  to `zmq_mechanism_t_parse_metadata`.

## Aliases Added

- `sub_413400` -> `std_ostream_insert_cstr`
- `sub_427130` -> `zmq_plain_mechanism_t_produce_hello`
- `sub_427360` -> `zmq_plain_mechanism_t_process_hello`
- `sub_4274E0` -> `zmq_plain_mechanism_t_process_welcome`
- `sub_427530` -> `zmq_plain_mechanism_t_produce_initiate`
- `sub_4276D0` -> `zmq_plain_mechanism_t_process_initiate`
- `sub_427740` -> `zmq_plain_mechanism_t_produce_ready`
- `sub_4278E0` -> `zmq_plain_mechanism_t_process_ready`
- `sub_523530` -> `res2_class`
- `sub_523570` -> `res2_forward`
- `sub_5237A0` -> `res2_inverse`

## Verification

Alias artifact validation:

- `references/analysis/quakelive_symbol_aliases.json` parses through
  `python -m json.tool`
- duplicate-key scan passed after the alias update
- recount after this pass: `1574` raw alias entries, `1568` address-keyed
  aliases
- address-keyed coverage: `28.650%` of `5473` functions
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
| 9 | `0x004FC460` | `FUN_004fc460` | `552` |
| 10 | `0x00517340` | `FUN_00517340` | `552` |

The next pass should start with `sub_463980`, `sub_4F67A0`, and
`sub_435070`, then keep working down the remaining top queue while preserving
the existing classification guardrails on the unresolved platform-service,
engine, and support-library rows.
