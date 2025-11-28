# Competitive HUD round and overtime captures

This directory holds the headless capture payloads for the competitive HUD's round and overtime banners.

- **How to run:** `python tools/tests/hud_round_overtime_capture.py --output-root docs/hud-round-overtime`
- **Inputs:** synthetic snapshots in `tools/tests/client_regression/round_overtime_snapshots.json` seeded with regulation, sudden-death, and chained overtime states.
- **Outputs:** JSON payloads per aspect ratio plus a `manifest.json` with commit metadata, HUD configuration, and frame counts (four frames per aspect at 4:3, 16:9, and 21:9).
- **Verification:** regenerated captures successfully using the competitive HUD stack; manifest confirms the expected frame totals and source snapshot archive.
