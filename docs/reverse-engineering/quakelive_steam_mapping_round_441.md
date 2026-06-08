# quakelive_steam.exe Mapping Round 441

Date: 2026-06-08

Scope: Win32 DirectSound DMA host aliases and source reconstruction for the
retail sound backend.

## Summary

This round maps the contiguous DirectSound host helper cluster around the
existing `SNDDMA_InitDS` entry and reconstructs the retail background-audio
control in `src/code/win32/win_snd.c`.

The current source already carried most of the Quake Live DirectSound backend:
COM startup/shutdown, DirectSound 8 fallback, the 22 kHz stereo 16-bit DMA
format, lock/restore handling, submit unlocks, and activation recovery. The
new source delta is limited to retail's `s_muteBackground` cvar, which controls
whether hardware and software secondary buffers receive `DSBCAPS_GLOBALFOCUS`.

## Evidence

Primary evidence:

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `src/code/win32/win_snd.c`

Observed facts:

1. The owning binary is `quakelive_steam.exe`; the Win32 sound host calls COM
   and DirectSound imports rather than the VM sound modules.
2. `functions.csv` records eight contiguous DirectSound helper owners:
   `FUN_004ef9f0` size `60`, `FUN_004efa30` size `330`,
   `FUN_004efb80` size `103`, `FUN_004efbf0` size `258`,
   `FUN_004efd00` size `36`, `FUN_004efd30` size `49`,
   `FUN_004efd70` size `795`, and `FUN_004f0090` size `93`.
3. HLIL `sub_4ef9f0` maps DirectSound HRESULTs to the visible diagnostic
   strings `DSERR_PRIOLEVELNEEDED`, `DSERR_INVALIDPARAM`,
   `DSERR_INVALIDCALLS`, `DSERR_BUFFERLOST`, and `unknown`.
4. HLIL `sub_4efa30` prints the DirectSound shutdown diagnostics, releases the
   secondary and primary buffers, frees `DSOUND.DLL`, clears the DMA block, and
   tailcalls `CoUninitialize`.
5. HLIL `sub_4efbf0` handles `GetStatus`, buffer restore/play recovery, lock
   retries on `DSERR_BUFFERLOST`, the `SNDDMA_BeginPainting` lock-failure
   diagnostic, and sound-system shutdown on unrecoverable lock failure.
6. HLIL `sub_4efd70` prints `Initializing DirectSound`, registers
   `s_muteBackground` with default `1` and flags `0x21`, sets the secondary
   buffer flags, and ORs `0x8000` into both the hardware and software flag
   paths when the cvar integer is zero.
7. The source cvar flag definitions identify `0x21` as
   `CVAR_ARCHIVE | CVAR_LATCH`.
8. The Windows SDK DirectSound flag represented by `0x8000` is
   `DSBCAPS_GLOBALFOCUS`, matching the source reconstruction: if background
   muting is disabled, keep DirectSound playback focused globally.

## Alias Updates

- `sub_4EF9F0 -> DSoundError`
- `sub_4EFA30 -> SNDDMA_Shutdown`
- `sub_4EFB80 -> SNDDMA_GetDMAPos`
- `sub_4EFBF0 -> SNDDMA_BeginPainting`
- `sub_4EFD00 -> SNDDMA_Submit`
- `sub_4EFD30 -> SNDDMA_Activate`
- `sub_4EFD70 -> SNDDMA_InitDS`
- `sub_4F0090 -> SNDDMA_Init`

## Source Reconstruction

`SNDDMA_InitDS()` now registers `s_muteBackground` with retail's default and
flags:

- name: `s_muteBackground`
- default: `1`
- flags: `CVAR_ARCHIVE | CVAR_LATCH`

When `s_muteBackground` is `0`, both the hardware and software secondary-buffer
creation paths add `DSBCAPS_GLOBALFOCUS`, matching the two retail HLIL branches
that OR `0x8000` into the DirectSound buffer flags.

## Verification

Commands run:

- `python -m json.tool references\analysis\quakelive_symbol_aliases.json > $null`
  -> passed
- `python -m pytest tests\test_win32_sound_dma_parity.py tests\test_client_sound_voice_parity.py -q --tb=short`
  -> `11 passed`
- `git diff --check -- references\analysis\quakelive_symbol_aliases.json src\code\win32\win_snd.c tests\test_win32_sound_dma_parity.py docs\reverse-engineering\quakelive_steam_mapping_round_441.md`
  -> passed with only LF-to-CRLF working-copy warnings on existing text files

## Parity Estimate

- Focused Win32 DirectSound DMA host mapping: **72% -> 93%**.
- Focused DirectSound source behavior parity: **88% -> 95%**.
- Broader client sound-system reconstruction confidence: **85% -> 87%**.
- Repo-wide checked-in tree parity: **99% -> 99%**.
