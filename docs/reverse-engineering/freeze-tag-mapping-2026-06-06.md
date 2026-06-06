# Freeze Tag Mapping Round - 2026-06-06

## Scope

This round focused on `qagamex86.dll` Freeze Tag wiring around frozen-client
state, ally thaw progression, helper retention, and the adjacent cvar/event
surface. The main source targets were `g_freeze.c`, `g_client.c`,
`g_local.h`, `g_main.c`, and the lightweight match-simulation harness.

## Evidence Reviewed

- Canonical HLIL: `references/hlil/quakelive/qagamex86.dll/`
- Companion Ghidra corpus:
  `references/reverse-engineering/ghidra/qagamex86/metadata.txt`,
  `functions.csv`, `analysis_symbols.txt`, and `decompile_top_functions.c`
- Existing symbol map and mapping notes:
  `references/symbol-maps/qagame.json`,
  `docs/reverse-engineering/qagame-mapping.md`

The focused Ghidra rows pin the retail function band used here:

| Retail address | Ghidra row | Recovered name | Notes |
| --- | --- | --- | --- |
| `0x1004BC80` | `FUN_1004bc80,1004bc80,339` | `G_FreezeSetClientFrozenState` | Shared frozen/thawed mutator. |
| `0x1004CD00` | `FUN_1004cd00,1004cd00,57` | `G_FreezeFindThawHelperByClientNum` | Retained-helper lookup. |
| `0x1004CD40` | `FUN_1004cd40,1004cd40,1327` | `G_FreezeClientEndFrame` | Per-frame thaw/auto-thaw owner. |
| `0x10053020` | symbol-map row | `G_FreezeCanSeeThawProgressEvent` | Native visibility filter for thaw-progress event `0x58`. |

## Observed Retail Facts

`FUN_1004CD40` treats the client field equivalent to `gclient + 500` as
remaining thaw time, not accumulated thaw progress. A valid nearby helper
decrements that field by the frame delta parameter. A frame with no helper
increments it by the same delta and caps it back to the configured
`g_freezeThawTime` value.

The adjacent client fields at the retail `+0x1f8` / `+0x1fc` positions act as a
helper-active latch and retained helper client number. Once a helper has been
selected, retail calls the small `FUN_1004CD00` lookup to keep awarding and
validating that helper while the helper remains a legal same-team thaw source.

`g_freezeThawTick` is not the thaw-progress amount in the recovered retail
path. The value is read as the non-zero gate for the `FUN_1006C490(0x58)`
thaw-progress temp entity emitted when the whole-second remaining time changes.

Retail death/freeze state writes the synthetic frozen-player marker through
`client + 0x17c = 0x7fffffff` and `gentity + 0xc4 = 0x8000`, matching
`ps.powerups[PW_NUM_POWERUPS]` and the entitystate bit consumed by cgame. The
`arg2 == 1` branch of `FUN_1004BC80` clears those same fields before the
respawn-style thaw path continues.

At the top of `FUN_1004CD40`, retail also converts the remaining thaw time into
low `playerState_t::eFlags` buckets before helper search or timer mutation:
above two thirds of `g_freezeThawTime` clears bits `0x1|0x2`, between one third
and two thirds ORs bit `0x1`, and at or below one third ORs bit `0x2`. In the
shared source constants these bits are `EF_DEAD` and `EF_TICKING`; the
reconstruction keeps that odd low-bit reuse scoped to frozen clients.

Retail helper completion credits the helper through score/assist state, sets
the assist award flag/reward timer, and sends the `"ASSIST"` medal token from
the thaw path.

Retail assisted-thaw completion also emits an `EV_OBITUARY` temp entity with
`MOD_THAW`, the thawed client as `otherEntityNum`, the helper as
`otherEntityNum2`, and `SVF_BROADCAST`. It then emits an `EV_GLOBAL_TEAM_SOUND`
payload using `GTS_RED_RETURN` for blue-team clients and `GTS_BLUE_RETURN`
otherwise before falling into the Freeze-specific thaw visual path.

Retail thaw completion and round-state cleanup converge on a respawn tail:
`EV_THAW_PLAYER`, `PM_NORMAL`, then `ClientSpawn`. The round-state controller
shows this sequence directly for winning-team thaw, while assisted thaw reaches
the same tail by calling `FUN_10046d80` / `GibEntity` after the helper reward
and event surface.

