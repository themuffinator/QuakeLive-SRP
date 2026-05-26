# qagame client spawn reconstruction - 2026-05-26

## Scope

This pass maps the `qagamex86.dll` client-spawn band around the retail
`ClientBegin`, `G_SelectClientSpawnPoint`, ranked spawn selection,
spawn/loadout finalization, and `ClientSpawn` bootstrap boundary. The source
changes in this band focus on the retail no-spawn path, spawn route selection,
ranked-spawn candidate sizing, initial-spawn filtering, team begin fallback,
pre-existing `PM_SPECTATOR` spectator-spawn selection, and the recovered
ranked-spawn spawnflag filter that were still missing from the GPL-shaped
`ClientSpawn` flow.

## Evidence

- Canonical binary: `assets/quakelive/qagamex86.dll`.
- Canonical HLIL: `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt`.
- Companion decompile: `references/reverse-engineering/ghidra/qagamex86/decompile_top_functions.c`.
- Function index: `references/reverse-engineering/ghidra/qagamex86/functions.csv`.
- Curated names: `references/symbol-maps/qagame.json`.

The qagame corpus currently exposes `1027` function entries in
`functions.csv`, with `180` decompiled bodies in the committed Ghidra top
function slice.

## Function Map

| Retail address | Recovered name | Current source owner | Status |
| --- | --- | --- | --- |
| `0x10038B60` | `Team_SelectDominationSpawnPoint` | `src/code/game/g_team.c` | Domination point-linked spawn candidate collection and ranked selection are reconstructed. |
| `0x10039080` | `G_SelectRankedSpawnPoint` | `src/code/game/g_client.c`, `src/code/game/g_team.c` | Spawn classname selection, spawnflags bit-2 exclusion, initial-only bit-1 admission, telefrag filtering, Chebyshev distance ranking, the 26-entry ranked candidate window, `g_spawnRandomRatio`, and `g_spawnMinDistance` are represented by the shared ranked picker. |
| `0x10039730` | `G_SelectClientSpawnPoint` | `src/code/game/g_client.c` | ClientSpawn-side wrapper now owns the gametype route into spectator, Domination, team, initial, and neutral spawn paths, including the recovered team-spawn gametype band and same-team begin fallback. |
| `0x1003B030` | `ClientBegin` | `src/code/game/g_client.c` | Post-connect begin flow aligns with the retail `ClientBegin: %i` boundary and spawn bootstrap handoff. |
| `0x1003B5A0` | `G_FinalizeSpawnLoadout` | `src/code/game/g_client.c` | Selected spawn weapon, factory weapon/ammo seed, configured grant tail, and Red Rover infected override are split out of `ClientSpawn`. |
| `0x1003B6C0` | `G_InitClientSpawnState` | `src/code/game/g_client.c` | Reconstructed source helper runs Red Rover finalization, conditional spawn target usage, and loadout finalization. |
| `0x1003BB90` | `G_GiveItemByName` | `src/code/game/g_client.c` | Configured item grant helper is represented through the source grant-token path. |
| `0x1003BC30` | `ClientSpawn` | `src/code/game/g_client.c` | Main spawn bootstrap is source-faithful on persistent-state preservation, pre-existing `PM_SPECTATOR` spectator-spawn selection, profile pmove flags, entity relink, post-spawn frame finalization, and now the no-spawn retry path. |
| `0x10035960` | `G_CAADRespawnAsSpectator` | `src/code/game/g_team.c` | The CA/A-D elimination helper depends on the `ClientSpawn` pre-existing `PM_SPECTATOR` path: it copies the corpse, writes spectator pm_type, reruns `ClientSpawn`, counts active teams, and only calls `FollowCycle` when both teams still have players. |

## Observed Retail Facts

- Active players call `G_SelectClientSpawnPoint` before the large client reset.
  Spectators instead copy the intermission origin/angles and continue with a
  null spawn entity.
- If the active-player spawn wrapper returns null, retail sets
  `client->respawnTime = level.time + 600`, writes `PM_SPECTATOR` into the
  playerstate, increments the adjacent retry counter, and returns before
  preserving/resetting the rest of `gclient_t`.
- On a successful active-player spawn selection, retail clears the retry
  counter before the normal spawn bootstrap proceeds.
- The team spawn-class route is gated by the recovered `gametype - 4 <= 7`
  band. With the current source enum, that includes Clan Arena through Attack
  and Defend, and excludes the later Red Rover slot.
- The ranked spawn picker clamps the retained ranked candidate window to
  `0x1a` entries after applying the random-ratio calculation; the source now
  uses the same 26-entry cap instead of the older 32-entry local constant.
- Before distance scoring, the normal ranked path rejects candidate entities
  whose `spawnflags` have bit 2 set. Binary Ninja shows the byte read at
  `entity + 0x248` and the `(flags & 2) == 0` guard at `0x10039233`, and the
  Ghidra companion body shows the same `0x248`/bit-2 test before the candidate
  count and ranked insertion work.
- For neutral initial spawns, the same ranked helper requires bit 1 when the
  caller passes the initial mode without a team spawn class. HLIL expresses
  this as `arg7 != 0 || arg6 == 0 || (flags & 1) != 0`, which means normal
  neutral respawns admit any non-bit-2 deathmatch spawn, while initial neutral
  selection admits only bit-1 starts.
