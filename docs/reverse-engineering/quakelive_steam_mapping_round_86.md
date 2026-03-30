# Quake Live Steam Host Mapping Round 86

## Scope

This round closes the next bounded `quakelive_steam.exe` host compatibility
slice at the structured native import-table surface:

- strict retail-style null gaps for the UI native import slab
- strict retail-style null gaps for the cgame native import slab
- preserved explicit compatibility-tail slots beyond the recovered retail slabs

The evidence stayed inside the committed corpus plus the writable source tree:

- `src/code/client/cl_ui.c`
- `src/code/client/cl_cgame.c`
- `src/code/server/sv_game.c`
- `src/code/ui/ui_public.h`
- `src/code/cgame/cg_public.h`
- `tests/test_platform_services.py`

## Structured native import slabs

The current host already builds three native import slabs:

- `SV_InitGameImports()` in `sv_game.c`
- `CL_InitUIImports()` in `cl_ui.c`
- `CL_InitCGameImports()` in `cl_cgame.c`

Observed facts from the retained source before this round:

- `SV_InitGameImports()` already starts from `Com_Memset( ql_game_imports, 0, ... )`
  and only assigns recovered retail qagame imports plus the explicit
  compatibility tail
- `CL_InitUIImports()` prefilled every `UI_QL_NATIVE_IMPORT_COUNT` slot with
  `QL_UI_trap_Stub`
- `CL_InitCGameImports()` prefilled every `CGAME_NATIVE_IMPORT_COUNT` slot with
  `QL_CG_trap_Stub`

That meant the UI and cgame host slabs silently manufactured a generic
`return 0` behavior for every unrecovered retail import gap instead of
preserving the stricter null surface already used by qagame.

## Retained source changes

The writable host now aligns all three native import slabs on the stricter
retail-style shape:

- `src/code/client/cl_ui.c`
  - `CL_InitUIImports()` now zero-fills `ql_ui_imports`
  - only the recovered retail UI slots plus the explicit source compatibility
    extensions are assigned live function pointers
- `src/code/client/cl_cgame.c`
  - `CL_InitCGameImports()` now zero-fills `ql_cgame_imports`
  - only the recovered retail cgame slots plus the explicit source
    compatibility extensions are assigned live function pointers

The effect is deliberate:

- unrecovered retail import gaps now stay null instead of silently routing
  through a generic stub
- known Quake Live-specific rows such as UI advert/cursor slots and cgame
  avatar/advert slots remain explicitly assigned
- the source-only compatibility tail beyond the recovered retail slabs remains
  populated so the rebuilt native DLLs still load through the current host

## Verification

Updated coverage landed in:

- `tests/test_platform_services.py`

Command run:

```text
python -m pytest tests/test_steamworks_harness.py tests/test_platform_services.py tests/test_ui_menu_files.py -q
```

Result:

- `80 passed`

## Outcome

This round did not add new address aliases. It consumed already-mapped host
ownership in one concrete way:

- the UI and cgame native import slabs now preserve unmapped retail gaps as
  null entries, matching the stricter qagame host shape instead of masking
  those gaps behind a generic `return 0` stub

Estimated parity for this round: `86% -> 87%`.
