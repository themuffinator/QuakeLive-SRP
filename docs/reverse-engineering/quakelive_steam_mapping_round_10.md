# Quake Live Steam Host Mapping Round 10

## Scope

This round closes most of the remaining `qz_instance` utility cleanup around `quakelive_steam.exe` and tightens the browser-view callback ownership that was still generic after Round 09.

The main evidence threads are:

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/exports.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- `references/hlil/quakelive/quakelive_steam.exe/`

This pass does three things:

1. Promotes the packed Steam `CGameID` validity helper used by the `GetFriendList` current-game object.
2. Names the `QLViewHandler` callback suite around tooltip, cursor, and browser console messages.
3. Documents the still-inline `GetMapList`, `GetFactoryList`, and `GetDemoList` return surfaces at the field level so the remaining JS utility contract is recorded even where no standalone helper exists.

## `GetFriendList` Current-Game Validation

Round 09 already bounded the `GetFriendList` return path, but one helper inside the friend-game branch was still anonymous.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_431510` (`0x00431510`) | `CGameID_IsValid` | Observed | Reads the packed game-type nibble from the fourth byte, rejects values above `3`, and applies the standard Steam `CGameID` validity rules by case: app IDs must be non-zero for regular apps, mod IDs must carry the high bit for game mods, shortcut IDs are just the high-bit test, and the P2P/shared case requires app ID `0` plus the high-bit flag. |

The callsite at `00433AEA` makes the ownership clear enough to promote:

1. `GetFriendList` calls `SteamFriends()->GetFriendGamePlayed(...)` into a local struct beginning at `&var_2c`.
2. The same block immediately reads `var_2c & 0xFFFFFF` as `appid`, then exposes `lobby`, `ip`, and `port`.
3. Those fields match the standard `FriendGameInfo_t` layout, whose first member is `CGameID`.

So `sub_431510` is not a friend-list-specific predicate. It is the generic packed `CGameID::IsValid` helper used while building the nested current-game description for each friend entry.

## `QLViewHandler` Callback Suite

The RTTI and vftable at `00547FC0` now make the browser-view callback object explicit:

- `QLViewHandler::RTTI Type Descriptor` at `00574610`
- `QLViewHandler::RTTI Complete Object Locator` at `005528A8`
- `QLViewHandler::vftable{for Awesomium::WebViewListener::View}` at `00547FC0`

That vtable is installed during browser bootstrap in `sub_4F2D30`, where the host allocates a 4-byte object, writes the `QLViewHandler` vftable pointer, and passes it into the active `Awesomium::WebView`.

### Promoted `QLViewHandler` Methods

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_431670` (`0x00431670`) | `QLViewHandler_OnChangeCursor` | Observed | `QLViewHandler` vtable slot 4. Maps Awesomium cursor enums onto Win32 cursor IDs via `LoadCursorA`, stores the active cursor in `data_12D3560`, and returns the handle used by the host UI path. |
| `sub_434450` (`0x00434450`) | `QLViewHandler_OnChangeTooltip` | Observed | `QLViewHandler` vtable slot 2. Converts the incoming `WebString`, builds a payload with a single `tooltip` property, and publishes `web.tooltip` through `sub_4F3260`. |
| `sub_434520` (`0x00434520`) | `QLViewHandler_OnAddConsoleMessage` | Observed plus interface-shape inference | `QLViewHandler` vtable slot 6. Converts two incoming `WebString` values, gates on the `web_console` cvar, then logs `\"%s:%i: %s\\n\"`, which matches Awesomium's console-message callback contract of `source`, `line`, and `message`. |
| `sub_4F2AE0` (`0x004F2AE0`) | `QLViewHandler_Destroy` | Observed | `QLViewHandler` vtable slot 8. Restores the base `Awesomium::WebViewListener::View` vftable and conditionally frees the small heap object when the destructor's low-bit flag is set. |

### `QLJSHandler` Destructor

The parallel `QLJSHandler` vtable at `00548010` also now has a fully bounded slot 2:

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4F23B0` (`0x004F23B0`) | `QLJSHandler_Destroy` | Observed | Restores the base `Awesomium::JSMethodHandler` vftable and conditionally deletes the 4-byte heap object, matching the destructor slot in `QLJSHandler::vftable{for Awesomium::JSMethodHandler}`. |

## `web_hideBrowser` Ownership

Round 01 named `sub_4F24D0` as a generic browser deactivation helper. The command-registration context is now strong enough to tighten that name.

Observed facts:

1. `sub_4F3CD0` registers `web_hideBrowser` directly to `sub_4F24D0`.
2. The body only runs when the browser host exists and the one-shot key-capture flag `data_12D306C` is clear.
3. On the active path it tells the view to stop driving input, clears `web_browserActive`, restores cursor state, and leaves the browser hidden.

That makes the public role more specific than a generic lifecycle transition:

- `sub_4F24D0` now promotes to `QLWebHost_HideBrowser`

## Remaining Value-Returning Utility Surface

No new standalone helpers fell out of these cases, but the return contracts are now tight enough to record explicitly.

### `GetMapList`

The `sub_4328B0` dispatcher case at `00432C32` returns an array of map descriptors built from `data_c1e1f8` in `0x834`-byte records:

- `sysname`
- `name`
- `gametypes`

The `gametypes` field is a 13-entry boolean array populated from the byte block at record offset `0x800`, which matches Quake Live's internal per-map gametype availability table rather than a string list.

### `GetFactoryList`

The next dispatcher case at `00432EDF` returns an array of factory descriptors built from `data_a11200`, also in `0x834`-byte records. Each object contains:

- `sysname`
- `title`
- `basegt`
- optional `author`
- optional `description`
- `settings`

The `settings` child object is assembled from repeated key/value pairs starting at record offset `0x2c`. Keys are lowercased before insertion, and the loop caps at `0x100` entries, which matches the host-side factory rule expansion used by the browser.

### `GetDemoList`

The dispatcher case at `0043335B` uses `sub_4D0DB0("demos", "dm_91", ...)` and returns the resulting filenames as a JS array. This is a direct browser exposure of the demo directory scan rather than a Steam-specific surface.

2026-06-06 follow-up: the source-side `CL_WebHost_BuildDemoListJson` helper now
matches this observed return shape by preserving raw `.dm_91` file-list entries
instead of stripping the protocol suffix before building the JSON array.

## New High-Confidence Aliases Added Or Corrected This Round

- `sub_431510 -> CGameID_IsValid`
- `sub_431670 -> QLViewHandler_OnChangeCursor`
- `sub_434450 -> QLViewHandler_OnChangeTooltip`
- `sub_434520 -> QLViewHandler_OnAddConsoleMessage`
- `sub_4F23B0 -> QLJSHandler_Destroy`
- `sub_4F24D0` corrected from `QLWebHost_Deactivate` to `QLWebHost_HideBrowser`
- `sub_4F2AE0 -> QLViewHandler_Destroy`

## Open Questions

1. `sub_431640` is still only bounded as the single non-pure `QLDialogHandler` callback slot. The vtable ownership is clear, but the exact Awesomium dialog method name still needs one more pass.
2. `GetMapList` and `GetFactoryList` are now field-complete at the JS contract level, but their source-side reconstruction still needs the owning native loaders named on the engine side if we want end-to-end parity rather than host-surface parity. The `GetDemoList` raw `.dm_91` return shape was source-aligned in the 2026-06-06 demo record/playback follow-up.
