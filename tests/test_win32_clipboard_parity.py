from __future__ import annotations

import ctypes
import os
from pathlib import Path

import pytest

from tests.compiler_support import compile_c_binary, find_c_compiler, shared_library_name

REPO_ROOT = Path(__file__).resolve().parent.parent
WIN_MAIN = REPO_ROOT / "src" / "code" / "win32" / "win_main.c"
CL_KEYS = REPO_ROOT / "src" / "code" / "client" / "cl_keys.c"
CL_UI = REPO_ROOT / "src" / "code" / "client" / "cl_ui.c"


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
def win_clipboard_harness(tmp_path_factory: pytest.TempPathFactory) -> ctypes.CDLL:
	if os.name != "nt":
		pytest.skip("Win32 clipboard harness only applies on Windows")

	build_dir = tmp_path_factory.mktemp("win_clipboard_harness_build")
	lib_path = build_dir / shared_library_name("win_clipboard_harness")
	compiler = find_c_compiler()

	if compiler is None:
		pytest.skip("no supported C compiler is available for the Win32 clipboard harness")

	compile_c_binary(
		compiler,
		[
			REPO_ROOT / "tests" / "win_clipboard_harness.c",
		],
		lib_path,
		include_dirs=[
			REPO_ROOT / "src" / "code" / "win32",
		],
		shared=True,
		workdir=REPO_ROOT,
	)

	lib = ctypes.CDLL(str(lib_path))
	lib.QLR_WinClipboardWideToUtf8ByteCount.argtypes = [ctypes.c_wchar_p]
	lib.QLR_WinClipboardWideToUtf8ByteCount.restype = ctypes.c_int
	lib.QLR_WinClipboardWideToUtf8.argtypes = [ctypes.c_wchar_p, ctypes.POINTER(ctypes.c_char), ctypes.c_int]
	lib.QLR_WinClipboardWideToUtf8.restype = ctypes.c_int
	lib.QLR_WinClipboardTrimText.argtypes = [ctypes.POINTER(ctypes.c_char)]
	lib.QLR_WinClipboardTrimText.restype = None
	return lib


def _convert_utf16_text(lib: ctypes.CDLL, text: str) -> ctypes.Array[ctypes.c_char]:
	required = lib.QLR_WinClipboardWideToUtf8ByteCount(text)
	assert required > 0

	buffer = (ctypes.c_char * required)()
	written = lib.QLR_WinClipboardWideToUtf8(text, buffer, required)
	assert written == required
	return buffer


def test_shared_win32_clipboard_helper_converts_utf16_to_utf8_bytes(
	win_clipboard_harness: ctypes.CDLL,
) -> None:
	buffer = _convert_utf16_text(win_clipboard_harness, "Cafe EUR: \u20ac snow: \u2603")

	assert ctypes.string_at(buffer).decode("utf-8") == "Cafe EUR: \u20ac snow: \u2603"


@pytest.mark.parametrize(
	("text", "expected"),
	[
		("trim at newline\r\nignored", "trim at newline"),
		("trim at backspace\bignored", "trim at backspace"),
	],
)
def test_shared_win32_clipboard_helper_trims_control_characters_after_conversion(
	win_clipboard_harness: ctypes.CDLL,
	text: str,
	expected: str,
) -> None:
	buffer = _convert_utf16_text(win_clipboard_harness, text)

	win_clipboard_harness.QLR_WinClipboardTrimText(buffer)

	assert ctypes.string_at(buffer).decode("utf-8") == expected


def test_win32_clipboard_path_prefers_unicode_and_keeps_ansi_fallback() -> None:
	source = WIN_MAIN.read_text(encoding="utf-8")
	block = _extract_function_block(source, "char *Sys_GetClipboardData( void ) {")

	assert "GetClipboardData( CF_UNICODETEXT )" in block
	assert "Sys_CloneClipboardUnicodeText( cliptext )" in block
	assert "GetClipboardData( CF_TEXT )" in block
	assert "Sys_CloneClipboardText( cliptext )" in block


def test_clipboard_consumers_still_flow_through_the_host_utf8_helper() -> None:
	cl_keys = CL_KEYS.read_text(encoding="utf-8")
	cl_ui = CL_UI.read_text(encoding="utf-8")

	assert "cbd = Sys_GetClipboardData();" in cl_keys
	assert "cbd = Sys_GetClipboardData();" in cl_ui
