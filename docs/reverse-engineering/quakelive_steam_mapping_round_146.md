# quakelive_steam.exe Mapping Round 146

Date: 2026-04-27

Scope: refreshed largest-unaliased queue after round 145. This pass consumed
the renderer-owned advertisement lane around `sub_435070`, using the existing
advert bridge mappings plus the recovered `r_debugAds` cvar to close the
loader/update/shutdown/debug helpers that sit alongside `R_RenderView`.

## Summary

This round resolved `4` engine-owned `quakelive_steam.exe` rows: `1` exact
source-backed alias plus `3` high-confidence renderer ownership promotions for
the Quake Live advertisement runtime. Classification mix:

- `4` engine-owned functions
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

This pass also isolates an active renderer source gap: the committed source
already owns `R_LoadAdvertisements`, but the retail advert runtime update,
shutdown, and `r_debugAds` overlay helpers are still missing as first-class
source functions in the checked-in renderer.

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_435070` | `566` | engine-owned | `R_DebugAdvertisements` | High | Open renderer source gap; retail advert debug overlay gated by `r_debugAds` is not yet reconstructed in source. |
| 2 | `sub_434C80` | `447` | engine-owned | `R_LoadAdvertisements` | High | No new debt; exact owner already exists in `src/code/renderer/tr_bsp.c`. |
| 3 | `sub_434E40` | `322` | engine-owned | `R_UpdateAdvertisements` | Medium-high | Open renderer source gap; retail per-view advert runtime update/helper is still absent from source. |
| 4 | `sub_434FA0` | `123` | engine-owned | `R_ShutdownAdvertisements` | High | Open renderer source gap; retail advert teardown/reset helper is still absent from source. |

## Evidence Notes

- `sub_434C80` is an exact `R_LoadAdvertisements` hit. The body preserves the
  literal diagnostics `R_LoadAdvertisements: funny lump size` and
  `R_LoadAdvertisements: number of advertisements exceeds level limit.`, reads
  the Quake Live advertisement lump records, resolves each `*<modelNum>` brush
  model, rejects missing or multi-surface cells, computes the cell center, and
  stores the same `cellId` / `bmodel` / `normal` / `points` / `sourceIndex`
  payload now reconstructed in `src/code/renderer/tr_bsp.c`.
- `sub_434E40` is the retail advert runtime updater immediately before the main
  world draw path in `R_RenderView`. It resets per-cell state, calls the
  already-mapped visibility/projection helpers, records visibility class and
  screen-space coordinates, increments the visible-cell count, and populates a
  compact visible-entry list only when hardware occlusion support is enabled.
  That is the exact ownership slot missing between advert loading and advert
  teardown, so `R_UpdateAdvertisements` is the narrowest stable renderer name.
- `sub_434FA0` is the advert shutdown/reset helper. `RE_Shutdown` calls it
  before the rest of renderer teardown; when occlusion support is present it
  iterates the loaded advertisement cells and releases the retained per-cell GL
  query handles, then clears the loaded/runtime counts and zeroes the advert
  arrays. This is the retail shutdown owner for the advert lane.
- `sub_435070` is the renderer debug overlay guarded by the recovered
  `r_debugAds` cvar and `frameSceneNum == 1`. It tail-calls from the end of
  `R_RenderView`, walks the loaded advertisement cells, colors each entry by
  `AdvertisementBridge_GetCellDisplayState`, draws the cell label from
  `AdvertisementBridge_GetCellLabel`, outlines the cell quad, emits the bridge
  label-list entries, and therefore matches the retail advert debug overlay
  surface rather than a generic renderer helper.

## Aliases Added

- `sub_434C80` -> `R_LoadAdvertisements`
- `sub_434E40` -> `R_UpdateAdvertisements`
- `sub_434FA0` -> `R_ShutdownAdvertisements`
- `sub_435070` -> `R_DebugAdvertisements`

## Verification

Alias artifact validation:

- `references/analysis/quakelive_symbol_aliases.json` parses through
  `python -m json.tool`
- duplicate-key scan passed after the alias update
- recount after this pass: `1667` raw alias entries, `1596` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `29.161%` of `5473` functions
- refreshed unresolved queue was recomputed against the committed Ghidra
  function-start corpus after the alias update
- no game/runtime launch was performed; this was a static mapping pass

Parity estimate after this mapping-only pass remains unchanged:

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

The next pass should return to the still-open STL red-black-tree helpers at
`sub_40B050` and `sub_419AD0`, then keep working down the remaining queue head
while preserving the existing classification guardrails on engine,
platform-service, and support-library rows.
