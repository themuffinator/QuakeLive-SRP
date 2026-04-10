# `qcommon` VM Fallback Ownership Note

Last updated: 2026-04-10

Scope: `src/code/qcommon/vm.c`, `src/code/qcommon/vm_interpreted.c`, and `src/code/qcommon/vm_x86.c` against retail `quakelive_steam.exe`, with focused proof for the Windows fallback lane that sits beneath the already-closed native DLL host path.

## Retail evidence anchors

- `docs/reverse-engineering/quakelive_steam_mapping_round_63.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_84.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_99.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_107.md`
- current writable source in `src/code/qcommon/vm.c`, `src/code/qcommon/vm_interpreted.c`, and `src/code/qcommon/vm_x86.c`
- `tests/vm_fallback_harness.c`
- `tests/test_qcommon_vm_fallback_parity.py`

## Observed retail facts

1. Mapping round `63` already binds the active Windows host ownership around `VM_Create` and `VM_Restart`: the game bootstrap and restart owners still raise the retained `"VM_Create on game failed"` and `"VM_Restart on game failed"` fatals, but Quake Live folds its native-module path around the same host seam instead of replacing it with a different subsystem.
2. Mapping round `84` binds the native DLL contract tightening in `vm.c`, including `VM_ValidateNativeDllInterface`. That pass confirms the active retail closure lives at the structured DLL boundary, not in a separate platform-specific VM owner.
3. Mapping round `99` binds `Sys_LoadDll`, including the retained Win32 search roots, `"%sx86.dll"` naming, `dllEntry` resolution, and the module entry contract that the native `ui`, `cgame`, and `qagame` path depends on.
4. Mapping round `107` binds the retained UI-side lifecycle to the same owner family: `vm_ui` is read, `VM_Create` is called for `"ui"`, the `"VM_Create on UI failed"` fatal is preserved, and the API-version gate remains part of the same host path.
5. Across those rounds the stable retail story is consistent: Windows defaults to native modules, but the owning host seam is still `vm.c`, where native loading, restart, and qvm fallback selection meet.

## Observed current-source facts after `QC-P5`

1. `VM_Init()` still defaults `vm_cgame`, `vm_game`, and `vm_ui` to `"0"`, matching the retail Windows story that native modules are preferred by default.
2. `VM_Create()` retains the full recovered selection ladder in `vm.c`:
   - `fs_restrict` forces `interpret = VMI_COMPILED`
   - native `Sys_LoadDll` is attempted first when the lane is `VMI_NATIVE`
   - native load failure logs `"Failed to load dll, looking for qvm."`
   - fallback then opens `vm/<name>.qvm`
   - `VM_Compile` owns the compiled fallback path and `VM_PrepareInterpreter` owns the bytecode interpreter path
3. `VM_Restart()` re-enters the same owner seam instead of inventing a restart-only path:
   - `VM_Create( name, systemCall, VMI_NATIVE, dllImports, dllApiVersion );`
4. `vm_interpreted.c` is now directly bounded as the retained interpreter backend rather than as an unowned blind spot:
   - `VM_PrepareInterpreter`
   - `VM_CallInterpreted`
   - `SyscallContract_LogEvent( "vm-interpreted", vm->name, ... )`
5. `vm_x86.c` remains the retained compiled fallback backend:
   - `VM_Compile`
   - `VM_CallCompiled`
   - `AsmCall`
   - the legacy `instructionPointers = vm->instructionPointers` and `callMask = vm->dataMask` setup
6. The pointer-boundary helpers still preserve the expected native-versus-qvm split:
   - `VM_ArgPtr` and `VM_ExplicitArgPtr` return direct pointers for native DLL calls
   - qvm lanes keep masked data-base-relative pointer semantics

## Compatibility boundary

The active strict Windows parity owner is the host-selection seam in `vm.c`, not every historical backend equally.

Observed implication:

1. `vm_interpreted.c` matters to strict parity because the host still falls back to interpreted qvm execution when the native DLL lane is unavailable and compiled fallback is not selected.
2. `vm_x86.c` is still retained and must keep working at the boundary, but it is treated as a bounded compatibility carry rather than as an independent strict-retail owner. The committed retail evidence proves the Windows host chooses native DLLs first, and the new `QC-P5` harness now proves that `vm.c` still selects, restarts, and dispatches into the compiled fallback backend correctly.
3. That means the strict qcommon score no longer treats the entire fallback family as a vague open gap. The score now treats the selection seam and interpreter boundary as closed, while keeping the legacy x86 backend explicit as a compatibility carry beneath that closed host seam.

## Validation surface closed by `QC-P5`

`tests/vm_fallback_harness.c` now exposes focused entrypoints that exercise the retained host boundary directly:

- `QLR_VM_TestInitDefaults`
- `QLR_VM_TestNativeFallbackToCompiled`
- `QLR_VM_TestRestrictForcesCompiled`
- `QLR_VM_TestMissingQvmAfterNativeFailure`
- `QLR_VM_TestInterpreterAdd`
- `QLR_VM_TestInterpreterSyscall`
- `QLR_VM_TestRestartNativeFallback`
- `QLR_VM_TestArgPtrModes`

`tests/test_qcommon_vm_fallback_parity.py` now keeps the fallback lane pinned with both runtime and source checks:

1. native DLL failure falls back to compiled qvm execution
2. `fs_restrict` forces compiled fallback without attempting a native load
3. missing qvm content after native failure stays a hard failure with the retained fallback log
4. the real interpreter path executes bytecode and preserves syscall-contract logging
5. restart re-enters the native-first host seam before falling back again
6. masked qvm pointer semantics and native direct-pointer semantics stay distinct
7. `vm.c`, `vm_interpreted.c`, and `vm_x86.c` still contain the expected host-selection and backend-dispatch anchors

## Conclusion

`QC-G03` is now closed.

The remaining strict qcommon debt is no longer inside the fallback VM owner family. The host-selection seam in `vm.c` is source-backed, the interpreted fallback path is directly exercised, the compiled fallback handoff is bounded, and the legacy x86 backend is now documented as a compatibility carry instead of an open-ended parity blind spot.
