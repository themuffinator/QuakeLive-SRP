# Quake Live Steam Mapping Round 465: Spatializer Distance Falloff

## Scope

This round tightens the positional sound spatializer around retail
`sub_4D9EF0 -> S_SpatializeOrigin`. The retained Quake III source still used
an 80-unit full-volume radius before applying attenuation. The retail Quake
Live spatializer instead gates positional sounds at a 1250-unit maximum
distance and attenuates directly from the normalized listener distance.

## Evidence

Primary evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/analysis/quakelive_symbol_aliases.json`

Observed facts:

- `functions.csv` records `FUN_004d9ef0` at `0x004D9EF0`, size 352.
- The alias map promotes `sub_4D9EF0` to `S_SpatializeOrigin`.
- HLIL subtracts listener origin from the source origin, then calls
  `sub_4D8190`, the promoted `VectorNormalize`, on that vector.
- Retail compares the normalized distance against `1250f`. When the compare
  fails the helper writes zero to both output volumes and returns.
- The attenuation factor is derived from the distance and
  `0.00079999997979030013`.
- The mono path writes equal left/right volume from the same attenuation value.
- The stereo path rotates the source vector through the listener axis,
  computes right/left scales from `0.5 * (1 +/- dot)`, clamps negative channel
  scales, then applies the same distance attenuation.

## Source Reconstruction

Implemented source changes:

- Replaced the inherited `SOUND_FULLVOLUME 80` constant in
  `src/code/client/snd_dma.c` with `SOUND_MAXDISTANCE 1250.0f`.
- Updated `S_SpatializeOrigin` to zero both output channels and return when
  `dist >= SOUND_MAXDISTANCE`.
- Removed the old `dist -= SOUND_FULLVOLUME` full-volume-radius branch.
- Kept the retail `0.0008f` attenuation multiplier and existing mono/stereo
  pan math.
- Extended `tests/test_client_sound_playback_parity.py` to pin the promoted
  `sub_4D9EF0` alias/function-size row, HLIL distance/attenuation anchors, and
  the absence of the old 80-unit source branch.

No runtime launch was needed because this pass is static source reconstruction
against committed HLIL/Ghidra evidence. The relevant behavior is the
deterministic spatializer math and call wiring, not audio-device output.

## Confidence

High confidence:

- Function ownership and size for `S_SpatializeOrigin`.
- Retail maximum-distance constant and early zero-output branch.
- Removal of the Quake III `SOUND_FULLVOLUME 80` attenuation shape.

Medium confidence:

- Binary Ninja's x87 stack variable names obscure whether the decompiler names
  the post-compare temporary as the original distance or a stack expression.
  The surrounding compare, zero-return, mono branch, and final scale equations
  still support the source reconstruction as a direct distance falloff with a
  1250-unit cutoff.

## Validation

- `python -m pytest tests\test_client_sound_playback_parity.py::test_sound_spatializer_uses_retail_max_distance_falloff -q --tb=short`
  - 1 passed.
- `python -m pytest tests\test_client_sound_voice_parity.py tests\test_client_sound_playback_parity.py tests\test_win32_sound_dma_parity.py tests\test_cgame_sound_wiring_parity.py tests\test_botlib_cgame_native_import_slab_parity.py -q --tb=short`
  - 27 passed.
- `git diff --check -- src\code\client\snd_dma.c tests\test_client_sound_playback_parity.py docs\reverse-engineering\quakelive_steam_mapping_round_465.md`
  - Passed with the repository LF-to-CRLF working-copy warning on
    `src/code/client/snd_dma.c`.
- `C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe src\code\quakelive.sln /p:Configuration=Debug /p:Platform=x86 /p:PlatformToolset=v143 /v:minimal`
  - Build succeeded.

## Parity Estimate

- Focused `S_SpatializeOrigin` attenuation parity: 78% -> 94%.
- Positional sound playback parity: 88% -> 91%.
- Overall client sound-system reconstruction parity: 84% -> 85%.
