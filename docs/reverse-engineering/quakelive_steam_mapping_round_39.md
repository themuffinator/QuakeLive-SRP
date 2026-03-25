# Quake Live Steam Host Mapping Round 39

## Scope

This round closes the exact core shader-management tranche inside `quakelive_steam.exe`.

The previous passes promoted the public renderer registration surface. This one moves down one layer and closes the shader finalizer, shader-text lookup, live shader lookup/registration helpers, shader handle/list helpers, and the init path that builds the default internal shaders and indexes the `.shader` corpus.

The primary local evidence for this round is:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `src/code/renderer/tr_shader.c`

## Exact Shader Finalization Helpers

### `sub_458000`: `FinishShader`

Observed local facts:

1. The helper iterates the active global shader stages and emits the exact missing-image warning:
   - `Shader %s has a stage with no image\n`
2. It deactivates or memmoves away invalid/detail stages in the same stage-walk shape used by the source.
3. It supplies the same default texture coordinate generation for lightmap versus non-lightmap bundles and tracks whether any real lightmap stage was seen.
4. It derives fog-adjustment mode and default sort order from the blend-state combinations in the same decision tree used by the source.
5. It applies the same late simplification passes:
   - vertex-light collapse
   - multitexture collapse
6. It emits the same developer lightmap warning when a shader has a lightmap index but no surviving lightmap stage:
   - `WARNING: shader '%s' has lightmap but no lightmap stage!\n`
7. It stores `numUnfoggedPasses`, handles the fog-only sort case, computes the stage iterator, and returns the permanently generated shader record.

That is the exact shader finalizer `FinishShader`.

### `sub_458260`: `FindShaderInShaderText`

Observed local facts:

1. The helper hashes the requested shader name into the shader-text hash table.
2. It walks the hashed bucket entries, reparses each candidate name with the same token parser, and returns the body pointer on a case-insensitive match.
3. If no hashed hit is found, it falls back to the global combined shader-text blob.
4. In that fallback path it repeatedly parses a token, compares it against the requested name, and skips braced sections until a match or EOF.
5. It returns `NULL` when no shader definition is found.

That closes `sub_458260` as the exact shader-text lookup helper `FindShaderInShaderText`.

## Exact Shader Lookup And Registration Helpers

### `sub_458320`: `R_FindShaderByName`

Observed local facts:

1. The retail HLIL early-outs to the default shader when the incoming pointer is `NULL` or points to an empty string.
2. It strips the extension into a `MAX_QPATH` local buffer.
3. It hashes the stripped name with the file-hash helper and walks the matching shader hash chain.
4. It compares shader names case-insensitively and returns the first match.
5. It returns the default shader when no match exists.

The committed local source currently carries an extra reconstruction-only invalid-pointer guard ahead of the empty-string test, but the retail body after that point matches `R_FindShaderByName` exactly.

### `sub_4583C0`: `R_FindShader`

Observed local facts:

1. The helper returns the default shader immediately on an empty name.
2. It clamps an out-of-range positive lightmap index down to `LIGHTMAP_BY_VERTEX` when the current world has fewer lightmaps, matching the source fallback for fullbright vertex lighting.
3. It strips the extension, hashes the name, and reuses an existing shader when either:
   - `sh->lightmapIndex == lightmapIndex`, or
   - `sh->defaultShader` is already set
4. Under SMP it syncs the render thread before beginning a new shader build.
5. It clears the global `shader` and `stages` blocks, seeds all stage `texMods`, sets the same `needsNormal / needsST1 / needsST2 / needsColor` flags, and then queries `FindShaderInShaderText`.
6. If explicit shader text exists, it optionally logs `*SHADER* %s\n`, parses the text, marks `defaultShader` on parse failure, and finishes the shader.
7. If no explicit shader text exists, it appends `.tga`, calls the image finder, emits the exact developer miss string on failure:
   - `Couldn't find image for shader %s\n`
8. On success it builds the same default stage layouts for:
   - `LIGHTMAP_NONE`
   - `LIGHTMAP_BY_VERTEX`
   - `LIGHTMAP_2D`
   - `LIGHTMAP_WHITEIMAGE`
   - regular two-pass lightmap shaders
9. It returns the result of the now-closed `FinishShader`.

That is the exact shader lookup/auto-construction helper `R_FindShader`.

### `sub_4586D0`: `RE_RegisterShaderFromImage`

Observed local facts:

1. The helper hashes the incoming name and reuses an already-loaded shader when the same name/lightmap combination is present, with the same `defaultShader` exception as the source.
2. Under SMP it syncs the render thread before creating a new shader.
3. It clears the same global `shader` and `stages` blocks, copies the incoming name, stores `lightmapIndex`, seeds stage `texMods`, and sets the same `needs*` flags as `R_FindShader`.
4. Instead of loading an image from disk, it uses the incoming `image_t *` directly and builds the same five lightmap-mode stage layouts as the source.
5. It finishes the shader and returns the shader index from the finished record.

That closes `sub_4586D0` as the exact image-backed shader registration helper `RE_RegisterShaderFromImage`.

### `sub_458A40`: `R_GetShaderByHandle`

Observed local facts:

1. The helper returns a shader directly from the shader table when `0 <= hShader < tr.numShaders`.
2. Otherwise it emits the exact warning prefix:
   - `R_GetShaderByHandle: out of range hShader '%d'\n`
3. It returns the default shader on invalid handles.

That is the exact handle lookup helper `R_GetShaderByHandle`.

