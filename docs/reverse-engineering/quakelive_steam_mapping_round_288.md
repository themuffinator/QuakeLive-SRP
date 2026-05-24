# Quake Live Steam Mapping Round 288

Date: 2026-05-24

Scope: Awesomium listener/vtable wiring source reconstruction for
`QLResourceInterceptor`, `QLDialogHandler`, `QLViewHandler`, `QLLoadHandler`,
and `QLJSHandler`.

## Evidence

Primary retail signals:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
  exposes concrete vtable blocks for the Awesomium listener objects:
  `QLResourceInterceptor` at `0x00547F94`, `QLDialogHandler` at
  `0x00547FA8`, `QLViewHandler` at `0x00547FC0`, `QLLoadHandler` at
  `0x00547FE8`, and `QLJSHandler` at `0x00548010`.
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
  contains RTTI type descriptors, complete object locators, and base-class
  descriptors for the same listener objects and their Awesomium base classes.
- The alias corpus already promotes the concrete callback bodies:
  `sub_431640` is `QLDialogHandler_OnShowFileChooser`, `sub_431670` is
  `QLViewHandler_OnChangeCursor`, `sub_434450` is
  `QLViewHandler_OnChangeTooltip`, `sub_434520` is
  `QLViewHandler_OnAddConsoleMessage`, `sub_4317D0`/`sub_4317E0`/`sub_4317F0`
  are the load begin/finish/document-ready callbacks, `sub_434AE0` is the load
  failure callback, `sub_431E50` is `QLJSHandler_OnMethodCall`, and
  `sub_4328B0` is `QLJSHandler_OnMethodCallWithReturnValue`.
- The `QLDialogHandler` vtable has one concrete engine-owned callback:
  `OnShowFileChooser` at slot offset `0x08`, address `0x00431640`. Its HLIL is
  a one-line pass-through into the active WebView virtual method at `+0x158`.
- Several adjacent listener slots point to tiny no-engine bodies
  (`0x00431660`, `0x004317B0`, `0x004317C0`) rather than custom Quake Live
  logic. The exact Awesomium base callback names for these slots are not needed
  to prove the retail source-owned behavior: they do not mutate engine state.

## Reconstructed Wiring

`src/code/client/cl_cgame.c` now records the listener wiring explicitly through
`clWebListenerCallbackMapping_t` and `cl_webListenerCallbackMappings[]`.

Each row captures:

- listener name
- retail callback role
- retail vtable address
- vtable slot offset
- retail callback address
- source callback or source owner
- whether the row is a source callback, a no-engine callback, a built-in
  Awesomium forward, a bounded compatibility owner, or a destructor-owned slot

The mapping covers:

| Listener | Vtable | Recovered concrete slots |
|---|---|---|
| `QLResourceInterceptor` | `0x00547F94` | `OnRequest`, `OnFilterNavigation`, destructor, and one no-engine slot. |
| `QLDialogHandler` | `0x00547FA8` | `OnShowFileChooser`, destructor, and three no-engine slots. |
| `QLViewHandler` | `0x00547FC0` | `OnChangeTooltip`, `OnChangeCursor`, `OnAddConsoleMessage`, destructor, and no-engine slots. |
| `QLLoadHandler` | `0x00547FE8` | begin, fail, finish, document-ready, and destructor. |
| `QLJSHandler` | `0x00548010` | method call, method call with return value, and destructor. |

`QLWebHost_InstallRuntimeListeners()` now records the recovered listener
mapping count before marking the dialog, view, and load handlers installed.
That makes the source state reflect the retail vtable mapping, not just the fact
that some listener category exists.

`QLDialogHandler_OnShowFileChooser()` is source-visible as the retail
`0x00431640` callback. The default compatibility path does not attempt to open
an engine file chooser; it only reports success when a live Awesomium view is
active. That matches the observed retail shape: Quake Live does not build a
custom dialog payload in this function and delegates to Awesomium's built-in
WebView path.

## Guardrails

Observed:

- The vtable addresses and slot offsets are direct HLIL/Ghidra evidence.
- `QLDialogHandler_OnShowFileChooser` is the only concrete
  `QLDialogHandler` callback and forwards to the WebView.
- The load, view, JS, and resource-interceptor concrete callbacks are already
  address-backed in the alias corpus and existing source tests.

Inferred:

- The label `OnShowFileChooser` follows the already promoted alias and round 12
  interface-shape conclusion. The source still treats it as a built-in forward,
  not as a custom Quake Live dialog implementation.
- No-engine listener slots are grouped by observed behavior instead of forcing
  unstable Awesomium base-method names for each pure/no-op slot.

Still bounded:

- The repository does not construct literal retail C++ listener objects in
  default builds.
- The live `_Awe_*` adapter remains a bounded C-export substitution, not a
  byte-for-byte Awesomium C++ ABI recreation.
- Destructor slots are documented as retail ownership anchors; they are not
  invoked by the default compatibility source path.

## Validation

New and updated static coverage:

- `tests/test_awesomium_browser_parity.py` checks the listener mapping table,
  `QLDialogHandler_OnShowFileChooser`, vtable addresses, slot offsets, and
  callback ownership rows.
- `tools/ci/verify-awesomium-browser-host-parity.ps1` now checks source,
  alias, and mapping anchors for the listener/vtable reconstruction.

## Parity Movement

Before this round, the listener install seam was about 88% source-visible and
97% mapped: the behavior callbacks existed, but the retail vtable wiring was
mostly collapsed into installed-state booleans.

After this round, the seam is about 96% source-visible and 98% mapped. The
remaining delta is the intentional ABI boundary: exact C++ object allocation,
listener destructor invocation, and base no-op method names remain bounded by
the default compatibility architecture.
