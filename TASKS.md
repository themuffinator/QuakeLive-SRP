# Quake Live Functional Parity Tasks

1.  **Implement `cg_impactMarkTime` logic**: Update `cg_marks.c` to use `cg_impactMarkTime` for determining the duration of wall marks, replacing fixed constants or older cvar logic.
2.  **Update View Bobbing Logic**: Verify that `cg_kickScale` (0.25) and `cg_bob` (0.25) defaults provide the correct Quake Live visual feel in `cg_view.c`. Adjust scaling math if necessary to match QL's smoother/reduced movement.
3.  **Implement Spectator Team Vitals**: Use `cg_specTeamVitalsY` and `cg_specTeamVitalsWidth` in `cg_draw.c` (or relevant HUD file) to position the team vitals display correctly for spectators.
4.  **Verify Dead Body Color**: Ensure `cg_deadBodyColor` is correctly applied to dead bodies in `cg_players.c` / `cg_ents.c`, respecting the `0x101010FF` default.
5.  **Verify Enemy Head Color**: Ensure `cg_enemyHeadColor` (Green) is correctly applied to enemy models in team games, overriding skin colors where appropriate.
6.  **Verify Team Head Color**: Ensure `cg_teamHeadColor` (Grey) is correctly applied to teammate models, distinguishing them from enemies.
7.  **Check Low Ammo Warning**: Verify `cg_lowAmmoWarningPercentile` logic in `cg_draw.c` to ensure the warning triggers at 20% ammo as per default.
8.  **Verify Auto Action Flags**: Check if `cg_autoAction` needs `CVAR_USERINFO` to properly inform the server of client demo/screenshot intent, or if `CVAR_LATCH` is sufficient.
9.  **Simple Items Parity**: Verify `cg_simpleItems` behavior with the updated defaults (if any were changed) and ensure `cg_simpleItemsRadius` is used correctly.
10. **Score Plum Parity**: Verify `cg_scorePlum` behavior matches Quake Live's visual style and timing.