### `sub_458A80`: `R_ShaderList_f`

Observed local facts:

1. The helper emits the exact opening and closing banners:
   - `-----------------------\n`
   - `------------------\n`
2. It chooses between `tr.shaders[i]` and `tr.sortedShaders[i]` based on whether `Cmd_Argc() > 1`.
3. For each shader it prints the same data columns:
   - `numUnfoggedPasses`
   - `L` flag for lightmapped shaders
   - multitexture mode tags `MT(a)`, `MT(m)`, `MT(d)`
   - explicit-definition flag
   - optimal iterator tags `gen`, `sky`, `lmmt`, `vlt`
4. It chooses between the same name-format strings:
   - `: %s\n`
   - `: %s (DEFAULTED)\n`
5. It prints the total count through the exact trailer:
   - `%i total shaders\n`

That is the exact console command helper `R_ShaderList_f`.

## Exact Shader Bootstrap Helpers

### `sub_458BF0`: `ScanAndLoadShaderFiles`

Observed local facts:

1. The helper lists files from `scripts` with the `.shader` extension and caps the count at `0x1000`, matching `MAX_SHADER_FILES`.
2. It logs each file through the exact load banner:
   - `...loading '%s'\n`
3. It loads each file into a temporary buffer and errors out with:
   - `Couldn't load %s`
   when a shader file read fails.
4. It allocates a single combined shader-text blob sized as `sum + numShaders * 2`, then concatenates the file contents in reverse order with newline separators and runs `COM_Compress` on each block.
5. It frees the file list, performs the same first pass that counts shader-text hash bucket sizes, allocates the packed hash table slab, then performs the same second pass that stores the `oldp` pointers for each shader definition.
6. When no shader files are present it exits through the same warning path as the source-side no-files case.

That is the exact shader-file bootstrap helper `ScanAndLoadShaderFiles`.

### `sub_458F90`: `CreateInternalShaders`

Observed local facts:

1. The helper resets `tr.numShaders` to `0`.
2. It clears the global `shader` and `stages` working blocks.
3. It copies the exact built-in shader names:
   - `<default>`
   - `<stencil shadow>`
4. For the default shader it sets `LIGHTMAP_NONE`, binds `tr.defaultImage`, activates stage `0`, and uses `GLS_DEFAULT`.
5. It finalizes and stores both the default shader and the stencil-shadow marker shader through the shared finalizer.

That closes `sub_458F90` as the exact built-in shader bootstrap helper `CreateInternalShaders`.

### `sub_459030`: `R_InitShaders`

Observed local facts:

1. The helper emits the exact init banner:
   - `Initializing Shaders\n`
2. It clears the live shader hash table, the shader-text hash table, and the global working-stage slab.
3. It resets the deferred-load flag.
4. It calls the now-closed `CreateInternalShaders`.
5. It calls the now-closed `ScanAndLoadShaderFiles`.
6. It then resolves the same three external shaders directly through `R_FindShader`:
   - `projectionShadow`
   - `flareShader`
   - `sun`

The local source expresses the last step through a tiny `CreateExternalShaders` helper, but the retail binary has that tail inlined into `R_InitShaders`.

## Promoted Aliases

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_458000` (`0x00458000`) | `FinishShader` | Observed | Exact shader finalizer that validates stages, derives sort/fog behavior, and emits a permanent shader. |
| `sub_458260` (`0x00458260`) | `FindShaderInShaderText` | Observed | Exact hashed/fallback shader-text lookup helper. |
| `sub_458320` (`0x00458320`) | `R_FindShaderByName` | Observed | Exact shader lookup by stripped name. |
| `sub_4583C0` (`0x004583C0`) | `R_FindShader` | Observed | Exact shader lookup and auto-construction path. |
| `sub_4586D0` (`0x004586D0`) | `RE_RegisterShaderFromImage` | Observed | Exact shader registration helper for a prebuilt `image_t`. |
| `sub_458A40` (`0x00458A40`) | `R_GetShaderByHandle` | Observed | Exact shader-table handle lookup helper. |
| `sub_458A80` (`0x00458A80`) | `R_ShaderList_f` | Observed | Exact shader-list console command helper. |
| `sub_458BF0` (`0x00458BF0`) | `ScanAndLoadShaderFiles` | Observed | Exact `.shader` discovery, concatenation, and hash-index bootstrap helper. |
| `sub_458F90` (`0x00458F90`) | `CreateInternalShaders` | Observed | Exact built-in shader bootstrap helper. |
| `sub_459030` (`0x00459030`) | `R_InitShaders` | Observed | Exact shader system init entry point. |

## Coverage Impact

On the committed `quakelive_steam.exe` Ghidra baseline of `5473` functions, this pass moves the explicit `quakelive_steam` alias set from `372` to `382` functions, which is approximately `6.8%` to `7.0%` host-symbol coverage.

## Open Questions

1. The still-open renderer export slot at `sub_451360` remains unresolved. Its body currently looks tied to Quake Live advertisement/view-parameter plumbing rather than the classic `RE_RegisterFont` role, so it should stay unmapped until a source-side name is proven.
2. The adjacent image-loading band around `sub_446F80` is now well-bounded as Quake Live’s in-memory image path, but this round stops short of naming it because the current repo does not yet expose an exact source-side helper with that same interface.
3. The next clean continuation inside the shader/image subsystem is the image bootstrap chain itself: image creation, image lookup, image deletion, and the remaining shader-stage iterator helpers.
