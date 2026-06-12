# Botlib QAGame Instagib Exit Cleanup Reconstruction - 2026-06-12

## Scope

This pass closes the remaining raw cleanup-offset boundary in the source-backed
`AINode_InstaGib` tutorial flow. The reconstructed source lives in
`src/code/game/ai_dmnet.c`.

## Evidence

- Owning retail binary: `qagamex86.dll`.
- Binary Ninja HLIL:
  `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt`.
- Companion Ghidra row: `FUN_10013410,10013410,1711,0,unknown`.
- Alias support: `sub_10013410` / `FUN_10013410` => `AINode_InstaGib`.
- Source layout support:
  - `gentity_t.flags` is the retail entity flag word used by the training
    tutorial helpers.
  - `playerState_t.powerups[PW_FLIGHT]` is at player-state offset `0x158`.
  - `playerState_t.powerups[PW_REDFLAG]` is at player-state offset `0x15c`.

Observed facts:

- Retail `AINode_InstaGib` intermission exit clears entity flag `0x00010000`,
  clears player-state offset `0x158`, clears player-state offset `0x15c`, then
  clears `bs->ltgtype` before entering intermission.
- Retail `AINode_InstaGib` death exit performs the same cleanup sequence before
  entering respawn.
- The observer, no-AI, and found-enemy exits have different cleanup shapes and
  do not receive this source helper.

Reconstruction:

- Follow-up 2026-06-12: the raw entity bit is now shared as
  `FL_BOT_TRAINING_GODMODE`, matching the training helper's named sidecar bit.
- Added `BotInstaGibExitCleanup` to clear:
  - `g_entities[bs->client].flags & ~FL_BOT_TRAINING_GODMODE`;
  - `g_entities[bs->client].client->ps.powerups[PW_FLIGHT]`;
  - `g_entities[bs->client].client->ps.powerups[PW_REDFLAG]`;
  - `bs->ltgtype`.
- Routed the `BotIntermission(bs)` and `BotIsDead(bs)` exits through the helper.
- Extended `tests/test_botlib_qagame_ai_dmnet_tutorial_tail_parity.py` to pin
  the helper body, the two call sites, and the six retail HLIL cleanup anchors.

## Confidence

Confidence is high. The cleanup writes are directly visible in retail HLIL and
the two player-state offsets resolve to stable source fields confirmed by the
current reconstructed `playerState_t` layout.

Parity estimate: focused Instagib exit cleanup source confidence **40% ->
99%**; focused source-backed Instagib node reconstruction confidence **88% ->
93%**; overall botlib plus qagame/server wiring reconstruction parity
**84.18% -> 84.21%**.
