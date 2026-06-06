# Botlib Residual Gap And Wiring Audit - 2026-06-06

## Scope

This pass closes the current static mapping audit over the
`quakelive_steam.exe` botlib neighborhood from `0x00482000..0x004A8400` and
rechecks the native qagame botlib import bridge. The goal was to identify
whether any remaining unaliased functions still looked like botlib source
reconstruction candidates after the route, reachability, movement, chat,
character, item, and export-table mapping rounds.

No C source reconstruction was made in this pass. The remaining unpromoted
addresses are classification decisions rather than missing botlib owners.

## Evidence

- Canonical symbol evidence:
  - `references/analysis/quakelive_symbol_aliases.json`
  - `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- Canonical HLIL evidence:
  - `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part03.txt`
- Source wiring evidence:
  - `src/code/botlib/be_interface.c`
  - `src/code/game/botlib.h`
  - `src/code/game/g_public.h`
  - `src/code/game/g_syscalls.c`
  - `src/code/server/sv_game.c`
  - `src/code/server/ql_game_imports.inc`
  - `src/code/botlib/be_aas_move.c`
- Regression gate:
  - `tests/test_botlib_residual_gap_and_wiring_parity.py`

## Observed Facts

- The `0x00482000..0x004A8400` neighborhood has `417` Ghidra function rows.
- `401` of those rows are now promoted in `quakelive_symbol_aliases.json`.
- The same address band has `407` promoted aliases overall; six promoted
  aliases in the band are present in HLIL/alias evidence but are not emitted as
  rows in this `functions.csv` snapshot.
- The only unaliased addresses left in the neighborhood are:
  - `0x00482150`, `0x004821F0`, `0x00482290`, `0x004823E0`,
    `0x00482530`, `0x00482640`, `0x00482780`, `0x004828A0`,
    `0x004828C0`, `0x004828E0`, `0x004828F0`, `0x00482910`,
    `0x00482930`, `0x00482950`, `0x004829A0`
  - `0x00486F40`
- The first group is before `sub_4829C0 -> AAS_Trace` and is contiguous with
  libjpeg memory-manager evidence:
  - nearby aliases include `sub_480290 -> jinit_marker_reader`,
    `sub_4811C0 -> jpeg_fdct_float`, and `sub_4814A0 -> jpeg_idct_float`
  - HLIL seeds an allocation-method table with `sub_482290`,
    `sub_4823E0`, `sub_482530`, and `sub_482640`
  - the same block reads `JPEGMEM`
  - terminal helpers are plain `memcpy`/`memset` style routines
- `0x00486F40` is the compiler-folded weapon-jump wrapper. Source has both
  `AAS_RocketJumpZVelocity` and `AAS_BFGJumpZVelocity`, but both currently
  return `AAS_WeaponJumpZVelocity(origin, 120)`, matching the retail thunk
  that forwards to `sub_486D40 -> AAS_WeaponJumpZVelocity`.
- The native botlib import bridge exposes `134` `G_QL_IMPORT_BOTLIB_*` slots.
  `131` are regular qagame syscall remaps. The other three are intentional
  direct native slots:
  - `G_QL_IMPORT_BOTLIB_AI_DRAW_DEBUG_AREAS`
  - `G_QL_IMPORT_BOTLIB_AI_DRAW_AVOID_SPOTS`
  - `G_QL_IMPORT_BOTLIB_EA_WALK`
- Every public `G_QL_IMPORT_BOTLIB_*` slot has a server-side
  `ql_game_imports[...]` registration and a generated or local
  `QL_G_trap_*` implementation.
- `GetBotLibAPI` still gates `BOTLIB_API_VERSION == 2`, initializes AAS, EA,
  and AI exports in order, assigns the top-level lifecycle/parser/export
  callbacks, and returns `be_botlib_export`.

## Inference

The botlib-neighborhood residual set is now closed for this mapping tranche:
the unaliased pre-`AAS_Trace` rows should remain classified as libjpeg
memory-manager false leads, and `sub_486F40` should remain unpromoted unless
the source deliberately unfuses the two weapon-jump wrappers. There is no new
botlib source reconstruction target in the residual address scan.

The higher-risk remaining botlib work is therefore not "find another unnamed
function in this band"; it is behavioral validation of already mapped source
areas when a specific retail hypothesis appears.

## Parity Estimate

- Focused residual botlib address classification:
  **before 70% -> after 98%**
- Native botlib import bridge closure:
  **before 90% -> after 98%**
- Overall botlib plus related wiring estimate:
  **before 82% -> after 83%**

The overall movement is small because this round intentionally locks down
classification and bridge consistency rather than adding new source behavior.

## Follow-Up

- Do not promote `0x00482150..0x004829A0` as botlib unless new evidence
  contradicts the current libjpeg memory-manager classification.
- Do not promote `sub_486F40` while both source wrappers are identical retail
  thunks to `AAS_WeaponJumpZVelocity(origin, 120)`.
- Use runtime probes only for future botlib behavior questions that cannot be
  answered from HLIL, Ghidra, source comparison, and static regression tests.
