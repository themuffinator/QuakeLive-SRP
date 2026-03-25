# Quake Live Steam Host Mapping Round 30

## Scope

This round revisits the native `cgamex86.dll` advertisement callback seam at raw host offsets `+0xDC..+0xE4`.

Round 29 closed the adjacent map/delay helpers at `+0xF0..+0x104`, but the earlier callback pair at `+0xDC` and `+0xE0` still only had structural ownership. A fresh pass through the native cgame HUD/menu advert update code and the shared advertisement-bridge bodies now closes those two rows as the cgame-side advert-cell shader setup/refresh pair.

The primary local evidence for this round is:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `docs/reverse-engineering/quakelive_steam_mapping_round_15.md`
- `docs/reverse-engineering/ui-mapping-pass-2026-03-20.md`

## Raw Native Cgame Callback Rows At `+0xDC..+0xE4`

The relevant raw host rows in the native cgame slab are:

- `data_565A34 = sub_4AFF20` (`+0xDC`)
- `data_565A38 = sub_4AFF30` (`+0xE0`)
- `data_565A44 = sub_4AFF40` (`+0xE4`)

Observed local facts:

1. `sub_10029210` copies those raw rows into the local native cgame callback slab:
   - `data_10A256E8 = *(result + 0xDC)`
   - `data_10A256EC = *(result + 0xE0)`
   - `data_10A256F0 = *(result + 0xE4)`
2. Those locals back the later `data_1074CCF8 + 0xC8`, `+0xCC`, and `+0xD0` callback uses in native cgame HUD/menu code rather than the earlier raw-only bridge control rows from Rounds 28 and 29.
3. The committed Ghidra export exposes stable rows for the host wrappers and lower helpers:
   - `FUN_004AFF20,004aff20,9,0,unknown`
   - `FUN_004AFF30,004aff30,9,0,unknown`
   - `FUN_004AFF40,004aff40,9,0,unknown`
   - `FUN_004F21E0,004f21e0,53,0,unknown`
   - `FUN_004F2220,004f2220,53,0,unknown`
   - `FUN_004F1EF0,004f1ef0,21,0,unknown`

That is enough to treat `+0xDC..+0xE4` as a coherent native cgame advert-callback band rather than a few unrelated tailcalls.

## `sub_4AFF20` And `sub_4F21E0`: Setup Advert Cell Shader

This pair is now stable enough to promote.

Observed local facts:

1. `data_565A34 = sub_4AFF20`, and `sub_4AFF20` is a pure tailcall to `sub_4F21E0`.
2. Native cgame copies that raw host row into the local callback slab and later invokes it via `data_1074CCF8 + 0xC8`.
3. `sub_10058740` walks the local HUD/menu item list, filters on item type `0x225`, computes a live rectangle, and calls:
   - `(*(data_1074ccf8 + 0xc8))(ecx_1[0xa4], &var_14, ecx_1[0xa3])`
4. The call result is stored back into the item background slot:
   - `*(*esi_1 + 0xe8) = ...`
5. `ecx_1[0xA3]` and `ecx_1[0xA4]` are the same retail advert item fields already bounded on the UI side as `cellId` and `defaultContent`.
6. `sub_4F21E0` first dispatches through advertisement-bridge vtable slot `+0x50`.
7. If the bridge returns `0`, `sub_4F21E0` falls back to:
   - `sub_4589D0(arg1, nullptr, 0)`

This is the same "initial shader handle from `(defaultContent, rect, cellId)`" contract already documented for `QLUIImport_SetupAdvertCellShader` in Round 15 and the UI mapping pass, but here it is reached through the native cgame callback band.

That is enough to promote `sub_4AFF20` as the cgame import wrapper and `sub_4F21E0` as the owning shared advertisement-bridge setup helper.

## `sub_4AFF30` And `sub_4F2220`: Refresh Advert Cell Shader

The adjacent refresh pair closes from the same evidence pattern.

Observed local facts:

