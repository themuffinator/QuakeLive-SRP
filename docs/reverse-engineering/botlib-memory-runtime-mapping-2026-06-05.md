# Botlib Memory And Logging Runtime Mapping - 2026-06-05

## Coordination

Selected slice: botlib utility allocation and log-file runtime, centered on
`l_memory.c` with adjacent `l_log.c`, setup/shutdown hooks, and engine memory
import wiring.

This was chosen as the next clean botlib slice because it does not overlap the
active parser/resource-source corridor from session
`019e97e9-ddaa-7e53-81bb-6511a54422c2` or the chat lane from session
`019e97ef-042c-7171-855b-46853b848cb1`. This round did not edit
`l_struct.c`, `l_precomp.c`, `be_ai_chat.c`, shared parser/chat parity tests,
or the prior chat/precompiler mapping notes.

## Evidence

- Owning retail binary: `assets/quakelive/quakelive_steam.exe`.
- Ghidra companion corpus:
  - `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
  - `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
  - `references/reverse-engineering/ghidra/quakelive_steam/exports.txt`
  - `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  - `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
  - `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`
- Canonical HLIL:
  - `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part03.txt`
  - `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
- Name support:
  - `references/analysis/quakelive_symbol_aliases.json`
- Reconstruction surface:
  - `src/code/botlib/l_memory.c`
  - `src/code/botlib/l_memory.h`
  - `src/code/botlib/l_log.c`
  - `src/code/botlib/l_log.h`
  - `src/code/botlib/be_interface.c`
  - `src/code/botlib/be_aas_main.c`
  - `src/code/game/ai_main.c`
  - `src/code/game/botlib.h`
  - `src/code/server/sv_bot.c`
  - `src/code/qcommon/common.c`
  - `src/code/qcommon/qcommon.h`

`metadata.txt` identifies `quakelive_steam.exe` as x86 32-bit Windows with
5473 functions, 351 imports, 2 exports, and 4377 analysis symbols. The memory
and log band is not promoted in `analysis_symbols.txt`; the stable names are
kept in the repository alias map and are cross-checked against HLIL and local
source shape. `imports.txt` provides the CRT anchors used by this slice:
`fopen`, `fclose`, `fflush`, `strncpy`, `vfprintf`, and `memset`.

## Retail Function Map

| Address | Alias | Size | Evidence |
| --- | --- | ---: | --- |
| `004A8830` | `Log_Open` | 210 | gates on `bot_log`, handles filename/opened/fopen diagnostics |
| `004A8910` | `Log_Close` | 72 | closes `data_e4a4c8`, clears it, prints close message |
| `004A8960` | `Log_Shutdown` | 15 | tail-calls close only when a file is open |
| `004A8970` | `Log_Write` | 44 | `vfprintf` then `fflush` |
| `004A89A0` | `GetMemory` | 36 | zone callback plus 4-byte `0x12345678` header |
| `004A89D0` | `GetClearedMemory` | 71 | zone callback, `0x12345678`, payload `memset` |
| `004A8A20` | `GetHunkMemory` | 36 | hunk callback plus 4-byte `0x87654321` header |
| `004A8A50` | `GetClearedHunkMemory` | 71 | hunk callback, `0x87654321`, payload `memset` |
| `004A8AA0` | `FreeMemory` | 29 | subtracts header, frees only `0x12345678` blocks |
| `004A8AC0` | `AvailableMemory` | 6 | direct jump through import callback |

The next contiguous functions, `004A8AD0` and `004A8B30`, are
`SourceError`/`SourceWarning`. They were treated as the parser/source boundary
and not claimed by this slice.

## Source Reconstruction

Retail HLIL shows `Log_Open` checking:

```text
004a883e  st0, result = sub_4a8770("bot_log", U"0")
```

The local source still checked `LibVarValue("log", "0")`, which disconnected
the botlib logger from the qagame-facing `bot_log` cvar bridge. This round
reconstructed that literal in `src/code/botlib/l_log.c`:

```c
if (!LibVarValue("bot_log", "0")) return;
```

The rest of the local logging shape already matches the retail band:

- empty filename prints `openlog <filename>\n`;
- already-open log prints `log file %s is already opened\n`;
- `fopen(filename, "wb")` opens the log;
- failure prints `can't open the log file %s\n`;
- filename copy is bounded to `MAX_LOGFILENAMESIZE`/`0x400`;
- close failure prints `can't close log file %s\n`;
- `Log_Write` emits through `vfprintf` and flushes immediately.

`be_interface.c` wires the runtime by calling `Log_Open("botlib.log")` during
`Export_BotLibSetup` and `Log_Shutdown()` during `Export_BotLibShutdown`.
`ai_main.c` registers `bot_log`, reads that cvar, and forwards it into botlib
with `trap_BotLibVarSet("bot_log", buf)`, matching the reconstructed literal.

## Memory Semantics

Retail uses the non-`MEMORYMANEGER` path, not the debug block-list allocator.
The observed behavior is intentionally lightweight:

