# Quake Live Steam Host Mapping Round 89

## Scope

This round closes the next bounded `quakelive_steam.exe` host compatibility
slice at the UI native key-event export contract:

- explicit slot wrapper for the native UI key-event export
- explicit `qboolean` normalization for the native UI key-event dispatch
- shared retained ownership for both the `vmMain` and native export paths

The evidence stayed inside the committed corpus plus the writable source tree:

- `src/code/ui/ui_main.c`
- `src/code/ui/ui_public.h`
- `src/code/client/cl_keys.c`
- `src/code/qcommon/vm.c`
- `tests/test_platform_services.py`

## UI native key-event slot contract

Observed facts from the retained source before this round:

- the engine still issues UI key events through `VM_Call( uivm, UI_KEY_EVENT, key, down, time )`
- the legacy `vmMain` path in `ui_main.c` consumed that as `arg0`, `arg1`,
  and `arg2`, but only forwarded `arg0` and `arg1` into `_UI_KeyEvent`
- the native export table still pointed `UI_NATIVE_EXPORT_KEY_EVENT` directly
  at `_UI_KeyEvent( int key, qboolean down )`
- `vm.c` compensated by calling that native export slot as
  `void (QDECL *)( int, int, int )` and forwarding all three raw ints

That meant the retained native export path relied on cdecl tolerance and raw
integer truthiness instead of publishing an explicit recovered slot owner for
the `key/down/time` surface that the engine already drives.

## Retained source changes

The writable source now reconstructs that slot explicitly:

- `src/code/ui/ui_main.c`
  - adds `UI_NativeKeyEvent( int key, qboolean down, int time )`
  - routes the legacy `vmMain` `UI_KEY_EVENT` case through that wrapper
  - assigns `UI_NATIVE_EXPORT_KEY_EVENT` to that wrapper instead of exposing
    `_UI_KeyEvent` directly
- `src/code/qcommon/vm.c`
  - dispatches the native UI key-event slot as
    `void (QDECL *)( int, qboolean, int )`
  - normalizes the `down` argument through `VM_NormalizeQbooleanArg(...)`

The retained wrapper intentionally ignores `time` after owning the slot
surface, which matches the current UI implementation while removing the
ABI-tolerance dependency from the native export boundary.

## Verification

Updated coverage landed in:

- `tests/test_platform_services.py`

Command run:

```text
python -m pytest tests/test_steamworks_harness.py tests/test_platform_services.py tests/test_ui_menu_files.py -q
```

Result:

- `83 passed`

## Outcome

This round did not add new address aliases. It consumed already-mapped host
ownership in one concrete way:

- the native UI key-event slot now has an explicit retained wrapper that owns
  the `key/down/time` contract for both `vmMain` and the recovered native
  export table, instead of exposing a two-argument helper and depending on
  extra-argument ABI tolerance

Estimated parity for this round: `89% -> 90%`.
