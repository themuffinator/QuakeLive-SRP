# Awesomium browser wiring map

This note records the current retail mapping for the Quake Live Awesomium browser host and the source reconstruction seams that correspond to it. It is intentionally scoped to evidence already committed in this repository.

## Evidence anchors

- `references/hlil/quakelive_steam.exe/00_12d640/part05.txt:11025` shows retail opening `asset://ql/index.html` when the online browser path is allowed.
- `references/hlil/quakelive_steam.exe/00_12d640/part05.txt:15880` maps the browser bootstrap function that initializes WebCore, WebSession, data sources, WebView, handlers, URL load, resume, focus, and `web_browserActive`.
- `references/hlil/quakelive_steam.exe/00_12d640/part06.txt:22491` maps `QLResourceInterceptor` request behavior.
- `references/hlil/quakelive_steam.exe/00_12d640/part06.txt:35571` maps the Awesomium-facing vtables for `QLResourceInterceptor`, dialog/view/load handlers, `QLJSHandler`, `DataPakSource`, and `SteamDataSource`.
- `references/hlil/quakelive_steam.exe/00_12d640/part06.txt:49745` lists the Awesomium imports used by the retail executable, including JS object/value helpers, WebCore initialization, WebView calls, BitmapSurface copy, DataSource send response, and Steam API symbols.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:15728` maps `web_clearCache` to WebSession slot `0x1c`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:15739` maps `web_reload` to WebSession slot `0x1c` followed by WebView slot `0x78`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:15747` maps shutdown to WebView destroy plus `WebCore::Shutdown`, with no WebSession slot `0x1c` call.
- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c:36881` is the structured companion decompile for the WebCore/WebView bootstrap.
- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c:45532` is the structured companion decompile for the resource interceptor.

## Retail bootstrap sequence

| Order | Retail behavior | Current source owner |
| --- | --- | --- |
| 1 | Gate browser startup on platform/service state, then request `asset://ql/index.html`. | `src/code/client/cl_main.c`, `src/code/client/cl_awesomium_win32.cpp` |
| 2 | Construct `Awesomium::WebConfig` and call `Awesomium::WebCore::Initialize`. | `CL_Awesomium_Startup` |
| 3 | Construct `Awesomium::WebPreferences`. Retail sets two observed local preference bytes before WebSession creation. | Partially reconstructed in `CL_Awesomium_Startup`; exact preference field names remain open. |
| 4 | Create a WebSession using `fs_homepath`, then call WebSession slot `0x18`. | `CL_Awesomium_CreateSession` |
| 5 | Construct `DataPakSource("web.pak")` and add it under source host `QL`. | `CL_Awesomium_CreateSession`, `src/code/client/cl_webpak.c` |
| 6 | Construct `SteamDataSource` and add it under source host `steam`. | Offline-safe avatar/resource bridge in `src/code/client/cl_steam_resources.c`; not yet attached as a native live Awesomium data source. |
| 7 | Construct `QLResourceInterceptor` and set it on WebCore. | Request behavior reconstructed in `src/code/client/cl_steam_resources.c`; live native interceptor object is still a compatibility seam. |
| 8 | Create WebView with current video dimensions and the session. | `CL_Awesomium_Startup` |
| 9 | Construct `QLJSHandler` and install it on WebView vtable slot `0x12c`. | Source bridge reconstructs the browser-visible `qz_instance` method-name surface through startup script injection, including deterministic `FakeClient.qz_instance` creation. Native JSValue marshalling is still open. |
| 10 | Wait up to ten 100 ms helper iterations for browser helper initialization. | `CL_Awesomium_Startup` has equivalent polling around view initialization. |
| 11 | Install dialog, view, and load handlers on WebView slots `0x34`, `0x24`, and `0x28`. | Handler vtables are mapped; source currently uses direct host state and surface polling rather than native objects. |
| 12 | Call WebView slot `0xa0` with `1`, then load the URL through slot `0x64`. | URL load and transparent-state setup are reconstructed. |
| 13 | Resume rendering through slot `0xac`, focus through slot `0xb0`, update activation/cursor state, set `web_browserActive` to `1`, and enable key catcher. | `CL_Awesomium_OpenURL`, `CL_Awesomium_Startup`, and client-side browser host drawing/input paths. |

## Awesomium vtable and import mapping

