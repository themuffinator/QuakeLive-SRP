# Network Invalid-lc Probe Validation - 2026-06-05

## Scope

This note adds a validation gate for future controlled retail probes of
malicious invalid-`lc` packet behavior.

No runtime or game launch was required. No retail probe is claimed by this
pass.

## Validation Contract

`tools.trace.invalid_lc_probe.validate_invalid_lc_probe_dict` accepts
reviewable JSON reports with format `quake_live_invalid_lc_probe`.

The validator checks the malicious input:

- protocol must be `91`;
- the field table must be `entityStateFields` or `playerStateFields`;
- the field count must match the recovered retail count, `58`;
- `lc` must exceed that field count;
- packet hashes, when present, must be lowercase SHA-256 hex strings.

It also checks the observed outcomes:

- retail observation must have a recognized classification and message;
- closure mode requires provenance and at least one hashed artifact;
- retail crash classification requires a `crash_dump` artifact;
- source observation must be `err_drop`;
- the source error message must match the hardened guard for the chosen table
  and `lc`.

## Checklist Effect

The outstanding checklist now has a checked support row for invalid-`lc` probe
report validation. The actual retail-probe row remains open until a controlled
retail probe, packet capture, or equivalent known-good byte fixture is
committed and classified.

Estimated parity movement:

- Overall network-protocol source parity remains `90%` -> `90%`.
- Byte-for-byte capture evidence remains `0%` -> `0%`.
- Repo-wide parity remains `99%` -> `99%`.
