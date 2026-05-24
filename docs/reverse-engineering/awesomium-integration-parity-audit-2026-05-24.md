# Awesomium Integration Parity Audit - 2026-05-24

## Executive Summary

This audit re-checks the reconstructed Awesomium integration against the retail
Quake Live evidence currently committed in the repository. The result is
favorable but scope-sensitive: the source-owned Windows integration surface is
now effectively closed for the repository's strict-retail replacement target,
while literal byte/ABI identity and live online-service behavior remain bounded
non-goals or validation work.

The most important new conclusion is negative evidence: after re-reading the
retail HLIL/Ghidra references, mapping rounds, source implementation, and focused
tests, I did not find a remaining active source-owned Awesomium parity gap in the
current prioritized plan. The six earlier gap families are now closed or
explicitly scoped out:

| Gap family | Current state |
|---|---|
| JS/native bridge exactness around `data_12d2670` | Closed by the explicit `ql_web_bridge_t` / vtable model and slot offset assertions in `cl_cgame.c`. |
| Default online-service divergence | Closed as a policy-defined bounded divergence; `QL_BUILD_ONLINE_SERVICES` remains default-off and now publishes scope/reason labels. |
| `CL_MouseEvent` advertisement-delay gate | Closed; `CL_MouseEvent` now starts with `CL_AdvertisementBridge_IsDelayElapsed()`. |
| Activation keyboard helper exactness | Closed; source carries the fixed retail `WebKeyboardEvent(0, 0x11, 0x1d0001)` field model. |
| Win32 backend ABI substitution | Closed as an explicit compatibility adapter; source maps retail vtable slots to `_Awe_*` C exports. |
| Null/non-Windows browser lane | Closed for Awesomium strict Windows parity as `strict-retail-excluded`; real portability would be a separate target. |

Follow-up source reconstruction in mapping round 286 also closed the remaining
slot-116 naming/behavior drift from round 275: native cgame now publishes tagged
info strings into the Awesomium comm-notice lane instead of using the older
compatibility cvar-buffer shim. The main deliverable is therefore both a
refreshed parity record and a tighter source-owned browser wiring surface.

## Scope

This audit covers the Awesomium surfaces owned by the retail Windows client and
helper executable:

- `awesomium_process.exe`, the Awesomium child process bootstrap.
- `quakelive_steam.exe` browser host functions around WebCore startup,
  WebView lifecycle, listeners, JS/native bridge calls, input injection, event
  publication, surface upload, cursor handling, and advertisement bridge state.
- The repository source reconstruction in:
  - `src/code/win32/awesomium_process.cpp`
  - `src/code/win32/awesomium.def`
  - `src/code/awesomium_process.vcxproj`
  - `src/code/client/cl_awesomium_win32.cpp`
  - `src/code/client/cl_cgame.c`
  - `src/code/client/cl_input.c`
  - `src/code/client/cl_keys.c`
  - `src/code/client/cl_main.c`
  - `src/code/client/cl_steam_resources.c`
  - `src/code/client/cl_ui.c`
  - `src/code/win32/win_wndproc.c`
  - `src/code/null/null_client.c`

This audit does not attempt to reimplement `awesomium.dll`, recreate all of
Awesomium's internal C++ ABI, or turn the default build into a live Steam/browser
online-service build. Those are outside the repo's current source-owned
replacement policy unless a future plan explicitly changes scope.

## Evidence Used

Primary committed retail evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- `references/reverse-engineering/ghidra/awesomium_process/metadata.txt`
- `references/reverse-engineering/ghidra/awesomium_process/imports.txt`
- `references/analysis/quakelive_symbol_aliases.json`

Mapping and prior audit evidence:

- `docs/reverse-engineering/awesomium_process-mapping.md`
- `docs/launcher_awesomium_audit.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_01.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_02.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_10.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_11.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_12.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_29.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_94.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_96.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_257.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_285.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_286.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_287.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_288.md`
- `docs/plans/awesomium-parity-plan.md`