| Retail object/API | Evidence | Source reconstruction status |
| --- | --- | --- |
| `WebSession` bootstrap slot `0x18` | HLIL bootstrap calls slot `0x18` immediately after `WebCore::CreateWebSession`. | Reconstructed only when the external SDK C API exposes optional `_Awe_WebSession_Initialize@4`; no local vtable fallback is retained. |
| `WebSession` cache-clear slot `0x1c` | HLIL `web_clearCache` calls slot `0x1c`; `web_reload` calls the same slot before WebView reload; staged and retail `awesomium.dll` export `_Awe_WebSession_ClearCache@4`. | Reconstructed through optional `_Awe_WebSession_ClearCache@4`; `_Awe_WebSession_Release@4` remains shutdown-only, and reload still follows with the SDK WebView ignore-cache flag. |
| `WebView::LoadURL` slot `0x64` | HLIL bootstrap and Awesomium import list | Reconstructed through `_Awe_WebView_LoadURL@8`. |
| `WebView::Stop` slot `0x74` | HLIL/import surface | Reconstructed through `_Awe_WebView_Stop@4`. |
| `WebView::surface` slot `0x84` | BitmapSurface copy path | Reconstructed and used by `CL_Awesomium_CopySurface`. |
| `WebView::Resize` slot `0x9c` | Video size integration | Reconstructed through `_Awe_WebView_Resize@12`. |
| `WebView::SetTransparent` slot `0xa0` | HLIL bootstrap calls slot `0xa0` with `1` before URL presentation | Reconstructed through the SDK C API export `_Awe_WebView_SetTransparent@8`. |
| `WebView::PauseRendering` slot `0xa8` | HLIL hide-browser path calls slot `0xa8` before deactivating `web_browserActive` | Reconstructed through `_Awe_WebView_PauseRendering@4`. |
| `WebView::ExecuteJavascript` slot `0x124` | Awesomium import list and retail WebView ABI layout | Reconstructed in this pass as `CL_Awesomium_ExecuteJavascript`. |
| `WebView::set_js_method_handler` slot `0x12c` | HLIL bootstrap constructs `QLJSHandler` and calls slot `0x12c`; `data_55c008` stores the 34-entry `qz_instance` method table. | Native handler object remains mapped, while the source-visible browser contract is reconstructed through the injected `qz_instance`/`FakeClient.qz_instance` bridge. |
| `WebView::ResumeRendering` slot `0xac` | HLIL bootstrap | Reconstructed through `_Awe_WebView_ResumeRendering@4`. |
| `WebView::Focus` slot `0xb0` | HLIL bootstrap | Reconstructed through `_Awe_WebView_Focus@4`. |
| `WebView::Unfocus` slot `0xb4` | HLIL hide-browser path calls slot `0xb4` after pause rendering | Reconstructed through `_Awe_WebView_Unfocus@4`. |
| `WebView::SetZoom` slot `0xc4` | HLIL bootstrap passes the `web_zoom` cvar integer to slot `0xc4` before rebuilding the surface | Kept as an optional SDK C API import `_Awe_WebView_SetZoom@8`; no local vtable fallback is retained. |
| Mouse input slots `0xd0` to `0xdc` | Input path reconstruction | Reconstructed through SDK C API exports. |
| `WebKeyboardEvent` / `WebView::InjectKeyboardEvent` slot `0xe0` | HLIL `sub_4f28a0` constructs `Awesomium::WebKeyboardEvent(eventType, virtualKeyCode, nativeKeyCode)` and dispatches it through WebView slot `0xe0`; the import list names `??0WebKeyboardEvent@Awesomium@@QAE@IIJ@Z`. | Reconstructed through the SDK event-object path: `_Awe_new_WebKeyboardEvent_1@12`, `_Awe_WebView_InjectKeyboardEvent@8`, and `_Awe_delete_WebKeyboardEvent@4`. |
| `BitmapSurface::CopyTo` and dirty flag | Import list | Reconstructed in surface copy/upload path. |
| `Awesomium::DataPakSource` | Retail vtable and bootstrap | Reconstructed enough to load `web.pak`; source additionally searches deterministic filesystem roots. |
| `Awesomium::DataSource::SendResponse` | Import list | Mapped; source fallback request path is implemented in `cl_webpak.c` and `cl_steam_resources.c`. |

## Handler and data source wiring

| Retail class | Retail vtable evidence | Observed purpose | Current source equivalent |
| --- | --- | --- | --- |
| `QLResourceInterceptor` | vtable at `0x00547f94` | Intercepts `asset://ql/...`; maps screenshot URLs under `<fs_homepath>/<fs_game>/screenshots/`; maps other `asset://ql/...` paths through `fs_webpath` when set; navigation filter never blocks. | `QLResourceInterceptor_RequestRetailHost`, `QLResourceInterceptor_MapRetailPath`, and `QLResourceInterceptor_OnFilterNavigation` in `src/code/client/cl_steam_resources.c`. |
| `QLDialogHandler` | vtable at `0x00547fa8` | Dialog callback surface for WebView. | Mapped only; no live native object yet. |
| `QLViewHandler` | vtable at `0x00547fc0` | View lifecycle/paint-facing notifications. | Replaced by host polling of view/surface state. |
| `QLLoadHandler` | vtable at `0x00547fe8` | Load lifecycle callbacks. | Mapped only; startup script and direct state checks cover the currently required behavior. |
| `QLJSHandler` | vtable at `0x00548010` | Handles JS method calls and query responses for the menu. | Reconstructed with a deterministic injected `qz_instance`/`FakeClient` bridge. Full native JSValue/JSObject marshalling remains open. |
| `DataPakSource` | vtable at `0x00548070` | Serves browser assets from `web.pak` under `asset://ql/`. | Reconstructed in Awesomium session setup and `cl_webpak.c`. |
| `SteamDataSource` | vtable at `0x00532b80` | Serves Steam-backed resources, especially avatar-like data. | Offline-safe source-side bridge in `cl_steam_resources.c`; live Awesomium source attachment remains intentionally bounded by `QL_BUILD_ONLINE_SERVICES`. |

