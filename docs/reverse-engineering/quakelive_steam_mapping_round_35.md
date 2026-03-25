# Quake Live Steam Host Mapping Round 35

## Scope

This round revisits the raw native `cgamex86.dll` renderer seam that was left partly open after Round 27.

The main goal was to stop treating `sub_4B0040` as an isolated sibling thunk and instead anchor it against the retail renderer export table returned by `GetRefAPI`. Once that table was pinned, the same pass also closed several exact engine-side scene/draw helpers that were already bounded structurally but still unnamed in the alias table.

The primary local evidence for this round is:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `src/code/renderer/tr_init.c`
- `src/code/renderer/tr_scene.c`
- `src/code/renderer/tr_light.c`
- `src/code/renderer/tr_cmds.c`
- `src/code/renderer/tr_public.h`

## Renderer Export Table Anchor In `GetRefAPI`

The decisive signal for this pass is the explicit renderer export table assembly in the host binary.

Observed local facts:

1. `sub_449F70` builds the retail `refexport_t` table at `data_587848`.
2. The relevant assignments in that table are:
   - `data_58786C = sub_450840`
   - `data_587870 = sub_450CD0`
   - `data_587874 = sub_4508C0`
   - `data_587878 = sub_44B060`
   - `data_58787C = sub_450E00`
   - `data_587880 = sub_450E40`
   - `data_587884 = sub_450E80`
   - `data_587888 = sub_43C650`
   - `data_58788C = sub_43C6C0`
3. The local source assigns the same export-table run in `tr_init.c`:
   - `re.ClearScene = RE_ClearScene;`
   - `re.AddRefEntityToScene = RE_AddRefEntityToScene;`
   - `re.AddPolyToScene = RE_AddPolyToScene;`
   - `re.LightForPoint = R_LightForPoint;`
   - `re.AddLightToScene = RE_AddLightToScene;`
   - `re.AddAdditiveLightToScene = RE_AddAdditiveLightToScene;`
   - `re.RenderScene = RE_RenderScene;`
   - `re.SetColor = RE_SetColor;`
   - `re.DrawStretchPic = RE_StretchPic;`

That gives a direct export-table ownership signal independent of the raw native cgame wrapper slab.

## `sub_4B0040`: Raw Native Cgame `LightForPoint`

The remaining raw wrapper at `data_565A84` now closes exactly.

Observed local facts:

1. `data_565A84 = sub_4B0040`.
2. `sub_4B0040` is a pure jump through `data_146CC90`.
3. The neighboring stable wrappers were already closed:
   - `sub_4B0030 -> data_146CC8C` (`QLCGImport_R_AddPolysToScene`)
   - `sub_4BEF50 -> data_146CC94` (`QLCGImport_R_AddLightToScene`)
4. The `GetRefAPI` export-table run places `sub_44B060` between:
   - `sub_4508C0` (`RE_AddPolyToScene`)
   - `sub_450E00` (`RE_AddLightToScene`)
5. The copied wrapper target at `data_146CC90` therefore lands on the `LightForPoint` export between the already-identified poly and dynamic-light helpers.

That is the missing second signal Round 27 needed. `sub_4B0040` is the raw native cgame `LightForPoint` wrapper, not another light-submission helper.

## `sub_44B060`: Exact `R_LightForPoint`

The owning helper also closes directly from the body.

Observed local facts:

1. `sub_44B060` has the exact four-vector signature shape from `R_LightForPoint(point, ambientLight, directedLight, lightDir)`.
2. It immediately returns `0` when `*(data_1716EC4 + 0xEC) == 0`, which matches the local source guard:
   - `if ( tr.world->lightGridData == NULL ) return qfalse;`
3. It zeroes a local `0xC0`-sized temporary entity block.
4. It copies the input point into that local entity origin.
5. It calls `sub_44A810`, the host helper that populates entity lighting from the light grid.
6. It copies three output vectors back to the caller:
   - ambient light
   - directed light
   - light direction
7. It returns `1` on success.

That matches the local `tr_light.c` implementation of `R_LightForPoint` exactly.

## Exact Scene And Draw Helper Closures

The same export-table anchor also closes several exact renderer helpers that were already bracketed by wrapper ownership.