Source and test evidence:

- `tests/test_awesomium_browser_parity.py`
- `tests/test_platform_services.py`
- `tests/test_engine_client_command_parity.py`
- `tools/ci/verify-awesomium-process-parity.ps1`

## Retail Evidence Inventory

The Ghidra metadata shows the helper process is small and narrow:
`awesomium_process.exe` has 139 functions, 54 imports, and one meaningful
Awesomium-facing import. Its mapping note identifies the owned behavior as a
thin wrapper into `Awesomium::ChildProcessMain(HINSTANCE)`. The source mirrors
that in `AwesomiumProcess_RunChildProcessMain` and `WinMain`, while
`awesomium.def` preserves the mangled `ChildProcessMain` import.

The main executable is much broader. `quakelive_steam.exe` is tracked at 5473
functions, 351 imports, and 2 exports in the Ghidra corpus. Its Awesomium-related
symbols include RTTI and vtables for:

- `Awesomium::JSMethodHandler`
- `QLResourceInterceptor`
- `QLDialogHandler`
- `QLViewHandler`
- `QLLoadHandler`
- `QLJSHandler`
- `Awesomium::DataPakSource`
- `Awesomium::DataSource`
- `Awesomium::WebViewListener::{Dialog,View,Load}`

The HLIL imports and data globals establish the retail host shape:

| Retail evidence | Meaning |
|---|---|
| `data_12d2670` | Native browser/advertisement bridge owner used by wrapper calls. |
| `data_12d304c` | Retained `Awesomium::WebCore *`. |
| `data_12d3050` | Retained `Awesomium::WebView *`. |
| `Awesomium::WebCore::Initialize` / `Shutdown` | Browser runtime lifecycle. |
| `Awesomium::DataPakSource` and `DataSource::SendResponse` | Local launcher asset/data-source path. |
| `Awesomium::ResourceResponse::Create` | Resource interceptor response path. |
| `Awesomium::JSObject::{SetCustomMethod,InvokeAsync}` | JS/native bridge and outbound event delivery. |
| `Awesomium::WebKeyboardEvent` | Keyboard input and activation-key injection. |
| `Awesomium::BitmapSurface::CopyTo` | Surface-copy path into the renderer texture. |

The strongest retail address anchors used in this audit are:

| Address | Current alias | Evidence status |
|---|---|---|
| `0x00401000` | `AwesomiumProcess_RunChildProcessMain` | Helper process entry flow. |
| `0x00431640` | `QLDialogHandler_OnShowFileChooser` | Dialog listener pass-through. |
| `0x00431670` | `QLViewHandler_OnChangeCursor` | Cursor enum to Win32 cursor handling. |
| `0x004317F0` | `QLLoadHandler_OnDocumentReady` | JS script staging, window object refresh, `web.object.ready`. |
| `0x00434600` | `QLResourceInterceptor_OnFilterNavigation` | Resource-interceptor navigation filter returns false. |
| `0x00434620` | `QLResourceInterceptor_OnRequest` | WebURL/resource response path, including `ql` host and `/screenshot` split. |
| `0x004B54E0` | `CL_MouseEvent` | Mouse routing owner. |
| `0x004F1F10` to `0x004F2280` | Advertisement/native bridge wrappers | Calls into the object rooted at `data_12d2670`. |
| `0x004F22E0` | `AdvertisementBridge_IsDelayElapsed` | Delay gate before mouse dispatch. |
| `0x004F2310` | `AdvertisementBridge_ClearDelay` | Clears the bridge delay deadline. |
| `0x004F2590` | `QLWebCore_Update` | Per-frame WebCore update through slot `+0x18`. |
| `0x004F25C0` | `QLWebView_Resize` | WebView resize through slot `+0x9c`. |
| `0x004F25F0` | `QLWebView_RebuildSurfaceImage` | Bitmap surface to engine image. |
| `0x004F2750` | `QLWebView_InjectMouseMove` | Mouse coordinate scaling and slot `+0xd0`. |
| `0x004F27C0` | `QLWebView_InjectMouseDown` | Mouse down through slot `+0xd4`. |
| `0x004F2820` | `QLWebView_InjectMouseUp` | Mouse up through slot `+0xd8`. |
| `0x004F2870` | `QLWebView_InjectMouseWheel` | Wheel injection through slot `+0xdc`. |
| `0x004F28A0` | `QLWebView_InjectKeyboardEvent` | Keyboard event construction and slot `+0xe0`. |
| `0x004F2900` | `QLWebView_InjectActivationKeyboardEvent` | Fixed activation `WebKeyboardEvent(0, 0x11, 0x1d0001)`. |
| `0x004F2D30` | `QLWebHost_OpenURL` | WebCore/session/view bootstrap and navigation. |
| `0x004F3260` | `QLWebView_PublishEvent` | `window.EnginePublish` event bridge. |
| `0x004B03B0` / `0x004BF5D0` | `QLCGImport_PublishTaggedInfoString` / `QLWebView_PublishTaggedInfoString` | Native cgame slot `116` serializes `MSG_TYPE` plus info-string pairs into `OnCommNotice`. |

