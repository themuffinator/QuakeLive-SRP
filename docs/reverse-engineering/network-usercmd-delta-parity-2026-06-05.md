# Network Usercmd Delta Parity

Date: 2026-06-05

Scope: fifth entry in `docs/plans/2026-06-05-networking-2.md`, finalizing `usercmd_t` keyed and unkeyed delta parity with exact struct offsets, serializer order, and deterministic logical vectors.

## Evidence

Retail anchors from the committed `quakelive_steam.exe` HLIL corpus:

| Retail function | Address | Parity observation |
|---|---:|---|
| `MSG_WriteDeltaUsercmdKey` | `0x004D51A0` | Writes compact or full `serverTime`, checks all non-time fields for the no-change fast path, xors the key with `to->serverTime`, then writes angle, movement, button, weapon, `weaponPrimary`, and `fov` deltas. |
| `MSG_ReadDeltaUsercmdKey` | `0x004D54A0` | Reads compact or full `serverTime`, copies all non-time fields when the changed-command bit is clear, otherwise applies `key ^ serverTime` to the same field order. |
| `CL_WritePacket` | `0x004B5F70` | Calls `MSG_WriteDeltaUsercmdKey` for each outgoing command using the previous command as baseline. |
| `SV_UserMove` | `0x004E0320` | Calls `MSG_ReadDeltaUsercmdKey` for each incoming command using the previous decoded command as baseline. |

Retail HLIL confirms the compact `usercmd_t` layout:

| Field | Offset | Wire role |
|---|---:|---|
| `serverTime` | `0x00` | Always sent as compact delta or full 32-bit time. |
| `angles[0..2]` | `0x04` | Three 16-bit delta fields. |
| `buttons` | `0x10` | 16-bit delta field. |
| `weapon` | `0x14` | 8-bit delta field. |
| `weaponPrimary` | `0x15` | Quake Live command-tail byte. |
| `fov` | `0x16` | Quake Live command-tail byte. |
| `forwardmove`, `rightmove`, `upmove` | `0x17`, `0x18`, `0x19` | Signed command-axis bytes serialized as 8-bit payloads. |

The source layout in `src/code/game/q_shared.h` and the delta pair in `src/code/qcommon/msg.c` match those offsets and the retail wire order. The buffered-client-command stride observed in `CL_WritePacket` is `0x1c`, matching the aligned source `sizeof(usercmd_t)`.

## Logical Vectors

The machine-readable source of truth is:

- `docs/reverse-engineering/network-usercmd-delta-parity-2026-06-05.json`

The vectors are logical `MSG_WriteBits` transcripts rather than final packet bytes. That distinction matters because regular message payload bytes go through the adaptive Huffman bitstream layer. The stable parity surface for this task is the deterministic sequence of change bits, payload widths, keyed payload values, and decoded semantic fields.

Covered vectors:

| Vector | Path | Coverage |
|---|---|---|
| `keyed_compact_all_fields_changed` | keyed | Compact 8-bit time delta, changed-command bit, all fields changed, signed movement axes, `weaponPrimary`, and `fov`. |
| `keyed_compact_no_field_changes` | keyed | Compact 8-bit time delta plus changed-command bit `0`, proving non-time fields are copied from the baseline. |
| `keyed_full_time_tail_only` | keyed | Full 32-bit time fallback with only `weaponPrimary` and `fov` changed. |
| `unkeyed_compact_all_fields_changed` | unkeyed | Compact 8-bit time delta with all fields changed and unkeyed payload values. |
| `unkeyed_full_time_tail_only` | unkeyed | Full 32-bit time fallback with only the Quake Live command-tail fields changed. |

The keyed and unkeyed vectors intentionally do not share payload expectations. For example, the `keyed_full_time_tail_only` vector writes `weaponPrimary` as `0x00` after `0x0badc0de ^ 2000`, while the matching unkeyed tail-only vector writes the literal `0x0e`.

## Completion

Status: `completed_static_struct_layout_and_logical_vectors`

Validation added:

- `tests/test_netcode_parity_manifest.py::test_networking_2_usercmd_delta_struct_layout_and_logical_vectors`

Estimated parity movement for this task: focused `usercmd_t` delta slice `78%` -> `94%`; overall network-protocol parity `78%` -> `80%`.

Residual risk: capture-scoped adaptive Huffman fixtures are now pinned in `network-adaptive-huffman-fixtures-2026-06-05.md`, but full usercmd packet-byte replay still requires capture-specific message ordering or an external retail capture. No source patch or runtime launch was needed for this pass.
