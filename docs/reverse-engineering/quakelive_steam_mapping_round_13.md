# Quake Live Steam Host Mapping Round 13

## Scope

This round revisits the still-opaque bridge rooted at `data_12D2670`.

Round 02 established the slot layout, but it still treated the bridge too broadly as a generic engine-to-host surface. A fresh pass through the renderer, advertisement loader, and native VM import slabs now pins the owning subsystem much more tightly:

- the bridge is advertisement-facing first, not browser-facing
- the `sub_4AFF*` and `sub_4BEEF0`-style wrappers sit in native cgame/UI import slabs, not in the Awesomium JS dispatch path
- several previously generic bridge slots are now stable enough to promote with advertisement-specific names

The primary local evidence remains:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- `src/code/client/cl_cgame.c`
- `src/code/client/cl_ui.c`

## Advertisement Ownership

The renderer-side advertisement path is now explicit enough to reframe the bridge.

Observed local facts:

1. `sub_434C80` is the retail advertisement lump loader:
   - it logs `R_LoadAdvertisements: funny lump size`
   - it logs `R_LoadAdvertisements: number of advertisements exceeds level limit.`
   - it logs `HW Occlusion support missing. No Advertisements will be tracked.`
   - it clears and repopulates `data_585250`
   - it stores the advertisement count in `data_5850E4`
2. `sub_434E40` walks those loaded advertisement cells, computes runtime visibility/state for each one, and tracks visible entries separately when occlusion support exists.
3. The draw path at `004350EA` iterates the loaded advertisement cells in `data_585250` and uses the bridge in the middle of that loop:
   - `sub_4F2080(*esi)` chooses one of three display palettes
   - `sub_4F2040(*esi, U"0", 0x100)` fills the label buffer for the current cell
4. The same draw path then renders two more bridge-fed label lists immediately after the per-cell loop:
   - `sub_4F2160` / `sub_4F2180`
   - `sub_4F2260` / `sub_4F2280`
5. The retail UI corpus also contains the literal string `Waiting on Advertisement`, which fits the same subsystem surface even though the bridge wrappers themselves live in the host executable.

That combination is strong enough to treat `data_12D2670` as an advertisement bridge rather than a generic browser helper object.

## View And Trace Feed

Two previously vague bridge slots now have stable renderer/tracing roles.

### `sub_4F20A0`

Observed local facts:

1. Client init calls `sub_4F20A0(sub_4B9DA0)`.
2. `sub_4B9DA0(float* arg1, float* arg2)` wraps `sub_4C78C0(...)`.
3. That helper performs a world trace and returns `1` only when the trace fraction is below `1.0`.

This is not a generic UI registration hook. It is a visibility-test callback registration path for the advertisement bridge.

### `sub_4F1F70`

Observed local facts:

1. `sub_4F1F70` is called from the renderer path after refdef-like globals are copied into `data_1717704` and neighboring camera/projection globals.
2. The first call passes multiple vectors plus angle/depth/screen-size material.
3. A second helper call (`sub_451360`) feeds the same bridge slot with identity/default values, which matches a reset or neutral-view push rather than a gameplay command.

This is now stable as a per-frame advertisement view/projection update slot.

### `sub_4F1F30` And `sub_4F1F50`

Observed local facts:

1. `SCR_UpdateScreen`-style code at `sub_4BE3A0` calls:
   - `sub_4F1F30(data_1528BA4)`
   - `sub_4F1F50(data_1528CC4)`
2. `sub_4F1F50` is also called during cgame init warmup with `sub_4EF510()`.

That is a stable "push live frame state into the advertisement bridge" pattern, not an Awesomium or JS method path.

## Native VM Import Ownership

Round 02 treated the small `sub_4AFF*` / `sub_4BEEF0` wrappers as if they might be browser-facing. The table data says otherwise.

Observed local facts:

1. The native cgame load path uses `sub_4E9FF0("cgame", &data_146CC38, &data_565958, ...)`.
2. Inside that cgame import slab:
   - `data_565A34 = sub_4AFF20`
   - `data_565A38 = sub_4AFF30`
   - `data_565A3C = sub_4BEF30`
   - `data_565A48 = sub_4AFF50`
   - `data_565A4C = j_sub_4F2000`
   - `data_565A50 = j_sub_4F2020`
   - `data_565A54 = sub_4AFF80`
   - `data_565A58 = sub_4AFFD0`
   - `data_565A6C = sub_4AFFC0`
