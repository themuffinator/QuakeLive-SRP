# Awesomium Integration Parity Audit - Post Round 288 - 2026-05-24

## Executive Summary

This audit re-inventories the Awesomium integration after mapping rounds 286,
287, and 288 and compares the current source reconstruction against the retail
Quake Live evidence in the committed Binary Ninja HLIL, Ghidra, symbol-alias,
mapping, and source-test corpus.

The result is a closure classification for the current repository target:

`closed for source-owned Windows Awesomium parity, with bounded ABI and
online-service divergences`.

No new source-owned implementation gap was found in the prioritized Awesomium
parity list. The previously highest-risk rows now have explicit source owners:
the native bridge object rooted at retail `data_12d2670`, the cgame slot-116
communication notice path, the resource interceptor's `ql` host and
`/screenshot` branches, the listener/vtable callback table, the advertisement
delay gate in `CL_MouseEvent`, the activation keyboard-event field model, and
the Win32 `_Awe_*` backend substitution boundary.

The remaining differences are not invisible missing code in the checked-in
engine. They are bounded by project policy or by runtime validation scope:

- Retail used Awesomium C++ object pointers and vtables; source uses an
  explicit `_Awe_*` C-export adapter.
- Retail online browser/Steam resource behavior was live by default; the repo
  intentionally defaults `QL_BUILD_ONLINE_SERVICES` to `0`.
- The actual `awesomium.dll` engine remains an external dependency, not source
  reconstructed engine code.
- This audit was static and evidence-based; it did not launch an online-enabled
  game build or the live Awesomium runtime.
- Null and non-Windows browser hosts are explicit compatibility stubs and are
  `strict-retail-excluded`.

## Audit Scope

Covered retail-owned surfaces:

- `awesomium_process.exe` helper bootstrap.
- `quakelive_steam.exe` browser host lifecycle and retained WebCore/WebView
  pointers.
- Browser listener classes: `QLResourceInterceptor`, `QLDialogHandler`,
  `QLViewHandler`, `QLLoadHandler`, and `QLJSHandler`.
- `SteamDataSource` resource ownership and avatar callback evidence.
- JS/native `qz_instance` bridge binding and method dispatch.
- Outbound browser event publication through `EnginePublish` and
  communication-notice lanes.
- Mouse, keyboard, wheel, activation, cursor, and surface-copy paths.
- Default-off online service policy and fallback behavior.
- Null/non-Windows compatibility boundaries.

Out of scope for this audit:

- Reimplementing `awesomium.dll`.
- Proving byte-identical executable layout or C++ ABI identity.
- Running a live Steam/Awesomium online-services smoke test.
- Replacing the repository's default offline-safe service policy.

## Methodology

The audit followed the repository evidence workflow:

1. Start from the owning retail binaries and committed references.
2. Use Ghidra metadata, imports, exports, functions, and analyst-promoted
   symbols to identify ownership.
3. Cross-check names and behavior with `references/analysis/quakelive_symbol_aliases.json`.
4. Compare current source owners against mapping rounds and source tests.
5. Separate observed evidence from inferred classification.
6. Classify remaining differences as active gaps only when the checked-in source
   lacks a recoverable retail-owned behavior.

Primary evidence inspected:

| Evidence | Role in this audit |
|---|---|
| `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt` | Canonical retail control-flow and import evidence for the main client. |
| `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt` | Main-client function/import/export inventory. |
| `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt` | Vtables, RTTI, and promoted class evidence for Awesomium listener classes. |
| `references/reverse-engineering/ghidra/awesomium_process/metadata.txt` | Helper-process inventory. |
| `references/reverse-engineering/ghidra/awesomium_process/imports.txt` | Helper-process import evidence. |
| `references/analysis/quakelive_symbol_aliases.json` | Address-to-name stabilization for recovered Awesomium functions. |
| `docs/reverse-engineering/quakelive_steam_mapping_round_286.md` | Native cgame slot-116 communication notice reconstruction. |
| `docs/reverse-engineering/quakelive_steam_mapping_round_287.md` | Resource-interceptor `ql` host and `/screenshot` reconstruction. |
| `docs/reverse-engineering/quakelive_steam_mapping_round_288.md` | Listener/vtable callback table reconstruction. |
| `tools/ci/verify-awesomium-browser-host-parity.ps1` | Static verifier for browser-host anchors. |
| `tests/test_awesomium_browser_parity.py` | Focused source-structure tests for browser-host parity. |
| `tests/test_platform_services.py` | Online-service policy and resource fallback tests. |

