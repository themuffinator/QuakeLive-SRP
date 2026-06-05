# Network Protocol Header And Transport Spec - 2026-06-05

## Scope

This note is the human-readable companion for
`docs/reverse-engineering/network-protocol-header-transport-spec-2026-06-05.json`.
It closes the second Critical entry in
`docs/plans/2026-06-05-networking-2.md`: freeze protocol gates and packet
headers for protocol 91, qport behavior, reliable XOR enablement, and
connect/auth compression toggles.

No runtime launch was required. This pass used static source inspection plus
the committed retail HLIL and Ghidra corpus.

## Evidence Used

Owning retail binary:

- `assets/quakelive/quakelive_steam.exe`

Committed reference corpus:

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/exports.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/analysis/quakelive_symbol_aliases.json`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt`

Writable source inspected:

- `src/code/qcommon/qcommon.h`
- `src/code/qcommon/common.c`
- `src/code/qcommon/net_chan.c`
- `src/code/client/cl_main.c`
- `src/code/server/sv_main.c`
- `src/code/client/cl_net_chan.c`
- `src/code/server/sv_net_chan.c`

## Frozen Profile

The active profile is `NETPROFILE_QL_RETAIL` / `ql-retail-steam`.

| Field | Frozen value |
| --- | --- |
| Connect protocol | `91` |
| Demo protocol | `91` |
| Challenge handshake | Enabled |
| Client connect userinfo `qport` | Enabled |
| Sequenced client netchan `qport` | Enabled |
| Reliable XOR codec | Enabled |
| Compressed connect | Enabled |
| Legacy Quake III authorize | Disabled |
| Platform auth | Build gated behind online-service support; not required |
| Workshop content | Build gated |

This keeps live Quake Live online-service behavior in the documented divergence
lane: Steam-era service use remains behind `QL_BUILD_ONLINE_SERVICES` and is
not required for the header grammar frozen here.

## Frozen Packet Headers

Connectionless OOB packets:

- Offset `0`: four-byte sentinel `0xffffffff`.
- Offset `4`: raw command or payload bytes.
- `NET_OutOfBandPrint` and `NET_OutOfBandRaw` remain raw OOB paths.

Compressed `connect` OOB packets:

- Offset `0`: four-byte sentinel `0xffffffff`.
- Offset `4`: clear token `connect`.
- Offset `11`: clear delimiter, normally a space from `connect "%s"`.
- Offset `12`: compressed remainder.
- Client compression uses `Huff_Compress(&mbuf, 12)`.
- Server decompression uses `Huff_Decompress(msg, 12)`.
- `NET_IsConnectRequestPacket` identifies the packet before decompression by
  checking the clear token at offset `4` and accepting `NUL`, space, double
  quote, line feed, or carriage return after the token.

Sequenced client packets:

- Offset `0`: sequence.
- Offset `4`: `qport`, because the active profile enables netchan client
  qport.
- Offset `6`: client message body.

Sequenced server packets:

- Offset `0`: sequence.
- Offset `4`: server message body.

Source `MAX_MSGLEN` is `16384`; committed retail HLIL shows
`Netchan_Transmit` taking the error branch only above `0x8000`. This spec
freezes that observed distinction for follow-up transport parity work rather
than hiding it inside the header table.

Fragmented client packets:

- Offset `0`: sequence with `FRAGMENT_BIT` set.
- Offset `4`: `qport`.
- Offset `6`: fragment start.
- Offset `8`: fragment length.
- Offset `10`: fragment payload.

Fragmented server packets:

- Offset `0`: sequence with `FRAGMENT_BIT` set.
- Offset `4`: fragment start.
- Offset `6`: fragment length.
- Offset `8`: fragment payload.

Client message bodies:

- Offset `0`: `serverId`.
- Offset `4`: `messageAcknowledge`.
- Offset `8`: `reliableAcknowledge`.
- Offset `12`: retail client-message sideband byte.
- Offset `13`: first opcode.
- The parser grammar pass corrected the earlier local conclusion here: retail
  `SV_ExecuteClientMessage` consumes one byte after the three longs and before
  normal opcode parsing.

Server message bodies:

- Offset `0`: `reliableAcknowledge`.
- Offset `4`: first opcode.

## Retail Anchors

| Retail symbol | Address | Observation |
| --- | --- | --- |
| `CL_CheckForResend` | `0x004B9150` | Compressed connect path reaches `NET_OutOfBandData` at `0x004B9314`. |
| `NET_OutOfBandPrint` | `0x004D7080` | Writes four `0xff` bytes and sends raw payload bytes. |
| `NET_OutOfBandData` | `0x004D7120` | Writes four `0xff` bytes and applies Huffman from offset `0x0c`. |
| `Netchan_TransmitNextFragment` | `0x004D7370` | Writes sequence with fragment bit, optional client qport, and fragment metadata. |
| `Netchan_Transmit` | `0x004D74E0` | Rejects payloads above `0x8000` and fragments at `0x514`. |
| `Netchan_Process` | `0x004D7640` | Reads sequence, optional server-side qport, then fragment metadata. |
| `SV_PacketEvent` | `0x004E4500` | Dispatches `0xffffffff` as connectionless, otherwise reads sequence and qport for client lookup. |

## Assertions Added

The parity manifest test now verifies:

- Protocol 91 and the active profile gate values in `qcommon.h` and
  `common.c`.
- Connect userinfo qport inclusion and the compressed-connect send path in
  `CL_CheckForResend`.
- Server-side compressed-connect detection and decompression at offset `12`.
- Netchan qport, fragment, and payload field order for send and receive.
- Retail HLIL anchors for OOB send helpers, netchan transmit/process, and
  `SV_PacketEvent`.
- Plan linkage and completion markers.

## Residual Risks

This entry freezes the header and gate contract, but does not replace the next
tasks:

- Parser golden vectors now live in
  `docs/reverse-engineering/network-client-message-parser-grammar-2026-06-05.json`;
  the remaining parser-side risk is byte-for-byte recovery of the sideband flag
  producers behind retail `sub_4AF4D0` / `data_565948`.
- XOR deterministic vectors and capture-diff checks remain the dedicated XOR
  parity task.
- `entityStateFields` still has a known six-entry retail gap from the previous
  ledger pass.

Estimated parity movement for this task:

- Focused protocol-gate/header slice: `70%` before, `90%` after.
- Overall network-protocol parity: `72%` before, `74%` after.
