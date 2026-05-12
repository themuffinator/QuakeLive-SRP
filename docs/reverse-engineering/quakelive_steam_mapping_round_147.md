# quakelive_steam.exe Mapping Round 147

Date: 2026-04-27

Scope: source-backed advert-runtime reconstruction for the `quakelive_steam.exe`
renderer path. This pass converted the round 146 advert lane from
mapping-only coverage into committed source for the retail update/shutdown/query
flow, then promoted the newly stabilized helper owners that now have direct
source evidence.

## Summary

This round resolved `3` additional engine-owned `quakelive_steam.exe` rows and
closed most of the renderer-side advert runtime source gap identified in round
146. Classification mix:

- `3` engine-owned functions
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main source reconstruction landed:

- retail-sized `qlAdvertisement_t` runtime tail fields in `tr_local.h`
- retail-style `R_UpdateAdvertisements` front-end advert submission in
  `tr_world.c`
- renderer teardown via `R_ShutdownAdvertisements`
- backend occlusion-query command buffering via `R_AddAdvertisementQueryCmd`
  and `RB_DrawAdvertisementQueries`
- `GL_ARB_occlusion_query` loader plumbing in `qgl.h`, `win_glimp.c`,
  `win_qgl.c`, and `linux_qgl.c`
- corrected `R_RenderView` ordering so advert updates now run between
  `R_AddPolygonSurfaces` and `R_SetupProjection`, matching the retail
  `sub_44d700` flow

The remaining source gap in this lane is still `R_DebugAdvertisements`: the
retail `r_debugAds` overlay depends on bridge label/state helpers that are not
yet reconstructed cleanly in the checked-in client/renderer bridge surface.

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_434BC0` | `182` | engine-owned | `R_AddAdvertisementSurface` | High | Closed by source reconstruction; this helper is now committed in `src/code/renderer/tr_world.c`. |
| 2 | `sub_436A90` | `448` | engine-owned | `RB_DrawAdvertisementQueries` | High | Closed by source reconstruction; backend advert occlusion-query command now exists in source. |
| 3 | `sub_44B130` | `169` | engine-owned | `R_CullAdvertisementQuad` | High | Closed by source reconstruction; retail advert quad culler is now source-backed with the point-array signature used by the binary. |

## Evidence Notes

- `sub_44d700` calls `sub_434e40` only after `R_AddWorldSurfaces` and
  `R_AddPolygonSurfaces`, and only when `rdflags & (RDF_NOWORLDMODEL |
  RDF_HYPERSPACE)` is clear. The source now mirrors that ordering in
  `R_GenerateDrawSurfs`.
- `sub_434bc0` reads the advertisement bmodel surface, gates on the current
  `viewCount`, checks front-facing orientation from `vieworg - center`, uses
  `sub_44b130` on `points[4]`, and then routes the surface into the normal
  draw-surf path without the older source-only `R_DlightBmodel` detour. That is
  the exact single-cell owner now reconstructed as `R_AddAdvertisementSurface`.
- `sub_434e40` resets the per-cell runtime tail when `frameSceneNum == 1`,
  performs `R_inPVS` against the advert center, records cull state plus
  projected normal metadata, and appends only fully in-frustum cells to the
  compact occlusion-query list. The new `R_UpdateAdvertisements` follows that
  behavior.
- `sub_436a90` saves depth state, forces two-sided culling, disables color
  writes, and issues paired `GL_SAMPLES_PASSED_ARB` queries with `GL_EQUAL` and
  `GL_LEQUAL` depth functions around a simple advertisement quad draw helper.
  The new backend command implementation matches that structure.
- The extension loader evidence at `sub_46b362` / `sub_46b385` showed the
  retail executable resolving `glGenQueriesARB`, `glDeleteQueriesARB`,
  `glIsQueryARB`, `glBeginQueryARB`, `glEndQueryARB`, `glGetQueryivARB`,
  `glGetQueryObjectivARB`, and `glGetQueryObjectuivARB` as an all-or-nothing
  `GL_ARB_occlusion_query` feature block. The committed GL loader now mirrors
  that behavior.

## Aliases Added

- `sub_434BC0` -> `R_AddAdvertisementSurface`
- `sub_436A90` -> `RB_DrawAdvertisementQueries`
- `sub_44B130` -> `R_CullAdvertisementQuad`

## Verification

Source and alias validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- duplicate-key scan passed after the alias update
- recount after this pass: `1670` raw alias entries, `1599` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `29.216%` of `5473` functions
- `git diff --check` passed aside from the repo's existing LF -> CRLF
  normalization warnings on touched text files
- `quakelive_steam.vcxproj` built successfully with:
  `MSBuild.exe src\code\quakelive_steam.vcxproj /p:Configuration=Debug /p:Platform=Win32 /p:WindowsTargetPlatformVersion=10.0.26100.0 /m`
- the local environment still lacks the repo's original Windows SDK `8.1`
  target, so the build used a one-off SDK override for validation rather than a
  project-file retarget
- build completed with pre-existing unrelated warnings in `cl_main.c`,
  `sv_zmq.c`, and a linker `LNK4098` CRT warning
- no runtime launch was performed; this was static/source reconstruction work

Parity estimate after this pass:

- strict-retail Windows replacement target: `100%` before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

After this round, the refreshed largest-unaliased queue begins with:

| # | Address | Ghidra name | Size |
| ---: | --- | --- | ---: |
| 1 | `0x0040B050` | `FUN_0040b050` | `555` |
| 2 | `0x00419AD0` | `FUN_00419ad0` | `555` |
| 3 | `0x0040F7E0` | `FUN_0040f7e0` | `549` |
| 4 | `0x0041CFB0` | `FUN_0041cfb0` | `549` |
| 5 | `0x0042BA60` | `FUN_0042ba60` | `549` |
| 6 | `0x004940D0` | `FUN_004940d0` | `547` |
| 7 | `0x004F4410` | `FUN_004f4410` | `546` |
| 8 | `0x00475CA0` | `FUN_00475ca0` | `545` |
| 9 | `0x004999C0` | `FUN_004999c0` | `541` |
| 10 | `0x00403BB0` | `FUN_00403bb0` | `537` |

The next pass can return to the still-open queue head at `sub_40B050` and
`sub_419AD0`, or continue this advert lane by reconstructing the remaining
`R_DebugAdvertisements` bridge overlay once the needed cell-label/state access
surface is stabilized.