## Retail Evidence Inventory

### Helper Process

The helper process evidence remains narrow and strong. The relevant
`awesomium_process.exe` behavior is the wrapper into
`Awesomium::ChildProcessMain(HINSTANCE)`.

| Retail anchor | Recovered name | Source owner | Classification |
|---|---|---|---|
| `FUN_00401000` | `AwesomiumProcess_RunChildProcessMain` | `src/code/win32/awesomium_process.cpp` | Closed |
| Mangled import | `?ChildProcessMain@Awesomium@@YAHPAUHINSTANCE__@@@Z` | `src/code/win32/awesomium.def` | Closed |
| GUI helper project profile | `awesomium_process.vcxproj` | `src/code/awesomium_process.vcxproj` | Closed, default-off online policy retained |

The source-owned helper surface is therefore closed. The Chromium/Awesomium
runtime behavior behind `ChildProcessMain` belongs to `awesomium.dll` and is not
engine source debt under the current target.

### Main Client Awesomium Classes

The Ghidra symbol corpus confirms class and vtable evidence for the browser host:

| Retail evidence | Meaning |
|---|---|
| `QLResourceInterceptor::vftable` at `0x00547F94` | Resource request and navigation-filter callbacks. |
| `QLDialogHandler::vftable` at `0x00547FA8` | File chooser/dialog callbacks. |
| `QLViewHandler::vftable` at `0x00547FC0` | Tooltip, cursor, console message callbacks. |
| `QLLoadHandler::vftable` at `0x00547FE8` | Load begin/fail/finish/document-ready callbacks. |
| `QLJSHandler::vftable` at `0x00548010` | JS method call and return-value callbacks. |
| `SteamDataSource::vftable` at `0x00532B80` | Steam-backed data-source/resource owner. |
| `CCallback<class_SteamDataSource, struct_AvatarImageLoaded_t, 0>` | Steam avatar callback integration. |

The alias corpus now stabilizes the important Awesomium function owners:

