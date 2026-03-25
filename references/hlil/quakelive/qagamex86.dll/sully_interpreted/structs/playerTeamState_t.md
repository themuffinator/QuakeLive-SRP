# playerTeamState_t layout

## Source-canonical layout

The GPL `playerTeamState_t` itself is still a compact `0x30`-byte record. This
pass promotes the source member order directly in
`src/game/ql_game_types.h` so reconstruction work can refer to the original
shape without re-deriving it from `g_local.h` each time.

| Source offset | Field | Notes |
| ------ | ----- | ----- |
| `0x00` | `state` | `TEAM_BEGIN` / `TEAM_ACTIVE` in the GPL tree. |
| `0x04` | `location` | Team overlay location index. |
| `0x08` | `captures` | Flag captures. |
| `0x0C` | `basedefense` | Base-defense awards. |
| `0x10` | `carrierdefense` | Carrier-protect awards. |
| `0x14` | `flagrecovery` | Dropped-flag returns. |
| `0x18` | `fragcarrier` | Flag/skull-carrier frags. |
| `0x1C` | `assists` | Capture assists. |
| `0x20` | `lasthurtcarrier` | Source float timestamp used by the danger-protect timeout. |
| `0x24` | `lastreturnedflag` | Source float timestamp used by return-assist checks. |
| `0x28` | `flagsince` | Source float timestamp for how long the flag has been carried. |
| `0x2C` | `lastfraggedcarrier` | Source float timestamp used by frag-carrier assist checks. |

## Retail Quake Live drift

Retail qagame does not preserve `playerTeamState_t` as a clean contiguous
sub-struct inside `gclient_t`.

- A 32-bit source layout check puts `clientPersistant_t::teamState` at
  `clientPersistant_t + 0x58`, which would land at `gclient + 0x2A8` if the GPL
  layout still held end to end.
- Retail disproves that direct carryover. `gclient + 0x27C` is the stable
  `pers.netname` string, and the `ClientConnect` / `ClientSpawn` persistence
  copies show Quake Live has expanded the surrounding `pers` region.
- Retail still preserves the source `state` enum, but it now lives one dword
  earlier at `gclient + 0x2F8`.
- The evidence-backed teamplay counter/timer block lives at `gclient + 0x2FC`.

## Evidence-backed retail carryovers

The retail overlay at `gclient + 0x2FC` still preserves most of the classic
teamplay counters and timeout stamps, but several source fields have drifted or
been replaced by Quake Live-specific logic.

| Retail offset | Candidate field | Confidence | Evidence |
| ------ | ----- | ---------- | -------- |
| `0x2F8` | `state` | High | `ClientBegin` and `SetTeam` both reset this slot to `0` before spawn selection, matching source `TEAM_BEGIN`, and the retail `ClientSpawn` path later stores `1` after choosing the spawn point, matching source `TEAM_ACTIVE`.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41214-L41214】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L45260-L45260】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41820-L41820】 |
| `0x2FC` | `captures` | High | `Team_TouchOurFlag` increments this immediately after the capture print and team-score update.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L75835-L75843】 |
| `0x300` | `basedefense` | High | The base-flag defense branch in `Team_FragBonuses` increments this after the flag/PVS proximity test succeeds.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L75203-L75217】 |
| `0x304` | `carrierdefense` | High | The danger-protect and carrier-nearby branches increment this and then clear the victim-side hurt-carrier timer.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L75217-L75236】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L75305-L75305】 |
| `0x308` | `flagrecovery` | High | The dropped-flag return path prints `"returned the %s flag!"`, increments this slot, and stamps `0x320` with `level.time`.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L75754-L75759】 |
| `0x30C` | `fragcarrier` | High | The flag-carrier and skull-carrier frag branches stamp `0x324 = level.time` and increment this counter before printing the carrier-frag message.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L75243-L75245】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L75278-L75280】 |
| `0x310` | `assists` | High | The capture-assist loop increments this when a teammate has a recent return-flag or frag-carrier timestamp.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L75911-L75932】 |
| `0x314` | `field_18` | Medium | This slot feeds the retail held-time print in the capture path, is reset on flag pickup, and is also reused by non-CTF timer logic. It should not be forced to source `flagsince`.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L75779-L75779】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L76024-L76024】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L71158-L71169】 |
| `0x318` | `field_1c` | Low | This slot is paired with `0x314` in the retail pickup/capture path, but the exact Quake Live meaning is still open.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L75835-L75835】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L76024-L76024】 |
| `0x31C` | `lasthurtcarrier` | High | `Team_CheckHurtCarrier` stamps this with `level.time`, `Team_FragBonuses` checks it against the 8-second danger-protect timeout, and capture handling clears or poisons it with `-5`.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L75344-L75352】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L75043-L75043】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L75932-L75932】 |
| `0x320` | `lastreturnedflag` | High | The flag-return path stores `level.time` here, and the capture-assist loop checks `slot + 10000 > level.time`.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L75759-L75759】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L75911-L75916】 |
| `0x324` | `lastfraggedcarrier` | High | The carrier-frag path stores `level.time` here, and the capture-assist loop checks it as the alternate assist timeout source.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L75243-L75245】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L75927-L75932】 |
| `0x328` | `field_2c` | Low | The final dword before the inactivity block is still open. This pass only reserves it structurally in the retail overlay. |

## Open questions

- The source `location` member is still not pinned in the retail Quake Live
  binary.
- Retail `flagsince` remains unresolved. The tempting `0x314` candidate is
  reused by Quake Live hold/race timing paths and is not source-clean.
- The retail block at `0x2F8-0x32B` should be treated as an evidence-backed
  overlay, not a proof that Quake Live still stores the source struct at that
  exact offset.
