# Quake Live Steam Mapping Round 461: Soundtime Return-Value Reconstruction

## Scope

This round tightens the sound update spine around retail
`sub_4DB490 -> S_GetSoundtime`. The helper was already behaviorally present in
source, but it still used the old `void` source signature while the committed
Ghidra row and Binary Ninja HLIL expose an `int32_t` return.

## Evidence

Primary evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/analysis/quakelive_symbol_aliases.json`

Observed facts:

- `FUN_004db490`, size 209, is promoted as `S_GetSoundtime`.
- HLIL labels the function as `004db490 int32_t sub_4db490()`.
- The helper computes `s_soundtime` from the DMA sample position and buffer-wrap
  count, matching the retained Quake III source structure.
- The small submission-chunk path writes `s_paintedtime` from
  `s_soundtime + s_mixPreStep * dma.speed` and returns that painted time.
- The normal submission-chunk path writes
  `s_paintedtime = s_soundtime + dma.submission_chunk` and returns
  `s_soundtime`.
- `sub_4DB570 -> S_Update_` calls `sub_4DB490` but ignores its return value,
  so the source reconstruction is a function-boundary parity fix rather than a
  runtime behavior change.

## Source Reconstruction

Implemented source changes:

- Changed `S_GetSoundtime` in `src/code/client/snd_dma.c` from `void` to `int`.
- Added the required function header comment above the definition.
- Returned `s_paintedtime` from the small submission-chunk path.
- Returned `s_soundtime` from the normal path.
- Expanded `tests/test_client_sound_playback_parity.py` to pin the retail
  `int32_t` HLIL signature, both HLIL return anchors, and the source return
  statements.

## Confidence

High confidence:

- Function ownership and Ghidra size for `S_GetSoundtime`.
- Return type and ignored-call relationship from `S_Update_`.
- The two modeled return values in the source-visible paths.

Medium confidence:

- Retail HLIL includes a guard on an adjacent global after the DMA struct before
  updating `s_paintedtime`. The current source does not expose a clean named
  owner for that global, so this pass reconstructs the signature and return
  values without inventing a new field.

## Validation

- `python -m pytest tests\test_client_sound_playback_parity.py::test_sound_buffer_loop_raw_and_update_helpers_match_retail_wiring -q --tb=short`
  - 1 passed.
- `python -m pytest tests\test_client_sound_voice_parity.py tests\test_client_sound_playback_parity.py tests\test_win32_sound_dma_parity.py tests\test_cgame_sound_wiring_parity.py tests\test_botlib_cgame_native_import_slab_parity.py -q --tb=short`
  - 26 passed.
- `python -m pytest tests\test_platform_services.py::test_native_import_dispatch_normalizes_qboolean_contracts -q --tb=short`
  - 1 passed.
- `git diff --check -- src\code\client\snd_dma.c tests\test_client_sound_playback_parity.py docs\reverse-engineering\quakelive_steam_mapping_round_461.md`
  - Passed with repository LF-to-CRLF working-copy warning only.
- `C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe src\code\quakelive.sln /p:Configuration=Debug /p:Platform=x86 /p:PlatformToolset=v143 /v:minimal`
  - Build succeeded.

## Parity Estimate

- Focused `S_GetSoundtime` function-boundary parity: 84% -> 94%.
- Sound update spine parity: 88% -> 89%.
- Overall client sound-system reconstruction parity: 82% -> 83%.
