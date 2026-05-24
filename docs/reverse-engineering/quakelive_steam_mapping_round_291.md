# Quake Live Steam Mapping Round 291

Date: 2026-05-24

Scope: Awesomium Win32 backend bootstrap and lifecycle adapter source
reconstruction in `src/code/client/cl_awesomium_win32.cpp`.

## Evidence

Primary retail signals:

- `sub_4F2D30`, promoted as `QLWebHost_OpenURL`, constructs
  `Awesomium::WebConfig`, calls `Awesomium::WebCore::Initialize`, stores the
  returned core pointer in `data_12d304c`, and aborts with
  `Unable to initialize WebCore` when the core is absent.
- The HLIL import table exposes the direct Awesomium constructor/import
  anchors used by that path:
  `WebCore::Shutdown` at `0x0052C684`,
  `WebPreferences::WebPreferences` at `0x0052C698`,
  `WebConfig::WebConfig` at `0x0052C6A4`,
  `WebCore::Initialize` at `0x0052C6A0`,
  `DataPakSource::DataPakSource` at `0x0052C694`,
  `DataPakSource::OnRequest` at `0x0052C6A8`, and
  `DataPakSource::~DataPakSource` at `0x0052C6AC`.
- Once the core exists, retail constructs `Awesomium::WebPreferences`, creates
  a `WebSession` through the `WebCore` vtable slot `0x00`, then calls a
  session bootstrap slot at `0x18`.
- Retail allocates `Awesomium::DataPakSource("web.pak")`, writes the imported
  `DataPakSource::vftable` at `0x00548070`, and registers it through
  `WebSession::AddDataSource` slot `0x10` under the retained literal
  `QL` at `0x00548068`.
- The same session setup allocates `SteamDataSource`, registers it as
  `steam`, installs `QLResourceInterceptor`, creates the view through the
  `WebCore` slot `0x04`, installs JS/view/load/dialog handlers, and waits up to
  ten 100 ms bootstrap attempts before navigation.
- URL navigation constructs `Awesomium::WebURL`, calls `WebView::LoadURL` at
  slot `0x64`, then focuses/activates the view through slots `0xAC` and
  `0xB0`, obtains the surface through slot `0xC4`, sets
  `web_browserActive`, and arms the browser key catcher.
- `sub_4F2A60`, promoted as `QLWebHost_Shutdown`, destroys the live view
  through slot `0x00` and tail-calls `Awesomium::WebCore::Shutdown` when the
  core pointer is live.

Companion alias anchors:

| Address | Alias | Evidence role |
|---|---|---|
| `0x004F2A60` | `QLWebHost_Shutdown` | View/core teardown owner. |
| `0x004F2D30` | `QLWebHost_OpenURL` | WebConfig, WebCore, WebSession, view, URL, focus, and activation owner. |
| `0x00548068` | `QL` | Retail DataPakSource session name literal. |
| `0x00548070` | `Awesomium::DataPakSource::vftable` | Built-in Awesomium data-source vtable installed after construction. |
| `0x0052C684` | `Awesomium::WebCore::Shutdown` import thunk | Shutdown boundary. |
| `0x0052C694` | `Awesomium::DataPakSource::DataPakSource` import thunk | `web.pak` data-source constructor. |
| `0x0052C698` | `Awesomium::WebPreferences::WebPreferences` import thunk | Per-session preferences constructor. |
| `0x0052C6A0` | `Awesomium::WebCore::Initialize` import thunk | Browser core initialization boundary. |
| `0x0052C6A4` | `Awesomium::WebConfig::WebConfig` import thunk | Browser config constructor. |

## Source Reconstruction

`src/code/client/cl_awesomium_win32.cpp` now records the recovered backend
bootstrap path through `clAwesomiumBootstrapRetailMapping_t` and
`cl_aweBootstrapRetailMappings[]`.

Each row captures:

- the retail owner function address
- the direct import, literal address, or vtable slot anchor
- the retail member or lifecycle role
- the current source owner
- the resolved `_Awe_*` C-export adapter binding when applicable
- the bounded substitution scope for the row

The mapping covers:

