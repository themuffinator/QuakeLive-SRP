"""Command line entry point for the client regression harness."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .harness import ClientRegressionHarness
from .predict import ClientPredictor


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Replay client snapshots and output HUD hashes")
    parser.add_argument("snapshot_archive", type=Path, help="Path to a snapshot JSON archive")
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optionally limit the number of snapshots that are replayed",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    harness = ClientRegressionHarness(ClientPredictor())
    snapshots = harness.load_snapshots(args.snapshot_archive)
    if args.limit is not None:
        snapshots = snapshots[: args.limit]

    for frame in harness.replay(snapshots):
        payload = {
            "sequence": frame.sequence,
            "serverTime": frame.server_time,
            "hash": frame.hud_hash,
            "hud": frame.hud.to_dict(),
        }
        sys.stdout.write(f"{payload}\n")

    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
