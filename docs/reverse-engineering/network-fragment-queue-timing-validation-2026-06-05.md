# Network Fragment Queue Timing Validation - 2026-06-05

## Scope

This note adds a validation gate for future retail evidence covering the
fragmented server-message plus queued follow-up lane in
`docs/plans/2026-06-05-outstanding-work-checklist.md`.

No runtime or game launch was required. No retail packet capture is claimed by
this pass.

## Validation Contract

`tools.trace.fragment_timing.validate_fragment_queue_timing_dict` accepts
reviewable JSON reports with format `quake_live_fragment_queue_timing`.

The validator checks the fragment train:

- `fragmentStart` must equal the previous accumulated length for that sequence.
- `accumulatedLength` must equal `fragmentStart + fragmentLength`.
- At least one full `FRAGMENT_SIZE` event must be present and not accepted.
- At least one terminal short fragment must be present and accepted.
- Accepted terminal fragments must carry a SHA-256 `reassembledPayloadHash`.

The validator also checks queued follow-up timing:

- queued messages must be stored unencoded;
- queued messages must be encoded on pop;
- queued datagrams must carry a SHA-256 `datagramHash`;
- the final queued follow-up event must empty the queue.

When a report is used to close the retail checklist row, provenance is required:
`source`, `capture_type`, `capture_date_utc`, and `retail_build`.

## Checklist Effect

The outstanding checklist now has a checked support row for the fragment/queue
timing report validator. The actual fragmented snapshot plus queued follow-up
retail-capture row remains open until a byte-for-byte retail capture or
equivalent known-good timing report is committed.

Estimated parity movement:

- Overall network-protocol source parity remains `90%` -> `90%`.
- Byte-for-byte capture evidence remains `0%` -> `0%`.
- Repo-wide parity remains `99%` -> `99%`.