| Address/name | Current alias | Audit status |
|---|---|---|
| `sub_431A10` | `QLJSHandler_BindQzInstance` | Source-visible in `cl_cgame.c`. |
| `sub_431570` | `QLJSHandler_LookupMethodId` | Source-visible method binding table. |
| `sub_431640` | `QLDialogHandler_OnShowFileChooser` | Source-visible pass-through stub. |
| `sub_431670` | `QLViewHandler_OnChangeCursor` | Source-visible cursor callback. |
| `sub_4317D0` | `QLLoadHandler_OnBeginLoadingFrame` | Source-visible load state. |
| `sub_4317E0` | `QLLoadHandler_OnFinishLoadingFrame` | Source-visible load state. |
| `sub_4317F0` | `QLLoadHandler_OnDocumentReady` | Source-visible script/bootstrap path. |
| `sub_431E50` | `QLJSHandler_OnMethodCall` | Source-visible no-return method dispatch. |
| `sub_4328B0` | `QLJSHandler_OnMethodCallWithReturnValue` | Source-visible return-value dispatch. |
| `sub_434450` | `QLViewHandler_OnChangeTooltip` | Source-visible tooltip event lane. |
| `sub_434520` | `QLViewHandler_OnAddConsoleMessage` | Source-visible console event lane. |
| `sub_434600` | `QLResourceInterceptor_OnFilterNavigation` | Source-visible false-returning filter. |
| `sub_434620` | `QLResourceInterceptor_OnRequest` | Source-visible request routing owner. |
| `sub_434AE0` | `QLLoadHandler_OnFailLoadingFrame` | Source-visible failure handling. |
| `sub_463550` | `SteamDataSource_StartResponseThread` | Bounded by current fallback/SteamDataSource subset. |
| `sub_4640C0` | `SteamDataSource_OnRequest` | Bounded by current fallback/SteamDataSource subset. |
| `sub_464290` | `SteamDataSource_OnAvatarImageLoaded` | Partially represented through avatar resource bridge. |
| `sub_4B03B0` | `QLCGImport_PublishTaggedInfoString` | Source-visible cgame import slot. |
| `sub_4BF5D0` | `QLWebView_PublishTaggedInfoString` | Source-visible comm notice payload builder. |
| `sub_4EC6D0` | `QLWebView_InvokeCommNoticeThunk` | Source-visible one-argument comm notice lane. |
| `sub_4F23B0` | `QLJSHandler_Destroy` | Tracked as destructor-owned callback. |
| `sub_4F2590` | `QLWebCore_Update` | Source-visible via host and `_Awe_*` adapter. |
| `sub_4F25C0` | `QLWebView_Resize` | Source-visible via host and `_Awe_*` adapter. |
| `sub_4F25F0` | `QLWebView_RebuildSurfaceImage` | Source-visible surface path. |
| `sub_4F2750` | `QLWebView_InjectMouseMove` | Source-visible input path. |
| `sub_4F27C0` | `QLWebView_InjectMouseDown` | Source-visible input path. |
| `sub_4F2820` | `QLWebView_InjectMouseUp` | Source-visible input path. |
| `sub_4F2870` | `QLWebView_InjectMouseWheel` | Source-visible input path. |
| `sub_4F28A0` | `QLWebView_InjectKeyboardEvent` | Source-visible field model. |
| `sub_4F2900` | `QLWebView_InjectActivationKeyboardEvent` | Source-visible fixed activation event. |
| `sub_4F2950` | `QLWebView_InvokeCommNotice` | Source-visible event lane. |
| `sub_4F2A80` | `QLResourceInterceptor_Destroy` | Tracked as destructor-owned callback. |
| `sub_4F2AB0` | `QLDialogHandler_Destroy` | Tracked as destructor-owned callback. |
| `sub_4F2AE0` | `QLViewHandler_Destroy` | Tracked as destructor-owned callback. |
| `sub_4F2B10` | `QLLoadHandler_Destroy` | Tracked as destructor-owned callback. |
| `sub_4F3260` | `QLWebView_PublishEvent` | Source-visible `EnginePublish` event bridge. |
| `sub_4F3420` | `QLWebView_PublishGameKey` | Source-visible game key event. |
| `sub_4F3570` | `QLWebView_PublishGameError` | Source-visible game error event. |
| `sub_4F3600` | `QLWebView_PublishGameEnd` | Source-visible game-end event. |
| `sub_4F3630` | `QLWebView_PublishCvarChange` | Source-visible cvar event. |
| `sub_4F37C0` | `QLWebView_PublishBindChanged` | Source-visible bind event. |
| `sub_4F38F0` | `QLWebView_PublishGameStart` | Source-visible game-start event. |
| `sub_4F3B90` | `QLWebView_PublishGameDemo` | Source-visible demo event. |
| `sub_4F3C20` | `QLWebView_PublishGameScreenshot` | Source-visible screenshot event. |

## Source Reconstruction Inventory

### Browser Bridge Object

`src/code/client/cl_cgame.c` now models the opaque retail bridge object around
`data_12d2670` as a named `ql_web_bridge_t` with a fixed vtable model:

- `QL_WEB_BRIDGE_RETAIL_OBJECT_ADDRESS 0x012D2670u`
- slot offsets from `0x08` through `0x68`
- x86 compile-time offset assertions
- wrapper functions for advert state, map path, cgame/UI lifecycle, cell label
  queries, shader setup/refresh, and activation

Assessment: closed for source-visible exactness. Future wrapper renames may
improve address documentation, but the previous absence of a bridge owner is no
longer an implementation gap.

### JS Method Handler

The `qz_instance` binding table in `cl_cgame.c` carries 34 recovered method
names plus the sentinel slot under `CL_WEB_MAX_QZ_METHODS 35`. It covers file
presence, game state, cvars, map/factory/demo lists, URL and Steam overlay
commands, clipboard access, server/lobby requests, stats/friends, UGC, key
capture, and favorite-server actions.

Assessment: closed for the recovered JS/native bridge surface. Remaining work is
only naming/exactness refinement if additional retail JS callback arguments are
promoted from HLIL later.

### Listener and Vtable Wiring

Mapping round 288 added `clWebListenerCallbackMapping_t` and
`cl_webListenerCallbackMappings[]`, making the retail callback table
source-visible for:

- `QLResourceInterceptor`
- `QLDialogHandler`
- `QLViewHandler`
- `QLLoadHandler`
- `QLJSHandler`