- If a team `TEAM_BEGIN` class such as `team_CTF_redplayer` produces no ranked
  candidate, `G_SelectRankedSpawnPoint` clears the begin-mode argument and
  retries the same team class family as `team_CTF_redspawn` /
  `team_CTF_bluespawn` before `G_SelectClientSpawnPoint` falls through to its
  neutral fallback path.
- `ClientSpawn` preserves persistent/session state across a full client clear,
  increments `PERS_SPAWN_COUNT`, mirrors `PERS_TEAM`, and seeds the recovered
  movement profile bits from the active physics profile globals.
- A pre-existing `PM_SPECTATOR` playerstate entering `ClientSpawn` selects the
  spectator spawn path even when `sess.sessionTeam` still belongs to an active
  team. This is the mechanism used by `G_CAADRespawnAsSpectator @ 0x10035960`.
- The final spawn lane runs through the recovered Red Rover/loadout helper
  split before pulling the first usercmd, setting the view angles, linking, and
  running `ClientThink` / `ClientEndFrame`.

## Source Reconstruction

- Added `CLIENT_SPAWN_RETRY_DELAY` with the retail `600` ms constant.
- Added `gclient_t::noSpawnRetryCount` for the retry counter observed beside
  `respawnTime` in the retail client block.
- Added `G_DeferClientSpawnRetry`, which parks the player in `PM_SPECTATOR`,
  sets the retry deadline, increments the retry counter, and schedules a local
  think callback to retry `ClientSpawn`.
- Added `G_RetryDeferredClientSpawn`, guarded by connection/team state so team
  changes and disconnects do not resurrect a stale pending spawn.
- Replaced the old unbounded `do { ... } while ( 1 )` spawnpoint eligibility
  loop with a bounded `G_ClientCanUseSpawnPoint` retry plus the retail-style
  defer-and-return path. This preserves the `FL_NO_BOTS` / `FL_NO_HUMANS` gate
  without risking a null dereference or infinite retry inside one frame.
- Added `G_GametypeUsesTeamSpawnSelection` so the source wrapper mirrors the
  retail team-spawn gametype band directly: Clan Arena now uses the
  `team_CTF_redspawn` / `team_CTF_bluespawn` family, while Red Rover falls back
  to the neutral spawn path before its role/loadout finalizer runs.
- Corrected `MAX_RANKED_SPAWN_POINTS` from 32 to 26 to match the `0x1a`
  retained-candidate cap visible in `G_SelectRankedSpawnPoint`.
- Added `RANKED_SPAWN_EXCLUDE_FLAG` and `G_RankedSpawnPointAllowed` so the
  shared ranked picker now skips spawn entities with the recovered bit-2
  spawnflag before both the distance-ranking path and its no-ranked-candidate
  fallback.
- Added `RANKED_SPAWN_INITIAL_FLAG`, `G_RankedSpawnPointAllowedForMode`, and
  `G_SelectInitialRankedSpawnPoint` so `SelectInitialSpawnPoint` ranks all
  eligible initial deathmatch starts instead of taking the first bit-1 entity
  found by `G_Find`.
- Extended `SelectCTFSpawnPoint` so failed `TEAM_BEGIN` player-start selection
  retries the same team's regular spawn classname before falling back to the
  neutral deathmatch path.
- Added a `spawnAsSpectator` selector so `ClientSpawn` preserves the retail
  pre-existing `PM_SPECTATOR` path used by CA/A-D round eliminations, including
  spectator placement, `PMF_FOLLOW` clearing, non-solid entity setup, and
  non-player relink/item-grant suppression.

## Confidence

High confidence for the `ClientSpawn` no-spawn state writes and timing constant:
the same assignments are visible in both HLIL and the Ghidra decompile around
`0x1003BC30`. High confidence for the ranked-spawn bit-2 exclusion, neutral
initial bit-1 admission, and team begin fallback because both HLIL and Ghidra
show these predicates inside `G_SelectRankedSpawnPoint @ 0x10039080`. Medium
confidence for the local think scheduling: the committed source tree needs a
source-side mechanism to revisit the deferred spawn, while the retail evidence
proves the state transition and retry counter but not a standalone helper
boundary with this exact name.

## Remaining Questions

- The exact retail owner that re-enters `ClientSpawn` after the 600 ms deferred
  state remains a follow-up mapping target. The reconstructed tree uses the
  existing entity think lane because `G_RunThink` is already frame-serviced for
  client slots.
- The current source still has GPL-shaped team spawn helpers in a few places
  where retail keeps more of the fallback matrix inside
  `G_SelectClientSpawnPoint`. Those paths should be rechecked when the next
  spawn-selection pass tackles team fallback modes and retry-count thresholds.
- The ranked helper has a training-map-specific direct spawnflag path that
  depends on the server-type/training globals and the randomized first
  argument. That path remains a follow-up because the stable non-training
  initial/team fallback matrix is now reconstructed, while the training lane
  needs a separate pass against the training-map bootstrap evidence.

## Parity Estimate

Scoped client-spawn parity moved from **96%** to **98%** with the no-spawn
retry reconstruction, to **98.5%** after restoring the retail team-spawn
gametype band, to **98.7%** after correcting the ranked candidate cap, and to
**98.8%** after restoring the ranked-spawn bit-2 spawnflag exclusion. The
initial ranked selection and team-begin fallback reconstruction move the scoped
client-spawn parity to **99.0%**. The repo-wide parity estimate remains
**98%** because these close narrow runtime edges inside an already mostly
reconstructed qagame subsystem.
