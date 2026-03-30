# Quake Live Steam Host Mapping Round 68

## Scope

This round continues the writable host reconstruction work after round 67,
using already-mapped `quakelive_steam.exe` command ownership to close another
concrete launcher/platform gap without introducing a full Steam workshop mount
pipeline or a browser runtime.

The target slice is the retail Steam command surface bounded earlier in:

- Round 02: `SteamOverlay_Command_f`, `SteamWorkshop_RequestDownload`,
  `SteamWorkshop_SubscribeItem`, `SteamWorkshop_UnsubscribeItem`, and
  `SV_AddOperatorCommands`
- Round 05: `SteamUGC_GetItemDownloadInfo`
- Round 07: the surrounding Steam social/overlay browser contract

Primary evidence for this source-reconstruction pass:

- `docs/reverse-engineering/quakelive_steam_mapping_round_02.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_05.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_07.md`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `src/common/platform/platform_steamworks.c`
- `src/code/client/cl_main.c`
- `src/code/server/sv_ccmds.c`

## Reconstructed Source Closures

### `sub_460E60`: `SteamOverlay_Command_f`

Observed retail facts already documented in Round 02:

1. `clientviewprofile` and `clientfriendinvite` are registered during client
   init and share one host command handler.
2. That handler resolves the selected player identity into a SteamID pair.
3. It chooses the retail overlay verb `steamid` or `friendadd` and forwards the
   request into `SteamFriends()->ActivateGameOverlayToUser`.

Writable source closure landed in this round:

- `cl_main.c` now reconstructs `CL_Steam_OverlayCommand_f`, mirroring the
  retail shared handler instead of leaving the UI menu commands unresolved.
- The client side now resolves `steamid` from `CS_PLAYERS + clientNum` and
  forwards `clientviewprofile` / `clientfriendinvite` through the new
  `QL_Steamworks_ActivateOverlayToUser` platform helper.

### `sub_469260` / `sub_4692B0`: manual workshop subscribe surface

Observed retail facts already documented in Rounds 01 and 02:

1. The host owns thin subscribe/unsubscribe wrappers over `SteamUGC`.
2. `steam_subscribeugc` and `steam_unsubscribeugc` parse one decimal item id
   and route straight into those wrappers.

Writable source closure landed in this round:

- `platform_steamworks.c` now exposes direct `SteamUGC` wrapper helpers for
  item-state queries, subscribe, unsubscribe, and download.
- `sv_ccmds.c` now reconstructs the manual `steam_subscribeugc` and
  `steam_unsubscribeugc` operator commands with the same one-argument item-id
  surface as the retail host.

### `sub_4699C0` and `sub_4DF010`: manual workshop download surface

Observed retail facts already documented in Round 02:

1. `steam_downloadugc` parses one decimal item id.
2. The handler forwards into `SteamWorkshop_RequestDownload(itemId, 0)`.
3. The immediate retail path checks cached item state and then dispatches
   `SteamUGC()->DownloadItem(..., 1)` when the item is not already installed.

Writable source closure landed in this round:

- `sv_ccmds.c` now reconstructs `steam_downloadugc` as a first-order manual
  SteamUGC download command instead of leaving the retail command name absent.
- The current source path mirrors the manual immediate-download branch by
  checking `QL_Steamworks_GetItemState`, printing the mapped in-cache/download
  status, and routing live requests through `QL_Steamworks_DownloadItem`.

## Verification

This round extends the Steamworks harness and the host parity assertions with
behavioral coverage for the new overlay and workshop wrapper helpers plus
static checks for the client/server command surfaces.

Targeted result:

- `python -m pytest tests/test_steamworks_harness.py tests/test_platform_services.py tests/test_ui_menu_files.py -q`
- `48 passed`

The new assertions prove:

- `QL_Steamworks_ActivateOverlayToUser` reaches the mapped SteamFriends
  overlay slot and preserves the dialog verb plus target identity
- the platform UGC helpers reach the mapped `SteamUGC` item-state,
  subscribe, unsubscribe, and download slots
- `clientviewprofile` / `clientfriendinvite` are now registered and routed
  through the reconstructed overlay helper
- `steam_downloadugc`, `steam_subscribeugc`, and `steam_unsubscribeugc` are
  now registered in `SV_AddOperatorCommands` and routed through the shared
  platform SteamUGC wrappers

## Completion Summary

No new alias rows were added in `references/analysis/quakelive_symbol_aliases.json`
this round; the mapping work here was consumed as source reconstruction against
already-promoted host ownership.

Current global `quakelive_steam.exe` mapping coverage remains:

- raw alias entries: `944`
- address-backed aliases: `943`
- Ghidra function coverage: `17.230%` of `5473`

Source reconstruction improved the writable Task 21 host baseline by removing
another retail-mapped dead command surface: the Steam overlay menu commands and
the manual workshop operator commands now route through real SteamFriends and
SteamUGC host shims instead of remaining absent from the reconstructed engine.
