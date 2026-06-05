# Botlib EA Input And Export Mapping - 2026-06-05

## Coordination

Selected slice: elementary actions (`be_ea.c`) and related export/syscall
wiring.

This slice was chosen to avoid the active parser/resource-reader work in
session `019e97e9-ddaa-7e53-81bb-6511a54422c2` and the completed chat-lane
work in session `019e97ef-042c-7171-855b-46853b848cb1`. This round did not
edit `l_struct.c`, `l_precomp.c`, `be_ai_chat.c`, the shared internal parity
test, or the chat mapping note.

## Evidence

- Owning retail binary: `assets/quakelive/quakelive_steam.exe`.
- Ghidra companion corpus:
  - `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
  - `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
  - `references/reverse-engineering/ghidra/quakelive_steam/exports.txt`
  - `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  - `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- Canonical HLIL:
  - `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part03.txt`
- Name support:
  - `references/analysis/quakelive_symbol_aliases.json`
- Reconstruction surface:
  - `src/code/botlib/be_ea.c`
  - `src/code/botlib/be_interface.c`
  - `src/code/game/botlib.h`
  - `src/code/game/g_public.h`
  - `src/code/game/g_syscalls.c`
  - `src/code/game/ai_main.c`
  - `src/code/server/sv_game.c`
  - `src/code/server/ql_game_imports.inc`

`metadata.txt` identifies `quakelive_steam.exe` as x86 32-bit Windows with
5473 functions, 351 imports, 2 exports, and 4377 analysis symbols. The EA band
is not promoted in `analysis_symbols.txt`; the stable names are maintained in
the repository alias map and are cross-checked against HLIL and source shape.

## Retail Function Map

| Address | Alias | Size | Evidence |
| --- | --- | ---: | --- |
| `004A78C0` | `EA_Say` | 33 | calls `BotClientCommand(client, va("say %s", str))` shape |
| `004A78F0` | `EA_SayTeam` | 33 | calls `BotClientCommand(client, va("say_team %s", str))` shape |
| `004A7920` | `EA_Gesture` | 28 | ORs `0x20000` into `bot_input_t.actionflags` |
| `004A7940` | `EA_Command` | 10 | tail-jumps to `BotClientCommand` import callback |
| `004A7950` | `EA_SelectWeapon` | 24 | writes `bot_input_t + 0x24` |
| `004A7970` | `EA_Attack` | 25 | ORs `0x1` |
| `004A7990` | `EA_Talk` | 28 | ORs `0x10000` |
| `004A79B0` | `EA_Use` | 25 | ORs `0x2` |
| `004A79D0` | `EA_Respawn` | 25 | ORs `0x8` |
| `004A79F0` | `EA_Jump` | 44 | gates `ACTION_JUMP` with hidden latch `0x10000000` |
| `004A7A20` | `EA_DelayedJump` | 48 | gates `ACTION_DELAYEDJUMP` with hidden latch `0x10000000` |
| `004A7A50` | `EA_Crouch` | 28 | ORs `0x80` |
| `004A7A70` | `EA_Walk` | 28 | ORs `0x80000` |
| `004A7A90` | `EA_Action` | 27 | ORs caller-provided flags |
| `004A7AB0` | `EA_MoveUp` | 25 | ORs `0x20` |
| `004A7AD0` | `EA_MoveDown` | 28 | ORs `0x100` |
| `004A7AF0` | `EA_MoveForward` | 28 | ORs `0x200` |
| `004A7B10` | `EA_MoveBack` | 28 | ORs `0x800` |
| `004A7B30` | `EA_MoveLeft` | 28 | ORs `0x1000` |
| `004A7B50` | `EA_MoveRight` | 28 | ORs `0x2000` |
| `004A7B70` | `EA_Move` | 105 | copies dir, clamps speed to `[-400, 400]`, stores at `+0x10` |
| `004A7BE0` | `EA_View` | 40 | copies viewangles to offsets `+0x14`, `+0x18`, `+0x1c` |
| `004A7C10` | `EA_GetInput` | 40 | writes thinktime, copies 0x28-byte input via `Com_Memcpy` |
| `004A7C40` | `EA_ResetInput` | 61 | clears transient input and preserves jump-last-frame as `0x10000000` |
| `004A7C80` | `EA_Setup` | 31 | allocates `maxclients * 0x28` cleared hunk bytes |
| `004A7CA0` | `EA_Shutdown` | 25 | frees global input buffer and nulls it |
| `004A8060` | `Init_EA_Export` | 175 | fills `ea_export_t` slots |
| `004D7980` | inert stub used for `EA_EndRegular` | 1 | assigned to export slot `0x16` |

