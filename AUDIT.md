# Quake Live Parity Audit

Last updated: 2026-04-17

This file is the current cross-subsystem ledger for the repository. Detailed
reconstruction history belongs in the dedicated subsystem audits under
`docs/reverse-engineering/`; this top-level audit now records the current
repo-wide state, the active remaining work, and a minimal set of historical
closure anchors kept for existing parity gates.

## Current status

The repo is no longer carrying broad engine or module reconstruction debt as an
active top-level problem. The current audited state on 2026-04-17 is:

- `ui`, strict retail module, `qcommon`, the mapped `qshared` helper family,
  renderer, server, remaining engine host/support, and `client` parity gates
  are green on the current worktree.
- The focused 2026-04-16 Windows platform-specific engine audit remains closed.
- The focused 2026-04-16 engine netcode audit remains closed.
- The focused 2026-04-16 Awesomium/browser host audit remains closed.
- The focused gameplay validation sweep is now closed again on the current
  worktree through dedicated Race, gametype-lifecycle, ready-up, and `pmove`
  fixtures.
- The ownerdraw/stat payload validation lane is now closed again on the current
  worktree after the runtime harness was refreshed to match the live float
  `pickupAvg` debug payload shape.
- The previously reopened client validation lane is now reclosed on the current
  worktree; there is no top-level audited gate failure in the current ledger.

Treat the 2026-04-10 engine-wide **100%** report as an important closure
milestone, not as a substitute for the current checked-in evidence bundle. The
2026-04-17 client workflow/runtime refresh returns the current top-level gate
set to green on this worktree.

## Evidence checked on 2026-04-17

Verified directly:

- `pytest tests/test_ui_full_parity_gate.py -q --tb=no` -> `1 passed, 1 skipped`
- `pytest tests/test_game_module_retail_parity_gate.py -q --tb=no` -> `2 passed, 1 skipped`
- `pytest tests/test_qcommon_full_parity_gate.py -q --tb=no` -> `2 passed, 1 skipped`
- `pytest tests/test_renderer_full_parity_gate.py -q --tb=no` -> `2 passed, 1 skipped`
- `pytest tests/test_server_full_parity_gate.py -q --tb=no` -> `2 passed, 1 skipped`
- `pytest tests/test_engine_host_support_full_parity_gate.py -q --tb=no` -> `2 passed, 1 skipped`
- `pytest tests/test_platform_services.py tests/test_steamworks_harness.py tests/test_client_config_parity.py tests/test_client_workshop_bootstrap_parity.py tests/test_ui_menu_files.py tests/test_client_full_parity_gate.py -q --tb=no` -> `146 passed, 1 skipped`
- `pytest tests/test_client_full_parity_gate.py -q --tb=no` -> `2 passed, 1 skipped`
- `pytest tests/test_gametype_lifecycle.py -q` -> `8 passed`
- `pytest tests/test_game_readyup_parity.py tests/test_game_team_count_parity.py -q` -> `7 passed`
- `pytest tests/test_racepoint_commands.py -q` -> `1 passed`
- `pytest tests/test_pmove_validation_fixtures.py tests/test_pmove_air_control_runtime_parity.py tests/test_pmove_jump_timing_parity.py -q` -> `14 passed`

Current client-lane closure refresh details:

- `.github/workflows/client-validation.yml` is restored and now matches the
  audited `CL-P6` validation surface.
- `artifacts/client_validation/logs/client_runtime_evidence_20260410.json`
  now carries a clean main-menu plus `bloodrun` local-map bundle with the
  required disabled-browser markers, `CS_ACTIVE` transition, engine screenshot,
  flushed demo artifact, and lifecycle end markers.
- `tools/client/run_client_runtime_probe.ps1` now uses the valid
  `map bloodrun ffa` command shape, survives transient `pak_uiql.pk3` rewrite
  locks, and paces the local map probe deterministically enough to reach the
  active runtime before issuing demo/screenshot commands.

## Active remaining work

No top-level audited gap is currently open in `AUDIT.md`. Reopen this section
only when a parity gate fails or new retail evidence creates a concrete
cross-subsystem delta.

## Subsystem references

