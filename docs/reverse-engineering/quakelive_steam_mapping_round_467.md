# Quake Live Steam Mapping Round 467: Raw Sample Volume Cvar Scaling

## Scope

This round tightens the raw PCM stream path around retail
`sub_4DA840 -> S_RawSamples`. The source already matched the retail raw ring,
resampling branches, reset diagnostic, and overflow diagnostic, but it still
scaled raw samples only by the caller-provided volume. Retail applies the
global `s_volume` cvar in the same fixed-point multiplier.

## Evidence

Primary evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/analysis/quakelive_symbol_aliases.json`

Observed facts:

- The alias map promotes `sub_4DA840` to `S_RawSamples`.
- `functions.csv` records `FUN_004da840` at `0x004DA840`, size 688.
- HLIL at `0x004DA876` computes the raw stream multiplier from
  `*(data_13e185c + 0x2c) * arg6 * 256.0`.
- HLIL at `0x004DB9D9` binds `data_13e185c` to bounded cvar
  `"s_volume", "0.8", "0.0", "2.0", 0x81801`.
- The same `S_RawSamples` HLIL retains the existing `<< 8` style scale for
  8-bit raw streams, matching the source's extra `intVolume *= 256`.
- The background music update path passes its smoothed `s_musicvolume` value as
  `arg6`, so retail stacks music volume and global sound volume in
  `S_RawSamples`.

## Source Reconstruction

Implemented source changes:

- Changed `S_RawSamples` to compute `intVolume` as
  `256 * volume * s_volume->value`.
- Preserved the existing 8-bit path multiplier so 8-bit mono/stereo streams
  continue to receive the retail extra fixed-point shift.
- Extended `tests/test_client_sound_playback_parity.py` with HLIL anchors for
  the raw multiplier, `s_volume` cvar registration, the source reconstruction,
  and the absence of the old caller-volume-only expression.

This is a raw-stream path change. Normal positional channel scaling still
flows through `S_SpatializeOrigin`, while background music and any other raw
PCM producers now receive the retail global-volume layer.

No runtime launch was needed because this pass reconstructs deterministic
fixed-point volume wiring from committed HLIL/Ghidra evidence.

## Confidence

High confidence:

- Function ownership and size for `S_RawSamples`.
- `s_volume` cvar ownership through `S_Init`.
- Raw sample fixed-point multiplier shape for 16-bit and 8-bit streams.
- Interaction with background music, because `S_UpdateBackgroundTrack` feeds
  its smoothed music-volume value into `S_RawSamples`.

Open questions:

- None for this multiplier. Remaining raw-stream uncertainty is limited to
  future evidence around external movie/cinematic producers that also call
  `S_RawSamples`.

## Validation

- `python -m pytest tests\test_client_sound_playback_parity.py::test_sound_buffer_loop_raw_and_update_helpers_match_retail_wiring -q --tb=short`
  - 1 passed.
- `python -m pytest tests\test_client_sound_voice_parity.py tests\test_client_sound_playback_parity.py tests\test_win32_sound_dma_parity.py tests\test_cgame_sound_wiring_parity.py tests\test_botlib_cgame_native_import_slab_parity.py -q --tb=short`
  - 27 passed.
- `C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe src\code\quakelive.sln /p:Configuration=Debug /p:Platform=x86 /p:PlatformToolset=v143 /v:minimal`
  - Build completed successfully.

## Parity Estimate

- Focused `S_RawSamples` volume-scaling parity: 82% -> 96%.
- Raw/background sample playback parity: 88% -> 91%.
- Overall client sound-system reconstruction parity: 86% -> 87%.
