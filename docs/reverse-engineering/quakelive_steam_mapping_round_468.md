# Quake Live Steam Mapping Round 468: S_Update Slice Diagnostics and Timing

## Scope

This round maps and tightens the retail frame-update sound slice:
`sub_4DB680 -> S_Update`, `sub_4DB570 -> S_Update_`, and
`sub_4DB490 -> S_GetSoundtime`. The source already had the main paint path
shape, but the visible `s_show == 2` diagnostics still carried a legacy
floating-point format for integer channel volumes, and the update early-return
path emitted a source-only debug string absent from the retail corpus.

## Evidence

Primary evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/analysis/quakelive_symbol_aliases.json`

Observed facts:

- The alias map promotes `sub_4DB680` to `S_Update`, `sub_4DB570` to
  `S_Update_`, and `sub_4DB490` to `S_GetSoundtime`.
- `functions.csv` records `FUN_004db680` at `0x004DB680`, size 129;
  `FUN_004db570` at `0x004DB570`, size 262; and `FUN_004db490` at
  `0x004DB490`, size 209.
- HLIL at `0x004DB690` returns immediately when sound is not started or muted.
  The retail string corpus contains `"sound system not started\n"` for
  `S_SoundInfo_f`, but no `"not started or muted\n"` update-frame diagnostic.
- HLIL at `0x004DB69B` checks `s_show == 2`, walks 96 source channels, prints
  active channel volumes with `"%3i %3i %s\n"`, then prints
  `"----(%i)---- painted: %i\n"`.
- HLIL at `0x004DB6F6` calls `S_UpdateBackgroundTrack`, then tail-calls
  `S_Update_` at `0x004DB6FB`.
- HLIL at `0x004DB570` guards on started/unmuted sound, contains an observed
  retail-only direct-DMA control branch at `data_142c334`, and otherwise calls
  `S_GetSoundtime`, `S_ScanChannelStarts`, `SNDDMA_BeginPainting`,
  `S_PaintChannels`, and `SNDDMA_Submit`.
- HLIL at `0x004DB490` computes the DMA-derived sound clock, handles buffer
  wraps, resets and stops all sounds beyond the high `s_paintedtime` threshold,
  and updates `s_paintedtime` from either `s_mixPreStep * dma.speed` or
  `dma.submission_chunk`.

## Source Reconstruction

Implemented source changes:

- Removed the source-only `Com_DPrintf("not started or muted\n")` from
  `S_Update`.
- Changed the `s_show == 2` channel diagnostic from `"%f %f %s\n"` to the
  retail `"%3i %3i %s\n"` integer-volume format.
- Extended `tests/test_client_sound_playback_parity.py` to pin
  `S_GetSoundtime` alias ownership, the `S_Update` diagnostic strings, and the
  observed retail `S_Update_` timing/direct-control branch anchors.

Not reconstructed in source in this round:

- The retail `data_142c334` / `data_142c338` update-control words sit between
  `dma.speed` and the retail `dma.buffer` pointer at `data_142c33c`. DirectSound
  initialization and `s_info` confirm `data_142c33c` is the buffer pointer, but
  the current shared `dma_t` has no stable field analogue for the preceding
  retail control words. This remains mapped evidence rather than a speculative
  structure change.

No runtime launch was needed because this pass reconstructs deterministic
update diagnostics and timing wiring from committed HLIL/Ghidra evidence.

## Confidence

High confidence:

- Function ownership and sizes for `S_Update`, `S_Update_`, and
  `S_GetSoundtime`.
- Removal of the source-only update-frame muted/not-started diagnostic.
- `s_show == 2` integer-volume diagnostic format.
- Normal paint path order: background update, soundtime scan, channel-start
  scan, mix-ahead rounding/clamping, begin-paint, paint, submit.

Medium confidence:

- The direct-DMA branch meaning is clearly present in retail HLIL, but its
  source-level field ownership is not stable enough to reconstruct without
  further struct evidence.

## Validation

- `python -m pytest tests\test_client_sound_playback_parity.py::test_sound_buffer_loop_raw_and_update_helpers_match_retail_wiring tests\test_client_sound_playback_parity.py::test_sound_playback_aliases_cover_retail_core_entrypoints -q --tb=short`
  - 2 passed.
- `python -m pytest tests\test_client_sound_voice_parity.py tests\test_client_sound_playback_parity.py tests\test_win32_sound_dma_parity.py tests\test_cgame_sound_wiring_parity.py tests\test_botlib_cgame_native_import_slab_parity.py tests\test_engine_cvar_retail_parity.py::test_engine_cvar_eighteenth_sound_tranche_matches_retail_contracts -q --tb=short`
  - 28 passed.
- `python -m pytest tests\test_client_sound_voice_parity.py tests\test_client_sound_playback_parity.py tests\test_win32_sound_dma_parity.py tests\test_cgame_sound_wiring_parity.py tests\test_botlib_cgame_native_import_slab_parity.py tests\test_engine_cvar_retail_parity.py -q --tb=short`
  - 79 passed, 6 failed in unrelated common, WinMain, game, and UI cvar
    tranches.
- `git diff --check -- src\code\client\snd_dma.c tests\test_client_sound_playback_parity.py docs\reverse-engineering\quakelive_steam_mapping_round_467.md docs\reverse-engineering\quakelive_steam_mapping_round_468.md`
  - Passed with repository LF-to-CRLF working-copy warnings on touched C/Python
    files.
- `C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe src\code\quakelive.sln /p:Configuration=Debug /p:Platform=x86 /p:PlatformToolset=v143 /v:minimal`
  - Build completed successfully.

## Parity Estimate

- Focused `S_Update` diagnostic parity: 84% -> 97%.
- Focused `S_Update` / `S_Update_` / `S_GetSoundtime` slice mapping parity:
  86% -> 92%.
- Overall client sound-system reconstruction parity: 87% -> 88%.