## Source Surface Inventory

### Helper Process

`src/code/win32/awesomium_process.cpp` reconstructs the retail-owned helper
surface as:

- `WinMain(...)`
- `AwesomiumProcess_RunChildProcessMain(hInstance)`
- `Awesomium::ChildProcessMain(hInstance)`

`src/code/win32/awesomium.def` preserves the mangled
`?ChildProcessMain@Awesomium@@YAHPAUHINSTANCE__@@@Z` import. The project file
defaults `QLBuildOnlineServices` to `0`, but carries the online-enabled link path
and the retail PDB alt path. `tools/ci/verify-awesomium-process-parity.ps1`
checks import, linker, and version surface expectations when a built helper is
available.

Assessment: closed for executable-owned parity. Remaining behavior belongs to
`awesomium.dll`.

### Online-Service Policy

Both `quakelive_steam.vcxproj` and `awesomium_process.vcxproj` default
`QLBuildOnlineServices` to `0`. That is intentional policy, not an accidental
Awesomium omission. The source publishes this policy through:

- `QL_GetOnlineServicesParityScopeLabel()`
- `QL_GetOnlineServicesParityReasonLabel()`
- `ui_browserAwesomium*` cvars
- `ui_advertisementBridge*` cvars
- related resource/subscription/online-service cvars

Assessment: closed as a documented divergence. Retail-default online behavior is
available only to opt-in validation builds.

### Browser Host Runtime

`cl_cgame.c` models a retained browser host state object with the expected core,
session, view, load, source, input, surface, cursor, and listener wiring flags.
It reconstructs:

- WebCore/session/view readiness.
- Runtime source registration.
- Ten-attempt bootstrap wait with 100 ms sleep.
- Dialog, view, load, and JS method handler installation flags.
- Source-visible listener/vtable mappings for `QLResourceInterceptor`,
  `QLDialogHandler`, `QLViewHandler`, `QLLoadHandler`, and `QLJSHandler`, with
  retail vtable addresses, slot offsets, callback addresses, and bounded
  no-engine/destructor rows.
- Browser active/visible state and `web_browserActive`.
- Hash navigation and open/reopen behavior.
- Load-begin, load-finish, document-ready, and load-fail state transitions.

The live Win32 backend is isolated behind `CL_AwesomiumRuntimeAllowed()`;
otherwise the source uses the compatibility overlay/fallback lane while keeping
the same host state contract visible to the engine.

Assessment: source-owned host lifecycle is reconstructed. The live Awesomium path
is intentionally opt-in and was not launched as part of this audit.

### Data Sources and Resource Interceptor