## Current parity assessment for the browser host

Implemented or source-reconstructed:

- WebCore initialization and shutdown behind `QL_BUILD_ONLINE_SERVICES`.
- WebSession creation rooted in `fs_homepath`, including the post-create slot `0x18` initialization call.
- WebSession cache-clear ownership is reconstructed through the confirmed `_Awe_WebSession_ClearCache@4` export; reload clears the session cache and then uses SDK reload ignore-cache.
- `web.pak` mounting and deterministic package-path behavior for `asset://ql/index.html`.
- WebView creation, resize, URL load, render resume, focus, surface copy, dirty tracking, visible-surface gating, and dynamic texture upload.
- External SDK C API imports for the core WebView calls needed by the menu path.
- SDK-owned `WebKeyboardEvent` construction and WebView slot-`0xe0` keyboard event injection for modeled browser activation events.
- Startup JS bridge for the 34-entry `qz_instance` method-name surface, deterministic `FakeClient.qz_instance` compatibility, and bounded helper-readiness retries.
- `ExecuteJavascript` wrapper/fallback reconstructed at the retail WebView ABI seam.
- Retail-shaped resource request mapping for `asset://ql/screenshot/...` and `fs_webpath` overrides.
- Offline-safe Steam resource/avatar compatibility functions.

Mapped but not yet fully reconstructed:

- Native `QLJSHandler` with Awesomium `JSValue`, `JSArray`, and `JSObject` marshalling.
- Native `QLResourceInterceptor` object installation on the live WebCore instance.
- Native `SteamDataSource` installation into the live WebSession.
- Native dialog, view, and load handler objects.
- Exact names and semantics for the observed WebPreferences bytes.
- Native hidden-view lifecycle state around the retail guard that suppresses pause/unfocus during some shutdown paths.

Confidence notes:

- High confidence: bootstrap ordering, `asset://ql/index.html`, `QL` and `steam` source names, `web_browserActive`, WebView load/resume/focus slots, resource interceptor screenshot/fs_webpath mapping.
- Medium confidence: `ExecuteJavascript` slot `0x124` and raw wide-string wrapper shape, because it is aligned with the import surface and adjacent WebView ABI pattern but still needs a retail call-site-specific cross-check before using it for more complex script injection.
- Medium confidence: slot `0xa0` as `set_transparent`, because retail passes a boolean-like `1` immediately after listener installation and before page presentation, matching the old Awesomium WebView API shape.
- High confidence: slot `0xc4` as `SetZoom`, because retail passes `web_zoom->integer` to this slot both during page open and when the cvar modified latch is set.
- High confidence: slots `0xa8` and `0xb4` as pause/unfocus, because they are paired in the hide-browser path and mirror the complementary bootstrap calls to resume/focus.

## Recommended next reconstruction cuts

1. Reconstruct the native `QLJSHandler` object and Awesomium `JSValue` / `JSArray` / `JSObject` marshalling after the source-visible method-name surface is stable.
2. Add a source-side native resource interceptor object only if live Awesomium still needs it after the `web.pak` and startup script path are stable.
3. Cross-check WebPreferences field writes against Awesomium SDK headers or a focused retail object-layout pass before naming the fields.
4. Keep Steam-backed data source behavior offline-first unless a documented open replacement path is chosen.

## 2026-05-28 WebSession lifecycle and cache correction

