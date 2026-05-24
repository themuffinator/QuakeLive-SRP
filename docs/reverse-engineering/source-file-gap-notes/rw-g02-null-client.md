# `src/code/null/null_client.c` Gap Note

Last updated: 2026-05-24

Gap family: `RW-G02`
- Owning retail binary: `assets/quakelive/quakelive_steam.exe` for engine-owned surfaces, or the corresponding committed module corpus when this file sits in a module tree.
- Current classification: Closed as explicit compatibility-only null browser/advert lane; the file remains a retained null-client shim rather than a retail-equivalent runtime.

## Why this file is bounded

This file carries the modern null-client contract as an explicit compatibility boundary. The browser, advert, and client-owner entry points still resolve to no-ops or compatibility-safe defaults, but the browser/advert lane now advertises that status through source-visible provider, policy, parity-scope, and parity-reason cvars instead of reading like an unfinished retail Awesomium host.

## Observed facts

- Browser state is forced off through `ui_browserAwesomium` and `web_browserActive` cvars.
- Browser and advert cvars publish `Null host compatibility shim`, `compatibility-only null host`, `strict-retail-excluded`, and a stable reason explaining that the retail Windows Awesomium host is outside the null-client portability lane.
- Live-view, bound-window-object, cursor, event-publication, input, and advert-bridge entry points remain null-host stubs by design.
- The Awesomium plan treats this browser/advert lane as closed for strict Windows parity because it is an explicit compatibility exclusion; broader null-host runtime work remains a separate repo-wide portability question.

## Function-by-function status

| Function | Status | Notes |
| --- | --- | --- |
| `CL_NullResetAdvertisementBridgeState` | `bounded compatibility` | Null-client compatibility shim. |
| `CL_NullRefreshBrowserCvars` | `bounded compatibility` | Null-client compatibility shim. |
| `CL_Shutdown` | `bounded compatibility` | Null-client compatibility shim. |
| `CL_Init` | `bounded compatibility` | Null-client compatibility shim. |
| `CL_MouseEvent` | `bounded compatibility` | Null-client compatibility shim. |
| `Key_WriteBindings` | `bounded compatibility` | Null-client compatibility shim. |
| `Key_EnumerateBindings` | `bounded compatibility` | Null-client compatibility shim. |
| `CL_Frame` | `bounded compatibility` | Null-client compatibility shim. |
| `CL_PacketEvent` | `bounded compatibility` | Null-client compatibility shim. |
| `CL_CharEvent` | `bounded compatibility` | Null-client compatibility shim. |
| `CL_Disconnect` | `bounded compatibility` | Null-client compatibility shim. |
| `CL_MapLoading` | `bounded compatibility` | Null-client compatibility shim. |
| `CL_GameCommand` | `bounded compatibility` | Null-client compatibility shim. |
| `CL_KeyEvent` | `bounded compatibility` | Null-client compatibility shim. |
| `UI_GameCommand` | `bounded compatibility` | Null-client compatibility shim. |
| `CL_RefreshOnlineServicesBridgeState` | `bounded compatibility` | Explicitly forces the browser/online-service cvars into the null-host state and publishes the strict-retail exclusion labels. |
| `CL_WebHost_Init` | `bounded compatibility` | Initialises only the null browser-host compatibility state. |
| `CL_WebHost_Shutdown` | `bounded compatibility` | Shuts down only the null browser-host compatibility state. |
| `CL_WebHost_Frame` | `bounded compatibility` | No-op browser-host frame pump for the null runtime. |
| `CL_WebHost_HasLiveView` | `bounded compatibility` | Always false in the null compatibility host. |
| `CL_WebHost_HasBoundWindowObject` | `bounded compatibility` | Always false in the null compatibility host. |
| `CL_WebHost_GetCursorHandle` | `bounded compatibility` | Always returns `NULL`. |
| `CL_WebHost_NotifyAppActivation` | `bounded compatibility` | No-op null-host activation shim. |
| `CL_WebView_PublishEvent` | `bounded compatibility` | Null-host publication stub for browser events. |
| `CL_WebView_InvokeCommNotice` | `bounded compatibility` | Null-host browser bridge stub. |
| `CL_WebView_PublishGameError` | `bounded compatibility` | Null-host browser bridge stub. |
| `CL_WebView_PublishGameEnd` | `bounded compatibility` | Null-host browser bridge stub. |
| `CL_WebView_PublishCvarChange` | `bounded compatibility` | Null-client compatibility shim. |
| `CL_WebView_PublishBindChanged` | `bounded compatibility` | Null-host browser bridge stub. |
| `CL_WebView_PublishGameStart` | `bounded compatibility` | Null-host browser bridge stub. |
| `CL_WebView_PublishGameDemo` | `bounded compatibility` | Null-client compatibility shim. |
| `CL_WebView_PublishGameScreenshot` | `bounded compatibility` | Null-host browser bridge stub. |
| `CL_WebView_OnMouseMove` | `bounded compatibility` | Null-host input bridge stub. |
| `CL_WebView_OnMouseButtonEvent` | `bounded compatibility` | Null-host input bridge stub. |
| `CL_WebView_OnMouseWheelEvent` | `bounded compatibility` | Null-host input bridge stub. |
| `CL_WebView_OnKeyEvent` | `bounded compatibility` | Null-host input bridge stub. |
| `CL_AdvertisementBridge_RefreshLoadingViewParameters` | `bounded compatibility` | Null advert bridge shim. |
| `CL_AdvertisementBridge_UpdateLoadingViewParameters` | `bounded compatibility` | Null advert bridge shim. |
| `CL_AdvertisementBridge_InitUI` | `bounded compatibility` | Null advert bridge shim. |
| `CL_AdvertisementBridge_ActivateAdvert` | `bounded compatibility` | Null advert bridge shim. |
| `CL_AdvertisementBridge_SetActiveAdvert` | `bounded compatibility` | Null advert bridge shim. |
| `CL_ForwardCommandToServer` | `bounded compatibility` | Null-client compatibility shim. |
| `CL_ConsolePrint` | `bounded compatibility` | Null-client compatibility shim. |
| `CL_JoystickEvent` | `bounded compatibility` | Null-client compatibility shim. |
| `CL_InitKeyCommands` | `bounded compatibility` | Null-client compatibility shim. |
| `CL_CDDialog` | `bounded compatibility` | Null-client compatibility shim. |
| `CL_FlushMemory` | `bounded compatibility` | Null-client compatibility shim. |
| `CL_StartHunkUsers` | `bounded compatibility` | Null-client compatibility shim. |
| `CL_ShutdownAll` | `bounded compatibility` | Null-client compatibility shim. |
| `CL_CDKeyValidate` | `bounded compatibility` | Null-client compatibility shim. |

## Closure target

- Closed for the current null-client browser/advert scope because the no-op bridges are explicit and machine-testable compatibility shims.
- Reopen only if the repo begins claiming a richer null-host parity target than the current compatibility boundary, or if a real non-Windows browser/input/audio policy is adopted.