The table records vtable addresses, slot offsets, callback addresses, callback
aliases, and classification strings for source callbacks, no-engine callbacks,
Awesomium built-in forwarding, compatibility owners, and destructor-owned rows.
`QLWebHost_CountRecoveredListenerMappings()` turns this recovered mapping into a
runtime-visible count in the host state.

Assessment: closed for the source-owned listener/vtable seam. Destructor and
no-engine rows are documented rather than fabricated as engine logic.

### Resource Interceptor and SteamDataSource

Mapping round 287 made the interceptor branch explicit:

- `QLResourceInterceptor_OnFilterNavigation()` mirrors retail `sub_434600` by
  returning `qfalse`.
- `QLResourceInterceptor_ParseURL()` extracts scheme, host, path, and filename.
- `QLResourceInterceptor_RequestRetailHost()` recognizes the retail `ql` host.
- `/screenshot` requests map to the screenshot fallback root.
- normal `ql` host paths map to the web fallback root.
- `QLResourceInterceptor_OnRequest()` tries filter, SteamDataSource,
  retail-host projection, and generic launcher fallback in that order.

The current `SteamDataSource` subset is intentionally narrower than retail live
online behavior. It handles Steam/avatar resource ownership where the repository
has a retained service owner, then logs and falls back when live Steam or live
resource ownership is unavailable.

Assessment: closed for strict source-owned replacement scope. The live async
SteamDataSource response-thread behavior remains a bounded online-services
validation target, not a default-build implementation gap.

### Cgame Slot 116 and Communication Notice Lane

Mapping round 286 resolved the prior native cgame/serverinfo drift:

- `CG_QL_IMPORT_PUBLISH_TAGGED_INFO_STRING = 116`
- `QL_CG_trap_PublishTaggedInfoString()`
- `CL_WebView_PublishTaggedInfoString()`
- `CL_WebView_InvokeCommNotice()`

The source now serializes `MSG_TYPE` and `Info_NextPair()` key/value pairs into
the browser communication-notice payload before forwarding it through the
one-argument event lane.

Assessment: closed for source-owned comm-notice parity.

### Win32 Awesomium Adapter

`src/code/client/cl_awesomium_win32.cpp` records the retail C++ ABI boundary in
`cl_aweRetailAbiEquivalence[]`:

| Retail address | Retail slot | Retail method | Source binding | Boundary |
|---|---:|---|---|---|
| `0x004F2590` | `+0x18` | `WebCore::Update` | `_Awe_WebCore_Update@4` | C-export adapter |
| `0x004F25C0` | `+0x9c` | `WebView::Resize` | `_Awe_WebView_Resize@12` | C-export adapter |
| `0x004F2750` | `+0xd0` | `WebView::InjectMouseMove` | `_Awe_WebView_InjectMouseMove@12` | C-export adapter |
| `0x004F27C0` | `+0xd4` | `WebView::InjectMouseDown` | `_Awe_WebView_InjectMouseDown@8` | C-export adapter |
| `0x004F2820` | `+0xd8` | `WebView::InjectMouseUp` | `_Awe_WebView_InjectMouseUp@8` | C-export adapter |
| `0x004F2870` | `+0xdc` | `WebView::InjectMouseWheel` | `_Awe_WebView_InjectMouseWheel@12` | C-export adapter |
| `0x004F28A0` | `+0xe0` | `WebView::InjectKeyboardEvent` | `cl_cgame.c` field model | Source keyboard model |

Assessment: closed as an explicit adapter substitution. This does not claim
literal retail C++ ABI identity.

### Input, Activation, Cursor, and Surface Pump

The recovered input path includes:

- `CL_AdvertisementBridge_IsDelayElapsed()` before `cg_ignoreMouseInput`.
- Browser key catcher route to `CL_WebView_OnMouseMove()`.
- Mouse button, wheel, and keyboard injection helpers.
- `QLWebView_InjectActivationKeyboardEvent()` with the fixed retail fields:
  event type `0`, virtual key `0x11`, native key `0x1d0001`.
- Win32 cursor override integration.
- dirty `BitmapSurface` copy and browser image upload path.

Assessment: closed for the recovered source-owned input/rendering bridge.

### Online-Service Policy and Null Host

The repository intentionally keeps Quake Live-only online services behind
`QL_BUILD_ONLINE_SERVICES`, defaulted to `0`. This includes browser/Awesomium,
advert, Steam, auth, workshop, overlay, and stats behavior where live retail
services would otherwise be expected.

The null/non-Windows lane now publishes an explicit compatibility contract:

