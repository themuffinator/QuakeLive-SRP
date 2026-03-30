# `quakelive_steam.exe` Mapping Appendix

## Scope

This companion document accompanies the main reverse-engineering report and captures the practical inventory used during the mapping pass. It focuses on address anchors, confirmed aliases, subsystem clusters, and the largest remaining functions in the Ghidra export so the next pass can pick up quickly.

## Confirmed subsystem anchors

### Browser / Awesomium host

| Address | Function | Status |
|---|---|---|
| `0x00434620` | `QLResourceInterceptor_OnRequest` | High confidence |
| `0x004F23E0` | `QLWebView_SetLocationHash` | High confidence |
| `0x004F2D30` | `QLWebHost_OpenURL` | High confidence |
| `0x004F3260` | `QLWebView_PublishEvent` | High confidence |
| `0x004F3420` | `QLWebView_PublishGameKey` | High confidence |
| `0x004F3570` | `QLWebView_PublishGameError` | High confidence |
| `0x004F3600` | `QLWebView_PublishGameEnd` | High confidence |
| `0x004F38F0` | `QLWebView_PublishGameStart` | High confidence |
| `0x004F3CD0` | Browser command registration | High confidence |

### Steam client / overlay

| Address | Function | Status |
|---|---|---|
| `0x00460510` | `SteamClient_IsInitialized` | High confidence |
| `0x00460550` | `SteamClient_GetSteamID` | High confidence |
| `0x004605C0` | `SteamClient_GetAuthSessionTicket` | High confidence |
| `0x004605F0` | `SteamClient_CancelAuthTicket` | High confidence |
| `0x00460E60` | `SteamOverlay_Command_f` | High confidence |
| `0x004613A0` | `SteamCallbacks_Init` | High confidence |
| `0x00461500` | `SteamClient_Init` | High confidence |

### Steam lobby / matchmaking

| Address | Function | Status |
|---|---|---|
| `0x004645A0` | `SteamLobbyCallbacks_OnLobbyChatMessage` | High confidence |
| `0x00464720` | `SteamLobbyCallbacks_OnLobbyGameCreated` | High confidence |
| `0x00464830` | `SteamLobbyCallbacks_OnLobbyKicked` | High confidence |
| `0x00464900` | `SteamLobbyCallbacks_OnGameLobbyJoinRequested` | High confidence |
| `0x004649E0` | `SteamLobby_LeaveLobby` | High confidence |
| `0x00464BF0` | `SteamLobbyCallbacks_OnLobbyCreated` | High confidence |
| `0x00464D90` | `SteamLobbyCallbacks_OnLobbyEnter` | High confidence |
| `0x004652E0` | `SteamLobbyCallbacks_OnLobbyChatUpdate` | High confidence |
| `0x00465490` | `SteamLobbyCallbacks_OnLobbyDataUpdate` | High confidence |
| `0x004656A0` | `SteamLobbyCallbacks_Init` | High confidence |
| `0x00465840` | `SteamLobby_Init` | High confidence |
| `0x004658A0` | `SteamMicroCallbacks_OnAuthorizationResponse` | High confidence |
| `0x004659E0` | `SteamMicroCallbacks_Init` | High confidence |

### Steam server / auth

| Address | Function | Status |
|---|---|---|
| `0x00465B00` | `SteamServer_PublishSteamID` | High confidence |
| `0x00465B70` | `SteamServerCallbacks_OnP2PSessionRequest` | High confidence |
| `0x00465FD0` | `SteamServer_BeginAuthSession` | High confidence |
| `0x004661E0` | `SteamServer_EndAuthSession` | High confidence |
| `0x00466260` | `SteamServer_UpdatePublishedState` | High confidence |
| `0x00466850` | `SteamServer_Frame` | High confidence |
| `0x00466DB0` | `SteamServerCallbacks_Init` | High confidence |
| `0x00466ED0` | `SteamServer_Init` | High confidence |

### Steam stats

| Address | Function | Status |
|---|---|---|
| `0x004670C0` | `SteamStats_FlushPendingValues` | High confidence |
| `0x004671D0` | `SteamStats_OnStatsReceived` | High confidence |
| `0x004672D0` | `SteamStats_SetAchievement` | High confidence |
| `0x00467360` | `SteamStats_OnStatsStored` | High confidence |
| `0x00467560` | `SteamStats_Shutdown` | High confidence |
| `0x00467850` | `SteamStats_Init` | High confidence |
| `0x00467B10` | `SteamStats_RemovePlayerSession` | High confidence |
| `0x00467CD0` | `SteamStats_CreatePlayerSession` | High confidence |
| `0x00467D40` | `SteamStats_AddFieldValue` | High confidence |
| `0x00467E00` | `SteamStats_UnlockAchievement` | High confidence |
| `0x00467F70` | `SteamStats_HasAchievement` | High confidence |
| `0x00468030` | `SteamStats_ProcessEvent` | High confidence |
| `0x00468EE0` | `SteamStats_BroadcastSummary` | High confidence |

### Workshop / UGC

