# Network XOR Codec Parity

Date: 2026-06-05

Scope: fourth entry in `docs/plans/2026-06-05-networking-2.md`, finalizing the reliable XOR netchan codec with deterministic golden vectors and capture-diff-ready packet bytes.

## Evidence

Retail anchors from the committed `quakelive_steam.exe` HLIL corpus:

| Retail function | Address | Parity observation |
|---|---:|---|
| `CL_Netchan_Encode` | `0x004BCE30` | Reads `serverId`, `messageAcknowledge`, and `reliableAcknowledge`, computes `challenge ^ serverId ^ messageAcknowledge`, and starts the XOR window at body offset `0x0c`. |
| `CL_Netchan_Decode` | `0x004BCEF0` | Reads `reliableAcknowledge`, computes `challenge ^ netchan sequence`, and starts decoding at `msg->readcount + 4`. |
| `SV_Netchan_Encode` | `0x004E4CD0` | Reads `reliableAcknowledge`, computes `client challenge ^ outgoingSequence`, uses `lastClientCommandString`, and starts at body offset `4`. |
| `SV_Netchan_Decode` | `0x004E4D70` | Reads the three client body longs, computes `client challenge ^ serverId ^ messageAcknowledge`, and starts at `msg->readcount + 0x0c`. |

The committed source matches those windows:

- Client to server: `CL_ENCODE_START == 12`, `SV_DECODE_START == 12`.
- Server to client: `SV_ENCODE_START == 4`, `CL_DECODE_START == 4`.
- Both directions fold command-string bytes greater than `0x7f` or equal to `%` (`0x25`) to `.` (`0x2e`) before mixing the rolling byte key.

## Golden Vectors

The machine-readable source of truth is:

- `docs/reverse-engineering/network-xor-codec-parity-2026-06-05.json`

The vector suite covers four cases:

| Vector | Direction | Clear body | Encoded body |
|---|---|---|---|
| `client_to_server_sideband_move` | client to server | `04 03 02 01 0d 0c 0b 0a 02 00 00 00 77 02 01 05` | `04 03 02 01 0d 0c 0b 0a 02 00 00 00 45 f4 94 52` |
| `client_to_server_sanitized_command_bytes` | client to server | `04 03 02 01 0d 0c 0b 0a 02 00 00 00 10 20 30 40 05` | `04 03 02 01 0d 0c 0b 0a 02 00 00 00 6d 01 6b 47 2c` |
| `server_to_client_reliable_acknowledge` | server to client | `03 00 00 00 55 aa 99 06` | `03 00 00 00 0e 33 79 00` |
| `server_to_client_sanitized_command_bytes` | server to client | `03 00 00 00 10 20 30 40 06` | `03 00 00 00 16 7a 1b 37 5f` |

The first client vector intentionally exercises the parser-side correction from the previous task: the retail client-message sideband byte at body offset `12` is inside the XOR window. The three header longs remain clear, and client body byte 12 changes from `0x77` to `0x45`.

## Capture-Diff Readiness

No external retail packet capture is committed for this row yet. To keep the check deterministic and replayable, the JSON spec stores full unfragmented datagram bytes alongside the body vectors:

- Client to server vectors include the netchan `sequence` and `qport` prefix before the body.
- Server to client vectors include the netchan `sequence` prefix before the body.
- The assertion test replays the same XOR loop over both body bytes and datagram bytes, using the correct post-`Netchan_Process` read cursor.

That gives future capture work a byte-for-byte target without needing to reinterpret the codec rules.

## Completion

Status: `completed_static_golden_vectors_capture_diff_ready`

Validation added:

- `tests/test_netcode_parity_manifest.py::test_networking_2_xor_codec_golden_vectors_and_capture_diff_windows`

Estimated parity movement for this task: focused XOR codec slice `80%` -> `94%`; overall network-protocol parity `76%` -> `78%`.

Residual risk: the full retail capture replay is still pending because no committed external retail packet capture is available. The client-message flag producer behind retail `sub_4AF4D0` also remains a follow-up, but the codec now explicitly protects the sideband byte inside the client-to-server XOR window.