1. `data_565A38 = sub_4AFF30`, and `sub_4AFF30` is a pure tailcall to `sub_4F2220`.
2. Native cgame copies that raw host row into the local callback slab and later invokes it via `data_1074CCF8 + 0xCC`.
3. `sub_10058800` walks the same advert-item list and calls the callback in two bounded forms:
   - active/visible path: `(*(data_1074ccf8 + 0xcc))(defaultContent, &liveRect, cellId)`
   - hidden/inactive path: `(*(data_1074ccf8 + 0xcc))(defaultContent, &sentinelRect, cellId)`
4. The sentinel rectangle is the repeated `-1, -1, -1, -1` slab at `esp_2[6..9]`.
5. Both paths store the returned shader handle back into the same item background slot.
6. `sub_4F2220` first dispatches through advertisement-bridge vtable slot `+0x58`.
7. If the bridge returns `0`, `sub_4F2220` falls back to:
   - `sub_4589D0(arg1, nullptr, 0)`

This matches the already-mapped UI runtime refresh contract from Round 15 and `Menu_RefreshAdvertCellShaders`: the callback recomputes the advert-cell shader handle from `(defaultContent, bounds_or_sentinel, cellId)` rather than performing one-time setup.

That is enough to promote `sub_4AFF30` as the native cgame refresh wrapper and `sub_4F2220` as the shared advertisement-bridge refresh helper.

## Why The Bridge Names Stay Generic

The wrapper names stay `QLCGImport_*` because native cgame reaches these helpers through its copied local callback slab. The lower helpers keep the generic `AdvertisementBridge_*` prefix because the underlying bridge is shared across UI and native cgame, and the observed contracts are identical to the already-mapped UI advert-cell shader paths apart from the caller subsystem.

## What Stays Open

The third callback in this local band remains open:

- `data_565A44 = sub_4AFF40` (`+0xE4`)
- `sub_4AFF40 -> sub_4F1EF0`

Observed local facts:

1. Native cgame copies `+0xE4` into local callback slot `data_1074CCF8 + 0xD0`.
2. A later script-command path calls it with one parsed integer argument:
   - `(*(data_1074ccf8 + 0xd0))(atoi(&data_100d6a78))`
3. That is enough to bound it as advertisement-facing, but I still do not have the exact retail script-command string or public behavior pinned tightly enough to promote a stable name without churn.

So this round promotes only the setup/refresh pairs that close directly from the shared argument contract and the bridge fallback bodies.

## Promoted Aliases

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4AFF20` (`0x004AFF20`) | `QLCGImport_SetupAdvertCellShader` | Observed plus bounded inference | Native cgame callback wrapper that supplies the initial advert-cell shader handle from `(defaultContent, rect, cellId)` and stores it into the item background slot. |
| `sub_4AFF30` (`0x004AFF30`) | `QLCGImport_RefreshAdvertCellShader` | Observed plus bounded inference | Native cgame callback wrapper that recomputes advert-cell shader handles from `(defaultContent, bounds_or_sentinel, cellId)` during runtime refresh. |
| `sub_4F21E0` (`0x004F21E0`) | `AdvertisementBridge_SetupAdvertCellShader` | Observed plus bounded inference | Shared advertisement-bridge shader supplier used for the initial advert-cell setup path, with fallback to `sub_4589D0(defaultContent, nullptr, 0)`. |
| `sub_4F2220` (`0x004F2220`) | `AdvertisementBridge_RefreshAdvertCellShader` | Observed plus bounded inference | Shared advertisement-bridge shader supplier used for advert-cell refresh, again falling back to `sub_4589D0(defaultContent, nullptr, 0)` when the bridge does not override the result. |

## Open Questions

1. `sub_4AFF40` / `sub_4F1EF0` still need the exact retail script-command string before promotion.
2. The no-argument lifecycle helpers `sub_4F2000` and `sub_4F2020` from Round 29 remain bounded but unnamed.
3. The neighboring one-argument bridge helper `sub_4F1FC0` is still one direct retail argument contract short of a stable rename.
