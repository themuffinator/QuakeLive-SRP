# Agent Instructions

This repository exists to faithfully reconstruct the Quake Live engine and game source using the Binary Ninja HLIL references as an accurate guide to the retail code base.

## Implementation Plan

Agents **MUST** follow the tasks outlined in [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md).

*   **Consult the Plan**: Before starting any work, check `IMPLEMENTATION_PLAN.md`.
*   **Update Progress**: Tick off items in `IMPLEMENTATION_PLAN.md` as they are completed.
*   **Report Gaps**: If you identify a new parity gap, add it to `AUDIT.md` and the plan.

## Coding Standards

*   **Indentation**: Tabs only.
*   **Format**: Follow the existing C style (K&R-ish, space after `if`/`while`).
*   **Safety**: Use `Q_strncpyz` instead of `strncpy`.
*   **Parity**: Match Quake Live values exactly (e.g., Weapon Damage, Physics Constants).

## Build & Verify

*   **Compile**: Run `tools/build/linux32_qagame.sh` to compile the game module.
*   **Test**: Run `tests/test_*.py` to verify logic (e.g., `test_damage_timelines.py`).
