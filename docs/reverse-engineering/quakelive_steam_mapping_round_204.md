# quakelive_steam.exe Mapping Round 204

Date: 2026-04-28

Scope: retained bot movement weapon-jump and jumppad travel helpers around the
old queue head `0x004A4280`.

## Summary

This round resolved `7` additional `quakelive_steam.exe` aliases.
Classification mix:

- `7` engine-owned functions
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The useful outcome is that the anonymous `0x004A42**` through `0x004A49**`
movement seam now reads as real `be_ai_move.c` ownership instead of opaque bot
glue. The old queue head `0x004A4280` is gone, and the adjacent weapon-jump,
jumppad, and local-goal movement wrappers are now source-backed too.

## Evidence Notes

- The decisive source anchor is the retained bot movement lane in
  [be_ai_move.c](</E:/Repositories/QuakeLive-reverse/src/code/botlib/be_ai_move.c:2744>),
  especially
  [BotTravel_RocketJump](</E:/Repositories/QuakeLive-reverse/src/code/botlib/be_ai_move.c:2744>),
  [BotTravel_BFGJump](</E:/Repositories/QuakeLive-reverse/src/code/botlib/be_ai_move.c:2809>),
  [BotFinishTravel_WeaponJump](</E:/Repositories/QuakeLive-reverse/src/code/botlib/be_ai_move.c:2870>),
  [BotTravel_JumpPad](</E:/Repositories/QuakeLive-reverse/src/code/botlib/be_ai_move.c:2910>),
  [BotFinishTravel_JumpPad](</E:/Repositories/QuakeLive-reverse/src/code/botlib/be_ai_move.c:2937>),
  [BotReachabilityTime](</E:/Repositories/QuakeLive-reverse/src/code/botlib/be_ai_move.c:2965>),
  and
  [BotMoveInGoalArea](</E:/Repositories/QuakeLive-reverse/src/code/botlib/be_ai_move.c:2993>).
- `sub_4A4280` is exact as `BotTravel_RocketJump`. Its HLIL zeroes the mover
  result, builds `reach->start - ms->origin`, computes the same view-angle gate
  with `PITCH = 90`, switches to `reach->end` when the bot is aligned, emits
  `EA_Jump`, `EA_Attack`, and `EA_Move(..., 800)`, then tags the movement-view
  and movement-weapon flags while selecting the rocket launcher.
- `sub_4A4470` is exact as `BotTravel_BFGJump`. The retained HLIL mirrors the
  checked-in source, including the quirky first angle gate before the later
  `Vector2Angles` writeback, followed by the same jump/attack burst and BFG
  weapon selection.
- `sub_4A4640` and `sub_4A47A0` are the two `BotAirControl`-using finish
  helpers: `BotFinishTravel_WeaponJump` and `BotFinishTravel_JumpPad`. The
  fallback direct-move path, speed defaulting, and post-`BotAirControl` move
  result writes match exactly.
- `sub_4A4700` is exact as `BotTravel_JumpPad`, and `sub_4A4870` is exact as
  `BotReachabilityTime`; the latter preserves the same travel-type switch with
  `5`, `6`, `10`, and default `8` timeouts plus the “not implemented yet”
  print on unknown travel types.
- `sub_4A4910` is exact as `BotMoveInGoalArea`. The HLIL matches the source's
  swim-vs-walk split, speed clamp, `BotCheckBlocked` call, direct `EA_Move`,
  optional swim-view flagging, and the reset of `lastreachnum`, `lastareanum`,
  `lastgoalareanum`, and `lastorigin`.

## Aliases Added

- `sub_4A4280` -> `BotTravel_RocketJump`
- `sub_4A4470` -> `BotTravel_BFGJump`
- `sub_4A4640` -> `BotFinishTravel_WeaponJump`
- `sub_4A4700` -> `BotTravel_JumpPad`
- `sub_4A47A0` -> `BotFinishTravel_JumpPad`
- `sub_4A4870` -> `BotReachabilityTime`
- `sub_4A4910` -> `BotMoveInGoalArea`

## Verification

Static mapping validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- scoped duplicate-key scan for the `quakelive_steam` alias block passed with
  `0` duplicates
- recount after this pass: `2162` raw alias entries, `2089` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `38.169%` of `5473` functions
- `git diff --check` passed aside from the repo's existing LF -> CRLF
  normalization warnings on touched text files
- no build or runtime launch was needed; this was mapping-only work on the
  committed evidence corpus

Parity estimate after this pass:

- strict-retail Windows replacement target: `100%` before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

After this round, the refreshed largest-unaliased queue begins with:

| # | Address | Ghidra name | Size |
| ---: | --- | --- | ---: |
| 1 | `0x004B3672` | `FUN_004b3672` | `495` |
| 2 | `0x004B6630` | `FUN_004b6630` | `483` |
| 3 | `0x004241C0` | `FUN_004241c0` | `482` |
| 4 | `0x00498890` | `FUN_00498890` | `480` |
| 5 | `0x00480DD0` | `FUN_00480dd0` | `479` |
| 6 | `0x004C84E0` | `FUN_004c84e0` | `479` |
| 7 | `0x0050EF80` | `FUN_0050ef80` | `476` |
| 8 | `0x00412970` | `FUN_00412970` | `472` |
| 9 | `0x004A21A0` | `FUN_004a21a0` | `470` |
| 10 | `0x0050BB00` | `FUN_0050bb00` | `469` |

The next pass can return to the remaining `FUN_004b3672` console split, keep
harvesting the surrounding bot movement seam near `0x004A21A0`, or pivot into
the large support-library leftovers once a comparably exact evidence lane opens
up.
