# Botlib Character Cache Mapping - 2026-06-06

## Scope

This pass maps the `be_ai_char.c` character loading, defaulting, cache, interpolation, and characteristic accessor corridor against the retail `quakelive_steam.exe` botlib image. No C source rewrite was justified; the checked-in GPL-derived implementation already matches the static retail shape closely. The reconstruction work is therefore alias promotion plus parity coverage for the source and botlib/game/server wiring.

## Evidence

Observed retail function rows from `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`:

- `FUN_00496950,00496950,144,0,unknown` -> `BotDumpCharacter`
- `FUN_004969e0,004969e0,43,0,unknown` -> `BotFreeCharacterStrings`
- `FUN_00496a10,00496a10,102,0,unknown` -> `BotFreeCharacter2`
- `FUN_00496a80,00496a80,35,0,unknown` -> `BotFreeCharacter`
- `FUN_00496ab0,00496ab0,140,0,unknown` -> `BotDefaultCharacteristics`
- `FUN_00496b40,00496b40,1271,0,unknown` -> `BotLoadCharacterFromFile`
- `FUN_00497040,00497040,145,0,unknown` -> `BotFindCachedCharacter`
- `FUN_004970e0,004970e0,627,0,unknown` -> `BotLoadCachedCharacter`
- `FUN_00497360,00497360,104,0,unknown` -> `BotLoadCharacterSkill`
- `FUN_004973d0,004973d0,438,0,unknown` -> `BotInterpolateCharacters`
- `FUN_00497590,00497590,337,0,unknown` -> `BotLoadCharacter`
- `FUN_004976f0,004976f0,131,0,unknown` -> `CheckCharacteristicIndex`
- `FUN_00497780,00497780,139,0,unknown` -> `Characteristic_Float`
- `FUN_00497810,00497810,172,0,unknown` -> `Characteristic_BFloat`
- `FUN_004978c0,004978c0,143,0,unknown` -> `Characteristic_Integer`
- `FUN_00497950,00497950,139,0,unknown` -> `Characteristic_BInteger`
- `FUN_004979e0,004979e0,147,0,unknown` -> `Characteristic_String`
- `FUN_00497a80,00497a80,114,0,unknown` -> `BotShutdownCharacters`

Binary Ninja HLIL confirms the ownership and ordering in `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part03.txt`:

- `sub_496950` logs the character filename, skill, and all 80 initialized characteristics.
- `sub_4969e0` scans 80 characteristic entries and frees string values.
- `sub_496a10` performs handle validation, string cleanup, full character free, and slot clearing.
- `sub_496ab0` fills missing characteristics from the default character, duplicating strings.
- `sub_497040` scans cached characters by filename and skill, using the retail `0.01` float tolerance.
- `sub_4970e0` implements the cache/load fallback ladder for exact skill, default skill, any skill, and any default skill.
- `sub_4973d0` allocates an interpolated character, interpolates only float pairs, and copies integer/string values from the first character.
- `sub_4976f0` centralizes handle/index/initialized checks for the public characteristic accessors.
- `sub_4a8110` exports `BotLoadCharacter`, `BotFreeCharacter`, and the five characteristic accessors in slots `0..6` before chat APIs.

Source-side checks in `tests/test_botlib_character_cache_parity.py` pin the current reconstruction in `src/code/botlib/be_ai_char.c`, `src/code/botlib/be_interface.c`, `src/code/game/botlib.h`, `src/code/game/be_ai_char.h`, `src/code/game/g_public.h`, `src/code/game/g_local.h`, `src/code/game/g_syscalls.c`, `src/code/server/sv_game.c`, `src/code/server/ql_game_imports.inc`, and `src/code/game/ai_main.c`.

## Notes

- The parser still has the retail split where `BotLoadCharacterFromFile` rejects `index > MAX_CHARACTERISTICS`, while `CheckCharacteristicIndex` rejects `index >= MAX_CHARACTERISTICS`. This was preserved as evidence of retail behavior, not normalized.
- `BotFreeCharacter` remains gated by `bot_reloadcharacters`, while `BotFreeCharacter2` is the unconditional internal cleanup path used by shutdown and cache replacement.
- Native qagame import IDs `110..116` map directly to the character API, matching the legacy syscall cases and the server-side direct import slab.

## Confidence

High for static ownership, helper naming, export order, and qagame/server routing. Remaining uncertainty is limited to live bot-data behavior across retail character files and maps, which this static pass does not attempt to validate.