Retail evidence shows a `web.pak` data source, a Steam-backed source, and a
`QLResourceInterceptor` fallback. Mapping round 287 tightened this source lane:
`QLResourceInterceptor_OnFilterNavigation` is now source-visible as the retail
false-returning filter, and `QLResourceInterceptor_OnRequest` reconstructs the
`ql` host branch, the `/screenshot` special case, and the normal `fs_webpath`
style branch through the repository's mapped launcher/web fallback roots. The
source still keeps live service usage behind the online-services policy
boundary.

Assessment: source-owned contract is closed for strict Windows replacement
scope. Exact live network/resource behavior remains bounded by the default-off
online-services policy.

### JS/Native Bridge

The prior opaque bridge cluster around `data_12d2670` is now represented as:

- `QL_WEB_BRIDGE_RETAIL_OBJECT_ADDRESS 0x012D2670u`
- `ql_web_bridge_vtbl_t`
- `ql_web_bridge_t`
- explicit slot offsets from `0x08` through `0x68`
- compile-time vtable offset assertions on x86
- `cl_webBridgeVtbl`
- wrapper functions such as `QLWebBridge_SetActiveAdvert`,
  `QLWebBridge_SetMapPath`, `QLWebBridge_InitCGame`,
  `QLWebBridge_SetupAdvertCellShader`, and `QLWebBridge_ActivateAdvert`

The method table for the browser-visible `qz_instance` contract carries 34
method IDs, plus the sentinel slot under `CL_WEB_MAX_QZ_METHODS 35`. The current
binding list covers `IsPakFilePresent`, game state, cvar, map/factory/demo list,
Steam overlay, clipboard, server/lobby, stats/friends, UGC, key capture, and
favorite-server methods.

Assessment: closed for source-visible bridge exactness. Future mapping can still
rename or annotate additional wrappers, but the previous lack of a bridge owner
is no longer an active gap.

### Outbound Browser Events

Retail mapping rounds identify `QLWebView_PublishEvent` and the event vocabulary
used by the host. The source carries these publication paths, including:

- `web.object.ready`
- `web.tooltip`
- `game.key`
- `game.error`
- game lifecycle events
- cvar/bind/demo/screenshot publication wrappers in `cl_main.c`

The client-side wrappers check live-view and bound-window-object state before
publishing, matching the retail distinction between no view and no window object.

Assessment: closed functionally for the recovered host event contract.

### Input, Cursor, and Activation

Retail `CL_MouseEvent` begins with the advertisement-delay predicate and then
routes through browser/UI/cgame/gameplay branches. The source now matches the
critical order:

1. `CL_AdvertisementBridge_IsDelayElapsed()`
2. `cg_ignoreMouseInput`
3. `KEYCATCH_BROWSER` to `CL_WebView_OnMouseMove`
4. UI/cgame catcher dispatch
5. gameplay accumulation

`cl_keys.c` forwards browser key, mouse button, and wheel paths into the browser
host. `win_wndproc.c` forwards application activation and cursor override hooks.
The activation helper carries the exact retail field triple:

- event type `0`
- virtual key `0x11`
- native key `0x1d0001`

Assessment: closed for observed input and activation behavior. The source still
uses a C-level keyboard field model rather than constructing a live C++
`Awesomium::WebKeyboardEvent` in default builds, which is consistent with the
documented backend substitution.

### Surface Pump and Rendering

Retail mapping shows the host pulling a dirty `Awesomium::BitmapSurface`,
copying it into a buffer, creating/rebinding the `"browser"` renderer image, and
uploading subsequent dirty frames. The source reconstructs:

- browser view resize
- next-power-of-two surface sizing
- surface buffer allocation/reset
- mapped mouse coordinate scaling into browser-surface space
- dirty-surface upload through the retained browser shader/image path

Assessment: closed functionally for the recovered source-owned rendering bridge.

### Win32 Awesomium Backend Adapter

Retail calls directly through retained C++ object pointers and vtables. The
source intentionally resolves `_Awe_*` exports from `awesomium.dll` and records
the boundary in `cl_aweRetailAbiEquivalence[]`.

