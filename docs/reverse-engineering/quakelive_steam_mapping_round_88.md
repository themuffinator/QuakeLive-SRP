# Quake Live Steam Host Mapping Round 88

## Scope

This round closes the next bounded `quakelive_steam.exe` host compatibility
slice at the cgame native export-table tail contract:

- explicit integer-contract wrappers for `CG_GET_CHAT_FIELD_Y`
- explicit integer-contract wrappers for `CG_GET_CHAT_FIELD_PIXEL_WIDTH`
- explicit integer-contract wrappers for `CG_SET_CLIENT_SPEAKING_STATE`

The evidence stayed inside the committed corpus plus the writable source tree:

- `src/code/cgame/cg_main.c`
- `src/code/cgame/cg_public.h`
- `src/code/qcommon/vm.c`
- `tests/test_platform_services.py`

## Cgame native export tail contract

The recovered cgame native export slab includes a short tail used by the host
for chat-field and voice-indicator helpers:

- `CG_NATIVE_EXPORT_GET_CHAT_FIELD_Y`
- `CG_NATIVE_EXPORT_GET_CHAT_FIELD_PIXEL_WIDTH`
- `CG_NATIVE_EXPORT_GET_CHAT_FIELD_WIDTH_IN_CHARS`
- `CG_NATIVE_EXPORT_SET_CLIENT_SPEAKING_STATE`

Observed facts from the retained source before this round:

- `vmMain` already exported those contracts through integer returns:
  - `return (int)CG_GetChatFieldY();`
  - `return (int)CG_GetChatFieldPixelWidth();`
  - `return (int)(intptr_t)CG_SetClientSpeakingState( arg0, arg1 );`
- the native export table in `cg_main.c` still pointed those slots directly at
  the internal helpers:
  - `CG_GetChatFieldY` returning `float`
  - `CG_GetChatFieldPixelWidth` returning `float`
  - `CG_SetClientSpeakingState` returning `void *`
- `vm.c` compensated by calling those native export slots with float/pointer
  signatures and coercing the result on the host side

That left the recovered native export slab relying on implicit ABI details
instead of publishing the same explicit integer contract that `vmMain`
already exposed.

## Retained source changes

The writable source now makes that contract explicit in `src/code/cgame/cg_main.c`:

- `CG_NativeGetChatFieldY()`
- `CG_NativeGetChatFieldPixelWidth()`
- `CG_NativeSetClientSpeakingState( int clientNum, int speaking )`

Those wrappers now:

- mirror the existing `vmMain` integer coercion for the chat-field floats
- mirror the existing `vmMain` pointer-to-int coercion for the speaking-state
  sidecar
- own the corresponding native export slots in the cgame export table

`src/code/qcommon/vm.c` is tightened to match that explicit slot contract:

- the two chat-field slots now dispatch as `int (QDECL *)( void )`
- the speaking-state slot now dispatches as `int (QDECL *)( int, int )`

That removes the last reliance in this export band on float-return and
pointer-return ABI tolerance across the native cgame export boundary.

## Verification

Updated coverage landed in:

- `tests/test_platform_services.py`

Command run:

```text
python -m pytest tests/test_steamworks_harness.py tests/test_platform_services.py tests/test_ui_menu_files.py -q
```

Result:

- `82 passed`

## Outcome

This round did not add new address aliases. It consumed already-mapped host
ownership in one concrete way:

- the cgame native export tail now publishes the same integer-contract surface
  through both `vmMain` and the recovered native export table instead of
  exposing raw float/pointer helper signatures and relying on host-side ABI
  coercion

Estimated parity for this round: `88% -> 89%`.
