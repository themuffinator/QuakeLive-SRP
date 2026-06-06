# Freeze Tag Frozen Marker Mapping - 2026-06-06

## Scope

This note maps the retail Freeze Tag marker that tells cgame a player is
frozen. The focused source target is `src/code/game/g_freeze.c`, with consumer
checks in `src/code/cgame/cg_players.c` and `src/code/cgame/cg_draw.c`.

## Evidence

- Owning binary: `qagamex86.dll`.
- Canonical HLIL:
  `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt`.
- Companion Ghidra:
  `references/reverse-engineering/ghidra/qagamex86/functions.csv` and
  `decompile_top_functions.c`.
- Source consumers:
  `CG_IsFrozenPlayer`, `CG_PlayerSprites`, and the team overlay frozen bit.

## Observed Retail Facts

Retail death/freeze state writes `0x7fffffff` to the client field at
`client + 0x17c` and writes exactly `0x8000` to the entity powerup bitfield at
`gentity + 0xc4` while Freeze Tag is active. In the GPL-derived layout, those
slots line up with `ps.powerups[PW_NUM_POWERUPS]` and
`ent->s.powerups = ( 1 << PW_NUM_POWERUPS )`.

The shared Freeze mutator `FUN_1004BC80` clears the same marker when taking the
`arg2 == 1` thaw/respawn branch:

- `1004bcae`: `*(arg1[0x8f] + 0x17c) = 0`
- `1004bcb8`: `arg1[0x31] &= 0xffff7fff`

The opposite branch of `FUN_1004BC80` emits the thaw obituary and team sound
surface before gib/respawn wiring:

- `sub_1006c490(&arg1[0x88], 0x3a)` creates an `EV_OBITUARY` temp entity.
- The obituary `eventParm` is `0x1e`, matching `MOD_THAW`.
- The temp entity receives `0x20` at `+0x1e0`, matching the broadcast server
  flag.

That event split remains a larger reconstruction target. This pass only
reconstructs the marker producer required by already-mapped cgame consumers.

## Source Reconstruction

`G_FreezeSetClientFrozenPowerupMarker` now mirrors the retail marker through
both state surfaces:

- Frozen entry: `ent->client->ps.powerups[PW_NUM_POWERUPS] = INT_MAX` and
  `ent->s.powerups = ( 1 << PW_NUM_POWERUPS )`.
- Thawed/init path: clear `ps.powerups[PW_NUM_POWERUPS]` and clear
  `ent->s.powerups` bit `1 << PW_NUM_POWERUPS`.

`INT_MAX` matches the retail `0x7fffffff` sentinel and keeps the marker from
being expired by the normal powerup timeout pass. The explicit entitystate
assignment matches the retail immediate `0x8000` entity bitfield write and
avoids relying only on later `BG_PlayerStateToEntityState` propagation.

## Confidence And Open Questions

Confidence is high for the marker fields because the same high bit is consumed
in cgame through `cent->currentState.powerups & ( 1 << PW_NUM_POWERUPS )`, and
the qagame death/thaw writes match `PW_NUM_POWERUPS == 15` exactly.

Open follow-up: reconstruct the full `FUN_1004BC80` thaw branch split so
qagame emits the retail `EV_OBITUARY`/`MOD_THAW` and team-sound sequence before
the `EV_THAW_PLAYER`/respawn path.
