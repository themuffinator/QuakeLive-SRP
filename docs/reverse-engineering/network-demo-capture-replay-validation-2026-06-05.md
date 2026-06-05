# Network Demo/Capture Replay Validation - 2026-06-05

## Scope

This note is the human-readable companion for
`docs/reverse-engineering/network-demo-capture-replay-validation-2026-06-05.json`.
It closes the Medium implementation-plan entry in
`docs/plans/2026-06-05-networking-2.md`: build demo/capture replay
validation for baselines, snapshots, delta aging, and fragment reassembly.

No runtime launch was required. The repository does not currently contain a
retail packet capture or protocol-91 demo transcript, so this pass adds the
static replay contract, semantic diff lanes, and regression assertions that a
future byte-for-byte fixture must satisfy.

## Evidence Used

Owning retail binary:

- `assets/quakelive/quakelive_steam.exe`

Committed reference corpus:

- `references/analysis/quakelive_symbol_aliases.json`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt`

Writable source inspected:

- `src/code/client/cl_parse.c`
- `src/code/server/sv_snapshot.c`
- `src/code/server/sv_net_chan.c`
- `src/code/qcommon/net_chan.c`
- `src/code/qcommon/msg.c`

## Result

The replay validation surface is now explicit and machine-readable. The new
contract defines the lanes that future captures must replay and the semantic
columns that should appear in diff reports.

The repository also already carries one known-good semantic retail netdump:
`tests/netdumps/retail_duel.snap.json`, with deterministic HUD and usercmd hash
baselines in `tools/tests/client_regression/retail_netdump_baseline.json`.
This fixture is useful replay evidence for ordered retail snapshot frames, but
it is not a byte-for-byte packet capture, protocol-91 demo transcript, or
capture-scoped Huffman fixture.

| Lane | Retail/source conclusion | Diff shape |
| --- | --- | --- |
| Gamestate baseline replay | `CL_ParseGamestate` reads configstrings, rebuilds baselines from a zero `entityState_t`, then reads `clientNum` and `checksumFeed`. | Server command sequence, configstring index, baseline number/hash, client number, checksum feed. |
| Snapshot delta replay | `SV_WriteSnapshotToClient` and `CL_ParseSnapshot` agree on `svc_snapshot`, `serverTime`, `lastframe`/`deltaNum`, `snapFlags`, areamask, playerstate, then packet entities. | Message number, server time, delta number, snap flags, areamask bytes, playerstate hash, entity count. |
| Packet entity merge replay | Server and client preserve unchanged, delta-from-old, delta-from-baseline/new, removed, and sentinel cases. | Entity number, merge case, base source, delta hash, state hash, removed flag. |
| Delta aging rejection | The client rejects invalid, mismatched, and parse-entity-stale delta frames while still consuming the message. | Delta source validity, message mismatch, parse-entity age, accepted flag. |
| Fragment reassembly replay | `Netchan_Process` enforces contiguous fragments and rebuilds the terminal fragment into a normal sequenced message. | Sequence, fragment start/length, accumulated length, accepted flag, payload hash. |
| Queued fragment send replay | `SV_Netchan_Transmit` queues unencoded follow-up messages behind active fragments; `SV_Netchan_TransmitNextFragment` encodes them only when popped. | Queue index, stored-encoded flag, encoded-on-pop flag, queue-empty flag, datagram hash. |
| Capture diff report contract | Missing external captures are a fixture gap, not a source failure. Semantic reports are valid until packet-byte fixtures are committed. | Fixture id/type, lane id, expected/actual hashes, match kind, status. |

## Retail Anchors

| Retail symbol | Address | Observation |
| --- | --- | --- |
| `CL_ParsePacketEntities` | `0x004BD000` | Reads 10-bit entity numbers, merges unchanged/delta/baseline cases, and terminates at `0x3ff`. |
| `CL_ParseSnapshot` | `0x004BD350` | Reads snapshot fields and rejects stale delta frames before committing `cl.snap`. |
| `CL_ParseGamestate` | `0x004BD790` | Rebuilds baselines from zero entity state storage and reads `checksumFeed`. |
| `Netchan_TransmitNextFragment` | `0x004D7370` | Writes sequence, optional qport, fragment start/length, and payload. |
| `Netchan_Transmit` | `0x004D74E0` | Starts the fragment train for large messages. |
| `Netchan_Process` | `0x004D7640` | Enforces fragment order and copies terminal reassembly to `msg->data + 4`. |
| `SV_Netchan_TransmitNextFragment` | `0x004E4E20` | Pops and send-time-encodes queued messages after the active fragment train. |
| `SV_Netchan_Transmit` | `0x004E4EE0` | Queues unencoded follow-up messages behind active fragments. |
| `SV_EmitPacketEntities` | `0x004E4FC0` | Emits entity delta/new/remove cases plus the terminal sentinel. |
| `SV_WriteSnapshotToClient` | `0x004E50E0` | Writes the snapshot packet body in retail order. |
| `SV_BuildClientSnapshot` | `0x004E5680` | Builds the snapshot consumed by the writer. |

## Assertions Added

The parity manifest test now verifies:

- The replay spec depends on all prior networking-2 serializers/parsers.
- Every replay lane has the expected retail anchor and semantic diff columns.
- `CL_ParseGamestate` keeps baseline reconstruction from a zero `nullstate`
  before `clientNum` and `checksumFeed`.
- `CL_ParseSnapshot` resolves uncompressed and delta snapshots, checks invalid
  and stale delta sources, reads areamask/playerstate/entities, and commits
  only valid snapshots.
- `CL_ParsePacketEntities` and `SV_EmitPacketEntities` preserve unchanged,
  delta, baseline/new, removed, and sentinel behavior.
- `Netchan_Process` preserves fragment-order checks and terminal reassembly
  state (`cursize`, `readcount`, and `bit`).
- Server-side queued fragment sends remain unencoded while queued and are
  encoded only when popped for transmit.
- Retail HLIL contains the same parse, snapshot, fragment, and queue anchors.

## Residual Risks

This pass intentionally does not claim byte-for-byte replay completion. The
remaining gap is external evidence:

- No committed retail packet capture or protocol-91 demo transcript is
  available for final packet-byte replay. The existing
  `tests/netdumps/retail_duel.snap.json` fixture is semantic snapshot evidence
  only.
- Capture-scoped adaptive Huffman fixtures are now defined in
  `network-adaptive-huffman-fixtures-2026-06-05.md`; external retail captures
  are still needed for byte-for-byte replay.
- Fragmented snapshot plus queued follow-up timing is statically pinned but
  still needs a capture for byte-for-byte timing validation.

Estimated parity movement for this task:

- Focused demo/capture replay validation slice: `45%` before, `78%` after.
- Overall network-protocol parity: `85%` before, `86%` after.
