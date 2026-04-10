"""Focused qcommon fallback-VM parity probes for vm.c and vm_interpreted.c."""
from __future__ import annotations

import ctypes
from pathlib import Path

import pytest

from tests.compiler_support import compile_c_binary, find_c_compiler, shared_library_name

REPO_ROOT = Path(__file__).resolve().parent.parent
VM_PATH = REPO_ROOT / "src" / "code" / "qcommon" / "vm.c"
VM_INTERPRETED_PATH = REPO_ROOT / "src" / "code" / "qcommon" / "vm_interpreted.c"
VM_X86_PATH = REPO_ROOT / "src" / "code" / "qcommon" / "vm_x86.c"


@pytest.fixture(scope="session")
def vm_fallback_harness(tmp_path_factory: pytest.TempPathFactory) -> ctypes.CDLL:
	build_dir = tmp_path_factory.mktemp("vm_fallback_harness_build")
	lib_path = build_dir / shared_library_name("vm_fallback_harness")
	compiler = find_c_compiler()

	if compiler is None:
		pytest.skip("no supported C compiler is available for the qcommon fallback-VM harness")

	compile_c_binary(
		compiler,
		[
			REPO_ROOT / "tests" / "vm_fallback_harness.c",
			REPO_ROOT / "src" / "code" / "qcommon" / "vm.c",
			REPO_ROOT / "src" / "code" / "qcommon" / "vm_interpreted.c",
		],
		lib_path,
		include_dirs=[
			REPO_ROOT / "src" / "code",
			REPO_ROOT / "src" / "code" / "qcommon",
			REPO_ROOT / "src" / "code" / "game",
			REPO_ROOT / "src" / "code" / "client",
			REPO_ROOT / "src" / "code" / "server",
			REPO_ROOT / "src" / "code" / "ui",
			REPO_ROOT / "src" / "common",
		],
		shared=True,
		workdir=REPO_ROOT,
	)

	lib = ctypes.CDLL(str(lib_path))
	lib.QLR_VM_TestLastError.argtypes = []
	lib.QLR_VM_TestLastError.restype = ctypes.c_char_p
	lib.QLR_VM_TestCapturedLog.argtypes = []
	lib.QLR_VM_TestCapturedLog.restype = ctypes.c_char_p
	lib.QLR_VM_TestLastSyscallOrigin.argtypes = []
	lib.QLR_VM_TestLastSyscallOrigin.restype = ctypes.c_char_p
	lib.QLR_VM_TestLastSyscallModule.argtypes = []
	lib.QLR_VM_TestLastSyscallModule.restype = ctypes.c_char_p
	lib.QLR_VM_TestInitDefaults.argtypes = [
		ctypes.POINTER(ctypes.c_int),
		ctypes.POINTER(ctypes.c_int),
		ctypes.POINTER(ctypes.c_int),
	]
	lib.QLR_VM_TestInitDefaults.restype = ctypes.c_int
	lib.QLR_VM_TestNativeFallbackToCompiled.argtypes = [
		ctypes.POINTER(ctypes.c_int),
		ctypes.POINTER(ctypes.c_int),
		ctypes.POINTER(ctypes.c_int),
		ctypes.POINTER(ctypes.c_int),
	]
	lib.QLR_VM_TestNativeFallbackToCompiled.restype = ctypes.c_int
	lib.QLR_VM_TestRestrictForcesCompiled.argtypes = [
		ctypes.POINTER(ctypes.c_int),
		ctypes.POINTER(ctypes.c_int),
		ctypes.POINTER(ctypes.c_int),
		ctypes.POINTER(ctypes.c_int),
	]
	lib.QLR_VM_TestRestrictForcesCompiled.restype = ctypes.c_int
	lib.QLR_VM_TestMissingQvmAfterNativeFailure.argtypes = [
		ctypes.POINTER(ctypes.c_int),
		ctypes.POINTER(ctypes.c_int),
	]
	lib.QLR_VM_TestMissingQvmAfterNativeFailure.restype = ctypes.c_int
	lib.QLR_VM_TestInterpreterAdd.argtypes = [
		ctypes.POINTER(ctypes.c_int),
		ctypes.POINTER(ctypes.c_int),
		ctypes.POINTER(ctypes.c_int),
		ctypes.POINTER(ctypes.c_int),
	]
	lib.QLR_VM_TestInterpreterAdd.restype = ctypes.c_int
	lib.QLR_VM_TestInterpreterSyscall.argtypes = [
		ctypes.POINTER(ctypes.c_int),
		ctypes.POINTER(ctypes.c_int),
		ctypes.POINTER(ctypes.c_int),
		ctypes.POINTER(ctypes.c_int),
	]
	lib.QLR_VM_TestInterpreterSyscall.restype = ctypes.c_int
	lib.QLR_VM_TestRestartNativeFallback.argtypes = [
		ctypes.POINTER(ctypes.c_int),
		ctypes.POINTER(ctypes.c_int),
		ctypes.POINTER(ctypes.c_int),
		ctypes.POINTER(ctypes.c_int),
		ctypes.POINTER(ctypes.c_int),
	]
	lib.QLR_VM_TestRestartNativeFallback.restype = ctypes.c_int
	lib.QLR_VM_TestArgPtrModes.argtypes = [
		ctypes.POINTER(ctypes.c_ssize_t),
		ctypes.POINTER(ctypes.c_ssize_t),
		ctypes.POINTER(ctypes.c_ssize_t),
	]
	lib.QLR_VM_TestArgPtrModes.restype = ctypes.c_int
	return lib


