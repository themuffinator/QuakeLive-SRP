# Reverse‑Engineering Mapping for `quakelive_steam.exe`

## Overview

`quakelive_steam.exe` is a proprietary Windows executable used by the Steam release of **Quake Live**.  Unlike the GPL‑released Quake III Arena engine, the Steam host is a monolithic launcher that bundles an embedded Chromium/Awesomium UI, Steamworks integration and dynamic linking to several native game modules (e.g., `qagamex86.dll`, `cgamex86.dll`, `uix86.dll`).  The upstream GPL code base in `src/` lacks a counterpart for this binary, so reconstructing its behaviour requires reverse‑engineering.

The Quake Live reverse‑engineering repository provides high‑level intermediate language (HLIL) dumps, Ghidra analysis exports and several authored mapping rounds.  These notes synthesise those resources to create a cohesive map of the subsystems inside `quakelive_steam.exe`.  Where possible, raw functions are aliased to descriptive names and aligned with Quake III source structures for context.  Citations below refer to the mapping documents hosted in the repository.

## Reference inventory

The `references/` tree preserves the reverse‑engineering artefacts used as evidence.  The HLIL dump for the Steam host is located at `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`.  Metadata and function lists are stored in `references/reverse‑engineering/ghidra/quakelive_steam/` (including `metadata.txt`, `imports.txt`, `exports.txt`, `functions.csv` and `analysis_symbols.txt`).  The repository’s `docs/` folder contains several structured mapping notes.  The **Round 01**, **Round 02** and **Round 03** documents collectively cover a large portion of the binary and serve as the basis for this report.

## Subsystem Anchors

### Browser / Awesomium Host

The executable embeds the Awesomium browser engine to render the launcher UI.  Reverse‑engineered functions indicate a custom resource interceptor, JavaScript bridge and event publisher.  High‑confidence alias candidates include:

| Raw function | Proposed alias | Description |
|---|---|---|
| `sub_434620` (`0x00434620`) | **`QLResourceInterceptor_OnRequest`** | Implements a custom resource interceptor; examines `Awesomium::WebURL` to intercept `/screenshot*` and returns `Awesomium::ResourceResponse::Create(...)`【932230678200358†L38-L47】. |
| `sub_4F23E0` (`0x004F23E0`) | **`QLWebView_SetLocationHash`** | Updates `window.location.hash` on the embedded view【932230678200358†L40-L49】. |
| `sub_4F2D30` (`0x004F2D30`) | **`QLWebHost_OpenURL`** | Boots `Awesomium::WebCore`, creates a session rooted at `fs_homepath`, registers custom schemes (`web.pak`, `steam`, etc.), waits for readiness and navigates to the target URL【932230678200358†L48-L50】. |
| `sub_4F3260` (`0x004F3260`) | **`QLWebView_PublishEvent`** | Marshals event name and optional payload to JavaScript via `window.EnginePublish`【932230678200358†L51-L53】. |
| `sub_4F3420` (`0x004F3420`) | **`QLWebView_PublishGameKey`** | Publishes the `game.key` event with `id` and `key` fields【932230678200358†L51-L53】. |

The browser also defines higher‑level publishers for game lifecycle events, cvar/bind changes, demo/screenshot notifications and error reporting.  These functions, grouped in **Round 02**, include `QLWebView_PublishGameStart` (`sub_4F38F0`), `QLWebView_PublishGameEnd` (`sub_4F3600`), `QLWebView_PublishGameError` (`sub_4F3570`) and others【65628915320824†L27-L38】.  A registration function (`sub_4F3CD0`) exposes console commands (`web_showBrowser`, `web_changeHash`, `web_hideBrowser`, `web_showError`, `web_clearCache`, `web_reload`, etc.) to toggle the UI state【65628915320824†L37-L38】.

### Steam Client Integration

The host links to `steam_api.dll` and maintains persistent Steam client state.  Key bootstrap functions include:

