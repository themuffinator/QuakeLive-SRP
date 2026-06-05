# Non-Windows Portability Boundary

Last updated: 2026-06-05

Status: closed as explicit compatibility-only containment for Task A4.

This note closes the current A4 planning decision without claiming that the
legacy Unix/null client runtime is modern or retail-equivalent. The active
repository target remains the strict Windows retail replacement path. The
non-Windows lanes stay useful and visible, but their default role is bounded
source-build and compatibility evidence.

## Boundary Decision

- Active support endpoint: hosted POSIX source builds and dedicated/server
  module validation.
- Active evidence endpoint: the Linux glibc 32-bit preset for
  `qagamei386.so` export and symbol comparison.
- Compatibility-only endpoint: retained Unix host helpers, the Linux X11/GLX
  renderer/input stack, the Linux OSS sound path plus silent sink, and the
  null host/client/audio/input/renderer shims.
- Non-target by default: modern Linux client renderer, audio, input, and null
  host runtime parity.

Linux client/runtime parity is not an active target until a future task
explicitly adopts a modern dependency stack such as SDL2 or an equivalent
renderer, audio, and input abstraction and adds reproducible validation for it.

## Closed A4 Items

- Re-baselined the non-Windows portability lanes as server/module build
  evidence plus compatibility-only runtime carries.
- Chose the current default boundary: Linux client, renderer, audio, and input
  support are bounded compatibility endpoints, not active parity targets.
- Reclassified remaining Unix/null placeholder-style helpers as documented
  compatibility boundaries rather than open repo-wide parity debt.
- Updated the planning and gap-note surface so future work can reopen the
  boundary deliberately.

## Reopen Conditions

Reopen A4 or create a successor portability task only if one of these becomes
true:

- The project decides to support a real Linux client/runtime target.
- The Unix client build is modernized away from the retained XFree86,
  X11/GLX/DGA, Glide-era, and OSS assumptions.
- A real audible Linux audio backend replaces the current OSS-first path and
  silent sink bridge.
- The null host grows beyond compatibility shims into a real tested runtime
  surface.

## Parity Estimate

- Before: repo-wide parity remained 98% because RW-G02 was still carried as an
  open planning gap.
- After: repo-wide parity estimate moves to 99% for the current documented
  target, with non-Windows runtime divergence retained as explicit
  compatibility-only scope rather than hidden source debt.
