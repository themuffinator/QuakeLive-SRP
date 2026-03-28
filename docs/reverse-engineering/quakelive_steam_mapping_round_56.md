# Quake Live Steam Host Mapping Round 56

## Scope

This round maps the next retained Quake III core immediately after the
filesystem work from round 55:

- the startup / restart entry points from `files.c`
- the adaptive Huffman compressor and decompressor from `huffman.c`
- the MD4 checksum path used by pack validation and block checksums
- the early `msg.c` wrapper layer built on top of those retained primitives

Primary evidence for this round:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `src/code/qcommon/files.c`
- `src/code/qcommon/huffman.c`
- `src/code/qcommon/md4.c`
- `src/code/qcommon/msg.c`
- `assets/quake3/src/code/qcommon/files.c`
- `assets/quake3/src/code/qcommon/huffman.c`
- `assets/quake3/src/code/qcommon/md4.c`
- `assets/quake3/src/code/qcommon/msg.c`

## Filesystem Startup And Restart Closures

### `sub_4D3520`: `FS_InitFilesystem`

Observed facts:

1. The helper calls `Com_StartupVariable` on the expected filesystem cvars
   before invoking `sub_4D30A0("baseq3")`.
2. It validates startup success with the exact retained fatal
   `Couldn't load default.cfg`.
3. It snapshots the last-valid base and game directory strings exactly where
   Quake III `FS_InitFilesystem` does its post-startup bookkeeping.

The Quake Live host omits some newer source-side preflight and mapping setup in
this standalone body, but the retained ownership is still clearly
`FS_InitFilesystem`.

### `sub_4D35E0`: `FS_Restart`

Observed facts:

1. The helper begins by shutting the filesystem down, updating the checksum
   feed, clearing pack references, and restarting `baseq3`.
2. It preserves the same `Couldn't load default.cfg` / `Invalid game folder\n`
   fallback path as Quake III, including the recursive retry after restoring the
   last-valid base and game directory.
3. On game-directory changes it queues `exec qzconfig.cfg\n`, which is the
   Quake Live-specific filename divergence from Quake III's `q3config.cfg`
   while keeping the same restart role.

That makes `sub_4D35E0` the retained host `FS_Restart`.

### `sub_4D3730`: `FS_ConditionalRestart`

Observed facts:

1. The helper restarts when the incoming checksum feed differs from the stored
   feed.
2. It also restarts when the `fs_game` cvar remains marked modified.
3. Otherwise it returns `0`, matching the stock Quake III
   `FS_ConditionalRestart` contract.

## Huffman Core Closures

The next contiguous block matches Quake III `huffman.c` in source order and
behavior:

- `sub_4D3790 -> Huff_putBit`
- `sub_4D37D0 -> Huff_getBit`
- `sub_4D3800 -> swap`
- `sub_4D3840 -> swaplist`
- `sub_4D38A0 -> increment`
- `sub_4D3980 -> Huff_addRef`
- `sub_4D3B20 -> Huff_Receive`
- `sub_4D3B80 -> Huff_offsetReceive`
- `sub_4D3C00 -> send`
- `sub_4D3C90 -> Huff_transmit`
- `sub_4D3E20 -> Huff_offsetTransmit`
- `sub_4D3E60 -> Huff_Decompress`
- `sub_4D40F0 -> Huff_Compress`
- `sub_4D4260 -> Huff_Init`

Observed facts:

1. `sub_4D3790` and `sub_4D37D0` are the offset-based bit writers and readers,
   updating the shared bit cursor exactly like `Huff_putBit` and `Huff_getBit`.
2. `sub_4D3800`, `sub_4D3840`, and `sub_4D38A0` preserve the tree-swap,
   list-swap, and weight-increment machinery of the adaptive Huffman update
   path.
3. `sub_4D3E60` and `sub_4D40F0` preserve the Quake III compressed-buffer
   format: a two-byte uncompressed size header, `bloc = 16`, NYT expansion for
   first-seen symbols, and writeback into `msg_t`.
4. `sub_4D4260` initializes both compressor and decompressor tables with the
   NYT node in the exact dual-table layout defined by `huffman_t`.

The private `add_bit` and `get_bit` helpers are inlined into the retained host
implementation rather than emitted as standalone functions.

## MD4 Checksum Closures

The next retained block matches Quake III `md4.c`:

- `sub_4D4350 -> MD4Transform`
- `sub_4D47E0 -> MD4Update`
- `sub_4D4890 -> MD4Final`
- `sub_4D4960 -> Com_BlockChecksum`
- `sub_4D49D0 -> Com_BlockChecksumKey`

Observed facts:

1. `sub_4D4350` performs the three MD4 rounds with the exact `0x5A827999` and
   `0x6ED9EBA1` constants, after decoding a 64-byte block into sixteen
   32-bit words.
2. `sub_4D47E0` maintains the bit count, buffers partial input, and repeatedly
   invokes `sub_4D4350`, matching `MD4Update`.
