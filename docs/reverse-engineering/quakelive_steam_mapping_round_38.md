# Quake Live Steam Host Mapping Round 38

## Scope

This round closes another exact-match renderer tranche inside `quakelive_steam.exe`.

The focus here is the renderer-facing registration pipeline that still sat behind generic labels even though the committed HLIL and local source now bound it tightly: world-map loading, world-vis hookup, skin/shader registration, renderer shutdown and registration boundaries, the MD3/MD4 format loaders, and the remaining small model/skin console helpers that live directly beside those entry points.

The primary local evidence for this round is:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `src/code/renderer/tr_bsp.c`
- `src/code/renderer/tr_image.c`
- `src/code/renderer/tr_init.c`
- `src/code/renderer/tr_model.c`
- `src/code/renderer/tr_shader.c`

## Exact BSP Registration Exports

### `__initp_misc_invarg`: `RE_SetWorldVisData`

Observed local facts:

1. The `GetRefAPI` constructor exports this exact function in the `SetWorldVisData` slot immediately after `RE_LoadWorldMap`.
2. The body is only a one-field setter: it stores the incoming pointer into the renderer-global vis-data slot and returns the same pointer.
3. The later BSP visibility loader checks the same stored pointer and reuses it instead of allocating a new vis block, matching the source-side `tr.externalVisData` ownership.

That closes the misnamed `__initp_misc_invarg` slot as the exact `RE_SetWorldVisData`.

### `sub_43BF40`: `RE_LoadWorldMap`

Observed local facts:

1. The helper emits the exact redundant-load failure:
   - `ERROR: attempted to redundantly load world map\n`
2. It seeds the same default sun direction `{ 0.45f, 0.3f, 0.9f }` and normalizes it before marking the world as loaded.
3. It reads the incoming BSP through the renderer file import and emits the exact not-found error:
   - `RE_LoadWorldMap: %s not found`
4. It clears the world pointer, zeroes the world-data block, copies `name`, derives `baseName`, allocates the same start marker, and resets `c_gridVerts`.
5. It checks the BSP version against both accepted values and emits the exact version mismatch string:
   - `RE_LoadWorldMap: %s has wrong version number (%i should be %i or %i)`
6. It then swaps the header and dispatches into the same world-lump loader chain from `tr_bsp.c`.

That is the exact world-load export `RE_LoadWorldMap`.

## Exact Skin Registration And Helpers

### `sub_4479C0`: `RE_RegisterSkin`

Observed local facts:

1. The body emits both source validation strings:
   - `Empty name passed to RE_RegisterSkin\n`
   - `Skin name exceeds MAX_QPATH\n`
2. It linearly scans the loaded skin table for a case-insensitive name match and returns `0` for an already-known default skin whose surface count is zero.
3. It enforces `MAX_SKINS == 0x400` and emits the exact cap warning:
   - `WARNING: RE_RegisterSkin( '%s' ) MAX_SKINS hit\n`
4. On allocation it reserves `0xC4` bytes, copies the skin name, clears the surface count, and syncs the render thread before loading content.
5. For non-`.skin` names it creates a single-surface skin and resolves the shader through `R_FindShader( name, LIGHTMAP_NONE, qtrue )`.
6. For `.skin` files it reads the file, parses comma-delimited surface/shader pairs, lowercases surface names, skips `tag_` entries, allocates one surface record per parsed entry, and resolves each shader through the same shader lookup path.
7. It frees the file buffer and returns `0` when the final skin has no usable surfaces.

That is an exact match for `RE_RegisterSkin`.

### `sub_447C40`: `R_InitSkins`

Observed local facts:

1. The helper sets `tr.numSkins = 1`.
2. It allocates the default skin record and copies the exact name:
   - `<default skin>`
3. It sets `numSurfaces = 1`, allocates one surface pointer, and points that surface at `tr.defaultShader`.

That closes `sub_447C40` as the exact skin bootstrap helper `R_InitSkins`.

### `sub_447C90`: `R_GetSkinByHandle`

Observed local facts:

1. The helper returns the default skin when the handle is less than `1` or greater than or equal to `tr.numSkins`.
2. Otherwise it returns `tr.skins[hSkin]` directly.

That is the exact handle lookup helper `R_GetSkinByHandle`.

### `sub_447CC0`: `R_SkinList_f`

Observed local facts:

1. The helper prints the exact opening and closing banner:
   - `------------------\n`
2. It iterates `tr.skins[0..tr.numSkins-1]` and emits the same per-skin line:
   - `%3i:%s\n`
