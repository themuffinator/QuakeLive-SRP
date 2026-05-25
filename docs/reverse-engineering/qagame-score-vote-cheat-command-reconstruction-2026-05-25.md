# Qagame Score, Vote, and Cheat Command Reconstruction - 2026-05-25

## Scope

This pass covered ten non-chat client-issued `game` commands handled by
`qagamex86.dll` through `ClientCommand`:

- `score`
- `acc`
- `pstats`
- `readyup`
- `vote`
- `give`
- `god`
- `notarget`
- `noclip`
- `kill`

The adjacent retail-only `ragequit` compare was rechecked as boundary evidence.
It is visible in the retail command ladder between `readyup` and `vote`, but
its target is a one-argument native import at `data_104B13AC + 0x300`; this pass
does not reconstruct that behavior until the import owner is revalidated.

## Evidence

- Owning retail binary: `qagamex86.dll`.
- Corpus baseline: `references/reverse-engineering/ghidra/qagamex86/metadata.txt`,
  `imports.txt`, `exports.txt`, and `functions.csv`.
- Symbol map: `references/symbol-maps/qagame.json`.
- Canonical HLIL:
  - `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt`
  - `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt`

The relevant `ClientCommand` ladder begins at `sub_10045DEC`. After the
chat/voice cluster, retail compares `score`, `acc`, `pstats`, `readyup`,
`ragequit`, and `vote` before the intermission gate that protects `give`,
`god`, `notarget`, `noclip`, `kill`, and the later gameplay commands.

Observable strings and helper anchors include `acc %s`, `pstats %s`,
`No vote in progress.`, `Vote cast.`, `godmode ON/OFF`, `notarget ON/OFF`,
`noclip ON/OFF`, and `Kill is not enabled on this server.`

## Reconstruction

- Reordered `src/code/game/g_cmds.c::ClientCommand` so `acc`, `pstats`,
  `readyup`, and `vote` are handled in the same pre-intermission cluster as the
  retail ladder.
- Moved the source compatibility branches (`ready`, `notready`, `unready`,
  `players`, `teams`, and `cvar`) after the recovered retail `vote` branch.
- Removed the later post-intermission `vote` branch, making
  `Cmd_Vote_f` reachable during intermission so `G_HandleNextMapVote` can serve
  the retail next-map ballot flow.
- Added a focused parity sentinel in
  `tests/test_game_helper_seam_parity.py` tying the ten command names to
  source dispatch order, helper bodies, HLIL command strings, and recovered
  vote/cheat/self-kill messages.

## Open Boundary

Retail `ragequit` remains a mapped but unreconstructed neighbor in this ladder.
The command token is certain, but the import call at `data_104B13AC + 0x300`
needs a separate native-import mapping pass before source behavior should be
introduced.

## Parity Estimate

Before this pass, the scoped ten-command surface was about **72%**
reconstructed: handlers existed, but the source ladder mixed source-local
commands into the retail pre-intermission cluster and left the recovered
intermission `vote` path unreachable from `ClientCommand`.

After this pass, the scoped surface is about **93%** reconstructed. The main
remaining uncertainty is the adjacent `ragequit` native-import behavior and
fine-grained optimized helper layout, not the ten selected command handlers.
The repo-wide parity estimate remains **98%**.

## Verification

- `python -m pytest tests/test_game_helper_seam_parity.py -q --tb=short -k "score_vote_cheat_client_command_tranche"`:
  `1 passed, 29 deselected`.
- `python -m pytest tests/test_game_helper_seam_parity.py -q --tb=short`:
  `30 passed`.
- `python -m pytest tests/test_game_exit_rules_parity.py::test_nextmap_vote_pipeline_matches_retail_intermission_vote_flow tests/test_vote_ui_throttle.py::test_vote_ui_throttle_transitions -q --tb=short`:
  `1 passed, 1 skipped`.
