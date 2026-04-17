# clientSession_t layout

## Source-canonical layout

The reconstructed source `clientSession_t` is a `0x44`-byte record. This pass
promotes that source member order directly in `src/game/ql_game_types.h` so the
retail drift can be described against a stable baseline instead of a stale flat
guess inside `gclient_t`.

| Source offset | Field | Notes |
| ------ | ----- | ----- |
| `0x00` | `sessionTeam` | Persistent team / spectator assignment. |
| `0x04` | `spectatorTime` | Queue timestamp used to decide next-in-line spectators. |
| `0x08` | `spectatorState` | Follow / free / scoreboard spectator mode. |
| `0x0C` | `spectatorClient` | Follow target client number. |
| `0x10` | `selectedSpawnWeapon` | Persisted starting-weapon / loadout selection. |
| `0x14` | `wins` | Tournament wins. |
| `0x18` | `losses` | Tournament losses. |
| `0x1C` | `teamLeader` | Team-leader latch. |
| `0x20` | `privilege` | Admin privilege tier. |
| `0x24` | `spectateOnly` | Duel spectator-only latch. |
| `0x28` | `spectatorQueuePosition` | Duel queue position. |
| `0x2C` | `spectatorQueuePositionDirty` | Live queue-dirty latch skipped by the serializer. |
| `0x30` | `muted` | Persistent mute latch. |
| `0x34` | `sessionReservedTail` | Compatibility-only serializer tail preserved in the reconstructed source. |
| `0x38` | `skill1` | Auxiliary progression / rating slot. |
| `0x3C` | `skill2` | Auxiliary progression / rating slot. |
| `0x40` | `skill3` | Auxiliary progression / rating slot. |

## Retail Quake Live drift

Retail qagame still keeps a contiguous session-style block at `gclient + 0x348`,
but the serializer and live callsites show that Quake Live has repurposed
multiple members.

- `sub_10065880` and `sub_10065930` serialize `0x348`, `0x34C`, `0x350`,
  `0x354`, `0x358`, `0x35C`, `0x360`, `0x364`, `0x368`, `0x36C`, `0x370`,
  `0x378`, and `0x37C`, while explicitly skipping `0x374`.
- `ClientSpawn` loadout helpers (`0x1003B2A0` / `0x1003B5A0`) treat `0x358` as a
  persisted starting-weapon selection. That slot is not the tournament wins
  counter in retail.
- `AdjustTournamentScores` increments the winner at `0x35C` and the loser at
  `0x360`, proving the retail wins/losses pair moved down by one dword.
- The team-leader helpers around `0x10068310-0x10068468` clear and set `0x364`,
  so that slot is the live `teamLeader` latch rather than a surviving
  `sessionState`.
- `G_InitSessionData`, `ClientConnect`, and the admin command path seed
  `0x368` from `sub_10032460()` and broadcast it with `priv %i`, so the
  privilege slot is still present.
- `SetTeam` and `G_UpdateTournamentQueuePositions` use `0x36C` / `0x370` as the
  Quake Live `so` / `pq` spectator queue fields.
- The mute / unmute helpers toggle `0x378`, proving retail moved the persistent
  mute latch into the former tail of the source block.

The net result is a retail overlay with one inserted loadout field, the queue
dirty bit occupying the skipped serializer slot, and a compatibility-only tail
that remains preserved but behaviorally inert in the committed evidence set.

## Evidence-backed retail overlay

The retail `clientSession_t` overlay in `ql_game_types.h` is modeled relative
to `gclient->sess`.

| Retail offset | gclient offset | Field | Confidence | Evidence |
| ------ | ----- | ----- | ---------- | -------- |
| `0x00` | `0x348` | `sessionTeam` | High | `G_InitSessionData`, `G_ReadSessionData`, and `SetTeam` all read and write this as the persistent team slot. |
| `0x04` | `0x34C` | `spectatorTime` | High | The session helpers serialize it and the spectator-queue sorter uses it as the ordering timestamp. |
| `0x08` | `0x350` | `spectatorState` | High | Session init and `SetTeam` assign the classic free/follow/scoreboard spectator values here. |
| `0x0C` | `0x354` | `spectatorClient` | High | Read and written by the session helpers and follow-mode transitions. |
| `0x10` | `0x358` | `selected_spawn_weapon` | Medium | The retail loadout/spawn helpers validate this as a weapon id and copy it into the live player weapon slot when it is allowed. |
| `0x14` | `0x35C` | `wins` | High | `AdjustTournamentScores` increments this slot for the winning client. |
| `0x18` | `0x360` | `losses` | High | `AdjustTournamentScores` increments this slot for the losing client. |
| `0x1C` | `0x364` | `teamLeader` | High | The team-leader helpers clear/set this slot for clients on the chosen team and republish userinfo afterwards. |
| `0x20` | `0x368` | `privilege` | High | Retail seeds it from `sub_10032460()` and sends it back to the client with `priv %i`. |
| `0x24` | `0x36C` | `spectate_only` | High | `SetTeam` sets this when the player is forced to remain spectator-only and clears it when queue logic re-admits the client. |
| `0x28` | `0x370` | `spectator_queue_position` | High | `G_UpdateTournamentQueuePositions` assigns one-based queue positions here and the queue sync helper republishes changes. |
| `0x2C` | `0x374` | `spectator_queue_position_dirty` | High | Queue update/sync helpers set and clear this live dirty bit, and the retail session serializer skips it. |
| `0x30` | `0x378` | `muted` | High | The admin mute / unmute helpers flip this slot directly and the session serializer persists it. |
| `0x34` | `0x37C` | `reserved_tail` | Medium | `sub_10065880`, `sub_10065930`, and the all-clients save loop only serialize or restore this dword. No committed HLIL/Ghidra callsite currently consumes it as gameplay state, so the safest promotion is a reserved compatibility tail rather than a feature name. |

## Open questions

- `selected_spawn_weapon` is descriptive rather than source-backed. The
  loadout/spawn behavior is clear, but the exact retail naming used by id
  Software is still open.
- No committed retail evidence currently promotes `reserved_tail` beyond a
  serializer-only compatibility slot. If new HLIL evidence surfaces, revisit
  the name before attaching gameplay meaning to it.
- No committed HLIL evidence still supports a distinct retail `sessionState`
  inside `gclient->sess`; if that concept survives, it has moved elsewhere.