| Address | Function | Status |
|---|---|---|
| `0x00469260` | `SteamWorkshop_SubscribeItem` | High confidence |
| `0x004692B0` | `SteamWorkshop_UnsubscribeItem` | High confidence |
| `0x00469400` | `SteamWorkshop_AdvanceDownloadQueue` | High confidence |
| `0x00469470` | `SteamWorkshop_FinalizeItem` | High confidence |
| `0x004695C0` | `SteamWorkshopCallbacks_OnItemInstalled` | High confidence |
| `0x00469630` | `SteamWorkshopCallbacks_OnDownloadItemResult` | High confidence |
| `0x004696D0` | `SteamWorkshopCallbacks_Init` | High confidence |
| `0x004697A0` | `SteamWorkshop_Init` | High confidence |
| `0x004699C0` | `SteamWorkshop_RequestDownload` | High confidence |
| `0x004DF010` | `SteamCmd_DownloadUGC_f` | High confidence |
| `0x004DF070` | `SteamCmd_SubscribeUGC_f` | High confidence |
| `0x004DF0D0` | `SteamCmd_UnsubscribeUGC_f` | High confidence |

## Opaque bridge area still needing work

The dispatch object at `data_12d2670` remains one of the main unresolved areas. The small wrappers around `0x004F1F10` through roughly `0x004F2280` appear to forward through a vtable and return safe defaults when the bridge is absent. The working hypothesis is that this region bridges native engine state into the browser/UI host.

### Candidate bridge wrappers

| Address | Notes |
|---|---|
| `0x004F1EE0` | Likely base JS-handler or bridge thunk |
| `0x004F1F10` | Vtable wrapper |
| `0x004F1F30` | Vtable wrapper |
| `0x004F1F50` | Vtable wrapper |
| `0x004F1F70` | Vtable wrapper |
| `0x004F1FC0` | Vtable wrapper |
| `0x004F1FE0` | Vtable wrapper |
| `0x004F2040` | Vtable wrapper |
| `0x004F2080` | Vtable wrapper |
| `0x004F20A0` | Vtable wrapper |
| `0x004F20E0` | Vtable wrapper |
| `0x004F2120` | Vtable wrapper |
| `0x004F2160` | Vtable wrapper |
| `0x004F2180` | Vtable wrapper |
| `0x004F21E0` | Vtable wrapper |
| `0x004F2220` | Vtable wrapper |
| `0x004F2260` | Vtable wrapper |
| `0x004F2280` | Vtable wrapper |

## Largest unmapped functions from `functions.csv`

These are the biggest remaining bodies in the exported Ghidra function list and should be prioritised because they likely correspond to major subsystems or dense orchestration code.

| Rank | Address | Name | Size |
|---|---|---|---:|
| 1 | `0x004728D0` | `FUN_004728d0` | 8865 |
| 2 | `0x00470B40` | `FUN_00470b40` | 7528 |
| 3 | `0x004896E0` | `FUN_004896e0` | 6429 |
| 4 | `0x004FDE10` | `FUN_004fde10` | 5466 |
| 5 | `0x0051E4F0` | `FUN_0051e4f0` | 5099 |
| 6 | `0x005049D0` | `FUN_005049d0` | 4761 |
| 7 | `0x00507DD0` | `FUN_00507dd0` | 4001 |
| 8 | `0x00439E20` | `FUN_00439e20` | 3882 |
| 9 | `0x0048C980` | `FUN_0048c980` | 3809 |
| 10 | `0x00468030` | `SteamStats_ProcessEvent` | 3753 |
| 11 | `0x004872E0` | `FUN_004872e0` | 3752 |
| 12 | `0x00449000` | `FUN_00449000` | 3639 |
| 13 | `0x005181F0` | `FUN_005181f0` | 3610 |
| 14 | `0x00455E10` | `FUN_00455e10` | 3503 |
| 15 | `0x0050A1A0` | `FUN_0050a1a0` | 3327 |
| 16 | `0x004B1100` | `FUN_004b1100` | 3172 |
| 17 | `0x0048B0E0` | `FUN_0048b0e0` | 3155 |
| 18 | `0x0048BD40` | `FUN_0048bd40` | 3118 |
| 19 | `0x0044DCD0` | `FUN_0044dcd0` | 2988 |
| 20 | `0x00514550` | `FUN_00514550` | 2980 |

## Practical next-pass queue

1. Finish the `0x004F1EE0` to `0x004F2280` bridge region and recover real method names.
2. Take one of the top ten large bodies in the `0x00470***` range and determine whether it belongs to rendering, networking, UI state, or filesystem logic.
3. Resolve `0x004D2E80`, which appears adjacent to workshop/filesystem behaviour and was already flagged in prior notes.
4. Split the `0x004670C0` to `0x00468EE0` stats cluster into session management, field writes, and broadcast helpers.
5. Build a stable symbol import list for all high-confidence aliases so the Ghidra database can be re-labelled automatically.

## Source basis

This appendix was derived from the main mapping report plus the exported Ghidra function inventory in `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`, which records function names, entry points, and sizes. The large-function queue above was taken directly from the head of that export.
