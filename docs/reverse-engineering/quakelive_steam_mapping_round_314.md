# quakelive_steam.exe Mapping Round 314

Date: 2026-05-26

Scope: remaining `tr_image.c` diagnostic/source edges plus the filename hash
helper wiring used by image lookup.

## Summary

This pass rechecked the `tr_image.c` helper band after rounds 312 and 313
closed the image upload, memory loader, and target bind paths. The main loader
logic held, but two small parity findings were still source-visible:

- `R_ImageList_f` prints the retail `GL_RGB8` internal-format diagnostic as
  `RGB8 `, including the trailing alignment space.
- `sub_4D8990` is not sound-only ownership. It is the folded shared
  `generateHashValue(name, size)` helper used by image lookup, shader lookup,
  and sound lookup with caller-supplied hash-table sizes.

## Evidence Table

| Symbol | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_444940` | `R_ImageList_f` | High | Image-list header, format-label switch, wrap-label switch, and total texel/image diagnostics. |
| `sub_446D00` | `R_FindImageFile` | High | Image hash lookup, disk load, uppercase-extension retry, and `R_CreateImage` handoff. |
| `sub_4474C0` | `R_CreateBuiltinImages` | High | Builtin `*white`, `*identityLight`, `*scratch`, dlight, and fog image construction lane. |
| `sub_4475D0` | `R_SetColorMappings` | High | Overbright clamp, gamma/intensity table construction, and hardware-gamma upload gate. |
| `sub_447800` | `R_DeleteTextures` | High | Texture deletion loop, image table reset, current texture cache reset, and TMU unbind path. |
| `sub_4D8990` | `generateHashValue` | High | Lowercase/extension-stripping/path-normalizing hash with caller-supplied table size; observed from image, shader, and sound callers. |

## Source Reconstruction

`R_ImageList_f` now prints the retail `RGB8 ` diagnostic label. This is a tiny
change, but it keeps the renderer console output byte-for-byte aligned with the
retail format-label switch around `0x004449BB`.

The symbol map now names `sub_4D8990` as `generateHashValue` rather than the
older `S_HashSFXName` label. The source still contains local hash helpers where
the recovered GPL layout carries them, but the mapping now reflects the retail
binary evidence: image lookup calls this helper with `0x400`, sound lookup with
`0x80`, and shader text paths with their own table sizes.

Observed facts:

- `sub_446D00` calls `sub_4D8990(arg1, 0x400)` before walking the image hash
  chain.
- `sub_4D9D00` calls `sub_4D8990(arg1, 0x80)` before walking the sound hash
  chain.
- `sub_4D8990` lowercases characters, stops at `.`, normalizes `\\` to `/`,
  multiplies by `(i + 119)`, and masks by `(size - 1)`.

Inferred meaning:

- The old sound-only alias was too narrow. The helper is best tracked as the
  shared `generateHashValue` algorithm because `tr_image.c` and `tr_shader.c`
  are active retail callers.

## Verification

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
- `python -m pytest tests/test_renderer_memory_image_parity.py tests/test_renderer_internal_helper_mapping_parity.py -q`
- `python -m pytest tests/test_renderer_memory_image_parity.py tests/test_renderer_post_process_parity.py tests/test_platform_services.py::test_launcher_resource_bridge_reconstructs_retail_web_fallback_owner tests/test_awesomium_browser_parity.py::test_awesomium_surface_rebuild_and_mouse_mapping_reconstruct_browser_surface_space -q`
- `MSBuild.exe src\\code\\renderer\\renderer.vcxproj /p:Configuration=Debug /p:Platform=x86 /m`

The full `Debug|x86` solution build was also attempted, but it is currently
blocked outside this renderer lane by unresolved game-side identifiers
`g_spawnRandomRatio` and `g_spawnMinDistance` in `src/code/game/g_client.c`.

Parity estimate for this scoped renderer image/hash lane:

- before: `99.4%`
- after: `99.6%`

Repo-wide checked-in tree parity remains estimated at `98%`; this pass closes
diagnostic and mapping nits in an otherwise reconstructed `tr_image` band.
