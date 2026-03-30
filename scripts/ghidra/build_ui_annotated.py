#!/usr/bin/env python3
"""Re-derive references/reverse-engineering/ghidra/uix86/decompile_annotated.c.

Reads the committed Ghidra decompile (decompile_top_functions.c) and the
ui.json symbol map, substitutes every raw FUN_XXXXXXXX token with its
normalized name from the map, and writes the result to decompile_annotated.c
in the same directory.

Usage::

    python3 scripts/ghidra/build_ui_annotated.py [--repo-root <path>]

This is a pure-Python offline tool — no Ghidra installation required.
Run it whenever decompile_top_functions.c or ui.json is updated.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


_FILE_HEADER = """\
/*
 * Quake Live UI Module — annotated Ghidra decompile
 *
 * Binary  : uix86.dll
 * Source  : decompile_top_functions.c with function names substituted
 *           from references/symbol-maps/ui.json
 *
 * Functions decompiled: top {count} by body size
 * Symbol map coverage : {matched} / {unique} FUN_ tokens resolved
 *
 * Do NOT edit by hand — re-derive by running:
 *   python3 scripts/ghidra/build_ui_annotated.py
 */"""

_BANNER_PATTERN = re.compile(
	r"/\*\s*\nProgram: uix86\.dll\nFunctions decompiled: top \d+ by body size\s*\n\*/"
)

_FUN_TOKEN = re.compile(r"FUN_[0-9a-fA-F]{8}")

_BLOCK_HEADER = re.compile(r"^/\* FUN_[0-9a-fA-F]{8} @", re.MULTILINE)


def build_addr_map(functions: list[dict]) -> dict[str, str]:
	"""Return mapping of ``FUN_XXXXXXXX`` token → normalized_name."""
	result: dict[str, str] = {}
	for fn in functions:
		addr: str = fn.get("address", "")
		name: str = fn.get("normalized_name", "")
		if not addr or not name:
			continue
		hex_part = addr.lower()
		if hex_part.startswith("0x"):
			hex_part = hex_part[2:]
		token = "FUN_%s" % hex_part
		result[token] = name
	return result


def annotate(content: str, addr_map: dict[str, str]) -> tuple[str, int, int]:
	"""Replace FUN_ tokens in *content*; return (annotated, matched, unique)."""
	unique_tokens: set[str] = set(_FUN_TOKEN.findall(content))
	matched = sum(1 for t in unique_tokens if t in addr_map)

	def _replace(m: re.Match) -> str:
		return addr_map.get(m.group(0), m.group(0))

	annotated = _FUN_TOKEN.sub(_replace, content)
	return annotated, matched, len(unique_tokens)


def count_decompile_blocks(content: str) -> int:
	return len(_BLOCK_HEADER.findall(content))


def main(argv: list[str] | None = None) -> int:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument(
		"--repo-root",
		type=Path,
		default=Path(__file__).resolve().parents[2],
		help="Path to repository root (default: two levels above this script)",
	)
	args = parser.parse_args(argv)
	repo_root: Path = args.repo_root.resolve()

	map_path = repo_root / "references" / "symbol-maps" / "ui.json"
	src_path = repo_root / "references" / "reverse-engineering" / "ghidra" / "uix86" / "decompile_top_functions.c"
	out_path = repo_root / "references" / "reverse-engineering" / "ghidra" / "uix86" / "decompile_annotated.c"

	if not map_path.is_file():
		print(f"ERROR: symbol map not found: {map_path}", file=sys.stderr)
		return 1
	if not src_path.is_file():
		print(f"ERROR: decompile source not found: {src_path}", file=sys.stderr)
		return 1

	with map_path.open() as fh:
		manifest = json.load(fh)
	functions: list[dict] = manifest.get("functions", [])
	addr_map = build_addr_map(functions)
	print(f"Symbol map: {len(addr_map)} entries from {map_path.name}")

	content = src_path.read_text(encoding="utf-8")
	block_count = count_decompile_blocks(content)
	annotated, matched, unique = annotate(content, addr_map)

	# Replace the raw file header with an annotated one.
	new_header = _FILE_HEADER.format(
		count=block_count,
		matched=matched,
		unique=unique,
	)
	annotated = _BANNER_PATTERN.sub(new_header, annotated, count=1)

	out_path.write_text(annotated, encoding="utf-8")
	remaining = len(re.findall(r"\bFUN_[0-9a-fA-F]{8}\b", annotated))
	print(
		f"Written: {out_path}\n"
		f"  blocks={block_count}  matched={matched}/{unique} FUN_ tokens"
		f"  remaining_unresolved={remaining}"
	)
	return 0


if __name__ == "__main__":
	sys.exit(main())
