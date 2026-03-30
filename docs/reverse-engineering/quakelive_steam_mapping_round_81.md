# Quake Live Steam Host Mapping Round 81

## Scope

This round closes the next bounded `quakelive_steam.exe` host edge-contract
band still called out by the native ABI notes:

- the raw-int return handling in the UI, cgame, and server console-command
  query owners
- the raw-int fullscreen query handling in the UI draw gate

The evidence stayed inside the committed corpus plus the writable source tree:

- `docs/architecture/native-pipeline.md`
- `docs/reverse-engineering/ui-mapping-pass-2026-03-20.md`
- `src/code/client/cl_ui.c`
- `src/code/client/cl_cgame.c`
- `src/code/client/cl_scrn.c`
- `src/code/server/sv_game.c`

## Strict `qboolean` command/query contracts

The native-pipeline notes already document these host-side entry points as
`qboolean` contracts:

- `UI_ConsoleCommand(int realtime)`
- `CG_ConsoleCommand(void)`
- `G_ConsoleCommand(void)`
- `UI_IsFullscreen(void)`

Before this round, the retained host still forwarded the raw `VM_Call(...)`
integer return directly in the three console-command wrappers and assigned the
raw fullscreen return directly into the `SCR_DrawScreenField()` gate.

That worked for the rebuilt source path because `qboolean` is int-sized on
this target, but it still left the host looser than the documented retail
native interface shape. The earlier Round 80 `UI_HASUNIQUECDKEY` cleanup
closed one example of that mismatch; this round closes the adjacent band.

## Retained source changes

The writable source now normalizes these owners explicitly:

- `src/code/client/cl_ui.c`
  - `UI_GameCommand()` now converts any non-zero `UI_CONSOLE_COMMAND` return
    to `qtrue`
- `src/code/client/cl_cgame.c`
  - `CL_GameCommand()` now converts any non-zero `CG_CONSOLE_COMMAND` return
    to `qtrue`
- `src/code/server/sv_game.c`
  - `SV_GameCommand()` now converts any non-zero `GAME_CONSOLE_COMMAND`
    return to `qtrue`
- `src/code/client/cl_scrn.c`
  - `SCR_DrawScreenField()` now normalizes `UI_IS_FULLSCREEN` to explicit
    `qtrue` / `qfalse` before gating the background render path

This keeps the retained host aligned with the documented native ABI instead of
requiring exact integer spellings from the native DLL path.

## Verification

Updated coverage landed in:

- `tests/test_platform_services.py`

Command run:

```text
python -m pytest tests/test_steamworks_harness.py tests/test_platform_services.py tests/test_ui_menu_files.py -q
```

Result:

- `75 passed`

## Outcome

This round did not add new address aliases. It consumed already-mapped host
ownership in one concrete way:

- the UI, cgame, and server console-command query owners plus the UI
  fullscreen gate now honor strict `qboolean` normalization instead of passing
  raw native integer returns through unchanged

Estimated parity for this round: `81% -> 82%`.
