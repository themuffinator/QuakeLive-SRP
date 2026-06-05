# Runtime And Build Evidence Refresh

Last updated: 2026-06-05

Scope: Task A6 from `IMPLEMENTATION_PLAN.md`.

Status: completed for evidence available on this workstation, with the strict
retail VC10 lane documented as blocked rather than silently stale.

## Result

- The retail-module `latest` alias now points at
  `artifacts/module_validation/logs/retail_module_runtime_evidence_20260602.json`.
- That artifact has no missing log markers, no warnings, and reaches the live
  map path with retail `ui`, `qagame`, and `cgame` DLL loads, `Server:
  bloodrun`, `Going from CS_PRIMED to CS_ACTIVE`, engine screenshots, and
  vm-trace create/free/call traffic.
- Visual Studio 2022 `v143` is available on this workstation, and
  `tools/ci/verify-vs-toolchain.ps1 -PlatformToolset v143 -RequireToolset`
  passed.
- The modern native validation lane built `Release|x86` with `v143`,
  `RuntimeProfile modern`, and optional codecs disabled. MSBuild reported
  `Build succeeded`, `0 Warning(s)`, and `0 Error(s)`.
- The validation wrapper timed out after the successful build while continuing
  post-build checks, so the export audit was rerun directly.
- `tools/ci/assert-dll-exports.ps1` now prefers the newest Release artifact,
  avoiding stale `bin/baseq3` DLL copies when fresher module outputs exist.
  The direct export audit passed against the fresh `qagamex86.dll`,
  `cgamex86.dll`, and `uix86.dll` outputs.

## Strict Retail Lane

`tools/ci/audit-retail-toolchain.ps1 -Strict` is not promotable on this
checkout. It fails because the current checked-in project files use
`PlatformToolset` `v141`, while the strict retail audit expects `v100`.

That means the 2026-06-05 A6 pass refreshes current modern-host build evidence
and retail-module runtime freshness, but does not claim fresh strict VC10
staged-runtime evidence.

## Parity Estimate

- Repo-wide before: `99%`
- Repo-wide after: `99%`

The A6 gap is now a documented validation boundary rather than an uninspected
runtime freshness gap. The remaining distinction is strict retail VC10 evidence
versus modern-host compatibility build evidence.
