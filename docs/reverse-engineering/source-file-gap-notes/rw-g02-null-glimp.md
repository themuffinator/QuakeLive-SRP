# `src/code/null/null_glimp.c` Gap Note

Last updated: 2026-06-05

Gap family: `RW-G02`
- Owning retail binary: `assets/quakelive/quakelive_steam.exe` for engine-owned surfaces, or the corresponding committed module corpus when this file sits in a module tree.
- Current classification: Closed as explicit compatibility-only containment; the file is a compatibility-only null renderer host rather than a real graphics runtime.

## Why this file remains compatibility-only

The file now carries the corrected renderer-host signatures and refuses to fake a loaded GL backend, but every GL entry point still remains a compatibility boundary, so the null runtime still lacks a real graphics host.

## Observed facts

- `GLimp_Init()` now raises a fatal error that states the null renderer host has no OpenGL subsystem, avoiding a later crash through unbound GL function pointers.
- `QGL_Init()` now returns `qfalse` instead of claiming success without loading a renderer library or binding real GL entry points.
- `QGL_Shutdown()` clears the retained extension function pointers and logging state.
- The repo-wide audit still states that the null runtime does not implement a real live graphics/audio/input host.

## Function-by-function status

| Function | Status | Notes |
| --- | --- | --- |
| `GLimp_EndFrame` | `compatibility boundary` | No-op swap/end-frame path inside the null compatibility host. |
| `GLimp_Init` | `compatibility boundary` | Explicit fatal boundary for a renderer host that still creates no graphics context. |
| `GLimp_Shutdown` | `bounded compatibility` | Clears the null QGL state through `QGL_Shutdown()`. |
| `GLimp_EnableLogging` | `bounded compatibility` | Null renderer-host compatibility shim. |
| `GLimp_LogComment` | `bounded compatibility` | Null renderer-host compatibility shim. |
| `QGL_Init` | `bounded compatibility` | Returns `qfalse` because the null host has no real GL backend. |
| `QGL_Shutdown` | `bounded compatibility` | Clears retained null QGL extension pointer and logging state. |

## Reopen target

- Reopen only if the null renderer host is raised to a better-defined non-Windows graphics target with a real graphics context, swap path, and GL loader contract.
