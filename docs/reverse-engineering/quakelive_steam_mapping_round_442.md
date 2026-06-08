# quakelive_steam.exe Mapping Round 442

Date: 2026-06-08

Scope: native cgame sound import wiring, especially the split clear-loop sound
slots used by retail Quake Live.

## Summary

This round tightens the sound wiring between native cgame and the engine sound
backend. Retail's native cgame import table does not expose the old VM
`trap_S_ClearLoopingSounds( killall )` shape directly. It splits that surface
into fixed-argument imports:

- slot 41: `j_sub_4DA490`, the lightweight per-frame looping-sound clear
- slot 42: `j_sub_4DA3E0`, the full `S_ClearSoundBuffer` path

The source already had separate `CG_QL_IMPORT_S_CLEARLOOPINGSOUNDS_FRAME` and
`CG_QL_IMPORT_S_CLEARLOOPINGSOUNDS_KILLALL` slots, but the kill-all wrapper
still called `S_ClearLoopingSounds( qtrue )`. It now calls
`S_ClearSoundBuffer()`, matching retail's native import-table target while
leaving the legacy VM syscall switch path unchanged.

## Evidence

Primary evidence:

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part07.txt`
- `src/code/client/cl_cgame.c`
- `src/code/cgame/cg_syscalls.c`
- `src/code/cgame/cg_public.h`

Observed facts:

1. Retail table slot `0x005659F4` points at `sub_4BEFB0`, the native
   `S_StartLocalSound` import wrapper.
2. Retail table slot `0x005659FC` points at `j_sub_4DA490`; HLIL shows that
   thunk tailcalling `sub_4DA490`, the lightweight looping-sound frame clear.
3. Retail table slot `0x00565A00` points at `j_sub_4DA3E0`; HLIL shows that
   thunk tailcalling `sub_4DA3E0`, already mapped as `S_ClearSoundBuffer`.
4. Retail table slot `0x00565A18` is the stop-background-track sound slot and
   points at the tiny `0x4B02F0` thunk adjacent to the parser-source wrappers.
5. The source `CG_MapNativeImport()` already maps the legacy
   `CG_S_CLEARLOOPINGSOUNDS` syscall to the split native frame/kill-all slots
   based on the stack argument.

## Alias Updates

- `j_sub_4DA490 -> QLCGImport_S_ClearLoopingSoundsFrame`
- `j_sub_4DA3E0 -> QLCGImport_S_ClearLoopingSoundsKillAll`

## Source Reconstruction

`QL_CG_trap_S_ClearLoopingSoundsKillAll()` now calls `S_ClearSoundBuffer()`.
This matches retail's native cgame slot 42 target. The old VM syscall handler
in `CL_CgameSystemCallsImpl()` still routes `CG_S_CLEARLOOPINGSOUNDS` through
`S_ClearLoopingSounds( args[1] ? qtrue : qfalse )`, preserving the compatibility
surface for QVM-style callers.

## Verification

Commands run:

- `python -m json.tool references\analysis\quakelive_symbol_aliases.json > $null`
  -> passed
- `python -m pytest tests\test_botlib_cgame_native_import_slab_parity.py tests\test_client_sound_voice_parity.py -q --tb=short`
  -> `14 passed`
- `git diff --check -- references\analysis\quakelive_symbol_aliases.json src\code\client\cl_cgame.c tests\test_botlib_cgame_native_import_slab_parity.py docs\reverse-engineering\quakelive_steam_mapping_round_442.md`
  -> passed with only LF-to-CRLF working-copy warnings on existing text files

## Parity Estimate

- Focused native cgame sound import wiring: **86% -> 95%**.
- Focused clear-loop/full-clear source behavior parity: **78% -> 96%**.
- Broader client sound-system reconstruction confidence: **87% -> 88%**.
- Repo-wide checked-in tree parity: **99% -> 99%**.
