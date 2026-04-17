from __future__ import annotations

import ctypes
import os
import re
from pathlib import Path

import pytest

from tests.compiler_support import compile_c_binary, find_c_compiler, shared_library_name

REPO_ROOT = Path(__file__).resolve().parent.parent
WIN_INPUT = REPO_ROOT / "src" / "code" / "win32" / "win_input.c"
WIN_MAIN = REPO_ROOT / "src" / "code" / "win32" / "win_main.c"
WIN_WNDPROC = REPO_ROOT / "src" / "code" / "win32" / "win_wndproc.c"

RIDEV_REMOVE = 0x00000001

RI_MOUSE_BUTTON_1_DOWN = 0x0001
RI_MOUSE_BUTTON_1_UP = 0x0002
RI_MOUSE_BUTTON_2_DOWN = 0x0004
RI_MOUSE_BUTTON_4_DOWN = 0x0040
RI_MOUSE_BUTTON_5_UP = 0x0200
RI_MOUSE_WHEEL = 0x0400
WHEEL_DELTA = 120

# Retail command-owner evidence for this console-facing raw-input slice comes
# from `references/analysis/quakelive_symbol_aliases.json` plus the paired HLIL
# owner in `references/hlil/quakelive/quakelive_steam.exe/`:
# `sub_4EAB90` -> `ListInputDevices_f`
# `sub_4ED3E0` -> `Sys_In_Restart_f`


class RawInputDevice(ctypes.Structure):
	_fields_ = [
		("usUsagePage", ctypes.c_ushort),
		("usUsage", ctypes.c_ushort),
		("dwFlags", ctypes.c_ulong),
		("hwndTarget", ctypes.c_void_p),
	]


class RawMouseSample(ctypes.Structure):
	_fields_ = [
		("dx", ctypes.c_long),
		("dy", ctypes.c_long),
		("buttonFlags", ctypes.c_ushort),
		("wheelDelta", ctypes.c_short),
	]


def _extract_function_block(text: str, signature: str) -> str:
	start = text.find(signature)
	if start == -1:
		raise AssertionError(f"function signature not found: {signature}")

	brace_start = text.find("{", start)
	if brace_start == -1:
		raise AssertionError(f"opening brace not found for: {signature}")

	depth = 0
	for index in range(brace_start, len(text)):
		char = text[index]
		if char == "{":
			depth += 1
		elif char == "}":
			depth -= 1
			if depth == 0:
				return text[start : index + 1]

	raise AssertionError(f"unterminated function block for: {signature}")


@pytest.fixture(scope="session")
def win_raw_input_harness(tmp_path_factory: pytest.TempPathFactory) -> ctypes.CDLL:
	if os.name != "nt":
		pytest.skip("Win32 raw-input harness only applies on Windows")

	build_dir = tmp_path_factory.mktemp("win_raw_input_harness_build")
	lib_path = build_dir / shared_library_name("win_raw_input_harness")
	compiler = find_c_compiler()

	if compiler is None:
		pytest.skip("no supported C compiler is available for the Win32 raw-input harness")

	compile_c_binary(
		compiler,
		[
			REPO_ROOT / "tests" / "win_raw_input_harness.c",
		],
		lib_path,
		include_dirs=[
			REPO_ROOT / "src" / "code" / "win32",
		],
		shared=True,
		workdir=REPO_ROOT,
	)

	lib = ctypes.CDLL(str(lib_path))
	lib.QLR_WinRawInputBuildRegistration.argtypes = [
		ctypes.POINTER(RawInputDevice),
		ctypes.c_void_p,
		ctypes.c_int,
		ctypes.c_int,
	]
	lib.QLR_WinRawInputBuildRegistration.restype = None
	lib.QLR_WinRawInputExtractMouseSampleFromFields.argtypes = [
		ctypes.c_long,
		ctypes.c_long,
		ctypes.c_ushort,
		ctypes.c_ushort,
		ctypes.POINTER(RawMouseSample),
	]
	lib.QLR_WinRawInputExtractMouseSampleFromFields.restype = ctypes.c_int
	lib.QLR_WinRawInputTranslateButtonFlags.argtypes = [
		ctypes.c_ushort,
		ctypes.c_short,
		ctypes.POINTER(ctypes.c_int),
		ctypes.POINTER(ctypes.c_int),
		ctypes.c_int,
	]
	lib.QLR_WinRawInputTranslateButtonFlags.restype = ctypes.c_int
	lib.QLR_WinRawInputKeyMouse1.argtypes = []
	lib.QLR_WinRawInputKeyMouse1.restype = ctypes.c_int
	lib.QLR_WinRawInputKeyWheelDown.argtypes = []
	lib.QLR_WinRawInputKeyWheelDown.restype = ctypes.c_int
	lib.QLR_WinRawInputKeyWheelUp.argtypes = []
	lib.QLR_WinRawInputKeyWheelUp.restype = ctypes.c_int
	return lib


