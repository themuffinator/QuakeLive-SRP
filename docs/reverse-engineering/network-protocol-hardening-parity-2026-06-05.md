# Network Protocol Hardening Parity - 2026-06-05

## Scope

This note is the human-readable companion for
`docs/reverse-engineering/network-protocol-hardening-parity-2026-06-05.json`.
It closes the final Medium implementation-plan entry in
`docs/plans/2026-06-05-networking-2.md`: harden invalid `lc`, fragment edge
cases, command-ring wraparound, and stale delta frames.

No runtime launch was required. This pass used static source inspection plus
the committed retail HLIL and symbol-alias corpus.

## Evidence Used

Owning retail binary:

- `assets/quakelive/quakelive_steam.exe`

Committed reference corpus:

- `references/analysis/quakelive_symbol_aliases.json`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt`

Writable source inspected and patched:

- `src/code/qcommon/msg.c`
- `src/code/qcommon/net_chan.c`
- `src/code/client/cl_parse.c`
- `src/code/client/cl_net_chan.c`
- `src/code/server/sv_client.c`
- `src/code/server/sv_net_chan.c`
- `src/code/server/sv_snapshot.c`

## Result

The hardening surface is now explicit and regression-tested.

| Lane | Result |
| --- | --- |
| Invalid entity `lc` | `MSG_ReadDeltaEntity` now drops if wire `lc` exceeds the recovered `entityStateFields` count. |
| Invalid playerstate `lc` | `MSG_ReadDeltaPlayerstate` now drops if wire `lc` exceeds the recovered `playerStateFields` count. |
| Fragment edges | Existing `Netchan_Process` checks reject stale sequences, non-contiguous fragments, illegal lengths, buffer overflow, and oversized terminal reassembly. |
| Command rings | Client/server reliable command paths use monotonic sequence checks and `MAX_RELIABLE_COMMANDS - 1` ring masks. |
| Stale delta frames | Client snapshot parsing rejects invalid, mismatched, and parse-entity-stale delta sources; server snapshot writing falls back to uncompressed snapshots when delta sources are too old. |
| Usercmd counts | `SV_UserMove` rejects `cmdCount < 1` and `cmdCount > MAX_PACKET_USERCMDS` before reading keyed usercmd deltas. |
| Bad opcodes/read past end | Client server-message parsing drops illegible server opcodes and read-past-end messages; server parser warns on unexpected client command bytes. |

The only source patch in this pass is the invalid-`lc` guard. The committed
retail HLIL shows both delta readers using 58-entry field tables, but it does
not show a safe pre-walk bounds guard before consuming wire `lc`. The source
now treats `lc > 58` as malformed input and drops before indexing past the
recovered retail tables.

## Retail Anchors

| Retail symbol | Address | Observation |
| --- | --- | --- |
| `MSG_ReadDeltaEntity` | `0x004D5AC0` | Reads an 8-bit `lc` and uses the 58-entry `entityStateFields` table. |
| `MSG_ReadDeltaPlayerstate` | `0x004D66C0` | Reads an 8-bit `lc` and uses the 58-entry `playerStateFields` table. |
| `Netchan_Process` | `0x004D7640` | Rejects out-of-order, non-contiguous, and illegal fragments and accepts only terminal reassembly. |
| `CL_ParseServerMessage` | `0x004BDA00` | Parses reliable acknowledgements, server opcodes, and bad-message drop paths. |
| `CL_ParseSnapshot` | `0x004BD350` | Rejects invalid, mismatched, and parse-entity-stale delta frames. |
| `CL_ParseCommandString` | `0x004BDAB0` | Stores server commands through the reliable command ring. |
| `SV_UserMove` | `0x004E0320` | Bounds usercmd counts before reading keyed usercmd deltas. |
| `SV_ExecuteClientMessage` | `0x004E05C0` | Validates stale acknowledgements and dispatches client move opcodes. |
| `SV_WriteSnapshotToClient` | `0x004E50E0` | Falls back to uncompressed snapshots when delta sources are too old. |

## Assertions Added

The parity manifest test now verifies:

- Both delta readers guard `lc` immediately after `MSG_ReadByte` and before
  field-table iteration or tail-copy indexing.
- The recovered playerstate/entity field counts remain `58`.
- Netchan fragment processing preserves out-of-order, gap, illegal-length,
  nonterminal, and terminal-reassembly behavior.
- Client/server reliable acknowledgements are clamped or rejected before stale
  ring-indexed command ranges can expand.
- Command-string ring storage and XOR command-string selection use
  `MAX_RELIABLE_COMMANDS - 1` masks.
- Snapshot stale-delta rejection remains aligned with the `1920` parse-entity
  age threshold.
- `SV_UserMove` still rejects invalid command counts before reading deltas.
- Retail HLIL anchors remain present for the hardening owners.

## Residual Risks

- Invalid `lc` handling is intentionally source-hardened with `ERR_DROP`
  guards. The committed retail HLIL does not show a safe pre-walk guard, so
  exact malicious-packet equivalence remains an external retail-probe question.
- Byte-for-byte malicious-packet behavior still needs a controlled retail
  capture or probe before claiming exact crash/drop parity.
- The retail sideband producers behind `CL_RetailClientMessageFlags` are now
  source-modeled; byte-for-byte sideband validation remains a packet-capture
  follow-up.

Estimated parity movement for this task:

- Focused protocol-hardening slice: `58%` before, `88%` after.
- Overall network-protocol parity: `86%` before, `87%` after.
