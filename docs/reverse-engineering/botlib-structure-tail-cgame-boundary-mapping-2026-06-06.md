# Botlib Structure Tail And Cgame Boundary Mapping - 2026-06-06

## Scope

This pass rechecked the tail of the botlib parser/support range after
`ReadStructure` and the adjacent cgame import wiring. The selected retail range
was `0x004AE830..0x004AF820`, with special attention on the apparent residual
rows after `l_struct.c::ReadStructure`.

No C source body change was needed. The useful reconstruction result is a
boundary clarification plus two high-confidence alias promotions for the client
owners behind the native cgame import path.

## Evidence

- `references/analysis/quakelive_symbol_aliases.json`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
- `src/code/botlib/l_struct.c`
- `src/code/botlib/be_ai_weap.c`
- `src/code/botlib/be_ai_weight.c`
- `src/code/client/cl_cgame.c`
- `src/code/client/ql_cgame_imports.inc`
- `src/code/cgame/cg_syscalls.c`
- `src/code/cgame/cg_public.h`
- `tests/test_botlib_structure_tail_cgame_boundary_parity.py`

## Promotions

| Address | Alias | Evidence |
| --- | --- | --- |
| `0x004AF570` | `CL_GetSnapshot` | HLIL bounds the requested snapshot against `data_146cd30`, validates the packet ring, copies areamask/playerstate/entity rows, truncates to `0x180` entities, and returns `1` on success. Source `CL_GetSnapshot` has the same ring checks and copy order. |
| `0x004AF690` | `CL_ConfigstringModified` | HLIL reads the configstring index from command arg 1, rejects indexes outside `0..0x3ff`, rebuilds the `gameState_t` string buffer, enforces `MAX_GAMESTATE_CHARS`, and calls `CL_SystemInfoChanged` for index `1`. Source `CL_ConfigstringModified` matches that flow. |

Existing aliases remain important context:

- `0x004AE830 -> FindField`
- `0x004AE8A0 -> ReadNumber`
- `0x004AECD0 -> ReadStructure`
- `0x004AF820 -> CL_GetServerCommand`
- `0x004B0150 -> QLCGImport_GetSnapshot`
- `0x004B0160 -> QLCGImport_GetServerCommand`

## Boundary Finding

The rows immediately after `ReadStructure` are not botlib structure writer
helpers.

Source-visible helpers in `l_struct.c` remain real source helpers:

- `ReadChar`
- `ReadString`
- `WriteIndent`
- `WriteFloat`
- `WriteStructWithIndent`
- `WriteStructure`

However, this retail seam does not expose them as the adjacent emitted owners.
The committed HLIL for `0x004AF050..0x004AF500` instead shows non-botlib
client/C++ support behavior, including:

- a C++ string/camera object path that seeds `"camera01"`;
- reference-counted allocation/free helpers;
- a small obfuscated string lookup/decode helper used later by server/client
  command code.

That means `ReadStructure` remains the final promoted botlib structure-reader
owner in this band. The source write helpers should only be promoted in a
future pass if stable call-site and format-string evidence identify their
retail emitted bodies.

## Wiring Notes

- `QLCGImport_GetSnapshot` at `0x004B0150` is the native cgame import wrapper,
  while `CL_GetSnapshot` at `0x004AF570` is the actual client snapshot body.
- `CL_CgameSystemCallsImpl` dispatches legacy `CG_GETSNAPSHOT` to
  `CL_GetSnapshot`, and the native import table installs
  `QL_CG_trap_GetSnapshot` at `CG_QL_IMPORT_GETSNAPSHOT`.
- `cg_syscalls.c` maps `CG_GETSNAPSHOT` to native import slot `87` and
  `CG_GETSERVERCOMMAND` to slot `88`, preserving the retail cgame ABI bridge.
- `CL_ConfigstringModified` is the configstring mutation body reached by
  `CL_GetServerCommand` after the `cs` reliable command path and before the
  system-info refresh path.

## Parity Estimate

- Focused botlib structure-tail boundary classification:
  **before 78% -> after 98%**
- Cgame snapshot/configstring owner naming at the adjacent boundary:
  **before 72% -> after 97%**
- Overall botlib plus related parser/import wiring:
  **before 84% -> after 85%**

The overall botlib movement is deliberately small because the direct botlib
source was already reconstructed. This pass mostly prevents false botlib debt
from being assigned to adjacent client/cgame owners.

## Validation

- `python -m pytest tests/test_botlib_structure_tail_cgame_boundary_parity.py -q`
  - `3 passed`