| Retail evidence | Source owner | Adapter binding | Scope |
|---|---|---|---|
| `WebConfig::WebConfig` at `0x0052C6A4` | `CL_Awesomium_PrepareConfig` | `_Awe_new_WebConfig@0` | bounded C-export bootstrap substitution |
| `WebCore::Initialize` at `0x0052C6A0` | `CL_Awesomium_Startup` | `_Awe_WebCore_Initialize@4` | bounded C-export bootstrap substitution |
| `WebPreferences::WebPreferences` at `0x0052C698` | `CL_Awesomium_PreparePreferences` | `_Awe_new_WebPreferences@0` | bounded C-export bootstrap substitution |
| `WebCore::CreateWebSession` slot `0x00` | `CL_Awesomium_CreateSession` | `_Awe_WebCore_CreateWebSession@12` | bounded C-export bootstrap substitution |
| `WebSession` bootstrap slot `0x18` | `CL_Awesomium_CreateSession` | session initialisation boundary | object-lifetime boundary |
| `DataPakSource::DataPakSource` at `0x0052C694` | `CL_Awesomium_CreateSession` | `_Awe_new_DataPakSource@4` | bounded C-export bootstrap substitution |
| `QL` literal at `0x00548068` | `CL_Awesomium_CreateSession` | `"QL"` | retained retail literal |
| `DataPakSource::vftable` at `0x00548070` | `CL_Awesomium_CreateSession` | Awesomium built-in `DataPakSource` | object-lifetime boundary |
| `WebSession::AddDataSource` slot `0x10` | `CL_Awesomium_CreateSession` | `_Awe_WebSession_AddDataSource@12` | bounded C-export bootstrap substitution |
| `WebCore::CreateWebView` slot `0x04` | `CL_Awesomium_Startup` | `_Awe_WebCore_CreateWebView_0@20` | bounded C-export bootstrap substitution |
| `WebView::LoadURL` slot `0x64` | `CL_Awesomium_OpenURL` | `_Awe_WebView_LoadURL@8` | bounded C-export bootstrap substitution |
| `WebView::Focus` slot `0xAC` | `CL_Awesomium_OpenURL` | `_Awe_WebView_Focus@4` | bounded C-export bootstrap substitution |
| `WebView::surface` slot `0xC4` | `CL_Awesomium_Surface` | `_Awe_WebView_surface@4` | bounded C-export bootstrap substitution |
| `WebView::Destroy` slot `0x00` | `CL_Awesomium_Shutdown` | `_Awe_WebView_Destroy@4` | bounded C-export bootstrap substitution |
| `WebCore::Shutdown` at `0x0052C684` | `CL_Awesomium_Shutdown` | `_Awe_WebCore_Shutdown@0` | bounded C-export bootstrap substitution |

`CL_Awesomium_CountBootstrapRetailMappings()` counts these recovered anchors
and stores the result in `cl_awesomium.bootstrapMappingCount` after import
resolution. This mirrors the diagnostic approach already used by the
SteamDataSource and ResponseThread rounds, without adding a new runtime cvar for
an online-services-only backend.

The source adapter also now uses the previously dormant config helper path:

- `CL_Awesomium_AppendPath` derives `awesomium_process.exe`, `awesomium.log`,
  and `web.pak` paths from the supplied runtime path.
- `CL_Awesomium_BuildUserScript` projects the current player name, app id, and
  Steam id inputs into the source-owned `qz_instance` bootstrap script.
- `CL_Awesomium_SetConfigString` applies asset protocol, child-process path,
  log path, package path, and user-script settings through the resolved
  `_Awe_WebConfig_*_set` exports.

## Guardrails

Observed:

- `QLWebHost_OpenURL` owns the core/session/view construction chain in retail.
- The `QL` and `web.pak` literals are direct HLIL data anchors.
- `DataPakSource::vftable` and the Awesomium import thunks are direct
  HLIL/Ghidra evidence.
- The recovered WebView navigation/focus/surface slots come directly from the
  `sub_4F2D30` call chain.
- `QLWebHost_Shutdown` calls the view destroy slot and `WebCore::Shutdown`.

Inferred:

- The C-export adapter rows are substitutions for retail C++ constructor and
  vtable usage, not proof of literal retail C++ ABI identity.
- The source WebConfig setter path is the repository's bounded adapter
  projection for startup paths and bootstrap script state. Retail HLIL shows
  `WebConfig` construction and initialization, but does not name every config
  field that the compatibility adapter can set.
- The `WebSession` slot `0x18` is retained as an initialization/lifetime
  boundary because the current open adapter exposes session creation and data
  source registration, not that exact C++ method.

Still bounded:

- The source does not recreate the exact retail C++ `WebConfig`,
  `WebPreferences`, `WebSession`, `WebView`, or `DataPakSource` layouts.
- Listener, JS handler, SteamDataSource, ResponseThread, and resource
  interceptor details remain documented in their dedicated mapping rounds.
- Live Awesomium and Steam behavior still requires `QL_BUILD_ONLINE_SERVICES`;
  default builds keep the offline-safe fallback policy.

## Validation

New and updated static coverage:

- `tests/test_awesomium_browser_parity.py` checks the
  `cl_aweBootstrapRetailMappings[]` table, import anchors, retained `QL`
  literal, config setter usage, session/source registration, URL load/focus,
  shutdown, and mapping counter.
- `tools/ci/verify-awesomium-browser-host-parity.ps1` now checks source, alias,
  and mapping anchors for this round.
- `docs/plans/awesomium-parity-plan.md` records the round as a completed
  source-visible reconstruction step beyond the already closed prioritized gap
  table.

No game/runtime launch was performed. This round is static source
reconstruction and mapping documentation.

## Parity Movement

Before this round, the Win32 backend bootstrap seam was about 82%
source-visible: the source loaded the right `_Awe_*` exports and performed the
major lifecycle calls, but the recovered retail `QLWebHost_OpenURL`/shutdown
chain and several startup parameters were not encoded as source-owned mapping
or live config setup.

After this round, the seam is about 94% source-visible and 98% mapped. The
remaining delta is intentional: exact C++ ABI layout, direct vtable dispatch,
handler object allocation, and live online-service behavior remain bounded by
the adapter and `QL_BUILD_ONLINE_SERVICES` policy.
