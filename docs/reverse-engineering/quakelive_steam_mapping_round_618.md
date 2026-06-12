# Quake Live Steam Mapping Round 618: Workshop Callback Bootstrap And Finalization

Date: 2026-06-12

## Scope

This round pins the Steam Workshop callback bundle used by retail
`quakelive_steam.exe` for runtime Workshop download completion:

- `ItemInstalled_t`
- `DownloadItemResult_t`
- `SteamWorkshopCallbacks_Init`
- `SteamWorkshop_Init`

The focus is the launch/runtime contract around callback registration,
callback-vs-polling fallback, item finalization, and queue advancement. No live
Steam behavior was enabled, and no game launch was required.

## Retail Evidence

Observed Binary Ninja HLIL and Ghidra evidence:

- Alias map:
  - `FUN_004695c0` -> `SteamWorkshopCallbacks_OnItemInstalled`
  - `FUN_00469630` -> `SteamWorkshopCallbacks_OnDownloadItemResult`
  - `FUN_004696d0` -> `SteamWorkshopCallbacks_Init`
  - `FUN_004697a0` -> `SteamWorkshop_Init`
- Ghidra function rows keep the relevant bodies at `004695c0`, `00469630`,
  `004696d0`, and `004697a0`.
- Ghidra imports confirm `SteamAPI_RegisterCallback`, `SteamUtils`,
  `SteamUGC`, and `SteamGameServerUGC` are part of the retail Steam surface.
- Ghidra analysis symbols expose:
  - `CCallback<class_SteamWorkshopCallbacks,struct_ItemInstalled_t,0>::vftable`
  - `CCallback<class_SteamWorkshopCallbacks,struct_DownloadItemResult_t,0>::vftable`
- HLIL registration in `sub_4696d0` constructs two callback objects and
  registers callback ids `0xd4d` and `0xd4e`.
- HLIL `sub_4695c0` validates the retail app id through `SteamUtils`, skips
  invalid app ids, checks `ISteamUGC::GetItemState` slot `0xd0`, and finalizes
  an item when it is not already installed.
- HLIL `sub_469630` validates app id, checks the active download low/high item
  pair, finalizes on `EResult == 1`, and otherwise logs the failed result then
  advances the queue.
- HLIL `sub_4697a0` creates the Workshop callback bundle and then applies the
  retail startup gates for `pak00.pk3`, `fs_skipWorkshop`, `com_build`, and a
  non-null `ISteamUGC` interface.

## Source Reconstruction

SRP now has focused test coverage tying the retail evidence to these source
surfaces:

- raw ABI layouts:
  - `ql_steam_item_installed_raw_t`, size `0x10`
  - `ql_steam_download_item_result_raw_t`, size `0x18`
- callback ids:
  - `QL_STEAM_CALLBACK_ITEM_INSTALLED` = `0xd4d`
  - `QL_STEAM_CALLBACK_DOWNLOAD_ITEM_RESULT` = `0xd4e`
- dispatch shims:
  - `QL_Steamworks_DispatchItemInstalled`
  - `QL_Steamworks_DispatchDownloadItemResult`
- registration lifecycle:
  - `QL_Steamworks_RegisterWorkshopCallbacks`
  - `QL_Steamworks_UnregisterWorkshopCallbacks`
  - disabled inline stubs in default/offline builds
- client callback owners:
  - `CL_Steam_RegisterWorkshopCallbacks`
  - `CL_Steam_Workshop_OnItemInstalled`
  - `CL_Steam_Workshop_OnDownloadItemResult`
  - `SteamClient_RecoverCallbackBootstrap`
  - `CL_Steam_ShutdownCallbacks`

SRP intentionally keeps Workshop callback registration compatibility-owned:
retail client, lobby, and micro callback bundles must register for the callback
bootstrap to become active, while Workshop callbacks may fail independently and
leave the polling fallback in place. That matches the repository's online
service policy: live Workshop use remains opt-in, and default builds retain
safe stubs.

## Compatibility Boundary

This is an explicit online-service divergence boundary. Retail registers the
Workshop callbacks during `SteamWorkshop_Init`; SRP registers them after the
core callback bootstrap succeeds, and logs `callback-bootstrap` when the
callback route is unavailable. The runtime observable contract remains:

1. item-installed callbacks only finalize tracked items for the active app;
2. download-result callbacks only finalize the active download item;
3. successful results finalize and advance the queue;
4. failed results log the retail-style error and advance the queue; and
5. unavailable callbacks leave the existing polling fallback active.

## Validation

New focused parity gate:

```powershell
python -m pytest tests/test_platform_services.py::test_steam_workshop_callback_bootstrap_finalization_tracks_round_618 -q --tb=short
```

The gate checks aliases, Ghidra function/import rows, analysis symbols, HLIL
callback bodies, HLIL startup gates, vtable/string anchors, raw ABI layouts,
callback ids, platform dispatch shims, register/unregister order, source
callback filtering/finalization behavior, recovery/shutdown ownership, disabled
header stubs, harness callback capture names, this round note, and the Task
A487 planning anchor.

## Confidence

- Focused Steam Workshop callback bootstrap confidence:
  **before 94% -> after 99%**.
- Focused item-installed/download-result finalization confidence:
  **before 94% -> after 99%**.
- Overall Steam launch/runtime integration mapping confidence:
  **93.38% -> 93.40%**.
