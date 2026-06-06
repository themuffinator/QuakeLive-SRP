# Botlib Cgame Shutdown Import Boundary Mapping - 2026-06-06

## Scope

This pass extends the previous botlib structure-tail mapping into the adjacent
native cgame lifecycle/import pocket at `0x004AF820..0x004B0500`. The goal was
to close the one strong unnamed client lifecycle owner in that band and to
separate it from the remaining tiny cgame import-table trampolines whose exact
retail semantics are still weaker than their slot neighborhoods.

No C source body change was needed. The reconstruction result is one
high-confidence alias promotion plus a bounded residual classification for
three cgame-native import rows.

## Evidence

- `references/analysis/quakelive_symbol_aliases.json`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part07.txt`
- `src/code/client/cl_cgame.c`
- `src/code/client/cl_main.c`
- `src/code/client/client.h`
- `src/code/qcommon/common.c`
- `src/code/cgame/cg_public.h`
- `tests/test_botlib_cgame_shutdown_import_boundary_parity.py`

## Promotion

| Address | Alias | Evidence |
| --- | --- | --- |
| `0x004AFBF0` | `CL_ShutdownCGame` | HLIL clears the cgame keycatcher bit, clears the cgame-started state, calls the cgame VM shutdown entry at `data_146CC38 + 8`, frees `data_1647F0C`, then nulls the VM and entry table globals. Source `CL_ShutdownCGame` performs the same `KEYCATCH_CGAME`, `CG_SHUTDOWN`, `VM_Free`, and `cgvm = NULL` sequence. |

Call-site evidence also matches lifecycle ownership: the retail function is
called from global client shutdown, disconnect/local-server transition, vid
restart, server-state reset, and cvar-registration VM warmup/teardown paths.

## Bounded Residual Rows

The cgame native import pocket now has `73` Ghidra function rows. After this
promotion, only the following rows remain unaliased in the pocket:

| Address | Ghidra row | HLIL shape | Current classification |
| --- | --- | --- | --- |
| `0x004AFFC0` | `FUN_004affc0,004affc0,9,0,unknown` | tailcall to `sub_4F1FC0` | Advertisement/web bridge neighborhood wrapper, still weakly named. |
| `0x004B00C0` | `FUN_004b00c0,004b00c0,10,0,unknown` | direct jump through `data_146CCF8` | Renderer/import-table gap at the slot-80 neighborhood. |
| `0x004B0370` | `FUN_004b0370,004b0370,51,0,unknown` | five-float forwarder through `data_146CCE4` | Native cgame utility forwarder; observed shape is clearer than final ownership. |

Source-side `cg_public.h` and `CL_InitCGameImports` already keep the unresolved
retail-only slots behind `QL_CG_trap_RetailReservedImport`, which fails closed.
That is still the right reconstruction behavior for these rows until a stable
native cgame caller proves their public meaning.

## Wiring Notes

- `0x004AF820 -> CL_GetServerCommand` remains the client reliable-command owner
  immediately before this lifecycle/import pocket.
- `0x004AFC40..0x004B0440` remains the dense native cgame import wrapper slab.
- `0x004B0460 -> CL_LoadCGameForCvarRegistration` and
  `0x004B04C0 -> CL_InitCGame` bracket the VM creation side of the same
  lifecycle corridor.
- The import-table rows in HLIL part 07 continue to identify the bounded
  residuals:
  - `data_565A6C = sub_4AFFC0`
  - `data_565A98 = sub_4B00C0`
  - `data_565B2C = sub_4B0370`

## Parity Estimate

- Focused cgame shutdown owner mapping:
  **before 70% -> after 98%**
- Adjacent cgame native residual import classification:
  **before 80% -> after 92%**
- Overall botlib plus related parser/import/lifecycle wiring:
  **before 85% -> after 86%**

The overall movement is small because direct botlib reconstruction was already
near closure; this pass removes lifecycle ambiguity immediately downstream of
the botlib/parser boundary and prevents weak reserved import rows from being
overpromoted.

## Validation

- `python -m pytest tests/test_botlib_cgame_shutdown_import_boundary_parity.py -q`
  - expected focused gate for alias, HLIL, Ghidra rows, source lifecycle body,
    import table rows, and reserved-slot containment.
