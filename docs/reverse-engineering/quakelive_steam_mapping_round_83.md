# Quake Live Steam Host Mapping Round 83

## Scope

This round closes the next bounded `quakelive_steam.exe` host edge-contract
slice at the central native VM/export boundary:

- explicit `qboolean` normalization for native UI export arguments/results
- explicit `qboolean` normalization for native cgame export arguments/results
- explicit `qboolean` normalization for native qagame export arguments/results

The evidence stayed inside the committed corpus plus the writable source tree:

- `docs/architecture/native-pipeline.md`
- `src/code/qcommon/vm.c`
- `tests/test_platform_services.py`

## `VM_Call` native export boundary

The earlier rounds normalized several high-value host callsites, but the
native export switch in `src/code/qcommon/vm.c` still forwarded a number of
documented `qboolean` contracts without explicit normalization.

Observed facts from the current native ABI notes:

- `UI_Init` takes `qboolean inGame`
- `UI_IsFullscreen`, `UI_ConsoleCommand`, `UI_HasUniqueCDKey`, and
  `UI_MenusAnyVisible` return `qboolean`
- `UI_DrawConnectScreen` takes `qboolean overlay`
- `CG_DrawActiveFrame` takes `qboolean demoPlaying`
- `CG_KeyEvent` takes `qboolean down`
- `CG_ConsoleCommand` and `CG_CopyClientIdentity` return `qboolean`
- `G_InitGame`, `G_ShutdownGame`, and `G_ClientConnect` all carry `qboolean`
  parameters
- multiple qagame query exports return `qboolean`

Before this round, those cases still relied on raw integer arguments and raw
int-sized `qboolean` returns inside the export dispatch switch.

## Retained source changes

The writable source now centralizes that contract in `src/code/qcommon/vm.c`:

- `VM_NormalizeQbooleanArg( int value )`
- `VM_NormalizeQbooleanResult( qboolean value )`

Those helpers now gate the native export switch for the documented `qboolean`
cases across all three native module families:

- UI
  - `UI_INIT`
  - `UI_IS_FULLSCREEN`
  - `UI_CONSOLE_COMMAND`
  - `UI_DRAW_CONNECT_SCREEN`
  - `UI_HASUNIQUECDKEY`
  - `UI_MENUS_ANY_VISIBLE`
- cgame
  - `CG_CONSOLE_COMMAND`
  - `CG_DRAW_ACTIVE_FRAME`
  - `CG_KEY_EVENT`
  - `CG_COPY_CLIENT_IDENTITY`
- qagame
  - `GAME_INIT`
  - `GAME_SHUTDOWN`
  - `GAME_CLIENT_CONNECT`
  - `GAME_CONSOLE_COMMAND`
  - `GAME_CAN_CLIENT_SEE_CLIENT`
  - `GAME_FREEZE_CAN_SEE_THAW_PROGRESS_EVENT`
  - `GAME_IS_OBJECTIVE_ENTITY`
  - `GAME_SHOULD_SUPPRESS_VOICE_TO_CLIENT`
  - `GAME_IS_CLIENT_ADMIN`
  - `GAME_ARE_ENEMY_CLIENTS`

That closes the contract at the host’s central native dispatch boundary rather
than depending only on scattered caller-side normalization.

## Verification

Updated coverage landed in:

- `tests/test_platform_services.py`

Command run:

```text
python -m pytest tests/test_steamworks_harness.py tests/test_platform_services.py tests/test_ui_menu_files.py -q
```

Result:

- `77 passed`

## Outcome

This round did not add new address aliases. It consumed already-mapped host
ownership in one concrete way:

- the central native export switch now enforces explicit `qboolean`
  normalization for the documented UI, cgame, and qagame contracts instead of
  forwarding raw int-sized truth values through unchanged

Estimated parity for this round: `83% -> 84%`.