def _assert_success(lib: ctypes.CDLL, result: int) -> None:
	assert result == 1, lib.QLR_VM_TestLastError().decode("utf-8", errors="replace")


def test_vm_init_defaults_native_modules_by_default(vm_fallback_harness: ctypes.CDLL) -> None:
	vm_cgame = ctypes.c_int()
	vm_game = ctypes.c_int()
	vm_ui = ctypes.c_int()

	_assert_success(
		vm_fallback_harness,
		vm_fallback_harness.QLR_VM_TestInitDefaults(
			ctypes.byref(vm_cgame), ctypes.byref(vm_game), ctypes.byref(vm_ui)
		),
	)

	assert vm_cgame.value == 0
	assert vm_game.value == 0
	assert vm_ui.value == 0


def test_native_failure_falls_back_to_compiled_qvm_and_dispatches_compiled_call(
	vm_fallback_harness: ctypes.CDLL,
) -> None:
	compiled = ctypes.c_int()
	dll_load_calls = ctypes.c_int()
	compile_calls = ctypes.c_int()
	call_result = ctypes.c_int()

	_assert_success(
		vm_fallback_harness,
		vm_fallback_harness.QLR_VM_TestNativeFallbackToCompiled(
			ctypes.byref(compiled),
			ctypes.byref(dll_load_calls),
			ctypes.byref(compile_calls),
			ctypes.byref(call_result),
		),
	)

	log = vm_fallback_harness.QLR_VM_TestCapturedLog().decode("utf-8", errors="replace")

	assert compiled.value == 1
	assert dll_load_calls.value == 1
	assert compile_calls.value == 1
	assert call_result.value == 1042
	assert "Loading dll file testvm." in log
	assert "Failed to load dll, looking for qvm." in log
	assert "Loading vm file vm/testvm.qvm." in log


def test_fs_restrict_forces_compiled_qvm_without_native_load_attempt(
	vm_fallback_harness: ctypes.CDLL,
) -> None:
	compiled = ctypes.c_int()
	dll_load_calls = ctypes.c_int()
	compile_calls = ctypes.c_int()
	call_result = ctypes.c_int()

	_assert_success(
		vm_fallback_harness,
		vm_fallback_harness.QLR_VM_TestRestrictForcesCompiled(
			ctypes.byref(compiled),
			ctypes.byref(dll_load_calls),
			ctypes.byref(compile_calls),
			ctypes.byref(call_result),
		),
	)

	assert compiled.value == 1
	assert dll_load_calls.value == 0
	assert compile_calls.value == 1
	assert call_result.value == 1007


def test_missing_qvm_after_native_failure_returns_null_and_logs_fallback_failure(
	vm_fallback_harness: ctypes.CDLL,
) -> None:
	created = ctypes.c_int()
	dll_load_calls = ctypes.c_int()

	_assert_success(
		vm_fallback_harness,
		vm_fallback_harness.QLR_VM_TestMissingQvmAfterNativeFailure(
			ctypes.byref(created), ctypes.byref(dll_load_calls)
		),
	)

	log = vm_fallback_harness.QLR_VM_TestCapturedLog().decode("utf-8", errors="replace")

	assert created.value == 0
	assert dll_load_calls.value == 1
	assert "Failed to load dll, looking for qvm." in log
	assert "Loading vm file vm/testvm.qvm." in log
	assert "Failed." in log


def test_bytecode_lane_uses_real_interpreter_and_executes_add_program(
	vm_fallback_harness: ctypes.CDLL,
) -> None:
	compiled = ctypes.c_int()
	instruction_pointers_length = ctypes.c_int()
	currently_interpreting = ctypes.c_int()
	call_result = ctypes.c_int()

	_assert_success(
		vm_fallback_harness,
		vm_fallback_harness.QLR_VM_TestInterpreterAdd(
			ctypes.byref(compiled),
			ctypes.byref(instruction_pointers_length),
			ctypes.byref(currently_interpreting),
			ctypes.byref(call_result),
		),
	)

	assert compiled.value == 0
	assert instruction_pointers_length.value == 28
	assert currently_interpreting.value == 0
	assert call_result.value == 42


