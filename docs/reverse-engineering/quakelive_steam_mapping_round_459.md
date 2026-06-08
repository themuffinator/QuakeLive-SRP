# Quake Live Steam Mapping Round 459: Native Looping-Sound Frame Clear Wiring

## Scope

This round closes the retail native-cgame looping-sound frame-clear path. The
target was the split clear-loop sound import wiring around:

- `j_sub_4DA490` / `QLCGImport_S_ClearLoopingSoundsFrame`
- `j_sub_4DA3E0` / `QLCGImport_S_ClearLoopingSoundsKillAll`
- `sub_4DA490` / `S_ClearLoopingSoundsFrame`
- `sub_4DA3E0` / `S_ClearSoundBuffer`

## Evidence

Primary evidence came from:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part07.txt`
- `references/analysis/quakelive_symbol_aliases.json`

Observed facts:

- Retail native-cgame table slot `0x005659FC` points at `j_sub_4DA490`, and
  `j_sub_4DA490` tailcalls `sub_4DA490`.
- Retail native-cgame table slot `0x00565A00` points at `j_sub_4DA3E0`, and
  `j_sub_4DA3E0` tailcalls `sub_4DA3E0`.
- `sub_4DA490` walks the looping-sound bank from `data_12B8964` to
  `0x12C5964` in `0x34`-byte record strides, clears one dword per record, and
  resets `data_142C2F0`.
- `sub_4DA3E0` is the heavier full sound-buffer clear path: it clears the
  looping-sound bank, loop channels, raw stream state, voice channels, and DMA
  output buffer.

The committed Ghidra function table does not expose `FUN_004da490` as a stable
standalone row, so this helper remains an HLIL-backed alias rather than a
function-size-pinned row.

## Source Reconstruction

Implemented source changes:

- Added `S_ClearLoopingSoundsFrame()` in `src/code/client/snd_dma.c`.
- Exposed the helper through `src/code/client/snd_public.h`.
- Rewired `QL_CG_trap_S_ClearLoopingSoundsFrame()` in
  `src/code/client/cl_cgame.c` to call the new retail-shaped helper directly.
- Left the legacy VM syscall path unchanged:
  `S_ClearLoopingSounds( args[1] ? qtrue : qfalse )` still services old QVM
  callers and preserves compatibility with `S_AddRealLoopingSound`.
- Expanded parity tests to pin the HLIL frame-clear loop, the native import
  table split, and the source wrapper call.

## Confidence

High confidence:

- Native import table ownership for frame-clear and kill-all slots.
- `sub_4DA490` frame-clear behavior and `data_142C2F0` reset.
- Source wiring from the native frame-clear wrapper to a distinct engine helper.

Medium confidence:

- The source-side `loopSound_t` still carries the GPL compatibility `kill`
  field for legacy VM and `S_AddRealLoopingSound` behavior. The retail native
  frame-clear helper only needs to model the active-flag clear and loop-channel
  count reset.

## Validation

- `python -m pytest tests\test_client_sound_playback_parity.py tests\test_botlib_cgame_native_import_slab_parity.py tests\test_client_sound_voice_parity.py -q --tb=short`
  - 20 passed.
- `python -m pytest tests\test_client_sound_voice_parity.py tests\test_client_sound_playback_parity.py tests\test_win32_sound_dma_parity.py tests\test_cgame_sound_wiring_parity.py tests\test_botlib_cgame_native_import_slab_parity.py -q --tb=short`
  - 26 passed.
- `python -m pytest tests\test_platform_services.py::test_native_import_dispatch_normalizes_qboolean_contracts -q --tb=short`
  - 1 passed.
- `git diff --check -- src\code\client\snd_public.h src\code\client\snd_dma.c src\code\client\cl_cgame.c tests\test_client_sound_playback_parity.py tests\test_botlib_cgame_native_import_slab_parity.py docs\reverse-engineering\quakelive_steam_mapping_round_459.md`
  - Passed with repository LF-to-CRLF working-copy warnings only.
- `C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe src\code\quakelive.sln /p:Configuration=Debug /p:Platform=x86 /p:PlatformToolset=v143 /v:minimal`
  - Build succeeded.

## Parity Estimate

- Focused native cgame clear-loop sound wiring: 95% -> 98%.
- Focused looping-sound frame-clear source parity: 78% -> 92%.
- Overall client sound-system reconstruction parity: 81% -> 82%.
