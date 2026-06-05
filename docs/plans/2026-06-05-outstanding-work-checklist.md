# Outstanding Work Checklist

Last updated: 2026-06-05

This checklist is a task-level rollup of currently outstanding work from
`IMPLEMENTATION_PLAN.md` and the residual gaps documented by
`docs/plans/2026-06-05-networking-2.md`. It is intentionally short; detailed
evidence and closure notes stay in the owning plans and reverse-engineering
audits.

## Repo-Level Open Tasks

- [x] Task A4: Re-baseline the non-Windows portability lanes.
- [x] Task A4: Decide whether Linux client, renderer, audio, and input support
  are active support targets or bounded server-only compatibility endpoints.
- [x] Task A4: Replace or explicitly classify any remaining Unix `Sys_*`
  helper placeholders after the current bounded lanes.
- [x] Task A4: Refresh Linux/glibc, null-host, and Unix-host docs/tests after
  the intended portability boundary is settled.
- [x] Task A6: Refresh archived build/runtime evidence on current toolchains.
- [x] Task A6: Re-run native Windows build validation where the required
  toolchain is available.
- [x] Task A6: Promote stable `latest` runtime-evidence aliases only after
  sufficient reruns.
- [x] Task A6: Capture remaining glibc and continuous/self-hosted publication
  follow-ups in `docs/platform/toolchain-matrix.md`.
- [x] Task A6: Capture the current Windows native validation preflight blocker
  in `docs/reverse-engineering/windows-native-validation-preflight-2026-06-05.md`.
- [x] Task A6: Refresh the remaining retail-module runtime freshness evidence.

## Networking Residual Closure Work

- [x] Register the existing semantic retail netdump fixture
  `tests/netdumps/retail_duel.snap.json` as known-good snapshot replay
  evidence, with its hashed baseline in
  `tools/tests/client_regression/retail_netdump_baseline.json`.
- [x] 2026-06-05 residual capture-blocker audit: committed evidence inventory
  confirms the packet-byte and retail-probe rows below are externally
  evidence-gated, not hidden source-parity failures.
- [x] Add protocol-91 demo transcript intake tooling so future retail `.dm_91`
  evidence can be committed as reviewed JSON packet-byte transcripts instead of
  binary demo files; no retail transcript is claimed by this row.
- [x] Add protocol-91 transcript validation gates for hashes, offsets,
  terminators, and required retail provenance before any JSON byte fixture can
  close the replay-validation row.
- [x] Add residual capture evidence bundle validation gates so future retail
  packet/demo/probe/decode submissions map artifacts to the exact open
  checklist rows; no retail evidence bundle is claimed by this row.
- [x] Add a command-line validator for residual capture evidence bundles so
  future closure submissions can run the same row/format/provenance checks used
  by the manifest tests; no retail evidence bundle is claimed by this row.
- [x] Add command-line residual capture evidence required-row checks so future
  closure submissions must prove the exact checklist row being closed is
  submitted for closure; no retail evidence bundle is claimed by this row.
- [x] Add command-line residual capture evidence row contract output so future
  submissions and reviews can list row IDs, checklist text, and allowed
  artifact formats; no retail evidence bundle is claimed by this row.
- [x] Add command-line residual capture evidence capture-plan output so future
  submissions can list required retail evidence, provenance keys, reviewed
  artifact path expectations, and helper commands by row; no retail evidence
  bundle is claimed by this row.
- [x] Add command-line residual capture evidence bundle template generation so
  future submissions can start from row-scoped allowed artifact formats; no
  retail evidence bundle is claimed by this row.
- [x] Add command-line residual capture evidence artifact hash generation so
  future submissions can populate repo-relative path, size, and SHA-256 fields;
  no retail evidence bundle is claimed by this row.
- [x] Add command-line residual capture evidence artifact path/SHA-256
  verification so future committed bundles prove their referenced files are
  present; no retail evidence bundle is claimed by this row.
- [x] Add command-line residual capture evidence closure-status summaries so
  future reviews can see which rows are submitted, supporting, not claimed, or
  missing; no retail evidence bundle is claimed by this row.
- [x] Add command-line residual capture evidence all-rows closure checks so a
  future final bundle must submit every external-evidence row together; no
  retail evidence bundle is claimed by this row.
- [x] Add command-line residual capture evidence strict final-closure checks so
  future final review can require retail provenance, all residual rows, and
  artifact file verification with one flag; no retail evidence bundle is
  claimed by this row.
- [x] Add command-line residual capture evidence closure-blocker reports so
  future reviewers can see the exact blocked rows, accepted artifact formats,
  and next actions from a partial bundle; no retail evidence bundle is claimed
  by this row.
- [x] Add command-line residual capture evidence blocker-fail gates so future
  CI/review jobs can return non-zero when required rows still have closure
  blockers; no retail evidence bundle is claimed by this row.
- [x] Add command-line residual capture evidence artifact text-policy checks so
  future submissions use reviewed JSON/text evidence paths instead of raw
  binary capture/demo/dump/archive artifacts; no retail evidence bundle is
  claimed by this row.
- [x] Add command-line residual capture evidence artifact path-scope checks so
  future submissions keep evidence references under reviewed evidence
  directories and away from `assets/`, `references/`, and source trees; no
  retail evidence bundle is claimed by this row.
- [x] Add command-line residual capture evidence artifact uniqueness checks so
  future final bundles cannot accidentally reuse artifact IDs or paths across
  multiple closure rows; no retail evidence bundle is claimed by this row.