def test_raw_input_registration_defaults_to_mouse_usage_page_and_null_target(
	win_raw_input_harness: ctypes.CDLL,
) -> None:
	device = RawInputDevice()

	win_raw_input_harness.QLR_WinRawInputBuildRegistration(
		ctypes.byref(device),
		ctypes.c_void_p(0x1234),
		0,
		0,
	)

	assert device.usUsagePage == 1
	assert device.usUsage == 2
	assert device.dwFlags == 0
	assert not device.hwndTarget


def test_raw_input_registration_can_bind_the_window_handle(
	win_raw_input_harness: ctypes.CDLL,
) -> None:
	device = RawInputDevice()

	win_raw_input_harness.QLR_WinRawInputBuildRegistration(
		ctypes.byref(device),
		ctypes.c_void_p(0x1234),
		1,
		0,
	)

	assert device.usUsagePage == 1
	assert device.usUsage == 2
	assert device.dwFlags == 0
	assert device.hwndTarget == 0x1234


def test_raw_input_removal_uses_ridev_remove_and_clears_the_target(
	win_raw_input_harness: ctypes.CDLL,
) -> None:
	device = RawInputDevice()

	win_raw_input_harness.QLR_WinRawInputBuildRegistration(
		ctypes.byref(device),
		ctypes.c_void_p(0x1234),
		1,
		1,
	)

	assert device.usUsagePage == 1
	assert device.usUsage == 2
	assert device.dwFlags == RIDEV_REMOVE
	assert not device.hwndTarget


def test_raw_input_mouse_sample_extraction_matches_synthetic_rawinput_fields(
	win_raw_input_harness: ctypes.CDLL,
) -> None:
	sample = RawMouseSample()
	result = win_raw_input_harness.QLR_WinRawInputExtractMouseSampleFromFields(
		21,
		-13,
		RI_MOUSE_BUTTON_1_DOWN | RI_MOUSE_WHEEL,
		WHEEL_DELTA,
		ctypes.byref(sample),
	)

	assert result == 1
	assert sample.dx == 21
	assert sample.dy == -13
	assert sample.buttonFlags == (RI_MOUSE_BUTTON_1_DOWN | RI_MOUSE_WHEEL)
	assert sample.wheelDelta == WHEEL_DELTA


def test_raw_input_button_translation_emits_buttons_and_positive_wheel_events(
	win_raw_input_harness: ctypes.CDLL,
) -> None:
	keys = (ctypes.c_int * 12)()
	down = (ctypes.c_int * 12)()
	mouse1 = win_raw_input_harness.QLR_WinRawInputKeyMouse1()
	wheel_up = win_raw_input_harness.QLR_WinRawInputKeyWheelUp()

	count = win_raw_input_harness.QLR_WinRawInputTranslateButtonFlags(
		RI_MOUSE_BUTTON_1_DOWN | RI_MOUSE_BUTTON_1_UP | RI_MOUSE_BUTTON_4_DOWN | RI_MOUSE_BUTTON_5_UP | RI_MOUSE_WHEEL,
		WHEEL_DELTA,
		keys,
		down,
		12,
	)

	assert count == 6
	assert list(keys)[:count] == [mouse1, mouse1, mouse1 + 3, mouse1 + 4, wheel_up, wheel_up]
	assert list(down)[:count] == [1, 0, 1, 0, 1, 0]