| Raw function | Proposed alias | Observed role |
|---|---|---|
| `sub_461500` (`0x00461500`) | **`SteamClient_Init`** | Calls `SteamAPI_Init`, allocates callback objects, registers microtransaction and lobby subsystems, and sets initial rich presence to “At the main menu”【932230678200358†L80-L85】. |
| `sub_4613A0` (`0x004613A0`) | **`SteamCallbacks_Init`** | Allocates the main client callback bundle and registers handlers for `GameRichPresenceJoinRequested_t`, `UserStatsReceived_t`, `PersonaStateChange_t`, `P2PSessionRequest_t`, `GameServerChangeRequested_t`, `FriendRichPresenceUpdate_t` and `SteamUGCQueryCompleted_t`【932230678200358†L80-L86】. |
| `sub_460510` (`0x00460510`) | **`SteamClient_IsInitialized`** | Returns the global Steam‑API flag set by `SteamAPI_Init`【325473679468188†L41-L46】. |
| `sub_460550` (`0x00460550`) | **`SteamClient_GetSteamID`** | Returns the local user’s `CSteamID`, reused for `fs_homepath` and identity propagation【325473679468188†L41-L46】. |
| `sub_4605C0` (`0x004605C0`) | **`SteamClient_GetAuthSessionTicket`** | Calls `SteamUser()->GetAuthSessionTicket`, stores the handle and size for later use by the server auth path【325473679468188†L41-L46】. |
| `sub_4605F0` (`0x004605F0`) | **`SteamClient_CancelAuthTicket`** | Cancels the cached auth‑ticket handle during disconnect or error cleanup【325473679468188†L41-L46】. |

These functions support subsequent subsystems—lobby, matchmaking, microtransactions, game server auth and workshop—by providing the necessary callbacks and identity tokens.

### Steam Lobby & Matchmaking

The lobby subsystem enables host‑managed matchmaking and chat.  Core functions (identified in **Round 01**) are:

| Raw function | Proposed alias | Observed role |
|---|---|---|
| `sub_4656A0` (`0x004656A0`) | **`SteamLobbyCallbacks_Init`** | Registers callbacks for `LobbyCreated_t`, `LobbyEnter_t`, `LobbyChatUpdate_t`, `LobbyChatMsg_t`, `LobbyDataUpdate_t`, `LobbyGameCreated_t`, `LobbyKicked_t` and `GameLobbyJoinRequested_t`【932230678200358†L95-L105】. |
| `sub_465840` (`0x00465840`) | **`SteamLobby_Init`** | Allocates the callback bundle, registers the `lobby_autoconnect` cvar, creates the `steam_maxLobbyClients` cvar and exposes the `connect_lobby` console command【932230678200358†L95-L107】. |
| `sub_4649E0` (`0x004649E0`) | **`SteamLobby_LeaveLobby`** | Leaves the current lobby, publishes `lobby.%s.left` and clears state【932230678200358†L105-L106】. |
| `sub_464AA0` (`0x00464AA0`) | **`SteamLobby_ConnectLobby_f`** | Console command handler behind `connect_lobby`【932230678200358†L105-L106】. |
| `sub_464BF0` (`0x00464BF0`) | **`SteamLobbyCallbacks_OnLobbyCreated`** | Publishes `lobby.%s.create` on success or `lobby.error` with details on failure【932230678200358†L95-L101】. |
| `sub_464D90` (`0x00464D90`) | **`SteamLobbyCallbacks_OnLobbyEnter`** | Updates the current lobby ID, enumerates lobby metadata and players, and publishes `lobby.%s.enter` or `lobby.error`【932230678200358†L95-L101】. |
| `sub_4652E0` (`0x004652E0`) | **`SteamLobbyCallbacks_OnLobbyChatUpdate`** | Publishes `lobby.%s.user.joined`/`lobby.%s.user.left` with player details【932230678200358†L98-L102】. |
| `sub_4645A0` (`0x004645A0`) | **`SteamLobbyCallbacks_OnLobbyChatMessage`** | Relays chat messages to the browser event path `lobby.%s.chat`【932230678200358†L100-L101】. |
| `sub_465490` (`0x00465490`) | **`SteamLobbyCallbacks_OnLobbyDataUpdate`** | Broadcasts updated lobby key/value data【932230678200358†L100-L102】. |
| `sub_464720` (`0x00464720`) | **`SteamLobbyCallbacks_OnLobbyGameCreated`** | Publishes `lobby.%llu.game_created` with IP/port and server ID【932230678200358†L101-L103】. |
| `sub_464830` (`0x00464830`) | **`SteamLobbyCallbacks_OnLobbyKicked`** | Publishes `lobby.%llu.kicked` and clears lobby state【932230678200358†L103-L103】. |
| `sub_464900` (`0x00464900`) | **`SteamLobbyCallbacks_OnGameLobbyJoinRequested`** | Publishes `lobby.%llu.join_requested` to the browser【932230678200358†L103-L105】. |

