# Cgame Client Prediction Parity Recheck - 2026-06-05

## Scope

Focused recheck for the client-side prediction corridor owned by retail
`cgamex86.dll`: local playerstate prediction, usercmd replay into shared
`Pmove`, fallback interpolation, item/trigger prediction, collision tracing,
step smoothing, the predicted rail replay sidecar, and the related frame,
snapshot, packet-entity, mover-compensation, native-export, snapshot-import,
usercmd-import, and pmove-settings wiring that feeds or consumes prediction.

## Evidence

- `references/reverse-engineering/ghidra/cgamex86/metadata.txt` identifies the
  owning retail binary as `cgamex86.dll`.
- `references/symbol-maps/cgame.json` maps the prediction corridor:
  `BG_IsRedBlueFlagItem` at `0x10001000`, `CG_BuildSolidList` at `0x10043C90`,
  `CG_ClipMoveToEntities` at `0x10043D40`, `CG_Trace` at `0x10044040`,
  `CG_TraceCapsule` at `0x10044100`, `CG_PointContents` at `0x100441A0`,
  `CG_InterpolatePlayerState` at `0x10044230`, `CG_TouchItem` at
  `0x100443C0`, `CG_TouchTriggerPrediction` at `0x100444D0`,
  `CG_UpdateStepChange` at `0x10044620`, `CG_PredictPlayerState` at
  `0x100446E0`, and `CG_UpdatePredictedRailFire` at `0x10044CE0`.
- The same symbol map pins the related wiring corridor: `CG_AdjustPositionForMover`
  at `0x10017F70`, `CG_AddPacketEntities` at `0x10018BE0`,
  `CG_SetInitialSnapshot` at `0x1004BE80`, `CG_TransitionSnapshot` at
  `0x1004C020`, `CG_SetNextSnap` at `0x1004C2E0`,
  `CG_ReadNextSnapshot` at `0x1004C3E0`, `CG_ProcessSnapshots` at
  `0x1004C4D0`, and `CG_DrawActiveFrame` at `0x1004E4E0`.
- `docs/reverse-engineering/cgame-mapping.md` records the matching retail
  prediction sweep and the later capsule-trace promotion, including the
  deliberate split where normal prediction traces can use capsule collision but
  trigger-touch prediction remains on the box trace path. The same mapping
  records the snapshot handoff, packet-entity predicted proxy, mover adjustment,
  and active-frame caller order around prediction.
- `src/code/cgame/cg_predict.c` already preserves the recovered retail replay
  shape: first-frame validity, demo/follow and no-predict interpolation
  fallbacks, copied local `pmove_settings_t`, trace and pointcontents callbacks,
  body-aware tracemasks, command backup guards, latest-command rail replay,
  next-snapshot seeding, `pmove_msec` clamping, fixed-pmove angle handling,
  `Pmove`, step smoothing, projectile nudge, trigger/item touches, final mover
  adjustment, and `CG_TransitionPlayerState`.

## Result

No gameplay source patch was required. The recheck tightened
`tests/test_cgame_snapshot_parity.py` so the executable parity gate now also
pins the solid-list, box/capsule trace, point-contents, interpolation,
red/blue-flag predicate, and high-value item skip helpers, plus the full mapped
symbol evidence set for the prediction corridor. The follow-up related-wiring
pass extends that same guard to the active-frame call order, predicted
player-entity proxy, non-predicted local-player refresh, mover compensation,
initial/next/transition snapshot handoffs, snapshot pump, and mapped frame /
snapshot / entity symbol evidence.

Parity estimate for this focused client-side prediction and related wiring
slice remains **before 100% -> after 100%** against the committed retail QL
evidence. The useful change is validation strength: the suite now guards more
of the retail-mapped prediction surface against future source drift.

## Verification

- `python -m pytest tests/test_cgame_snapshot_parity.py tests/test_usercmd_movement_transport_parity.py tests/test_step_jump_gate_parity.py -q --tb=short`
  -> `32 passed`
- `python -m pytest tests/test_cgame_snapshot_parity.py tests/test_usercmd_movement_transport_parity.py tests/test_step_jump_gate_parity.py tests/test_pmove_validation_fixtures.py tests/test_pmove_air_control_runtime_parity.py tests/test_pmove_jump_timing_parity.py -q --tb=short`
  -> `50 passed`
- `python -m pytest tests/test_cgame_snapshot_parity.py tests/test_cgame_playerstate_transition_parity.py tests/test_cgame_event_transport_parity.py tests/test_playerstate_replication.py tests/test_usercmd_movement_transport_parity.py tests/test_pmove_selected_cvar_parity.py tools/tests/test_pmove_settings_configstring.py -q --tb=short`
  -> `68 passed, 107 subtests passed`
- `python -m pytest tests/test_cgame_snapshot_parity.py tests/test_playerstate_replication.py tests/test_usercmd_movement_transport_parity.py tests/test_cgame_playerstate_transition_parity.py tests/test_cgame_event_transport_parity.py tests/test_teleport_state_reconstruction.py tests/test_pmove_selected_cvar_parity.py tools/tests/test_pmove_settings_configstring.py -q --tb=short`
  -> `76 passed, 107 subtests passed`
- `python -m pytest tests/test_cgame_displaycontext_parity.py::test_cgame_thirdperson_timescale_tracer_and_track_cvars_match_retail_table_and_wiring -q --tb=short`
  -> `1 passed`
- `python -m pytest tests/test_engine_client_command_parity.py -q --tb=short`
  -> `23 passed`
- `python -m pytest tests/test_platform_services.py::test_module_native_export_qboolean_slots_use_explicit_wrappers -q --tb=short`
  -> `1 passed`
