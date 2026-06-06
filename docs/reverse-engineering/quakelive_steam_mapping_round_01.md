# Quake Live Steam Host Mapping Round 01

## Scope

This note records a high-confidence reverse-engineering pass over `quakelive_steam.exe` using the committed evidence set:

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/exports.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c` as a hint set only
- `references/hlil/quakelive/quakelive_steam.exe/`

Observed baseline from `metadata.txt`:

- `5473` functions
- `351` imports
- `2` exports (`_Mutex`, `entry`)
- `4377` promoted analysis symbols

This round focused on stable subsystem ownership and alias candidates for the host executable rather than source implementation. Alias names below are intentionally descriptive and should be treated as candidate names until regenerated symbol exports confirm them against the current Ghidra database.

## Subsystem Anchors

| Subsystem | Observed anchors | Owning host role |
| --- | --- | --- |
| Browser / Awesomium host | `QLResourceInterceptor`, `QLJSHandler`, `web_browserActive`, `EnginePublish`, `OnCommNotice`, `game.key` | Native browser bootstrap, JS bridge, surface pump, local asset interception |
| Steam client callbacks | `SteamAPI_Init`, `SteamFriends`, `SteamUserStats`, `SteamNetworking`, `SteamCallbacks` RTTI | Rich presence, join requests, persona updates, UGC query completion |
| Steam lobby / matchmaking | `SteamLobbyCallbacks` RTTI, `lobby.%s.enter`, `lobby.error`, `connect_lobby`, `steam_maxLobbyClients` | Lobby create/join/leave/chat/data event publication into JS |
| Steam microtransactions | `SteamMicroCallbacks` RTTI, `MicroTxnAuthorizationResponse_t`, `GOT MICRO RESPONSE...` | Browser-facing store authorization events |
| Steam game server / auth | `SteamGameServer_Init`, `SteamServerCallbacks` RTTI, `ValidateAuthTicketResponse_t`, `VAC check timed out`, `Steam Gameserver initialized.` | Dedicated bootstrap, VAC/auth, SteamID publication, periodic server state updates |
| Workshop / UGC | `SteamWorkshopCallbacks` RTTI, `SteamUGC`, `SteamGameServerUGC`, `web.ugc.results`, `steam_downloadugc` | Query, subscribe, download, mount, and callback relay for workshop content |

## High-Confidence Alias Candidates

### Browser Host And JS Bridge

| Raw symbol | Alias candidate | Observed role |
| --- | --- | --- |
| `sub_434620` (`0x00434620`) | `QLResourceInterceptor_OnRequest` | Reads `fs_webpath`, inspects `Awesomium::WebURL` host/path, special-cases `/screenshot*`, and returns `Awesomium::ResourceResponse::Create(...)`. |
| `sub_4F23E0` (`0x004F23E0`) | `QLWebView_SetLocationHash` | Resolves cached `window` and `document.location`, then updates `window.location.hash` without reopening the view. |
| `sub_4F24D0` (`0x004F24D0`) | `QLWebHost_Deactivate` | Clears browser-active state, restores cursor state, and stops the embedded view from driving input. |
| `sub_4F27C0` (`0x004F27C0`) | `QLWebView_InjectMouseDown` | Forwards mouse-button down events into the active `WebView`. |
| `sub_4F2820` (`0x004F2820`) | `QLWebView_InjectMouseUp` | Forwards mouse-button up events into the active `WebView`. |
| `sub_4F2870` (`0x004F2870`) | `QLWebView_InjectMouseWheel` | Forwards wheel motion into the active `WebView`. |
| `sub_4F2A60` (`0x004F2A60`) | `QLWebHost_Shutdown` | Tears down the active view and calls `Awesomium::WebCore::Shutdown` when the browser host is live. |
| `sub_4F2B40` (`0x004F2B40`) | `QLWebHost_PumpFrame` | Pulls dirty `BitmapSurface` data, uploads it into an engine texture, and mirrors cursor state into native globals. |
| `sub_4F2D30` (`0x004F2D30`) | `QLWebHost_OpenURL` | Initializes `Awesomium::WebCore`, creates a session rooted at `fs_homepath`, registers `web.pak`, `steam`, and `QLResourceInterceptor`, waits for bootstrap readiness, then navigates to the target URL and flips `web_browserActive` on. |
| `sub_4F3160` (`0x004F3160`) | `QLWebHost_OpenRelativeURL` | Builds a URL from cached launcher state and routes it through `sub_4F2D30`. |
| `sub_4F31D0` (`0x004F31D0`) | `QLWebHost_NavigateOrOpen` | Updates the current browser hash when the view exists; otherwise reopens the launcher root URL. |
| `sub_4F3260` (`0x004F3260`) | `QLWebView_PublishEvent` | Marshals event name plus optional payload into a JS call to `window.EnginePublish`, logging `PublishEvent failed: no view` or `...no window object` on failure. |
| `sub_4F3420` (`0x004F3420`) | `QLWebView_PublishGameKey` | Builds a JSON object containing `id` and `key`, then publishes the `game.key` event through `sub_4F3260`. |

Observed event/API strings tied to this block:

- `OnCommNotice`
- `EnginePublish`
- `game.key`
- `ActivateGameOverlayToUser`
- `ShowInviteOverlay`
- `OpenSteamOverlayURL`

### Steam Browser Data Source

| Raw symbol | Alias candidate | Observed role |
| --- | --- | --- |
| `sub_464290` (`0x00464290`) | `SteamDataSource_OnAvatarImageLoaded` | Handles `AvatarImageLoaded_t`, looks up the pending request, and completes the browser-side response path. |
| `sub_464300` (`0x00464300`) | `SteamDataSource_Init` | Constructs the `SteamDataSource`, allocates two internal caches/trees, and registers the `AvatarImageLoaded_t` callback (`0x14e`). |
| `sub_464440` (`0x00464440`) | `SteamDataSource_Shutdown` | Unregisters the callback and destroys the internal request/cache containers. |

Additional observations:

- The request path immediately around `0x00464169` parses avatar-style filenames, validates size/type, queries `SteamFriends()->Get*Avatar`, and either fulfills immediately or queues the request for the `AvatarImageLoaded_t` callback.
- `sub_460F30` also looks host-owned rather than UI-owned: it fetches Steam avatar pixels through `SteamUtils`, uploads them into an engine-side cached image named `steam_%llu`, and is likely shared by the data source path.

### Steam Client Bootstrap, Presence, And UGC Querying

| Raw symbol | Alias candidate | Observed role |
| --- | --- | --- |
| `sub_4613A0` (`0x004613A0`) | `SteamCallbacks_Init` | Allocates the main client callback bundle and registers `GameRichPresenceJoinRequested_t`, `UserStatsReceived_t`, `PersonaStateChange_t`, client-side `P2PSessionRequest_t`, `GameServerChangeRequested_t`, `FriendRichPresenceUpdate_t`, and the `SteamUGCQueryCompleted_t` call-result slot. |
| `sub_461500` (`0x00461500`) | `SteamClient_Init` | Calls `SteamAPI_Init`, allocates `SteamCallbacks`, initializes microtransaction and lobby layers, registers `+voice` / `-voice`, conditionally registers `stats_clear`, and sets rich presence `status = "At the main menu"`. |
| `sub_45FD00` (`0x0045FD00`) | `SteamCallbacks_OnUGCQueryCompleted` | Builds a JSON array of query results and publishes either `web.ugc.results` or `web.ugc.failed`, then closes the UGC query handle. |
| `sub_45FEF0` (`0x0045FEF0`) | `SteamCallbacks_OnP2PSessionRequest` | Accepts a client-side P2P session only when the incoming Steam ID matches the currently tracked peer target. |
| `sub_45FF50` (`0x0045FF50`) | `SteamCallbacks_OnRichPresenceJoinRequested` | Routes the rich-presence join payload into the existing `connect` command path. |
| `sub_45FF70` (`0x0045FF70`) | `SteamCallbacks_OnGameServerChangeRequested` | Copies the supplied password into the `password` cvar when present and emits `connect %s\n`. |
| `sub_45FFD0` (`0x0045FFD0`) | `SteamCallbacks_OnUserStatsReceived` | Builds a browser-facing payload containing `ID`, `NAME`, and a nested `STATS` object populated from `SteamUserStats`. |
| `sub_460800` (`0x00460800`) | `SteamCallbacks_OnPersonaStateChange` | High-confidence callback target from `SteamCallbacks_Init`; body publishes persona-change state into browser-facing event paths. |
| `sub_4602E0` (`0x004602E0`) | `SteamCallbacks_OnFriendRichPresenceUpdate` | High-confidence callback target from `SteamCallbacks_Init`; used for friend rich-presence change relays. |
| `sub_460DC0` (`0x00460DC0`) | `SteamClient_RequestUGCQuery` | Creates a UGC query, executes it through `SteamUGC`, and binds the call result to `sub_45FD00`. |

### Steam Lobby And Matchmaking Bridge

| Raw symbol | Alias candidate | Observed role |
| --- | --- | --- |
| `sub_4656A0` (`0x004656A0`) | `SteamLobbyCallbacks_Init` | Registers callbacks for `LobbyCreated_t`, `LobbyEnter_t`, `LobbyChatUpdate_t`, `LobbyChatMsg_t`, `LobbyDataUpdate_t`, `LobbyGameCreated_t`, `LobbyKicked_t`, and `GameLobbyJoinRequested_t`. |
| `sub_465840` (`0x00465840`) | `SteamLobby_Init` | Allocates the callback bundle, registers `lobby_autoconnect`, creates `steam_maxLobbyClients`, and exposes the `connect_lobby` console command. |
| `sub_464BF0` (`0x00464BF0`) | `SteamLobbyCallbacks_OnLobbyCreated` | Publishes `lobby.%s.create` on success and `lobby.error` with an error payload on failure. |
| `sub_464D90` (`0x00464D90`) | `SteamLobbyCallbacks_OnLobbyEnter` | Updates the current lobby ID, enumerates lobby metadata and player list, and publishes `lobby.%s.enter`; error paths publish `lobby.error`. |
| `sub_4652E0` (`0x004652E0`) | `SteamLobbyCallbacks_OnLobbyChatUpdate` | Emits `lobby.%s.user.joined` or `lobby.%s.user.left` with `id`, `name`, and population counts. |
| `sub_4645A0` (`0x004645A0`) | `SteamLobbyCallbacks_OnLobbyChatMessage` | Reads the Steam lobby chat entry and publishes `lobby.%s.chat` with `id`, `name`, and `msg`. |
| `sub_465490` (`0x00465490`) | `SteamLobbyCallbacks_OnLobbyDataUpdate` | Builds a payload keyed by lobby ID and publishes `lobby.%llu.updated`; current-lobby updates also enumerate key/value data. |
| `sub_464720` (`0x00464720`) | `SteamLobbyCallbacks_OnLobbyGameCreated` | Publishes `lobby.%llu.game_created` with `ip`, `port`, and `id`. |
| `sub_464830` (`0x00464830`) | `SteamLobbyCallbacks_OnLobbyKicked` | Publishes `lobby.%llu.kicked` and clears the retained current-lobby state. |
| `sub_464900` (`0x00464900`) | `SteamLobbyCallbacks_OnGameLobbyJoinRequested` | Publishes `lobby.%llu.join_requested`. |
| `sub_4649E0` (`0x004649E0`) | `SteamLobby_LeaveLobby` | Leaves the current lobby, publishes `lobby.%s.left`, and clears the retained lobby ID. |
| `sub_464AA0` (`0x00464AA0`) | `SteamLobby_ConnectLobby_f` | Console command handler behind `connect_lobby`. |
| `sub_464AC0` (`0x00464AC0`) | `SteamLobby_SetData` | Wrapper around `SteamMatchmaking()->SetLobbyData` for the current lobby. |

Observed lobby event contract strings:

- `lobby.%s.create`
- `lobby.%s.enter`
- `lobby.%s.left`
- `lobby.%s.chat`
- `lobby.%s.user.joined`
- `lobby.%s.user.left`
- `lobby.%llu.updated`
- `lobby.%llu.game_created`
- `lobby.%llu.kicked`
- `lobby.%llu.join_requested`
- `lobby.error`
- `Cannot join lobby with blocked member`
- `You are banned from this lobby`
- `Unable to create lobby`

Two helpers remain intentionally unnamed in this pass:

- `sub_4649B0` is very likely the lobby create/request entry point because it calls into `SteamMatchmaking` with the configured max-clients path.
- `sub_464BB0` appears to be lobby/overlay-adjacent but still needs direct control-flow review before naming.

### Steam Microtransactions

| Raw symbol | Alias candidate | Observed role |
| --- | --- | --- |
| `sub_4658A0` (`0x004658A0`) | `SteamMicroCallbacks_OnAuthorizationResponse` | Builds a browser-facing JSON object with `appid`, `orderid`, and `authorized`, then logs `GOT MICRO RESPONSE: ...`. |
| `sub_4659E0` (`0x004659E0`) | `SteamMicroCallbacks_Init` | Allocates and registers the `MicroTxnAuthorizationResponse_t` callback object. |

### Steam Game Server, Auth, And Presence Publication

| Raw symbol | Alias candidate | Observed role |
| --- | --- | --- |
| `sub_466DB0` (`0x00466DB0`) | `SteamServerCallbacks_Init` | Registers `SteamServersConnected_t`, `SteamServerConnectFailure_t`, `SteamServersDisconnected_t`, `ValidateAuthTicketResponse_t`, and server-side `P2PSessionRequest_t`. |
| `sub_466ED0` (`0x00466ED0`) | `SteamServer_Init` | Creates the callback bundle, registers `sv_vac`, calls `SteamGameServer_Init`, selects `SteamUGC` vs `SteamGameServerUGC`, applies the Steam account/login path, sets product/mod strings, and logs `Steam Gameserver initialized.` |
| `sub_466800` (`0x00466800`) | `SteamServerCallbacks_OnServersConnected` | Logs the successful Steam server connection, marks the global connected flag, publishes the GS SteamID, pushes initial server state, and primes the dedicated path. |
| `sub_465C10` (`0x00465C10`) | `SteamServerCallbacks_OnConnectFailure` | Clears the connected flag and logs the failure. |
| `sub_465C30` (`0x00465C30`) | `SteamServerCallbacks_OnServersDisconnected` | Clears the connected flag and logs the disconnect. |
| `sub_465C50` (`0x00465C50`) | `SteamServerCallbacks_OnValidateAuthTicketResponse` | Matches the callback SteamID to a live client, applies fake-VAC overrides when configured, accepts only allowed status codes, and kicks on failure using reason strings including `VAC check timed out` and `Issuer canceled auth ticket`. |
| `sub_465B00` (`0x00465B00`) | `SteamServer_PublishSteamID` | Reads the GS SteamID, writes `sv_referencedSteamworks`, and publishes configstrings `0x2ca` and `0x2cb`. |
| `sub_465B70` (`0x00465B70`) | `SteamServerCallbacks_OnP2PSessionRequest` | Accepts P2P requests only when the incoming SteamID matches a live `CS_ACTIVE` client slot. |
| `sub_465D30` (`0x00465D30`) | `SteamServer_Shutdown` | Calls `SteamGameServer_Shutdown` and clears the global initialized flag. |
| `sub_465E30` (`0x00465E30`) | `SteamServer_InitDefaultHostname` | Defaults `sv_hostname` to `"%s's Match"` using the Steam persona name when not running a build harness. |
| `sub_465FD0` (`0x00465FD0`) | `SteamServer_BeginAuthSession` | Deduplicates auth requests, calls `SteamGameServer()->BeginAuthSession`, logs the call, and inserts the SteamID into the auth-session tree. |
| `sub_4661E0` (`0x004661E0`) | `SteamServer_EndAuthSession` | Ends the Steam auth session, removes the SteamID from the auth tree, and logs the action. |
| `sub_466260` (`0x00466260`) | `SteamServer_UpdatePublishedState` | Publishes dynamic server metadata such as player count, passworded state, gametype/map details, bot masking, tags, and per-player Steam identity/name entries. |
| `sub_466850` (`0x00466850`) | `SteamServer_Frame` | Runs `SteamGameServer_RunCallbacks`, periodically refreshes published server state, pumps P2P networking, and drains Steam-owned packet/auth work. |

Lower-confidence but bounded server helpers:

- `sub_465A60` is called after the server connect path and iterates fixed-size chunks into `SteamGameServer()->vtable[0x50/4]`; it likely publishes a buffered ruleset/config batch.
- `sub_465DB0` toggles `SteamGameServer()->vtable[0x9c/4]` and stores a timestamp; it looks like an advertise-active helper.
- `sub_4670C0` onward is a distinct stats upload cluster around `SteamGameServerStats`, but that branch needs a dedicated pass before aliasing.

### Workshop And UGC Downloads

| Raw symbol | Alias candidate | Observed role |
| --- | --- | --- |
| `sub_4696D0` (`0x004696D0`) | `SteamWorkshopCallbacks_Init` | Registers `ItemInstalled_t` and `DownloadItemResult_t` callbacks. |
| `sub_4697A0` (`0x004697A0`) | `SteamWorkshop_Init` | Allocates the callback bundle if needed, checks `pak00.pk3`, respects `fs_skipWorkshop` and `com_build`, validates the active UGC interface, enumerates subscribed items, and queues/mounts them. |
| `sub_4699C0` (`0x004699C0`) | `SteamWorkshop_RequestDownload` | Chooses immediate versus queued download mode, checks cached item state, requests download when needed, and handles the in-cache fast path. |
| `sub_469260` (`0x00469260`) | `SteamWorkshop_SubscribeItem` | Wrapper around the Steam subscribe-item path. |
| `sub_4692B0` (`0x004692B0`) | `SteamWorkshop_UnsubscribeItem` | Wrapper around the Steam unsubscribe-item path. |
| `sub_4695C0` (`0x004695C0`) | `SteamWorkshopCallbacks_OnItemInstalled` | High-confidence installed-item callback target from `SteamWorkshopCallbacks_Init`. |
| `sub_469630` (`0x00469630`) | `SteamWorkshopCallbacks_OnDownloadItemResult` | High-confidence download-result callback target from `SteamWorkshopCallbacks_Init`. |
| `sub_4DF010` (`0x004DF010`) | `SteamCmd_DownloadUGC_f` | Console command handler for `steam_downloadugc`. |
| `sub_4DF070` (`0x004DF070`) | `SteamCmd_SubscribeUGC_f` | Console command handler for `steam_subscribeugc`. |
| `sub_4DF0D0` (`0x004DF0D0`) | `SteamCmd_UnsubscribeUGC_f` | Console command handler for `steam_unsubscribeugc`. |

Three workshop helpers still need direct ownership confirmation before naming:

- `sub_469470` appears to finalize a mounted-or-ready workshop item.
- `sub_469400` is the common download-result completion path.
- `sub_4D2E80` is the filesystem-facing mount/import helper used by `SteamWorkshop_Init`.

## Cross-Cutting Reconstruction Notes

### Browser-to-engine event contract

The host executable already exposes the event names the engine-side fallback must preserve:

- browser publish path: `sub_4F3260`
- game key relay: `sub_4F3420`
- lobby publish path: `sub_4645A0`, `sub_464D90`, `sub_4652E0`, `sub_465490`
- UGC query publish path: `sub_45FD00`
- user stats/persona publish path: `sub_45FFD0`, `sub_460800`

That makes the minimal browser replacement problem narrower than a full Awesomium reconstruction. The highest-value compatibility target is the host event contract, not the exact retail rendering backend.

### Best next slices

1. Map the `QLJSHandler` method table (`sub_4F1EE0` through `sub_4F2280`) into named slots. This should unlock the native-to-JS contract without requiring a full browser runtime.
2. Finish the workshop mount path (`sub_469470`, `sub_469400`, `sub_4D2E80`) so workshop downloads can be tied back to existing filesystem code.
3. Split the server-side Steam stats cluster (`0x004670C0+`) away from auth/session flow. It is adjacent in memory but represents a separate reconstruction task.
4. Regenerate a symbol export for `quakelive_steam.exe` once the alias set stabilizes, so unresolved prefixes stop obscuring host-specific work.

## Deliverables From This Round

- High-confidence host-function naming candidates for browser, Steam client, lobby, microtransaction, game server, auth, and workshop subsystems.
- A bounded list of still-unnamed helpers whose ownership is now clear enough for the next pass.
- Matching additions to `references/analysis/quakelive_symbol_aliases.json` under the `quakelive_steam` key.
