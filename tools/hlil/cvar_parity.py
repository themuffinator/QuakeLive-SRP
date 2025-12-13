"""HLIL-derived cvar/dvar registration parity check utilities."""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
HLIL_ROOT = REPO_ROOT / "references" / "hlil" / "quakelive"
SOURCE_DIRS: Sequence[Path] = (
    REPO_ROOT / "src" / "code" / "game",
    REPO_ROOT / "src" / "code" / "cgame",
    REPO_ROOT / "src" / "code" / "ui",
    REPO_ROOT / "src" / "code" / "client",
    REPO_ROOT / "src" / "code" / "server",
    REPO_ROOT / "src" / "code" / "renderer",
)

REGISTER_PATTERN = re.compile(
    r'''(?P<func>(?:C|D)var_Register\w*)\s*\(\s*"(?P<name>[^"]+)"\s*,\s*"(?P<default>[^"]*)"\s*,\s*(?P<flags>[^)\n]+?)\s*\)''',
    re.IGNORECASE | re.DOTALL,
)

REGISTER_WITH_HANDLE_PATTERN = re.compile(
    r'''(?P<func>(?:C|D)var_Register\w*)\s*\(\s*[^,]+,\s*"(?P<name>[^"]+)"\s*,\s*"(?P<default>[^"]*)"\s*,\s*(?P<flags>[^)\n]+?)\s*\)''',
    re.IGNORECASE | re.DOTALL,
)


@dataclass
class Registration:
    name: str
    default: str
    flags: str
    source: Path

    def normalized_flags(self) -> str:
        cleaned = self.flags.strip().strip("()")
        parts = [part.strip() for part in cleaned.replace("||", "|").split("|") if part.strip()]
        if not parts:
            return "0"
        parts.sort()
        return "|".join(parts)


def _extract_from_text(text: str, source: Path) -> List[Registration]:
    matches = list(REGISTER_PATTERN.finditer(text)) + list(REGISTER_WITH_HANDLE_PATTERN.finditer(text))
    registrations: List[Registration] = []
    for match in matches:
        name = match.group("name")
        default = match.group("default")
        flags = match.group("flags")
        registrations.append(Registration(name=name, default=default, flags=flags, source=source))
    return registrations


def extract_hlil_registrations(root: Path = HLIL_ROOT) -> List[Registration]:
    registrations: List[Registration] = []
    for path in root.rglob("*.txt"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        registrations.extend(_extract_from_text(text, path))
    for path in root.rglob("*.md"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        registrations.extend(_extract_from_text(text, path))
    return registrations


def extract_source_registrations(source_dirs: Iterable[Path] = SOURCE_DIRS) -> List[Registration]:
    registrations: List[Registration] = []
    for base_dir in source_dirs:
        if not base_dir.exists():
            continue
        for path in base_dir.rglob("*.c"):
            text = path.read_text(encoding="utf-8", errors="ignore")
            registrations.extend(_extract_from_text(text, path))
        for path in base_dir.rglob("*.cpp"):
            text = path.read_text(encoding="utf-8", errors="ignore")
            registrations.extend(_extract_from_text(text, path))
    return registrations


def _index_by_name(entries: Iterable[Registration]) -> Dict[str, Registration]:
    indexed: Dict[str, Registration] = {}
    for entry in entries:
        if entry.name not in indexed:
            indexed[entry.name] = entry
    return indexed


def compare_registrations(
    hlil_entries: Iterable[Registration], source_entries: Iterable[Registration]
) -> Dict[str, Dict[str, Registration]]:
    hlil_map = _index_by_name(hlil_entries)
    source_map = _index_by_name(source_entries)

    missing_in_source: Dict[str, Registration] = {}
    extra_in_source: Dict[str, Registration] = {}
    mismatched_defaults: Dict[str, Registration] = {}
    mismatched_flags: Dict[str, Registration] = {}

    for name, registration in hlil_map.items():
        if name not in source_map:
            missing_in_source[name] = registration
            continue
        source_registration = source_map[name]
        if registration.default != source_registration.default:
            mismatched_defaults[name] = registration
        if registration.normalized_flags() != source_registration.normalized_flags():
            mismatched_flags[name] = registration

    for name, registration in source_map.items():
        if name not in hlil_map:
            extra_in_source[name] = registration

    return {
        "missing_in_source": missing_in_source,
        "extra_in_source": extra_in_source,
        "mismatched_defaults": mismatched_defaults,
        "mismatched_flags": mismatched_flags,
    }


def _serialize_report(report: Dict[str, Dict[str, Registration]]) -> Dict[str, Dict[str, str]]:
    def _serialize(entries: Dict[str, Registration]) -> Dict[str, str]:
        return {name: f"{entry.default} [{entry.flags}] ({entry.source})" for name, entry in entries.items()}

    return {key: _serialize(value) for key, value in report.items()}


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare HLIL cvar/dvar registrations against source.")
    parser.add_argument("--hlil-root", type=Path, default=HLIL_ROOT, help="Root of HLIL reference tree.")
    parser.add_argument("--output", type=Path, help="Optional path to emit JSON report.")
    args = parser.parse_args()

    hlil = extract_hlil_registrations(args.hlil_root)
    source = extract_source_registrations()
    report = compare_registrations(hlil, source)
    has_diff = any(report.values())

    if args.output:
        args.output.write_text(json.dumps(_serialize_report(report), indent=2))

    if has_diff:
        print(json.dumps(_serialize_report(report), indent=2))
        return 1

    print("HLIL cvar/dvar registration parity check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