### `sub_450840`: `RE_ClearScene`

Observed local facts:

1. `sub_450840` stores:
   - `data_1716DEC = data_1716DE8`
   - `data_1716DFC = data_1716DE4`
   - `data_1716DF4 = data_1716E00`
2. The local source `RE_ClearScene` does exactly:
   - `r_firstSceneDlight = r_numdlights;`
   - `r_firstSceneEntity = r_numentities;`
   - `r_firstScenePoly = r_numpolys;`
3. `GetRefAPI` assigns `sub_450840` to `re.ClearScene`.

That is an exact body-level match.

### `sub_450CD0`: `RE_AddRefEntityToScene`

Observed local facts:

1. The body emits:
   - `RE_AddRefEntityToScene: bad reType %i`
2. It copies `0x8C` bytes from the caller entity into the frame entity buffer.
3. It clears the per-entity `lightingCalculated` flag.
4. It increments the scene entity count.
5. `GetRefAPI` assigns `sub_450CD0` to `re.AddRefEntityToScene`.

That matches `tr_scene.c` exactly.

### `sub_450E80`: `RE_RenderScene`

Observed local facts:

1. The body logs:
   - `====== RE_RenderScene =====\n`
2. It early-outs on the same renderer registration and `r_norefresh` conditions as the local source.
3. It copies the incoming `refdef_t` into the active renderer frame state.
4. `GetRefAPI` assigns `sub_450E80` to `re.RenderScene`.

That is the exact render-scene entry point.

### `sub_43C650`: `RE_SetColor`

Observed local facts:

1. The helper takes one pointer argument.
2. It writes a small render command with command id `1`.
3. When the argument is null it substitutes the white RGBA block at `data_55C310`.
4. It copies four float color components into the queued command.
5. The local source `RE_SetColor` has the same null-to-white fallback and four-float command write.
6. `GetRefAPI` assigns `sub_43C650` to `re.SetColor`.

That is exact ownership, not just slot-order inference.

### `sub_43C6C0`: `RE_StretchPic`

Observed local facts:

1. The helper takes eight floats plus a shader handle.
2. It writes a render command with command id `2`.
3. It resolves the incoming handle through `sub_458A40(arg9)`, matching `R_GetShaderByHandle`.
4. It stores:
   - `x, y, w, h`
   - `s1, t1, s2, t2`
   - shader pointer
5. The local source `RE_StretchPic` has the same argument shape and command-buffer write.
6. `GetRefAPI` assigns `sub_43C6C0` to `re.DrawStretchPic`.

The engine-side helper name should therefore follow the source implementation name: `RE_StretchPic`.

## Promoted Aliases

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_43C650` (`0x0043C650`) | `RE_SetColor` | Observed | Exact renderer command helper for `SetColor`, including the null-to-white fallback. |
| `sub_43C6C0` (`0x0043C6C0`) | `RE_StretchPic` | Observed | Exact renderer command helper for stretch-pic submission. |
| `sub_44B060` (`0x0044B060`) | `R_LightForPoint` | Observed | Exact renderer light-grid query helper returning ambient, directed, and light-direction vectors for one point. |
| `sub_450840` (`0x00450840`) | `RE_ClearScene` | Observed | Exact renderer helper that snapshots the current scene counts into the first-scene markers. |
| `sub_450CD0` (`0x00450CD0`) | `RE_AddRefEntityToScene` | Observed | Exact renderer helper for scene entity submission. |
| `sub_450E80` (`0x00450E80`) | `RE_RenderScene` | Observed | Exact renderer scene entry point. |
| `sub_4B0040` (`0x004B0040`) | `QLCGImport_R_LightForPoint` | Observed | Raw native cgame import wrapper for the renderer light-grid point query. |

## Open Questions

1. The literal thunk at `0x4B0050` still lacks a stable committed `functions.csv` row, so I am not promoting its raw wrapper even though the surrounding renderer export slice is now much clearer.
2. This round intentionally does not rename the remaining hidden scene-export gaps implied by the copied wrapper table; it promotes only the helpers whose ownership closes from explicit export-table assignment plus body or call-shape evidence.
