# Freeze Tag round controller notes

## g_roundWarmupDelay

`g_roundWarmupDelay` defines how long the server waits between kicking off the
round warmup countdown and letting players move. Each time the Freeze Tag state
machine transitions into warmup the game calls `G_FreezePrepareClientsForWarmup`
and then schedules the active round with `level.roundTransitionTime = level.time
+ g_roundWarmupDelay`. Once the timer expires `G_FreezeStartRound` is invoked and
everyone regains control. This is handled inside `G_Frame_BeginRoundWarmup` and
`G_Frame_UpdateRoundController`. To exercise the behaviour in a local build,
set `g_roundWarmupDelay 5000`, start a Freeze Tag match, and watch the warmup
countdown hold players in place for five seconds before the round begins.

## g_freezeResetWeaponsOnRound

During warmup the server walks every connected client and decides whether to
respawn them via `G_RequestClientSpawn` or simply reset their inventory in
place. When `g_freezeResetWeaponsOnRound` is non-zero the respawn path is used,
so everyone gets a fresh loadout and spawn location at the top of the round. If
it is zero the players stay put and the server optionally restores health,
armor, and persistent powerups according to the other `g_freezeReset*`
toggles. This logic lives inside `G_FreezePrepareClientsForWarmup`. To verify
it manually you can start a Freeze Tag server, set `g_freezeResetWeaponsOnRound
0`, lower your health, and note that the next round leaves you in place with
your accumulated weapons.

## g_freezeProtectedSpawnTime

Every time a player respawns or gets thawed the game calls
`G_FreezeClientRespawned` to clear the Freeze Tag timers and, when the cvar is
non-zero, set `client->freezeProtectedUntil = level.time +
g_freezeProtectedSpawnTime`. `G_FreezeDamageProtected` runs at the top of
`G_Damage` and prevents any incoming damage while that timestamp is still in the
future. A simple regression test is to set `g_freezeProtectedSpawnTime 3000`,
thaw a teammate, and observe that they cannot be damaged for the next three
seconds.