| Helper | Retail behavior | Local source |
| --- | --- | --- |
| `GetMemory` | `GetMemory(size + 4)`, write `0x12345678`, return payload | matches |
| `GetClearedMemory` | same tag path, `memset(payload, 0, size)` | matches |
| `GetHunkMemory` | `HunkAlloc(size + 4)`, write `0x87654321`, return payload | matches |
| `GetClearedHunkMemory` | same tag path, `memset(payload, 0, size)` | matches |
| `FreeMemory` | subtract 4; if header is not `0x12345678`, return without freeing | matches |
| `AvailableMemory` | jump through import callback | matches |

Observed fact: `FreeMemory` does not free `HUNK_ID` blocks. This preserves
Quake hunk ownership: hunk memory is released by hunk lifecycle operations, not
by the zone free callback.

Observed fact: the cleared-allocation HLIL emits a `memset(nullptr, 0, size)`
call in the failed-allocation branch before returning `0`. The local source's
unconditional `Com_Memset(ptr, 0, size)` after `GetMemory`/`GetHunkMemory`
matches that control-flow shape.

The non-manager `PrintUsedMemorySize` and `PrintMemoryLabels` functions are
empty. `be_aas_main.c` still exposes the developer cvars `showmemoryusage` and
`memorydump`, but on the retail path they reset after calling no-op printers.

## Engine Import Wiring

The public import struct keeps memory callbacks in this order:

1. `GetMemory`
2. `FreeMemory`
3. `AvailableMemory`
4. `HunkAlloc`

Source-side server wiring in `SV_BotInitBotLib` matches that order:

```c
botlib_import.GetMemory = BotImport_GetMemory;
botlib_import.FreeMemory = BotImport_FreeMemory;
botlib_import.AvailableMemory = Z_AvailableMemory;
botlib_import.HunkAlloc = BotImport_HunkAlloc;
```

Retail HLIL part04 shows the same callback group when building the import
table before calling `GetBotLibAPI`:

| Import slot evidence | Interpreted source callback | Supporting fact |
| --- | --- | --- |
| `var_3c = sub_4dd350` | `BotImport_GetMemory` | `sub_4dd350` calls `Z_TagMalloc(size, 2)` |
| `var_38 = sub_4dd370` | `BotImport_FreeMemory` | tail-calls `sub_4ca1d0`, the `Z_Free` body |
| `var_34 = sub_4c9220` | `Z_AvailableMemory` | returns zone free-space expression |
| `var_30 = sub_4dd380` | `BotImport_HunkAlloc` | checks hunk mark then calls `Hunk_Alloc(size, 0)` |

The `sub_4dd370` prototype is weak in HLIL because the decompiler loses the
incoming argument at the tail call, but the neighboring source order and the
body target (`Z_Free`) make the ownership role stable.

`BotImport_HunkAlloc` is also anchored by the retail fatal string:

```text
SV_Bot_HunkAlloc: Alloc with marks already set\n
```

## Alias Promotions

`references/analysis/quakelive_symbol_aliases.json` now includes bounded
aliases for the retail band:

- `sub_4A8830` -> `Log_Open`
- `sub_4A8910` -> `Log_Close`
- `sub_4A8960` -> `Log_Shutdown`
- `sub_4A8970` -> `Log_Write`
- `sub_4A89A0` -> `GetMemory`
- `sub_4A89D0` -> `GetClearedMemory`
- `sub_4A8A20` -> `GetHunkMemory`
- `sub_4A8A50` -> `GetClearedHunkMemory`
- `sub_4A8AA0` -> `FreeMemory`
- `sub_4A8AC0` -> `AvailableMemory`

## Verification

Added `tests/test_botlib_memory_parity.py`, covering:

- Ghidra function rows and CRT import anchors;
- HLIL evidence for the logging and allocator functions;
- alias-map names for the selected retail band;
- source shape of the retail non-manager allocator path;
- reconstructed `bot_log` logging gate and qagame cvar bridge;
- setup/shutdown calls and developer memory cvar calls;
- server import callback order and engine allocator helpers.

Focused verification:

```text
python -m pytest tests/test_botlib_memory_parity.py
4 passed
```

Alias-map syntax verification:

```text
python -m json.tool references/analysis/quakelive_symbol_aliases.json
```

## Open Questions

- `Log_WriteTimeStamped`, `Log_FilePointer`, and `Log_Flush` remain local
  source helpers outside the observed `004A8830`-`004A8AC0` retail band. They
  were not promoted in this round.
- The disabled `MEMORYMANEGER` block-list path remains GPL/debug scaffolding.
  Retail evidence for the Quake Live runtime maps to the compact tag-header
  path only.
- Broader source/parser diagnostics begin at `SourceError`/`SourceWarning` and
  should stay with the parser/source-handle slice.

## Parity Estimate

- Selected memory/log slice before this round: about 82% parity. The core
  allocator behavior was already structurally correct, but the retail function
  map and `bot_log` source literal were not pinned.
- Selected memory/log slice after this round: about 97% parity. The remaining
  gap is limited to non-promoted local helper functions and the disabled debug
  allocator scaffolding.
- Overall botlib reconstruction impact: about +0.2 percentage points, because
  this is a small utility corridor but it touches global allocation/logging
  wiring used across botlib.
