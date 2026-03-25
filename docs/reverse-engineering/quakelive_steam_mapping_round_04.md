# Quake Live Steam Host Mapping Round 04

## Scope

This round closes a smaller but important wrapper layer that sat between the already-mapped Steam callback objects and the rest of the engine:

1. client-side Steam convenience helpers for persona name, country, and stats-clear control
2. Steam game-server packet and identity wrappers that were still only bounded in Round 01
3. the server-facing client Steam/auth/stat helper suite around `sub_4e2710` through `sub_4e2920`
4. the remaining global cleanup helper for pending stats-summary state

As in the earlier rounds, the evidence chain is built from:

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- `references/hlil/quakelive/quakelive_steam.exe/`

## Client Steam Convenience Helpers

These are small wrappers, but they define concrete host behavior that the browser/UI layer and local player state already rely on.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_460520` (`0x00460520`) | `SteamCmd_ClearStats_f` | Observed | Registered as `stats_clear` during client init and calls the `SteamUserStats` clear/reset slot with `1`. |
| `sub_460610` (`0x00460610`) | `SteamClient_SyncPersonaNameCvar` | Observed | Sets the `name` cvar from `SteamFriends()->GetPersonaName()` with `"anon"` fallback; client init calls it once and `sub_460800` calls it again when the local persona state changes. |
| `sub_460690` (`0x00460690`) | `SteamUtils_GetIPCountry` | Observed | Returns `0` until the client Steam API is initialized, otherwise jumps directly to the `SteamUtils` country-string slot; client init uses it to seed the `country` cvar when that cvar is empty. |

Two notes from this block:

- `SteamClient_SyncPersonaNameCvar` makes the Steam persona name the owning source for the player's local `name` cvar outside build harnesses.
- `SteamUtils_GetIPCountry` is not just a passive wrapper; the host uses it during bootstrap to populate `country` automatically.

## Steam Game-Server Packet And Identity Wrappers

Round 01 left part of this layer as lower-confidence helpers. The surrounding call sites are now strong enough to promote several of them.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_465d50` (`0x00465d50`) | `SteamServer_HandleIncomingPacket` | Observed | Rebuilds source IP/port from the packet address block and feeds the packet buffer plus source endpoint into the Steam game-server interface; both client and dedicated packet-event paths use it as the Steam connectionless packet handler. |
| `sub_465db0` (`0x00465db0`) | `SteamServer_EnableHeartbeats` | Observed | Toggles the Steam game-server heartbeat/advertise slot based on a boolean and stores the current timestamp in `data_e30348`; server startup passes `sv_master != 0`, while server shutdown passes `0`. |
| `sub_465df0` (`0x00465df0`) | `SteamServer_GetSteamID` | Observed | Returns the current game-server `CSteamID` pair through the Steam game-server interface; the server-client allocation path stores the returned low/high halves into the client SteamID fields. |
| `sub_465e80` (`0x00465e80`) | `SteamServer_GetPublicIP` | Observed | Direct wrapper around the Steam game-server public-IP slot; `sub_4f38f0` uses it when publishing `game.start` for the dedicated/public-server path. |

This also resolves one of the remaining bounded notes from Round 01:

- `sub_465db0` is no longer just an advertise-looking helper. The startup/shutdown call pattern makes the heartbeat/advertise role stable enough to name.

## Server-Facing Client Steam Helpers

The wrapper cluster at `sub_4e2710` through `sub_4e2920` is now stable enough to name. These functions operate directly on the live server client array at `data_13337ac` and the active client count at `data_13e17ec`.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4e2710` (`0x004e2710`) | `SV_ClientGetSteamID` | Observed | For a valid client slot, returns the stored SteamID when the user's `characterfile` key is empty; bot-style clients with a `characterfile` return `0`. |
| `sub_4e2770` (`0x004e2770`) | `SV_ClientAddSteamStat` | Observed | Validates the client slot and skips flagged bot/non-live clients, then forwards `(clientSteamID, statIndex, delta)` into `SteamStats_AddFieldValue`. |
| `sub_4e2860` (`0x004e2860`) | `SV_ClientUnlockSteamAchievement` | Observed | Same client validation path as `sub_4e2770`, then forwards the client SteamID plus achievement index into `SteamStats_UnlockAchievement`. |
| `sub_4e28c0` (`0x004e28c0`) | `SV_ClientHasSteamAchievement` | Observed | Same client validation path as the two wrappers above, then queries `SteamStats_HasAchievement`. |
| `sub_4e2920` (`0x004e2920`) | `SV_ClientBeginSteamAuthSession` | Observed | For valid non-bypass clients, finds the matching challenge/auth record, calls `SteamServer_BeginAuthSession`, and on success creates the matching per-player `idSteamStats` session with `SteamStats_CreatePlayerSession`. |

### Practical reconstruction result

This cluster makes the server-side ownership boundary much clearer:

- `sub_467d40`, `sub_467e00`, and `sub_467f70` are the Steam stats core
- `sub_4e2770`, `sub_4e2860`, and `sub_4e28c0` are the server-client export wrappers that feed those core helpers
- `sub_4e2920` is the bridge from client auth/challenge state into both Steam auth-session tracking and per-player stats-session creation

## Pending Summary Cleanup

The last still-unnamed helper in the match-summary path is now constrained enough to promote.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_467bb0` (`0x00467bb0`) | `SteamStats_ClearPendingSummaryState` | Observed | Clears `data_e303a0` and `data_e30380`, then clears the `data_e30370` recipient tree; process shutdown calls it directly, and its behavior mirrors the post-broadcast cleanup already visible in `sub_468ee0`. |

That name is intentionally behavioral rather than lifecycle-specific. The helper is used from shutdown, but its body is a pure reset of the pending summary/report state.

## New High-Confidence Aliases Added This Round

- client helpers:
  - `sub_460520`
  - `sub_460610`
  - `sub_460690`
- game-server wrappers:
  - `sub_465d50`
  - `sub_465db0`
  - `sub_465df0`
  - `sub_465e80`
- server-facing client wrappers:
  - `sub_4e2710`
  - `sub_4e2770`
  - `sub_4e2860`
  - `sub_4e28c0`
  - `sub_4e2920`
- summary cleanup:
  - `sub_467bb0`

## Open Questions

1. `sub_460590` and its thin wrapper at `sub_4bf2e0` are clearly a SteamApps query path, but I did not promote a final semantic name without a stronger call-site anchor.
2. `sub_4e2620` and `sub_4e2640` still look like engine-facing container front ends for the summary/report pipeline, but I want one more pass on the surrounding container helpers before naming them.
3. `sub_465a60` remains bounded as the Steam game-server rules/config batch sender, but this round did not add enough new evidence to make the exact API-facing name stable.