Retail evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:15728` shows `sub_4f2a10` loading `data_12d3044` and tail-calling WebSession slot `0x1c`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:15739` shows `sub_4f2a30` calling WebSession slot `0x1c` before WebView slot `0x78` with `1`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:15747` shows shutdown destroying the WebView and then calling `Awesomium::WebCore::Shutdown`; it does not call the WebSession `0x1c` slot.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:15868` shows the WebSession created from `fs_homepath` and then immediately dispatched through slot `0x18`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:16532` shows `web_showError` forwarding `sub_4c7ee0(1)`, the full command tail after the command name.

Source divergence found:

- The source adapter named WebSession slot `0x1c` as a release path and called it during shutdown.
- Live `web_clearCache`/reload cleared only source-side resource caches and did not dispatch to the live Awesomium WebSession cache slot.
- The post-create WebSession slot `0x18` call was documented as an object-lifetime boundary rather than reconstructed.
- `web_showError` consumed only the first token after the command name.
- Live navigation ignored an `CL_Awesomium_OpenURL` failure return, so the host could remain marked active after a failed URL dispatch.

Fix implemented:

- Added optional `_Awe_WebSession_Initialize@4` binding for WebSession slot `0x18`.
- Removed the incorrect `_Awe_WebSession_Release@4` cache-clear classification. That SDK export is now used only as session release during shutdown.
- Confirmed `_Awe_WebSession_ClearCache@4` in both the staged rebuilt runtime and the retail Steam Awesomium runtime, then wired `CL_Awesomium_ClearCache` to call it when a live WebSession exists.
- Routed `CL_Web_ClearSessionState` through `CL_Awesomium_ClearCache` before source-side resource cache clearing when live Awesomium is active.
- Switched `web_showError` to `Cmd_ArgsFrom( 1 )` and made live navigation failure publish the load-failure path.

## 2026-05-28 WebUI launch/cache/image correction

Retail evidence:

- `references/analysis/quakelive_symbol_aliases.json` maps `sub_4F2A10` to `CL_Web_ClearCache_f`, `sub_4F2A30` to `CL_Web_Reload_f`, `sub_4F2590` to `QLWebCore_Update`, `sub_445910` to `R_CreateImage`, `sub_458A40` to `R_GetShaderByHandle`, and `sub_4586D0` to `RE_RegisterShaderFromImage`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:15587` shows the browser bitmap upload calling `R_CreateImage("browser", ...)`, retrieving the retained shader handle, and writing the new image pointer into the shader stage.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt` shows the retained browser shader registration using the literal `browserShader`.
- `dumpbin /exports` on both `build/win32/Debug/bin/awesomium.dll` and the Steam Quake Live `awesomium.dll` shows `_Awe_WebSession_ClearCache@4`, `_Awe_WebSession_Release@4`, and `_Awe_WebView_Reload@8`.

Source reconstruction:

- `ui_browserAwesomium 0` launch profiles stay authoritative through the source-side runtime request gate, so a map launch such as `campgrounds` does not bring up the WebUI runtime unless explicitly requested.
- The browser upload path now separates the retained shader handle name from the backing renderer image name. Retail uses `browserShader` plus `browser`; source uses the retail shader handle `browserShader` and the private image `*ql_web_browser` to avoid collisions with unrelated renderer image cache entries.
- `CL_RegisterShaderFromRGBAWithImageName` mirrors the retail distinction without changing existing Steam/avatar resource callers, which still use the one-name `CL_RegisterShaderFromRGBA` wrapper.
- `CL_Awesomium_ClearCache` now dispatches to `_Awe_WebSession_ClearCache@4` when a live session and export are present; `_Awe_WebSession_Release@4` is kept solely in shutdown.

## 2026-05-28 WebUI hash-navigation and overlay ownership correction

Retail/runtime evidence:

- Retail WebUI menu changes use the existing document and change only the hash;
  they do not reload `asset://ql/index.html` for every menu transition.
- A live runtime pass reproduced the source failure: navigating to Settings and
  pressing Escape hid the retained browser host, leaving only the dark
  background/copyright shell. Retail comparison shows browser-owned Escape is
  consumed as a no-op.

Source reconstruction:

- `web_changeHash` on a live Awesomium view now executes JavaScript to assign
  `window.location.hash` and rerun the bridge hook, instead of reloading the
  current URL.
- The startup script's `SendGameCommand` shim recognizes `web_changeHash`, but
  no longer installs a JavaScript Escape handler.
- `CL_KeyEvent` now returns immediately for Escape while `KEYCATCH_BROWSER` is
  set, matching the observed retail no-op.
- Overlay drawing, `KEYCATCH_BROWSER`, and `web_browserActive` publication are
  now tied to a contentful browser surface, so shell-only paints do not take over
  the native menu or game view.

## 2026-05-25 update/pump parity audit

Retail evidence:

- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c:27537` shows `Com_Frame` running the second event loop, executing pending commands, then calling `FUN_004f2590` before Steam callbacks and the client frame.
- `references/analysis/quakelive_symbol_aliases.json` maps `sub_4F2590` to `QLWebCore_Update`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:15501` shows `sub_4f2590` calling WebCore slot `0x18` and maintaining the browser keycatcher bit while `data_15ee390` is active.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:15804` shows the draw/update helper rebuilding the browser surface when dimensions change, updating the GL texture when the `BitmapSurface` dirty flag is set, then clearing the dirty flag.
- Retail command registration at `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:16540` includes `web_showBrowser`, `web_changeHash`, `web_hideBrowser`, `web_showError`, `web_clearCache`, and `web_reload`; it does not show a retail `web_stopRefresh` browser command.

Source divergence found:

- The source UI bridge forwards the legacy `uiScript stopRefresh` action from `src/ui/main.menu` through `web_stopRefresh` when a browser overlay is available.
- `src/ui/main.menu` runs `uiScript stopRefresh` in the main menu `onOpen` block, so the command can fire immediately after the Awesomium menu is requested.
- The previous source-side `web_stopRefresh` handler called `CL_Awesomium_Stop()` for a live Awesomium view and set `refreshStopped`.
- The previous `QLWebCore_Update` treated `refreshStopped` as a hard gate and stopped calling `CL_Awesomium_Update()`, freezing the WebCore paint/update loop.

Fix implemented:

- `QLWebCore_Update` now continues pumping WebCore once the core is initialized, matching the retail frame-pump contract.
- `CL_Web_StopRefresh_f` now treats `web_stopRefresh` as a non-destructive legacy UI/server-list stop signal for live Awesomium. It does not call `WebView::Stop`, does not latch `refreshStopped`, and marks the surface dirty so the next frame can upload the live paint.

Expected effect:

- The main menu's inherited `stopRefresh` action no longer aborts the initial `asset://ql/index.html` load.
- Awesomium can continue running JavaScript, receiving paints, and producing dirty `BitmapSurface` updates across frames instead of showing a black or stale canvas until shutdown timing changes.