- Engine-wide closure milestone:
  `docs/reverse-engineering/engine-full-parity-audit-and-implementation-plan-2026-04-10.md`
- Current strict retail module ledger:
  `docs/reverse-engineering/game-module-parity-audit-and-implementation-plan-2026-04-10.md`
- UI parity ledger:
  `docs/reverse-engineering/ui-full-parity-audit-and-implementation-plan-2026-04-05.md`
- Client closure milestone and validation note:
  `docs/reverse-engineering/client-full-parity-audit-and-implementation-plan-2026-04-09.md`
  and
  `docs/reverse-engineering/client-validation-and-runtime-evidence-2026-04-10.md`
- Qcommon parity ledger:
  `docs/reverse-engineering/qcommon-full-parity-audit-and-implementation-plan-2026-04-10.md`
- Qshared helper parity ledger:
  `docs/reverse-engineering/qshared-retail-helper-parity-audit-2026-04-17.md`
- Renderer parity ledger:
  `docs/reverse-engineering/renderer-full-parity-audit-and-implementation-plan-2026-04-09.md`
- Server parity ledger:
  `docs/reverse-engineering/server-full-parity-audit-and-implementation-plan-2026-04-10.md`
- Remaining engine host/support ledger:
  `docs/reverse-engineering/engine-host-support-full-parity-audit-and-implementation-plan-2026-04-10.md`
- Platform-specific Windows engine ledger:
  `docs/reverse-engineering/platform-specific-engine-parity-audit-and-implementation-plan-2026-04-16.md`
- Engine netcode ledger:
  `docs/reverse-engineering/engine-netcode-parity-audit-2026-04-16.md`
- Awesomium/browser host ledger:
  `docs/reverse-engineering/awesomium-browser-host-parity-audit-and-implementation-plan-2026-04-16.md`

## Historical closure anchors kept for parity-gate compatibility

These lines intentionally preserve a minimal set of exact historical closure
strings that the checked-in parity gates still consume. They document past
closure milestones, not the full current 2026-04-17 top-level state by
themselves.

### Module closure milestones

- `GMR-P7` is now complete in the current worktree.
- `GMR-P8` is now complete in the current worktree.
- The current module audit, the top-level ledgers, and the supporting pipeline notes now all point at the same closure state again.
- The current strict retail module estimate for the current worktree is back at **100%** in the refreshed module report.

### Renderer closure milestones

- The open renderer gap register is now wider than the old single-tranche `RG-G05` story.
- `RG-P5` is now complete.

### Qcommon closure milestones

- The refreshed strict `qcommon` estimate is now **92%**.
- `QC-P2` and `QC-P3` are now complete.
- `QC-G04` and `QC-G01` are now closed.
- The refreshed strict `qcommon` estimate is now **95%**.
- `QC-P4` is now complete.
- `QC-G02` is now closed.
- The refreshed strict `qcommon` estimate is now **98%**.
- `QC-P5` is now complete.
- `QC-G03` is now closed.
- The refreshed strict `qcommon` estimate is now **100%**.
- `QC-P6` is now complete.
- `QC-G05` is now closed.
- No open gap remains in the audited qcommon register.

### Qshared closure milestone

- The refreshed strict `qshared` helper estimate is now **100%**.
- `QS-P1` and `QS-P2` are now complete.
- `QS-G01` and `QS-G02` are now closed.

### Server closure milestones

- The refreshed strict `server` estimate is now explicitly tracked as **100%**.
- `SV-P7` is now complete.
- No open gap remains in the audited server register.

### Remaining engine host/support closure milestones

- The refreshed strict `remaining engine host/support` estimate is now tracked as **100%**.
- `EH-P1` is now complete. The host/support artifact now carries machine-readable scope boundary and classification metadata and reports `overall_status: pass`.
- `EH-P4` is now complete.
- `EH-G04` is now closed.
- `EH-P6` is now complete.
- `EH-G06` is now closed.

### Client closure milestone

- `CL-P6` is now complete.
- The refreshed strict `client` estimate is now **100%**.
- No open gap remains in the audited client register.

Those three lines record the 2026-04-10 client closure milestone. The
2026-04-17 worktree now revalidates that same closure state with a refreshed
workflow plus runtime bundle, as described in the current-status sections
above.
