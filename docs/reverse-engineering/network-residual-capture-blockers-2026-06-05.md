# Network Residual Capture Blockers - 2026-06-05

## Scope

This note classifies the remaining unchecked networking rows in
`docs/plans/2026-06-05-outstanding-work-checklist.md` after the source-side
parser, field-table, XOR, Huffman, sideband, replay-contract, and hardening
passes.

No runtime or game launch was required. The result is intentionally conservative:
the byte-for-byte rows remain open because the repository still lacks the
external retail packet/demo evidence needed to close them.

## Evidence Inventory

Committed evidence that can be used now:

- `tests/netdumps/retail_duel.snap.json`, with hashes in
  `tools/tests/client_regression/retail_netdump_baseline.json`, is known-good
  semantic retail snapshot replay evidence.
- `network-xor-codec-parity-2026-06-05.json` stores static clear/encoded
  datagram vectors for future packet-trace diffing.
- `network-adaptive-huffman-fixtures-2026-06-05.json` stores deterministic
  packet-byte fixtures, including a profile-91 compressed `connect` datagram.
- `network-demo-capture-replay-validation-2026-06-05.json` defines semantic
  replay lanes for gamestate, snapshots, packet entities, stale deltas,
  fragment reassembly, queued fragment sends, and capture-diff reports.
- `tools/trace/demo_transcript.py` can convert protocol-91 `.dm_91` envelopes
  into reviewable JSON transcripts for future retail evidence submissions.
- `validate_demo_transcript_dict` now validates transcript hashes, offsets,
  terminator sizing, and required retail provenance before fixture closure.
- `tools.trace.capture_diff` now compares future packet-byte captures against
  committed XOR datagrams and compressed-connect Huffman fixtures.
- `tools.trace.fragment_timing` now validates future fragmented-message plus
  queued-follow-up timing reports before closure.
- `tools.trace.invalid_lc_probe` now validates future controlled invalid-`lc`
  retail probe reports before closure.
- `tools.trace.snapshot_decode` now validates future retail snapshot
  player/entity field decode reports before closure.
- `tools.trace.capture_evidence` now validates future evidence bundles that map
  artifacts to the exact residual checklist rows, with a command-line entry
  point at `python -m tools.trace.capture_evidence`.
- Reviewers can require exact residual rows to be submitted for closure with
  `--require-closure-row <row_id>`.
- Reviewers can require every residual external-evidence row to be submitted in
  one final bundle with `--require-all-closure-rows`.
- Reviewers can run final-bundle closure with one stricter flag using
  `--strict-final-closure --artifact-root <repo_root>`, which requires retail
  provenance, every residual row, and matching committed artifact files.
- The capture-evidence CLI can print row contract inventories with
  `--print-row-contracts --row-contract <row_id>`.
- The capture-evidence CLI can print row-scoped capture plans with
  `--print-capture-plan --capture-plan-row <row_id>`, listing required
  evidence, retail provenance keys, reviewed artifact path expectations, and
  helper commands without claiming new evidence.
- The same capture-evidence CLI can print row-scoped, non-claiming templates
  with `--print-template --template-row <row_id>` so future submissions start
  from the validator's allowed artifact formats.
- Future submissions can emit repo-relative artifact path, size, and SHA-256
  inventories with `--hash-artifact <artifact_path> --artifact-root <repo_root>`.
- The capture-evidence CLI can also verify submitted artifact paths and declared
  SHA-256 hashes with `--verify-artifact-files --artifact-root <repo_root>`.
- The capture-evidence CLI can enforce reviewed JSON/text artifact paths with
  `--enforce-artifact-text-policy`, rejecting raw capture/demo/dump/archive
  suffixes before final review.
- The capture-evidence CLI can enforce reviewed evidence directories with
  `--enforce-artifact-path-policy`, rejecting `assets/`, `references/`, and
  source-tree artifact references.
- The capture-evidence CLI can enforce unique artifact IDs and paths with
  `--enforce-artifact-uniqueness-policy`, preventing accidental evidence reuse
  across residual rows.
- The capture-evidence CLI can print a per-row reviewer summary with
  `--print-closure-status`, showing submitted, supporting, not-claimed, and
  missing residual rows without claiming new retail evidence.
- The capture-evidence CLI can print only the blocked rows with
  `--print-closure-blockers`, including accepted artifact formats and next
  actions for partial submissions.
- CI/review jobs can combine `--print-closure-blockers` with
  `--fail-on-closure-blockers` to emit the blocker JSON and return non-zero
  while blockers remain.

Missing external evidence:

- no committed retail packet capture;
- no committed protocol-91 demo transcript with packet bytes;
- no committed fragmented retail server-message capture with a queued follow-up;
- no committed compressed-connect retail trace;
- no controlled retail invalid-`lc` malicious-packet probe result;
- no end-to-end retail snapshot packet/decode report covering both
  `playerStateFields` and `entityStateFields`.

## Blocked Rows

| Checklist row | Current status | Required evidence |
| --- | --- | --- |
| Byte-for-byte replay fixture | Open. The semantic netdump is useful but not packet-byte evidence. | Retail datagram capture, protocol-91 demo-derived transcript, or equivalent known-good byte fixture with provenance. |
| Fragmented snapshot plus queued follow-up timing | Open. Source and HLIL ordering are pinned, and timing-report validation is ready. | Fragmented retail server-message capture and queued follow-up datagram from the same session. |
| XOR golden datagram capture-diff | Open. Static clear/encoded datagram vectors are ready. | Retail packet traces exercising the committed XOR windows. |
| Compressed `connect` capture-diff | Open. Deterministic Huffman fixture is ready. | Retail connect datagram trace with documented challenge/qport inputs. |
| Invalid-`lc` malicious-packet behavior | Open. Source now drops safely, and probe-report validation is ready; exact retail crash/drop behavior is not claimed. | Controlled retail probe plus log or dump classification. |
| End-to-end snapshot field decode | Open. Field tables are retail-locked, and decode-report validation is ready, but packet decode evidence is absent. | Retail snapshot packet capture or protocol-91 transcript covering playerstate and packet entities. |

## Checklist Effect

The outstanding checklist now has a checked blocker-audit row so future passes
can distinguish external evidence gaps from unfinished source reconstruction.
It also has checked transcript-intake, transcript-validation, and capture-diff
tooling rows, plus checked fragment/queue timing-validation and invalid-`lc`
probe-validation rows, plus checked snapshot field decode-validation and
capture evidence bundle-validation rows, including CLI validation,
required-row closure checks, row contract output, capture-plan output,
non-claiming template generation,
all-rows closure checks, artifact hash generation, artifact path/SHA-256 verification,
artifact text-policy checks, artifact path-scope checks, strict final-closure checks,
artifact uniqueness checks, closure-status summaries, and closure-blocker
summaries, plus blocker-fail gates for CI/review jobs.
The actual packet-byte and retail-probe rows remain unchecked.

Estimated parity movement:

- Overall network-protocol source parity remains `90%` -> `90%`.
- Byte-for-byte capture evidence remains `0%` -> `0%`.
- Repo-wide parity remains `99%` -> `99%`.
