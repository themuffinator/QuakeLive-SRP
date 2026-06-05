# `src/code/unix/linux_glimp.c` Gap Note

Last updated: 2026-06-05

Gap family: `RW-G02`
- Owning retail binary: `assets/quakelive/quakelive_steam.exe` for engine-owned surfaces, or the corresponding committed module corpus when this file sits in a module tree.
- Current classification: Closed as explicit compatibility-only containment; this legacy X11/GLX client host path is not a retail-equivalent portability surface.

## Why this file remains compatibility-only

The file is the retained Linux OpenGL/input host implementation. The 2026-06-05 A4 boundary decision keeps the Linux client, renderer, and input runtime as compatibility-only rather than part of the closed Windows replacement target.

## Observed facts

- The file still owns the Linux GLX window, gamma, input-grab, and renderer-thread glue path.
- `GLimp_Shutdown()` now no longer returns early solely because `ctx` is missing; it deactivates mouse state, detaches the current GLX context when the loader is still present, destroys partial contexts/windows only when present, restores VidMode/gamma state, closes the QGL log file, clears GLX globals, and always releases QGL state.
- `GLimp_EndFrame()` now refuses to swap when the display, window, or GLX swap pointer is absent, keeping shutdown and partial-init failure paths from falling through into stale GLX state.
- The input owner now deactivates retained X mouse grabs before clearing mouse availability, then forwards shutdown and latched `in_joystick` restarts through `IN_ShutdownJoystick()` / `IN_StartupJoystick()`, keeping the Linux mouse-active flag, joystick descriptor, and `ui_joyavail` state bounded while the broader input path remains compatibility-only.
- No current repo-wide claim says the Linux client/runtime is equivalent to the closed Windows target; reopening that target requires a future modernization task.
- The portability work completed so far has focused on bounded Unix helper restoration rather than on closing this renderer/input host lane.

## Function-by-function status

| Function | Status | Notes |
| --- | --- | --- |
| `Q_stristr` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `XLateKey` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `CreateNullCursor` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `install_grabs` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `uninstall_grabs` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `X11_PendingInput` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `repeated_press` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `HandleEvents` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `KBD_Init` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `KBD_Close` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `IN_ActivateMouse` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `IN_DeactivateMouse` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `GLimp_SetGamma` | `compatibility boundary` | Renderer gamma host path remains part of the retained Linux client/runtime carry. |
| `GLimp_Shutdown` | `bounded compatibility` | Linux GL teardown now handles partial-init state, restores retained VidMode/gamma state, closes the QGL log, and releases QGL before clearing renderer state. |
| `GLimp_LogComment` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `GLW_StartDriverAndSetMode` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `GLW_SetMode` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `GLW_InitExtensions` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `GLW_InitGamma` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `GLW_LoadOpenGL` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `qXErrorHandler` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `GLimp_Init` | `compatibility boundary` | Top-level Linux GL init path remains part of the retained X11/GLX compatibility carry. |
| `GLimp_EndFrame` | `bounded compatibility` | Linux swap/end-frame now guards missing display/window/swap state, but the GLX renderer host remains compatibility-only. |
| `GLimp_RenderThreadWrapper` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `GLimp_SpawnRenderThread` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `GLimp_RendererSleep` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `GLimp_FrontEndSleep` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `GLimp_WakeRenderer` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `GLimp_RenderThreadWrapper` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `GLimp_SpawnRenderThread` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `GLimp_RendererSleep` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `GLimp_FrontEndSleep` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `GLimp_WakeRenderer` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `IN_Init` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `IN_Shutdown` | `bounded compatibility` | Linux input teardown now releases the retained X mouse grab, calls the joystick shutdown bridge, and clears mouse availability/activity state, but the broader Linux input host remains open. |
| `IN_Frame` | `compatibility boundary` | Linux input pump remains part of the retained non-Windows client path, now with bounded latched joystick restart handling. |
| `IN_Activate` | `compatibility boundary` | Linux active/inactive input state remains compatibility-owned. |
| `Sys_SendKeyEvents` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `IN_StartupJoystick` | `compatibility boundary` | Linux joystick startup remains part of the retained compatibility lane. |
| `IN_JoyMove` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |

## Reopen target

- Reopen only if Linux client/runtime parity becomes an active target with a modern renderer/input dependency stack and reproducible validation.
