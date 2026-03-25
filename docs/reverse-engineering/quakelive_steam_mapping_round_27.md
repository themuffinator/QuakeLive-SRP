# Quake Live Steam Host Mapping Round 27

## Scope

This round revisits the raw native `cgamex86.dll` renderer seam immediately after `AddRefEntityToScene` and promotes the stable poly and dynamic-light helpers that earlier passes had only bounded loosely.

The goal was to map the stable wrappers in the host slab around `data_565A78` and tie them back to the owning renderer helpers inside `quakelive_steam.exe` without forcing a weak name onto the remaining sibling thunk.

The primary local evidence for this round is:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `src/code/renderer/tr_scene.c`
- `src/code/renderer/tr_light.c`
- `src/code/renderer/tr_public.h`
- `src/code/renderer/tr_init.c`
- `src/code/cgame/cg_syscalls.c`
- `src/code/client/cl_cgame.c`

## `sub_4508C0`: `RE_AddPolyToScene`

`sub_4508C0` is now exact.

Observed local facts:

1. The committed Ghidra export exposes a stable `FUN_004508C0,004508c0,1031,0,unknown` row.
2. The body emits the exact warning strings:
   - `WARNING: RE_AddPolyToScene: NULL poly shader\n`
   - `WARNING: RE_AddPolyToScene: r_max_polys or r_max_polyverts reached\n`
3. It multiplies the vertex count by `0x18`, matching `sizeof(polyVert_t)`, and then copies repeated `polyVert_t` records into the renderer frame buffers.
4. It advances the same poly/polyvert frame counters and bounds checks that the local `RE_AddPolyToScene` source uses in `tr_scene.c`.
5. The two raw native cgame wrappers in this seam both forward into the same callback target, with `sub_4B0010` forcing the final `numPolys` argument to `1` and `sub_4B0030` forwarding the explicit count unchanged.

That gives exact ownership for the engine helper, not just for the wrapper pair.

## `sub_450D70`, `sub_450E00`, `sub_450E40`: Dynamic-Light Helper Split

This cluster is now stable enough to promote as the renderer dynamic-light path.

Observed local facts:

1. The committed Ghidra export exposes stable rows for all three helpers:
   - `FUN_00450D70,00450d70,138,0,unknown`
   - `FUN_00450E00,00450e00,49,0,unknown`
   - `FUN_00450E40,00450e40,49,0,unknown`
2. `sub_450D70` enforces the same guard sequence as the local `RE_AddDynamicLightToScene` source:
   - early out when the renderer is not registered
   - early out when the light count has reached `0x20`
   - early out when `intensity <= 0`
   - early out on the same two hardware-type values before storing the light
3. On success it writes a `0x2C`-sized record containing:
   - origin vector at offsets `0x00..0x08`
   - radius/intensity at `0x0C`
   - color triplet at `0x10..0x18`
   - additive flag at `0x28`
4. `sub_450E00` and `sub_450E40` are tiny wrappers over `sub_450D70` that differ only in the final flag they pass:
   - `sub_450E00(..., 0)`
   - `sub_450E40(..., 1)`
5. That matches the local renderer split exactly:
   - `RE_AddLightToScene` calls `RE_AddDynamicLightToScene(..., qfalse)`
   - `RE_AddAdditiveLightToScene` calls `RE_AddDynamicLightToScene(..., qtrue)`

This is one of the cleaner observed closures in the recent native cgame renderer passes because the body shape, guard logic, record layout, and wrapper split all line up at once.

## Raw Native Cgame Poly/Light Wrappers At `data_565A78..data_565A80`

The stable wrapper band in the raw host slab is now:

- `data_565A78 = sub_4B0010`
- `data_565A7C = sub_4B0030`
- `data_565A80 = sub_4BEF50`
- `data_565A84 = sub_4B0040` (still open)
- `data_565A88 = sub_4BEF80` (already promoted earlier)
- `data_565A8C = 0x4B0050` (literal thunk, still open)

### `sub_4B0010`: One-Poly Wrapper

Observed local facts:

