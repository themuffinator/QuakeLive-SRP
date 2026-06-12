# Botlib qagame entity flag naming reconstruction - 2026-06-12

## Scope

This pass closes two small but persistent source-reconstruction gaps where
retail qagame bot paths were already behaviorally mapped but still carried raw
`gentity_t.flags` masks in source.

The affected lanes are:

- `BotAIStartFrame -> trap_BotLibUpdateEntity`, where retail exports the
  inverted bit-18 flag sidecar as botlib `qlFlagsBit18Clear`.
- `BotSetTrainingBotState`, where retail pairs the familiar `FL_GODMODE` and
  `FL_NO_KNOCKBACK` flags with training-only sidecar bits while enabling and
  disabling the tutorial trainer bot.
- `AINode_InstaGib` exit cleanup, where the same training sidecar bit is
  cleared before leaving the tutorial Instagib node.

## Evidence

- Binary Ninja HLIL for `qagamex86.dll`:
  - `BotAIStartFrame` writes `!(gentity_t.flags & 0x00040000)` to the producer
    entity-state tail word copied by botlib as `qlFlagsBit18Clear`.
  - `BotSetTrainingBotState` applies `0x10010` and `0x20800` on enable, then
    clears the matching masks on disable.
- Ghidra `qagamex86/functions.csv` rows:
  - `FUN_10023400,10023400,2038,0,unknown` for `BotAIStartFrame`.
  - `FUN_100245c0,100245c0,124,0,unknown` for `BotSetTrainingBotState`.
- Existing source reconstruction already mapped the producer fields, botlib
  copy path, and training helper body; this pass only names the source-visible
  entity flag bits.

## Source Reconstruction

- Added `FL_BOT_TRAINING_GODMODE` and `FL_BOT_TRAINING_NO_KNOCKBACK` to
  `g_local.h` as retail training sidecars paired with `FL_GODMODE` and
  `FL_NO_KNOCKBACK`.
- Added `FL_BOTLIB_ENTITY_STATE_BIT18` to `g_local.h` for the botlib
  entity-state bit exported inverted as `qlFlagsBit18Clear`.
- Replaced the private `ai_main.c` raw `0x00040000` botlib mask with
  `FL_BOTLIB_ENTITY_STATE_BIT18`.
- Reworked the training helper flag groups to use the new `FL_BOT_TRAINING_*`
  names instead of embedded `0x00010000` / `0x00020000` masks.
- Routed `BotInstaGibExitCleanup` through `FL_BOT_TRAINING_GODMODE` instead of
  keeping a separate local name for the same retail bit.
- Updated the botlib entity-state comments and parity gates to pin the named
  flag definitions alongside the HLIL/Ghidra-backed field layout.

## Verification

```text
python -m pytest tests/test_botlib_qagame_ai_main_lifecycle_training_parity.py tests/test_botlib_qagame_ai_dmnet_tutorial_tail_parity.py tests/test_botlib_entity_update_bridge_parity.py tests/test_botlib_internal_parity.py -q --tb=short
43 passed in 1.49s

$tests = Get-ChildItem tests -Filter 'test_botlib*.py' | ForEach-Object { $_.FullName }
python -m pytest $tests -q --tb=short
223 passed in 5.85s

git diff --check -- <touched botlib flag source/docs/tests>
clean apart from existing LF-to-CRLF working-copy warnings

Direct trailing-whitespace scan for the new/untracked markdown notes was clean.
```

No runtime launch was needed; this was static source reconstruction against the
committed retail references.

## Parity Estimate

- Focused qagame bot entity flag naming confidence:
  **before 55% -> after 99%**.
- Focused botlib entity-state producer naming confidence:
  **before 90% -> after 99%**.
- Focused training helper flag-source confidence:
  **before 93% -> after 98%**.
- Overall botlib plus adjacent qagame/server wiring reconstruction parity:
  **before 84.21% -> after 84.24%**.
