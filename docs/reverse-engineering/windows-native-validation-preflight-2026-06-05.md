# Windows Native Validation Preflight

Last updated: 2026-06-05

Status: captured strict-retail blocker; superseded for Task A6 by
`runtime-build-evidence-refresh-2026-06-05`.

This note records the strict-retail local preflight for the A6 native Windows
build validation row. It is not a successful strict retail native build, export
audit, staged runtime audit, or runtime launch. The later A6 refresh note
records the successful modern-host build/export evidence and current
retail-module runtime evidence.

## Commands

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\audit-retail-toolchain.ps1 -Strict
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\validate-windows-native.ps1 -RuntimeProfile retail
```

Both commands now infer the repository root from their script path when
`-RepoRoot` is omitted. That resolves the wrapper-level preflight issue and
lets the commands reach the real strict-retail project metadata checks.

## Observed Result

- `audit-retail-toolchain.ps1 -Strict` verified
  `src/code/quakelive_steam.vcxproj` `ToolsVersion="4.0"` and the expected
  release/debug runtime-library settings before failing on
  `//msb:PlatformToolset`.
- `validate-windows-native.ps1 -RuntimeProfile retail` verified that
  `qagamex86`, `cgamex86`, `uix86`, `quakelive_steam`, and
  `awesomium_process` currently use `PlatformToolset='v141'`, then invoked
  the strict retail toolchain audit and hit the same failure.
- The blocking failure is:
  `Value mismatch in src/code/quakelive_steam.vcxproj for //msb:PlatformToolset: expected 'v100', found 'v141'`.
- No strict retail native build, staged runtime dependency audit, export audit,
  game launch, or runtime evidence refresh was performed after that blocker.

## Impact

The strict-retail validation target still expects the recovered VC10-era
`v100` project metadata, while the current checked-in project files are on the
hosted-compatible `v141` default path. Until that policy is reconciled, fresh
strict VC10 staged-runtime evidence cannot be claimed.

Repo-wide parity estimate remains **99% -> 99%**. This preflight improves the
strict-retail diagnosability trail; the later A6 refresh note captures the
available modern-host build/export and retail-module runtime evidence.

## Next Actions

1. Decide whether the checked-in retail-facing projects should return to
   `PlatformToolset=v100` for strict retail metadata, or whether the strict
   audit needs a separately named hosted-compatible path.
2. Rerun `validate-windows-native.ps1 -RuntimeProfile retail` after that
   decision and capture the build, export, staged-runtime, and dependency
   results.
3. Keep strict VC10 staged-runtime promotion blocked until a successful rerun
   produces fresh evidence.