3. `sub_4D4890` appends the MD4 padding block plus bit-count trailer, writes a
   16-byte digest, and zeroes the context, matching `MD4Final`.
4. `sub_4D4960` and `sub_4D49D0` build the standard four-word digest and fold
   it with XOR exactly like Quake III `Com_BlockChecksum` and
   `Com_BlockChecksumKey`.

As in the retail Quake III code, `MD4Init`, `Encode`, and `Decode` are folded
into adjacent emitted code rather than surviving here as separate standalone
functions.

## Message Wrapper Closures

The next block keeps the retained Quake III `msg.c` wrapper layer intact:

- `sub_4D4A50 -> MSG_Clear`
- `sub_4D4A70 -> MSG_Bitstream`
- `sub_4D4A80 -> MSG_BeginReadingOOB`
- `sub_4D4AA0 -> MSG_Copy`
- `sub_4D4AF0 -> MSG_WriteBits`
- `sub_4D4C70 -> MSG_ReadBits`
- `sub_4D4DC0 -> MSG_WriteByte`
- `sub_4D4DE0 -> MSG_WriteData`
- `sub_4D4E10 -> MSG_WriteShort`
- `sub_4D4E30 -> MSG_WriteLong`
- `sub_4D4E50 -> MSG_WriteString`
- `sub_4D4F00 -> MSG_WriteBigString`
- `sub_4D4FC0 -> MSG_ReadByte`
- `sub_4D4FF0 -> MSG_ReadShort`
- `sub_4D5020 -> MSG_ReadLong`
- `sub_4D5040 -> MSG_ReadString`
- `sub_4D50A0 -> MSG_ReadBigString`
- `sub_4D5100 -> MSG_ReadStringLine`
- `sub_4D5160 -> MSG_ReadData`

Observed facts:

1. `sub_4D4AA0` preserves the exact Quake III fatal
   `MSG_Copy: can't copy into a smaller msg_t buffer`.
2. `sub_4D4AF0` and `sub_4D4C70` preserve the stock split between OOB direct
   writes/reads and compressed Huffman-backed bitstreams, including the exact
   `MSG_WriteBits: bad bits %i` and `can't read %d bits\n` diagnostics.
3. `sub_4D4E50`, `sub_4D4F00`, `sub_4D5040`, `sub_4D50A0`, and `sub_4D5100`
   preserve the Quake III string limits and sanitization rules, including the
   `MAX_STRING_CHARS` and `BIG_INFO_STRING` diagnostics plus the `%` to `.`
   rewrite in the read path.
4. `sub_4D4A50`, `sub_4D4A70`, and `sub_4D4A80` line up with the compact retail
   `msg_t` setup helpers emitted by the Quake Live host, where the standalone
   `allowoverflow` field from the GPL source no longer survives as a distinct
   stored field in this code generation.

The standalone `MSG_WriteChar`, `MSG_BeginReading`, and `MSG_Init*` entry
points are either folded away or emitted elsewhere in the retail host, but the
retained wrapper layer itself is now source-aligned.

## Completion Summary

This round promotes `41` retained Quake III aliases:

- filesystem startup: `FS_InitFilesystem`, `FS_Restart`, `FS_ConditionalRestart`
- Huffman core: `Huff_putBit`, `Huff_getBit`, `swap`, `swaplist`, `increment`,
  `Huff_addRef`, `Huff_Receive`, `Huff_offsetReceive`, `send`,
  `Huff_transmit`, `Huff_offsetTransmit`, `Huff_Decompress`, `Huff_Compress`,
  `Huff_Init`
- checksum core: `MD4Transform`, `MD4Update`, `MD4Final`,
  `Com_BlockChecksum`, `Com_BlockChecksumKey`
- message wrappers: `MSG_Clear`, `MSG_Bitstream`, `MSG_BeginReadingOOB`,
  `MSG_Copy`, `MSG_WriteBits`, `MSG_ReadBits`, `MSG_WriteByte`,
  `MSG_WriteData`, `MSG_WriteShort`, `MSG_WriteLong`, `MSG_WriteString`,
  `MSG_WriteBigString`, `MSG_ReadByte`, `MSG_ReadShort`, `MSG_ReadLong`,
  `MSG_ReadString`, `MSG_ReadBigString`, `MSG_ReadStringLine`,
  `MSG_ReadData`

Focused band results after this pass:

- `0x4D3520-0x4D4260`: `17 -> 0` remaining standalone gaps
- `0x4D4350-0x4D49D0`: `5 -> 0`
- `0x4D3520-0x4D49D0`: `22 -> 0`
- core compression/checksum slice `0x4D3790-0x4D49D0`: `19 -> 0`
- `0x4D4A50-0x4D5160`: `19 -> 0`
- `0x4D3520-0x4D5160`: `41 -> 0`

The next adjacent unresolved starts now begin in the later delta-message path:

- `0x004D51A0`
- `0x004D54A0`

Those two starts sit in the next retained `msg.c` delta-encoding block rather
than in the startup / checksum / wrapper tranche that this round targeted.
