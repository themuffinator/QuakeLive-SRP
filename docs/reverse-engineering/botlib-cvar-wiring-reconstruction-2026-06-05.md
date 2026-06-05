# Botlib Cvar Wiring Reconstruction - 2026-06-05

## Scope

This pass reconstructs a focused retail `SV_BotInitCvars` tranche and one matching qagame-side bot control default. The affected cvars are part of the botlib/server/game wiring rather than botlib internals, but they directly control whether botlib starts and which travel flags bots use.

## Evidence

Canonical Binary Ninja HLIL for `SV_BotInitCvars` (`sub_4dd6f0`) in `quakelive_steam.exe_hlil_part04.txt`:

- `0x004dd6fc`: `bot_enable`, default `1`, flags `0x40`.
- `0x004dd7d7`: `bot_thinktime`, default `100`, flags `0`.
- `0x004dd890`: `bot_grapple`, default `1`, flags `0`.

Structured Ghidra companion evidence in `src2/ghidra/quakelive_steam/quakelive_steam_decomp.cpp` agrees:

- `Cvar_Get("bot_enable", &DAT_00551624, 0x40);`
- `Cvar_Get("bot_thinktime", &DAT_0052f690, 0);`
- `Cvar_Get("bot_grapple", &DAT_00551624, 0);`

The source cvar constants identify `0x40` as `CVAR_ROM`. Retail also keeps the later `SV_InitGameProgs` `Cvar_Get("bot_enable", "1", 0)`/source `CVAR_LATCH` read as a separate owner; source `Cvar_Get` ORs flags on existing variables, so retaining the later latch read preserves that two-stage ownership.

Qagame companion evidence in `references/reverse-engineering/ghidra/qagamex86/decompile_top_functions.c` shows the deathmatch AI setup registering `bot_grapple` with the same `1` default string:

- `(&DAT_105e4280,"bot_grapple",&DAT_1007d1d8,0);`

## Reconstruction

- Changed `SV_BotInitCvars` to register `bot_enable` as `CVAR_ROM`.
- Changed `SV_BotInitCvars` to register `bot_thinktime` without `CVAR_CHEAT`.
- Changed `SV_BotInitCvars` to default `bot_grapple` to `1`.
- Changed qagame deathmatch AI setup to default `bot_grapple` to `1`, matching the server-side retail default and the qagame Ghidra call.

## Follow-up Resolution

A later qagame HLIL-backed pass resolved the earlier `BotAISetup` open question: retail registers qagame `bot_thinktime` with flags `0`, matching the engine precreation call. See `docs/reverse-engineering/botlib-qagame-cvar-reconstruction-2026-06-05.md` for the VM-side reconstruction and BotAIStartFrame bridge mapping.

## Confidence

High for the server cvar registration changes and high for the qagame `bot_grapple` default. The qagame `bot_thinktime` registration has since been upgraded to high confidence by the fuller qagame HLIL slice.
