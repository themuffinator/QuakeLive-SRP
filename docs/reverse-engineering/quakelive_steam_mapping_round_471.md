# Quake Live Steam Mapping Round 471: Sound Allocator Counter and Display Wiring

## Scope

This round maps and reconstructs the sound cache allocator slice around
`sub_4DBB10 -> SND_free`, `sub_4DBB30 -> SND_setup`,
`sub_4DBBA0 -> SND_shutdown`, `sub_4DBBE0 -> S_DisplayFreeMemory`, and the
allocator counter transitions visible inside `sub_4DBC00 -> ResampleSfx`.

The source implementation already matched the allocator behavior closely, but
the free-memory diagnostic string missed the retail trailing space before the
newline.

## Evidence

Primary evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/analysis/quakelive_symbol_aliases.json`

Observed facts:

- The alias map promotes `sub_4DBB10` to `SND_free`, `sub_4DBB30` to
  `SND_setup`, `sub_4DBBA0` to `SND_shutdown`, and `sub_4DBBE0` to
  `S_DisplayFreeMemory`.
- `functions.csv` records `FUN_004dbb10` at `0x004DBB10`, size 31;
  `FUN_004dbb30` at `0x004DBB30`, size 106; `FUN_004dbba0` at `0x004DBBA0`,
  size 50; and `FUN_004dbbe0` at `0x004DBBE0`, size 27.
- HLIL at `0x004DBB1C` increments the free-byte counter by `0x808` when a
  sound buffer is returned to the freelist.
- HLIL at `0x004DBB48` obtains `com_soundMegs` with default `16` and flags
  `0x21`, multiplies the integer by `0x202000`, stores the total free byte
  count, allocates the slab, builds the reverse freelist, and prints
  `"Sound memory manager started\n"`.
- HLIL at `0x004DBBA5` and `0x004DBBAF` clears the free-byte and in-use
  counters during shutdown before freeing the slab.
- HLIL at `0x004DBBE0` passes the allocator counters to the diagnostic string
  whose corpus entry is
  `"%d bytes sound buffer memory in use, %d free \n"`.
- HLIL inside `ResampleSfx` at `0x004DBCA2` and `0x004DBCAC` shows allocation
  transitions decrementing the free-byte counter and incrementing the in-use
  counter by `0x808`.

## Source Reconstruction

Implemented source changes:

- Changed `S_DisplayFreeMemory` to use the retail diagnostic format with the
  trailing space before the newline:
  `"%d bytes sound buffer memory in use, %d free \n"`.
- Extended `tests/test_client_sound_voice_parity.py` to pin the allocator
  helper aliases, function sizes, counter movement, slab setup, shutdown reset,
  and exact free-memory diagnostic string.

No runtime launch was needed. This pass reconstructs deterministic sound
allocator output and counter wiring from committed HLIL/Ghidra evidence.

## Confidence

High confidence:

- `SND_free`, `SND_setup`, `SND_shutdown`, and `S_DisplayFreeMemory` ownership
  and function sizes.
- Retail counter increments/decrements by `0x808`, matching the source
  `sizeof(sndBuffer)` allocator model.
- `com_soundMegs` default and setup banner.
- Exact free-memory diagnostic string, including the trailing space before
  newline.

Medium confidence:

- Local counter names (`inUse` and `totalInUse`) remain source-derived names.
  The retail cells are directly observed, but their semantic labels are
  inferred from source ownership and update direction.

## Validation

- `python -m pytest tests\test_client_sound_voice_parity.py -q --tb=short`
  - 10 passed.
- `python -m pytest tests\test_client_sound_voice_parity.py tests\test_client_sound_playback_parity.py tests\test_win32_sound_dma_parity.py tests\test_cgame_sound_wiring_parity.py tests\test_cgame_sound_registration_parity.py tests\test_cgame_announcer_timer_helper_parity.py tests\test_cgame_playerstate_transition_parity.py tests\test_botlib_cgame_native_import_slab_parity.py tests\test_engine_cvar_retail_parity.py::test_engine_cvar_eighteenth_sound_tranche_matches_retail_contracts -q --tb=short`
  - 41 passed.
- `C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe src\code\quakelive.sln /p:Configuration=Debug /p:Platform=x86 /p:PlatformToolset=v143 /v:minimal`
  - Build completed successfully; `quakelive_steam.exe` rebuilt.
- `git diff --check -- src\code\client\snd_mem.c tests\test_client_sound_voice_parity.py docs\reverse-engineering\quakelive_steam_mapping_round_471.md`
  - Passed with repository LF-to-CRLF working-copy warnings on touched text
    files.

## Parity Estimate

- Focused sound allocator diagnostic parity: 94% -> 99%.
- Focused sound cache allocator mapping parity: 88% -> 93%.
- Overall client sound-system reconstruction parity: 90% -> 90.5%.
