# Quake Live Steam Host Mapping Round 90

## Scope

This round closes the remaining bounded module-side `qboolean` adapter slice
that sat between the already-normalized host export dispatch and the native
module ownership points:

- explicit retained wrappers for the remaining UI boolean-bearing native export
  slots
- explicit retained wrappers for the remaining cgame boolean-bearing native
  export slots
- explicit retained wrappers for the remaining qagame boolean-bearing native
  export and pointer-return slots

The evidence stayed inside the committed corpus plus the writable source tree:

- `src/code/ui/ui_main.c`
- `src/code/cgame/cg_main.c`
- `src/code/game/g_main.c`
- `src/code/qcommon/vm.c`
- `tests/test_platform_services.py`
- `tests/test_ui_menu_files.py`

## Module-side native export boolean contract

Observed facts from the retained source before this round:

- the host native export switch in `vm.c` already normalized the documented
  boolean-bearing slots for:
  - `UI_INIT`
  - `UI_DRAW_CONNECT_SCREEN`
  - `CG_DRAW_ACTIVE_FRAME`
  - `CG_KEY_EVENT`
  - `GAME_INIT`
  - `GAME_SHUTDOWN`
  - `GAME_CLIENT_CONNECT`
- the legacy `vmMain` paths in `ui_main.c`, `cg_main.c`, and `g_main.c` still
  forwarded those incoming arguments as raw ints
- the corresponding native export tables still pointed directly at the raw
  module helpers instead of explicit retained wrappers that owned the recovered
  boolean and pointer contracts

That left the module side lagging behind the stricter host-side reconstruction:
the host normalized the ABI, but the module-owned export slabs still published
the older direct helper surfaces.

## Retained source changes

The writable source now closes that module-side gap explicitly:

- `src/code/ui/ui_main.c`
  - adds `UI_NativeInit( qboolean inGameLoad )`
  - adds `UI_NativeDrawConnectScreen( qboolean overlay )`
  - routes both `vmMain` and the `UI_NATIVE_EXPORT_INIT` /
    `UI_NATIVE_EXPORT_DRAW_CONNECT_SCREEN` slots through those wrappers
- `src/code/cgame/cg_main.c`
  - adds `CG_NativeDrawActiveFrame( int, stereoFrame_t, qboolean )`
  - adds `CG_NativeKeyEvent( int, qboolean )`
  - routes both `vmMain` and the `CG_NATIVE_EXPORT_DRAW_ACTIVE_FRAME` /
    `CG_NATIVE_EXPORT_KEY_EVENT` slots through those wrappers
- `src/code/game/g_main.c`
  - adds `G_NativeInit( int, int, qboolean )`
  - adds `G_NativeShutdown( qboolean )`
  - adds `G_NativeClientConnect( int, qboolean, qboolean )`
  - routes both `vmMain` and the `GAME_NATIVE_EXPORT_INIT` /
    `GAME_NATIVE_EXPORT_SHUTDOWN` / `GAME_NATIVE_EXPORT_CLIENT_CONNECT` slots
    through those wrappers

The retained wrappers intentionally keep behavior unchanged inside the modules.
Their purpose is to make the recovered boolean and pointer contracts explicit at
the native export boundary, rather than relying on raw integer forwarding in
`vmMain` or direct helper exposure in the native export tables.

## Verification

Updated coverage landed in:

- `tests/test_platform_services.py`
- `tests/test_ui_menu_files.py`

Command run:

```text
python -m pytest tests/test_steamworks_harness.py tests/test_platform_services.py tests/test_ui_menu_files.py -q
```

Result:

- `84 passed`

## Outcome

This round did not add new address aliases. It consumed already-mapped host and
module ownership in one concrete way:

- the remaining UI, cgame, and qagame boolean-bearing native export slots now
  publish explicit retained wrappers through both `vmMain` and the recovered
  export tables, instead of exposing raw helpers on the module side while the
  host side already expected normalized contracts

Estimated parity for this round: `90% -> 91%`.
