# Quake Live Steam Host Mapping Round 12

## Scope

This round closes the last two small Awesomium listener gaps that were left open after Round 11 and records three inline return-value JS contracts that were still only broadly described in the launcher audit:

- the remaining `QLResourceInterceptor` slot at `sub_434600`
- the remaining concrete `QLDialogHandler` callback at `sub_431640`
- the inline `FileExists`, `GetConfig`, and `GetCursorPosition` return paths in `QLJSHandler_OnMethodCallWithReturnValue`

The primary evidence remains the committed local corpus:

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- `references/hlil/quakelive/quakelive_steam.exe/`

I also used two auxiliary Awesomium sanity checks for interface shape only, not as primary ownership evidence:

- https://stackoverflow.com/questions/21336391/loading-local-content-in-awesomium
- https://hybrid-analysis.com/sample/4be9f9449603808bebcaded59bc562fd82425c95c3907d624ab91231316ab6d3/5bc063627ca3e1610b13cad0

## `QLResourceInterceptor` Slot 1

Round 11 already proved that `sub_434620` and `sub_434600` belong to the `QLResourceInterceptor` vtable at `00547F94`.

Observed local facts:

1. `sub_434620` is the first non-destructor slot and returns `Awesomium::ResourceResponse*` while reading URL host/path/filename data from the incoming request object.
2. `sub_434600` is the second non-destructor slot and just returns `false`.
3. The destructor at `sub_4F2A80` restores the base `Awesomium::ResourceInterceptor` vftable, so there are only two meaningful callback slots in this class before destruction.

That leaves only one stable reading for slot 1 once `sub_434620` is already pinned as `OnRequest`: the boolean navigation filter callback.

The auxiliary Awesomium examples line up with that local layout:

- `ResourceInterceptor` exposes `OnRequest(...)` returning `ResourceResponse*`
- the companion boolean callback is `OnFilterNavigation(...)`

### Promoted Alias

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_434600` (`0x00434600`) | `QLResourceInterceptor_OnFilterNavigation` | Observed plus interface-shape inference | Slot 1 in `QLResourceInterceptor::vftable{for Awesomium::ResourceInterceptor}`. Returns `false` unconditionally, which matches the host allowing all navigation to proceed rather than blocking URLs at the interceptor layer. |

## `QLDialogHandler` Concrete Callback

Round 11 also left one `QLDialogHandler` slot unnamed:

- `QLDialogHandler::vftable{for Awesomium::WebViewListener::Dialog}` at `00547FA8`
- four callback slots before destruction
- only one concrete callback in the Quake Live subclass: `sub_431640`

Observed local facts:

1. `sub_431640` is the only non-pure callback in the class.
2. Its whole body is a pass-through: `return (*(*arg1 + 0x158))()`.
3. The host does not construct any engine-side dialog payload, publish any JS event, or touch any renderer/UI state before returning.

That makes this callback look less like a custom Quake Live dialog policy hook and more like a request to let the active `WebView` run one of Awesomium's built-in dialog handlers directly.

The auxiliary Awesomium sanity checks narrow the candidate set:

- the native `WebViewListener::Dialog` symbol family exposed in `awesomium.dll` includes `OnShowCertificateErrorDialog`, `OnShowFileChooser`, `OnShowLoginDialog`, and `OnShowPageInfoDialog`
- the same binary surface also exposes `_IpcMessageHandlerClass::OnRunFileChooser` and `_IpcMessageHandlerClass::OnFileChooserResponse`
- popup/menu surfaces are separate and therefore not candidates for this listener slot

The file-chooser path is the best fit for Quake Live's concrete implementation because it is the one dialog family with a clearly exposed built-in request/response pipeline in the `WebView` itself, which matches the one-line pass-through body.

### Promoted Alias

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_431640` (`0x00431640`) | `QLDialogHandler_OnShowFileChooser` | Observed plus interface-shape inference | The only concrete callback in `QLDialogHandler::vftable{for Awesomium::WebViewListener::Dialog}`. It simply forwards to a `WebView` virtual method, which best matches the built-in file-chooser dispatch path rather than a Quake-specific dialog implementation. |

## Inline Return-Value JS Contracts

These paths are still inline in `sub_4328B0`, so there are no new standalone helpers to promote, but the method contracts are now stable enough to record.

### `FileExists`

Method ID `0x1B` in the `data_55C000` JS table is `FileExists`. The return-value dispatcher case at `00433414`:

1. requires one string argument
2. converts the incoming `WebString` to a native string
3. calls `sub_4CEF10`
4. wraps the result as a boolean `JSValue`

That makes `FileExists` a direct browser-visible file-presence probe rather than a Steam or web-session helper.

### `GetConfig`

Method ID `0x1C` is `GetConfig`. The return-value dispatcher case at `00433DDB` builds a composite `JSObject`, not a single string or scalar:

1. It iterates `sub_4CDB20(...)` and copies the returned key/value material into properties on the root object.
2. It adds a `cvars` property populated from a prebuilt array assembled earlier in the same case.
3. It adds a `binds` property populated from the key-bind table rooted at `data_1648068`.

The bind-array leg is especially clear:

- each element carries `id`
- `sub_4B6570(index)` supplies the key name
- the stored bind string becomes `value`

So `GetConfig` is effectively the launcher's browser-side configuration snapshot RPC.

### `GetCursorPosition`

Method ID `0x1D` is `GetCursorPosition`. The return-value dispatcher case at `00434238`:

1. calls `GetCursorPos`
2. converts the screen-space point into client-space with `ScreenToClient(data_12D34B4, ...)`
3. returns a JS object with properties `x` and `y`

This is a native window-coordinate query for the launcher surface, not an Awesomium DOM coordinate helper.

## New High-Confidence Aliases Added This Round

- `sub_431640 -> QLDialogHandler_OnShowFileChooser`
- `sub_434600 -> QLResourceInterceptor_OnFilterNavigation`

## Open Questions

1. The `data_12D2670` bridge still has a structurally stable vtable but several slot names remain too weak to promote without tracing the surrounding advertisement/status surfaces more completely.
2. `GetConfig` is now contract-complete at the object-shape level, but the earlier inline array builder feeding its `cvars` member still deserves a dedicated source-side pass if we want field-exact reconstruction rather than host-surface parity.