The winning-team thaw lane is source-distinct from assisted thaw. Retail emits
the thaw visual and respawns from `Freeze_RoundStateTransition` directly, with
no helper obituary, assist medal, or `GibEntity` prelude.

## Source Reconstruction

- Replaced the old `freezeAccumulatedThaw` / `freezeNextThawTick` source model
  with `freezeThawTimeRemaining` and `freezeThawHelperActive`.
- Seeded the remaining thaw budget from `level.freezeConfig.thawTime` when a
  client freezes, and clear it when the client thaws.
- Reworked `G_FreezeClientEndFrame` to use `level.msec` as the progress delta,
  retain a valid helper through `G_FreezeFindThawHelperByClientNum`, decrement
  remaining time while helped, refill it when abandoned, and emit
  `EV_THAW_TICK` only when `g_freezeThawTick` is non-zero.
- Added `G_FreezeUpdateThawProgressFlags` to reproduce the retail
  `EF_DEAD`/`EF_TICKING` thaw-progress buckets and clear the reused low bits on
  Freeze state transitions.
- Centralized thaw-helper validity in `G_FreezeClientCanHelpThaw`, preserving
  same-team, connected, unfrozen, `PM_NORMAL`, radius, and line-of-sight gates.
- Follow-up mapping in
  `docs/reverse-engineering/freeze-tag-helper-query-mapping-2026-06-06.md`
  replaced the temporary client-slot thaw-helper scan with the retail
  `trap_EntitiesInBox` entity-query topology.
- Follow-up mapping in
  `docs/reverse-engineering/freeze-tag-frozen-marker-mapping-2026-06-06.md`
  added the qagame frozen-marker producer: freeze entry sets
  `ps.powerups[PW_NUM_POWERUPS] = INT_MAX` plus the matching entitystate
  powerup bit, and init/thaw clear both surfaces for the cgame frozen-player
  sprite/model/team-overlay readers.
- Follow-up mapping in
  `docs/reverse-engineering/freeze-tag-thaw-obituary-sound-mapping-2026-06-06.md`
  added the assisted-thaw obituary and global-team-sound publisher, and restored
  the matching `CG_Obituary` `MOD_THAW` text for auto, local-helper, and
  remote-helper thaw messages.
- Follow-up mapping in
  `docs/reverse-engineering/freeze-tag-thaw-respawn-tail-mapping-2026-06-06.md`
  moved the normal thaw visual through the retail frozen-marker branch in
  `GibEntity`, emits `EV_THAW_PLAYER` there, restores `PM_NORMAL`, and calls
  `ClientSpawn`.
- Follow-up mapping in
  `docs/reverse-engineering/freeze-tag-winning-thaw-respawn-mapping-2026-06-06.md`
  split configured winning-team thaw into a direct round-controller helper,
  `G_FreezeRespawnThawedWinner`, so that path emits `EV_THAW_PLAYER`, restores
  `PM_NORMAL`, and calls `ClientSpawn` without routing through assisted thaw.
- Removed timeout shifting for the obsolete thaw tick deadline field, since the
  replacement helper-active latch is not an absolute time.
- Updated the match-simulation harness to model Freeze assist-thaw as a
  remaining-time countdown/refill surface rather than an accumulated tick
  counter.

## Confidence And Open Questions

Confidence is high for the remaining-time counter, helper retention, tick-event
gate, low-bit thaw-progress buckets, frozen-player marker, assisted-thaw
`MOD_THAW` obituary/global-team-sound layer, assist medal token, and
`EV_THAW_PLAYER` respawn tails because those are visible in the committed
Ghidra decompile, HLIL string/event references, and symbol map.

Confidence is now high for the source-level helper-search structure after the
follow-up entity-query pass. Retail enumerates candidates through an
`EntitiesInBox` import before applying the client/team/radius/trace gates, and
the reconstructed source now mirrors that topology directly.

No runtime launch was needed for this round; the changes were justified by the
committed static reference corpus and covered with source/reference tests.

Open follow-up: audit whether thaw respawn carries any extra retail
Freeze-specific spawn protection or loadout preservation beyond the normal
`ClientSpawn` path.