The lobby event strings (e.g., `lobby.%s.create`, `lobby.%s.enter`, `lobby.%s.user.joined`, `lobby.error`) expose a stable contract that an engine replacement must honour【932230678200358†L109-L123】.

### Steam Microtransactions

Microtransaction support is minimal but clearly separated:

| Raw function | Proposed alias | Observed role |
|---|---|---|
| `sub_4659E0` (`0x004659E0`) | **`SteamMicroCallbacks_Init`** | Allocates and registers a callback for `MicroTxnAuthorizationResponse_t`【932230678200358†L131-L137】. |
| `sub_4658A0` (`0x004658A0`) | **`SteamMicroCallbacks_OnAuthorizationResponse`** | Publishes a JSON object containing `appid`, `orderid` and `authorized`, and logs `GOT MICRO RESPONSE: ...`【932230678200358†L131-L137】. |

### Steam Game Server & Authentication

The host can run as a dedicated server with Steam authentication and P2P networking.  Key functions:

| Raw function | Proposed alias | Observed role |
|---|---|---|
| `sub_466ED0` (`0x00466ED0`) | **`SteamServer_Init`** | Initializes `SteamGameServer`, sets product/mod strings, registers server callback bundle (`SteamServerCallbacks`), and logs `Steam Gameserver initialized.`【932230678200358†L142-L155】. |
| `sub_466DB0` (`0x00466DB0`) | **`SteamServerCallbacks_Init`** | Registers callbacks for server connection/disconnect events (`SteamServersConnected_t`, `SteamServerConnectFailure_t`, `SteamServersDisconnected_t`), `ValidateAuthTicketResponse_t` and server‑side `P2PSessionRequest_t`【932230678200358†L142-L151】. |
| `sub_465B70` (`0x00465B70`) | **`SteamServerCallbacks_OnP2PSessionRequest`** | Accepts P2P sessions only when the connecting Steam ID matches a live active client slot【932230678200358†L142-L149】. |
| `sub_465C10`–`sub_465C50` | **`SteamServerCallbacks_OnConnectFailure`, `SteamServerCallbacks_OnServersDisconnected`, `SteamServerCallbacks_OnValidateAuthTicketResponse`** | Handle failure/disconnect/authentication events; implement VAC timeouts, banned codes and reasons (e.g., `VAC check timed out`, `Issuer canceled auth ticket`)【932230678200358†L144-L149】. |
| `sub_465B00` (`0x00465B00`) | **`SteamServer_PublishSteamID`** | Publishes the game server’s Steam ID into configstrings `0x2ca` and `0x2cb` for client consumption【932230678200358†L148-L149】. |
| `sub_465FD0` (`0x00465FD0`) | **`SteamServer_BeginAuthSession`** | Starts Steam authentication for a connecting client; deduplicates pending sessions and stores them in an auth tree【932230678200358†L152-L154】. |
| `sub_4661E0` (`0x004661E0`) | **`SteamServer_EndAuthSession`** | Ends an auth session and removes the Steam ID from the auth tree【932230678200358†L152-L154】. |
| `sub_466260` (`0x00466260`) | **`SteamServer_UpdatePublishedState`** | Publishes dynamic server metadata (player count, password state, map/gametype details, player Steam identities, etc.)【932230678200358†L154-L155】. |
| `sub_466850` (`0x00466850`) | **`SteamServer_Frame`** | Runs `SteamGameServer_RunCallbacks`, periodically refreshes published server state, pumps P2P networking and handles pending auth work【932230678200358†L154-L155】. |