## 2026-05-27 browser keycatcher activation correction

Retail evidence:

- `references/analysis/quakelive_symbol_aliases.json` maps `sub_4F2590` to `QLWebCore_Update`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:15501` shows `sub_4f2590` checking the active browser byte and setting keycatcher bit `0x20` before dispatching WebCore slot `0x18`.
- The same HLIL block does not gate the keycatcher write on the drawable browser surface or paint-presentation state.

Source divergence found:

- The reconstructed `QLWebCore_Update` armed `KEYCATCH_BROWSER` only when `browserActive` and `surfacePresented` were both true.
- The frame loop also republished `web_browserActive` from the same surface-presented condition even after the browser was opened.
- If live Awesomium was active but the first valid paint had not reached `CL_WebHost_DrawBrowserSurface`, keyboard capture could remain disabled even though retail would already route input to the WebUI.

Fix implemented:

- `QLWebCore_Update` now arms `KEYCATCH_BROWSER` from browser-active state alone, matching the retail `sub_4f2590` condition.
- The frame loop now republishes `web_browserActive` from browser-active state alone, but the publisher first checks the existing cvar value so repeated compatibility refreshes do not re-enter `Cvar_Set2`.
- Fullscreen browser drawing still remains protected by the existing visible-surface checks, so blank-surface presentation behavior is unchanged.

## 2026-05-28 no-op bridge cvar publish guard

Retail evidence:

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv` identifies `FUN_004cce90` as the 959-byte cvar setter body and `references/analysis/quakelive_symbol_aliases.json` promotes it to `Cvar_Set2`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt:33429` shows the retail `Cvar_Set2: %s (%s)\n` debug print before cvar lookup and same-value filtering.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:15483` and `:15927` show retail `web_browserActive` publication on hide/open transitions, not as a generic advert-bridge telemetry stream.

Source divergence found:

- The retained compatibility advert/browser bridge refreshed provider, policy, parity, and active cvars from renderer/UI bridge callbacks that can run every frame.
- Because reconstructed `Cvar_Set2` correctly prints before detecting an unchanged value, default offline builds could flood the developer console with unchanged bridge cvar writes while falling back to the main menu.

Fix implemented:

- Added `CL_SetCvarIfChanged()` for bridge telemetry publishers that mirror long-lived compatibility state.
- Routed repeated browser/advert bridge telemetry and frame-loop `web_browserActive` mirrors through that helper while keeping the retail event-style open/hide cvar writes intact.
- Added an Awesomium launch guard that refuses `-EnableAwesomium` launches when the latest build stamp says `QLBuildOnlineServices=0`, preventing accidental testing of the default offline build.

## 2026-05-28 web_* cvar cached-owner reconstruction

Retail evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt:32923` registers `web_browserActive` into `data_145ca50` with default `0` and flags `0x40`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:16547` registers `web_zoom` into `data_12d3060` with default `100` and flags `1`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:16550` registers `web_console` into `data_12d3064` with default `0` and flags `1`.
- The live WebView path checks the `web_zoom` modified byte before calling WebView slot `0xc4`, then clears that modified latch.

Source reconstruction:

- `common.c` now keeps `com_webBrowserActive` as the cached core cvar pointer and uses it in the frame idle-sleep decision.
- `cl_cgame.c` now keeps `cl_webZoom`, `cl_webConsole`, and `cl_webBrowserActive` pointers from `QLWebHost_RegisterCommands()`.
- The browser host exposes `cl_webCvarRetailMappings[]` with the recovered retail globals/defaults/flags, and live Awesomium zoom handling now consumes the cached `web_zoom` modified latch.

## 2026-05-25 WebView bootstrap slot reconstruction

Retail evidence:

- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c:45644` shows the bootstrap calling WebView slot `0xa0` with `1` after installing dialog/view/load handlers.
- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c:45665` shows the bootstrap calling WebView slot `0xc4` with `web_zoom->integer`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:15811` shows the browser draw/update path applying the same slot `0xc4` when the `web_zoom` modified bit is set.

Source reconstruction:

- Added the SDK C API export `_Awe_WebView_SetTransparent@8` for the retail slot `0xa0` behavior.
- Kept `_Awe_WebView_SetZoom@8` optional. The retail slot remains mapped, but the source no longer reconstructs a local vtable fallback when the SDK C API export is absent.
- `CL_Awesomium_Startup` now applies transparent mode immediately after WebView creation, matching the retail bootstrap position.
- `CL_Awesomium_OpenURL` applies default zoom before resume/focus.
- `QLWebCore_Update` now watches `web_zoom` and pushes changes to live Awesomium before the WebCore update tick, matching the retail cvar-modified behavior.
- Navigation and reload paths now reapply `web_zoom` after URL/reload commands.

