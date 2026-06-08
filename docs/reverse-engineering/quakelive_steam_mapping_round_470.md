# Quake Live Steam Mapping Round 470: Sound Lifecycle Setup State Edges

## Scope

This round maps and reconstructs the engine sound lifecycle slice around
`sub_4D9C50 -> S_ChannelSetup`, `sub_4D9CA0 -> S_Shutdown`,
`sub_4DB870 -> S_Init`, and `sub_4DBAD0 -> S_DisableSounds`.

The source was already close, but two lifecycle details differed from retail:
channel setup suppressed repeated debug output through a source-only static
guard, and successful sound initialization still left the retail
`s_numSfx = 0` reset commented out.

## Evidence

Primary evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/analysis/quakelive_symbol_aliases.json`

Observed facts:

- The alias map promotes `sub_4D9C50` to `S_ChannelSetup`, `sub_4D9CA0` to
  `S_Shutdown`, `sub_4DB450` to `S_StopAllSounds`, `sub_4DB870` to `S_Init`,
  and `sub_4DBAD0` to `S_DisableSounds`.
- `functions.csv` records `FUN_004d9c50` at `0x004D9C50`, size 74;
  `FUN_004d9ca0` at `0x004D9CA0`, size 83; `FUN_004db450` at `0x004DB450`,
  size 49; `FUN_004db870` at `0x004DB870`, size 593; and `FUN_004dbad0` at
  `0x004DBAD0`, size 59.
- HLIL at `0x004D9C5C` clears the channel slab with
  `sub_4c95e0(&data_14298c0, 0, 0x1500)`, rebuilds the reverse freelist from
  `data_142ad88` down to `data_14298c0`, stores the freelist head at
  `data_12c5b78`, and always returns through
  `"Channel memory manager started\n"`.
- No retail guard exists around the channel setup banner.
- HLIL at `0x004DBA70` sets sound-started state, `0x004DBA75` sets the muted
  state, `0x004DBA7A` resets the known-sound count, and `0x004DBA80` clears
  the sound hash table before resetting sound clocks and clearing active
  sounds.
- HLIL at `0x004D9CA0` confirms shutdown ordering: sound allocator shutdown,
  DMA shutdown, started-state clear, then removal of `play`, `music`, `s_list`,
  `s_info`, and `s_stop`.
- HLIL at `0x004DBAD0` confirms the disable path reuses the stop-all-sounds
  clearing behavior and then sets the muted flag.

## Source Reconstruction

Implemented source changes:

- Removed the source-only `s_channelInitPrinted` guard from `S_ChannelSetup`.
- Restored unconditional `Com_DPrintf("Channel memory manager started\n")`
  after rebuilding the channel freelist.
- Restored `s_numSfx = 0` in the successful `S_Init` path, matching the retail
  post-DMA initialization state reset.
- Extended `tests/test_client_sound_playback_parity.py` to pin lifecycle
  aliases, function sizes, HLIL state edges, and the source-level absence of
  the one-shot channel setup guard.

No runtime launch was needed. This pass reconstructs deterministic sound
startup/shutdown state from committed HLIL/Ghidra evidence and compile-time
source tests.

## Confidence

High confidence:

- `S_ChannelSetup` ownership, size, freelist rebuild, and unconditional debug
  banner.
- `S_Init` successful-start state order through `s_soundStarted`,
  `s_soundMuted`, `s_numSfx`, `sfxHash`, sound clocks, `S_StopAllSounds`, and
  `S_SoundInfo_f`.
- `S_Shutdown` command removal order.
- `S_DisableSounds` stop-and-mute behavior.

Medium confidence:

- The exact local symbol names for the global retail state cells are inferred
  from source ownership and cross-function use. The side effects themselves are
  directly observed in HLIL.

## Validation

- `python -m pytest tests\test_client_sound_playback_parity.py -q --tb=short`
  - 7 passed.
- `python -m pytest tests\test_client_sound_voice_parity.py tests\test_client_sound_playback_parity.py tests\test_win32_sound_dma_parity.py tests\test_cgame_sound_wiring_parity.py tests\test_cgame_sound_registration_parity.py tests\test_cgame_announcer_timer_helper_parity.py tests\test_cgame_playerstate_transition_parity.py tests\test_botlib_cgame_native_import_slab_parity.py tests\test_engine_cvar_retail_parity.py::test_engine_cvar_eighteenth_sound_tranche_matches_retail_contracts -q --tb=short`
  - 41 passed.
- `C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe src\code\quakelive.sln /p:Configuration=Debug /p:Platform=x86 /p:PlatformToolset=v143 /v:minimal`
  - Build completed successfully; `quakelive_steam.exe` rebuilt.
- `git diff --check -- src\code\client\snd_dma.c tests\test_client_sound_playback_parity.py docs\reverse-engineering\quakelive_steam_mapping_round_470.md`
  - Passed with repository LF-to-CRLF working-copy warnings on touched text
    files.

## Parity Estimate

- Focused sound lifecycle setup-state parity: 89% -> 96%.
- Focused engine playback lifecycle mapping parity: 90% -> 93%.
- Overall client sound-system reconstruction parity: 89% -> 90%.
