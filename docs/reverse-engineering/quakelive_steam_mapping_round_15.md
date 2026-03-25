# Quake Live Steam Host Mapping Round 15

## Scope

This round closes the remaining retail UI advertisement-extension seam around the native `uix86.dll` import slab.

Round 14 mapped the parser/text/workshop imports at `0x164..0x180`, but the earlier entries at `0x140..0x150` were still too loosely described. A fresh pass through `_UI_Init`, the retail script-command table, and the menu advertisement update paths now pins that cluster as:

- three Quake Live display-context extension callbacks copied from host imports `0x140`, `0x144`, and `0x150`
- one raw UI-init thunk at import `0x148` that lands directly in the advertisement bridge
- the retail-only `activateAdvert` script command

The primary local evidence for this round is:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/hlil/quakelive/uix86.all/uix86.dll_hlil.txt`
- `references/analysis/quakelive_symbol_aliases.json`

## Retail UI Advertisement Extension

The retail UI imports extend the display context beyond the GPL layout.

Observed local facts:

1. During `_UI_Init`, `uix86.dll` copies host imports into extra display-context slots:
   - `data_10746408 = *(esi + 0x140)`
   - `data_1074640C = *(esi + 0x144)`
   - `data_10746410 = *(esi + 0x150)`
   - `data_10746414 = sub_10002BF0`
2. The host UI slab resolves those matching imports to:
   - `data_567478 = sub_4BEEF0`
   - `data_56747C = sub_4BEF00`
   - `data_567488 = sub_4BEF30`
3. The remaining raw import `data_567480 = 0x4BEEE0` is a relative jump thunk whose target lands at `sub_4F20C0`.

That is enough to treat `0x140..0x150` as a coherent Quake Live UI advertisement extension rather than a few unrelated leftovers.

## Import `0x148`: UI Init Thunk

The old "optional overlay hook" reading for import `82` is now too weak.

Observed local facts:

1. `_UI_Init` calls `(*(data_106B40A8 + 0x148))()` before wiring the extended display context.
2. The host slab entry at `data_567480` is a raw relative jump rather than an opaque data slot.
3. That jump lands at `sub_4F20C0`.
4. `sub_4F20C0` is a guarded advertisement-bridge dispatch:
   - it reads `data_12D2670`
   - if the bridge exists, it tail-dispatches to vtable slot `+0x44`
   - otherwise it returns immediately

This is best understood as a retail UI advertisement-bridge init/notify helper.

## Import `0x150`: `activateAdvert`

The `activateAdvert` path is now high-confidence.

Observed local facts:

1. The retail UI command table contains the extra script command string `activateAdvert`.
2. That command maps to the already-promoted UI helper `Script_ActivateAdvert` (`sub_10016AD0`).
3. `Script_ActivateAdvert` parses one integer argument and calls `(*(data_106B40D0 + 0xD0))(atoi(...))`.
4. `_UI_Init` fills that display-context slot from host import `0x150`.
5. Host import `0x150` is `sub_4BEF30`, which tailcalls `sub_4F22C0`.
6. `sub_4F22C0` guards `data_12D2670` and dispatches to advertisement-bridge slot `+0x68`.

That chain is strong enough to promote both the UI import wrapper and the bridge helper as the retail advertisement activation path.

## Imports `0x140` And `0x144`: Advert Cell Shader Setup/Refresh

The two earlier display-context callbacks now have enough behavioral evidence to name at the UI-import level.

Observed local facts:

1. The UI parser already exposes the Quake Live-specific advertisement fields:
   - `ItemParse_cellId` writes `arg1 + 0x28C`
   - `ItemParse_defaultContent` writes `arg1 + 0x290`
2. After menu parsing, `sub_10004D73` calls `sub_100154E0()`.
3. `sub_100154E0` walks menu items, filters on item type `0x225`, and calls `(*(data_106B40D0 + 0xC8))(defaultContent, &rect, cellId)`, storing the result back into the item background slot.
4. Menu activation/refresh paths repeatedly call `sub_100155A0(...)`.
5. `sub_100155A0` walks the same `0x225` items and calls `(*(data_106B40D0 + 0xCC))(defaultContent, bounds_or_sentinel, cellId)`, again storing the result into the item background slot.
6. The host providers for those slots are:
   - `sub_4BEEF0 -> sub_4F20E0`
   - `sub_4BEF00 -> sub_4F2120`
7. Both lower helpers fall back to `sub_4589D0(defaultContent, nullptr, 0)` when the advertisement bridge does not override them, which constrains both paths as shader-handle suppliers keyed by `defaultContent`.

The exact bridge-side slot names can still be refined later, but the UI wrapper roles are now stable: one is the post-parse advert-cell shader setup path, and the other is the runtime refresh path.

## Promoted Aliases

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4BEEF0` (`0x004BEEF0`) | `QLUIImport_SetupAdvertCellShader` | Observed plus bounded inference | UI display-context extension callback used immediately after menu parse to assign initial shader handles for item type `0x225` advert cells from `(defaultContent, rect, cellId)`. |
| `sub_4BEF00` (`0x004BEF00`) | `QLUIImport_RefreshAdvertCellShader` | Observed plus bounded inference | UI display-context extension callback used during menu activation/refresh to recompute advert-cell shader handles from `(defaultContent, bounds_or_sentinel, cellId)`. |
| `sub_4BEF30` (`0x004BEF30`) | `QLUIImport_ActivateAdvert` | Observed | UI display-context extension callback behind the retail `activateAdvert` script command. |
| `sub_4F20C0` (`0x004F20C0`) | `AdvertisementBridge_InitUI` | Observed plus bounded inference | No-arg advertisement-bridge helper reached from UI import `0x148` during `_UI_Init`. |
| `sub_4F22C0` (`0x004F22C0`) | `AdvertisementBridge_ActivateAdvert` | Observed | Bridge dispatch for advertisement activation, reached from `QLUIImport_ActivateAdvert`. |

## Open Questions

1. The lower bridge shader suppliers `sub_4F20E0` and `sub_4F2120` are now constrained by UI callsites, but I am still leaving their exact bridge-level names open for one more pass.
2. UI import `0x154` is still the retail `sub_4D7980` no-op, even though the GPL-style local reconstruction wires `trap_S_StopBackgroundTrack` there.
3. The neighboring imports at `0x158..0x160` (`sub_4B0340`, `sub_4BEF20`, `sub_4E1740`) remain outside this advert-cell extension cluster and still need separate ownership work.
