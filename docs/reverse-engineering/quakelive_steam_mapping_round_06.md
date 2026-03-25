# Quake Live Steam Host Mapping Round 06

## Scope

This round resolves two host-side clusters that were still undernamed after Round 05:

1. the Steam voice capture / P2P transport path plus the nearby avatar-image cache helper
2. the Steam server-browser request surface and the `JSBrowserDetails` callback publisher suite

The evidence chain stayed inside the committed retail corpus:

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- `references/hlil/quakelive/quakelive_steam.exe/`

For the browser request names, I also used the retail string table around `RequestServers`, `RequestServerDetails`, and `RefreshList` as a second signal so the promoted aliases match the host-facing JS surface rather than only the internal helper mechanics.

## Steam Voice Transport And Avatar Cache

The voice path now has enough evidence to promote the recording, outgoing-packet, incoming-packet, and per-frame pump helpers.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4603F0` (`0x004603F0`) | `SteamVoice_StartRecording_f` | Observed | Registered as `+voice` at `0046156A`. When `data_e3021c` is clear, it sets the recording flag, marks the local Steam ID as speaking through `SteamFriends()->vtable[0x6c]`, starts voice capture through `SteamUser()->vtable[0x1c]`, queries the optimal sample rate through `SteamUser()->vtable[0x30]`, and logs `Started recording - optimal sample rate %d`. |
| `sub_460490` (`0x00460490`) | `SteamVoice_StopRecording_f` | Observed | Registered as `-voice` at `00461579`. Stops capture through `SteamUser()->vtable[0x20]`, clears the speaking state through the same `SteamFriends()->vtable[0x6c]` path, and drops the local recording flag. |
| `sub_460D10` (`0x00460D10`) | `SteamVoice_SendCapturedPacket` | Observed | Only runs while recording. Pulls compressed voice from `SteamUser()->vtable[0x28]` into `data_e2c218`, parses a target SteamID with `sscanf("%llu", ...)`, and sends the captured packet over `SteamNetworking()` channel `1` when the current net mode is the Steam P2P path. |
| `sub_460F30` (`0x00460F30`) | `SteamClient_GetAvatarImageHandle` | Observed | Builds a `steam_%llu` cache key, returns the existing cached image handle when present, otherwise fetches the Steam avatar image through `SteamFriends()->vtable[0x90]`, reads dimensions and RGBA pixels through `SteamUtils()->vtable[0x14]` / `vtable[0x18]`, creates an engine image resource, and registers it back into the cache. |
| `sub_461A60` (`0x00461A60`) | `SteamVoice_ProcessIncomingPackets` | Observed | Loops on `SteamNetworking()->vtable[4]` / `vtable[8]` for channel `1`, decompresses payloads through `SteamUser()->vtable[0x2c]`, logs zero-length decompressions with `%d compressed voice bytes, decompressed to 0`, marks speakers active through `data_146cc38`, and feeds PCM into `sub_4DAB00`. |
| `sub_461D40` (`0x00461D40`) | `SteamClient_Frame` | Observed | Called from the main client frame at `004CC995`. Runs `SteamAPI_RunCallbacks()`, pumps outgoing voice through `sub_460D10`, drains channel `0` Steam packets into `game.stats.report`, and then calls `sub_461A60` to process incoming voice traffic. |

### Supporting signals

1. The command registration at `0046156A` / `00461579` ties `sub_4603F0` and `sub_460490` directly to `+voice` and `-voice`.
2. The retail string table exposes the matching runtime text at `0053277C` (`Started recording - optimal sample rate %d\n`) and `005328F8` (`%d compressed voice bytes, decompressed to 0\n`).
3. The frame call at `004CC995` makes `sub_461D40` the owning per-frame Steam client pump rather than only another packet helper.

## Steam Browser Request Surface And `JSBrowserDetails`

The server-browser path resolves cleanly once the JS dispatch, RTTI, and publisher strings are considered together.

### Public browser request wrappers

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_462E80` (`0x00462E80`) | `SteamBrowser_RefreshList` | Observed | Reached from the JS dispatch at `0043215B`. If the global browser state at `data_e30334` has an active request handle, it forwards that handle into `SteamMatchmakingServers()->vtable[0x24]`. The surrounding method string table names this surface `RefreshList`. |
| `sub_463090` (`0x00463090`) | `SteamBrowser_RequestServers` | Observed | Reached from the JS dispatch at `00432111` after one integer argument is extracted from the Awesomium argument array. It tailcalls the stateful request worker with `data_e30334`. The retail method string table names this surface `RequestServers`. |
| `sub_4630B0` (`0x004630B0`) | `SteamBrowser_RequestServerDetails` | Observed | Reached from the JS dispatch at `0043214E` after two integer arguments are decoded. Allocates a `0x58`-byte `JSBrowserDetails` object, installs the three Steam callback vfptrs, and starts the async detail-query suite. The retail method string table names this surface `RequestServerDetails`. |