The contiguous retail EA band omits the legacy GPL helper commands
`EA_Tell`, `EA_UseItem`, `EA_DropItem`, `EA_UseInv`, and `EA_DropInv`; they
are not part of the observed Quake Live `ea_export_t` table.

## `bot_input_t` Layout

The HLIL consistently indexes the global `botinputs` array as
`data_16ddaa4 + client * 0x28`, matching the public `bot_input_t` layout:

| Offset | Field | Evidence |
| --- | --- | --- |
| `+0x00` | `thinktime` | `EA_GetInput` stores the caller thinktime before copying |
| `+0x04` | `dir[0]` | `EA_Move` writes from `arg2[0]` |
| `+0x08` | `dir[1]` | `EA_Move` writes from `arg2[1]` |
| `+0x0C` | `dir[2]` | `EA_Move` writes from `arg2[2]` |
| `+0x10` | `speed` | `EA_Move` stores the clamped speed |
| `+0x14` | `viewangles[0]` | `EA_View` writes from `arg2[0]` |
| `+0x18` | `viewangles[1]` | `EA_View` writes from `arg2[1]` |
| `+0x1C` | `viewangles[2]` | `EA_View` writes from `arg2[2]` |
| `+0x20` | `actionflags` | every simple action ORs a flag here |
| `+0x24` | `weapon` | `EA_SelectWeapon` writes here |

The only source reconstruction in this round is the hidden latch constant:
`ACTION_JUMPEDLASTFRAME` is now `0x10000000` in `be_ea.c`. Retail HLIL checks
that mask in `EA_Jump` and `EA_DelayedJump`, then `EA_ResetInput` preserves it
when the outgoing input carried `ACTION_JUMP` (`0x10`). The previous local value
`128` overlapped `ACTION_CROUCH` and did not match retail.

## Export Wiring

`Init_EA_Export` at `004A8060` assigns the public `ea_export_t` as follows:

| Slot | Retail target | Public field |
| ---: | --- | --- |
| `0x00` | `004A7940` | `EA_Command` |
| `0x01` | `004A78C0` | `EA_Say` |
| `0x02` | `004A78F0` | `EA_SayTeam` |
| `0x03` | `004A7A90` | `EA_Action` |
| `0x04` | `004A7A70` | `EA_Walk` |
| `0x05` | `004A7920` | `EA_Gesture` |
| `0x06` | `004A7990` | `EA_Talk` |
| `0x07` | `004A7970` | `EA_Attack` |
| `0x08` | `004A79B0` | `EA_Use` |
| `0x09` | `004A79D0` | `EA_Respawn` |
| `0x0A` | `004A7AB0` | `EA_MoveUp` |
| `0x0B` | `004A7AD0` | `EA_MoveDown` |
| `0x0C` | `004A7AF0` | `EA_MoveForward` |
| `0x0D` | `004A7B10` | `EA_MoveBack` |
| `0x0E` | `004A7B30` | `EA_MoveLeft` |
| `0x0F` | `004A7B50` | `EA_MoveRight` |
| `0x10` | `004A7A50` | `EA_Crouch` |
| `0x11` | `004A7950` | `EA_SelectWeapon` |
| `0x12` | `004A79F0` | `EA_Jump` |
| `0x13` | `004A7A20` | `EA_DelayedJump` |
| `0x14` | `004A7B70` | `EA_Move` |
| `0x15` | `004A7BE0` | `EA_View` |
| `0x16` | `004D7980` | `EA_EndRegular` inert stub |
| `0x17` | `004A7C10` | `EA_GetInput` |
| `0x18` | `004A7C40` | `EA_ResetInput` |

The current source table in `be_interface.c` matches this field order. The
HLIL assigns `EA_GetInput` at slot `0x17` immediately before assigning the
slot `0x16` inert stub, which is a compiler ordering artifact rather than a
struct-layout difference.

## Game And Server Wiring

The reconstructed call path is:

1. qagame AI code accumulates actions through `trap_EA_*` wrappers.
2. Native or VM import glue routes those calls to engine syscall IDs.
3. `SV_GameSystemCalls` dispatches `BOTLIB_EA_*` IDs to `botlib_export->ea`.
4. `EA_GetInput` copies the botlib buffer to qagame without clearing it.
5. `BotInputToUserCommand` converts `bot_input_t` into `usercmd_t`.
6. Bot lifecycle code separately calls `trap_EA_ResetInput` for reset points.

Relevant IDs:

- VM syscall range starts at `BOTLIB_EA_SAY = 400` and ends this EA block at
  `BOTLIB_EA_RESET_INPUT`.
