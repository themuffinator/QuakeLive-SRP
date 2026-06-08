# quakelive_steam.exe Mapping Round 450

Date: 2026-06-08

Scope: client sound registration/cache helpers and missing-load diagnostics.

## Summary

This round tightens the source reconstruction around the sound-registration
cache lane:

- `S_FindName`
- `S_memoryLoad`
- `S_RegisterSound`
- `S_FreeOldestSound`
- `S_BeginRegistration`

The retail HLIL shows exact diagnostics for `S_FindName` fatal paths and a
two-stage missing-sound warning path: `S_memoryLoad` prints
`^3WARNING: couldn't load sound: %s\n`, and `S_RegisterSound` prints
`^3WARNING: could not find %s - using default\n` before returning handle `0`
for a defaulted sound. The source previously retained an older long-name
diagnostic and had the `S_memoryLoad` warning commented out.

## Evidence

Primary evidence:

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/analysis/quakelive_symbol_aliases.json`
- `src/code/client/snd_dma.c`

Observed facts:

1. `functions.csv` records the registration/cache helper rows:
   - `FUN_004d9d00`, size `266`
   - `FUN_004d9e10`, size `50`
   - `FUN_004d9e50`, size `151`
   - `FUN_004db320`, size `126`
   - `FUN_004db3a0`, size `78`
2. The alias map identifies these as `S_FindName`, `S_memoryLoad`,
   `S_RegisterSound`, `S_FreeOldestSound`, and `S_BeginRegistration`.
3. Retail `S_FindName` HLIL emits:
   - `"S_FindName: NULL"`
   - `"S_FindName: empty name"`
   - `"S_FindName: name too long: %s"`
   - `"S_FindName: out of sfx_t"`
4. Retail `S_FindName` uses the shared lowercase/path-normalizing hash helper
   with table size `0x80`, then walks the sound hash chain before allocating a
   zeroed `sfx_t`.
5. Retail `S_memoryLoad` calls `S_LoadSound`, prints
   `^3WARNING: couldn't load sound: %s\n` on failure, marks the default-sound
   bit, and marks the sound as resident.
6. Retail `S_RegisterSound` still prints
   `^3WARNING: could not find %s - using default\n` for a defaulted sound and
   returns `0` rather than the allocated handle.
7. Retail `S_BeginRegistration` unmutes sound, rebuilds the sound slab and hash
   table, then registers `sound/feedback/hit.wav`.
8. Retail `S_FreeOldestSound` skips handle `0`, selects the oldest resident
   sound by `lastTimeUsed`, logs
   `S_FreeOldestSound: freeing sound %s\n`, frees the linked sound buffers,
   and clears the resident state and data pointer.

## Source Reconstruction

- Updated `S_FindName` to use the retail long-name diagnostic:
  `S_FindName: name too long: %s`.
- Removed the legacy newlines from the `S_FindName: NULL` and
  `S_FindName: empty name` fatal strings so they match the retail string
  table.
- Restored the retail `S_memoryLoad` missing-load warning.
- Fixed the local indentation on the `S_memoryLoad(sfx);` call while touching
  the same registration block.
- Added a standard function header above `S_memoryLoad`.
- Extended `tests/test_client_sound_voice_parity.py` to bind the five helper
  aliases to Ghidra row sizes, HLIL diagnostics, and source reset/free/warning
  behavior.

No runtime launch was needed because this pass is literal source and mapping
reconstruction against committed HLIL/Ghidra evidence.

## Verification

- `python -m pytest tests\test_client_sound_voice_parity.py tests\test_client_sound_playback_parity.py tests\test_win32_sound_dma_parity.py tests\test_botlib_cgame_native_import_slab_parity.py -q --tb=short`
  - `22 passed`
- `git diff --check -- src\code\client\snd_dma.c tests\test_client_sound_voice_parity.py docs\reverse-engineering\quakelive_steam_mapping_round_450.md`
  - No whitespace errors; Git reported LF-to-CRLF normalization warnings for
    the touched source/test files.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .vscode/build.ps1 -Configuration Debug -Platform x86 -Targets quakelive_steam`
  - `Build succeeded.`
  - `0 Warning(s)`
  - `0 Error(s)`

## Parity Estimate

- Focused sound registration/cache helper parity: **90% -> 97%**.
- Focused missing-sound diagnostic parity: **78% -> 98%**.
- Broader client sound-system reconstruction confidence: **90% -> 91%**.
