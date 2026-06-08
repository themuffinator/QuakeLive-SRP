# quakelive_steam.exe Mapping Round 446

Date: 2026-06-08

Scope: cgame sound-command wiring, custom player sounds, and the buffered
announcer queue in `cgamex86.dll`.

## Summary

This round tightens the remaining cgame-side sound mapping around three related
retail paths:

- `CG_CustomSound` at `0x1003CA30`
- sound server commands inside `CG_ServerCommand`
- the buffered announcer helpers at `0x1004E050`, `0x1004E110`, `0x1004E180`,
  and `0x1004E220`

The source implementation already matched the retail queue and server-command
shape. The only source-code reconstruction needed here was the exact retail
`CG_CustomSound` invalid-client format string: `%d` was tightened to `%i`.

## Evidence

Primary evidence:

- `references/reverse-engineering/ghidra/cgamex86/functions.csv`
- `references/reverse-engineering/ghidra/cgamex86/decompile_top_functions.c`
- `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt`
- `references/analysis/quakelive_symbol_aliases.json`
- `src/code/cgame/cg_players.c`
- `src/code/cgame/cg_servercmds.c`
- `src/code/cgame/cg_view.c`

Observed facts:

1. `functions.csv` records `FUN_1003ca30` at `0x1003CA30`, size `156`.
   HLIL shows the non-star path tailing through cgame import `+0xB8`
   (`trap_S_RegisterSound`) and the star-prefixed path indexing a 32-entry
   custom sound table before returning the selected client sound.
2. The retail string table stores
   `"CG_CustomSound: invalid client %i"` and `"Unknown custom sound: %s"`.
   Source now uses the same `%i` invalid-client diagnostic.
3. The retail `CG_ServerCommand` Ghidra decompile keeps the sound command run
   as `playSound`, `playMusic`, `stopMusic`, `clearSounds`. The corresponding
   imports are `+0xB8` then `+0x9C` channel `6` for local one-shots, `+0xBC`
   for background-track start, `+0xC0` for stop, and `+0xA8` for clearing
   looping sounds.
4. `functions.csv` records the buffered queue helpers as
   `FUN_1004e050` size `180`, `FUN_1004e110` size `109`,
   `FUN_1004e180` size `153`, and `FUN_1004e220` size `182`.
5. HLIL shows `0x1004E110` writing the sound handle to the ring buffer and a
   `0x5DC` delay, `0x1004E180` clearing the ring while preserving a pending
   future timestamp, and `0x1004E220` playing through import `+0xA0` on
   channel `7`.

## Source Reconstruction

- Added the missing `sub_1003ca30 -> CG_CustomSound` mirror alias beside the
  existing `FUN_1003ca30` alias.
- Changed `CG_CustomSound` to report
  `"CG_CustomSound: invalid client %i"`, matching the retail string table.
- Added `tests/test_cgame_sound_wiring_parity.py` to pin aliases, Ghidra
  function sizes, HLIL offsets, Ghidra server-command imports, and the source
  helper bodies for the custom sound, server command, powerup timer, buffered
  clear, buffered add, and buffered play paths.

No game launch was needed because this pass is literal mapping/source
reconstruction against committed Binary Ninja HLIL and Ghidra evidence.

## Parity Estimate

- Focused cgame sound command and buffered-announcer wiring:
  **96% -> 98%**.
- Focused `CG_CustomSound` source-string parity:
  **98% -> 99%**.
- Broader sound subsystem reconstruction confidence after this and the prior
  OGG/WAV, DMA, native cgame import, and native UI import sound rounds:
  **89% -> 91%**.
- Repo-wide checked-in tree parity: **99% -> 99%**.
