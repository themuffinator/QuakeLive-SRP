# quakelive_steam.exe Mapping Round 439

Date: 2026-06-08

Scope: client sound helper cleanup around the Quake Live voice, OGG, WAV, and
background-track stream corridor at `0x004D9B20..0x004DCC70`.

## Summary

This round promotes `11` additional sound-system aliases and makes one small
source reconstruction in the sample decode path. The mapped area sits between
the previously closed retained `snd_dma.c` / `snd_mem.c` / `snd_mix.c` core
from rounds 59 and 60 and the OGG-specific closure from round 199.

The source-visible reconstruction aligns non-mono decode handling with retail:
Quake Live drops on non-mono OGG and WAV assets instead of merely printing and
soft-failing the sound.

## Evidence

Primary evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/analysis/quakelive_symbol_aliases.json`
- `src/code/client/snd_dma.c`
- `src/code/client/snd_mem.c`
- `src/code/client/snd_ogg_decode.c`
- `src/code/client/snd_ogg_stream.c`

Observed facts:

1. `sub_4D9B20` is the small sound-file type classifier used by
   `S_LoadSound`: it checks the extension against `.ogg` and `.wav` and
   returns the OGG/WAV type selector consumed by the load branch.
2. `sub_4DAB00` owns the five-lane voice ring rooted at `data_13e1860`.
   It searches by client number, reuses expired lanes, reports silenced
   clients when all five lanes are active, schedules initial playback from
   `s_paintedtime`, and writes PCM samples into a `0x4000` sample circular
   buffer. This matches the reconstructed `S_AddVoiceSamples` source path.
3. `sub_4DB1C0` is the background-track update pump. It smooths music volume,
   reads OGG bytes through `sub_4DCA50`, submits decoded frames through
   `S_RawSamples`, closes exhausted streams through `sub_4DCA40`, and restarts
   the configured loop track through `S_StartBackgroundTrack`.
4. `sub_4DBBA0` frees the sound slab and clears the sound-memory counters,
   matching the now-source-owned `SND_shutdown` lifecycle.
5. `sub_4DC920` is the OGG sample-load wrapper used by `S_LoadSound`: it
   copies file bytes into temporary memory, calls `S_VorbisDecodeMemory`, and
   frees the temporary copy afterward.
6. `sub_4DC960` and `sub_4DC980` are the background OGG stream read and close
   callbacks. They bridge the Vorbis callback table to Quake Live filesystem
   reads and file-handle close respectively.
7. `sub_4DCA40` closes the retained background OGG Vorbis state. The current
   source factors this through the generic `S_OggStreamClose` wrapper, so the
   promoted name records the retail global owner as `S_CloseBackgroundOgg`.
8. `sub_4DCAD0`, `sub_4DCB20`, and `sub_4DCC70` cover WAV chunk discovery,
   RIFF/WAVE header parsing, and WAV sample loading. The HLIL confirms the
   `RIFF`, `WAVE`, `fmt `, and `data` constants, the aligned chunk-length
   walk, and the retail diagnostics for non-mono, non-16-bit, and non-22kHz
   assets.
9. `sub_4D99B0` was rechecked and intentionally left unpromoted in this
   sound pass. Its table begins with map-token pairs such as `qzca1` to
   `asylum`, and its callers are server map loading / `mapname` publication,
   so it is adjacent to the sound band but not a sound-system helper.

## Aliases Added

- `sub_4D9B20` -> `S_SoundFileTypeForPath`
- `sub_4DAB00` -> `S_AddVoiceSamples`
- `sub_4DB1C0` -> `S_UpdateBackgroundTrack`
- `sub_4DBBA0` -> `SND_shutdown`
- `sub_4DC920` -> `S_LoadOggSound`
- `sub_4DC960` -> `S_OggReadCallback`
- `sub_4DC980` -> `S_OggCloseCallback`
- `sub_4DCA40` -> `S_CloseBackgroundOgg`
- `sub_4DCAD0` -> `S_FindWavChunk`
- `sub_4DCB20` -> `GetWavinfo`
- `sub_4DCC70` -> `S_LoadWavSound`

## Source Reconstruction

`src/code/client/snd_ogg_decode.c` now clears the Vorbis decode state and calls
`Com_Error( ERR_DROP, "%s is not a mono file", ... )` on non-mono OGG streams,
matching the retail `sub_4DC730` path.

`src/code/client/snd_mem.c` now drops on non-mono WAV loads with
`"%s is not a mono wav file"` and uses the retail `WAV_Load:` diagnostics for
non-16-bit or non-22kHz assets. The current source still keeps the broader
source-side memory-buffer WAV parser rather than splitting out a separate
retail-shaped file-handle `S_LoadWavSound` helper; the diagnostic and error
contract is the source-visible parity fix from this round.

## Verification

Static validation added in `tests/test_client_sound_voice_parity.py` pins the
new aliases, Ghidra function rows, HLIL control-flow/string anchors, and source
diagnostic changes.

Commands run:

- `python -m json.tool references\analysis\quakelive_symbol_aliases.json > $null`
- `python -m pytest tests\test_client_sound_voice_parity.py -q --tb=short`
  -> `9 passed`
- `python -m pytest tests\test_cgame_sound_registration_parity.py -q --tb=short`
  -> `2 passed`
- `git diff --check -- src\code\client\snd_mem.c src\code\client\snd_ogg_decode.c tests\test_client_sound_voice_parity.py references\analysis\quakelive_symbol_aliases.json docs\reverse-engineering\quakelive_steam_mapping_round_439.md`
  -> passed with only existing LF-to-CRLF working-copy warnings on touched text
  files.

## Parity Estimate

- Focused sound helper mapping confidence: **82% -> 96%**.
- Focused OGG/WAV decode error-contract source parity: **88% -> 97%**.
- Strict retail Windows replacement target: **100% -> 100%**.
- Repo-wide checked-in tree parity: **99% -> 99%**.
