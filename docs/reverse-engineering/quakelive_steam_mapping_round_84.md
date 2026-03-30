# Quake Live Steam Host Mapping Round 84

## Scope

This round closes the next bounded `quakelive_steam.exe` host compatibility
slice at the structured native DLL loader boundary:

- strict validation of recovered native export-table sizes for `uix86.dll`
- strict validation of recovered native export-table sizes for `cgamex86.dll`
- strict validation of recovered native export-table sizes for `qagamex86.dll`

The evidence stayed inside the committed corpus plus the writable source tree:

- `src/code/ui/ui_public.h`
- `src/code/cgame/cg_public.h`
- `src/code/game/g_public.h`
- `src/code/qcommon/vm.c`
- `tests/test_platform_services.py`

## Structured native DLL validation

The retained native loader already rejected structured DLLs whose reported
native API version did not match the recovered retail expectation.

Observed facts from the recovered export tables:

- `uix86.dll` has a fixed recovered native export count of
  `UI_NATIVE_EXPORT_COUNT`
- `cgamex86.dll` has a fixed recovered native export count of
  `CG_NATIVE_EXPORT_COUNT`
- `qagamex86.dll` has a fixed recovered native export count of
  `GAME_NATIVE_EXPORT_COUNT`
- the recovered `cgame` export slab includes one observed intentional null slot:
  `CG_NATIVE_EXPORT_RESERVED_NULL`

Before this round, `VM_Create()` accepted any structured export table whose API
version matched, even if the returned table omitted a required slot and would
only fail later when the host reached the first affected `VM_Call`.

## Retained source changes

The writable source now tightens that boundary in `src/code/qcommon/vm.c`:

- `VM_GetExpectedNativeExportCount( const char *module )`
- `VM_NativeExportSlotIsRequired( const char *module, int slot )`
- `VM_ValidateNativeDllInterface( vm_t *vm )`

The loader now:

- derives the recovered expected export-table size for `ui`, `cgame`, and
  `qagame`
- skips only the documented retail null cgame slot
- rejects structured DLLs that leave any other required export slot null before
  the VM is accepted by the host

That shifts the host closer to retail-binary compatibility validation instead
of relying on deferred first-call failures.

## Verification

Updated coverage landed in:

- `tests/test_platform_services.py`

Command run:

```text
python -m pytest tests/test_steamworks_harness.py tests/test_platform_services.py tests/test_ui_menu_files.py -q
```

Result:

- `78 passed`

## Outcome

This round did not add new address aliases. It consumed already-mapped host
ownership in one concrete way:

- the structured native loader now enforces the recovered required export-slot
  surface for `ui`, `cgame`, and `qagame` instead of accepting incomplete
  retail-style DLL tables until the first missing-slot dispatch

Estimated parity for this round: `84% -> 85%`.
