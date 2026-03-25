#!/usr/bin/env python3
"""Emit writable retail UI overrides for the read-only src/ui tree."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE_ROOT = REPO_ROOT / "src" / "ui"
DEFAULT_RETAIL_ROOT = REPO_ROOT / "assets" / "quakelive" / "baseq3" / "ui"
DEFAULT_HOMEPATH_ROOT = REPO_ROOT / "build" / "ui_retail_overrides"


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(
		description=(
			"Write retail-correct ui panel overrides into a writable fs_homepath-style "
			"overlay without editing the read-only src/ui tree."
		)
	)
	parser.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
	parser.add_argument("--retail-root", type=Path, default=DEFAULT_RETAIL_ROOT)
	parser.add_argument("--homepath-root", type=Path, default=DEFAULT_HOMEPATH_ROOT)
	parser.add_argument("--manifest", type=Path, default=None)
	parser.add_argument("--overlay-prefix", default="baseq3/ui")
	return parser.parse_args()


def collect_files(root: Path) -> set[str]:
	return {
		str(path.relative_to(root)).replace("\\", "/")
		for path in root.rglob("*")
		if path.is_file()
	}


def compute_drift(source_root: Path, retail_root: Path) -> dict[str, object]:
	source_files = collect_files(source_root)
	retail_files = collect_files(retail_root)
	common_files = sorted(source_files & retail_files)
	content_diffs = [
		relative_path
		for relative_path in common_files
		if (source_root / relative_path).read_bytes() != (retail_root / relative_path).read_bytes()
	]

	return {
		"source_root": str(source_root),
		"retail_root": str(retail_root),
		"source_file_count": len(source_files),
		"retail_file_count": len(retail_files),
		"missing_in_source": sorted(retail_files - source_files),
		"extra_in_source": sorted(source_files - retail_files),
		"content_diffs": content_diffs,
	}


def load_previous_manifest(manifest_path: Path) -> dict[str, object]:
	if not manifest_path.exists():
		return {}

	try:
		return json.loads(manifest_path.read_text(encoding="utf-8"))
	except json.JSONDecodeError:
		return {}


def normalize_overlay_prefix(prefix: str) -> str:
	normalized = prefix.replace("\\", "/").strip("/")

	if not normalized or ".." in normalized.split("/"):
		raise ValueError(f"Invalid overlay prefix: {prefix!r}")

	return normalized


def delete_stale_overrides(homepath_root: Path, previous_manifest: dict[str, object], current_overlay_files: set[str]) -> None:
	for relative_path in previous_manifest.get("overlay_files", []):
		if relative_path in current_overlay_files:
			continue

		target_path = homepath_root / relative_path
		if target_path.exists():
			target_path.unlink()


def write_overrides(
	retail_root: Path,
	homepath_root: Path,
	drift: dict[str, object],
	manifest_path: Path,
	overlay_prefix: str,
) -> dict[str, object]:
	overlay_files = sorted(
		{
			f"{overlay_prefix}/{relative_path}"
			for relative_path in [
				*drift["missing_in_source"],
				*drift["content_diffs"],
			]
		}
	)
	overlay_file_set = set(overlay_files)
	previous_manifest = load_previous_manifest(manifest_path)

	delete_stale_overrides(homepath_root, previous_manifest, overlay_file_set)

	for relative_overlay_path in overlay_files:
		relative_ui_path = relative_overlay_path.removeprefix(f"{overlay_prefix}/")
		source_path = retail_root / relative_ui_path
		target_path = homepath_root / relative_overlay_path
		target_path.parent.mkdir(parents=True, exist_ok=True)
		target_path.write_bytes(source_path.read_bytes())

	report = dict(drift)
	report["homepath_root"] = str(homepath_root)
	report["overlay_prefix"] = overlay_prefix
	report["overlay_files"] = overlay_files
	return report


def main() -> int:
	args = parse_args()
	manifest_path = args.manifest or (args.homepath_root / "ui_retail_overrides.json")
	overlay_prefix = normalize_overlay_prefix(args.overlay_prefix)

	drift = compute_drift(args.source_root, args.retail_root)
	report = write_overrides(args.retail_root, args.homepath_root, drift, manifest_path, overlay_prefix)

	manifest_path.parent.mkdir(parents=True, exist_ok=True)
	manifest_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

	print(
		f"Wrote {len(report['overlay_files'])} retail ui overrides to "
		f"{(args.homepath_root / overlay_prefix).as_posix()}"
	)
	print(f"Manifest written to {manifest_path.as_posix()}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
