# Quake Live Source Reconstruction Project

[![Accuracy First](https://img.shields.io/badge/Accuracy-First-1f6feb)](AUDIT.md)
[![Reconstruction Status](https://img.shields.io/badge/Reconstruction-In%20Progress-b8860b)](AUDIT.md)
[![Reconstruction Plan](https://img.shields.io/badge/Work%20Queue-Reconstruction%20Plan-2ea44f)](IMPLEMENTATION_PLAN.md)
[![Getting Started](https://img.shields.io/badge/Docs-Getting%20Started-6f42c1)](docs/onboarding/overview.md)

[![Deterministic Harnesses](https://github.com/quakelive-reverse/quakelive-reverse/actions/workflows/deterministic-harnesses.yml/badge.svg?branch=main)](https://github.com/quakelive-reverse/quakelive-reverse/actions/workflows/deterministic-harnesses.yml)

This project reconstructs the full Quake Live source code as faithfully as possible.
It starts from the public Quake III Arena GPL source release and then rebuilds the
retail engine and game code piece by piece using retail binaries, committed HLIL and
Ghidra reference corpora, symbol maps, and runtime validation.

Accurate reconstruction is the top priority. This repository is not trying to make a
"Quake Live-like" fork or a rough gameplay approximation. The goal is to reconstruct how
the retail game actually works, document what is known, and close the remaining gaps in a
way that stays grounded in evidence instead of guesswork.

## What accurate reconstruction means here

- Retail Quake Live behavior is the target, not convenience or approximation.
- The committed retail reference corpus is treated as the source of truth when the open GPL
  baseline and the retail game differ.
- Where evidence is incomplete, small intuitive fixes or compatibility wiring may still be
  needed to keep the reconstruction working, but they should stay minimal and give way to
  stronger evidence when it appears.
- Unclear areas are tracked as open gaps instead of being filled in with confident-looking
  assumptions.
- Quake Live-specific online services can be disabled in builds when the retail dependency
  cannot yet be reconstructed cleanly or does not have an open replacement.
- Progress is measured by parity with the retail game, not just by whether the code builds
  or runs.

## Current status

The project is well past initial bring-up. The strict retail-facing module register for
`cgame`, `qagame`, and `ui` is closed, and the dedicated `client` and `renderer` engine
audits are also fully closed.

The remaining work is concentrated in `server`, `qcommon`, and the broader native
launcher/platform host. So while the repo is not yet a finished drop-in replacement for the
retail Windows host, most gameplay-side reconstruction is now in the "close the last gaps"
phase rather than the "discover the system" phase.

Based on the focused parity audits published between 2026-04-05 and 2026-04-10:

Legend: `🟢` closed or effectively complete, `🟡` strong but still open, `🔴` major open
reconstruction lane.

### Game reconstruction

| Area | Status | Strict retail parity | Current snapshot |
| --- | --- | ---: | --- |
| `cgame` | 🟢 Closed | `100%` | Closed in the combined strict-retail module audit; the direct `cgame` suite is green (`170 passed`). |
| `qagame` | 🟢 Closed | `100%` | Closed in the combined strict-retail module audit; retail `qagamex86.dll` hosting is validated. |
| `ui` | 🟢 Closed | `100%` | UI parity gate, retail corpus parity, bundle reproducibility, and runtime evidence are all green. |

### Engine reconstruction

| Area | Status | Strict retail parity | Current snapshot |
| --- | --- | ---: | --- |
| `client` | 🟢 Closed | `100%` | Dedicated parity gate and tracked runtime evidence are both closed. |
| `renderer` | 🟢 Closed | `100%` | Final text/font/runtime closure landed in the `RG-P11` audit pass. |
| `qcommon` | 🟡 Strong, open | `90%` | Active runtime is strong; remaining work is concentrated in filesystem/homepath exactness, collision leaves, fallback QVM paths, and ledger cleanup. |
| `server` | 🟡 Strong, open | `81%` | Classic server spine is strong; remaining work is `idZMQ`, report/stat publication, rankings, control-plane CVars, and a dedicated parity gate. |
| `other` | 🔴 Major open work | `Not yet percentage-scored` | Native launcher/platform host, Windows bootstrap glue, and the broader browser/Awesomium replacement track remain the biggest engine-side gap. |

`other` is intentionally qualitative here: the top-level audit still treats the
launcher/platform host as the largest remaining engine-side gap, but it does not yet have a
dedicated strict-parity percentage of its own.

For the detailed parity breakdown and current task queue, see [`AUDIT.md`](AUDIT.md) and
[`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md).

## Repository guide

- `src/` contains the active reconstructed codebase built on top of the Quake III Arena GPL
  source layout.
- `src-re/` is the clean-room reconstruction workspace used for staged reconstruction work,
  prototypes, and promoted headers.
- `references/` holds the main reconstruction reference corpus, including HLIL exports and
  the committed Ghidra corpus.
- `assets/` stores upstream and retail reference material used for validation and comparison.
- `docs/` contains onboarding notes, workflow guides, parity documentation, and subsystem
  research.
- `tests/`, `tools/`, `artifacts/`, and `logs/` support the deterministic validation and CI
  workflows used to check reconstruction progress.

## Reference corpus

The project keeps its main evidence base in the repository so work can be reviewed and
replayed:

- `references/hlil/` contains Binary Ninja HLIL dumps for both Quake III Arena and Quake
  Live binaries.
- `references/reverse-engineering/ghidra/` contains the committed Ghidra exports used as a
  structured companion corpus.
- `references/symbol-maps/` and `references/analysis/quakelive_symbol_aliases.json` support
  naming, ownership, and symbol recovery work.

If you are tracing a subsystem, start with the committed reference material before making new
assumptions. The canonical workflow is documented in
[`docs/reverse-engineering/ghidra-reference-workflow.md`](docs/reverse-engineering/ghidra-reference-workflow.md).

## Getting started

- Read [`docs/onboarding/overview.md`](docs/onboarding/overview.md) for the quickest project
  orientation.
- Read [`BUILDING.md`](BUILDING.md) for the top-level build guide and the most
  common Windows and Linux build commands.
- Read [`docs/repo-overview.md`](docs/repo-overview.md) for a fuller explanation of the
  repository layout.
- Use [`docs/platform/toolchain-matrix.md`](docs/platform/toolchain-matrix.md) to understand
  build requirements and supported toolchains.
- Use [`docs/reverse-engineering/ghidrassist-mcp.md`](docs/reverse-engineering/ghidrassist-mcp.md)
  and related notes if you are working through the reconstruction reference workflow.

## Credits

- This project builds on the public Quake III Arena GPL source release from id Software:
  [id-Software/Quake-III-Arena](https://github.com/id-Software/Quake-III-Arena)
- This project exists to reconstruct the retail Quake Live codebase as accurately as
  possible: [Quake Live](https://www.quakelive.com/)