1. `sub_4B0010` forwards to `data_146CC8C(arg1, arg2, arg3, 1)`.
2. `sub_4B0030` jumps to the same target without fixing the final argument.
3. That matches the local split between:
   - `trap_R_AddPolyToScene( hShader, numVerts, verts )`
   - `trap_R_AddPolysToScene( hShader, numVerts, verts, numPolys )`
4. The shared target aligns with the engine-side `RE_AddPolyToScene( ..., numPolys )` helper promoted above.

So `sub_4B0010` is the stable one-poly convenience wrapper over the same poly core.

### `sub_4B0030`: Multi-Poly Wrapper

Observed local facts:

1. `sub_4B0030` is a pure jump through the same callback target used by `sub_4B0010`.
2. Unlike `sub_4B0010`, it does not hardcode the final argument, so it preserves the explicit poly count from native cgame.
3. That makes it the raw native cgame wrapper for the multi-poly import surface, not a second alias for the one-poly convenience entry.

### `sub_4BEF50`: Stable Raw `AddLightToScene` Wrapper

`sub_4BEF50` is now stable enough to promote as the normal dynamic-light wrapper.

Observed local facts:

1. The committed Ghidra export exposes a stable `FUN_004BEF50,004bef50,48,0,unknown` row.
2. The host slab contains `data_565A80 = sub_4BEF50`.
3. `sub_4BEF50` forwards a point/vector pointer plus four scalar arguments through `data_146CC94`, which matches the `origin, intensity, r, g, b` light-shape surface rather than the poly or render-scene paths.
4. Retail native cgame calls raw slot `data_1074CCCC + 0x128` repeatedly with the exact dynamic-light tuple used by explosions, missiles, and player effects:
   - `(&var_10, 500f, 1f, 1f, 1f)`
   - `(&var_10, 500f, 1f, 0f, 0f)`
   - `(&arg1[0xAE], intensity, r, g, b)`
5. The local cgame code uses `trap_R_AddLightToScene` extensively in the matching effect paths, while `trap_R_AddAdditiveLightToScene` exists in the syscall surface but has no live cgame callsites in the current source tree.
6. The owning renderer helper split promoted above shows that the retail engine has a normal-light wrapper and an additive-light wrapper backed by the same dynamic-light core, so the heavily used raw retail slot is the normal path first.

This is still slightly weaker than the poly closure because the additive sibling thunk remains unnamed, but the raw call-shape evidence is now good enough to promote `sub_4BEF50` itself.

## Promoted Aliases

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4508C0` (`0x004508C0`) | `RE_AddPolyToScene` | Observed | Retail renderer helper for poly submission. |
| `sub_450D70` (`0x00450D70`) | `RE_AddDynamicLightToScene` | Observed | Retail renderer core for dynamic-light record submission. |
| `sub_450E00` (`0x00450E00`) | `RE_AddLightToScene` | Observed | Retail normal dynamic-light wrapper over `RE_AddDynamicLightToScene(..., 0)`. |
| `sub_450E40` (`0x00450E40`) | `RE_AddAdditiveLightToScene` | Observed | Retail additive dynamic-light wrapper over `RE_AddDynamicLightToScene(..., 1)`. |
| `sub_4B0010` (`0x004B0010`) | `QLCGImport_R_AddPolyToScene` | Observed | Raw native cgame wrapper that fixes `numPolys = 1` and forwards into the renderer poly helper. |
| `sub_4B0030` (`0x004B0030`) | `QLCGImport_R_AddPolysToScene` | Observed | Raw native cgame wrapper for the explicit multi-poly renderer import. |
| `sub_4BEF50` (`0x004BEF50`) | `QLCGImport_R_AddLightToScene` | Observed plus bounded inference | Raw native cgame wrapper for the normal dynamic-light renderer import. |

## Open Questions

1. `sub_4B0040` is still bounded only as the next sibling in this poly/light/render seam. It likely belongs to the remaining `LightForPoint` or additive-light surface, but I do not yet have the second direct retail signal needed to promote it.
2. The literal thunk at `0x4B0050` is still undocumented in committed `functions.csv`, so even though it sits immediately beside the stable light/render wrappers, it remains JSON-ineligible for now.
3. The retail placement of `LightForPoint` relative to the raw dynamic-light pair is still one step less explicit than the local reconstruction surface. This round intentionally promotes only the helpers whose ownership closes cleanly from the committed corpus.