| Retail address | Retail slot | Retail method | Source binding |
|---|---:|---|---|
| `0x004F2590` | `+0x18` | `WebCore::Update` | `_Awe_WebCore_Update@4` |
| `0x004F25C0` | `+0x9c` | `WebView::Resize` | `_Awe_WebView_Resize@12` |
| `0x004F2750` | `+0xd0` | `WebView::InjectMouseMove` | `_Awe_WebView_InjectMouseMove@12` |
| `0x004F27C0` | `+0xd4` | `WebView::InjectMouseDown` | `_Awe_WebView_InjectMouseDown@8` |
| `0x004F2820` | `+0xd8` | `WebView::InjectMouseUp` | `_Awe_WebView_InjectMouseUp@8` |
| `0x004F2870` | `+0xdc` | `WebView::InjectMouseWheel` | `_Awe_WebView_InjectMouseWheel@12` |
| `0x004F28A0` | `+0xe0` | `WebView::InjectKeyboardEvent` | source-owned keyboard field model |

Assessment: closed as a documented C-export substitution. It is not a claim of
literal C++ ABI identity.

### Null and Non-Windows Lanes

`src/code/null/null_client.c` now publishes an explicit compatibility contract:

- provider: `Null browser host`
- policy: `compatibility-stub`
- parity scope: `strict-retail-excluded`
- parity reason: no retail Windows Awesomium runtime in the null host

Assessment: closed for the Awesomium strict-Windows target. It remains a separate
portability decision if the project later wants a real non-Windows browser host.

## Parity Matrix

| Surface | Retail evidence strength | Source parity | Current status |
|---|---|---|---|
| `awesomium_process.exe` entry flow | High | Direct semantic reconstruction | Closed |
| Helper imports/link profile | High | Import and build profile recorded; CI script available | Closed when online-enabled helper is built and verified |
| WebCore initialization/shutdown | High | Reconstructed host contract plus opt-in live backend | Closed for source-owned scope |
| Session/data sources | Medium-high | State and policy boundary reconstructed | Closed with default-off online-service divergence |
| Resource interceptor | Medium-high | Source contract retained; live resource behavior policy-gated | Closed for strict source-owned scope |
| View/listener installation | High | Dialog/view/load/listener states and callbacks reconstructed | Closed |
| JS method handler | High | Method table, dispatch, return-value paths reconstructed | Closed |
| `data_12d2670` bridge | High after closure work | Explicit bridge/vtable/slot model | Closed |
| Outbound `EnginePublish` events | High | Event helpers and state gating reconstructed | Closed |
| Mouse input route | High | Delay gate and browser catcher route reconstructed | Closed |
| Keyboard/button/wheel input | High | Browser input helpers reconstructed; keyboard uses field model | Closed with backend substitution |
| Activation key helper | High | Exact fixed constructor fields modeled | Closed |
| Cursor override | High | Win32 cursor callback surface reconstructed | Closed |
| Bitmap surface pump | High | Surface sizing, upload, dirty flags reconstructed | Closed |
| Live Awesomium C++ ABI | High evidence of retail direct vtables | Source uses `_Awe_*` C-export adapter | Closed as substitution, not ABI identity |
| Default online-services behavior | High evidence that retail used live services | Default build disables services by policy | Closed as documented divergence |
| Null/non-Windows browser host | Retail Windows-only | Explicit compatibility exclusion | Closed for Awesomium scope |

## Findings

### Finding 1: No Active Source-Owned Gap Remains In The Prioritized Awesomium Plan

The current source has explicit owners for the areas that were previously the
highest-risk open rows: the native bridge object, the advertisement-delay mouse
gate, the activation key helper, the Win32 backend substitution table, and the
null-host exclusion. The focused tests in `tests/test_awesomium_browser_parity.py`
now cover these seams directly.

Severity: none. This is a closure finding.

