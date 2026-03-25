# Quake Live Steam Host Mapping Round 43

## Scope

This round closes the remaining raw post-loading-text callback tail used by retail `cgamex86.dll`.

The previously open seam was the no-argument host callback at raw native cgame import offset `+0x134`, which retail calls immediately after `UpdateScreen()` and immediately before `AdvertisementBridge_SetFrameTime(1000)` in the loading-string helpers.

The primary local evidence for this round is:

- `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/analysis/quakelive_symbol_aliases.json`
- `docs/reverse-engineering/quakelive_steam_mapping_round_13.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_28.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_37.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_39.md`

## Retail Loading-Text Tail In Native `cgame`

The retail loading helpers now pin the full callback sequence cleanly.

Observed local facts:

1. `sub_1001CB80` copies the incoming loading string into `data_10A9C9B8`, clears `data_10A9CDB7`, then calls:
   - `(*(data_1074CCCC + 0x60))()`
   - `(*(data_1074CCCC + 0x134))()`
   - `(*(data_1074CCCC + 0x100))(0x3E8)`
2. `sub_1001CBE0` performs the same tail after copying the cleaned loading-client name.
3. The same `+0x134` then `+0x100(0x3E8)` sequence repeats in the direct `"game media"` loading-text path and throughout the staged init loading updates.
4. Round 28 already closed `+0x100` as `QLCGImport_AdvertisementBridge_SetFrameTime`, so the only open behavior in that tail was the no-argument `+0x134` call.

That keeps the problem tightly scoped: whatever `+0x134` is, retail uses it as a dedicated loading-screen side effect paired with `SetFrameTime(1000)`.

## Raw Host Slot `+0x134`

The owning host slab row is now stable.

Observed local facts:

1. The raw native cgame host slab contains:
   - `data_565A88 = sub_4BEF80`
   - `data_565A8C = 0x4B0050`
   - `data_565A90 = sub_4B0060`
   - `data_565A94 = sub_4B0070`
2. Local disassembly of `assets/quakelive/quakelive_steam.exe` shows:
   - `0x4B0050: jmpl *0x146CCA0`
   - `0x4B0060: jmpl *0x146CCA4`
   - `0x4B0070` forwarding the classic stretch-pic argument pack into `*0x146CCA8`
3. The adjacent rows are already closed:
   - `sub_4BEF80 -> QLCGImport_R_RenderScene`
   - `sub_4B0060 -> QLCGImport_R_SetColor`
   - `sub_4B0070 -> QLCGImport_R_DrawStretchPic`
4. That places `0x4B0050` on the single still-open host callback slot between the known render-scene and set-color rows.

This is enough to stabilize `0x4B0050` itself as the raw no-argument wrapper behind the loading-text tail.

## Host Target `sub_451360`

The destination of that wrapper now closes as a loading-view bridge helper rather than a classic renderer export.

Observed local facts:

1. `GetRefAPI` writes the renderer export rows in this exact order:
   - `sub_450E80`
   - `sub_451360`
   - `sub_43C650`
   - `sub_43C6C0`
2. The same export constructor assigns:
   - `data_587884 = sub_450E80`
   - `data_587888 = sub_451360`
   - `data_58788C = sub_43C650`
   - `data_587890 = sub_43C6C0`
3. `sub_451360` builds a default parameter pack:
   - zeroed vectors and angles
   - identity terms
   - current viewport width/height from `data_1743BCC` / `data_1743BD0`
   - constants `0.0174532924f`, `10000f`, and `4f`
4. `sub_451360` then calls `sub_4F1F70`.
5. Round 13 and Round 28 already closed `sub_4F1F70` as `AdvertisementBridge_UpdateViewParameters`.
6. Round 39 already noted that `sub_451360` looked tied to Quake Live advertisement/view-parameter plumbing rather than the older `RE_RegisterFont` reading.

That chain is enough for a bounded promotion: `sub_451360` is a no-argument helper that pushes a neutral/default view-parameter set into the advertisement bridge, and `0x4B0050` is the raw native cgame wrapper that reaches it.

## Why The Name Uses `LoadingViewParameters`

This round keeps the synthetic name intentionally narrow.

Observed local facts:

1. The already-mapped raw wrapper `sub_4AFF80 -> QLCGImport_AdvertisementBridge_UpdateViewParameters` preserves a large argument pack and is used for the general view-parameter path.
2. The newly closed `0x4B0050` takes no arguments at all.
3. Retail `cgame` only calls that no-argument wrapper in loading/progress update paths.
4. The helper body itself seeds neutral/default values instead of forwarding live camera state.

So the stable distinction is:

- `AdvertisementBridge_UpdateViewParameters` for the existing general argument-rich path
- `AdvertisementBridge_UpdateLoadingViewParameters` for the no-argument default-value path used by loading-screen updates

That naming keeps the two behaviors separate and avoids collapsing the new helper onto the older full-view callback.

## Promoted Aliases

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4B0050` (`0x004B0050`) | `QLCGImport_AdvertisementBridge_UpdateLoadingViewParameters` | Observed plus bounded inference | Raw native cgame wrapper for the no-argument loading-view update helper used in the retail loading-text tail. |
| `sub_451360` (`0x00451360`) | `AdvertisementBridge_UpdateLoadingViewParameters` | Observed plus bounded inference | No-argument helper that pushes neutral/default view parameters into the advertisement bridge using the current viewport dimensions. |

## Coverage Impact

On the committed `quakelive_steam.exe` Ghidra baseline of `5473` functions, this pass moves the explicit `quakelive_steam` alias set from `404` to `406` functions, which is approximately `7.4%` host-symbol coverage either way, but closes one of the last remaining high-value native cgame loading seams.

## Open Questions

1. The exact public-facing renderer export name for `sub_451360` remains intentionally synthetic. The stable behavior is the advertisement-facing loading-view push, not a proven renderer API verb.
2. The nearby general view-parameter path `sub_4AFF80 -> sub_4F1F70` remains a distinct contract and should stay separate from this loading-only helper.
