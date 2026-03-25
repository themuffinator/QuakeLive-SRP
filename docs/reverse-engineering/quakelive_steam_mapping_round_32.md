# Quake Live Steam Host Mapping Round 32

## Scope

This round closes the remaining lower UI advert-cell shader suppliers behind the shared advertisement bridge.

Round 15 already promoted the UI import wrappers `sub_4BEEF0` and `sub_4BEF00` as the setup/refresh callbacks used by retail menu advert items, and Round 30 later closed the analogous native cgame bridge pair at `sub_4F21E0` / `sub_4F2220`. The remaining gap was the lower UI-side pair `sub_4F20E0` / `sub_4F2120`, which still had stable wrapper ownership but no bridge-level names.

The primary local evidence for this round is:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/hlil/quakelive/uix86.all/uix86.dll_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `docs/reverse-engineering/quakelive_steam_mapping_round_15.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_30.md`
- `docs/reverse-engineering/ui-mapping-pass-2026-03-20.md`

## `sub_4F20E0`: UI Setup Advert Cell Shader Supplier

This helper is now stable enough to promote at the bridge level.

Observed local facts:

1. The committed Ghidra export exposes:
   - `FUN_004F20E0,004f20e0,53,0,unknown`
2. The host UI import slab contains:
   - `data_567478 = sub_4BEEF0`
3. `sub_4BEEF0` is a pure tailcall to `sub_4F20E0`.
4. During `_UI_Init`, retail UI copies host import `0x140` into the extended display-context callback slot used later as:
   - `data_106B40D0 + 0xC8`
5. `Menu_SetupAdvertCellShaders` (`sub_100154E0`) walks menu items, filters on item type `0x225`, and calls:
   - `(*(data_106b40d0 + 0xc8))(defaultContent, &rect, cellId)`
6. The result of that callback is stored into the item background slot, which closes the callback as the initial shader-handle supplier for retail UI advert cells.
7. `sub_4F20E0` first dispatches through advertisement-bridge vtable slot `+0x54`.
8. If the bridge does not override the result, `sub_4F20E0` falls back to:
   - `sub_4589D0(arg1, nullptr, 0)`

That is the same setup-side contract already bounded on the UI wrapper side in Round 15. The lower helper is therefore the UI-side advertisement-bridge shader supplier used during initial menu advert-cell setup.

## `sub_4F2120`: UI Refresh Advert Cell Shader Supplier

The adjacent refresh helper closes from the same evidence pattern.

Observed local facts:

1. The committed Ghidra export exposes:
   - `FUN_004F2120,004f2120,53,0,unknown`
2. The host UI import slab contains:
   - `data_56747C = sub_4BEF00`
3. `sub_4BEF00` is a pure tailcall to `sub_4F2120`.
4. During `_UI_Init`, retail UI copies host import `0x144` into the extended display-context callback slot used later as:
   - `data_106B40D0 + 0xCC`
5. `Menu_RefreshAdvertCellShaders` (`sub_100155A0`) walks the same advert-item list and calls the callback in the two already-bounded forms:
   - `(...)(defaultContent, &liveRect, cellId)`
   - `(...)(defaultContent, &sentinelRect, cellId)`
6. That result is again stored into the item background slot, which closes the callback as the runtime refresh-side shader supplier for retail UI advert cells.
7. `sub_4F2120` first dispatches through advertisement-bridge vtable slot `+0x5C`.
8. If the bridge does not override the result, `sub_4F2120` falls back to:
   - `sub_4589D0(arg1, nullptr, 0)`

That is enough to promote the lower helper as the UI refresh-side advert-cell shader supplier.

## Why The New Names Keep The `UI` Qualifier

Round 30 already promoted the analogous native cgame lower pair:

- `sub_4F21E0 -> AdvertisementBridge_SetupAdvertCellShader`
- `sub_4F2220 -> AdvertisementBridge_RefreshAdvertCellShader`

The UI helpers in this round are separate bridge slots:

- `sub_4F20E0` uses slot `+0x54`
- `sub_4F2120` uses slot `+0x5C`

Because the underlying bridge clearly exposes distinct UI and native-cgame shader-supplier slots, this round keeps the `UI` qualifier on the lower helper names instead of collapsing them onto the already-promoted cgame-side pair.

## Promoted Aliases

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4F20E0` (`0x004F20E0`) | `AdvertisementBridge_SetupUIAdvertCellShader` | Observed plus bounded inference | Shared advertisement-bridge shader supplier used by the retail UI setup callback to assign initial advert-cell shader handles from `(defaultContent, rect, cellId)`. |
| `sub_4F2120` (`0x004F2120`) | `AdvertisementBridge_RefreshUIAdvertCellShader` | Observed plus bounded inference | Shared advertisement-bridge shader supplier used by the retail UI refresh callback to recompute advert-cell shader handles from `(defaultContent, bounds_or_sentinel, cellId)`. |

## Open Questions

1. `sub_4F1F10` remains open. The current signal only bounds it as a one-argument advertisement-bridge state setter reached from the `VID_AppActivate` path.
2. `sub_4AFFC0 -> sub_4F1FC0` still lacks a stable public callsite in the committed retail corpus.
3. `sub_4F21C0` is still only bounded as a no-argument advertisement-bridge slot with no behavior-level owner.
