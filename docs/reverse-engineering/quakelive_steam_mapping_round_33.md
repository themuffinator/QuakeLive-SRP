# Quake Live Steam Host Mapping Round 33

## Scope

This round closes the raw native `cgamex86.dll` command-and-collision seam immediately before the already-mapped sound band at `data_5659EC`.

The focus was the stable wrapper block at host raw offsets `+0x54..+0x8C`, plus the owning engine helpers behind that block. The goal was to promote only the entries whose public behavior is pinned by both:

- committed `functions.csv` rows in the `quakelive_steam` Ghidra corpus
- direct raw `data_1074CCCC + offset` call shapes in native `cgamex86.dll`
- the current reconstructed syscall table in `src/code/client/cl_cgame.c`

The primary local evidence for this round is:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `src/code/client/cl_cgame.c`
- `src/code/client/ql_cgame_imports.inc`
- `src/code/client/cl_main.c`
- `src/code/qcommon/cmd.c`
- `src/code/qcommon/cm_load.c`
- `src/code/qcommon/cm_public.h`
- `src/code/qcommon/cm_test.c`
- `src/code/qcommon/cm_trace.c`

## Raw Command Helpers At `+0x54..+0x5C`

The command side of the raw native cgame slab now closes cleanly.

Observed local facts:

1. The owning host slots are:
   - `data_5659AC = sub_4AFC40` (`+0x54`)
   - `data_5659B0 = sub_4AFC60` (`+0x58`)
   - `data_5659B4 = sub_4AFC70` (`+0x5C`)
2. Native cgame uses raw `+0x54` as a one-string command registrar during startup:
   - `(*(data_1074CCCC + 0x54))("abort")`
   - `(*(data_1074CCCC + 0x54))("callvote")`
   - `(*(data_1074CCCC + 0x54))("vote")`
3. `sub_4AFC40` tailcalls `sub_4C81D0(arg1, 0)`.
4. `sub_4C81D0` emits the exact duplicate-command string:
   - `Cmd_AddCommand: %s already defined\n`
5. The source-side syscall table matches that role directly:
   - `cl_cgame.c`: `case CG_ADDCOMMAND: CL_AddCgameCommand( VMA(1) );`
   - `CL_AddCgameCommand` immediately forwards to `Cmd_AddCommand( cmdName, NULL );`
6. Native cgame uses raw `+0x5C` as a one-string reliable-command path:
   - `"dropflag"`
   - `"readyup"`
   - formatted `"tell %i %s"`
   - formatted `"teamtask %d\n"`
7. `sub_4AFC70` tailcalls `sub_4B8200`, and `sub_4B8200` emits:
   - `Client command overflow`
8. The source-side syscall table matches that role directly:
   - `cl_cgame.c`: `case CG_SENDCLIENTCOMMAND: CL_AddReliableCommand( VMA(1) );`
9. `sub_4AFC60` tailcalls `sub_4C8270`, whose linked-list walk matches `Cmd_RemoveCommand`.

That gives exact wrapper ownership for `AddCommand`, `RemoveCommand`, and `SendClientCommand`, and it also closes the underlying engine helpers behind those wrappers.

## Raw Collision Setup At `+0x64..+0x7C`

The collision-map load, inline-model, temp-model, and point-content helpers are now stable.

Observed local facts:

1. The owning host slots are:
   - `data_5659BC = sub_4AFC80` (`+0x64`)
   - `data_5659C0 = j_sub_4C0240` (`+0x68`, documented only)
   - `data_5659C4 = sub_4AFCB0` (`+0x6C`)
   - `data_5659C8 = sub_4AFCC0` (`+0x70`)
   - `data_5659CC = sub_4AFCE0` (`+0x74`)
   - `data_5659D0 = sub_4AFD00` (`+0x78`)
   - `data_5659D4 = sub_4AFD10` (`+0x7C`)
2. Native cgame calls raw `+0x64` with the current map name during media init:
   - `(*(data_1074CCCC + 0x64))(0x10A3FF64)`
3. `sub_4AFC80` tailcalls `sub_4C0580`, and `sub_4C0580` emits the exact debug string:
   - `CM_LoadMap( %s, %i )\n`
4. `sub_4AFCB0` tailcalls `sub_4C0210`, and `sub_4C0210` emits:
   - `CM_InlineModel: bad number`
