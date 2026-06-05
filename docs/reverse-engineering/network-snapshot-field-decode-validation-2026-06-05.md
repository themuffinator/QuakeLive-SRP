# Network Snapshot Field Decode Validation - 2026-06-05

## Scope

This note adds a validation gate for future end-to-end retail snapshot
capture/decode reports covering both `playerStateFields` and
`entityStateFields`.

No runtime or game launch was required. No retail packet capture or protocol-91
snapshot transcript is claimed by this pass.

## Validation Contract

`tools.trace.snapshot_decode.validate_snapshot_field_decode_dict` accepts
reviewable JSON reports with format `quake_live_snapshot_field_decode`.

The validator checks the field-table decode sections:

- both `playerStateFields` and `entityStateFields` must be present;
- each table must declare the recovered retail count, `58`;
- table-level and value-level hashes must be lowercase SHA-256 hex strings;
- observed field indexes must be within `0..57`;
- when the retail source-of-truth specs are supplied, observed field index,
  bit width, and wire kind must match those specs;
- source aliases such as `retailEventData` may validate against the retail
  `generic1` entity slot.

The validator also checks decoded snapshot frames:

- at least one frame must be present;
- `messageNum` and `packetEntityCount` must be non-negative integers;
- `serverTime` and `deltaNum` must be integers;
- playerstate, entitystate, and packet-entity hashes must be present.

Closure mode requires provenance. This keeps future retail snapshot decode
evidence reviewable without allowing a semantic-only netdump to close a packet
decode row.

## Checklist Effect

The outstanding checklist now has a checked support row for snapshot field
decode report validation. The actual end-to-end retail snapshot capture/decode
row remains open until a retail packet capture, protocol-91 transcript, or
equivalent known-good decode report is committed.

Estimated parity movement:

- Overall network-protocol source parity remains `90%` -> `90%`.
- Byte-for-byte capture evidence remains `0%` -> `0%`.
- Repo-wide parity remains `99%` -> `99%`.
