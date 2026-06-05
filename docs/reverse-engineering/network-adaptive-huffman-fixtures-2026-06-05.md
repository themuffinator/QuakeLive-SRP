# Network Adaptive Huffman Fixtures - 2026-06-05

## Scope

This note closes the residual checklist row for capture-scoped adaptive Huffman
fixtures. It does not claim that a retail packet trace has been captured; it
defines deterministic byte fixtures and state scopes so later trace comparison
can be mechanical.

No runtime launch was required.

## Evidence Used

Owning retail binary:

- `assets/quakelive/quakelive_steam.exe`

Committed reference corpus:

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
- `docs/reverse-engineering/quakelive_steam_mapping_round_56.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_57.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_65.md`

Source inspected:

- `src/code/qcommon/huffman.c`
- `src/code/qcommon/msg.c`
- `src/code/qcommon/net_chan.c`
- `src/code/client/cl_main.c`
- `src/code/server/sv_main.c`

## Fixture Scopes

Two Huffman scopes matter for packet-byte work:

| Scope | Owner | State model | Fixture rule |
| --- | --- | --- | --- |
| `huffcompress_local_reset` | `Huff_Compress` | Local NYT tree per call; transmit byte, then `Huff_addRef`. | Used for compressed `connect` OOB payloads after byte offset `12`. |
| `msghuff_seeded_bitstream` | `MSG_WriteBits` | `MSG_initHuffman` seeds `msgHuff` from `msg_hData`; normal writes use `Huff_offsetTransmit`. | Used for regular non-OOB bitstream byte fixtures. |

The compressed-connect fixture deliberately uses numeric challenge `1234`
because its encoded bit count is not byte-aligned. That avoids treating an
unwritten terminal pad byte as stable packet evidence.

## Frozen Fixtures

The machine-readable fixture source is:

- `docs/reverse-engineering/network-adaptive-huffman-fixtures-2026-06-05.json`

Key vectors:

| Fixture | Scope | Input | Encoded bytes |
| --- | --- | --- | --- |
| `compressed_connect_profile91_numeric_challenge` | `huffcompress_local_reset` | `connect "\\protocol\\91\\qport\\1234\\challenge\\1234"` with compression from offset `12` | Full datagram `ff ff ff ff 63 6f 6e 6e 65 63 74 20 00 28 44 74 70 88 13 ec c7 a5 61 2c d8 e8 70 1a c6 05 c7 f9 c4 dc 30 15 cc 09 cb 52 60 61 18 26 51 4c 11 3b c2 9c 3e 14 51 14` |
| `huffcompress_local_reset_abc` | `huffcompress_local_reset` | `61 62 63` | `00 03 86 8c 30 06` |
| `msghuff_seeded_three_ascii_bytes` | `msghuff_seeded_bitstream` | `61 62 63` | `3c ab 1f 03` |
| `msghuff_seeded_client_sideband_move_body` | `msghuff_seeded_bitstream` | `04 03 02 01 0d 0c 0b 0a 02 00 00 00 80 02 01 05` | `a1 6c e4 6e 27 8b 34 52 fd 90 3b 02` |

## Residual Risks

- These fixtures make the Huffman state and byte targets explicit, but no
  external retail packet capture is committed yet.
- Full snapshot and usercmd packet-byte replay still needs capture-specific
  message ordering, payloads, and fragmentation timing.
- The compressed-connect fixture is deterministic and capture-ready; it still
  needs an actual retail trace before the compressed-connect capture-diff row
  can close.

Estimated parity movement for this residual slice:

- Focused Huffman fixture slice: `35%` before, `82%` after.
- Overall network-protocol parity: `87%` before, `88%` after.
