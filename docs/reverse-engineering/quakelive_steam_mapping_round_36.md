# Quake Live Steam Host Mapping Round 36

## Scope

This round closes the stable renderer export tail in `quakelive_steam.exe` that sits between the already-mapped scene/draw helpers and the older parser/world helpers.

The main goal was to stop leaving the late `GetRefAPI` slice half-generic once the exact bodies were already present in the committed corpus. This pass promotes the renderer cinematic upload helpers, the frame begin/end pair, the fragment/tag/bounds helpers, and the exact shader/entity/PVS utilities behind the same export-table run.

The primary local evidence for this round is:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `src/code/renderer/tr_init.c`
- `src/code/renderer/tr_public.h`
- `src/code/renderer/tr_cmds.c`
- `src/code/renderer/tr_backend.c`
- `src/code/renderer/tr_marks.c`
- `src/code/renderer/tr_model.c`
- `src/code/renderer/tr_shader.c`
- `src/code/renderer/tr_bsp.c`
- `src/code/renderer/tr_world.c`

## Renderer Export Tail Anchor In `GetRefAPI`

Observed local facts:

1. `sub_449F70` assembles the renderer export table at `data_587848`.
2. The late renderer run relevant to this pass is assigned in this order:
   - `data_587894 = sub_436350`
   - `data_587898 = sub_4366D0`
   - `data_58789C = sub_43C7B0`
   - `data_5878A0 = sub_43CAC0`
   - `data_5878A4 = sub_44DCD0`
   - `data_5878A8 = sub_44F710`
   - `data_5878AC = sub_44F8A0`
   - `data_5878B0 = sub_4D7980`
   - `data_5878B4 = sub_4590F0`
   - `data_5878B8 = sub_43BEF0`
   - `data_5878BC = sub_45E320`
3. The local source `tr_init.c` assigns the same stable tail around these helpers:
   - `re.DrawStretchRaw = RE_StretchRaw;`
   - `re.UploadCinematic = RE_UploadCinematic;`
   - `re.BeginFrame = RE_BeginFrame;`
   - `re.EndFrame = RE_EndFrame;`
   - `re.MarkFragments = R_MarkFragments;`
   - `re.LerpTag = R_LerpTag;`
   - `re.ModelBounds = R_ModelBounds;`
   - `re.RemapShader = R_RemapShader;`
   - `re.GetEntityToken = R_GetEntityToken;`
   - `re.inPVS = R_inPVS;`

That gives a stable export-table bracket for the helpers promoted here, while still leaving the single one-byte slot at `sub_4D7980` unforced.

## Exact Cinematic Upload Helper Closures

### `sub_436350`: `RE_StretchRaw`

Observed local facts:

1. The body hard-errors with `Draw_StretchRaw: size not a power of 2: %i by %i`.
2. It conditionally prints `qglTexSubImage2D %i, %i: %i msec\n`.
3. It calls the same bind/upload sequence as the local source:
   - bind `tr.scratchImage[client]`
   - `qglTexImage2D` on size changes
   - `qglTexSubImage2D` only when `dirty != 0`
4. It then switches to 2D and emits one textured quad using the half-texel `0.5 / cols` and `0.5 / rows` offsets.
5. `sub_449F70` exports it immediately before `sub_4366D0`.

That is an exact body-level match for `RE_StretchRaw` in `tr_backend.c`.

### `sub_4366D0`: `RE_UploadCinematic`

Observed local facts:

1. The helper binds `tr.scratchImage[client]`.
2. It checks the cached width and height at the same image fields as `sub_436350`.
3. On size changes it issues `qglTexImage2D` plus the same linear/clamp parameter setup.
4. Otherwise it only performs `qglTexSubImage2D` when `dirty != 0`.
5. Unlike `sub_436350`, it does not emit any 2D quad draw.

That matches the local `RE_UploadCinematic` helper exactly.

## Exact Frame Lifecycle Closures

### `sub_43C7B0`: `RE_BeginFrame`

Observed local facts:

1. The body emits both retail error strings:
   - `RE_BeginFrame() - glGetError() failed (0x%x)!\n`
   - `RE_BeginFrame: Stereo is enabled...`
   - `RE_BeginFrame: Stereo is disabled...`
2. It increments the frame count, clears the scene number, and runs the same overdraw, texture-mode, and gamma synchronization checks as the local source.
3. It allocates a command-buffer entry and writes command id `4`, matching the draw-buffer command.
4. It writes `GL_BACK_LEFT`, `GL_BACK_RIGHT`, `GL_FRONT`, or `GL_BACK` using the same stereo-mode logic as `RE_BeginFrame`.

That is the exact renderer frame-begin entry point.

### `sub_43CAC0`: `RE_EndFrame`

Observed local facts:

1. The helper allocates a command-buffer entry and writes command id `5`, matching the swap-buffers command.
2. It calls the render-command flush path and then `sub_4507E0()`, which matches the SMP-frame toggle.
3. When the optional output pointers are non-null it writes back `data_17178F4` and `data_1745F18`, then clears both counters.
4. It clears `data_1716EA4`, matching the end-of-frame active state reset.

That matches `RE_EndFrame` exactly.

## Exact Fragment, Tag, And Bounds Closures

### `sub_44DCD0`: `R_MarkFragments`