## 2026-05-25 WebView hide/deactivation reconstruction

Retail evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:15474` maps the browser hide path.
- In that path, retail checks that WebCore and WebView exist, then calls WebView slot `0xa8` when the shutdown guard is clear.
- Retail then calls WebView slot `0xb4`, clears the active browser flag, sets `web_browserActive` to `0`, clears the browser keycatcher bit, and restores the cursor.

Source reconstruction:

- Added `CL_AWE_WEBVIEW_PAUSE_RENDERING_SLOT` and `CL_AWE_WEBVIEW_UNFOCUS_SLOT` wrappers to the Win32 adapter.
- Added `_Awe_WebView_PauseRendering@4` and `_Awe_WebView_Unfocus@4` dynamic import seams.
- Added public `CL_Awesomium_PauseRendering` and `CL_Awesomium_Unfocus` APIs plus disabled-build stubs.
- `QLWebHost_HideBrowser` now invokes pause/unfocus for live Awesomium before clearing source-side active/visible state, matching the retail lifecycle ordering.

Remaining caveat:

- Retail suppresses the pause-rendering call when its shutdown guard byte is set. The current source path calls pause/unfocus only through normal browser hide, while full shutdown still releases the runtime separately. That preserves the important behavioral distinction without naming the retail guard until more evidence is mapped.

## 2026-05-25 WebKeyboardEvent injection reconstruction

Retail evidence:

- `references/hlil/quakelive_steam.exe/hlil_by_address/part05.txt:15659-15671` maps `sub_4f28a0` to construction of `Awesomium::WebKeyboardEvent(eventType, virtualKeyCode, nativeKeyCode)` followed by a WebView vtable call at slot `0xe0`.
- `references/hlil/quakelive_steam.exe/hlil_by_address/part05.txt:15685-15688` shows the activation event using the retail triplet `(0, 0x11, 0x1d0001)`.
- `references/hlil/quakelive_steam.exe/hlil_by_address/part06.txt:18384` names the imported constructor as `??0WebKeyboardEvent@Awesomium@@QAE@IIJ@Z`.

Source reconstruction:

- Replaced the old four-argument pseudo export with the SDK event-object path: `_Awe_new_WebKeyboardEvent_1@12`, `_Awe_WebView_InjectKeyboardEvent@8`, and `_Awe_delete_WebKeyboardEvent@4`.
- Removed the local object-storage constructor/vtable fallback so `WebKeyboardEvent` lifetime remains owned by the external SDK.
- Added `CL_Awesomium_InjectKeyboardEvent` and wired `QLWebView_InjectKeyboardEventFields` to forward the preserved `{ eventType, virtualKeyCode, nativeKeyCode }` triplet when live Awesomium is active.

Remaining caveat:

- The current source-side key path still only models the retail activation event at full field fidelity. General per-key browser input should be reconstructed from the broader key-event caller before expanding beyond the observed triplet.

## 2026-05-25 QLJSHandler and qz_instance bootstrap reconstruction

Retail evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:16009-16011` shows retail constructing a four-byte `QLJSHandler` object and installing it through WebView slot `0x12c`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt:285623-285629` maps the `QLJSHandler` vtable to `OnMethodCall`, `OnMethodCallWithReturnValue`, and destroy callbacks.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt:301553-301690` maps the `data_55c008` table, including `IsPakFilePresent`, `IsGameRunning`, `SendGameCommand`, `WriteTextFile`, cvar helpers, map/factory/demo list helpers, Steam/lobby helpers, `GetConfig`, `GetCursorPosition`, `GetAllUGC`, `GetNextKeyDown`, and `SetFavoriteServer`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt:268623-268624` anchors the browser object name `qz_instance` and the retail fallback log string for unimplemented plugin calls.

Source reconstruction:

- The native slot-`0x12c` object remains mapped rather than claimed as ABI-reconstructed; `Awesomium::JSValue` and `Awesomium::JSArray` marshalling are still a separate evidence pass.
- The startup script now deterministically creates `window.FakeClient.qz_instance` when absent, exposes `window.qz_instance`, fills missing browser-visible methods from the retail 34-entry method-name surface, and invokes `main_hook_v2` immediately instead of waiting for page code to call it.
- Default implementations are deliberately offline-safe: catalog getters return bounded placeholder data, return-value helpers return stable empty/false values, and Steam/lobby/UGC methods no-op rather than attempting live services outside the source-owned service gates.

Expected effect:

- Browser payloads that assume `FakeClient.qz_instance` exists at startup should no longer trip a JavaScript exception before first paint.
- Missing qz method names should no longer leave the menu in a black or loader-only state solely because the native Awesomium `QLJSHandler` object is still mapped rather than fully reconstructed.

## 2026-05-25 browser-helper readiness reconstruction

Retail evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt:216003-216017` shows retail installing `QLJSHandler` on WebView slot `0x12c`, then calling `QLJSHandler_BindQzInstance` in a helper loop.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt:216008-216019` bounds that readiness loop to ten iterations with a 100 ms sleep before failing with `Could not initialize browser helpers. Please try restarting the game.`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt:44555-44564` shows `QLJSHandler_BindQzInstance` probing the page for `qz_instance` object state rather than treating the native object install alone as sufficient.

