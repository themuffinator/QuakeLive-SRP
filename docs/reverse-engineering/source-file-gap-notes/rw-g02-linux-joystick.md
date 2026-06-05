# `src/code/unix/linux_joystick.c` Gap Note

Last updated: 2026-06-05

Gap family: `RW-G02`
- Owning retail binary: `assets/quakelive/quakelive_steam.exe` for engine-owned surfaces, or the corresponding committed module corpus when this file sits in a module tree.
- Current classification: Closed as explicit compatibility-only containment; Linux joystick support remains a retained non-Windows input host lane, not a modern input parity target.

## Why this file remains compatibility-only

The file still owns Linux joystick device probing and axis-to-key translation. The current source now bounds the retained Linux joystick host more tightly, but it is still not a modern SDL/input-stack replacement.

## Observed facts

- The startup path now prefers `/dev/input/js0` through `/dev/input/js3` before the historical `/dev/js0` through `/dev/js3` device nodes.
- Axis values are still translated into Quake-style key events through threshold checks, now capped to the 8 axis / 16 direction-key range represented by the retained `joy_keys` table.
- `IN_ShutdownJoystick()` releases queued joystick keys, closes `joy_fd`, clears the tracked axis/button state, and resets `ui_joyavail`; `linux_glimp.c` now calls that shutdown path when input shuts down or when the latched `in_joystick` cvar restarts the joystick lane.
- Button event translation is capped to `K_JOY1` through `K_JOY32`, matching the exposed Quake key range instead of trusting arbitrary Linux event numbers.
- The 2026-06-05 A4 boundary decision treats Linux input support as a compatibility-only lane unless a future task adopts a modern input stack.

## Function-by-function status

| Function | Status | Notes |
| --- | --- | --- |
| `IN_ClearJoystickState` | `bounded compatibility` | Tracks bounded axis/button state reset for the retained Linux joystick lane. |
| `IN_ReleaseJoystickKeys` | `bounded compatibility` | Releases queued joystick key state on shutdown/restart so stale device state does not leak into later input frames. |
| `IN_TryOpenJoystick` | `bounded compatibility` | Opens one candidate Linux joystick device, reports its capability metadata, and sets `ui_joyavail` on success. |
| `IN_StartupJoystick` | `compatibility boundary` | Still owns the retained Linux joystick startup lane, now bounded to explicit modern and historical js device probes. |
| `IN_ShutdownJoystick` | `bounded compatibility` | Closes the retained Linux joystick descriptor and clears the UI availability bridge. |
| `IN_JoyMove` | `compatibility boundary` | Still owns Linux joystick event translation, with capped button and axis ranges but no modern input abstraction. |

## Reopen target

- Reopen only if Linux input parity becomes an active target with a modern input abstraction and reproducible validation. The descriptor cleanup, `ui_joyavail` bridge, and event caps reduce compatibility debt but remain compatibility-only.
