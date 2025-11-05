# Gameplay Loop Validation Notes

## Frame Loop
- **Entry point:** `G_RunFrame` at `0x0010A740` matches Quake Live behavior where the server advances world time, updates thinkers, and finalizes clients each frame.
- **Delta clamp:** Negative `msec` protection mirrors live server logic when processing demo rewinds, preventing timer underflow.
- **Timer handling:** Warmup and intermission transitions follow the same checks observed in the retail binary, ensuring start/stop events trigger once per threshold.

## Entity Think Pipeline
- **Linked-list traversal:** The VM uses the active-entity linked list instead of iterating the array to reduce cache churn; this ordering reproduces live server entity priority (doors and movers before items/clients).
- **Pre/post hooks:** Validation runs on the retail client confirm that mover activation, event flushing, and client post-thinks occur before the next entity tick, matching our reconstructed `G_PreThink`/`G_PostThink` split.
- **Think scheduling:** The `nextthink <= level.time` comparison, combined with zeroing `nextthink`, aligns with how Quake Live avoids double-firing thinks when frame rates hitch.

## Spawn Logic
- **Spawn table dispatch:** Hash-based lookup of `classname` corresponds to the observed constant-time spawn dispatcher in the shipping VM, ensuring entity-specific spawn functions are selected identically.
- **Immediate think execution:** Entities that schedule `nextthink` for the current frame (e.g., target_delay) execute immediately post-spawn in Quake Live; the reconstruction preserves this to match trigger timing.
- **Team linking and bot activation:** The order of `G_AddToTeam`, `trap_LinkEntity`, and optional bot initialization reproduces the sequence required for team doors and bot navmesh seeding seen in production builds.
