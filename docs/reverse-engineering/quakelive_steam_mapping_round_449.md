# quakelive_steam.exe Mapping Round 449

Date: 2026-06-08

Scope: client sound initialization cvar surface and Win32 DMA sample-rate
wiring.

## Summary

This round removes two retained Quake III sound controls that are absent from
the retail Quake Live Steam sound initialization path: `s_khz` and
`s_separation`.

Retail `S_Init` registers the Quake Live sound cvar set for volume, music,
voice, announcer, mixer timing, PVS, doppler, diagnostics, and `s_initsound`.
The retail references do not expose `s_khz` or `s_separation`, and the Win32
DMA setup uses the fixed 22050 Hz PCM path instead of a user-selected sample
rate branch.

## Evidence

Primary evidence:

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `src/code/client/snd_dma.c`
- `src/code/client/snd_local.h`
- `src/code/win32/win_snd.c`

Observed facts:

1. `functions.csv` records `FUN_004db870` at `0x004DB870`, and the alias map
   identifies `sub_4DB870` as `S_Init`.
2. The retail `S_Init` HLIL contains string/cvar evidence for
   `s_announcerVolume`, `s_doppler`, `s_initsound`, `s_mixahead`,
   `s_mixPreStep`, `s_musicvolume`, `s_pvs`, `s_voiceVolume`, `s_voiceStep`,
   `s_show`, `s_testsound`, and `s_volume`.
3. The same HLIL corpus has no `"s_khz"` or `"s_separation"` string evidence
   in the retail executable.
4. The source previously kept `s_khz` and `s_separation` globals, public
   externs, and post-`s_initsound` registrations even though no active sound
   path consumed them.
5. `win_snd.c` already executes a fixed `dma.speed = 22050` path, matching the
   retail fixed-rate behavior, with only commented GPL-era `s_khz` branches
   remaining.

## Source Reconstruction

- Removed the inactive `s_khz` and `s_separation` cvar globals from
  `snd_dma.c`.
- Removed their public extern declarations from `snd_local.h`.
- Removed their post-`s_initsound` `Cvar_Get` registrations from `S_Init`.
- Removed stale commented-out `s_separation` spatialization formulas and
  commented-out `s_khz` sample-rate selection branches.
- Extended `tests/test_client_sound_playback_parity.py` to pin the retail
  sound-init cvar surface, absence of the legacy controls, and fixed Win32
  22050 Hz DMA setup.

No runtime launch was needed because this change is static source
reconstruction against committed HLIL/Ghidra evidence and does not need audio
device behavior to disambiguate.

## Verification

- `python -m pytest tests\test_client_sound_playback_parity.py tests\test_engine_cvar_retail_parity.py::test_engine_cvar_eighteenth_sound_tranche_matches_retail_contracts tests\test_win32_sound_dma_parity.py -q --tb=short`
  - `8 passed`
- `git diff --check -- src\code\client\snd_dma.c src\code\client\snd_local.h src\code\win32\win_snd.c tests\test_client_sound_playback_parity.py docs\reverse-engineering\quakelive_steam_mapping_round_449.md`
  - No whitespace errors; Git reported LF-to-CRLF normalization warnings for
    the touched source files.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .vscode/build.ps1 -Configuration Debug -Platform x86 -Targets quakelive_steam`
  - `Build succeeded.`
  - `0 Warning(s)`
  - `0 Error(s)`

## Parity Estimate

- Focused sound initialization cvar surface: **86% -> 96%**.
- Focused Win32 DMA sample-rate wiring confidence: **94% -> 97%**.
- Broader client sound-system reconstruction confidence: **89% -> 90%**.