These functions enable VAC and auth ticket enforcement, P2P networking, dedicated server state publication and per‑client Steam ID advertisement.

### Steam Workshop & UGC

Quake Live integrates the Steam Workshop to manage custom maps and mods.  The host provides facilities to subscribe, download and mount UGC items and to query for them.  The finalization and queue management logic was mapped in **Rounds 01** and **02**:

| Raw function | Proposed alias | Observed role |
|---|---|---|
| `sub_4697A0` (`0x004697A0`) | **`SteamWorkshop_Init`** | Checks `pak00.pk3`, respects `fs_skipWorkshop` and `com_build` cvars, validates the UGC interface, enumerates subscribed items and mounts them【932230678200358†L167-L173】. |
| `sub_4696D0` (`0x004696D0`) | **`SteamWorkshopCallbacks_Init`** | Registers callbacks for `ItemInstalled_t` and `DownloadItemResult_t`【932230678200358†L167-L173】. |
| `sub_469400` (`0x00469400`) | **`SteamWorkshop_AdvanceDownloadQueue`** | Clears the current active download ID, pops the next queued item from `data_e40bc0`, logs the transition and calls `DownloadItem` for the next queued item【65628915320824†L108-L121】. |
| `sub_469470` (`0x00469470`) | **`SteamWorkshop_FinalizeItem`** | Fetches item metadata/state, copies the mounted item into the host cache array (`data_e303b0`), triggers a filesystem refresh and optionally advances the queue【65628915320824†L109-L123】. |
| `sub_4695C0` (`0x004695C0`) | **`SteamWorkshopCallbacks_OnItemInstalled`** | Ignores invalid app IDs, skips already‑installed items and routes valid installs through `SteamWorkshop_FinalizeItem`【65628915320824†L110-L113】. |
| `sub_469630` (`0x00469630`) | **`SteamWorkshopCallbacks_OnDownloadItemResult`** | Validates the app ID and active queue item; finalizes successful downloads and handles errors by advancing the queue【65628915320824†L112-L114】. |
| `sub_469260` (`0x00469260`) | **`SteamWorkshop_SubscribeItem`** | Wrapper around `SteamUGC()->SubscribeItem`. |
| `sub_4692B0` (`0x004692B0`) | **`SteamWorkshop_UnsubscribeItem`** | Wrapper around `SteamUGC()->UnsubscribeItem`. |
| `sub_4699C0` (`0x004699C0`) | **`SteamWorkshop_RequestDownload`** | Chooses immediate vs. queued download mode and handles caching before calling `SteamUGC()->DownloadItem`. |
| `sub_4DF010`–`sub_4DF0D0` | **`SteamCmd_DownloadUGC_f`**, **`SteamCmd_SubscribeUGC_f`**, **`SteamCmd_UnsubscribeUGC_f`** | Console commands to trigger workshop operations【932230678200358†L174-L176】. |

The queue state is maintained in `data_e40bb4`–`data_e40bc0`, and the final cache array resides in `data_e303b0`【65628915320824†L116-L122】.

### Steam Stats Manager

The binary includes a dedicated per‑player stats manager that tracks numeric fields and achievements and publishes aggregated summaries.  Key functions (drawn from **Rounds 02** and **03**) include:

