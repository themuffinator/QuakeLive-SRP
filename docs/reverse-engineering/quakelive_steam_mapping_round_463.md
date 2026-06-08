# Quake Live Steam Mapping Round 463: Uniform Loop-Sound Spatialization Volume

## Scope

This round tightens the client sound loop mixer around retail
`sub_4DA6F0 -> S_AddLoopSounds`. The retained Quake III source still used the
older `kill` latch to choose between a full-volume 3D path and a lower-volume
sphere path. The retail Quake Live loop mixer spatializes both the primary loop
record and merged duplicate loop records with `0x7f`.

## Evidence

Primary evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/analysis/quakelive_symbol_aliases.json`

Observed facts:

- `functions.csv` records `FUN_004da6f0` at `0x004DA6F0`, size 328.
- The alias map promotes `sub_4DA6F0` to `S_AddLoopSounds`.
- HLIL shows the loop mixer clearing the raw-merge count, advancing the loop
  frame, and walking loop records in the retail 0x34-byte stride.
- The primary loop spatialization call is
  `sub_4d9ef0(&var_8, &var_c, i - 0x2c, 0x7f)`.
- The merged duplicate loop spatialization call is
  `sub_4d9ef0(&var_20, &var_1c, j - 0x28, 0x7f)`.
- No `0x5a` / 90-volume alternate branch appears in the retail loop mixer.

## Source Reconstruction

Implemented source changes:

- Changed the primary `S_AddLoopSounds` spatialization path in
  `src/code/client/snd_dma.c` to always call
  `S_SpatializeOrigin( loop->origin, 127, &left_total, &right_total )`.
- Changed the duplicate-merge spatialization path to always call
  `S_SpatializeOrigin( loop2->origin, 127, &left, &right )`.
- Left the compatibility `kill` field and `S_AddRealLoopingSound` entry point
  intact for the existing source/QVM surface, but stopped using that latch to
  lower the mixer volume.
- Expanded `tests/test_client_sound_playback_parity.py` to pin both HLIL
  `0x7f` spatialization anchors and reject the old `90`-volume branches inside
  `S_AddLoopSounds`.

No runtime launch was needed because this is a static source reconstruction
against committed Binary Ninja HLIL and Ghidra evidence; audio-device behavior
does not disambiguate the branch shape.

## Confidence

High confidence:

- Function ownership and size for `S_AddLoopSounds`.
- Uniform `0x7f` master volume for primary and merged loop spatialization.
- Absence of the retained source `90`-volume branch in the retail loop mixer.

Medium confidence:

- The retained `S_AddRealLoopingSound` compatibility surface remains useful for
  source and VM callers, but the exact retail-era source-level intent behind
  the old `kill` name is no longer represented in the native mixer.

## Validation

- `python -m pytest tests\test_client_sound_playback_parity.py::test_sound_buffer_loop_raw_and_update_helpers_match_retail_wiring -q --tb=short`
  - 1 passed.
- `python -m pytest tests\test_client_sound_voice_parity.py tests\test_client_sound_playback_parity.py tests\test_win32_sound_dma_parity.py tests\test_cgame_sound_wiring_parity.py tests\test_botlib_cgame_native_import_slab_parity.py -q --tb=short`
  - 26 passed.
- `python -m pytest tests\test_platform_services.py::test_native_import_dispatch_normalizes_qboolean_contracts -q --tb=short`
  - 1 passed.
- `C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe src\code\quakelive.sln /p:Configuration=Debug /p:Platform=x86 /p:PlatformToolset=v143 /v:minimal`
  - Build succeeded.

## Parity Estimate

- Focused `S_AddLoopSounds` source behavior parity: 84% -> 96%.
- Looping-sound playback/mix parity: 89% -> 92%.
- Overall client sound-system reconstruction parity: 83% -> 84%.
