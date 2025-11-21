# Weapon balance parity captures (2024-09-22)

The demo captures listed below were generated after porting the Quake Live weapon constants to confirm refire pacing, ammo pickups, and splash behaviour. Binary demos are stored in the internal capture vault; use the filenames to retrieve them from the QA share.

- `weapon-balance-2024-09-22-rocket-lg.dm_91` – Duel scrim covering rocket splash falloff and lightning 50 ms refire during extended fights on `qzdm6`.
- `weapon-balance-2024-09-22-rail-ammo.dm_91` – Focused run on `qztourney7` showing railgun max stack/pickup deltas alongside respawn timing cues.
- `weapon-balance-2024-09-22-prox-chaingun.dm_91` – Team scrim validating proximity mine reload cycles and chaingun 50 ms spin-up cadence.

For review convenience, attach these demos to parity tickets or replay them with `cl_avidemo` logging enabled to cross-check damage ticks against `bg_pmove.c` and `bg_misc.c` defaults.
