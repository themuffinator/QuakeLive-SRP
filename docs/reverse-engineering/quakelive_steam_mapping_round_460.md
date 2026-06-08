# Quake Live Steam Mapping Round 460: Active-Only Looping-Sound Frame Clear

## Scope

This round tightens the source reconstruction for the native-cgame
looping-sound frame-clear helper introduced in the previous pass. The target
remains the retail `j_sub_4DA490 -> sub_4DA490` path, but this pass corrects
the exact source-side field effect.

## Evidence

Primary evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part07.txt`
- `references/analysis/quakelive_symbol_aliases.json`

Observed facts:

- Retail table slot `0x005659FC` points at `j_sub_4DA490`, and that thunk
  tailcalls `sub_4DA490`.
- The full HLIL for `sub_4DA490` walks from `data_12B8964` to `0x12C5964` in
  `0x34`-byte strides and stores `0` through the current pointer.
- Round 22 recovered the retail loop-sound record: `+0x14` is the active flag,
  while the source-only GPL compatibility `kill` flag does not have a distinct
  retail field in this helper.
- `sub_4DA490` then resets `data_142C2F0`, the retail loop-channel count.

## Source Reconstruction

Implemented source changes:

- Refined `S_ClearLoopingSoundsFrame()` so it clears only
  `loopSounds[i].active`.
- Kept the `numLoopChannels = 0` reset matching retail `data_142C2F0 = 0`.
- Stopped clearing `loopSounds[i].kill` in the native frame-clear helper.
- Left the compatibility `S_ClearLoopingSounds( qboolean killall )` path intact
  for legacy VM callers and `S_AddRealLoopingSound` semantics.
- Updated playback parity tests so the native frame helper explicitly rejects
  the `kill` clear and `S_StopLoopingSound` path.

## Confidence

High confidence:

- Active-only field effect for `sub_4DA490`.
- Loop-channel count reset.
- Separation between retail native frame-clear behavior and the legacy
  compatibility `killall` syscall surface.

Medium confidence:

- The source still keeps a GPL-era `kill` field because the QVM compatibility
  layer still exposes `S_ClearLoopingSounds( killall )` and
  `S_AddRealLoopingSound`. This is intentionally outside the retail native
  `sub_4DA490` field effect.

## Validation

- `python -m pytest tests\test_client_sound_playback_parity.py::test_sound_buffer_loop_raw_and_update_helpers_match_retail_wiring tests\test_botlib_cgame_native_import_slab_parity.py::test_native_cgame_sound_import_wiring_reconstructs_retail_clear_slots -q --tb=short`
  - 2 passed.
- `python -m pytest tests\test_client_sound_voice_parity.py tests\test_client_sound_playback_parity.py tests\test_win32_sound_dma_parity.py tests\test_cgame_sound_wiring_parity.py tests\test_botlib_cgame_native_import_slab_parity.py -q --tb=short`
  - 26 passed.
- `python -m pytest tests\test_platform_services.py::test_native_import_dispatch_normalizes_qboolean_contracts -q --tb=short`
  - 1 passed.
- `git diff --check -- src\code\client\snd_dma.c tests\test_client_sound_playback_parity.py docs\reverse-engineering\quakelive_steam_mapping_round_460.md`
  - Passed with repository LF-to-CRLF working-copy warning only.
- `C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe src\code\quakelive.sln /p:Configuration=Debug /p:Platform=x86 /p:PlatformToolset=v143 /v:minimal`
  - Build succeeded.

## Parity Estimate

- Focused `sub_4DA490` source-field parity: 92% -> 98%.
- Native cgame clear-loop sound wiring: 98% -> 99%.
- Overall client sound-system reconstruction parity: 82% -> 82%.