3. The native UI load path uses `sub_4E9FF0("ui", &data_146CC18, &data_567338, ...)`.
4. Inside that UI import slab:
   - `data_567478 = sub_4BEEF0`
   - `data_56747C = sub_4BEF00`
   - `data_567488 = sub_4BEF30`

Those wrappers are therefore native VM import-table entries that happen to forward into the advertisement bridge. They are not part of `QLJSHandler`.

This matters because it explains why the same bridge surface shows up in browser-era documentation and in non-browser runtime paths at the same time: the bridge is shared host functionality consumed by native game/UI code.

## Shader-Supplying Bridge Slots

The four string-return slots below are still not tight enough to promote with final surface names, but their fallback behavior is now constrained:

- `sub_4F20E0`
- `sub_4F2120`
- `sub_4F21E0`
- `sub_4F2220`

Observed local facts:

1. Each function first tries a `data_12D2670` bridge slot.
2. If the bridge returns `0`, each helper falls back to `sub_4589D0(arg1, nullptr, 0)`.
3. `sub_4589D0` is the renderer shader lookup/register path when its second argument is null.

So these are not empty-string helpers. They are advertisement shader-supplying hooks that ultimately degrade to ordinary shader lookup when the bridge does not override them. I am leaving them unnamed for one more round because the slot-to-surface order is still not pinned tightly enough.

## Promoted Aliases

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4F1F30` (`0x004F1F30`) | `AdvertisementBridge_SetClientStateFlags` | Observed plus bounded inference | Called once per screen update with the live client state bitfield `data_1528BA4`, immediately before the main draw path. |
| `sub_4F1F50` (`0x004F1F50`) | `AdvertisementBridge_SetFrameTime` | Observed plus bounded inference | Called from screen update and cgame init with live frame/time values, feeding per-frame timing into the advertisement bridge. |
| `sub_4F1F70` (`0x004F1F70`) | `AdvertisementBridge_UpdateViewParameters` | Observed plus bounded inference | Pushes renderer-derived vectors, depth/angle values, and screen dimensions into the advertisement bridge. |
| `sub_4F2040` (`0x004F2040`) | `AdvertisementBridge_GetCellLabel` | Observed | Fills the label buffer for each loaded advertisement cell during the main advertisement draw loop. |
| `sub_4F2080` (`0x004F2080`) | `AdvertisementBridge_GetCellDisplayState` | Observed | Returns one of three display states used to select the palette for a loaded advertisement cell. |
| `sub_4F20A0` (`0x004F20A0`) | `AdvertisementBridge_SetVisibilityTraceCallback` | Observed plus bounded inference | Registers the `sub_4B9DA0` world-trace callback during client init so the bridge can test advertisement visibility/tracking. |
| `sub_4F2160` (`0x004F2160`) | `AdvertisementBridge_GetLabelList1Count` | Observed | Returns the count for the first bridge-fed label list rendered after the main advertisement-cell loop. |
| `sub_4F2180` (`0x004F2180`) | `AdvertisementBridge_GetLabelList1Entry` | Observed | Fills label text for that first post-cell bridge-fed label list. |
| `sub_4F2260` (`0x004F2260`) | `AdvertisementBridge_GetLabelList2Count` | Observed | Returns the count for the second bridge-fed label list rendered after the main advertisement-cell loop. |
| `sub_4F2280` (`0x004F2280`) | `AdvertisementBridge_GetLabelList2Entry` | Observed | Fills label text for that second post-cell bridge-fed label list. |

## Open Questions

1. The shader-return slots `sub_4F20E0` / `sub_4F2120` / `sub_4F21E0` / `sub_4F2220` are now clearly advertisement shader hooks, but the exact retail surface ordering is still open.
2. `sub_4F1F10`, `sub_4F1FC0`, `sub_4F1FE0`, `sub_4F2000`, `sub_4F2020`, `sub_4F20C0`, `sub_4F21C0`, and `sub_4F22C0` still need tighter callsite ownership before promotion.
3. `docs/launcher_awesomium_audit.md` still describes the `data_12D2670` bridge too generically; the bridge is now better understood as advertisement-facing shared host functionality rather than a pure browser contract.