Source reconstruction:

- The startup bridge now advertises `window.__qlr_browser_helpers_ready` once the source-owned `qz_instance` surface is installed.
- It dispatches a `qz_instance.ready` DOM event for page scripts that wait on an explicit readiness signal.
- It re-runs `main_hook_v2` for forty 250 ms intervals, preserving the retail idea of a bounded helper-readiness window while allowing source-side page code to create or replace `FakeClient.qz_instance` after the injected script first runs.

Remaining caveat:

- The retry loop is intentionally source-owned and JavaScript-level. It reconstructs the observable browser-helper readiness contract, not the native Awesomium `JSMethodHandler` return-value ABI.

## 2026-05-25 startup script compactness and truncation guard

Retail evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt:216003-216017` keeps the native helper install and readiness loop separate from page script parsing, so a failed helper bind is surfaced through the explicit browser-helper failure path.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt:301553-301690` bounds the browser-visible method-name table to a fixed method surface rather than a page-owned ad hoc object shape.

Source reconstruction:

- The injected `qz_instance` bridge now builds the fixed retail method-name surface from compact method groups instead of a long sequence of individual `bind(...)` calls.
- The script sets `window.__qlr_qz_instance_script_complete` only at the end of the injected payload, giving future diagnostics a stable marker for successful parse-through.
- `CL_Awesomium_BuildStartupScript` now logs a debug diagnostic if `_snprintf` truncates the injected helper script before WebConfig receives it.

Expected effect:

- Source-owned additions to the bridge are less likely to silently truncate the injected script and leave live Awesomium with a black page before the menu JavaScript can attach to `qz_instance`.
- If truncation does occur, the failure becomes visible in developer logging instead of looking like an unrelated paint/surface problem.

## 2026-05-25 live-surface renderer containment

- Dirty-state parity: the retail `BitmapSurface::IsDirty` fallback now reads the same reconstructed dirty byte used by `SetIsDirty`, rather than treating every non-empty surface as permanently dirty. This keeps the client from re-uploading the last bad browser frame every renderer frame after Awesomium has already acknowledged the paint.

Observed source failure mode:

- The live Awesomium path copied `BitmapSurface` pixels into the browser surface buffer and treated a successful copy as drawable even when all sampled RGB channels were zero.
- When the live surface was black or empty, the fallback path synthesized a full-screen diagnostic texture and `CL_WebHost_DrawBrowserSurface` still drew it while `browserActive` was set.
- Because the browser surface is drawn as a full-screen overlay, promoting an empty/black live surface could make the UI appear black, hide the console, or make the world look incorrectly bright or washed depending on draw order and the current 2D state.

Source reconstruction at the time:

- `QLWebView_WriteSurfacePixels` now returns whether a drawable surface was produced.
- Live Awesomium surfaces are drawable only after `CL_Awesomium_CopySurface` succeeds and `QLWebView_SurfaceHasVisiblePixels` finds non-zero RGB data.
- Empty or all-black live surfaces no longer fall through to the diagnostic fallback surface and no longer upload a browser shader.
- `CL_WebHost_DrawBrowserSurface` now requires `browserVisible`, `browserActive`, a valid shader, and `surfaceHasVisiblePixels` before issuing the full-screen draw.

Expected effect:

- Awesomium can continue updating in the background while black/empty paints are ignored, rather than corrupting or covering the rest of the renderer.
- If the browser page still fails to paint, the normal Quake UI, console, and world render should remain visible instead of being replaced by the browser overlay.

## 2026-05-28 runtime/update parity correction

Retail evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:15969` shows `DataPakSource::DataPakSource` receiving the literal `"web.pak"` before the source is added under `"QL"`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:15804` maps the browser draw/update helper: it recreates the browser image when dimensions change, uploads the Awesomium `BitmapSurface` only when dirty, clears the dirty bit, then draws the browser shader without an RGB-visibility gate.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt:33128` shows `QLWebCore_Update` called from the main frame loop before Steam callbacks and the client frame; surface upload/draw remains in the renderer-facing helper.

Source divergence found:

- `CL_Awesomium_CreateSession` verified `web.pak` under the selected runtime/base root, but then passed the absolute path into `DataPakSource` instead of the retail `"web.pak"` package member name. With `WebConfig::package_path` already pointing at the root, this could prevent `asset://ql/...` loads from resolving.
- The live surface path treated all-black copied surfaces as non-drawable. Retail treats a copied `BitmapSurface` as the drawable browser texture and lets page content, including dark startup frames, present normally.
- `QLWebCore_Update` still forced the live browser surface dirty every active frame. Retail dirty handling is driven by `BitmapSurface::IsDirty` plus dimension changes.

