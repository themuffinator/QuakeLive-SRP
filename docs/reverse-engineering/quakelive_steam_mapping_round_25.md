# Quake Live Steam Host Mapping Round 25

## Scope

This round closes two long-bounded native `cgamex86.dll` import gaps in `quakelive_steam.exe`:

- the raw pre-sound slot at `data_5659E8`
- the renderer-side gap at `data_565AA4` between the already-mapped `R_LerpTag` and `GetGlconfig` imports

The primary local evidence for this round is:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `src/code/client/cl_cgame.c`
- `src/code/client/ql_cgame_imports.inc`
- `src/code/cgame/cg_syscalls.c`
- `src/code/cgame/cg_marks.c`
- `src/code/cgame/cg_servercmds.c`

## Raw Offset `0x90`: `CM_MarkFragments`

`sub_4AFE00` is now exact.

Observed local facts:

1. The host raw cgame import slab contains `data_5659E8 = sub_4AFE00`, immediately ahead of the already-closed raw sound band that starts at `data_5659EC`.
2. `sub_4AFE00` is a pure jump through `data_146CCBC`, so it is a thin import wrapper rather than independent engine logic.
3. Retail native cgame calls this raw slot with the exact seven-argument mark-fragment shape in multiple places:
   - `(*(eax_13 + 0x90))(4, &arg_68, &arg_5c, 0x180, &arg_588, 0x80, &arg_188)`
   - `(*(eax_24 + 0x90))(4, &arg_68, &arg_5c, 0x180, &arg_588, 0x80, &arg_188)`
   - `(*(edx_3 + 0x90))(4, &arg_60, &arg_54, 0x180, &arg_580, 0x80, &arg_180)`
4. That argument pattern matches `trap_CM_MarkFragments( numPoints, points, projection, maxPoints, pointBuffer, maxFragments, fragmentBuffer )` exactly.
5. The local cgame source in `cg_marks.c` uses the same concrete call shape:
   - `trap_CM_MarkFragments( 4, (void *)originalPoints, projection, MAX_MARK_POINTS, markPoints[0], MAX_MARK_FRAGMENTS, markFragments )`
6. In the local import table, `CG_CM_MARKFRAGMENTS` is the last collision-model import immediately before `CG_S_STARTSOUND`, matching the retail slab placement just ahead of the raw sound band.

That closes the last unresolved raw pre-sound import wrapper as the native cgame `CM_MarkFragments` seam.

## Native Cgame Renderer Gap At `0x14C`: `R_RemapShader`

`sub_4B0100` is now stable enough to promote.

Observed local facts:

1. The host native cgame slab contains:
   - `data_565AA0 = sub_4B00D0` (`R_LerpTag`, already mapped)
   - `data_565AA4 = sub_4B0100`
   - `data_565AA8 = sub_4BF070` (`GetGlconfig`, already mapped)
2. `sub_4B0100` is a pure jump through `data_146CCCC`, so it is another thin import wrapper owned by the same renderer/state-query band from Round 17.
3. In the local cgame import dispatch, `CG_R_REMAP_SHADER` sits exactly between `CG_R_LERPTAG` and `CG_GETGLCONFIG`.
4. `cg_syscalls.c` exposes the matching three-string trap surface:
   - `trap_R_RemapShader( const char *oldShader, const char *newShader, const char *timeOffset )`
5. `cl_cgame.c` routes that import directly to the renderer interface:
   - `re.RemapShader( VMA(1), VMA(2), VMA(3) )`
6. The local cgame logic uses that trap in the exact shader-remap paths:
   - `CG_ShaderStateChanged()` parses `CS_SHADERSTATE` and calls `trap_R_RemapShader( originalShader, newShader, timeOffset )`
   - the `"remapShader"` server-command path also calls `trap_R_RemapShader( CG_Argv(1), CG_Argv(2), CG_Argv(3) )`

This is one step more inferential than `sub_4AFE00` because I do not yet have a singled-out raw retail HLIL callsite printed with `+ 0x14C`, but the slab position, adjacent mapped anchors, and exact source-side import order make the ownership stable enough to promote.

## Promoted Aliases

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4AFE00` (`0x004AFE00`) | `QLCGImport_CM_MarkFragments` | Observed | Raw native cgame import wrapper for collision-model mark fragmentation. |
| `sub_4B0100` (`0x004B0100`) | `QLCGImport_R_RemapShader` | Observed plus bounded inference | Native cgame import wrapper for renderer shader remapping. |

## Open Questions

1. `sub_4B0330` is still the most likely `GetEntityToken` wrapper from the post-cinematic seam, but I still do not have a direct retail cgame callsite strong enough to promote it.
2. The paired no-arg `0x1C8` / `0x1CC` seam and the vector/math seam at `0x1E0` / `0x1E4` remain bounded but unnamed; the current HLIL still proves usage more clearly than final API ownership.
3. The raw native cgame thunk at `0x4B02F0` remains semantically closed as `stopBackgroundTrack`, but it still does not have a stable committed Ghidra function row, so it stays documented-only.