def test_raw_input_button_translation_emits_negative_wheel_events(
	win_raw_input_harness: ctypes.CDLL,
) -> None:
	keys = (ctypes.c_int * 12)()
	down = (ctypes.c_int * 12)()
	mouse1 = win_raw_input_harness.QLR_WinRawInputKeyMouse1()
	wheel_down = win_raw_input_harness.QLR_WinRawInputKeyWheelDown()

	count = win_raw_input_harness.QLR_WinRawInputTranslateButtonFlags(
		RI_MOUSE_BUTTON_2_DOWN | RI_MOUSE_WHEEL,
		-WHEEL_DELTA,
		keys,
		down,
		12,
	)

	assert count == 3
	assert list(keys)[:count] == [mouse1 + 1, wheel_down, wheel_down]
	assert list(down)[:count] == [1, 1, 0]


def test_win32_raw_input_source_registers_cvars_and_raw_fallback_lane() -> None:
	source = WIN_INPUT.read_text(encoding="utf-8")
	init_block = _extract_function_block(source, "void IN_Init( void ) {")
	shutdown_block = _extract_function_block(source, "void IN_Shutdown( void ) {")
	startup_block = _extract_function_block(source, "void IN_StartupMouse( void )")

	assert re.search(r'in_mouse\s*=\s*Cvar_Get\s*\(\s*"in_mouse"\s*,\s*"2"', init_block)
	assert 'Cvar_Get ("in_mouseMode"' in init_block
	assert 'Cvar_Get ("in_debugMouse"' in init_block
	assert 'Cvar_Get ("in_nograb"' in init_block
	assert 'Cvar_Get ("in_raw_useWindowHandle"' in init_block
	assert 'Cmd_AddCommand( "ListInputDevices", ListInputDevices_f );' in init_block
	assert 'Cmd_RemoveCommand("ListInputDevices" );' in shutdown_block

	assert "IN_InitRawInput()" in startup_block
	assert 'Com_Printf( "Falling back on raw input...\\n" );' in startup_block
	assert 'Cvar_Set( "in_mouse", "2" );' in startup_block


def test_win32_raw_input_source_includes_device_listing_and_wm_input_dispatch() -> None:
	win_input = WIN_INPUT.read_text(encoding="utf-8")
	win_wndproc = WIN_WNDPROC.read_text(encoding="utf-8")
	list_block = _extract_function_block(win_input, "static void ListInputDevices_f( void )\n{")
	main_wndproc = _extract_function_block(win_wndproc, "LONG WINAPI MainWndProc (")

	assert "ListInputDevices is only supported for Raw Input (in_mouse 2).\\n" in list_block
	assert "GetRawInputDeviceList" in list_block
	assert "GetRawInputDeviceInfoA" in list_block
	assert "Raw Input Mouse Devices: \\n" in list_block

	assert "case WM_INPUT:" in main_wndproc
	assert "IN_RawInputEvent( wParam, lParam );" in main_wndproc
	assert "IN_RawInputIsActive()" in main_wndproc


def test_win32_input_restart_command_matches_retail_registration_and_handler() -> None:
	win_main = WIN_MAIN.read_text(encoding="utf-8")

	sys_init_block = _extract_function_block(win_main, "void Sys_Init( void ) {")
	restart_block = _extract_function_block(win_main, "void Sys_In_Restart_f( void ) {")

	assert 'Cmd_AddCommand ("in_restart", Sys_In_Restart_f);' in sys_init_block
	assert "IN_Shutdown();" in restart_block
	assert "IN_Init();" in restart_block