3. For each surface it emits the exact mapping line:
   - `       %s = %s\n`

That is the exact console command helper `R_SkinList_f`.

## Exact Renderer Registration Boundaries

### `sub_449E40`: `RE_Shutdown`

Observed local facts:

1. The body emits the exact shutdown banner:
   - `RE_Shutdown( %i )\n`
2. It unregisters the same renderer console commands:
   - `modellist`
   - `screenshotJPEG`
   - `screenshot`
   - `imagelist`
   - `shaderlist`
   - `skinlist`
   - `gfxinfo`
   - `modelist`
3. When the renderer is registered, it executes the same shutdown chain used by the source before tearing down the image/state backend.
4. When the incoming `destroyWindow` flag is non-zero, it calls the extra platform/window shutdown helper.
5. It clears the renderer registered flag before returning.

That is the exact exported shutdown entry point `RE_Shutdown`.

### `sub_449EF0`: `RE_EndRegistration`

Observed local facts:

1. The helper first syncs the render thread.
2. It then calls the low-memory check and returns immediately when low physical memory is reported.
3. Otherwise it tail-calls the image-dump helper used by the source-side `RB_ShowImages()` path.

That closes `sub_449EF0` as the exact registration tail `RE_EndRegistration`.

### `sub_44F550`: `RE_BeginRegistration`

Observed local facts:

1. The helper begins by calling the now-closed `R_Init`.
2. It copies the current `glConfig` block into the caller-provided output buffer.
3. It syncs the render thread, resets `viewCluster` to `-1`, clears scene state, and marks the renderer as registered.
4. It ends by issuing the same zero-sized stretch-pic warmup call as the source:
   - `RE_StretchPic( 0, 0, 0, 0, 0, 0, 1, 1, 0 )`

That is the exact exported registration entry point `RE_BeginRegistration`.

## Exact Model Initialization And Listing Helpers

### `sub_44F5D0`: `R_ModelInit`

Observed local facts:

1. The helper resets `tr.numModels` to `0`.
2. It immediately allocates one model entry through the same allocator used by `R_AllocModel`.
3. It assigns that first model `type = MOD_BAD`.

That is the exact model bootstrap helper `R_ModelInit`.

### `sub_44F610`: `R_Modellist_f`

Observed local facts:

1. The helper iterates models from index `1` up to `tr.numModels - 1`.
2. It computes the same effective LOD count by checking whether `md3[j]` exists and differs from `md3[j - 1]`.
3. It emits the exact per-model line:
   - `%8i : (%i) %s\n`
4. It accumulates `mod->dataSize` and emits the exact trailer:
   - `%8i : Total models\n`

That closes `sub_44F610` as the exact console command helper `R_Modellist_f`.

## Exact MD3 And MD4 Loaders

### `sub_44F0F0`: `R_LoadMD3`

Observed local facts:

1. The helper checks the header version against `0x0F` and emits the exact mismatch string:
   - `R_LoadMD3: %s has wrong version (%i should be %i)\n`
2. It marks the destination model `MOD_MESH`, adds the file size into `dataSize`, allocates the copied header blob, and copies the full input buffer into hunk memory.
3. It emits the exact no-frame warning:
   - `R_LoadMD3: %s has no frames\n`
4. It walks the copied frames, tags, and surfaces using the same offsets and counts as the source.
5. For each surface it enforces the same vertex and triangle caps with the exact fatal strings:
   - `R_LoadMD3: %s has more than %i verts on a surface (%i)`
   - `R_LoadMD3: %s has more than %i triangles on a surface (%i)`
6. It stamps each surface as `SF_MD3`, lowercases the surface name, strips the trailing `_1` / `_2` suffix when present, registers the per-surface shaders, and byte-swaps triangles, texcoords, and compressed normals in the same loop structure as the source.

That is an exact body-level match for `R_LoadMD3`.

### `sub_44F300`: `R_LoadMD4`

Observed local facts:

1. The helper checks the header version against `1` and emits the exact mismatch string:
   - `R_LoadMD4: %s has wrong version (%i should be %i)\n`
2. It marks the destination model `MOD_MD4`, adds the file size into `dataSize`, allocates the copied header blob, and copies the full buffer into hunk memory.
3. It emits the exact no-frame warning:
   - `R_LoadMD4: %s has no frames\n`
4. It byte-swaps the frame/bone data across all frames using the same per-frame stride as the source.
5. It iterates LODs and surfaces, enforces the same per-surface vertex and triangle caps, stamps each surface as `SF_MD4`, lowercases the surface name, and resolves the surface shader the same way as the source path.
6. It then swaps the MD4 triangles and per-vertex weight blocks in the same nested loop structure as `tr_model.c`.

