# Network Client Message Parser Grammar - 2026-06-05

## Scope

This note is the human-readable companion for
`docs/reverse-engineering/network-client-message-parser-grammar-2026-06-05.json`.
It closes the third Critical entry in
`docs/plans/2026-06-05-networking-2.md`: verify the protocol 91
client-message parser header semantics, including the reported extra byte after
the three header longs.

No runtime launch was required. This pass used static source inspection plus
the committed retail HLIL and Ghidra corpus.

## Evidence Used

Owning retail binary:

- `assets/quakelive/quakelive_steam.exe`

Committed reference corpus:

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/analysis/quakelive_symbol_aliases.json`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`

Writable source inspected and patched:

- `src/code/client/cl_input.c`
- `src/code/server/sv_client.c`
- `src/code/client/cl_net_chan.c`
- `src/code/server/sv_net_chan.c`
- `src/code/qcommon/qcommon.h`
- `src/code/qcommon/msg.c`

## Corrected Parser Shape

The earlier local ledger note said committed `SV_ExecuteClientMessage` HLIL
contradicted the external extra-byte claim. That was too optimistic. A closer
pass shows retail has the extra byte:

- Retail `CL_WritePacket` at `0x004B5F70` writes three `MSG_WriteLong` fields,
  then writes one `MSG_WriteByte` from `sub_4AF4D0() ^ serverCommandSequence`.
- Retail `SV_ExecuteClientMessage` at `0x004E05C0` reads three `MSG_ReadLong`
  fields, consumes one unassigned `MSG_ReadByte`, then starts normal opcode
  parsing with another `MSG_ReadByte`.

The source now mirrors that parser shape:

- `CL_WritePacket` writes `CL_RetailClientMessageFlags() ^
  ( clc.serverCommandSequence & 0xff )` after `clc.serverCommandSequence`.
- `SV_ExecuteClientMessage` consumes one byte after `reliableAcknowledge` and
  before reliable-command opcode parsing.

`CL_RetailClientMessageFlags()` currently returns zero. Retail `sub_4AF4D0`
returns `data_565948`, whose producers are cgame/native-state bits. The retail
server consumes but does not validate this byte in committed HLIL, so the zero
stub restores parser compatibility while leaving byte-for-byte flag recovery as
a named follow-up.

## Frozen Body Grammar

Offsets are relative to the client message body: the current message cursor
after netchan processing and server-side XOR decode.

| Offset | Width | Field |
| --- | ---: | --- |
| `0` | 4 | `serverId` |
| `4` | 4 | `messageAcknowledge` |
| `8` | 4 | `reliableAcknowledge` |
| `12` | 1 | Retail client-message sideband byte |
| `13` | 1 | First opcode |

The opcode enum remains:

| Opcode | Value |
| --- | ---: |
| `clc_bad` | `0` |
| `clc_nop` | `1` |
| `clc_move` | `2` |
| `clc_moveNoDelta` | `3` |
| `clc_clientCommand` | `4` |
| `clc_EOF` | `5` |

## Golden Vectors

The JSON grammar includes four deterministic vectors:

- zero sideband followed by `clc_move`;
- non-zero sideband followed by `clc_moveNoDelta`;
- sideband plus `clc_clientCommand`, command sequence, string, then `clc_move`;
- a negative Quake III-style no-sideband body, proving retail would consume the
  move opcode as sideband and see the command-count byte as the first opcode.

These are parser grammar vectors, not full usercmd/XOR vectors. The later XOR
task still needs byte-for-byte encrypted packet coverage.

## Residual Risks

- The cgame/native-state flag producers behind retail `sub_4AF4D0` /
  `data_565948` still need a dedicated naming pass.
- The sideband byte is currently parser-compatible but not byte-for-byte
  complete when retail would set `0x20`, `0x40`, or future recovered bits.
- Full XOR byte-vector tests remain the next transport task.

Estimated parity movement for this task:

- Focused client-parser header slice: `55%` before, `90%` after.
- Overall network-protocol parity: `74%` before, `76%` after.