| Raw function | Proposed alias | Description |
|---|---|---|
| `sub_467850` (`0x00467850`) | **`SteamStats_Init`** | Constructor for an `idSteamStats` object; copies the descriptor table from `data_561060`, allocates writable buffers, registers callbacks for `SteamServersConnected_t`, `GSStatsReceived_t` and `GSStatsStored_t` and requests initial stats【65628915320824†L132-L160】. |
| `sub_467560` (`0x00467560`) | **`SteamStats_Shutdown`** | Frees the stat buffers and unregisters callbacks【65628915320824†L156-L160】. |
| `sub_467190` (`0x00467190`) | **`SteamStats_OnServersConnected`** | Requests current stats when server interfaces are ready【65628915320824†L153-L158】. |
| `sub_4671D0` (`0x004671D0`) | **`SteamStats_OnStatsReceived`** | Reads all current values via `SteamGameServerStats`, initializes the writable index table and marks the object ready【65628915320824†L153-L158】. |
| `sub_467360` (`0x00467360`) | **`SteamStats_OnStatsStored`** | Logs store success/failure and retries reception if validation fails【65628915320824†L153-L158】. |
| `sub_4670C0` (`0x004670C0`) | **`SteamStats_FlushPendingValues`** | Iterates cached descriptors and pushes pending values through `SteamGameServerStats`【65628915320824†L153-L158】. |
| `sub_4672D0` (`0x004672D0`) | **`SteamStats_SetAchievement`** (corrected) | Sets a specific achievement by name on `SteamGameServerStats` and then flushes the numeric stats【325473679468188†L88-L96】. |
| `sub_467D40` (`0x00467D40`) | **`SteamStats_AddFieldValue`** | Updates a numeric stat field for a player and logs the value【325473679468188†L71-L77】. |
| `sub_467E00` (`0x00467E00`) | **`SteamStats_UnlockAchievement`** | High‑level wrapper that applies gating and calls `SteamStats_SetAchievement`【325473679468188†L71-L77】. |
| `sub_467F70` (`0x00467F70`) | **`SteamStats_HasAchievement`** | Returns whether an achievement is already unlocked【325473679468188†L71-L77】. |
| `sub_467B10` (`0x00467B10`) | **`SteamStats_RemovePlayerSession`** | Looks up a player session in the `data_e30390` red‑black tree, flushes pending data, shuts down the object, deletes it and removes the tree node【325473679468188†L71-L77】. |
| `sub_467CD0` (`0x00467CD0`) | **`SteamStats_CreatePlayerSession`** | Creates an `idSteamStats` session for a player, inserts it into `data_e30390` and sends a “hello” packet through `SteamGameServerNetworking()`【325473679468188†L71-L77】. |
| `sub_468030` (`0x00468030`) | **`SteamStats_ProcessEvent`** | Processes event names like `PLAYER_STATS`, `PLAYER_DEATH` and `PLAYER_KILL`; updates pending stat and event accumulators (`data_e303a0`, `data_e30380`) and increments counters【325473679468188†L98-L104】. |
| `sub_468EE0` (`0x00468EE0`) | **`SteamStats_BroadcastSummary`** | Merges a summary object with pending stats/events, serializes the payload and broadcasts it to every recipient in `data_e30370`, then clears the accumulators【325473679468188†L98-L104】. |

These functions rely on red‑black trees (`data_e30390`/`e30394`) to store per‑player sessions and maintain lists of recipients (`data_e30370`/`e30374`) and JSON‑like accumulators for pending statistics【325473679468188†L61-L68】.

### Steam Overlay Commands

The host registers two console commands—`clientviewprofile` and `clientfriendinvite`—which call the Steam overlay functions `ActivateGameOverlayToUser` and `ShowInviteOverlay`.  A shared handler, `sub_460E60` (**`SteamOverlay_Command_f`**), parses the target `CSteamID` from the command argument and selects the appropriate overlay verb【65628915320824†L87-L100】.

### Engine‑to‑Host Bridge (`data_12d2670`)

A particularly opaque section of the binary is the dispatch object at `data_12d2670`.  Multiple wrappers (e.g., `sub_4F1F10`, `sub_4F1F30`, …) call through this vtable, and if the bridge pointer is null they return default values or no‑ops.  The table appears to expose:

- a callback registration slot (`+0x18`) used during client initialization【65628915320824†L60-L63】
- projection/geometry helpers for rendering (`+0x14`)【65628915320824†L55-L58】
- multiple list/count functions for drawing string lists on the UI (`+0x38`..`+0x64`)【65628915320824†L60-L72】
- per‑frame update and activation hooks (`+0x0C`, `+0x2C`)【65628915320824†L50-L54】

