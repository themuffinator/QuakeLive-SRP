# Quake Live Steam Host Mapping Round 11

## Scope

This round cleans up the remaining Awesomium listener ownership around browser bootstrap in `quakelive_steam.exe`.

The stable promotions here are not Steam APIs; they are the small host-side listener objects allocated in `sub_4F2D30` during browser creation:

- `QLResourceInterceptor`
- `QLDialogHandler`
- `QLLoadHandler`

The committed evidence set is unchanged:

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- `references/hlil/quakelive/quakelive_steam.exe/`

## Listener Object Installation

The browser bootstrap at `004F2D30` now gives a clean ownership chain for the remaining tiny helper objects:

1. Allocate a 4-byte `QLDialogHandler`, write `QLDialogHandler::vftable`, and register it on the active `WebView`.
2. Allocate a 4-byte `QLViewHandler`, write `QLViewHandler::vftable`, and register it on the active `WebView`.
3. Allocate a 4-byte `QLLoadHandler`, write `QLLoadHandler::vftable`, and register it on the active `WebView`.

That makes the RTTI/vftable blocks at `00547FA8`, `00547FC0`, and `00547FE8` exact ownership anchors rather than generic Awesomium guesses.

## `QLLoadHandler` Lifecycle

The `QLLoadHandler::vftable{for Awesomium::WebViewListener::Load}` at `00547FE8` now resolves into a coherent load/error lifecycle when read together with the render path and error cvar updates.

### Promoted `QLLoadHandler` Methods

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4317D0` (`0x004317D0`) | `QLLoadHandler_OnBeginLoadingFrame` | Observed plus interface-shape inference | Sets `data_12D3068 = 1`. The browser render path at `004F2CCA` checks this flag to draw the loading spinner overlay, so this is the load-begin transition rather than a generic toggle. |
| `sub_434AE0` (`0x00434AE0`) | `QLLoadHandler_OnFailLoadingFrame` | Observed plus interface-shape inference | Clears `data_12D3068`, checks the boolean explicit argument as the main-frame gate, formats the retail string `Failed to load QUAKE LIVE site... Error %i %s`, sets `data_12D3069 = 1`, optionally hides the browser, and pushes `com_errorMessage`. |
| `sub_4317E0` (`0x004317E0`) | `QLLoadHandler_OnFinishLoadingFrame` | Observed plus interface-shape inference | Clears `data_12D3068`, matching the end of the loading-spinner state without doing the error-path work. |
| `sub_4317F0` (`0x004317F0`) | `QLLoadHandler_OnDocumentReady` | Observed plus interface-shape inference | Enumerates `js/*.js`, executes each helper script through the active `WebView`, refreshes the cached `window` object into `data_12D3078`, and publishes `web.object.ready`. |
| `sub_4F2B10` (`0x004F2B10`) | `QLLoadHandler_Destroy` | Observed | Restores the base `Awesomium::WebViewListener::Load` vftable and conditionally deletes the 4-byte heap allocation. |

### Load/Error State Coupling

Two globals close the meaning of the load callbacks:

- `data_12D3068`
  - Set by `sub_4317D0`
  - Cleared by `sub_4317E0` and `sub_434AE0`
  - Read by `004F2CCA` to draw the browser loading indicator

- `data_12D3069`
  - Set only by `sub_434AE0`
  - Checked in `004F308E` when a browser is shown again, where the view is told to leave the previous error state and the flag is cleared
  - Suppresses the normal `game.error` JS publisher path in `sub_4F3570` while a load-failure error page is already pending

That makes the failure path more specific than a generic browser error helper: it is the main-frame load failure callback for the Awesomium `Load` listener.

## Remaining Destructor Slots

Round 10 named the `QLViewHandler` and `QLJSHandler` destructors. The adjacent listener objects now complete the same pattern.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4F2A80` (`0x004F2A80`) | `QLResourceInterceptor_Destroy` | Observed | Restores the base `Awesomium::ResourceInterceptor` vftable and conditionally deletes the small heap object. |
| `sub_4F2AB0` (`0x004F2AB0`) | `QLDialogHandler_Destroy` | Observed | Restores the base `Awesomium::WebViewListener::Dialog` vftable and conditionally deletes the small heap object. |

## `QLDialogHandler` Status

The vtable ownership for `QLDialogHandler` is now exact:

- `QLDialogHandler::RTTI Type Descriptor` at `005745C0`
- `QLDialogHandler::RTTI Complete Object Locator` at `00552828`
- `QLDialogHandler::vftable{for Awesomium::WebViewListener::Dialog}` at `00547FA8`

But the one non-pure callback slot remains underconstrained:

- `sub_431640` is the only concrete listener callback in the class
- it takes one explicit argument
- it simply returns `(*(*arg1 + 0x158))()`

That is enough to prove the slot is a pass-through dialog callback, but not enough yet to promote the exact Awesomium method name without leaning too hard on interface folklore.

## `QLResourceInterceptor` Boundary Cleanup

This round also clarifies one vtable boundary that was easy to misread from the surrounding callbacks:

- `sub_434620` is still `QLResourceInterceptor_OnRequest`
- `sub_434600` is the second `QLResourceInterceptor` slot, not part of `QLDialogHandler`

`sub_434600` currently remains unnamed because the body is just a `false` return and the exact base-method contract still needs one more interface pass before promoting a specific name.

## New High-Confidence Aliases Added This Round

- `sub_4317D0 -> QLLoadHandler_OnBeginLoadingFrame`
- `sub_4317E0 -> QLLoadHandler_OnFinishLoadingFrame`
- `sub_4317F0 -> QLLoadHandler_OnDocumentReady`
- `sub_434AE0 -> QLLoadHandler_OnFailLoadingFrame`
- `sub_4F2A80 -> QLResourceInterceptor_Destroy`
- `sub_4F2AB0 -> QLDialogHandler_Destroy`
- `sub_4F2B10 -> QLLoadHandler_Destroy`

## Open Questions

1. `sub_431640` is still only bounded as the concrete `QLDialogHandler` pass-through callback and needs one more interface-specific pass before I would assign a retail-quality Awesomium method name.
2. `sub_434600` is now correctly isolated inside `QLResourceInterceptor`, but its exact interface role is still too generic to promote beyond “returns false in slot 1.”
