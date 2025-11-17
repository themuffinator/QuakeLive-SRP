# Freeze Tag Gameplay Notes

Freeze Tag extends the round controller and client lifecycle so that deaths immobilize players until a teammate thaws them. The following cvars control the cadence that the new flow follows.

## `g_roundWarmupDelay`

`g_roundWarmupDelay` determines how long the server waits before transitioning from warmup to an active freeze round. `G_FreezeScheduleWarmupDelay` in `g_active.c` reads the cvar whenever warmup begins and publishes the new countdown via `CS_WARMUP`, so changing the delay updates both the server state machine and the HUD clock immediately.【F:src/code/game/g_active.c†L1241-L1267】

## `g_freezeResetWeaponsOnRound`

When `g_freezeResetWeaponsOnRound` is non-zero the round controller respawns every player with the factory loadout at the start of a round. `G_FreezeResetClientsForRound` calls `G_RequestClientSpawn` for each client so their inventory, ammo, and factory tweaks are reapplied even if the player never left the map between rounds.【F:src/code/game/g_active.c†L1276-L1314】

## `g_freezeProtectedSpawnTime`

`g_freezeProtectedSpawnTime` adds a temporary shield to players who just spawned or thawed. `G_FreezeInitClient` and `G_FreezeThawClient` stamp the protection expiry time on the client, and `G_Damage` suppresses incoming damage from other players while the flag is active. The timer automatically clears in `G_FreezeClientEndFrame`, so protection ends cleanly even if nobody attacks.【F:src/code/game/g_client.c†L31-L216】【F:src/code/game/g_client.c†L1493-L1605】【F:src/code/game/g_combat.c†L1270-L1280】
