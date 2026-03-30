# Quake Live Steam Host Mapping Round 87

## Scope

This round closes the next bounded `quakelive_steam.exe` host compatibility
slice at the module-side native syscall wrapper boundary:

- explicit `qboolean` normalization in UI native syscall wrappers
- explicit `qboolean` normalization in cgame native syscall wrappers
- explicit `qboolean` normalization in qagame native syscall wrappers

The evidence stayed inside the committed corpus plus the writable source tree:

- `src/code/ui/ui_syscalls.c`
- `src/code/cgame/cg_syscalls.c`
- `src/code/game/g_syscalls.c`
- `src/code/ui/ui_local.h`
- `src/code/cgame/cg_local.h`
- `src/code/game/g_local.h`
- `tests/test_platform_services.py`

## Module-side native syscall `qboolean` boundary

The previous rounds tightened the host-side boolean contract in:

- direct `VM_Call(...)` owners
- the central native export dispatch in `vm.c`
- the host-side native import/syscall bridges in `cl_ui.c`, `cl_cgame.c`, and
  `sv_game.c`
- the UI/cgame native import slabs themselves

Observed facts from the module-side wrappers before this round:

- many `qboolean`-typed UI wrappers in `ui_syscalls.c` still returned raw
  `syscall(...)` integers or forwarded raw `qboolean` arguments directly
- many `qboolean`-typed cgame wrappers in `cg_syscalls.c` still returned raw
  `syscall(...)` integers or forwarded raw `qboolean` arguments directly
- many `qboolean`-typed qagame wrappers in `g_syscalls.c` still returned raw
  `syscall(...)` integers or forwarded raw `qboolean` arguments directly

That left the module-owned public trap surface relying on implicit integer
truthiness even after the host-side seams had been tightened.

## Retained source changes

The writable module-side wrappers now normalize the documented boolean imports
and results explicitly:

- `src/code/ui/ui_syscalls.c`
  - normalizes `trap_S_RegisterSound`, key state wrappers, LAN visibility
    wrappers, `trap_VerifyCDKey`, cursor helpers, app-subscription helpers, and
    the `forceColor` flag used by `trap_QL_DrawScaledText`
- `src/code/cgame/cg_syscalls.c`
  - normalizes looping-sound, register-sound, snapshot, server-command,
    usercmd, key state, entity-token, and `R_inPVS` wrappers
- `src/code/game/g_syscalls.c`
  - normalizes SteamID/auth wrappers, achievement/rank-state wrappers,
    `trap_RankReportInt`, PVS/portal-state wrappers, area/entity-contact
    wrappers, and the entity-token wrapper

That closes the same boolean contract band on the module-owned side instead of
leaving the DLL-facing trap layer to rely on raw integer spellings.

## Verification

Updated coverage landed in:

- `tests/test_platform_services.py`

Command run:

```text
python -m pytest tests/test_steamworks_harness.py tests/test_platform_services.py tests/test_ui_menu_files.py -q
```

Result:

- `81 passed`

## Outcome

This round did not add new address aliases. It consumed already-mapped host
ownership in one concrete way:

- the UI, cgame, and qagame native syscall wrappers now enforce explicit
  `qtrue` / `qfalse` normalization for their documented boolean args/results
  instead of exposing raw integer truthiness through the public module-side
  trap surface

Estimated parity for this round: `87% -> 88%`.
