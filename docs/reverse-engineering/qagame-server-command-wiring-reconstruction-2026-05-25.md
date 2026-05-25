# Qagame Server Command Wiring Reconstruction - 2026-05-25

## Scope

This pass covered ten retail `game` server-command surfaces that bridge the
direct in-game command table and server-console command dispatcher:

- Direct command table: `addscore`, `addteamscore`, `setmatchtime`.
- Server console dispatch: `entitylist`, `forceteam`, `game_memory`, `addbot`,
  `botlist`, `game_crash`, and `reload_access`.

Adjacent retail-dispatch evidence for `forceshuffle`, `dumpvars`, and the
legacy handled no-op debug tokens (`markstate`, `diffstate`, `dumpentities`,
`printentitystates`) was rechecked as context, but the ten commands above were
the reconstruction target for this tranche.

## Evidence

- Owning retail binary: `qagamex86.dll`.
- Corpus baseline: `references/reverse-engineering/ghidra/qagamex86/metadata.txt`,
  `imports.txt`, `exports.txt`, and `functions.csv`.
- Symbol map: `references/symbol-maps/qagame.json`.
- Canonical HLIL:
  - `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt`
  - `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt`

The direct table at `data_10080750` provides the table-layout anchor for
`addscore`, `addteamscore`, and `setmatchtime`, with command strings at
`data_100884B4`, `data_1008846C`, and `data_10088420`.

The server-console dispatcher at `sub_10066B90` compares the command token
against `entitylist`, `forceteam`, `game_memory`, `addbot`, `botlist`,
`game_crash`, `forceshuffle`, `dumpvars`, `markstate`, `reload_access`,
`diffstate`, `dumpentities`, and `printentitystates` before falling into the
dedicated-server chat path.

`Svcmd_AddBot_f` is `sub_10037910`. Its late local-client media refresh sends
`loaddeferred\n`; the committed source had the old Quake III typo in that
path, so the reconstruction corrected it to the retail Quake Live spelling.

## Reconstruction

- Revalidated the direct command-table tail already reconstructed in
  `src/code/game/g_cmds.c`: `addscore`, `addteamscore`, and `setmatchtime`
  remain moderator-level table rows backed by the recovered score and
  match-time handlers.
- Revalidated server-console dispatch in `src/code/game/g_svcmds.c`:
  `entitylist` routes to `Svcmd_EntityList_f`, `forceteam` to
  `Svcmd_ForceTeam_f`, `game_memory` to `Svcmd_GameMem_f`, `addbot` to
  `Svcmd_AddBot_f`, `botlist` to `Svcmd_BotList_f`, `game_crash` to the
  developer-gated crash helper, and `reload_access` to `G_ReloadAdminAccess`.
- Corrected `src/code/game/g_bot.c` so the gameplay-time `addbot` media refresh
  sends `loaddeferred\n`, matching the HLIL and the training-bot path.
- Added a focused parity sentinel in
  `tests/test_game_helper_seam_parity.py` that ties the ten command names to
  source dispatch, helper bodies, symbol-map identities, and HLIL strings.

## Parity Estimate

Before this pass, the scoped ten-command qagame server-command surface was
about **82%** reconstructed: the major helpers and direct rows were present, but
the `addbot` media-refresh command still carried the inherited misspelling and
the cross-surface evidence was spread across older tests and notes.

After this pass, the scoped surface is about **94%** reconstructed. The
remaining uncertainty is mostly source-layout fidelity for optimized/inlined
retail leaves such as `game_memory` and `game_crash`, not command ownership or
observable behavior. The repo-wide parity estimate remains **98%**.

## Verification

- `python -m pytest tests/test_game_helper_seam_parity.py -q --tb=short -k "server_command_wiring or console_tail or direct_score_time"`:
  `3 passed, 25 deselected`.
- `python -m pytest tests/test_game_helper_seam_parity.py -q --tb=short`:
  `28 passed`.
