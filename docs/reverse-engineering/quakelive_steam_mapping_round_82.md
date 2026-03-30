# Quake Live Steam Host Mapping Round 82

## Scope

This round closes the next bounded `quakelive_steam.exe` host edge-contract
band adjacent to the earlier strict-boolean return work:

- the implicit-int `qboolean` argument passed into `UI_INIT`
- the implicit demo-playing flag passed into `CG_DRAW_ACTIVE_FRAME`
- the shared UI/cgame key-event boolean fanout in `CL_KeyEvent`

The evidence stayed inside the committed corpus plus the writable source tree:

- `docs/architecture/native-pipeline.md`
- `docs/reverse-engineering/ui-mapping-pass-2026-03-20.md`
- `src/code/client/cl_ui.c`
- `src/code/client/cl_cgame.c`
- `src/code/client/cl_keys.c`

## Strict `qboolean` argument contracts

The native-pipeline notes already describe these entry points with explicit
`qboolean` parameters:

- `UI_Init(qboolean inGame)`
- `CG_DrawActiveFrame(..., qboolean demoPlaying)`
- `UI_KeyEvent(int key, qboolean down)`
- `CG_KeyEvent(int key, qboolean down)`

Before this round, the retained host still relied on implicit integer coercion
for these arguments:

- `CL_InitUI()` passed the raw `(cls.state >= ... && cls.state < ...)`
  expression directly into `UI_INIT`
- `CL_CGameRendering()` forwarded `clc.demoplaying` directly into
  `CG_DRAW_ACTIVE_FRAME`
- `CL_KeyEvent()` fanned the raw `down` value directly into the UI/cgame
  native key-entry points

That was functionally acceptable for the rebuilt source path, but it still
left the host looser than the documented native contract shape that the retail
host interface implies.

## Retained source changes

The writable source now normalizes those argument owners explicitly:

- `src/code/client/cl_ui.c`
  - `CL_InitUI()` derives a single `inGame` `qboolean` and passes that into
    both legacy and current `UI_INIT` call paths
- `src/code/client/cl_cgame.c`
  - `CL_CGameRendering()` derives a `demoPlaying` `qboolean` before calling
    `CG_DRAW_ACTIVE_FRAME`
- `src/code/client/cl_keys.c`
  - `CL_KeyEvent()` derives one normalized `dispatchDown` `qboolean`
  - all UI/cgame key-event dispatches now reuse that normalized value
  - local key-state bookkeeping now also stores the normalized `qboolean`

That keeps the host-side native argument surface explicit instead of depending
on int-sized truthiness at these call boundaries.

## Verification

Updated coverage landed in:

- `tests/test_platform_services.py`

Command run:

```text
python -m pytest tests/test_steamworks_harness.py tests/test_platform_services.py tests/test_ui_menu_files.py -q
```

Result:

- `76 passed`

## Outcome

This round did not add new address aliases. It consumed already-mapped host
ownership in one concrete way:

- the UI init gate, cgame render demo flag, and UI/cgame key-event fanout now
  pass explicit `qboolean` values rather than relying on implicit integer
  coercion

Estimated parity for this round: `82% -> 83%`.
