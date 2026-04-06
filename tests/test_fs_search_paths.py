"""Filesystem search path regression tests for FS_FOpenFileRead."""
from __future__ import annotations

import ctypes
import shutil
import subprocess
import zipfile
from pathlib import Path
from typing import Iterator, Tuple

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def fs_harness(tmp_path_factory: pytest.TempPathFactory) -> ctypes.CDLL:
    build_dir = tmp_path_factory.mktemp("fs_harness_build")
    lib_path = build_dir / "libfs_harness.so"
    compiler = shutil.which("gcc")

    if compiler is None:
        pytest.skip("gcc is not available for the filesystem search-path harness")

    compile_cmd = [
        compiler,
        "-shared",
        "-fPIC",
        "-Isrc/code",
        "-Isrc/code/qcommon",
        "-Isrc/code/game",
        "-Isrc/code/client",
        "-Isrc/code/server",
        "-Isrc/code/botlib",
        str(REPO_ROOT / "tests" / "fs_searchpath_harness.c"),
        str(REPO_ROOT / "src" / "code" / "qcommon" / "unzip.c"),
        "-lz",
        "-o",
        str(lib_path),
    ]
    subprocess.check_call(compile_cmd, cwd=REPO_ROOT)

    lib = ctypes.CDLL(str(lib_path))
    lib.QLR_FS_TestInitCvars.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    lib.QLR_FS_TestShutdown.argtypes = []
    lib.QLR_FS_TestAddGameDirectory.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    lib.QLR_FS_TestSetRestrict.argtypes = [ctypes.c_int]
    lib.QLR_FS_TestSetDebug.argtypes = [ctypes.c_int]
    lib.QLR_FS_TestLoadedPakNames.argtypes = []
    lib.QLR_FS_TestLoadedPakNames.restype = ctypes.c_char_p
    lib.QLR_FS_TestReadFile.argtypes = [
        ctypes.c_char_p,
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_size_t),
    ]
    lib.QLR_FS_TestReadFile.restype = ctypes.c_int
    return lib


@pytest.fixture()
def fs_environment(tmp_path: Path, fs_harness: ctypes.CDLL) -> Iterator[Tuple[ctypes.CDLL, Path, Path]]:
    basepath = tmp_path / "base"
    homepath = tmp_path / "home"
    (basepath / "baseq3").mkdir(parents=True)
    (homepath / "baseq3").mkdir(parents=True)

    fs_harness.QLR_FS_TestInitCvars(
        str(basepath).encode(), str(homepath).encode()
    )
    fs_harness.QLR_FS_TestSetRestrict(0)
    yield fs_harness, basepath, homepath
    fs_harness.QLR_FS_TestShutdown()


def _write_pk3(root: Path, relative: str, content: str) -> None:
    pak_path = root / "baseq3" / "pak_test.pk3"
    with zipfile.ZipFile(pak_path, "w") as archive:
        archive.writestr(relative, content)


def _write_named_pk3(root: Path, pak_name: str, relative: str, content: str) -> None:
    pak_path = root / "baseq3" / pak_name
    with zipfile.ZipFile(pak_path, "w") as archive:
        archive.writestr(relative, content)


def _write_dir(root: Path, relative: str, content: str) -> Path:
    dest = root / "baseq3" / relative
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8")
    return dest


def _read_file(
    lib: ctypes.CDLL, filename: str, unique: bool = False
) -> Tuple[int, str, int]:
    buffer = ctypes.create_string_buffer(256)
    handle = ctypes.c_size_t()
    length = lib.QLR_FS_TestReadFile(
        filename.encode(), int(unique), buffer, ctypes.sizeof(buffer), ctypes.byref(handle)
    )
    return length, buffer.value.decode(), handle.value


def test_pk3_precedence_over_directory(fs_environment: Tuple[ctypes.CDLL, Path, Path]) -> None:
    lib, basepath, _ = fs_environment

    _write_dir(basepath, "ui/test.menu", "directory-version")
    _write_pk3(basepath, "ui/test.menu", "pak-version")

    lib.QLR_FS_TestAddGameDirectory(str(basepath).encode(), b"baseq3")

    length, content, _ = _read_file(lib, "ui/test.menu")

    assert length == len("pak-version")
    assert content == "pak-version"


def test_restrict_mode_prefers_pak_and_skips_directory(
    fs_environment: Tuple[ctypes.CDLL, Path, Path]
) -> None:
    lib, basepath, _ = fs_environment

    _write_dir(basepath, "ui/restrict.menu", "from-directory")
    _write_pk3(basepath, "ui/restrict.menu", "from-pak")

    lib.QLR_FS_TestSetRestrict(1)
    lib.QLR_FS_TestAddGameDirectory(str(basepath).encode(), b"baseq3")

    length, content, _ = _read_file(lib, "ui/restrict.menu")

    assert length == len("from-pak")
    assert content == "from-pak"


def test_unique_file_reopens_zip_handle(fs_environment: Tuple[ctypes.CDLL, Path, Path]) -> None:
    lib, basepath, _ = fs_environment

    _write_pk3(basepath, "ui/unique.menu", "unique")
    lib.QLR_FS_TestAddGameDirectory(str(basepath).encode(), b"baseq3")

    first_len, first_content, shared_handle = _read_file(lib, "ui/unique.menu", unique=False)
    second_len, second_content, unique_handle = _read_file(lib, "ui/unique.menu", unique=True)

    assert first_len == len("unique")
    assert second_len == len("unique")
    assert first_content == "unique"
    assert second_content == "unique"
    assert shared_handle != 0
    assert unique_handle != 0
    assert shared_handle != unique_handle


def test_homepath_overlay_pk3_precedes_base_bundle_and_logs_source(
    fs_environment: Tuple[ctypes.CDLL, Path, Path],
    capfd: pytest.CaptureFixture[str],
) -> None:
    lib, basepath, homepath = fs_environment

    _write_named_pk3(basepath, "pak_uiql.pk3", "ui/hud.txt", "base-bundle")
    _write_named_pk3(homepath, "pak_ui_src_retail_overlay.pk3", "ui/hud.txt", "overlay-bundle")

    lib.QLR_FS_TestSetDebug(1)
    lib.QLR_FS_TestAddGameDirectory(str(basepath).encode(), b"baseq3")
    lib.QLR_FS_TestAddGameDirectory(str(homepath).encode(), b"baseq3")

    loaded_paks = lib.QLR_FS_TestLoadedPakNames().decode()
    assert loaded_paks.split()[:2] == ["pak_ui_src_retail_overlay", "pak_uiql"]

    capfd.readouterr()
    length, content, _ = _read_file(lib, "ui/hud.txt")
    captured = capfd.readouterr().out

    assert length == len("overlay-bundle")
    assert content == "overlay-bundle"
    assert "FS_FOpenFileRead: ui/hud.txt" in captured
    assert str(homepath / "baseq3" / "pak_ui_src_retail_overlay.pk3") in captured

