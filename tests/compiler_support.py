from __future__ import annotations

import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


@dataclass(frozen=True, slots=True)
class CCompiler:
	path: str
	command: str
	family: str

	@property
	def is_msvc(self) -> bool:
		return self.family == "msvc"


def _resolve_command(candidate: str | None) -> tuple[str, str] | None:
	if not candidate:
		return None

	resolved = shutil.which(candidate)
	if resolved:
		return resolved, candidate

	path = Path(candidate)
	if path.exists():
		return str(path), candidate

	return None


def find_c_compiler() -> CCompiler | None:
	override_candidates = [
		os.environ.get("QLR_TEST_CC"),
		os.environ.get("QLR_RE_CC"),
		os.environ.get("CC"),
	]
	default_candidates = (
		["clang", "clang-cl", "gcc", "cc", "cl"]
		if os.name == "nt"
		else ["gcc", "clang", "cc"]
	)

	for candidate in override_candidates + default_candidates:
		resolved = _resolve_command(candidate)
		if not resolved:
			continue

		path, command = resolved
		family = "msvc" if os.name == "nt" and Path(command).name.lower() in {"cl", "cl.exe", "clang-cl", "clang-cl.exe"} else "posix"
		return CCompiler(path=path, command=command, family=family)

	return None


def executable_name(stem: str) -> str:
	return stem + (".exe" if os.name == "nt" else "")


def shared_library_name(stem: str) -> str:
	if os.name == "nt":
		return stem + ".dll"
	if sys.platform == "darwin":
		return "lib" + stem + ".dylib"
	return "lib" + stem + ".so"


def compile_c_binary(
	compiler: CCompiler,
	sources: Sequence[Path | str],
	output: Path,
	*,
	include_dirs: Sequence[Path | str] = (),
	defines: Sequence[str] = (),
	extra_cflags: Sequence[str] = (),
	library_dirs: Sequence[Path | str] = (),
	libraries: Sequence[Path | str] = (),
	extra_link_args: Sequence[str] = (),
	shared: bool = False,
	workdir: Path | None = None,
) -> None:
	output.parent.mkdir(parents=True, exist_ok=True)
	effective_defines = list(defines)

	if os.name == "nt":
		for default_define in ("WIN32", "_CRT_SECURE_NO_WARNINGS", "_CRT_NONSTDC_NO_WARNINGS"):
			if default_define not in effective_defines:
				effective_defines.append(default_define)

	if compiler.is_msvc:
		command: list[str] = [compiler.path, "/nologo", "/TC", "/std:c11"]
		if shared:
			command.append("/LD")
		command.extend(extra_cflags)
		command.extend(f"/D{define}" for define in effective_defines)
		command.extend(f"/I{Path(include_dir)}" for include_dir in include_dirs)
		command.extend(str(Path(source)) for source in sources)
		command.append("/link")
		command.append(f"/OUT:{output}")
		command.extend(f"/LIBPATH:{Path(library_dir)}" for library_dir in library_dirs)
		command.extend(str(library) for library in libraries)
		command.extend(extra_link_args)
	else:
		command = [compiler.path, "-std=c99"]
		if shared:
			command.append("-shared")
			if os.name != "nt":
				command.append("-fPIC")
		command.extend(extra_cflags)
		command.extend(f"-D{define}" for define in effective_defines)
		for include_dir in include_dirs:
			command.extend(["-I", str(Path(include_dir))])
		command.extend(str(Path(source)) for source in sources)
		for library_dir in library_dirs:
			command.extend(["-L", str(Path(library_dir))])
		command.extend(str(library) for library in libraries)
		command.extend(extra_link_args)
		command.extend(["-o", str(output)])

	subprocess.run(command, check=True, cwd=workdir)