def test_interpreted_syscall_lane_preserves_contract_logging(
	vm_fallback_harness: ctypes.CDLL,
) -> None:
	call_result = ctypes.c_int()
	system_call_count = ctypes.c_int()
	system_call_arg0 = ctypes.c_int()
	contract_first_arg = ctypes.c_int()

	_assert_success(
		vm_fallback_harness,
		vm_fallback_harness.QLR_VM_TestInterpreterSyscall(
			ctypes.byref(call_result),
			ctypes.byref(system_call_count),
			ctypes.byref(system_call_arg0),
			ctypes.byref(contract_first_arg),
		),
	)

	assert call_result.value == 31337
	assert system_call_count.value == 1
	assert system_call_arg0.value == 5
	assert contract_first_arg.value == 5
	assert vm_fallback_harness.QLR_VM_TestLastSyscallOrigin().decode() == "vm-interpreted"
	assert vm_fallback_harness.QLR_VM_TestLastSyscallModule().decode() == "testvm"


def test_restart_retries_native_then_falls_back_to_compiled_qvm(
	vm_fallback_harness: ctypes.CDLL,
) -> None:
	compiled = ctypes.c_int()
	dll_load_calls = ctypes.c_int()
	dll_unload_calls = ctypes.c_int()
	compile_calls = ctypes.c_int()
	call_result = ctypes.c_int()

	_assert_success(
		vm_fallback_harness,
		vm_fallback_harness.QLR_VM_TestRestartNativeFallback(
			ctypes.byref(compiled),
			ctypes.byref(dll_load_calls),
			ctypes.byref(dll_unload_calls),
			ctypes.byref(compile_calls),
			ctypes.byref(call_result),
		),
	)

	assert compiled.value == 1
	assert dll_load_calls.value == 2
	assert dll_unload_calls.value == 1
	assert compile_calls.value == 1
	assert call_result.value == 1042


def test_vm_arg_ptr_and_explicit_arg_ptr_preserve_native_and_qvm_pointer_modes(
	vm_fallback_harness: ctypes.CDLL,
) -> None:
	masked = ctypes.c_ssize_t()
	entry = ctypes.c_ssize_t()
	dll_interface = ctypes.c_ssize_t()

	_assert_success(
		vm_fallback_harness,
		vm_fallback_harness.QLR_VM_TestArgPtrModes(
			ctypes.byref(masked), ctypes.byref(entry), ctypes.byref(dll_interface)
		),
	)

	assert masked.value == 0x03
	assert entry.value == 0x23
	assert dll_interface.value == 0x23


def test_vm_fallback_sources_bound_host_selection_and_legacy_x86_backend() -> None:
	vm = VM_PATH.read_text(encoding="utf-8")
	vm_interpreted = VM_INTERPRETED_PATH.read_text(encoding="utf-8")
	vm_x86 = VM_X86_PATH.read_text(encoding="utf-8")

	assert 'Cvar_Get( "vm_cgame", "0", CVAR_ARCHIVE );' in vm
	assert 'Cvar_Get( "vm_game", "0", CVAR_ARCHIVE );' in vm
	assert 'Cvar_Get( "vm_ui", "0", CVAR_ARCHIVE );' in vm
	assert 'if ( Cvar_VariableValue( "fs_restrict" ) ) {' in vm
	assert "interpret = VMI_COMPILED;" in vm
	assert 'Com_Printf( "Failed to load dll, looking for qvm.\\n" );' in vm
	assert 'Com_sprintf( filename, sizeof(filename), "vm/%s.qvm", vm->name );' in vm
	assert "vm->compiled = qtrue;" in vm
	assert "VM_Compile( vm, header );" in vm
	assert "vm->compiled = qfalse;" in vm
	assert "VM_PrepareInterpreter( vm, header );" in vm
	assert "vm = VM_Create( name, systemCall, VMI_NATIVE, dllImports, dllApiVersion );" in vm
	assert "return (void *)(currentVM->dataBase + (intValue & currentVM->dataMask));" in vm
	assert "return (void *)(vm->dataBase + (intValue & vm->dataMask));" in vm

	assert 'SyscallContract_LogEvent( "vm-interpreted", vm->name' in vm_interpreted
	assert "vm->currentlyInterpreting = qtrue;" in vm_interpreted
	assert "vm->currentlyInterpreting = qfalse;" in vm_interpreted

	assert "void AsmCall( void );" in vm_x86
	assert "void VM_Compile( vm_t *vm, vmHeader_t *header ) {" in vm_x86
	assert "int\tVM_CallCompiled( vm_t *vm, int *args ) {" in vm_x86
	assert "instructionPointers = vm->instructionPointers;" in vm_x86
	assert "callMask = vm->dataMask;" in vm_x86
