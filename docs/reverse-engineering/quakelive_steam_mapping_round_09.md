# Quake Live Steam Host Mapping Round 09

## Scope

This round resolves the `QLJSHandler` seam behind the `qz_instance` Awesomium object and uses that dispatch evidence to clean up the post-social utility surface.

The key correction is that the earlier Round-08 read of `0043264D` as a `GetFriendList`-adjacent path was wrong. Once the method table, return-value flag, and `QLJSHandler` vtable are read together, the remaining utility methods line up cleanly:

- `GetAllUGC`
- `GetNextKeyDown`
- `SetFavoriteServer`
- `GetFriendList`
- `FileExists`
- `GetConfig`
- `GetCursorPosition`

The evidence chain stayed inside the committed retail corpus:

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- `references/hlil/quakelive/quakelive_steam.exe/`

## `QLJSHandler` Registration And Dispatch

The RTTI and vftable at `00548010` now pin the two main method dispatchers exactly:

- `sub_431E50` is vtable slot 0 for `QLJSHandler::vftable{for Awesomium::JSMethodHandler}`
- `sub_4328B0` is vtable slot 1 for the same object

The binder at `sub_431A10` provides the missing registration context: it locates `window.qz_instance`, walks `data_55C008`, calls `Awesomium::JSObject::SetCustomMethod` for each entry, and passes the third dword of each table triple as the boolean return-value flag.

That makes the dispatch split stable rather than inferred.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_431A10` (`0x00431A10`) | `QLJSHandler_BindQzInstance` | Observed | Resolves `window.qz_instance`, registers every `data_55C008` method through `SetCustomMethod(name, returnsValue)`, and publishes the bootstrap properties `version`, `steamId`, `playerName`, and `appId` onto the same object. |
| `sub_431570` (`0x00431570`) | `QLJSHandler_LookupMethodId` | Observed | Scans `data_55C008` entry names, compares each against the incoming method `WebString`, and returns the numeric method ID from the second dword of the matching table entry. |
| `sub_431E50` (`0x00431E50`) | `QLJSHandler_OnMethodCall` | Observed | `QLJSHandler` vtable slot 0. Handles the non-returning JS methods after mapping the method ID through the compact lookup table and dispatch jump table. |
| `sub_4328B0` (`0x004328B0`) | `QLJSHandler_OnMethodCallWithReturnValue` | Observed | `QLJSHandler` vtable slot 1. Builds `Awesomium::JSValue` results for the value-returning `qz_instance` methods such as `IsPakFilePresent`, `GetCvar`, `GetDemoList`, `GetFriendList`, `FileExists`, `GetConfig`, and `GetCursorPosition`. |

## Corrected Post-Social Utility Surface

### `GetAllUGC`

Round 01 had already bounded the UGC query path generically. The `qz_instance` method table now pins that same path to the public method name `GetAllUGC`.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_460DC0` (`0x00460DC0`) | `SteamWorkshop_GetAllUGC` | Observed | Reached from the non-returning `QLJSHandler` dispatcher for the `GetAllUGC` method. Creates a Steam UGC query using the current app ID plus the incoming integer filter, executes it, and binds the call-result slot at `data_e2c20c` to `sub_45FD00`. |
| `sub_45FD00` (`0x0045FD00`) | `SteamCallbacks_OnGetAllUGCQueryCompleted` | Observed | The call-result callback for `sub_460DC0`. Iterates `SteamUGCQueryCompleted_t` rows, builds a JSON array with `title`, `description`, `id`, and `image`, publishes `web.ugc.results` on success or `web.ugc.failed` on failure, then releases the UGC query handle. |

### `GetNextKeyDown`

The one-shot key-capture path is now pinned tightly enough to correct the earlier tentative read.

Observed facts:

1. The non-returning dispatcher writes `data_12d306c` from a boolean argument or defaults it to `1` when no argument is supplied.
2. `sub_4F3420` only publishes `game.key` when `arg2 == 0` and `data_12d306c == 1`, then clears the flag immediately.
3. `sub_4F1D10` and `sub_4F24D0` both special-case the same flag so browser key capture stays armed without normal browser teardown/input behavior interfering.

That makes the `0043264D` inline body the public `GetNextKeyDown` arm/disarm path, not a friend-list query.

### `SetFavoriteServer`

The remaining inline utility method at `00432681` also resolves cleanly.

Observed facts:

1. The method takes three integer arguments.
2. It reads the current app ID through `SteamUtils()->GetAppID()`.
3. One branch calls the `SteamMatchmaking` favorite-game slot with a fresh `_time64` timestamp.
4. The other branch calls the paired favorite-game slot without the timestamp.

That matches the Quake Live host surface `SetFavoriteServer`: add/remove favorite-game records through Steam matchmaking using the supplied server coordinates and a boolean mode flag.

## Value-Returning Utility Methods

The return-value dispatcher in `sub_4328B0` now gives a much cleaner picture of the browser utility surface after the lobby/social block.

| Public surface | Dispatcher evidence | Observed role |
| --- | --- | --- |
| `GetFriendList` | `0043355D` | Returns an array of Steam friend objects. Each entry includes at least `id`, `name`, `state`, `relationship`, `nickname`, `status`, `lanIp`, `playingQuake`, and a nested current-game/lobby description when present. |
| `FileExists` | `00433414` | Converts the incoming `WebString` path to UTF-8 and returns the boolean result of `sub_4CEF10(path)`. |
| `GetConfig` | `00433DDB` | Builds a structured JS object from the config iterator at `sub_4CDB20`, including top-level config entries plus aggregated `cvars` and `binds` arrays. |
| `GetCursorPosition` | `00434238` | Calls `GetCursorPos`, converts the point into client coordinates with `ScreenToClient(data_12d34b4, ...)`, and returns a JS object with `x` and `y`. |

The same dispatcher also reaffirms earlier utility surfaces:

- `IsPakFilePresent`
- `IsGameRunning`
- `GetCvar`
- `SetCvar`
- `ResetCvar`
- `GetMapList`
- `GetFactoryList`
- `GetDemoList`
- `GetClipboardText`

## Corrected Read From Round 08

The earlier Round-08 note said the `0043264D` body was probably part of `GetFriendList`. The `QLJSHandler` registration evidence now disproves that:

1. `sub_431A10` registers `GetFriendList` as a return-value method.
2. `sub_4328B0` contains the actual friend-list return path at `0043355D`.
3. The inline `data_12d306c` toggle participates in `game.key` capture, which matches `GetNextKeyDown` instead.

So Round 08’s `GetFriendList` placeholder should now be considered retired.

## New High-Confidence Aliases Added Or Corrected This Round

- `sub_431A10`
- `sub_431570`
- `sub_431E50`
- `sub_4328B0`
- `sub_45FD00` corrected to `SteamCallbacks_OnGetAllUGCQueryCompleted`
- `sub_460DC0` corrected to `SteamWorkshop_GetAllUGC`

## Open Questions

1. `SteamWorkshop_GetAllUGC` takes a single integer filter argument, but the exact retail enum meaning of that filter still needs one more SteamUGC-specific pass before I would promote a named enum or parameter contract.
2. `SetFavoriteServer` is now bounded as the add/remove favorite-game surface, but it is still inlined in the JS dispatcher rather than owned by a standalone helper function.
3. `GetFactoryList` and `GetConfig` are both strongly bounded at the shape level, but their full field-by-field parity would still benefit from a source-side reconstruction pass in the corresponding host config loaders.