- [ ] Commit at least one retail packet capture, protocol-91 demo transcript,
  or equivalent known-good capture fixture for byte-for-byte replay validation.
- [x] Add capture-scoped adaptive Huffman fixtures for final packet-byte
  comparison.
- [x] Add packet-byte capture-diff tooling for committed XOR datagram vectors
  and compressed `connect` Huffman fixtures; no retail trace is claimed by this
  tooling row.
- [x] Add fragmented snapshot/queued follow-up timing report validation gates
  for terminal fragment acceptance and queued-message encode-on-pop behavior;
  no retail trace is claimed by this tooling row.
- [ ] Validate fragmented snapshot plus queued follow-up timing against a
  byte-for-byte retail capture.
- [ ] Capture-diff the XOR golden datagrams against retail packet traces.
- [x] Map the observed retail sideband producers behind `sub_4AF4D0` /
  `data_565948` and implement the constant `0x80` initializer bit in
  `CL_RetailClientMessageFlags()`.
- [x] Recover the retail `0x20` `CL_Frame` viewangle-delta sideband producer
  and wire it into the persistent `CL_RetailClientMessageFlags()` byte.
- [x] Recover the retail low-five renderer counter bits behind `sub_43C120` /
  `R_PerformanceCounters()` and wire them into the persistent
  `CL_RetailClientMessageFlags()` byte.
- [x] Recover the retail `0x40` native cgame/import guard behind retail
  `sub_4AF4D0` / `data_565948` so the client-message sideband byte becomes
  source-complete; capture-backed byte comparison remains tracked above.
- [ ] Capture-diff the compressed `connect` request path against a retail trace.
- [x] Add invalid-`lc` controlled retail probe report validation gates for
  source `ERR_DROP` comparison and hashed retail crash/drop artifacts; no
  retail probe is claimed by this tooling row.
- [ ] Probe invalid-`lc` malicious packet behavior against retail before
  claiming exact crash/drop equivalence.
- [x] Add snapshot field decode report validation gates for future
  `playerStateFields` and `entityStateFields` retail packet/decode evidence;
  no retail snapshot capture is claimed by this tooling row.
- [ ] Verify end-to-end retail snapshot capture/decode parity for
  `playerStateFields` and `entityStateFields`.

## Ongoing Policy And Planning Checks

- [ ] Keep Quake Live-only online-service replacements behind
  `QL_BUILD_ONLINE_SERVICES` unless a documented open replacement path exists.
- [x] 2026-06-05 spot-check: default online-service policy still routes through
  `QL_BUILD_ONLINE_SERVICES=0` and build-disabled descriptors.
- [x] 2026-06-05 lane inventory: known Steamworks, open-adapter, Awesomium,
  and Steam-resource bridge paths are documented with compile-time or runtime
  policy gates; no online-service lane is enabled by this row.
- [x] 2026-06-05 call-site/stub inventory: auth dispatch, Steamworks stubs,
  common startup/frame hooks, client Steam frame/init, and Windows net restart
  hooks are documented against their default-disabled gates; no online-service
  lane is enabled by this row.
- [ ] Check the ownerdraw parity indexes before starting new UI work, since
  `src/ui/` is read-only for agents and any remaining menu-owner gaps need a
  documentation-first path.
- [x] 2026-06-05 spot-check: `ui-ownerdrawtype-parity-index.md` was reviewed;
  no `src/ui/` edits were made and the remaining `UI_KEYBINDSTATUS` /
  retail-no-op decisions stay documentation-first.
- [x] 2026-06-05 ownerdraw follow-up inventory: `UI_KEYBINDSTATUS`, the
  retail no-op/source legacy ID set, and `UI_VOTE_KICK` are documented as
  separate evidence lanes before any `src/ui/` owner changes; no `src/ui/`
  edits were made by this row.
- [x] 2026-06-05 manifest guard: residual policy spot-check is backed by
  source/manifest assertions for default-disabled online services,
  build-disabled descriptors, and documentation-first ownerdraw follow-ups.

## Source References

- `IMPLEMENTATION_PLAN.md`
- `docs/reverse-engineering/runtime-build-evidence-refresh-2026-06-05.md`
- `docs/reverse-engineering/non-windows-portability-boundary-2026-06-05.md`
- `docs/reverse-engineering/windows-native-validation-preflight-2026-06-05.md`
- `docs/reverse-engineering/residual-policy-spot-check-2026-06-05.md`
- `docs/plans/2026-06-05-networking-2.md`
- `docs/reverse-engineering/network-client-message-sideband-producers-2026-06-05.md`
- `docs/reverse-engineering/network-adaptive-huffman-fixtures-2026-06-05.md`
- `docs/reverse-engineering/network-capture-diff-tooling-2026-06-05.md`
- `docs/reverse-engineering/network-capture-evidence-bundle-validation-2026-06-05.md`
- `docs/reverse-engineering/network-capture-fixture-validation-2026-06-05.md`
- `docs/reverse-engineering/network-demo-capture-replay-validation-2026-06-05.md`
- `docs/reverse-engineering/network-demo-transcript-intake-2026-06-05.md`
- `docs/reverse-engineering/network-fragment-queue-timing-validation-2026-06-05.md`
- `docs/reverse-engineering/network-invalid-lc-probe-validation-2026-06-05.md`
- `docs/reverse-engineering/network-residual-capture-blockers-2026-06-05.md`
- `docs/reverse-engineering/network-snapshot-field-decode-validation-2026-06-05.md`
- `docs/reverse-engineering/network-protocol-hardening-parity-2026-06-05.md`
