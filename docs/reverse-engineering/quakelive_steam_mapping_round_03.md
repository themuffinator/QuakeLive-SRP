# Quake Live Steam Host Mapping Round 03

## Scope

This round extends [Round 01](./quakelive_steam_mapping_round_01.md) and [Round 02](./quakelive_steam_mapping_round_02.md) in three areas that were still only partially named:

1. the browser control command handlers behind `web_clearCache`, `web_reload`, and `web_showError`
2. the small Steam identity and auth-ticket helpers around `sub_460510` through `sub_4605f0`
3. the per-player Steam stats manager rooted at `data_e30390` plus the event/report pipeline around `sub_468030` and `sub_468ee0`

This pass also corrects one earlier tentative read from Round 02:

- `sub_4672d0` is not a generic stat-field commit helper. It calls `SteamGameServerStats` with an entry from the `AW_*` table at `data_561c00`, so it is the internal achievement-set path.

Evidence order stayed the same:

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- `references/hlil/quakelive/quakelive_steam.exe/`

## Browser Control Commands

Round 02 named the browser command registration block at `sub_4f3cd0`. This round closes the three still-unnamed command handlers that registration block exposes.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4f2a10` (`0x004f2a10`) | `QLWebHost_ClearCache_f` | Observed | Registered as `web_clearCache`; jumps through `data_12d3044` slot `+0x1c` and does nothing when the backing session object is absent. |
| `sub_4f2a30` (`0x004f2a30`) | `QLWebHost_Reload_f` | Observed | Registered as `web_reload`; clears the current cache/session state through `data_12d3044` and then calls the active `WebView` reload slot with `1`. |
| `sub_4f3cb0` (`0x004f3cb0`) | `QLWebHost_ShowError_f` | Observed | Registered as `web_showError`; forwards the first command argument into `sub_4f3570`, reusing the normal `game.error` publisher path. |

Two practical takeaways from this block:

- the browser control path is not limited to open/close/hash commands; the host keeps cache, reload, and manual error publication as first-class console hooks
- `web_showError` proves that the browser error publisher is intentionally reusable outside the normal crash/fatal flow

## Steam Identity And Auth Helpers

The client-side Steam bootstrap code already had the larger init/callback objects named. This pass closes the smaller helper layer those init paths depend on.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_460510` (`0x00460510`) | `SteamClient_IsInitialized` | Observed | Returns the global client Steam-API live flag `data_e30218`; `sub_461500` sets that flag from `SteamAPI_Init()`. |
| `sub_460550` (`0x00460550`) | `SteamClient_GetSteamID` | Observed | Returns the local `CSteamID` from `SteamUser()->GetSteamID()` when the client Steam API is live; the pair is reused for `fs_homepath`, local player identity, and disconnect cleanup. |
| `sub_4605c0` (`0x004605c0`) | `SteamClient_GetAuthSessionTicket` | Observed | Calls the `SteamUser` ticket function, stores the returned handle in `data_e2c208`, and returns the ticket size; the connect path immediately feeds that buffer into `SteamServer_BeginAuthSession`. |
| `sub_4605f0` (`0x004605f0`) | `SteamClient_CancelAuthTicket` | Observed | Cancels the cached auth-ticket handle in `data_e2c208`; the common disconnect/error path calls it before publishing `game.end`. |
| `sub_465a30` (`0x00465a30`) | `SteamServer_IsInitialized` | Observed | Returns `data_e30358`; `sub_466ed0` sets that flag from `SteamGameServer_Init(...)` and `sub_465d30` clears it during server shutdown. |

These helpers tighten the ownership split:

- `SteamClient_*` wrappers gate local-user identity and ticket issuance
- `SteamServer_IsInitialized` is the shared predicate for server auth, per-player stats, and end-of-match report broadcast

## Per-Player Steam Stats Manager

Round 02 established the `idSteamStats` object itself. This round closes the management layer around that object.

### Stable object stores

Two red-black-tree stores now have stable roles:

- `data_e30390` / sentinel `data_e30394`: per-player `idSteamStats` sessions keyed by the two 32-bit halves of a `CSteamID`
- `data_e30370` / sentinel `data_e30374`: recipients used when broadcasting the final aggregated stats payload

Two JSON-like accumulators are also now bounded:

- `data_e303a0`: pending `PLYR_STATS` payload
- `data_e30380`: pending `PLYR_EVENTS` payload

