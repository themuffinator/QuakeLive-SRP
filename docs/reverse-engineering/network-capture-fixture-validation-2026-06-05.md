# Network Capture Fixture Validation - 2026-06-05

## Scope

This pass adds a validation gate for protocol-91 demo transcripts created by
`tools.trace.demo_transcript`. It supports the residual byte-for-byte replay
row, but does not claim that retail packet or demo evidence is now committed.

No runtime or game launch was required.

## Validator

`validate_demo_transcript_dict` now verifies transcript JSON before it can be
used as closure evidence:

- schema and format identifiers;
- positive protocol number;
- `message_count` matching the message array length;
- `source_size` matching `terminator_offset + 8` for the `-1/-1` terminator;
- contiguous message offsets from zero;
- payload hex that decodes, matches the declared length, and hashes correctly;
- aggregate payload SHA-256 across concatenated payloads;
- `first_byte` matching the decoded payload.

When called with `require_retail_provenance=True`, the validator also requires
provenance keys for `source`, `capture_type`, `capture_date_utc`, and
`retail_build`. Accepted capture types are `retail_packet_capture`,
`protocol91_demo_transcript`, and `known_good_byte_fixture`.

## Checklist Effect

The checklist now records transcript validation as complete. The actual
byte-for-byte fixture row and downstream capture-diff rows remain unchecked
until a transcript or capture with retail provenance is committed and validated.

Estimated parity movement:

- Overall network-protocol source parity remains `90%` -> `90%`.
- Byte-for-byte capture evidence remains `0%` -> `0%`.
- Repo-wide parity remains `99%` -> `99%`.