Fix implemented:

- `CL_Awesomium_CreateSession` now constructs the data source with `DataPakSource("web.pak")` after verifying the file exists in the selected root.
- A successful live `BitmapSurface` copy now produces an uploadable browser shader even when sampled RGB values are zero; the visible-pixel check is retained only as a diagnostic.
- Live Awesomium no longer forces `surfaceDirty` every active frame after `WebCore::Update`; dirty uploads now follow `BitmapSurface::IsDirty` and size rebuilds, matching the retail update cadence.

## 2026-05-28 qz_instance return-flag correction

Retail evidence:

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv:366`, `:1121`, `:1308`, and `:1549` retain the owning retail functions at `0x00431A10`, `0x004328B0`, `0x00431E50`, and `0x00431570`.
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt:3372` identifies the `QLJSHandler::vftable` at `0x00548010`, while `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c:45616` shows retail installing that handler on the WebView before the ten-try browser-helper bind loop.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt:44299` shows `QLJSHandler_LookupMethodId` walking `data_55c008` to `0x55c1a0` in 12-byte rows.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt:44571-44577` shows `QLJSHandler_BindQzInstance` passing the third table field to `Awesomium::JSObject::SetCustomMethod`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part07.txt:1559-1698` maps the 34-entry qz method table. The `SetCvar` row at `0x0055C044` and `ResetCvar` row at `0x0055C050` both have return flag `1`; the final `NoOp` row is at `0x0055C194`, after `SetFavoriteServer`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt:45282` maps `QLJSHandler_OnMethodCallWithReturnValue`, and the adjacent switch cases reconstruct return-valued cvar set/reset behavior.

Source divergence found:

- The source-visible qz method binding table did not preserve the retail data-table address for each row, making row-order regressions hard to catch.
- `SetCvar` and `ResetCvar` were treated like void/no-op browser helpers in the injected startup bridge even though retail registers them as return-valued custom methods.
- The compact startup method group placed `NoOp` before the late UGC/key/favorite rows, which did not match the retail table's final-row ordering.

Fix implemented:

- Added retail qz table bounds and per-row table addresses to `cl_webMethodBindings`.
- Marked `SetCvar` and `ResetCvar` as return-valued rows, routed them through `QLJSHandler_OnMethodCallWithReturnValue`, and made them return boolean success/failure strings to Awesomium.
- Updated the injected `qz_instance` bridge so local `SetCvar` and `ResetCvar` helpers normalize cvar names and return `true`, matching the browser-visible return contract.
- Reordered the startup no-op method group so `NoOp` remains the last retail method row after `GetAllUGC`, `GetNextKeyDown`, and `SetFavoriteServer`.

Expected effect:

- Menu JavaScript that checks the result of `qz_instance.SetCvar(...)` or `qz_instance.ResetCvar(...)` should now see the same truthy return behavior retail exposes.
- Future reconstruction work has source-visible anchors for the exact `data_55c008` table span and row addresses, reducing the chance of silently drifting from the retail qz method surface.

## 2026-05-28 SDK dependency hygiene correction

Audit finding:

- The Win32 backend had accumulated SDK-like C++ ABI fallback code: local object storage, `__thiscall` typedefs, vtable-slot dispatch helpers, decorated constructor lookups, and raw `BitmapSurface` field-offset reads.
- The helper project generated an Awesomium import library from `src/code/win32/awesomium.def`, and `awesomium_process.cpp` locally redeclared `Awesomium::ChildProcessMain`.
- `awesomium_process.rc` presented the rebuilt helper as an Awesomium Technologies binary instead of project-owned source.

Fix implemented:

- Removed the C++ ABI fallback layer. Runtime calls now stay on the external Awesomium SDK C API exports loaded from `awesomium.dll`; if an export is absent, the adapter reports the missing SDK export or treats documented optional exports as no-op/optional.
- Corrected SDK export names for live paths that matter at startup/input: `_Awe_WebView_SetTransparent@8` and the SDK-owned keyboard event-object sequence `_Awe_new_WebKeyboardEvent_1@12`, `_Awe_WebView_InjectKeyboardEvent@8`, `_Awe_delete_WebKeyboardEvent@4`.
- Deleted `src/code/win32/awesomium.def`; `awesomium_process.vcxproj` now requires an external Awesomium SDK path and links `awesomium.lib` when `QLBuildOnlineServices=1`.
- `quakelive_steam.vcxproj` now declares the external SDK/runtime dependency for online builds through `AwesomiumSdkDir` or `AWESOMIUM_SDK_DIR`, while default builds remain offline-safe.
- `awesomium_process.cpp` includes `<Awesomium/ChildProcess.h>` instead of redeclaring SDK symbols, and the helper version resource now uses project-owned metadata.

Expected effect:

- The repository no longer contains a local reconstruction of Awesomium SDK object layout or C++ ABI behavior.
- Live WebUI startup should fail with a precise missing-SDK/missing-export diagnostic instead of falling into an inaccurate local ABI imitation.
