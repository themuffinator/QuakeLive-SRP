# Botlib qagame Powerup Active Vector Reconstruction - 2026-06-12

## Scope

This pass tightened the `BotAIStartFrame` producer for the Quake Live
botlib entity-state active-powerup vector. The previous reconstruction carried
the recovered tail layout but still had a source-only nonzero guard and a
defensive `MAX_POWERUPS` loop bound in the 16-slot producer.

## Retail evidence

- Owning producer binary: `qagamex86.dll`.
- Owning bridge consumer binary: `quakelive_steam.exe`.
- Ghidra `qagamex86` `BotAIStartFrame` seeds a cursor at
  `&DAT_1008ff18`, reads playerstate powerup timers from `client + 0x180`,
  and writes a 16-word local vector before calling the botlib update import.
- The Ghidra predicate is:
  - if the timer is earlier than the table threshold and not `-1`, write `0`;
  - otherwise write `1`.
- Binary Ninja HLIL carries the same condition as
  `if (edx_31 s>= *j || edx_31 == 0xffffffff)`.
- Retail advances the metadata cursor by `0x30` bytes per slot and stops at
  `DAT_10090218`, matching 16 produced vector entries.
- The engine-side `AAS_UpdateEntity` tail copy remains the existing 16-word
  transfer from producer words `0x22..0x31` to entity-info words `0x29..0x38`.

## Source reconstruction

- `BotAIStartFrame` now iterates exactly
  `BOTLIB_QL_POWERUP_ACTIVE_COUNT` entries for the active vector.
- The source-side predicate now matches the recovered retail shape:
  `powerupTime >= level.time || powerupTime == INT_MAX`.
- The previous source-only `powerupTime != 0` check was removed.
- The previous redundant loop guard against `MAX_POWERUPS` was removed; the
  retail ABI, `BOTLIB_QL_POWERUP_ACTIVE_COUNT`, and current
  `playerState_t::powerups` storage are all 16 entries in this source base.

## Open questions

The exact source owner of the stride-`0x30`
`DAT_1008ff18..DAT_10090218` table remains open. The table is used by multiple
qagame item and powerup paths, so this pass only reconstructed the producer
predicate and loop shape. It does not invent a new item metadata symbol.

## Verification

- `tests/test_botlib_entity_update_bridge_parity.py` now pins the 16-slot
  producer loop, rejects the removed source-only guards, and cross-checks the
  Ghidra and HLIL retail predicates.
- `tests/test_botlib_internal_parity.py` carries the same source and retail
  anchors through the broader internal botlib parity gate.

## Parity estimate

- Focused botlib active-powerup vector producer confidence:
  **before 78% -> after 96%**.
- Focused botlib entity-state producer source-shape confidence:
  **before 96% -> after 98%**.
- Overall botlib plus qagame/server wiring reconstruction parity:
  **before 84.24% -> after 84.27%**.
