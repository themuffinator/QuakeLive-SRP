#!/usr/bin/env python3
"""Validate the staged retail UI corpus and emit a deterministic inventory manifest."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


if __package__ in (None, ""):
	sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.ui.retail_ui_corpus import (  # noqa: E402
	DEFAULT_BASEQ3_ROOT,
	DEFAULT_BUNDLE_MANIFEST,
	build_retail_ui_inventory,
	inventory_missing_reason,
	write_inventory_manifest,
)


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(
		description=(
			"Validate the locally staged retail Quake Live baseq3 UI corpus and optionally "
			"write a machine-readable inventory manifest."
		)
	)
	parser.add_argument("--baseq3-root", type=Path, default=DEFAULT_BASEQ3_ROOT)
	parser.add_argument("--bundle-manifest", type=Path, default=DEFAULT_BUNDLE_MANIFEST)
	parser.add_argument("--inventory-out", type=Path, default=None)
	parser.add_argument(
		"--strict",
		action="store_true",
		help="exit non-zero when required retail inputs are missing",
	)
	return parser.parse_args()


def main() -> int:
	args = parse_args()
	inventory = build_retail_ui_inventory(args.baseq3_root, args.bundle_manifest)

	if args.inventory_out is not None:
		write_inventory_manifest(args.inventory_out, inventory)

	if inventory["retail_ui_corpus_available"]:
		print(
			"Retail UI corpus available: "
			f"{inventory['inventory_counts']['files']} manifest-tracked files verified."
		)
		if args.inventory_out is not None:
			print(f"Inventory manifest written to {args.inventory_out.as_posix()}")
		return 0

	print("Retail UI corpus unavailable.", file=sys.stderr)
	print(inventory_missing_reason(inventory, limit=12), file=sys.stderr)
	print("Missing required inputs:", file=sys.stderr)
	for relative_path in inventory["missing_required_inputs"]:
		print(f"  - {relative_path}", file=sys.stderr)
	if args.inventory_out is not None:
		print(f"Inventory manifest written to {args.inventory_out.as_posix()}", file=sys.stderr)

	return 1 if args.strict else 0


if __name__ == "__main__":
	raise SystemExit(main())