### `JSBrowserDetails` object lifecycle and callbacks

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_461F70` (`0x00461F70`) | `JSBrowserDetails_RequestServerDetails` | Observed | Initializes the request object with the two incoming integers, formats the browser-side ID string as `"%u_%i"`, and fires three Steam matchmaking-server queries through vtable slots `0x34`, `0x3c`, and `0x38`. |
| `sub_461FE0` (`0x00461FE0`) | `JSBrowserDetails_OnServerResponded` | Observed | Validates the server's app ID against `SteamUtils()->GetAppID()`, builds the `servers.details.%u_%u.response` payload, publishes fields including `name`, `numPlayers`, `maxPlayers`, `ping`, `map`, `botPlayers`, `password`, `vac`, `ip`, `port`, `id`, `steam_id`, `tags`, `gametype`, and `lastPlayed`, then retires the object after the third callback leg completes. |
| `sub_462360` (`0x00462360`) | `JSBrowserDetails_OnRuleResponded` | Observed | Builds and publishes `servers.rules.%s.response` with `id`, `ip`, `port`, `rule`, and `value`. |
| `sub_462490` (`0x00462490`) | `JSBrowserDetails_OnRulesFailed` | Observed | Publishes `servers.rules.%s.failed`, increments the completion counter at `+0x54`, and deletes the request object when all three callback legs are done. |
| `sub_4625A0` (`0x004625A0`) | `JSBrowserDetails_OnRulesRefreshComplete` | Observed | Publishes `servers.rules.%s.end`, increments the same rules-side completion counter, and deletes the object on the third completion. |
| `sub_4626B0` (`0x004626B0`) | `JSBrowserDetails_OnPlayerResponded` | Observed | Builds and publishes `servers.players.%s.response` with `id`, `ip`, `port`, `name`, `score`, and `time`. |
| `sub_462830` (`0x00462830`) | `JSBrowserDetails_OnPlayersFailed` | Observed | Publishes `servers.players.%s.failed`, increments the players-side completion counter at `+0x50`, and deletes the owning `JSBrowserDetails` object when the aggregate callback count reaches three. |
| `sub_462940` (`0x00462940`) | `JSBrowserDetails_OnPlayersRefreshComplete` | Observed | Publishes `servers.players.%s.end`, increments the same players-side completion counter, and deletes the owning object after the third completion. |

### Shared browser publishers

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_462DB0` (`0x00462DB0`) | `SteamBrowser_PublishServerDetailsFailed` | Observed | Despite Ghidra's default `std::locale::_Locimp::_Locimp_dtor` collision, the HLIL shows that it builds a one-field `{ "id": arg1 }` object and publishes `servers.details.%i.failed`. |
| `sub_462E60` (`0x00462E60`) | `SteamBrowser_PublishRefreshEnd` | Observed | Clears the active-refresh flag at `*(arg1 + 4)` and publishes `servers.refresh.end`. |

### Supporting signals

1. The JS dispatch at `004320EF` / `0043211D` / `0043215B` routes directly to `sub_463090`, `sub_4630B0`, and `sub_462E80`.
2. The retail string table exposes the corresponding public method names:
   - `0052C900` / `data_55C0B0`: `RequestServers`
   - `0052C8E8` / `data_55C0BC`: `RequestServerDetails`
   - `0052C8DC` / `data_55C0C8`: `RefreshList`
3. `analysis_symbols.txt` confirms that `JSBrowserDetails` carries RTTI and vfptrs for `ISteamMatchmakingRulesResponse`, `ISteamMatchmakingPlayersResponse`, and `ISteamMatchmakingPingResponse`, which matches the object layout installed by `sub_4630B0`.

## New High-Confidence Aliases Added This Round

- `sub_4603F0`
- `sub_460490`
- `sub_460D10`
- `sub_460F30`
- `sub_461A60`
- `sub_461D40`
- `sub_461F70`
- `sub_461FE0`
- `sub_462360`
- `sub_462490`
- `sub_4625A0`
- `sub_4626B0`
- `sub_462830`
- `sub_462940`
- `sub_462DB0`
- `sub_462E60`
- `sub_462E80`
- `sub_463090`
- `sub_4630B0`

## Open Questions

1. `sub_462A50` clearly rebuilds the same server-details payload through `SteamMatchmakingServers()->vtable[0x1c]`, but I am leaving it unnamed until its owning callsite is pinned well enough to distinguish list-handle/index semantics from any direct lookup wrapper.
2. `sub_462EB0` is the stateful worker behind `SteamBrowser_RequestServers`, but I am keeping only the public JS wrapper named until the exact Steam matchmaking-server slot ownership around `+0x18` / `+0x24` is revalidated.
3. `sub_461C00` and its thin wrapper at `sub_4B0420` still look like remote-speaker membership bookkeeping, but the current evidence is not stable enough to promote a semantic alias.
