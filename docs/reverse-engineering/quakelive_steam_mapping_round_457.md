# Quake Live Steam Mapping Round 457: Handle-Based Sound Asset Loading

## Scope

This round closes the loader gap left after the WAV/OGG helper ownership pass. The target was retail `S_LoadSound` and its direct wiring to handle-based WAV/OGG loaders in `quakelive_steam.exe`.

## Evidence

Primary retail evidence:

- `sub_4DBD00` / `FUN_004dbd00`, size 228, maps to `S_LoadSound`.
- `sub_4DBD37` calls `sub_4D9B20(&arg1[4])`, the sound file extension classifier.
- `sub_4DBD40` calls `sub_4CF640(&arg1[4], &var_4c, 1)`, matching `FS_FOpenFileRead(..., qtrue)`.
- On a missing handle, retail copies the name, applies default `.ogg`, forces type `2`, and opens again.
- Type `1` dispatches to `sub_4DCC70(arg1, ecx_2)` / `S_LoadWavSound`.
- Type `2` dispatches to `sub_4DC920(arg1, ecx_2, eax_4)` / `S_LoadOggSound`.
- `sub_4CF320(ecx_2)` closes the handle, then `arg1[0x14] = sub_4CAF40()` stamps `lastTimeUsed`.

Companion loader evidence:

- `sub_4DC920` allocates a temporary file-sized buffer, reads the open handle through `FS_Read`, calls the Vorbis memory decoder, and frees the file buffer.
- `sub_4DCAD0` and `sub_4DCB20` read WAV chunk headers through `FS_Read`, not a preloaded source buffer.
- `sub_4DCC70` reads exactly the WAV data chunk length into temporary memory before resampling into the sound cache.

## Source Reconstruction

Implemented in `src/code/client/snd_mem.c`:

- Replaced `S_LoadSoundFile` with `S_OpenSoundFile`, using `FS_FOpenFileRead(..., qtrue)` and the same `.ogg` retry/type-forcing behavior visible in HLIL.
- Converted `S_ReadWavBytes`, `GetLittleShort`, `GetLittleLong`, `S_FindWavChunk`, and `GetWavinfo` to read from `fileHandle_t` through `FS_Read`.
- Converted `S_LoadWavSound` to parse the WAV header from the open handle, allocate the data chunk length, read that chunk through `FS_Read`, and pass the resulting PCM source into the shared resample/cache helper.
- Converted `S_LoadOggSound` to allocate a file-sized temp buffer, read the handle through `FS_Read`, decode through `S_VorbisDecodeMemory`, and free the file buffer.
- Moved the `lastTimeUsed` stamp out of the PCM helper and into the `S_LoadSound` close path as `Com_Milliseconds()`, matching retail placement more closely than the inherited `+1` stamp.

Updated `tests/test_client_sound_voice_parity.py` to pin:

- `sub_4DBD00` alias/function-size coverage.
- The `FS_FOpenFileRead`/`FS_FCloseFile` dispatch path.
- Absence of the older `FS_ReadFile`/`FS_FreeFile` loaded-buffer path in this sound-effect loader.
- Handle-based WAV chunk reads and temp-buffer reads for OGG/WAV payloads.

## Confidence

High confidence:

- `S_LoadSound` owner, function size, open/retry/dispatch/close/stamp shape.
- Handle-based WAV chunk parser ownership.
- OGG file-buffer read path before Vorbis decode.

Medium confidence:

- Error behavior for malformed WAV chunks still retains some inherited diagnostic prints before the retail mono `Com_Error` path. The retail HLIL mostly returns zero through the parser and lets the loader enforce mono; exact malformed-file diagnostics remain a low-priority edge.

## Validation

- `python -m pytest tests\test_client_sound_voice_parity.py::test_sound_helper_aliases_cover_retail_ogg_wav_voice_cluster tests\test_client_sound_voice_parity.py::test_sound_cache_and_shutdown_match_retail_allocator_contracts -q --tb=short`
  - 2 passed.
- `python -m pytest tests\test_client_sound_voice_parity.py tests\test_client_sound_playback_parity.py tests\test_win32_sound_dma_parity.py tests\test_cgame_sound_wiring_parity.py tests\test_botlib_cgame_native_import_slab_parity.py -q --tb=short`
  - 26 passed.
- `git diff --check -- src\code\client\snd_mem.c tests\test_client_sound_voice_parity.py`
  - Only repository LF-to-CRLF warnings were reported.
- `C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe src\code\quakelive.sln /p:Configuration=Debug /p:Platform=x86 /p:PlatformToolset=v143 /v:minimal`
  - Build succeeded.

Note: the first `/m` build attempt reached link/post-build but hit a transient BSCMAKE `.sbr` open error. The immediate non-parallel build passed without source changes.