That closes `sub_44F300` as the exact `R_LoadMD4` path.

## Exact Shader Registration Helpers

### `sub_4588E0`: `RE_RegisterShaderLightMap`

Observed local facts:

1. The helper emits the exact validation string:
   - `Shader name exceeds MAX_QPATH\n`
2. It calls the core shader finder with the incoming `lightmapIndex` and `mipRawImage = qtrue`.
3. It returns `0` when the resolved shader is marked `defaultShader`, otherwise it returns the shader index.

That is the exact lightmap-aware shader registration helper `RE_RegisterShaderLightMap`.

### `sub_458930`: `RE_RegisterShader`

Observed local facts:

1. The helper emits the same MAX_QPATH validation string as the source.
2. It calls the shader finder with `LIGHTMAP_2D` and `qtrue`.
3. It returns `0` for `defaultShader` results and otherwise returns the resolved shader index.

That is the exact exported shader registration entry point `RE_RegisterShader`.

### `sub_458980`: `RE_RegisterShaderNoMip`

Observed local facts:

1. The helper emits the same MAX_QPATH validation string as the source.
2. It calls the shader finder with `LIGHTMAP_2D` and `qfalse`.
3. It returns `0` for `defaultShader` results and otherwise returns the resolved shader index.

That closes `sub_458980` as the exact exported helper `RE_RegisterShaderNoMip`.

## Promoted Aliases

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `__initp_misc_invarg` (`0x00438CC0`) | `RE_SetWorldVisData` | Observed | Exact renderer export that stores the shared external vis-data pointer. |
| `sub_43BF40` (`0x0043BF40`) | `RE_LoadWorldMap` | Observed | Exact BSP world-load export. |
| `sub_4479C0` (`0x004479C0`) | `RE_RegisterSkin` | Observed | Exact skin registration entry point. |
| `sub_447C40` (`0x00447C40`) | `R_InitSkins` | Observed | Exact default-skin bootstrap helper. |
| `sub_447C90` (`0x00447C90`) | `R_GetSkinByHandle` | Observed | Exact skin-table handle lookup helper. |
| `sub_447CC0` (`0x00447CC0`) | `R_SkinList_f` | Observed | Exact skin-list console command helper. |
| `sub_449E40` (`0x00449E40`) | `RE_Shutdown` | Observed | Exact renderer shutdown export. |
| `sub_449EF0` (`0x00449EF0`) | `RE_EndRegistration` | Observed | Exact renderer end-registration export. |
| `sub_44F0F0` (`0x0044F0F0`) | `R_LoadMD3` | Observed | Exact MD3 model-load helper. |
| `sub_44F300` (`0x0044F300`) | `R_LoadMD4` | Observed | Exact MD4 model-load helper. |
| `sub_44F550` (`0x0044F550`) | `RE_BeginRegistration` | Observed | Exact renderer begin-registration export. |
| `sub_44F5D0` (`0x0044F5D0`) | `R_ModelInit` | Observed | Exact model bootstrap helper. |
| `sub_44F610` (`0x0044F610`) | `R_Modellist_f` | Observed | Exact model-list console command helper. |
| `sub_4588E0` (`0x004588E0`) | `RE_RegisterShaderLightMap` | Observed | Exact shared shader registration helper with explicit lightmap index. |
| `sub_458930` (`0x00458930`) | `RE_RegisterShader` | Observed | Exact exported shader registration entry point. |
| `sub_458980` (`0x00458980`) | `RE_RegisterShaderNoMip` | Observed | Exact exported no-mip shader registration helper. |

## Coverage Impact

On the committed `quakelive_steam.exe` Ghidra baseline of `5473` functions, this pass moves the explicit `quakelive_steam` alias set from `356` to `372` functions, which is approximately `6.5%` to `6.8%` host-symbol coverage.

## Open Questions

1. The renderer export slot at `sub_451360` still remains open. It is definitely exported from `GetRefAPI`, but the local `refexport_t` no longer matches the retail Quake Live tail exactly, so the slot should not be forced to `RE_RegisterFont` without body-level proof.
2. The adjacent shader-management area still has more internal helpers worth promoting, especially around shader remapping and explicit image-backed shader registration, but this round focused first on the exact public registration boundary.
3. The BSP and renderer bootstrap band still contains a few pre-init helpers immediately before `R_Init` and `RE_LoadWorldMap`; they are now better bounded by context, but this pass keeps them generic until their exact source identities are equally direct.
