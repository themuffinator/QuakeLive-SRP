# Botlib bot_showPath Runtime Reconstruction - 2026-06-05

## Scope

This pass reconstructs the Quake Live retail `bot_showPath` botlib runtime path. The original GPL source only exposed the movement reachability visualization through the compile-time `DEBUG_AI_MOVE` block in `be_ai_move.c`; retail keeps a cached libvar value and gates a live visualization block from `BotMoveToGoal`.

## Evidence

Canonical Binary Ninja HLIL:

- `AAS_StartFrame` caches `bot_showPath` each frame at `0x004863bb`:
  `data_16dd7ec = sub_526000(sub_4a8680("bot_showPath"))`.
- `Export_BotLibSetup` seeds the same cache at `0x004a7d03`, immediately after `bot_developer`.
- `BotMoveToGoal` checks `data_16dd7ec` at `0x004a573e`, then calls the retail debug-line helper `sub_4844e0()` and direct arrow helper `sub_484a80()` before copying the current origin into the previous-origin slots.

Structured Ghidra companion evidence:

- `src2/ghidra/quakelive_steam/quakelive_steam_decomp.cpp` shows `FUN_004a8680("bot_showPath"); DAT_016dd7ec = FUN_00526000();` in the setup/frame path.
- The same decompile shows `if (DAT_016dd7ec != 0)` in `BotMoveToGoal`, followed by:
  - `AAS_ReachabilityFromNum(pfVar1[0x13], local_ac);`
  - `FUN_004844e0(pfVar1, pfVar1 + 0x14, 4);`
  - `FUN_00484a80(local_a0, local_94, 3, 4);`

Source correlation:

- `pfVar1[0x13]` maps to `bot_movestate_t.lastreachnum`.
- `pfVar1 + 0x14` maps to `bot_movestate_t.lastorigin`.
- `FUN_004844e0(..., 4)` matches `AAS_DebugLine(..., LINECOLOR_YELLOW)` with the source `LINECOLOR_*` constants.
- `FUN_00484a80(..., 3, 4)` matches `AAS_DrawArrow(..., LINECOLOR_BLUE, LINECOLOR_YELLOW)`, including the helper body's 6-unit arrowhead and three debug-line calls.

## Reconstruction

- Added the global `bot_showPath` cache next to `bot_developer` in `be_interface.c` and exported it through `be_interface.h`.
- Seeded `bot_showPath` during `Export_BotLibSetup`.
- Refreshed `bot_showPath` during `AAS_StartFrame` before `saveroutingcache`, matching the retail order.
- Added the `BotMoveToGoal` tail gate after the blocked-reachability timeout adjustment and before `VectorCopy(ms->origin, ms->lastorigin)`.
- Routed the tail through `AAS_DebugLine` and `AAS_DrawArrow` directly, matching the retail call shape and avoiding the heavier `AAS_ShowReachability` wrapper used elsewhere for full reachability visualization.
- Promoted `sub_4844E0 -> AAS_DebugLine` and `sub_484A80 -> AAS_DrawArrow` in `references/analysis/quakelive_symbol_aliases.json`.

## Confidence

High for ownership, placement, and cvar cache behavior. The HLIL and Ghidra corpora agree on setup, frame refresh, and end-of-move gating. The helper-name mapping is an inference from call shape, arguments, source constants, and existing AAS debug helper behavior, but it is strong because both helper functions are already represented by GPL-source equivalents.

## Open Questions

- `bot_showPath` is still forced to `0` by the game-side AI initialization/start-frame bridge, matching the current source wiring. This pass reconstructs the botlib side so future retail-accurate bridge work has a concrete target.
