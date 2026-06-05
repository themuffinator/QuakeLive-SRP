# Network Capture Diff Tooling - 2026-06-05

## Scope

This pass adds packet-byte diff tooling for the residual XOR and compressed
`connect` capture rows. It does not claim that a retail packet trace is now
committed.

No runtime or game launch was required.

## Tooling

`tools.trace.capture_diff` provides:

- `validate_packet_capture_dict` for `quake_live_packet_byte_capture` JSON;
- `packet_expectations_from_xor_spec`, reading
  `network-xor-codec-parity-2026-06-05.json` `encoded_datagram_hex` vectors;
- `packet_expectations_from_huffman_spec`, reading
  `network-adaptive-huffman-fixtures-2026-06-05.json` datagram fixtures;
- `diff_packet_capture`, producing a `quake_live_capture_diff_report`.

The report records `fixture_id`, lane, source, match status, expected and
observed sizes, expected and observed SHA-256, and first mismatch offset. Missing
fixtures and byte mismatches are distinct statuses so future retail captures can
fail loudly and usefully.

## Checklist Effect

The checklist now records capture-diff tooling as complete. The actual XOR
golden datagram and compressed `connect` capture-diff rows remain unchecked
until retail packet traces are committed and compared.

Estimated parity movement:

- Overall network-protocol source parity remains `90%` -> `90%`.
- Byte-for-byte capture evidence remains `0%` -> `0%`.
- Repo-wide parity remains `99%` -> `99%`.
