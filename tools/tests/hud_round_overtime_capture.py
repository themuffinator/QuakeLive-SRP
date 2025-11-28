#!/usr/bin/env python3
"""Headless renderer for competitive HUD round and overtime states."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Mapping

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tests.run_harnesses import COMPETITIVE_HUD_CONFIG, HUD_ASPECT_RATIOS, _current_commit
from tools.tests.client_regression import ClientPredictor, ClientRegressionHarness

DEFAULT_OUTPUT_ROOT = REPO_ROOT / "docs" / "hud-round-overtime"
SNAPSHOT_ARCHIVE = (
    REPO_ROOT / "tools" / "tests" / "client_regression" / "round_overtime_snapshots.json"
)
SCENARIO_NAME = "round_overtime"


def _write_json(path: Path, payload: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _load_frames(snapshot_path: Path) -> tuple[list[dict[str, object]], Mapping[str, object]]:
    harness = ClientRegressionHarness(ClientPredictor())

    archive_payload = json.loads(snapshot_path.read_text(encoding="utf-8"))
    metadata = archive_payload.get("metadata", {})

    snapshots = harness.load_snapshots(snapshot_path)
    frames = [harness.frame_to_payload(frame) for frame in harness.replay(snapshots)]
    return frames, metadata


def capture(output_root: Path) -> dict[str, object]:
    frames, snapshot_metadata = _load_frames(SNAPSHOT_ARCHIVE)
    commit_hash = _current_commit()

    manifest_entries: list[dict[str, object]] = []
    for aspect in HUD_ASPECT_RATIOS:
        payload = {
            "metadata": {
                "aspect": aspect,
                "hudConfig": COMPETITIVE_HUD_CONFIG,
                "commit": commit_hash,
                "scenario": SCENARIO_NAME,
                "snapshotArchive": str(SNAPSHOT_ARCHIVE.relative_to(REPO_ROOT)),
                "frames": len(frames),
                "snapshotMetadata": snapshot_metadata,
            },
            "frames": frames,
        }

        capture_path = output_root / aspect / f"{SCENARIO_NAME}.json"
        _write_json(capture_path, payload)

        manifest_entries.append(
            {
                "aspect": aspect,
                "scenario": SCENARIO_NAME,
                "frames": len(frames),
                "path": str(capture_path.relative_to(output_root)),
                "hudConfig": COMPETITIVE_HUD_CONFIG,
                "commit": commit_hash,
                "snapshotArchive": str(SNAPSHOT_ARCHIVE.relative_to(REPO_ROOT)),
            }
        )

    manifest = {
        "commit": commit_hash,
        "hudConfig": COMPETITIVE_HUD_CONFIG,
        "captures": manifest_entries,
    }

    _write_json(output_root / "manifest.json", manifest)
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate headless round and overtime HUD captures"
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Destination directory for capture payloads (defaults to docs/hud-round-overtime)",
    )
    args = parser.parse_args(argv)

    manifest = capture(args.output_root)
    print(
        "Wrote headless HUD round/overtime captures to",
        args.output_root,
        "for aspects:",
        ", ".join(HUD_ASPECT_RATIOS),
    )
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
