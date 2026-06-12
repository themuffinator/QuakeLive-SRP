# Botlib Entity State Layout Reconstruction - 2026-06-05

## Scope

This pass focused on the botlib entity update and entity-info ABI shared by qagame and the retail Quake Live engine. The old Quake III source structs were still sized for the `0x70` `bot_entitystate_t` producer payload and the `0x8c` `aas_entityinfo_t` consumer payload. Retail Quake Live carries a larger tail through the same path.

## Retail evidence

- Owning engine binary: `quakelive_steam.exe`.
- Owning qagame producer: `qagamex86.dll`.
- Ghidra `qagamex86` `FUN_10023400` (`BotAIStartFrame`) zeroes a local `bot_entitystate_t` with `memset(&iStack_e0,0,0xd0)` before calling the botlib update import at vtable offset `0xe0`.
- Ghidra `quakelive_steam` `AAS_UpdateEntity @ 0x00484E20` indexes `aasworld.entities` with `entnum * 0xf4`, matching a `0xec` entity-info slab plus two 32-bit link pointers in the retail 32-bit build.
- HLIL for `AAS_UpdateEntity` copies the Quake Live tail in three groups:
  - producer words `0x1c..0x21` to info words `0x23..0x28`
  - producer words `0x22..0x31` to info words `0x29..0x38`
  - producer words `0x32..0x33` to info words `0x39..0x3a`
- Retail `AAS_EntityInfo` zeroes and copies `0xec` bytes and uses the same `entnum * 0xf4` stride.
- qagame `BotAIStartFrame` fills the expanded tail from a `gentity_t::r.linked`-based cursor:
  - local `+0x88` / producer word `0x1c` receives `(float)(ent->s.time / 1000)`.
  - local `+0x8c..0x94` / words `0x1d..0x1f` receive `client->ps.gravity`, `client->ps.speed`, and `client->ps.delta_angles[0]`.
  - local `+0x98` / word `0x20` receives `gentity_t.health`.
  - local `+0x9c` / word `0x21` receives retail `playerState_t +0xdc`, cross-checked against item-grab and health-bar paths as `STAT_MAX_HEALTH`.
  - local `+0xa0..0xdc` / words `0x22..0x31` are a 16-entry active-powerup vector.
  - local `+0xe0` / word `0x32` receives `!(gentity_t.flags & 0x00040000)`,
    now source-named as `FL_BOTLIB_ENTITY_STATE_BIT18`.
  - local `+0xe4` / word `0x33` receives a red/blue carried-flag sidecar derived from retail playerstate offsets `+0x144` and `+0x148`.

## Source reconstruction

- `bot_entitystate_t` in `src/code/game/botlib.h` now carries the Quake Live tail, making the source-side payload layout `0xd0` bytes in the retail 32-bit ABI.
- `aas_entityinfo_t` in `src/code/game/be_aas.h` now carries the matching tail, making the info layout `0xec` bytes in the retail 32-bit ABI.
- `AAS_UpdateEntity` now transfers the tail into `aasworld.entities[entnum].i` before setting the entity number and valid bit, matching the retail copy order before relink handling.
- `BotAIStartFrame` now fills the mapped tail fields recovered from qagame: entity time seconds, the three player movement fields, entity health, client max health, the active-powerup vector, the retail `gentity_t.flags` bit-18 boolean, and the red/blue carried-flag boolean.
- Follow-up 2026-06-12: the bit-18 producer mask is now named
  `FL_BOTLIB_ENTITY_STATE_BIT18` in `g_local.h`, and the source producer uses
  that flag instead of a private raw mask.
- Follow-up 2026-06-12: the active-powerup vector now mirrors the retail
  producer loop shape more closely. `BotAIStartFrame` writes all 16
  `BOTLIB_QL_POWERUP_ACTIVE_COUNT` slots and treats a timer as active when it
  is not earlier than the source-side threshold or is the permanent
  `INT_MAX` timer, with no extra source-only `powerupTime != 0` guard. Retail
  compares the timer values with a stride-`0x30` table rooted at
  `DAT_1008ff18`; the source expression keeps the existing `level.time`
  threshold mapping while leaving the raw table identity documented for future
  refinement.

## Open questions

The exact identity of the `DAT_1008ff18..DAT_10090218` table remains open. Multiple qagame paths use it for item/powerup timer comparisons and grants, so it is likely tied to retail item/powerup metadata, but this pass avoided inventing a source table until the owner is fully named.

Closed 2026-06-12: the `gentity_t.flags & 0x00040000` bit is now source-named
as `FL_BOTLIB_ENTITY_STATE_BIT18`. The producer-side boolean remains
`qlFlagsBit18Clear` because the retail ABI exports the inverted flag state
rather than the raw flag itself.

## Verification

`tests/test_botlib_internal_parity.py::test_botlib_ql_entity_state_tail_matches_retail_layout_references` checks the source fields and copy path against the committed qagame Ghidra output, the `quakelive_steam` Ghidra output, and the Binary Ninja HLIL split around `AAS_UpdateEntity`.