Because the semantics are not yet fully understood, the mapping documents refrain from assigning permanent names to these slots【65628915320824†L75-L85】.  Nevertheless, the structural analysis indicates this object mediates between the Quake III engine’s UI lists/projections and the host’s browser overlay.

### Browser Control Commands (Round 03 additions)

The third mapping pass closed the remaining browser command handlers:

| Raw function | Proposed alias | Role |
|---|---|---|
| `sub_4F2A10` (`0x004F2A10`) | **`QLWebHost_ClearCache_f`** | Registered as `web_clearCache`; clears the current Awesomium session cache【325473679468188†L25-L29】. |
| `sub_4F2A30` (`0x004F2A30`) | **`QLWebHost_Reload_f`** | Registered as `web_reload`; resets session state and reloads the view【325473679468188†L25-L29】. |
| `sub_4F3CB0` (`0x004F3CB0`) | **`QLWebHost_ShowError_f`** | Registered as `web_showError`; forwards an error string into the normal `game.error` publisher【325473679468188†L25-L29】. |

These functions demonstrate that the host treats the browser as a controllable UI component beyond the initial launcher; engine code can clear caches, reload the UI or show error messages through simple console commands【325473679468188†L32-L35】.

## Cross‑cutting Observations and Next Steps

1. **Stable event contract:**  The host publishes a consistent set of event names (`game.start`, `game.end`, `game.error`, `bind.changed`, `cvar.name`, `lobby.*`, `web.*`, etc.), implying any open‑source replacement should reproduce this API to maintain compatibility.  Browser event publication is central to the UI/engine bridge【65628915320824†L41-L43】.

2. **Separation of concerns:**  Steam client, lobby, workshop, game server, microtransactions and stats are modular subsystems with dedicated init, callback and shutdown paths.  Each registers its own callback objects and publishes messages into the browser or engine.  This modularity suggests that porting efforts can tackle subsystems incrementally.

3. **Unmapped areas:**  The `data_12d2670` bridge still hides several opaque slots; further passes should instrument these functions to infer the semantics of list drawing and projection helpers.  Additionally, some low‑confidence helpers within the Steam stats and game server clusters remain unnamed; targeted dynamic analysis could confirm their roles【65628915320824†L75-L85】【325473679468188†L146-L149】.

4. **Chromium/Awesomium reproduction:**  The notes emphasise that replicating the entire Awesomium runtime is unnecessary for parity; the high‑value compatibility target is the host event contract rather than the exact rendering backend【932230678200358†L186-L197】.  A minimal browser replacement could provide the same JavaScript API endpoints without bundling Awesomium.

5. **Potential future work:**  Subsequent rounds could:
   - Map the `QLJSHandler` method table (`sub_4F1EE0` through `sub_4F2280`) to understand the native‑to‑JS contract【932230678200358†L198-L202】.
   - Finish naming the workshop finalization helpers (`sub_469470`, `sub_469400`, `sub_4D2E80`) to align with filesystem logic【932230678200358†L198-L203】.
   - Split the server‑side Steam stats cluster (`0x004670C0+`) from auth/session code to clarify responsibilities【932230678200358†L198-L203】.
   - Generate stable symbol exports for `quakelive_steam.exe` once alias sets stabilise, allowing automatic application of names in the Ghidra database and reducing confusion【932230678200358†L200-L204】.

## Conclusion

The reverse‑engineering of `quakelive_steam.exe` reveals a complex host application that integrates browser rendering, Steamworks services and Quake Live–specific functionality.  The mapping documents in the repository provide a robust foundation for understanding this binary.  By organising functions into subsystems and aligning them with Quake III sources where possible, we can identify clear targets for re‑implementation, hooks for engine integration and areas where additional analysis is needed.  Future work can expand upon these mappings, refine alias names and build the glue required to reproduce the live-service behaviour of Quake Live in an open‑source context.
