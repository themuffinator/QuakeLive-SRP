# Network Client Message Sideband Producers - 2026-06-05

## Scope

This note maps the retail producer sites behind `sub_4AF4D0` / `data_565948`,
the client-message sideband byte written by protocol 91 `CL_WritePacket`.

No runtime launch was required. The pass used the committed
`quakelive_steam.exe` HLIL and Ghidra corpus, then applied conservative source
patches for the observed constant high bit, the `CL_Frame` viewangle-delta bit,
the renderer low-five node-count replacement, and the native cgame import guard.

## Evidence Used

Owning retail binary:

- `assets/quakelive/quakelive_steam.exe`

Committed reference corpus:

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`
- `references/analysis/quakelive_symbol_aliases.json`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part07.txt`

Source touched:

- `src/code/client/cl_input.c`
- `src/code/client/cl_cgame.c`
- `src/code/client/cl_main.c`
- `src/code/client/client.h`
- `src/code/renderer/tr_cmds.c`
- `src/code/renderer/tr_public.h`

## Observed Producer Map

`sub_4AF4D0` is a six-byte retail helper that returns `data_565948`. The full
committed HLIL split only references that global at the following sites:

| Mask | Site | Observed behavior | Source status |
| ---: | --- | --- | --- |
| `0x80` | data initializer `0x00565948` | `data_565948` starts at `0x80`. | Implemented as the persistent `CL_RetailClientMessageFlags()` initializer. |
| `0x1f` | `sub_43C120` / `R_PerformanceCounters` | Replaces the low five bits with `sub_4D8970(..., 0x20, data_1745edc)` output. | Implemented via renderer import callback from `R_PerformanceCounters()` before counter clear. |
| `0x40` | `sub_4B0A50` | ORs `0x40` when `data_565a74` / `data_565a88` differ from expected function pointers. | Implemented by checking the matching native cgame import slots in `CL_Frame`. |
| `0x20` | `sub_4BC3E0` / `CL_Frame` | ORs `0x20` when viewangle globals differ after `sub_4BE3A0()` / `SCR_UpdateScreen()`. | Implemented by comparing `cl.viewangles[YAW]` and `cl.viewangles[PITCH]` across `SCR_UpdateScreen()`. |

## Interpretation

Observed facts:

- `data_565948` initializes to `0x80`.
- `sub_4AF4D0` returns `data_565948` directly.
- The low five bits are replaced without clearing the upper bits.
- The `0x20` and `0x40` producers OR their bits and no committed HLIL writer
  clears them.

Inferences:

- The low five bits are the clamped renderer front-end node/leaf visit count.
  `sub_43C120` maps to `R_PerformanceCounters`, and `sub_4D8970(0, 0x20,
  data_1745edc)` is a clamp to `0..32` before the assignment masks to `0x1f`.
- The `0x40` producer is a native cgame import-slab integrity guard. Round 20
  already maps `data_565a74` / `sub_4B0000` as
  `QLCGImport_R_AddRefEntityToScene` and `data_565a88` / `sub_4BEF80` as
  `QLCGImport_R_RenderScene`.
- The `0x20` producer is a client pitch/yaw delta bit across the screen-update
  frame call. Retail snapshots the values after `CL_SetCGameTime`, calls
  `SCR_UpdateScreen`, then raises the sticky sideband bit if either changed.

## Source Status

`CL_RetailClientMessageFlags()` now returns a persistent flag byte initialized
to `0x80`, matching the retail global initializer. `CL_Frame` also snapshots
pitch/yaw before `SCR_UpdateScreen()` and raises the sticky `0x20` flag if the
screen/cgame frame mutates either angle. Because `CL_SendCmd()` runs before the
screen update in the same frame, this naturally affects subsequent client
packets, matching the retail call order.

The renderer low-five producer is also reconstructed. Source keeps the renderer
module boundary by adding a `refimport_t` callback:
`R_PerformanceCounters()` reports `tr.pc.c_leafs` before clearing `tr.pc` and
`backEnd.pc`, and `CL_SetRetailClientMessageRendererNodeCount()` replaces the
sideband low five bits with `clamp(nodeCount, 0, 32) & 0x1f` through the same
XOR replacement form observed in retail.

The `0x40` import guard is reconstructed too. `CL_Frame()` calls
`CL_CheckCGameNativeImportIntegrity()` before `CL_SetCGameTime()`, matching the
retail call window. The source check compares
`CG_QL_IMPORT_R_ADDREFENTITYTOSCENE` and `CG_QL_IMPORT_R_RENDERSCENE` against
their expected wrapper functions and raises the sticky `0x40` sideband bit if
either slot diverges.

All observed retail sideband producer sites are now source-modeled. The only
remaining sideband work is capture-diffing client packet bytes against retail.

Estimated parity movement for this residual slice:

- Focused sideband producer slice: `88%` before, `100%` after.
- Overall network-protocol parity: `89%` before, `90%` after.
