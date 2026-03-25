from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE_ROOT = REPO_ROOT / "src" / "ui"
RETAIL_ROOT = REPO_ROOT / "assets" / "quakelive" / "baseq3" / "ui"
SCRIPT_PATH = REPO_ROOT / "scripts" / "ui" / "write_retail_ui_overrides.py"

EXPECTED_CONTENT_DIFFS = {
	"comp_spectator.menu",
	"comp_spectator_follow.menu",
	"hud.txt",
	"hud3.txt",
	"ingame_callvote.menu",
	"ingame_join.menu",
	"menudef.h",
}


def _collect_files(root: Path) -> set[str]:
	return {
		str(path.relative_to(root)).replace("\\", "/")
		for path in root.rglob("*")
		if path.is_file()
	}


def _compute_drift() -> dict[str, object]:
	source_files = _collect_files(SOURCE_ROOT)
	retail_files = _collect_files(RETAIL_ROOT)
	common_files = sorted(source_files & retail_files)
	content_diffs = [
		relative_path
		for relative_path in common_files
		if (SOURCE_ROOT / relative_path).read_bytes() != (RETAIL_ROOT / relative_path).read_bytes()
	]

	return {
		"missing_in_source": sorted(retail_files - source_files),
		"extra_in_source": sorted(source_files - retail_files),
		"content_diffs": content_diffs,
	}


def test_src_ui_inventory_matches_retail_tree() -> None:
	drift = _compute_drift()
	assert drift["missing_in_source"] == []
	assert drift["extra_in_source"] == []

	source_assets = SOURCE_ROOT / "assets"
	retail_assets = RETAIL_ROOT / "assets"
	assert _collect_files(source_assets) == _collect_files(retail_assets)


def test_src_ui_content_drift_is_limited_to_known_retail_gaps() -> None:
	drift = _compute_drift()
	assert set(drift["content_diffs"]) == EXPECTED_CONTENT_DIFFS

	hud_text = (SOURCE_ROOT / "hud.txt").read_text(encoding="utf-8")
	hud3_text = (SOURCE_ROOT / "hud3.txt").read_text(encoding="utf-8")
	callvote_text = (SOURCE_ROOT / "ingame_callvote.menu").read_text(encoding="utf-8")
	assert "<<<<<<<" in hud_text
	assert "<<<<<<<" in hud3_text
	assert "<<<<<<<" in callvote_text


def test_retail_ui_override_script_emits_drifted_files(tmp_path: Path) -> None:
	homepath_root = tmp_path / "ui_homepath"
	manifest_path = tmp_path / "ui_retail_overrides.json"

	subprocess.run(
		[
			sys.executable,
			str(SCRIPT_PATH),
			"--homepath-root",
			str(homepath_root),
			"--manifest",
			str(manifest_path),
		],
		check=True,
		cwd=REPO_ROOT,
	)

	report = json.loads(manifest_path.read_text(encoding="utf-8"))
	assert set(report["overlay_files"]) == {
		f"baseq3/ui/{relative_path}" for relative_path in EXPECTED_CONTENT_DIFFS
	}

	for relative_path in EXPECTED_CONTENT_DIFFS:
		override_path = homepath_root / "baseq3" / "ui" / relative_path
		retail_path = RETAIL_ROOT / relative_path
		assert override_path.exists()
		assert override_path.read_bytes() == retail_path.read_bytes()


def test_retail_ui_override_script_supports_pk3_overlay_prefix(tmp_path: Path) -> None:
	overlay_root = tmp_path / "ui_overlay_pk3"
	manifest_path = tmp_path / "ui_overlay_pk3.json"

	subprocess.run(
		[
			sys.executable,
			str(SCRIPT_PATH),
			"--homepath-root",
			str(overlay_root),
			"--manifest",
			str(manifest_path),
			"--overlay-prefix",
			"ui",
		],
		check=True,
		cwd=REPO_ROOT,
	)

	report = json.loads(manifest_path.read_text(encoding="utf-8"))
	assert report["overlay_prefix"] == "ui"
	assert set(report["overlay_files"]) == {
		f"ui/{relative_path}" for relative_path in EXPECTED_CONTENT_DIFFS
	}

	for relative_path in EXPECTED_CONTENT_DIFFS:
		override_path = overlay_root / "ui" / relative_path
		retail_path = RETAIL_ROOT / relative_path
		assert override_path.exists()
		assert override_path.read_bytes() == retail_path.read_bytes()


def test_ui_bundle_build_emits_src_ui_overlay_package() -> None:
	bash = shutil.which("bash")
	if not bash:
		pytest.skip("bash is required for the UI bundle script")

	overlay_package = REPO_ROOT / "build" / "ui_bundle" / "pak_ui_src_retail_overlay.pk3"
	overlay_manifest = REPO_ROOT / "artifacts" / "ui_bundle" / "ui_src_retail_overlay.json"
	main_package = REPO_ROOT / "build" / "ui_bundle" / "pak_uiql.pk3"
	metrics_path = REPO_ROOT / "artifacts" / "ui_bundle" / "metrics" / "font_metrics.json"

	if overlay_package.exists():
		overlay_package.unlink()
	if overlay_manifest.exists():
		overlay_manifest.unlink()
	if main_package.exists():
		main_package.unlink()
	if metrics_path.exists():
		metrics_path.unlink()

	result = subprocess.run(
		[bash, "tools/build_ui_bundle.sh"],
		cwd=REPO_ROOT,
		check=False,
		text=True,
		capture_output=True,
	)

	assert result.returncode == 0, result.stderr
	assert overlay_package.exists()
	assert overlay_manifest.exists()
	assert main_package.exists()
	assert metrics_path.exists()

	report = json.loads(overlay_manifest.read_text(encoding="utf-8"))
	assert report["overlay_prefix"] == "ui"
	assert set(report["overlay_files"]) == {
		f"ui/{relative_path}" for relative_path in EXPECTED_CONTENT_DIFFS
	}