### Finding 2: The Strictest Possible ABI Target Is Still Not The Implemented Target

Retail `quakelive_steam.exe` directly used Awesomium C++ vtables and C++ object
types. The repository's live backend resolves a C-export adapter from
`awesomium.dll`. The new source table makes that substitution visible, which is
the right outcome under current policy.

Severity: low for the current project target, high only if the target changes to
byte/ABI-faithful Awesomium C++ recreation.

Recommended action: do not reopen as a parity bug unless the project explicitly
adopts literal Awesomium SDK ABI identity as a new target.

### Finding 3: Default Builds Correctly Diverge From Retail Online Behavior

Retail Quake Live used Awesomium, Steam, and online data/resource paths. The repo
defaults those services off under `QL_BUILD_ONLINE_SERVICES=0`. The important
parity improvement is that the divergence is now source-visible through cvars and
policy labels instead of silently failing.

Severity: none for the current policy; medium if someone evaluates default builds
as literal retail online builds.

Recommended action: keep default builds offline-safe. Use an opt-in
online-services validation lane for retail browser checks.

### Finding 4: Runtime Proof Is Still Separate From Static Parity Proof

This audit did not launch the game or the live Awesomium runtime. The static
evidence and tests are strong enough to classify source-owned parity, but they do
not replace a live `QL_BUILD_ONLINE_SERVICES=1` smoke run with retail assets and
`awesomium.dll`.

Severity: low. It affects confidence in the opt-in live path, not the source
mapping itself.

Recommended action: add a browser-host verification script or smoke test lane if
future work needs runtime proof. Keep launches windowed and minimal per
repository policy.

### Finding 5: `awesomium.dll` Remains External

`awesomium_process.exe` is closed because its owned code is just the child
process bootstrap. The actual Chromium/Awesomium behavior lives in
`awesomium.dll`, which is not reconstructed here.

Severity: none for source-owned engine parity. It is a scope boundary.

Recommended action: keep helper-process parity focused on imports, link profile,
and entry flow; do not treat `awesomium.dll` internals as engine source debt.

## Recommended Follow-Up Work

| Priority | Work | Reason |
|---|---|---|
| Optional | Add `QL_BUILD_ONLINE_SERVICES=1` browser-host smoke validation | Converts static confidence into runtime confidence for the live backend. |
| Completed 2026-05-24 | Extend `verify-awesomium-process-parity.ps1` style checks to browser host source, alias, mapping, and adapter anchors | Gives CI a direct static signal for Awesomium binding drift without launching the game. |
| Optional | Add a small alias/mapping note for any newly discovered `data_12d2670` wrapper names | Improves address-backed documentation without reopening closed source behavior. |
| Do not do by default | Recreate the retail C++ Awesomium ABI in source | High complexity, low value under current policy, and already bounded as substitution. |
| Separate plan | Implement a real non-Windows browser host | This is portability work, not retail Awesomium parity. |

## Parity Estimates

These percentages are scope estimates, not binary-diff measurements.

| Scope | Before this audit | After this audit | Notes |
|---|---:|---:|---|
| `awesomium_process.exe` source-owned helper surface | 100% | 100% | Closed; remaining behavior is external `awesomium.dll`. |
| Windows source-owned Awesomium integration, policy-aware strict scope | 100% | 100% | No active prioritized source gap found. Confidence improved by the audit. |
| Literal retail ABI and live online-service behavior | 92% | 92% | Bounded by C-export adapter, default-off online services, and no fresh runtime smoke run. |
| Repo-wide Awesomium posture including null/non-Windows lanes | 98% | 98% | Null/non-Windows is explicit compatibility scope, not retail parity. |

## Final Classification

For the current repository target, Awesomium integration should be classified as:

`closed for source-owned Windows parity, with documented online-service and ABI
substitution boundaries`.

Future work should be framed as optional validation or a new stricter scope, not
as continuation of the now-closed prioritized Awesomium parity gap list.
