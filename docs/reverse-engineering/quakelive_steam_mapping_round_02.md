# Quake Live Steam Host Mapping Round 02

## Scope

This round extends [Round 01](./quakelive_steam_mapping_round_01.md) with four narrower host contracts that were still only partially mapped after the first pass:

1. the browser-side event publisher suite around `sub_4F2950` and `sub_4F3570+`
2. the opaque engine-to-host bridge rooted at `data_12d2670`
3. the Steam overlay command path for `clientviewprofile` / `clientfriendinvite`
4. the workshop finalize queue and the `idSteamStats` callback object

As in Round 01, the evidence order stayed the same:

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- `references/hlil/quakelive/quakelive_steam.exe/`

The names below are split between:

- **Observed role**: directly supported by strings, callback IDs, or explicit API use
- **Inferred role**: supported by call shape and call sites, but still not strong enough for a final semantic name

## Browser Publisher Suite

This block is separate from the generic `QLWebView_PublishEvent` helper documented in Round 01. The functions below are higher-level publishers that package specific host state transitions into the browser event contract.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4F2950` (`0x004F2950`) | `QLWebView_InvokeCommNotice` | Observed | Invokes cached `window.OnCommNotice` asynchronously with a two-element JS array payload. |
| `sub_4F3570` (`0x004F3570`) | `QLWebView_PublishGameError` | Observed | Clears `com_errorMessage`, builds `{ "text": ... }`, and publishes `game.error`. |
| `sub_4F3600` (`0x004F3600`) | `QLWebView_PublishGameEnd` | Observed | Publishes `game.end` with no payload when the browser window object is valid. |
| `sub_4F3630` (`0x004F3630`) | `QLWebView_PublishCvarChange` | Observed | Publishes `cvar.%s` with `{ "name", "value", "replicate" }`, explicitly filtering `vid_xpos` and `vid_ypos`. |
| `sub_4F37C0` (`0x004F37C0`) | `QLWebView_PublishBindChanged` | Observed | Publishes `bind.changed` with `{ "name", "value" }` after packaging the bound action name and binding text. |
| `sub_4F38F0` (`0x004F38F0`) | `QLWebView_PublishGameStart` | Observed | Publishes `game.start` with `ip` / `port`, updates Steam rich presence to `Playing a match`, and on some paths creates a lobby/server advertisement handle. |
| `sub_4F3B90` (`0x004F3B90`) | `QLWebView_PublishGameDemo` | Observed | Packages `{ "id", "name" }` and publishes `game.demo`. |
| `sub_4F3C20` (`0x004F3C20`) | `QLWebView_PublishGameScreenshot` | Observed | Packages `{ "id", "name" }` and publishes `game.screenshot`. |
| `sub_4F3CD0` (`0x004F3CD0`) | `QLWebHost_RegisterCommands` | Observed | Registers the browser console commands `web_showBrowser`, `web_changeHash`, `web_hideBrowser`, `web_showError`, `web_clearCache`, and `web_reload`, then creates `web_zoom` and `web_console`. |

Two practical takeaways from this block:

- The browser contract is broader than just `EnginePublish`. The host publishes a stable event vocabulary that any in-engine replacement should preserve.
- The host already treats browser state as operational UI state, not just launcher chrome. `game.start`, `game.end`, demo, screenshot, cvar, and bind events all route through the same publisher path.

## `data_12d2670` Engine-To-Host Bridge

The wrappers at `sub_4F1F10` through `sub_4F2280` are not the `QLJSHandler` vtable itself. They dispatch into a second object at `data_12d2670`. That object looks like an engine-facing host bridge with a stable slot layout and a mix of setters, queries, and buffer-fill APIs.

### Observed slot inventory

| Wrapper | Vtable offset | Missing-bridge fallback | Observed use | Confidence |
| --- | --- | --- | --- | --- |
| `sub_4F1F10` | `+0x0c` | no-op | Called from `VID_AppActivate` with `0` or `1`. | Medium |
| `sub_4F1F30` | `+0x2c` | returns input arg | Called once per `SCR_UpdateScreen` before the main draw pass. | Low |
| `sub_4F1F50` | `+0x10` | returns `-1` | Called during screen update with a live global timestamp/state value. | Low |
| `sub_4F1F70` | `+0x14` | returns `-1` | Called with multiple vectors, angles, near/far values, and screen dimensions; almost certainly a geometry/projection helper. | Medium |
| `sub_4F1FC0` | `+0x1c` | returns `-1` | Exposed through a trampoline but not yet tied to a stable high-level behavior. | Low |
| `sub_4F1FE0` | `+0x20` | returns `-1` | Exposed through a trampoline but not yet tied to a stable high-level behavior. | Low |
| `sub_4F2000` | `+0x24` | returns `-1` | Trampoline-only in this pass. | Low |
| `sub_4F2020` | `+0x28` | returns `-1` | Trampoline-only in this pass. | Low |
| `sub_4F2040` | `+0x3c` | clears output buffer, returns `-1` | Used in a string-list drawing loop with item index and `0x100` buffer. | Medium |
| `sub_4F2080` | `+0x38` | returns `0` | Used in the same list loop to select one of three display-state palettes. | Medium |
| `sub_4F20A0` | `+0x18` | no-op | Called once during client init with `sub_4B9DA0`, so this slot likely registers a callback/dispatcher into the bridge. | Medium |
| `sub_4F20C0` | `+0x44` | no-op | Trampoline-only in this pass. | Low |
| `sub_4F20E0` | `+0x54` | writes empty string via `sub_4589D0` | Buffer-fill API surfaced through a tailcall export. | Low |
| `sub_4F2120` | `+0x5c` | writes empty string via `sub_4589D0` | Buffer-fill API surfaced through a tailcall export. | Low |
| `sub_4F2160` | `+0x4c` | returns `0` | Returns a count for a second string-list block rendered after the primary list. | Medium |
| `sub_4F2180` | `+0x64` | clears output buffer, returns `-1` | Fills labels for that second list. | Medium |
| `sub_4F21C0` | `+0x40` | no-op | Trampoline-only in this pass. | Low |
| `sub_4F21E0` | `+0x50` | writes empty string via `sub_4589D0` | Buffer-fill API surfaced through a tailcall export. | Low |
| `sub_4F2220` | `+0x58` | writes empty string via `sub_4589D0` | Buffer-fill API surfaced through a tailcall export. | Low |
| `sub_4F2260` | `+0x48` | returns `0` | Returns a count for a third string-list block rendered after the second list. | Medium |
| `sub_4F2280` | `+0x60` | clears output buffer, returns `-1` | Fills labels for that third list. | Medium |
| `sub_4F22C0` | `+0x68` | no-op | Exposed through a trampoline export that forwards one integer to the bridge. | Low |

### Practical mapping result

The bridge is now constrained enough to reconstruct structurally even though several slot semantics are still opaque:

- it has at least `0x69` bytes of vtable surface
- it includes one callback registration slot (`+0x18`)
- it exposes at least three list/count string feeds (`+0x38` through `+0x64`)
- it includes at least one projection-or-camera helper (`+0x14`)
- it is used during app activation and frame update, so it is not browser-only

I am deliberately not adding aliases for the lower-confidence slot wrappers yet. The structure is now stable, but the semantic names are not.

## Steam Overlay Command Path

`sub_460E60` is now stable enough to name.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_460E60` (`0x00460E60`) | `SteamOverlay_Command_f` | Observed | Shared command handler for `clientviewprofile` and `clientfriendinvite`; parses the target SteamID, chooses an overlay verb, and calls `SteamFriends()->ActivateGameOverlayToUser(...)`. |