Observed local facts:

1. The helper increments `data_1716EB4`, matching `tr.viewCount++`.
2. It normalizes the projection direction and expands a mins/maxs bounds box from both the source points and their projected endpoints.
3. It clamps the incoming point count to `0x40`, matching `MAX_VERTS_ON_POLY`.
4. It builds the same clipping-plane set as the local source, including the near and far plane offsets `32` and `20`.
5. It calls `sub_44D7F0` with the world-node pointer, the computed bounds, a 64-entry surface array, and the projection direction.
6. The later loop distinguishes grid surfaces (`*surface == 2`) and feeds clipped fragments back into the returned-point and returned-fragment accumulators.

That closes `sub_44DCD0` as the exact mark-fragment helper from `tr_marks.c`.

### `sub_44F710`: `R_LerpTag`

Observed local facts:

1. The body resolves the model handle through the same model table used elsewhere in the renderer.
2. On missing model or tag data it clears the axis and origin and returns `0`.
3. It calls `sub_44F690` twice to fetch the start-frame and end-frame tag records by name.
4. It linearly blends origin and all three axis vectors using `frac` and `1.0f - frac`.
5. It normalizes the three output axis vectors and returns `1`.

That is the exact `R_LerpTag` implementation from `tr_model.c`.

### `sub_44F8A0`: `R_ModelBounds`

Observed local facts:

1. The helper resolves the model handle through the same renderer model table as `sub_44F710`.
2. If the bmodel pointer at offset `0x4C` is present it copies two bound vectors directly from that record.
3. Otherwise it falls back to the MD3 pointer at offset `0x50`.
4. On missing MD3 data it clears both output vectors.
5. On present MD3 data it copies the first frame bounds into `mins` and `maxs`.

That matches `R_ModelBounds` exactly.

## Exact Shader, Entity, And PVS Closures

### `sub_4590F0`: `R_RemapShader`

Observed local facts:

1. The body emits both retail warning strings:
   - `WARNING: R_RemapShader: shader %s not found\n`
   - `WARNING: R_RemapShader: new shader %s not found\n`
2. It resolves the old shader name, falling back through the register/get-by-handle path when the direct lookup returns null or the default shader.
3. It resolves the replacement shader through the same fallback path.
4. It strips the extension from the source shader name, hashes it, and walks the shader hash chain.
5. Matching shader records receive the same `remappedShader` assignment logic as the local source.
6. When `arg4 != 0` it parses the time-offset string with `atof` and stores the float on the replacement shader record.

That is an exact body-level match for `R_RemapShader`.

### `sub_43BEF0`: `R_GetEntityToken`

Observed local facts:

1. The helper reparses from `data_58620C`, the world-entity parse pointer.
2. It copies the parsed token into the caller buffer with a bounded string copy.
3. If the parse pointer or token is empty it resets `data_58620C` back to `data_586208`, the start of the world entity string.
4. It returns `0` on that reset path and `1` otherwise.

That matches `R_GetEntityToken` exactly.

### `sub_45E320`: `R_inPVS`

Observed local facts:

1. The helper resolves the first point through `sub_45E270`, the leaf lookup path.
2. It derives the first cluster's PVS bitset through `sub_4C4D20(*(leaf + 0x30))`.
3. It resolves the second point through the same leaf lookup helper.
4. It tests the second cluster bit in the returned bitset and returns that boolean directly.

That is the exact `R_inPVS` implementation from `tr_world.c`.

## Promoted Aliases

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_436350` (`0x00436350`) | `RE_StretchRaw` | Observed | Exact cinematic scratch-texture upload and immediate quad draw helper. |
| `sub_4366D0` (`0x004366D0`) | `RE_UploadCinematic` | Observed | Exact cinematic scratch-texture upload helper without the draw step. |
| `sub_43BEF0` (`0x0043BEF0`) | `R_GetEntityToken` | Observed | Exact world-entity token parser and reset helper. |
| `sub_43C7B0` (`0x0043C7B0`) | `RE_BeginFrame` | Observed | Exact renderer frame-begin entry point. |
| `sub_43CAC0` (`0x0043CAC0`) | `RE_EndFrame` | Observed | Exact renderer frame-end entry point. |
| `sub_44DCD0` (`0x0044DCD0`) | `R_MarkFragments` | Observed | Exact projected mark-fragment clipping helper. |
| `sub_44F710` (`0x0044F710`) | `R_LerpTag` | Observed | Exact MD3 tag interpolation helper. |
| `sub_44F8A0` (`0x0044F8A0`) | `R_ModelBounds` | Observed | Exact model-bounds query helper. |
| `sub_4590F0` (`0x004590F0`) | `R_RemapShader` | Observed | Exact shader remap helper with fallback shader resolution and optional time offset. |
| `sub_45E320` (`0x0045E320`) | `R_inPVS` | Observed | Exact renderer point-in-PVS test. |

## Open Questions

1. `sub_4D7980` is still a one-byte no-op exported immediately after `R_ModelBounds`. Its slot position clearly marks it as part of the same renderer tail, but this round does not force whether it is a retired placeholder or part of the retail Quake Live font-export rearrangement.
2. The raw native cgame `R_RegisterFont` wrapper is already mapped, but the owning engine-side export is still not pinned from the committed corpus strongly enough to promote here.