- provider: `Null browser host`
- policy: `compatibility-stub`
- parity scope: `strict-retail-excluded`
- parity reason: no retail Windows Awesomium runtime in the null host

Assessment: closed as a documented policy divergence. Reopening this would
require a new project target, such as literal online retail behavior by default
or a real non-Windows browser implementation.

## Subsystem Parity Matrix

| Subsystem | Retail evidence strength | Current source coverage | Status |
|---|---|---|---|
| Helper process bootstrap | High | Direct wrapper into `ChildProcessMain` plus import/link evidence | Closed |
| Main WebCore/WebView host state | High | Retained host state, startup, shutdown, update, open, reload, resize, active/visible state | Closed for source-owned scope |
| DataPakSource/session setup | Medium-high | Session path, source registration state, live adapter/fallback boundary | Closed with policy boundary |
| Resource interceptor | High after round 287 | Filter, `ql` host, `/screenshot`, web-root projection, fallback order | Closed |
| SteamDataSource | Medium-high | Avatar/resource subset plus fallback and service-policy labels | Bounded live-service subset |
| Listener/vtable install | High after round 288 | Full callback mapping table with vtable addresses and slots | Closed |
| `QLDialogHandler_OnShowFileChooser` | High | Pass-through/no-engine source stub | Closed |
| `QLViewHandler` callbacks | High | Tooltip, cursor, console message callbacks | Closed |
| `QLLoadHandler` callbacks | High | begin/fail/finish/document-ready state and bootstrap | Closed |
| `QLJSHandler` callbacks | High | method lookup, no-return dispatch, return-value dispatch | Closed |
| `qz_instance` method table | High | 34 methods plus sentinel | Closed for recovered surface |
| Native bridge `data_12d2670` | High | named bridge object, vtable, slots, assertions | Closed |
| Cgame slot 116 | High after round 286 | tagged info-string publisher into comm notice lane | Closed |
| Outbound `EnginePublish` events | High | game/key/error/start/end/cvar/bind/demo/screenshot/event wrappers | Closed |
| Mouse route and advert delay | High | retail ordering reconstructed | Closed |
| Keyboard and activation | High | browser keyboard field model and fixed activation event | Closed with adapter boundary |
| Cursor override | High | Win32 cursor callback and override state | Closed |
| Surface copy/upload | High | dirty surface, NPOT/POT buffer, renderer image upload | Closed |
| Win32 Awesomium backend ABI | High evidence of retail vtables | `_Awe_*` C-export adapter table | Bounded substitution |
| Default live online behavior | High evidence of retail online services | `QL_BUILD_ONLINE_SERVICES=0` default and labels | Bounded policy divergence |
| `awesomium.dll` internals | High external dependency evidence | not reconstructed | External scope boundary |
| Null/non-Windows host | Retail Windows-only | explicit compatibility stubs | Strict-retail excluded |

## Prioritized Gap and Risk Register

There is no active source-owned implementation gap in the current prioritized
Awesomium parity list. The remaining items are risk or scope rows:

| Priority | Item | Classification | Impact | Recommended handling |
|---|---|---|---|---|
| P0 | Source-owned Windows browser host | Closed | No current blocker | Keep static verifier and tests aligned with future mapping. |
| R1 | Literal retail C++ Awesomium ABI | Bounded substitution | Matters only for a stricter ABI-faithful target | Do not reopen unless the project adopts literal C++ ABI identity. |
| R2 | Live SteamDataSource/resource behavior | Bounded online-service divergence | Default build intentionally differs from retail live services | Keep behind `QL_BUILD_ONLINE_SERVICES`; add opt-in smoke validation if needed. |
| R3 | Runtime proof for online-enabled build | Validation gap | Static proof does not prove live `awesomium.dll` startup | Optional windowed/minimal smoke test only when runtime confidence is required. |
| R4 | `awesomium.dll` internals | External dependency | Outside source-owned engine reconstruction | Keep helper parity focused on entry/import/link behavior. |
| R5 | Null/non-Windows browser host | Strict-retail excluded | No retail Windows Awesomium runtime exists in these lanes | Treat as separate portability work, not Awesomium parity debt. |

## Observed Facts vs Inferences

Observed facts:

