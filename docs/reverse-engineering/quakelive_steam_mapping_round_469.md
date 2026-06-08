# Quake Live Steam Mapping Round 469: Cgame Warmup Announcer Volume Sound Wiring

## Scope

This round maps and reconstructs the cgame-side announcer sound wiring around
`sub_1000eb30 -> CG_PlayWarmupCountSound`, with companion mapping for adjacent
sound helpers `sub_10015450 -> CG_SetEntitySoundPosition` and
`sub_1001ec10 -> CG_FragmentBounceSound`.

The main source gap was that warmup countdown and round-start announcer clips
still used the plain local-sound syscall wrapper. Retail cgame routes these
through the volume-aware local-sound import and the cgame VM mirror of
`s_announcerVolume`.

## Evidence

Primary evidence:

- `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt`
- `references/reverse-engineering/ghidra/cgamex86/functions.csv`
- `references/analysis/quakelive_symbol_aliases.json`

Observed facts:

- The alias map promotes `FUN_1000eb30` / `sub_1000eb30` to
  `CG_PlayWarmupCountSound`, `FUN_10015450` / `sub_10015450` to
  `CG_SetEntitySoundPosition`, `FUN_1001ec10` / `sub_1001ec10` to
  `CG_FragmentBounceSound`, `FUN_10020dd0` / `sub_10020dd0` to
  `CG_BuildAnnouncerSoundPath`, `FUN_10020e70` to `CG_RegisterSounds`, and
  `FUN_100435b0` to `CG_CheckLocalSounds`.
- `functions.csv` records `FUN_1000eb30` at `0x1000eb30`, size 151;
  `FUN_10015450` at `0x10015450`, size 168; `FUN_1001ec10` at `0x1001ec10`,
  size 190; `FUN_10020dd0` at `0x10020dd0`, size 122; `FUN_10020e70` at
  `0x10020e70`, size 8324; and `FUN_100435b0` at `0x100435b0`, size 1420.
- HLIL at `0x1000eb8c` calls import-table slot `data_1074cccc + 0xa0` for
  the one, two, three, prepare-to-fight, and round-begins-in clips.
- Those calls pass channel `7` and
  `fconvert.s(fconvert.t(data_10a6b528))`; the data corpus names the backing
  string at `0x1006a930` as `"s_announcerVolume"` and the cvar-table pointer at
  `0x100784d4` as that same string.
- The cvar-table row for `s_announcerVolume` points at the VM cvar storage base
  whose `value` field is observed as `data_10a6b528`, and carries the same
  default/range/flag pattern as `s_killBeepVolume`: default `1`, minimum `0`,
  maximum `4`, archive/protected/VM-created/cloud flags.
- HLIL at `0x10015450` updates entity sound positions directly for non-bmodel
  entities, and adds `cgs.inlineModelMidpoints[modelindex]` before the
  update-position syscall for `SOLID_BMODEL`.
- HLIL at `0x1001ec10` uses `rand() & 3` for blood fragment bounce sounds,
  import-table slot `data_1074cccc + 0x94` for world-positioned playback, and
  the retail `rand() & 4` electro-fragment quirk before clearing the bounce
  sound type.

## Source Reconstruction

Implemented source changes:

- Added the cgame VM mirror `s_announcerVolume` in `cg_main.c`.
- Added the cvar-table row:
  `s_announcerVolume`, default `1`, flags
  `CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD`, range
  `0..4`.
- Exposed `s_announcerVolume` through `cg_local.h`.
- Replaced five `CG_PlayWarmupCountSound` calls from
  `trap_S_StartLocalSound(..., CHAN_ANNOUNCER)` to
  `trap_QL_S_StartLocalSoundVolume(..., CHAN_ANNOUNCER, s_announcerVolume.value)`.
- Preserved the existing source-side guards for missing registered sound
  handles; the retail-backed reconstruction is the syscall slot and volume
  source, not removal of local defensive checks.
- Extended `tests/test_cgame_sound_wiring_parity.py` to pin the cgame sound
  helper aliases, function sizes, warmup announcer volume import, VM cvar row,
  entity-position wiring, and fragment-bounce sound selection quirks.

No runtime launch was needed. This pass reconstructs deterministic cgame sound
wiring from committed HLIL/Ghidra evidence and source-level parity tests.

## Confidence

High confidence:

- `CG_PlayWarmupCountSound` ownership and retail import slot `+0xa0` for the
  affected announcer clips.
- `s_announcerVolume` cgame cvar ownership, default, range, and flags.
- Use of `s_announcerVolume.value` as the third argument to the volume-aware
  local-sound wrapper.
- `CG_SetEntitySoundPosition` bmodel midpoint wiring.
- `CG_FragmentBounceSound` blood/electro random-selection behavior and
  world-channel playback.

Medium confidence:

- The source keeps handle-existence guards around warmup sounds that are not
  visible in the retail HLIL slice. They are harmless defensive checks, but the
  exact retail low-level expression has no corresponding guard at this level.

## Validation

- `python -m pytest tests\test_cgame_sound_wiring_parity.py -q --tb=short`
  - 6 passed.
- `python -m pytest tests\test_client_sound_voice_parity.py tests\test_client_sound_playback_parity.py tests\test_win32_sound_dma_parity.py tests\test_cgame_sound_wiring_parity.py tests\test_cgame_announcer_timer_helper_parity.py tests\test_cgame_playerstate_transition_parity.py tests\test_botlib_cgame_native_import_slab_parity.py tests\test_engine_cvar_retail_parity.py::test_engine_cvar_eighteenth_sound_tranche_matches_retail_contracts -q --tb=short`
  - 38 passed.
- `C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe src\code\quakelive.sln /p:Configuration=Debug /p:Platform=x86 /p:PlatformToolset=v143 /v:minimal`
  - Build completed successfully; `cgamex86.dll` rebuilt.
- `git diff --check -- src\code\cgame\cg_draw.c src\code\cgame\cg_local.h src\code\cgame\cg_main.c tests\test_cgame_sound_wiring_parity.py docs\reverse-engineering\quakelive_steam_mapping_round_469.md`
  - Passed with repository LF-to-CRLF working-copy warnings on touched text
    files.

## Parity Estimate

- Focused warmup countdown announcer volume wiring parity: 72% -> 96%.
- Focused cgame sound helper mapping parity: 86% -> 91%.
- Overall client/cgame sound-system reconstruction parity: 88% -> 89%.
