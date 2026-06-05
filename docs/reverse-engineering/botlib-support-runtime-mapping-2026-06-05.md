# Botlib Support Runtime Mapping - 2026-06-05

## Scope

This pass selects the botlib support runtime as the next slice:

- `src/code/botlib/l_log.c`
- `src/code/botlib/l_log.h`
- `src/code/botlib/l_memory.c`
- `src/code/botlib/l_memory.h`
- related setup/shutdown and server import wiring

It deliberately avoids the busy parser/precompiler files, elementary actions,
and the just-finished libvar test lanes. The work is mostly proof-oriented, with
one source-reconstruction fact now guarded: retail `Log_Open` gates on the
`bot_log` libvar, not the older GPL `log` libvar name.

## Owning Retail Binary

Owning binary:

- `assets/quakelive/quakelive_steam.exe`

Primary references:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part03.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt`
- `references/reverse-engineering/ghidra/qagamex86/decompile_top_functions.c`
- `src/code/botlib/l_log.c`
- `src/code/botlib/l_memory.c`
- `src/code/botlib/be_interface.c`
- `src/code/game/ai_main.c`
- `src/code/game/botlib.h`
- `src/code/server/sv_bot.c`

## Retail Function Map

Observed retail rows from `functions.csv`:

| Address | Size | Source owner | Notes |
| --- | ---: | --- | --- |
| `0x004A8830` | 210 | `Log_Open` | Checks `bot_log`, validates filename/open state, opens `wb`, copies 1024-byte filename. |
| `0x004A8910` | 72 | `Log_Close` | No-op when closed; closes `FILE*`, clears pointer, prints success/error. |
| `0x004A8960` | 15 | `Log_Shutdown` | Tailcalls `Log_Close` only when a file is open. |
| `0x004A8970` | 44 | `Log_Write` | No-op when closed; `vfprintf` plus `fflush`. |
| `0x004A89A0` | 36 | `GetMemory` | Calls imported zone allocator with `size + 4`, writes `MEM_ID`. |
| `0x004A89D0` | 71 | `GetClearedMemory` | Same header as `GetMemory`, then clears user bytes with `Com_Memset`. |
| `0x004A8A20` | 36 | `GetHunkMemory` | Calls imported hunk allocator with `size + 4`, writes `HUNK_ID`. |
| `0x004A8A50` | 71 | `GetClearedHunkMemory` | Same header as `GetHunkMemory`, then clears user bytes. |
| `0x004A8AA0` | 29 | `FreeMemory` | Subtracts four bytes, frees only blocks tagged with `MEM_ID`. |
| `0x004A8AC0` | 6 | `AvailableMemory` | Tail-jumps to the imported available-memory callback. |
| `0x004A83C0` | 240 | `GetBotLibAPI` | Copies the 0x58-byte import table and exports the botlib API. |

Source-visible helpers without separate retail starts in this pass:

- `Log_WriteTimeStamped`
- `Log_FilePointer`
- `Log_Flush`
- `PrintUsedMemorySize`
- `PrintMemoryLabels`
- `MemoryByteSize`
- `DumpMemory`

The log helpers remain guarded in source because other botlib code uses the
headers. The memory diagnostics collapse in the retail host build because
`MEMORYMANEGER` is not enabled.

## Observed Facts

- Retail `Log_Open` uses `LibVarValue("bot_log", "0")`. This matches qagame,
  where `BotAISetup` registers `bot_log` and `BotInitLibrary` forwards it through
  `BotLibVarSet`.
- `Export_BotLibSetup` calls `Log_Open("botlib.log")` at `0x004A7D23`.
- `Export_BotLibShutdown` reaches `Log_Shutdown` at `0x004A7E16`, after
  `LibVarDeAllocAll` and `PC_RemoveAllGlobalDefines`.
- `Log_Open` stores the filename in a 1024-byte fixed buffer and prints the same
  retail strings for open success, already-open, missing filename, and open
  failure.
- `Log_Write` is the only log write body with a stable retail start in this
  slice. It returns immediately when no file is open.
- Retail memory wrappers are the non-`MEMORYMANEGER` branch. Each allocation
  asks the host import for four extra bytes, writes a header tag, and returns the
  pointer after the tag.
- Zone allocations use `MEM_ID` (`0x12345678`). Hunk allocations use `HUNK_ID`
  (`0x87654321`).
- `FreeMemory` subtracts the four-byte header and only calls the imported
  `FreeMemory` callback for `MEM_ID` blocks. Hunk memory is intentionally not
  freed through the zone callback.
- `GetClearedMemory` and `GetClearedHunkMemory` preserve the source shape where
  the clear is attempted after allocation; the retail HLIL keeps the clear call
  even on the null path.
- `PrintUsedMemorySize` and `PrintMemoryLabels` are empty in the retail branch.
  This explains why AAS developer toggles can still self-clear without producing
  a memory dump in release host builds.

## Related Wiring

- `botlib_import_t` exposes `GetMemory`, `FreeMemory`, `AvailableMemory`, and
  `HunkAlloc`.
- `SV_BotInitBotLib` fills those callbacks with `BotImport_GetMemory`,
  `BotImport_FreeMemory`, `Z_AvailableMemory`, and `BotImport_HunkAlloc`.
- `BotImport_GetMemory` wraps `Z_TagMalloc(size, TAG_BOTLIB)`.
- `BotImport_FreeMemory` wraps `Z_Free`.
- `BotImport_HunkAlloc` rejects allocation while hunk marks are set, then uses
  `Hunk_Alloc(size, h_high)`.
- `GetBotLibAPI` copies the import table into the botlib global block; Binary
  Ninja shows `__builtin_memcpy(dest: &data_16dd800, src: arg2, n: 0x58)`.

## Changes

- Added `tests/test_botlib_support_runtime_parity.py`.
- Added this mapping note.
- Confirmed/guarded the current `l_log.c::Log_Open` reconstruction against the
  retail `bot_log` gate.
- No alias promotion was attempted; the active alias ledger is already busy.

## Validation

Targeted validation for this pass:

- `python -m pytest tests/test_botlib_support_runtime_parity.py -q` - `2 passed`
- `python -m pytest tests/test_botlib_support_runtime_parity.py tests/test_botlib_libvar_parity.py tests/test_botlib_chat_parity.py tests/test_botlib_weight_runtime_parity.py -q` - `14 passed`

No game launch was performed. Static source checks plus the committed
Binary Ninja/Ghidra retail references fully answer this support-runtime slice.

## Parity Estimate

- Focused botlib support runtime (`l_log.c`, `l_memory.c`, import wiring):
  `82% -> 96%`. Before this pass, the helper addresses and the `bot_log` retail
  gate were not protected by a dedicated guard.
- Overall botlib plus related wiring: approximately `78% -> 79%`.
- Strict-retail Windows replacement target: unchanged at `100%`.
