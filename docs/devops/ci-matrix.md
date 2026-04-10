# Deterministic Validation Matrix

The hosted GitHub Actions workflows are intentionally pruned at this stage, but the deterministic validation matrix still exists as a local/manual runbook. The same three gameplay flavours remain the expected validation surface: bytecode, native, and reverse-engineered targets.

## Matrix jobs

- **QVM** – Run on a Unix-like host, re-validate the legacy toolchain, reuse the clean-room build helper, and drive the deterministic harness suite against the VM output.【F:tests/run_harnesses.py†L24-L112】
- **DLL** – Run on Windows, provision the Visual Studio 2010 components as needed, verify the `v100` toolset, validate the retail-aligned Windows native pipeline, and then execute the shared harness runner.【F:tests/run_harnesses.py†L24-L112】
- **Reverse** – Run on a Unix-like host, rebuild the clean-room modules via `tools/ci/build-cleanroom.sh`, and extend the harness invocation with the reverse build root so the trace harness can diff the clean-room binaries against the expected transcript.【F:tests/run_harnesses.py†L24-L112】

## Artefacts

`tests/run_harnesses.py` emits deterministic match timelines, HUD hash captures, weapon timing baselines, and text summaries for every target, while the reverse leg adds normalised trace logs and diffs.【F:tests/run_harnesses.py†L27-L116】 These artefacts land underneath `artifacts/tests/<suite>/<target>/latest/` when run locally. In particular:

- `logs/<target>/latest/*.log` – Harness summaries for the match, client regression, and trace suites.
- `match_sim/<target>/latest/<slug>/timeline.json` – Deterministic bot timelines for each bundled scenario (`duel`, `overtime`, and `loadouts`).
- `match_sim/<target>/latest/index.json` – Inventory of published match simulations with metadata (frame counts, seeds, etc.).
- `client_regression/<target>/latest/hud_hashes.json` – Stable HUD hashes replayed from the regression snapshots.
- `weapon_timings/<target>/latest/baseline.json` – Reload/refire and ammo pickup baselines diffed against HLIL tables.
- `trace/<target>/latest/*` – Reverse-only logs and diffs that compare the clean-room output with the expectation.

Re-run the harness locally with the shared entry points:

```bash
python tests/run_harnesses.py --target qvm
python tests/run_harnesses.py --target dll
python tests/run_harnesses.py --target re --reverse-build-root build/re/linux
```

## Status reporting

Capture local run logs and artefacts alongside the relevant audit or implementation note when a matrix leg is re-run. With hosted workflows disabled, those checked-in artefacts are now the authoritative validation evidence.