5. `j_sub_4C0240` returns `data_146CBB8`, which is the raw `CM_NumInlineModels` count surface, but the committed corpus still does not expose a stable wrapper row for JSON promotion.
6. `sub_4AFCC0` and `sub_4AFCE0` both tailcall `sub_4C0400(mins, maxs, capsuleFlag)`:
   - `sub_4AFCC0 -> ... , 0`
   - `sub_4AFCE0 -> ... , 1`
7. That exactly matches the current syscall split:
   - `CG_CM_TEMPBOXMODEL -> CM_TempBoxModel(..., qfalse)`
   - `CG_CM_TEMPCAPSULEMODEL -> CM_TempBoxModel(..., qtrue)`
8. `sub_4AFD00` tailcalls `sub_4C4A50(point, model)`, matching `CM_PointContents`.
9. `sub_4AFD10` tailcalls `sub_4C4C10(point, model, origin, angles)`, matching `CM_TransformedPointContents`.

That closes the raw collision-setup seam through transformed point contents.

## Raw Trace Helpers At `+0x80..+0x8C`

The trace half of the seam also closes exactly.

Observed local facts:

1. The owning host slots are:
   - `data_5659D8 = sub_4AFD20` (`+0x80`)
   - `data_5659DC = sub_4AFD50` (`+0x84`)
   - `data_5659E0 = sub_4AFD80` (`+0x88`)
   - `data_5659E4 = sub_4AFDC0` (`+0x8C`)
2. `sub_4AFD20` and `sub_4AFD50` tailcall `sub_4C78C0(..., capsuleFlag)`:
   - `sub_4AFD20 -> ... , 0`
   - `sub_4AFD50 -> ... , 1`
3. The raw native cgame callers at `+0x80` use the exact `trace_t*, start, end, mins, maxs, model, brushmask` shape from `CM_BoxTrace`.
4. The current syscall table matches the same split:
   - `CG_CM_BOXTRACE -> CM_BoxTrace(..., qfalse)`
   - `CG_CM_CAPSULETRACE -> CM_BoxTrace(..., qtrue)`
5. `sub_4AFD80` and `sub_4AFDC0` tailcall `sub_4C7900(..., origin, angles, capsuleFlag)`:
   - `sub_4AFD80 -> ... , 0`
   - `sub_4AFDC0 -> ... , 1`
6. Native cgame uses raw `+0x88` with the exact transformed-trace argument shape:
   - `trace_t*`
   - `start`
   - `end`
   - `mins`
   - `maxs`
   - `model`
   - `brushmask`
   - `origin`
   - `angles`
7. The current syscall table again matches the same split:
   - `CG_CM_TRANSFORMEDBOXTRACE -> CM_TransformedBoxTrace(..., qfalse)`
   - `CG_CM_TRANSFORMEDCAPSULETRACE -> CM_TransformedBoxTrace(..., qtrue)`

That gives exact ownership for both the wrappers and the shared trace helpers underneath them.

## Documented-Only Gaps In This Band

Two small raw entries are semantically closed but still JSON-ineligible at the current committed-corpus granularity:

1. `data_5659B8 = 0x4BEFA0` (`+0x60`) is the native cgame `UpdateScreen` slot.
   - Native cgame calls it repeatedly during lengthy loading passes just before progress-frame updates.
   - `cl_cgame.c` documents the same `CG_UPDATESCREEN` purpose directly above `SCR_UpdateScreen();`
   - The committed Ghidra export still does not expose a stable `004BEFA0` function row.
2. `data_5659C0 = j_sub_4C0240` (`+0x68`) is the native cgame `CM_NumInlineModels` slot.
   - `sub_4C0240` returns the inline-model count directly.
   - The committed Ghidra export still does not expose a stable wrapper row for `004AFCA0` or `004C0240`.

I am leaving both documented-only in this round.

