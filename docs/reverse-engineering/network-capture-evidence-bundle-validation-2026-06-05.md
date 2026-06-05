# Network Capture Evidence Bundle Validation - 2026-06-05

## Scope

This note adds a bundle-level validation gate for future retail packet, demo,
probe, and snapshot-decode evidence submitted against the residual networking
checklist rows.

No runtime or game launch was required. No retail capture, probe, or decode
artifact is claimed by this pass.

## Validation Contract

`tools.trace.capture_evidence.validate_capture_evidence_bundle_dict` accepts
reviewable JSON reports with format `quake_live_capture_evidence_bundle`.

The validator maps evidence to the remaining residual rows:

- byte-for-byte replay fixture;
- fragmented snapshot plus queued follow-up timing;
- XOR golden datagram capture-diff;
- compressed `connect` capture-diff;
- invalid-`lc` retail probe;
- end-to-end snapshot field decode.

Each closure target must identify a known row, declare whether it is submitted
for closure or only supporting evidence, and provide hashed artifacts with
allowed formats for that row. Embedded reports are delegated to the existing
row-specific validators. Closure capture-diff reports must be full matches.

The same validation is available from the command line:

```powershell
python -m tools.trace.capture_evidence path\to\bundle.json --require-retail-provenance
```

For embedded snapshot decode reports, pass the recovered field-table specs with
`--playerstate-spec` and `--entitystate-spec`.

Reviewers can require one or more specific residual rows to be submitted for
closure:

```powershell
python -m tools.trace.capture_evidence path\to\bundle.json --require-closure-row xor_golden_datagrams
```

Each required row must appear with `submitted_for_closure` status; supporting or
non-claiming targets do not satisfy the requirement.

For final closure review, reviewers can require every residual row in one pass:

```powershell
python -m tools.trace.capture_evidence path\to\bundle.json --require-all-closure-rows
```

This is equivalent to requiring all six residual row IDs. It is a completeness
gate for submitted bundles and does not add or claim retail capture evidence by
itself.

For final bundle review, strict mode composes the closure gates that must hold
for a submitted bundle:

```powershell
python -m tools.trace.capture_evidence path\to\bundle.json --strict-final-closure --artifact-root .
```

Strict final closure requires retail provenance, every residual row submitted
for closure, and artifact files that exist under the artifact root with matching
SHA-256 hashes. It is still a review gate only and does not create or claim
retail capture evidence.

The CLI can print the residual row contract inventory:

```powershell
python -m tools.trace.capture_evidence --print-row-contracts --row-contract xor_golden_datagrams
```

Each row contract lists the row ID, checklist text, allowed artifact formats,
artifact types, and accepted closure target statuses.

The CLI can also print a row-scoped capture plan:

```powershell
python -m tools.trace.capture_evidence --print-capture-plan --capture-plan-row compressed_connect_capture_diff
```

The capture plan lists required evidence, retail provenance keys, reviewed
artifact path/suffix expectations, and helper commands for templates, row
contracts, hashing, and strict final review. It is a collection aid only and
does not claim that retail evidence has been captured or committed.

The CLI can also print a non-claiming template for future submissions:

```powershell
python -m tools.trace.capture_evidence --print-template --template-row xor_golden_datagrams
```

Template targets are emitted as `not_claimed` with empty `artifacts` arrays and
row-specific `artifact_templates`; a reviewer must fill real paths, hashes,
reports, and switch the target status before closure validation can pass.

Artifact hashes for bundle population can be generated from repo-relative paths:

```powershell
python -m tools.trace.capture_evidence --hash-artifact docs\reverse-engineering\fixtures\retail-demo.json --artifact-root .
```

The output records the repo-relative path, byte size, and lowercase SHA-256 for
each submitted file.

For reviewer triage, the CLI can print a per-row closure status report for a
validated bundle:

```powershell
python -m tools.trace.capture_evidence path\to\bundle.json --print-closure-status
```

The status report lists every residual row as submitted, supporting evidence,
not claimed, or missing, with artifact counts and closure blockers. This is a
review aid only; it does not turn a non-claiming bundle into retail evidence.

The CLI can also print just the blocked residual rows from a partial bundle:

```powershell
python -m tools.trace.capture_evidence path\to\bundle.json --print-closure-blockers
```

The blocker report includes the blocked row IDs, checklist text, current target
status, closure blocker, accepted artifact formats, artifact types, and a short
next action. It is a triage aid only and does not turn partial evidence into a
closure claim.

CI or scripted review jobs can turn remaining blockers into a non-zero exit:

```powershell
python -m tools.trace.capture_evidence path\to\bundle.json --print-closure-blockers --fail-on-closure-blockers
```

When combined with `--print-closure-blockers`, the command still prints the
blocker JSON before returning non-zero. This is a review gate only and does not
add or claim retail capture evidence.

For committed submissions, the CLI can additionally verify artifact files under
a repository root:

```powershell
python -m tools.trace.capture_evidence path\to\bundle.json --verify-artifact-files --artifact-root .
```

This pass checks that every declared artifact path is repo-relative, stays under
the artifact root, exists on disk, and matches the declared lowercase SHA-256
hash. It does not inspect binary capture contents beyond the hash match.

Reviewers can also require evidence paths to stay in reviewed text fixtures:

```powershell
python -m tools.trace.capture_evidence path\to\bundle.json --enforce-artifact-text-policy
```

The text-policy gate accepts `.json`, `.md`, and `.txt` artifact paths and
rejects raw capture/demo/dump/archive suffixes such as `.pcap`, `.pcapng`,
`.dm_91`, `.dmp`, and `.zip`. This keeps future submissions aligned with the
repo preference for reviewed text evidence and does not add or claim retail
capture evidence.

Reviewers can require artifact paths to stay under reviewed evidence
directories:

```powershell
python -m tools.trace.capture_evidence path\to\bundle.json --enforce-artifact-path-policy
```

The path-scope gate accepts evidence paths under
`docs/reverse-engineering/fixtures/`, `docs/reverse-engineering/evidence/`,
`tests/netdumps/`, and `tools/tests/client_regression/`; it rejects paths under
`assets/`, `references/`, and source trees. This is a review hygiene check only
and does not add or claim retail capture evidence.

Reviewers can reject accidental artifact reuse across rows:

```powershell
python -m tools.trace.capture_evidence path\to\bundle.json --enforce-artifact-uniqueness-policy
```

The uniqueness gate requires artifact IDs and artifact paths to be unique across
the whole bundle. This prevents a final bundle from reusing one reviewed report
as evidence for multiple residual rows by mistake and does not add or claim
retail capture evidence.

Closure mode requires provenance for the bundle and at least one submitted
closure target. The actual residual rows remain open until retail evidence is
committed.

## Checklist Effect

The outstanding checklist now has checked support rows for capture evidence
bundle validation, command-line bundle validation, required-row closure checks,
all-rows closure checks, strict final-closure checks, row contract output, and
capture-plan output, and non-claiming template generation, plus artifact hash
generation, closure-status reporting, closure-blocker reporting, blocker-fail
gates, and artifact
path/SHA-256 verification, text-policy checks, and path-scope checks for
committed evidence bundles, plus artifact uniqueness checks. The actual
packet-byte, capture-diff, retail-probe, and snapshot-decode rows remain open.

Estimated parity movement:

- Overall network-protocol source parity remains `90%` -> `90%`.
- Byte-for-byte capture evidence remains `0%` -> `0%`.
- Repo-wide parity remains `99%` -> `99%`.