- Ghidra symbols expose Awesomium listener and data-source vtables and RTTI.
- The alias corpus maps the core Awesomium host functions to stable names.
- Current source contains the bridge object, slot assertions, JS method table,
  listener callback table, resource-interceptor host branches, comm-notice
  publisher, and ABI equivalence table.
- Default build configuration keeps online services disabled.
- Static verifier and focused tests target these source anchors.

Inferences:

- The source-owned Windows host should be treated as closed because the retail
  behaviors with engine ownership now have explicit source owners or explicit
  policy boundaries.
- SteamDataSource's live asynchronous response behavior is not fully recreated,
  but under repository policy that is an online-services/runtime validation
  boundary rather than a default source gap.
- The `_Awe_*` adapter is acceptable for the current replacement target because
  it records the retail slot mapping while avoiding an unsupported claim of C++
  ABI identity.

Open questions:

- Whether future work wants an opt-in live `QL_BUILD_ONLINE_SERVICES=1`
  browser-host smoke test with retail assets and `awesomium.dll`.
- Whether any remaining unnamed wrapper near the `data_12d2670` family deserves
  alias promotion for documentation quality, even though it does not block the
  current source-owned parity target.
- Whether a future portability plan should implement a real non-Windows browser
  host, which would be outside retail Awesomium parity.

## What Changed Since The Prior Audit

Round 286 closed the native cgame communication-notice drift:

- introduced `CG_QL_IMPORT_PUBLISH_TAGGED_INFO_STRING = 116`
- wired `QL_CG_trap_PublishTaggedInfoString()`
- added `CL_WebView_PublishTaggedInfoString()`
- narrowed `CL_WebView_InvokeCommNotice()` to the one-argument comm-notice lane

Round 287 closed the resource-interceptor source visibility gap:

- promoted `QLResourceInterceptor_OnFilterNavigation()`
- reconstructed URL parsing for retail host/path/filename ownership
- added `ql` host recognition
- split `/screenshot` from normal web-root requests
- preserved SteamDataSource-first ordering before launcher fallback

Round 288 closed the listener/vtable wiring source visibility gap:

- added `clWebListenerCallbackMapping_t`
- added `cl_webListenerCallbackMappings[]`
- recorded listener vtables, slot offsets, callback addresses, aliases, and
  scope classifications
- added `QLDialogHandler_OnShowFileChooser()`
- recorded recovered listener mapping count during runtime listener install

## Validation Performed In This Audit

This audit performed static source/reference inspection only. It did not launch
the game. That is intentional: the request is an evidence audit, and repository
policy says to avoid launches unless runtime evidence is necessary.

Recommended static validation commands for this state:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/ci/verify-awesomium-browser-host-parity.ps1
python -m pytest tests/test_awesomium_browser_parity.py -q --tb=short
python -m pytest tests/test_platform_services.py -q --tb=short -k "launcher_resource_fallbacks or steam_resource"
```

Recommended optional runtime validation, only if future scope requires live
proof:

- build `Debug|x86` with `QL_BUILD_ONLINE_SERVICES=1`
- use retail assets and `awesomium.dll`
- force windowed mode with `+set r_fullscreen 0`
- prefer reduced rendering if visuals are not the question
- capture logs and engine screenshots per repository debugging policy

## Parity Estimates

These are engineering estimates, not binary diff percentages.

| Scope | Before this audit pass | After this audit pass | Notes |
|---|---:|---:|---|
| `awesomium_process.exe` source-owned helper surface | 100% | 100% | Owned helper code remains closed; `awesomium.dll` is external. |
| Prioritized source-owned Windows Awesomium gap list | 100% | 100% | No active source-owned gap found after rounds 286-288. |
| Source-visible browser-host wiring confidence | 98% | 98.5% | Audit confidence improves because listener/vtable/resource/comm-notice seams are now classified together. |
| Literal retail ABI and live online-service behavior | 92% | 92% | Still bounded by `_Awe_*` adapter, default-off online services, and no live smoke test. |
| Repo-wide Awesomium posture including null/non-Windows lanes | 98% | 98% | Null/non-Windows remain explicit compatibility exclusions. |

## Final Classification

For the current repository target, Awesomium integration is closed for
source-owned Windows parity. The next useful work should not be framed as
"resolve the next prioritized Awesomium source gap" unless the project changes
scope. It should instead be one of:

- optional live online-enabled smoke validation,
- optional alias/mapping refinement for documentation,
- a new literal ABI recreation target,
- or a separate non-Windows browser portability plan.