## Promoted Aliases

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4AFC40` (`0x004AFC40`) | `QLCGImport_AddCommand` | Observed | Raw native cgame import wrapper for `trap_AddCommand`, forwarding to the command-registration path with a null function pointer. |
| `sub_4AFC60` (`0x004AFC60`) | `QLCGImport_RemoveCommand` | Observed | Raw native cgame import wrapper for `trap_RemoveCommand`. |
| `sub_4AFC70` (`0x004AFC70`) | `QLCGImport_SendClientCommand` | Observed | Raw native cgame import wrapper for `trap_SendClientCommand`, forwarding to the reliable-command queue. |
| `sub_4AFC80` (`0x004AFC80`) | `QLCGImport_CM_LoadMap` | Observed | Raw native cgame import wrapper for `trap_CM_LoadMap`. |
| `sub_4AFCB0` (`0x004AFCB0`) | `QLCGImport_CM_InlineModel` | Observed | Raw native cgame import wrapper for `trap_CM_InlineModel`. |
| `sub_4AFCC0` (`0x004AFCC0`) | `QLCGImport_CM_TempBoxModel` | Observed | Raw native cgame import wrapper for `trap_CM_TempBoxModel`. |
| `sub_4AFCE0` (`0x004AFCE0`) | `QLCGImport_CM_TempCapsuleModel` | Observed | Raw native cgame import wrapper for `trap_CM_TempCapsuleModel`. |
| `sub_4AFD00` (`0x004AFD00`) | `QLCGImport_CM_PointContents` | Observed | Raw native cgame import wrapper for `trap_CM_PointContents`. |
| `sub_4AFD10` (`0x004AFD10`) | `QLCGImport_CM_TransformedPointContents` | Observed | Raw native cgame import wrapper for `trap_CM_TransformedPointContents`. |
| `sub_4AFD20` (`0x004AFD20`) | `QLCGImport_CM_BoxTrace` | Observed | Raw native cgame import wrapper for `trap_CM_BoxTrace`. |
| `sub_4AFD50` (`0x004AFD50`) | `QLCGImport_CM_CapsuleTrace` | Observed | Raw native cgame import wrapper for `trap_CM_CapsuleTrace`. |
| `sub_4AFD80` (`0x004AFD80`) | `QLCGImport_CM_TransformedBoxTrace` | Observed | Raw native cgame import wrapper for `trap_CM_TransformedBoxTrace`. |
| `sub_4AFDC0` (`0x004AFDC0`) | `QLCGImport_CM_TransformedCapsuleTrace` | Observed | Raw native cgame import wrapper for `trap_CM_TransformedCapsuleTrace`. |
| `sub_4B8200` (`0x004B8200`) | `CL_AddReliableCommand` | Observed | Retail reliable-command enqueue helper used by raw native cgame `SendClientCommand`. |
| `sub_4C0210` (`0x004C0210`) | `CM_InlineModel` | Observed | Retail inline-model lookup helper. |
| `sub_4C0400` (`0x004C0400`) | `CM_TempBoxModel` | Observed | Retail temp collision-model builder shared by the box and capsule wrappers through the final mode flag. |
| `sub_4C0580` (`0x004C0580`) | `CM_LoadMap` | Observed | Retail collision-map load helper. |
| `sub_4C4A50` (`0x004C4A50`) | `CM_PointContents` | Observed | Retail point-contents helper. |
| `sub_4C4C10` (`0x004C4C10`) | `CM_TransformedPointContents` | Observed | Retail transformed point-contents helper. |
| `sub_4C78C0` (`0x004C78C0`) | `CM_BoxTrace` | Observed | Retail box-trace helper shared by the box and capsule wrappers through the final mode flag. |
| `sub_4C7900` (`0x004C7900`) | `CM_TransformedBoxTrace` | Observed | Retail transformed box-trace helper shared by the transformed box and transformed capsule wrappers through the final mode flag. |
| `sub_4C81D0` (`0x004C81D0`) | `Cmd_AddCommand` | Observed | Retail command-registration helper used by `CL_AddCgameCommand`. |
| `sub_4C8270` (`0x004C8270`) | `Cmd_RemoveCommand` | Observed | Retail command-removal helper. |

## Open Questions

1. `0x004BEFA0` is now semantically bounded as the raw native cgame `UpdateScreen` thunk, but it still lacks a stable committed Ghidra function row for JSON aliasing.
2. `j_sub_4C0240` is likewise semantically closed as `CM_NumInlineModels`, but it still lacks a stable committed wrapper row for promotion.
3. This round intentionally does not revisit the earlier unresolved advertisement-bridge helpers (`sub_4F1F10`, `sub_4F1FC0`, `sub_4F21C0`) or the renderer-side `sub_4B0040`; those remain separate seams with weaker public call contracts.
