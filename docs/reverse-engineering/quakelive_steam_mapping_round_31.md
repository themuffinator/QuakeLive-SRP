# Quake Live Steam Host Mapping Round 31

## Scope

This round revisits the last small advertisement-control helpers that were still open after Round 30.

Round 30 closed the advert-cell shader setup/refresh pair, but three pieces were still hanging off the same native cgame advertisement seam:

- the copied local callback at raw host `+0xE4`
- the no-argument raw bridge lifecycle helpers at `+0xF4` and `+0xF8`
- the naming split between the cgame-side `activateAdvert` command and the already-mapped UI `ActivateAdvert` bridge path

The primary local evidence for this round is:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `docs/reverse-engineering/quakelive_steam_mapping_round_15.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_29.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_30.md`
- `docs/reverse-engineering/cgame-mapping.md`

## `sub_4AFF40` And `sub_4F1EF0`: Active Advert Selector

The previously open `+0xE4` callback now closes as the active-advert state setter used by native cgame.

Observed local facts:

1. The committed Ghidra export exposes a stable wrapper row:
   - `FUN_004AFF40,004aff40,9,0,unknown`
2. The raw host cgame slab contains:
   - `data_565A44 = sub_4AFF40` (`+0xE4`)
3. `sub_4AFF40` is a pure tailcall to `sub_4F1EF0`.
4. `sub_10029210` copies raw host `+0xE4` into the local native cgame callback slab, which later backs `data_1074CCF8 + 0xD0`.
5. Native cgame's script-command table binds the literal command string:
   - `data_100750C8 -> "activateAdvert"`
   - `data_100750CC -> sub_10059CB0`
6. `sub_10059CB0` parses one integer argument and forwards it through that copied callback:
   - `(*(data_1074ccf8 + 0xd0))(atoi(&data_100d6a78))`
7. The host client shutdown path also calls the same lower helper with a literal zero:
   - `sub_4F1EF0(0)` in `sub_4B9E10`, the already-bounded `CL_Shutdown` path
8. `sub_4F1EF0` itself is a guarded bridge dispatch through vtable slot `+0x08`; when the bridge is absent it returns `0xFFFFFFFF`.

That combination closes the public behavior more tightly than the earlier generic "activate advert" reading. The integer argument is clearly advert-facing, and the shutdown-side zero call strongly suggests "set or clear the current advert selection/state" rather than a one-shot clickthrough action.

That is why this round promotes the cgame wrapper as `QLCGImport_SetActiveAdvert` and the underlying helper as `AdvertisementBridge_SetActiveAdvert`, while leaving the already-mapped UI-side `AdvertisementBridge_ActivateAdvert` (`sub_4F22C0`) intact as a separate higher-level activation path.

## `sub_4F2000` And `sub_4F2020`: Native Cgame Lifecycle Hooks

The remaining no-argument bridge helpers now close as native cgame lifecycle callbacks.

Observed local facts:

1. The raw native cgame host slab still contains:
   - `data_565A4C = j_sub_4F2000` (`+0xF4`)
   - `data_565A50 = j_sub_4F2020` (`+0xF8`)
2. Native cgame calls `+0xF4` once late in `CG_Init`:
   - `0x10029FA4  (*(data_1074cccc + 0xf4))()`
3. The repo already normalizes `sub_10029820` as `CG_Init` in the cgame mapping ledger and alias map.
4. Native cgame calls `+0xF8` from `sub_10029FC0`, which the repo already normalizes as `CG_Shutdown`:
   - `0x10029FCB  (*(data_1074cccc + 0xf8))()`
5. Only after that `+0xF8` callback does `CG_Shutdown` restore:
   - `("ui_mainmenu", &data_10068C04)`
6. The lower host helpers are pure guarded no-argument advertisement-bridge dispatches:
   - `sub_4F2000` -> vtable slot `+0x24`
   - `sub_4F2020` -> vtable slot `+0x28`
   - both return `0xFFFFFFFF` when `data_12D2670` is null
7. Those two helpers sit immediately beside the already-mapped raw cgame advertisement bridge band from Rounds 28 and 29:
   - `SetMapPath`
   - `SetFrameTime`
   - `UpdateViewParameters`
   - `ClearDelay`
8. Round 15 already established an analogous no-argument UI-side lifecycle helper:
   - `sub_4F20C0 -> AdvertisementBridge_InitUI`

This is enough to stabilize the lower helpers as advertisement-bridge init/shutdown hooks for native cgame rather than leaving them as anonymous pre/post-mainmenu side effects.

I am not promoting wrapper aliases for `004AFF60` / `004AFF70` in this round because the committed Ghidra export still does not surface stable function rows for those relative-jump wrappers. The behavior is closed at the lower helper level, but the wrapper symbols themselves are still export-corpus-weak.

## Why The UI And Cgame Names Differ

The retail script verb is shared:

- UI has `activateAdvert -> sub_10016AD0`
- native cgame has `activateAdvert -> sub_10059CB0`

But the lower bridge targets are not the same:

- UI reaches `sub_4F22C0` via bridge slot `+0x68`
- native cgame reaches `sub_4F1EF0` via bridge slot `+0x08`

The extra shutdown-side `sub_4F1EF0(0)` call makes the cgame helper look like active-advert state selection/reset, not the same final action as the UI-side `ActivateAdvert` path. So this round keeps the names intentionally split instead of forcing both helpers under one unstable verb.

## Promoted Aliases

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4AFF40` (`0x004AFF40`) | `QLCGImport_SetActiveAdvert` | Observed plus bounded inference | Native cgame callback wrapper behind the retail `activateAdvert` script command, forwarding one integer advert token/state value into the advertisement bridge. |
| `sub_4F1EF0` (`0x004F1EF0`) | `AdvertisementBridge_SetActiveAdvert` | Observed plus bounded inference | Shared advertisement-bridge helper that sets or clears the active advert selection/state; native cgame passes parsed advert ids, and `CL_Shutdown` clears it with `0`. |
| `sub_4F2000` (`0x004F2000`) | `AdvertisementBridge_InitCGame` | Observed plus bounded inference | No-argument advertisement-bridge lifecycle hook called once from native `CG_Init`. |
| `sub_4F2020` (`0x004F2020`) | `AdvertisementBridge_ShutdownCGame` | Observed plus bounded inference | No-argument advertisement-bridge lifecycle hook called from native `CG_Shutdown` before `ui_mainmenu` is restored. |

## Open Questions

1. The raw wrapper thunks at `004AFF60` / `004AFF70` are still documented-only because the committed Ghidra export does not yet expose stable rows for them.
2. `sub_4F1F10` and `sub_4F1FC0` remain neighboring advertisement-bridge helpers with insufficient public-behavior evidence for promotion.
3. The UI-side `sub_4F22C0 -> AdvertisementBridge_ActivateAdvert` remains intentionally separate from `AdvertisementBridge_SetActiveAdvert`; the shared script verb alone is not enough to collapse those two bridge slots.