Observed details:

- `clientviewprofile` and `clientfriendinvite` are both registered during client init.
- the handler resolves a SteamID from the supplied command argument
- the strings `steamid` and `friendadd` appear in the same handler
- the imported string set also includes `ActivateGameOverlayToUser`, `ShowInviteOverlay`, and `OpenSteamOverlayURL`

This is one of the clearer examples where the host executable is not just passing through Steam APIs. It is defining an explicit console/UI contract for overlay operations.

## Workshop Queue And Finalize Flow

Round 01 mapped workshop bootstrap and download request entry points. This round closes the queue/finalize side.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_469400` (`0x00469400`) | `SteamWorkshop_AdvanceDownloadQueue` | Observed | Clears the current active download ID, pops the next queued item from `data_e40bc0`, logs the transition, and calls the UGC `DownloadItem` slot for the next queued item. |
| `sub_469470` (`0x00469470`) | `SteamWorkshop_FinalizeItem` | Observed | Fetches item metadata/state, copies the mounted item into the host workshop cache array `data_e303b0`, triggers a filesystem/content refresh when appropriate, and optionally advances the queue after automatic completion. |
| `sub_4695C0` (`0x004695C0`) | `SteamWorkshopCallbacks_OnItemInstalled` | Observed | Ignores invalid app IDs, skips already-installed items, and routes valid installs through `sub_469470`. |
| `sub_469630` (`0x00469630`) | `SteamWorkshopCallbacks_OnDownloadItemResult` | Observed | Validates app ID and active queue item, finalizes successful downloads, and logs plus advances the queue on failure. |
| `sub_4DF130` (`0x004DF130`) | `SV_AddOperatorCommands` | Observed | Registers standard server operator commands plus `steam_downloadugc`, `steam_subscribeugc`, and `steam_unsubscribeugc`. |

Observed queue state:

- `data_e40bb4` gates queue mode
- `data_e40bb8` / `data_e40bbc` retain the currently active workshop item ID
- `data_e40bc0` is the queued-download list
- `data_e303b0` is the resident workshop mount/cache array written by `sub_469470`

That makes the workshop flow easier to reason about:

1. `SteamWorkshop_RequestDownload` decides immediate vs queued request.
2. Steam callbacks land in `sub_4695C0` or `sub_469630`.
3. `SteamWorkshop_FinalizeItem` commits the installed item into the host cache and triggers mount refresh work.
4. `SteamWorkshop_AdvanceDownloadQueue` launches the next queued item if queue mode is active.

## `idSteamStats` Object

The stats/upload block adjacent to Steam server auth is now clearly its own subsystem.

### Stable callback object layout

`analysis_symbols.txt` already exposes RTTI for:

- `CCallback<class idSteamStats, struct SteamServersConnected_t, 1>`
- `CCallback<class idSteamStats, struct GSStatsReceived_t, 1>`
- `CCallback<class idSteamStats, struct GSStatsStored_t, 1>`

The constructor at `sub_467850` confirms those three callbacks belong to a single object that also owns:

- a copied stat-descriptor table from `data_561060`
- a writable shadow buffer for current stat values
- a ready flag at `+0x20`
- per-player identity fields at `+0x08` / `+0x0c`

### Stable aliases

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4670C0` (`0x004670C0`) | `SteamStats_FlushPendingValues` | Observed | Iterates the cached stat descriptors, pushes the pending values through `SteamGameServerStats`, and finalizes the batch. |
| `sub_467190` (`0x00467190`) | `SteamStats_OnServersConnected` | Observed | When stats interfaces exist and the game server is logged on, requests the current user/server stat block. |
| `sub_4671D0` (`0x004671D0`) | `SteamStats_OnStatsReceived` | Observed | Logs success/failure, reads all current values from `SteamGameServerStats`, initializes the writable index table, and marks the object ready. |
| `sub_4672D0` (`0x004672D0`) | `SteamStats_CommitField` | Observed | Commits one stat by index, then immediately flushes pending values through `sub_4670C0`. |
| `sub_467360` (`0x00467360`) | `SteamStats_OnStatsStored` | Observed | Logs store success/failure and retries the receive path when Steam reports validation failures (`result == 8`). |
| `sub_467560` (`0x00467560`) | `SteamStats_Shutdown` | Observed | Frees the stat buffer and unregisters all three callbacks. |
| `sub_467850` (`0x00467850`) | `SteamStats_Init` | Observed | Zeroes object state, registers all three callbacks, copies the stat descriptor table, allocates the writable buffers, and immediately requests stats when the Steam server interfaces are live. |

