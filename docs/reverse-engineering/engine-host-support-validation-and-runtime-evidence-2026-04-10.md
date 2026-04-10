# Remaining Engine Host/Support Validation And Runtime Evidence (2026-04-10)

Scope: `EH-P1` / `EH-P5` / `EH-P6` closure for the remaining engine-owned host/support surface outside `qcommon`, `server`, `client`, and `renderer`

## Purpose

This note records the validation tranche introduced by `EH-P6`, extended by
the later `EH-P4` botlib proof closure, and finalized by `EH-P5`. The goal is
not to reopen the earlier Win32 Unicode clipboard or raw-input reconstruction
work; it is to keep the recovered host behavior enforceable with one dedicated
parity gate and one tracked evidence bundle while also making the
compatibility-only lanes impossible to misread as open strict-retail debt.

## Tracked Evidence Bundle

Tracked artifact:

- `artifacts/engine_host_support_validation/logs/engine_host_support_runtime_evidence_20260410.json`

Observed closure evidence from the tracked bundle:

1. The closed Win32 clipboard lane is now pinned to the Unicode-first `Sys_GetClipboardData()` source owner plus the shared UTF-16 sizing, conversion, and trim helpers in `win_clipboard_shared.h`, with the focused proof lane in `tests/test_win32_clipboard_parity.py`.
2. The closed Win32 raw-input lane is now pinned to retained registration, `WM_INPUT` dispatch, bounded sample extraction, device listing, and fallback-lane ownership in `win_input.c` / `win_wndproc.c`, with focused proof in `tests/test_win32_raw_input_parity.py`.
3. The botlib internal lane is now also pinned to dedicated deterministic proof in `tests/test_botlib_internal_parity.py`, which exercises representative AAS/sample, reachability, and goal-state helpers through `tests/botlib_internal_harness.c`.
4. The remaining Win32 loading-window/bootstrap proof for this scope is now tracked explicitly through `tests/test_renderer_win32_host_glue_parity.py`, which keeps the shared loading-window wrappers, startup ordering, and fast-restart maximize preservation visible in one low-cost source-backed check.
5. `tests/test_input_translation.py` now uses the shared compiler-discovery helper in `tests/compiler_support.py`, so the Unicode/CPI input translation lane no longer depends on `gcc` being present on the default Windows host.
6. No fresh live engine launch was required for `EH-P6` or `EH-P4`: the runtime-sensitive Win32 host gaps (`EH-G01` and `EH-G02`) were already closed in writable source, and the later botlib tranche closed a proof/evidence gap through deterministic harness coverage instead of a new live probe.

## Dedicated Remaining-Engine Host/Support Parity Gate

Tracked status artifact:

- `artifacts/engine_host_support_validation/logs/engine_host_support_full_parity_gate.json`

Gate owner:

- `tests/test_engine_host_support_full_parity_gate.py`

The unified gate now records the full remaining-engine host/support gap register
(`EH-G01`..`EH-G06`) in one machine-readable report. After `EH-P5`, that
artifact now reports `overall_status = pass`: `EH-G03` and `EH-G05` no longer
show up as blocked parity debt because they are now explicitly classified as
documented compatibility-only divergences outside the strict-retail Windows
score. `EH-G04` remains closed because the botlib internal helper lane has a
dedicated audit plus deterministic proof coverage, and `EH-G06` remains closed
because the dedicated gate, tracked evidence bundle, and workflow wiring still
exist and stay green.

`EH-P1` now adds scope-boundary metadata and classification metadata to the
same artifact. In practice that means the report no longer only answers
"which gaps pass?"; it also answers "which lanes count toward the strict-retail
headline score?" and "which lanes are compatibility-only exclusions?"

## Workflow Wiring

CI owner:

- `.github/workflows/engine-host-support-validation.yml`

The workflow runs the focused host/support regression surface:

- `tests/test_platform_services.py`
- `tests/test_steamworks_harness.py`
- `tests/test_renderer_win32_host_glue_parity.py`
- `tests/test_bot_resource_loading.py`
- `tests/test_botlib_internal_parity.py`
- `tests/test_win32_clipboard_parity.py`
- `tests/test_win32_raw_input_parity.py`
- `tests/test_input_translation.py`
- `tests/test_engine_host_support_full_parity_gate.py`

and uploads `artifacts/engine_host_support_validation/**` so the tracked evidence bundle and the parity-gate artifact stay reviewable outside local machines.

## Current Gate State

After `EH-P5`, `EH-G03` and `EH-G05` are now considered closed as documented compatibility-only divergences.

After `EH-P4`, `EH-G04` is now considered closed.

`EH-P4` is now considered complete.

`EH-P1` is now considered complete.

`EH-P5` is now considered complete.

## Closure

`EH-P6` is now considered complete.

`EH-G06` is now considered closed.

The strict remaining-engine host/support estimate now moves to **100%**. The
lane is now fully closed in the audited register: the dedicated gate still
keeps the compatibility-only tranches machine-visible, but it now classifies
them as closed exclusions instead of leaving the overall scope blocked.
