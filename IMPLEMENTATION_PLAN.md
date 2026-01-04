# Implementation Plan

This document tracks the final steps to verify and seal the Quake Live reconstruction.

## Phase 1: Core Systems Verification [COMPLETED]
- [x] **Physics**: Verify `PM_AirControl` and PQL movement (Confirmed in `bg_pmove.c`).
- [x] **Weapons**: Verify damage constants and special mechanics (Confirmed in `g_weapon.c`/`g_main.c`).
- [x] **Game Logic**: Verify factory and gametype lifecycle (Confirmed in `g_factory.c`/`g_main.c`).

## Phase 2: User Interface Restoration [COMPLETED]
- [x] **UI Bridge**: Implement `ui_quakelive_bridge.c` to generate fallback menus.
- [x] **Menu Assets**: Ensure bridge writes `ql_bridge_*.menu` files to homepath.

## Phase 3: Social & Admin Features [COMPLETED]
- [x] **Admin Commands**: Implement `/admin`, `/mute`, `/ban`, `/kick` (Confirmed in `g_cmds.c`).
- [x] **Social Simulation**: Commands `/invite` and `/clan` are implemented as local simulations in `g_cmds.c`.

## Phase 4: Final Polish & Release [PENDING]
- [ ] **Regression Testing**: Run `tests/test_damage_timelines.py`.
- [ ] **Build Verification**: Confirm clean compile of `qagame` module.