- Quake Live native import IDs are `G_QL_IMPORT_BOTLIB_EA_SAY = 85` through
  `G_QL_IMPORT_BOTLIB_EA_RESET_INPUT = 109`.
- `QL_G_trap_EA_Move`, `QL_G_trap_EA_EndRegular`, and
  `QL_G_trap_EA_GetInput` pass floats through `QL_G_PASSFLOAT`, matching the
  VM wrapper convention.

## Qagame Consumer Map

The committed qagame symbol map supplies promoted names for the consumer side of
the same input path:

| Address | Alias | Size | Evidence |
| --- | --- | ---: | --- |
| `10021740` | `BotChangeViewAngles` | 980 | updates `bs->viewangles`, then terminates in `trap_EA_View` |
| `10021B20` | `BotInputToUserCommand` | 741 | translates `bot_input_t.actionflags` and movement into `usercmd_t` |
| `10021E10` | `BotUpdateInput` | 372 | wraps `trap_EA_GetInput`, respawn filtering, and command conversion |

Observed qagame Ghidra evidence for `BotInputToUserCommand`:

- The decompile initializes the `usercmd_t` words, writes the server time, and
  handles `ACTION_DELAYEDJUMP` by replacing it with `ACTION_JUMP`.
- It maps `ACTION_RESPAWN`/`ACTION_ATTACK` to `BUTTON_ATTACK`, `ACTION_TALK` to
  `BUTTON_TALK`, `ACTION_GESTURE` to `BUTTON_GESTURE`, `ACTION_USE` to
  `BUTTON_USE_HOLDABLE`, `ACTION_WALK` to `BUTTON_WALKING`, and the voice/team
  command flags to the retail button bits.
- It copies the selected weapon from `bot_input_t + 0x24` into the usercmd
  weapon byte.
- It scales `bot_input_t.speed` by the `127 / 400` command range ratio before
  projecting movement.
- It applies keyboard movement flags with `+/-0x7f`.
- It applies crouch/down movement only when the decompiled extra argument is not
  `0x3ff`, which matches `ENTITYNUM_NONE`. This is a retail-only consumer-side
  clue that should be reconstructed in `ai_main.c` only after the exact
  `BotUpdateInput -> BotInputToUserCommand` call signature is recovered.

The qagame decompile also shows a walk-forcing branch guarded by
`param_4 <= 0.0`, `DAT_105a8aac == 0`, and `DAT_1059de8c == 0`. The data names
are not yet promoted in the committed corpus, so this remains an observed branch
rather than a stable source reconstruction.

## Validation Added

Added `tests/test_botlib_ea_parity.py`, covering:

- alias-map names for the EA retail band and `Init_EA_Export`;
- Ghidra function sizes for the EA band and the one-byte `004D7980` inert
  `EA_EndRegular` provider;
- HLIL evidence for action flag writes, `bot_input_t` offsets, speed clamp,
  copy size, reset behavior, setup/shutdown, and export slot assignments;
- source-level shape in `be_ea.c`;
- public `bot_input_t` and `ea_export_t` fields;
- `g_public.h`, `g_syscalls.c`, `sv_game.c`, `ql_game_imports.inc`, and
  `ai_main.c` consumer wiring;
- qagame symbol-map entries and Ghidra companion decompile evidence for
  `BotChangeViewAngles`, `BotInputToUserCommand`, and `BotUpdateInput`;
- VM assembly syscall IDs `-401` through `-424` for the EA trap range.

## Open Questions

- The EA band has no promoted `analysis_symbols.txt` names; aliases remain
  repository-maintained until a later reference export promotes them.
- `EA_EndRegular` is retail-wired to a one-byte inert stub. The source body is
  empty, which matches behavior, but the retail stub itself does not preserve
  argument names or types.
- `BotInputToUserCommand` has retail-only qagame consumer clues around
  walk-forcing and crouch suppression while airborne (`ENTITYNUM_NONE`), but the
  exact extra argument provenance is not yet stable enough for a source edit.
- The legacy helper command functions in `be_ea.c` are not observed in the
  retained Quake Live EA export table. No removal was attempted in this round
  because the public surface and retail table are already bounded.
- No runtime launch was needed; the reconstruction is fully supported by the
  committed Ghidra and Binary Ninja references.

## Parity Estimate

- Selected EA slice before this round: about 89 percent. Most public functions
  were already mapped, but the hidden jump latch was wrong and the related
  wiring was not guarded by a focused test.
- Selected EA slice after this round: about 97 percent. Remaining uncertainty is
  limited to inert-stub typing and unexported legacy helper commands.
- Overall botlib parity impact: about 76 percent to 77 percent for the botlib
  source and wiring as a whole, because this is a narrow but central input
  corridor.
