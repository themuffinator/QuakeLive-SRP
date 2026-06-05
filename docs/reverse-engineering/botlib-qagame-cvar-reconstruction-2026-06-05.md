# Botlib Qagame Cvar Reconstruction - 2026-06-05

## Scope

This pass reconstructs a qagame-side bot control cvar flag tranche and maps the adjacent BotAI runtime bridge. The affected cvars are botlib-adjacent VM controls:

- `bot_thinktime`
- `bot_nochat`
- `bot_challenge`

Retail registers `bot_thinktime` as an unflagged qagame cvar, matching the engine-side `SV_BotInitCvars` precreation. Retail registers `bot_nochat` and `bot_challenge` as profile/cloud-style controls in `BotSetupDeathmatchAI`.

## Evidence

Canonical qagame Binary Ninja HLIL in `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt` shows `BotAISetup` (`sub_100241c0`) registering:

- `bot_log`, default `0`, flags `0`
- `bot_thinktime`, default `100`, flags `0`
- `bot_memorydump`, default `0`, flags `0x200`
- `bot_saveroutingcache`, default `0`, flags `0x200`

The same HLIL shows the `BotAIStartFrame` runtime bridge:

- When `bot_memorydump` is nonzero, set botlib `memorydump` to `1`, then reset `bot_memorydump` to `0`.
- When `bot_saveroutingcache` is nonzero, set botlib `saveroutingcache` to `1`, then reset `bot_saveroutingcache` to `0`.
- If `bot_thinktime` exceeds `200`, reset it to `200`.
- Set botlib `bot_showPath` to `0` each qagame bot frame.

Engine HLIL in `quakelive_steam.exe_hlil_part04.txt` agrees on the engine precreation side:

- `SV_BotInitCvars`: `bot_thinktime`, default `100`, flags `0`.

Structured qagame Ghidra companion evidence in `references/reverse-engineering/ghidra/qagamex86/decompile_top_functions.c` shows the `BotSetupDeathmatchAI` registration cluster:

- `(&DAT_105e3fa0,"bot_rocketjump",&DAT_1007d1d8,0);`
- `(&DAT_105e4280,"bot_grapple",&DAT_1007d1d8,0);`
- `(&DAT_105e4980,"bot_fastchat",&DAT_1007d0a8,0);`
- `(&DAT_105e3d20,"bot_nochat",&DAT_1007d0a8,0x80000);`
- `(&DAT_105e4160,"bot_testrchat",&DAT_1007d0a8,0);`
- `(&DAT_105e3e80,"bot_challenge",&DAT_1007d0a8,0x80000);`
- `(&DAT_105e43c0,"bot_predictobstacles",&DAT_1007d1d8,0);`
- `(&DAT_105e44e0,"g_spSkill",&DAT_1007d53c,0);`

The source constant map identifies `0x80000` as `CVAR_CLOUD` in `src/code/game/q_shared.h`.

The same Ghidra corpus separately shows `bot_minplayers` registered in qagame with flag `4`, which already matches the source `CVAR_SERVERINFO` registration in `g_bot.c`. Engine-side retail evidence for `SV_BotInitCvars` keeps its precreation call unflagged:

- Binary Ninja HLIL: `sub_4ce0d0(..., "bot_minplayers", U"0", 0)`
- Ghidra engine decompile: `Cvar_Get("bot_minplayers", &DAT_0054ffe0, 0);`

That boundary means this pass leaves `sv_bot.c` unchanged for `bot_minplayers`.

## Reconstruction

- Changed qagame `bot_thinktime` registration from `CVAR_CHEAT` to unflagged `0`.
- Changed qagame `bot_nochat` registration to `CVAR_CLOUD`.
- Changed qagame `bot_challenge` registration to `CVAR_CLOUD`.
- Added parity assertions tying the reconstructed source to qagame HLIL `BotAISetup`/`BotAIStartFrame`, qagame Ghidra `0x80000` calls, engine HLIL/ Ghidra `bot_thinktime`, and the local `CVAR_CLOUD` definition.

## Confidence

High. The names, defaults, registration order, exact retail flag values, and runtime bridge calls are present in the committed qagame HLIL and Ghidra slices. The source constant mapping for `0x80000` is already established and used throughout the Quake Live cvar parity tests.
