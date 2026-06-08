# quakelive_steam.exe Mapping Round 451

Date: 2026-06-08

Scope: client background-music sound wiring, focused on the retail OGG
`S_StartBackgroundTrack` and `S_UpdateBackgroundTrack` path.

## Summary

This round reconstructs the background music lane as an OGG-only retail Quake
Live path. The previous source still carried a compatibility resolver that
looked for `.ogg`, fell back to `.wav`, and kept a WAV streaming branch in the
background update loop. Retail QL instead normalizes non-`.ogg` background
track requests to `.ogg`, emits the exact
`S_StartBackgroundTrack: %s should have an OGG extension\n` debug diagnostic,
opens the OGG stream, and restarts through the same OGG start helper when the
stream ends.

## Evidence

Primary evidence:

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/analysis/quakelive_symbol_aliases.json`
- `src/code/client/snd_dma.c`

Observed facts:

1. `functions.csv` records the background sound helpers:
   - `FUN_004db030`, size `35`
   - `FUN_004db060`, size `351`
   - `FUN_004db1c0`, size `347`
   - `FUN_004dca40`, size `12`
   - `FUN_004dca50`, size `114`
2. The alias map identifies these as `S_StopBackgroundTrack`,
   `S_StartBackgroundTrack`, `S_UpdateBackgroundTrack`,
   `S_CloseBackgroundOgg`, and `S_OggUpdateBackgroundTrack`.
3. Retail `S_StartBackgroundTrack` HLIL emits
   `S_StartBackgroundTrack( %s, %s )\n`.
4. Retail checks the intro extension against `.ogg`; non-`.ogg` paths emit
   `S_StartBackgroundTrack: %s should have an OGG extension\n`.
5. Retail strips/defaults both the loop and intro paths to `.ogg` in that
   branch before opening the stream.
6. Retail opens the background path through the virtual filesystem and then
   initializes the OGG stream helper; on open failure it prints
   `^3WARNING: couldn't open music file %s\n`.
7. Retail `S_UpdateBackgroundTrack` feeds a stack raw buffer through
   `S_OggUpdateBackgroundTrack`, hands decoded samples to `S_RawSamples`, and
   on short-read/end-of-stream closes the OGG stream and restarts through
   `S_StartBackgroundTrack( loop, loop )` when a loop track exists.
8. No retail evidence was found for the source-side background `.wav` probing
   or decode-failure fallback inside `S_StartBackgroundTrack`.

## Source Reconstruction

- Replaced the compatibility `S_ResolveMusicFile` / `S_FileExists` /
  `S_SetTrackExtension` path with OGG-focused helpers:
  `S_BackgroundTrackHasOggExtension` and `S_SetOggTrackPath`.
- Reconstructed `S_StartBackgroundTrack` to normalize intro and loop paths to
  `.ogg`, emit the retail extension diagnostic, close any active stream, and
  open only the OGG stream.
- Removed the background `S_OpenBackgroundWav` fallback and the WAV streaming
  branch from `S_UpdateBackgroundTrack`.
- Removed the now-unused raw-sample byte-swap helper that only served the
  deleted WAV streaming branch.
- Updated `S_SoundInfo_f` so active OGG background music is reported as a
  background file instead of incorrectly falling through to
  `No background file.`.
- Extended `tests/test_client_sound_voice_parity.py` to pin the background
  helper aliases, retail HLIL strings/control flow, OGG normalization source,
  OGG update loop, and absence of the compatibility WAV fallback.

No runtime launch was needed because this pass is static source reconstruction
against committed HLIL/Ghidra evidence and does not need audio-device behavior
to disambiguate.

## Verification

- `python -m pytest tests\test_client_sound_voice_parity.py::test_background_track_ogg_update_matches_retail_restart_path -q --tb=short`
  - `1 passed`
- `python -m pytest tests\test_client_sound_voice_parity.py tests\test_client_sound_playback_parity.py tests\test_win32_sound_dma_parity.py tests\test_cgame_sound_wiring_parity.py tests\test_botlib_cgame_native_import_slab_parity.py -q --tb=short`
  - `26 passed`
- `git diff --check -- src\code\client\snd_dma.c tests\test_client_sound_voice_parity.py docs\reverse-engineering\quakelive_steam_mapping_round_451.md`
  - No whitespace errors; Git reported LF-to-CRLF normalization warnings for
    the touched source/test files.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .vscode/build.ps1 -Configuration Debug -Platform x86 -Targets quakelive_steam`
  - `Build succeeded.`
  - `0 Warning(s)`
  - `0 Error(s)`

## Parity Estimate

- Focused background-music start/update parity: **82% -> 96%**.
- Focused background OGG restart-loop wiring: **88% -> 96%**.
- Broader client sound-system reconstruction confidence: **91% -> 92%**.
