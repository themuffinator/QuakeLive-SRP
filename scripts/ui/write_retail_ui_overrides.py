#!/usr/bin/env python3
"""Emit writable retail UI overrides for the read-only src/ui tree."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


if __package__ in (None, ""):
	sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.ui.retail_ui_corpus import (  # noqa: E402
	DEFAULT_BUNDLE_MANIFEST,
	build_retail_ui_inventory,
	compute_ui_panel_drift,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE_ROOT = REPO_ROOT / "src" / "ui"
DEFAULT_RETAIL_ROOT = REPO_ROOT / "assets" / "quakelive" / "baseq3" / "ui"
DEFAULT_HOMEPATH_ROOT = REPO_ROOT / "build" / "ui_retail_overrides"
OVERLAY_PACKAGE_NAME = "pak_ui_src_retail_overlay.pk3"
BASE_UI_PACKAGE_NAME = "pak_uiql.pk3"


def _repo_relative(path: Path) -> str:
	try:
		return path.relative_to(REPO_ROOT).as_posix()
	except ValueError:
		return path.as_posix()


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


def _sha256_bytes(data: bytes) -> str:
	return hashlib.sha256(data).hexdigest()


def _prune_empty_overlay_dirs(homepath_root: Path, start_path: Path) -> list[str]:
	removed_dirs: list[str] = []
	current = start_path

	while current.exists() and current != homepath_root:
		try:
			next(current.iterdir())
			break
		except StopIteration:
			current.rmdir()
			removed_dirs.append(_repo_relative(current))
			current = current.parent

	return removed_dirs


def delete_stale_overrides(
	homepath_root: Path,
	previous_manifest: dict[str, object],
	current_overlay_files: set[str],
) -> dict[str, list[str]]:
	removed_files: list[str] = []
	missing_files: list[str] = []
	removed_dirs: list[str] = []

	for relative_path in previous_manifest.get("overlay_files", []):
		if relative_path in current_overlay_files:
			continue

		target_path = homepath_root / relative_path
		if target_path.exists():
			target_path.unlink()
			removed_files.append(relative_path)
			removed_dirs.extend(_prune_empty_overlay_dirs(homepath_root, target_path.parent))
		else:
			missing_files.append(relative_path)

	return {
		"stale_removed_files": sorted(removed_files),
		"stale_removed_dirs": sorted(set(removed_dirs)),
		"stale_missing_files": sorted(missing_files),
	}


def build_overlay_entries(
	retail_root: Path,
	overlay_files: list[str],
	overlay_prefix: str,
) -> list[dict[str, object]]:
	entries: list[dict[str, object]] = []

	for relative_overlay_path in overlay_files:
		relative_ui_path = relative_overlay_path.removeprefix(f"{overlay_prefix}/")
		source_path = retail_root / relative_ui_path
		file_bytes = source_path.read_bytes()

		entries.append(
			{
				"overlay_path": relative_overlay_path,
				"ui_path": relative_ui_path,
				"retail_source_path": _repo_relative(source_path),
				"size": len(file_bytes),
				"sha256": _sha256_bytes(file_bytes),
			}
		)

	return entries


def build_overlay_policy(overlay_prefix: str) -> dict[str, object]:
	return {
		"mode": "overlay-first-read-only-src-ui",
		"src_ui_baseline": _repo_relative(DEFAULT_SOURCE_ROOT),
		"src_ui_write_policy": "read-only",
		"overlay_mount_root": "fs_homepath/baseq3",
		"overlay_virtual_root": overlay_prefix,
		"overlay_package_name": OVERLAY_PACKAGE_NAME,
		"base_ui_package_name": BASE_UI_PACKAGE_NAME,
		"precedence_contract": (
			"Mount the drift overlay from fs_homepath so it outranks the base UI bundle and "
			"any lower-priority src/ui-derived payloads mounted from fs_basepath or fs_cdpath."
		),
		"verification_contract": (
			"With fs_debug enabled, FS_FOpenFileRead log lines for drifted ui/*.menu or ui/*.txt "
			"targets must report the overlay package as the winning source."
		),
		"same_root_warning": (
			"Do not rely on same-directory pk3 alphabetical ordering to give the overlay precedence; "
			"the supported runtime strategy is a separate fs_homepath overlay layer."
		),
	}


def write_overlay_files(
	retail_root: Path,
	homepath_root: Path,
	overlay_entries: list[dict[str, object]],
) -> None:
	for entry in overlay_entries:
		source_path = retail_root / entry["ui_path"]
		target_path = homepath_root / entry["overlay_path"]
		target_path.parent.mkdir(parents=True, exist_ok=True)
		target_path.write_bytes(source_path.read_bytes())


def main() -> int:
	args = parse_args()
	manifest_path = args.manifest or (args.homepath_root / "ui_retail_overrides.json")
	overlay_prefix = normalize_overlay_prefix(args.overlay_prefix)

	drift = compute_ui_panel_drift(args.source_root, args.retail_root)
	inventory = build_retail_ui_inventory(args.retail_root.parent, DEFAULT_BUNDLE_MANIFEST)
	drift_files = sorted(
		{
			*drift["missing_in_source"],
			*drift["content_diffs"],
		}
	)
	overlay_files = [f"{overlay_prefix}/{relative_path}" for relative_path in drift_files]
	overlay_entries = build_overlay_entries(args.retail_root, overlay_files, overlay_prefix)
	previous_manifest = load_previous_manifest(manifest_path)
	cleanup_report = delete_stale_overrides(args.homepath_root, previous_manifest, set(overlay_files))

	write_overlay_files(args.retail_root, args.homepath_root, overlay_entries)

	report = dict(drift)
	report["manifest_version"] = 2
	report["homepath_root"] = _repo_relative(args.homepath_root)
	report["overlay_root"] = _repo_relative(args.homepath_root / overlay_prefix)
	report["overlay_prefix"] = overlay_prefix
	report["overlay_files"] = overlay_files
	report["drift_files"] = drift_files
	report["overlay_entries"] = overlay_entries
	report["overlay_file_hashes"] = {
		entry["overlay_path"]: entry["sha256"] for entry in overlay_entries
	}
	report["overlay_policy"] = build_overlay_policy(overlay_prefix)
	report.update(cleanup_report)
	report["retail_ui_corpus_available"] = inventory["retail_ui_corpus_available"]
	report["missing_required_inputs"] = inventory["missing_required_inputs"]

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