### Callback IDs and strings

Observed callback wiring:

- callback `0x65` -> `sub_467190`
- callback `0x708` -> `sub_4671D0`
- callback `0x709` -> `sub_467360`

Observed strings:

- `RequestUserStats`
- `RequestStats - failed, %d\n`
- `Received stats and achievements from Steam\n`
- `StoreStats - success\n`

The subsystem is now mapped well enough to split from server auth in future parity planning. It is a separate Steam stats replication service, not just an auth-adjacent helper.

## New High-Confidence Aliases Added This Round

- browser event publishers:
  - `sub_4F2950`
  - `sub_4F3570`
  - `sub_4F3600`
  - `sub_4F3630`
  - `sub_4F37C0`
  - `sub_4F38F0`
  - `sub_4F3B90`
  - `sub_4F3C20`
  - `sub_4F3CD0`
- Steam overlay command:
  - `sub_460E60`
- workshop finalize/queue:
  - `sub_469400`
  - `sub_469470`
  - `sub_4DF130`
- Steam stats object:
  - `sub_4670C0`
  - `sub_467190`
  - `sub_4671D0`
  - `sub_4672D0`
  - `sub_467360`
  - `sub_467560`
  - `sub_467850`

## Open Questions

1. The `data_12d2670` bridge layout is now structurally stable, but several slot semantics are still too opaque for final names.
2. `sub_4F1EE0` still looks like setup/reset logic rather than a normal bridge dispatcher and should stay unnamed until its internal state object is traced.
3. `sub_467B10` and the surrounding red-black-tree helpers likely manage lifetime for per-player `idSteamStats` objects, but I did not promote names for those management helpers yet.