### High-confidence lifecycle and update aliases

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_467b10` (`0x00467b10`) | `SteamStats_RemovePlayerSession` | Observed | Looks up a player by SteamID in `data_e30390`, flushes pending data, shuts down the `idSteamStats` object, deletes it, and removes the tree node. |
| `sub_467cd0` (`0x00467cd0`) | `SteamStats_CreatePlayerSession` | Observed | Allocates an `idSteamStats` object with the player's SteamID, inserts it into `data_e30390`, and sends a `"hello"` packet through `SteamGameServerNetworking()` after creation. |
| `sub_467d40` (`0x00467d40`) | `SteamStats_AddFieldValue` | Observed | Resolves the player's `idSteamStats` object, adds `arg4` into the selected descriptor entry at `arg3`, and logs the updated field value. |
| `sub_467e00` (`0x00467e00`) | `SteamStats_UnlockAchievement` | Observed | Applies training/practice/in-progress gating, then unlocks one achievement by index either through the server-side helper `sub_4672d0` or through the client `SteamUserStats` path. |
| `sub_467f70` (`0x00467f70`) | `SteamStats_HasAchievement` | Observed | Returns whether the indexed achievement is already marked in the player's ready `idSteamStats` object. |

### Corrected internal achievement helper

`sub_4672d0` should now be read as the internal dedicated-server achievement setter, not as a generic stat-field commit helper.

Observed support:

- it calls `SteamGameServerStats()` and passes the player's two SteamID halves plus a string from `data_561c00`
- `data_561c00` is an `AW_*` table beginning with `AW_MIDAIR`, `AW_SPEED_KILLS`, and many other achievement identifiers
- after the API call it immediately falls through to `sub_4670c0`, which is the pending numeric stat flush path already mapped in Round 02

That leaves the corrected relationship as:

- `sub_467d40`: accumulate numeric stat fields
- `sub_4672d0`: set one achievement by name on the server-side stats interface
- `sub_467e00`: high-level achievement gate and dispatch wrapper
- `sub_467f70`: achievement-ready query helper

## Event And Report Pipeline

The large handler at `sub_468030` is now stable enough to name at the subsystem level, even though individual event branches still have room for finer sub-aliasing later.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_468030` (`0x00468030`) | `SteamStats_ProcessEvent` | Observed | Processes event names including `PLAYER_STATS`, `PLAYER_DEATH`, and `PLAYER_KILL`; appends payload into `data_e303a0` / `data_e30380`; updates win/loss counters, kill-family fields, and achievement gates. |
| `sub_468ee0` (`0x00468ee0`) | `SteamStats_BroadcastSummary` | Observed | Merges a supplied summary object with pending `PLYR_STATS` and `PLYR_EVENTS`, skips training/aborted summaries, serializes the payload, broadcasts it to every recipient in `data_e30370`, and clears the pending accumulators. |

### Engine-facing wrapper observations

I am not promoting these wrappers into the alias JSON yet, but their behavior is now constrained:

- `sub_4e2770` forwards a live client slot plus `(fieldIndex, delta)` into `sub_467d40`
- `sub_4e2860` forwards a live client slot plus `achievementIndex` into `sub_467e00`
- `sub_4e28c0` forwards a live client slot plus `achievementIndex` into `sub_467f70`
- `sub_4e2920` begins Steam auth for a live client and creates the matching per-player stats session when auth succeeds

The wrappers are structurally clear. I am leaving them unnamed for one more round because their exact exported surface still depends on confirming how the owning engine/game-module bridge labels them.

## New High-Confidence Aliases Added This Round

- browser control commands:
  - `sub_4f2a10`
  - `sub_4f2a30`
  - `sub_4f3cb0`
- Steam state and auth helpers:
  - `sub_460510`
  - `sub_460550`
  - `sub_4605c0`
  - `sub_4605f0`
  - `sub_465a30`
- per-player stats manager:
  - `sub_467b10`
  - `sub_467cd0`
  - `sub_467d40`
  - `sub_467e00`
  - `sub_467f70`
- event/report pipeline:
  - `sub_468030`
  - `sub_468ee0`

## Alias Correction From Earlier Rounds

- `sub_4672d0`
  - previous tentative alias: `SteamStats_CommitField`
  - corrected alias: `SteamStats_SetAchievement`

## Open Questions

1. The engine-facing wrappers at `sub_4e2770`, `sub_4e2860`, `sub_4e28c0`, and `sub_4e2920` are structurally clear but still need one more ownership pass before I promote final public names.
2. `sub_467bb0` clearly tears down pending stats/event state plus the report-recipient tree, but I want one more pass on `data_e30370` before naming that cleanup helper.
3. The `data_12d2670` bridge from Round 02 still has stable structure but weak semantics; this round did not materially improve those slot names.
