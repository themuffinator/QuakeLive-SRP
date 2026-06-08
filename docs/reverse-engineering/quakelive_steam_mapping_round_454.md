# Quake Live Steam Mapping Round 454: Sound WAV/OGG Asset Loader Ownership

## Scope

This round continues the retail `quakelive_steam.exe` sound-system reconstruction after the background-music OGG pass. The target was the sound-effect asset loader cluster around the retail Binary Ninja/Ghidra names:

- `sub_4D9B20` / `FUN_004d9b20`, size 63: `S_SoundFileTypeForPath`
- `sub_4DC920` / `FUN_004dc920`, size 55: `S_LoadOggSound`
- `sub_4DCAD0` / `FUN_004dcad0`, size 71: `S_FindWavChunk`
- `sub_4DCB20` / `FUN_004dcb20`, size 326: `GetWavinfo`
- `sub_4DCC70` / `FUN_004dcc70`, size 177: `S_LoadWavSound`

## Evidence

Observed retail facts:

- `sub_4D9B20` classifies by extension only: `.ogg` returns type `2`, `.wav` returns type `1`, and other extensions return `0`.
- `S_LoadSound` in the retail HLIL opens the requested asset, retries the same path with a default `.ogg` extension when the original open fails, then dispatches by the file-type value to `S_LoadWavSound` or `S_LoadOggSound`.
- `sub_4DC920` allocates a temporary file-sized buffer, reads the open file through `FS_Read`, calls the Vorbis memory decoder, and frees the temporary buffer.
- `sub_4DCAD0` is not a background-music helper. It is adjacent to `GetWavinfo` and reads the next WAV chunk id and length, rejects negative lengths, and returns `(len + 1) & ~1` only when the requested chunk id matches.
- `sub_4DCB20` calls the chunk helper for `RIFF`, `fmt `, and `data`, verifies `WAVE`/PCM structure, fills the `wavinfo_t`-style fields, and returns the data length.
- `sub_4DCC70` enforces mono WAV input with `"%s is not a mono wav file"` and keeps the retail 16-bit / 22 kHz debug diagnostics before resampling into the sound cache.

## Source Reconstruction

Implemented source changes:

- Replaced the GPL-era `FindChunk` / `FindNextChunk` scanner in `src/code/client/snd_mem.c` with a named `S_FindWavChunk` helper owned by the WAV sound-effect loader.
- Added `S_SoundFileTypeForPath` with explicit retail values `0`, `1`, and `2`.
- Split the asset-load path into `S_LoadWavSound`, `S_LoadOggSound`, and a shared `S_LoadPCMSound` cache/resample helper.
- Updated `S_LoadSoundFile` so the `.ogg` retry also carries the retail file-type dispatch value.
- Removed the stale file-handle `S_FindWavChunk`, `FGetLittleShort`, and `FGetLittleLong` helpers from `src/code/client/snd_dma.c`; after the OGG-only background-track reconstruction they no longer had a valid caller and were misleading the alias map.

## Confidence

High confidence:

- Function ownership and names for the WAV/OGG sound-effect cluster.
- Extension classifier values.
- WAV chunk helper behavior and ownership.
- Removal of the background-music WAV helper from `snd_dma.c`.

Medium confidence:

- The source still uses the existing `FS_ReadFile` loaded-buffer path under `S_LoadSoundFile`, while retail opens a file handle and lets `S_LoadWavSound` / `S_LoadOggSound` read through `FS_Read`. The helper boundaries and behavior now match the retail graph, but a future pass can convert the lower-level I/O representation if needed.

## Validation

- `python -m pytest tests\test_client_sound_voice_parity.py::test_sound_helper_aliases_cover_retail_ogg_wav_voice_cluster tests\test_client_sound_voice_parity.py::test_sound_cache_and_shutdown_match_retail_allocator_contracts tests\test_client_sound_voice_parity.py::test_background_track_ogg_update_matches_retail_restart_path -q --tb=short`
- `python -m pytest tests\test_client_sound_voice_parity.py tests\test_client_sound_playback_parity.py tests\test_win32_sound_dma_parity.py tests\test_cgame_sound_wiring_parity.py tests\test_botlib_cgame_native_import_slab_parity.py -q --tb=short`
- `git diff --check -- src\code\client\snd_mem.c src\code\client\snd_dma.c tests\test_client_sound_voice_parity.py`
  - Only repository line-ending warnings were reported.
- `C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe src\code\quakelive.sln /m /p:Configuration=Debug /p:Platform=x86 /p:PlatformToolset=v143 /v:minimal`
  - Build succeeded.
