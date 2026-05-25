# Qagame Chat and Voice Command Reconstruction - 2026-05-25

## Scope

This pass covered ten retail client-issued `game` commands handled by
`qagamex86.dll` through the `ClientCommand` ladder:

- `say`
- `say_team`
- `tell`
- `botSay`
- `vsay`
- `vsay_team`
- `vtell`
- `vosay`
- `vosay_team`
- `votell`

The adjacent `vtaunt` branch was rechecked as boundary evidence because it
terminates the same retail voice-command cluster. The source-local
`complaint` command remains available, but it is no longer placed between
`botSay` and `vsay`, where retail HLIL has no matching command-token compare.

## Evidence

- Owning retail binary: `qagamex86.dll`.
- Corpus baseline: `references/reverse-engineering/ghidra/qagamex86/metadata.txt`,
  `imports.txt`, `exports.txt`, and `functions.csv`.
- Symbol map: `references/symbol-maps/qagame.json`.
- Canonical HLIL:
  - `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt`
  - `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt`

The command-token chain at `sub_10045DEC` compares the client command against
`say`, `say_team`, `tell`, `botSay`, `vsay`, `vsay_team`, `vtell`, `vosay`,
`vosay_team`, `votell`, and then `vtaunt` before entering the next command
cluster. The helper calls behind that ladder map to `Cmd_Say_f`,
`Cmd_Tell_f`, `Cmd_BotSay_f`, `Cmd_Voice_f`, `Cmd_VoiceTell_f`, and
`Cmd_VoiceTaunt_f`.

String and helper anchors include the `sayteam: %s: %s\n` log, `vtell: %s to
%s: %s\n`, `vchat`, `vtchat`, `vtell`, and the retained bot chat payload.

## Reconstruction

- Reordered `src/code/game/g_cmds.c::ClientCommand` so the retail chat/voice
  ladder flows directly from `botSay` into `vsay`.
- Kept `complaint` as a supported source command, but moved it after the
  adjacent `vtaunt` voice boundary so it does not interrupt the reconstructed
  retail ladder.
- Added a focused parity sentinel in
  `tests/test_game_helper_seam_parity.py` that checks the ten command-token
  order, handler calls, symbol-map names, retained HLIL strings, voice command
  transports, tell echo behavior, bot chat behavior, and voice flood labels.

## Parity Estimate

Before this pass, the scoped chat/voice command surface was about **78%**
reconstructed: the handlers were present and mostly behaviorally aligned, but
the command ladder had a source-local `complaint` branch inside the retail
chat/voice cluster and the ten-command surface was not pinned as one unit.

After this pass, the scoped surface is about **95%** reconstructed. Remaining
uncertainty is mostly retail optimization detail in the compact HLIL voice
helpers, not command ownership or observable dispatch behavior. The repo-wide
parity estimate remains **98%**.

## Verification

- `python -m pytest tests/test_game_helper_seam_parity.py -q --tb=short -k "chat_voice_client_command_tranche or game_say_reconstructs"`:
  `2 passed, 27 deselected`.
- `python -m pytest tests/test_game_helper_seam_parity.py -q --tb=short`:
  `29 passed`.
