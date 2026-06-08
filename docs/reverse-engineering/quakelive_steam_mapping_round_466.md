# Quake Live Steam Mapping Round 466: Voice Lane Diagnostics and Reuse

## Scope

This round tightens the voice PCM path around retail
`sub_4DAB00 -> S_AddVoiceSamples` and the voice paint loop inside
`S_PaintChannels`. The source already had the five-lane circular voice buffer,
but it still used a source-side near-finished preemption fallback and omitted
the retail diagnostics that make voice lane ownership, queue pressure, and
paint-window consumption visible.

## Evidence

Primary evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/analysis/quakelive_symbol_aliases.json`

Observed facts:

- The alias map promotes `sub_4DAB00` to `S_AddVoiceSamples`.
- `functions.csv` records `FUN_004dab00` at `0x004DAB00`, size 373.
- HLIL shows a five-entry voice channel scan rooted at `data_13e1860`, matching
  the `MAX_VOICE_CHANNELS == 5` source lane count.
- When no existing client lane is found, retail compares
  `s_paintedtime - lane.endSample` against `dma.samples * 0.5`.
- Retail logs new lane assignment with `client %d: using voice %d`.
- Retail logs no available lane with `client %d silenced: no voices left` and
  returns without adding samples.
- Retail logs initial queue start, queued sample count, overflow trimming, and
  final samples added to the voice buffer.
- The paint loop logs `voice channel %d: no data in the paint window` when a
  buffered voice lane does not intersect the current paint interval.
- The paint loop logs `voice channel %d: consumed all buffered voice samples`
  when advancing the lane start consumes the queued voice payload.

## Source Reconstruction

Implemented source changes:

- Replaced the source-only `endSample <= s_paintedtime` immediate reuse and
  `dma.speed * 0.5f` near-finished preemption fallback with the retail
  `s_paintedtime - endSample > dma.samples * 0.5f` lane-reuse threshold.
- Added `Com_DPrintf` diagnostics for retail voice lane assignment and silence.
- Added `Com_DPrintf` diagnostics for voice start sample, already queued
  samples, overflow trimming, and samples added to the circular buffer.
- Added `Com_DPrintf` diagnostics in the voice paint loop for no paint-window
  overlap and fully consumed voice buffers.
- Extended `tests/test_client_sound_voice_parity.py` to pin the retail HLIL
  anchors, string table entries, source lane threshold, source diagnostics, and
  absence of the old near-finished preemption fallback.

No runtime launch was needed because this pass reconstructs deterministic
queueing and debug-output behavior from committed HLIL/Ghidra evidence.

## Confidence

High confidence:

- Function ownership, size, and string ownership for `S_AddVoiceSamples`.
- Five-lane voice buffer shape and `0x4000` sample ring.
- Retail diagnostics and paint-loop diagnostic strings.
- Removal of the source-only near-finished preemption fallback.

Medium confidence:

- Binary Ninja's x87 comparison rendering around the `dma.samples * 0.5`
  threshold is not perfectly named, but the single-loop shape, silence branch,
  and string placement strongly support the source reconstruction.

## Validation

- `python -m pytest tests\test_client_sound_voice_parity.py::test_voice_mixer_reconstructs_retail_lane_shape_and_cvars -q --tb=short`
  - 1 passed.
- `python -m pytest tests\test_client_sound_voice_parity.py tests\test_client_sound_playback_parity.py tests\test_win32_sound_dma_parity.py tests\test_cgame_sound_wiring_parity.py tests\test_botlib_cgame_native_import_slab_parity.py -q --tb=short`
  - 27 passed.
- `git diff --check -- src\code\client\snd_dma.c src\code\client\snd_mix.c tests\test_client_sound_voice_parity.py docs\reverse-engineering\quakelive_steam_mapping_round_466.md`
  - Passed with repository LF-to-CRLF working-copy warnings on touched C/Python
    files.
- `C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe src\code\quakelive.sln /p:Configuration=Debug /p:Platform=x86 /p:PlatformToolset=v143 /v:minimal`
  - Build succeeded.

## Parity Estimate

- Focused voice lane queueing/diagnostic parity: 76% -> 94%.
- Steam voice-to-sound wiring parity: 89% -> 91%.
- Overall client sound-system reconstruction parity: 85% -> 86%.
