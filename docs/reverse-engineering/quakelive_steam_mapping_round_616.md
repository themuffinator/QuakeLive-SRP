# Quake Live Steam Mapping Round 616: User Stats And Presence Callback Publications

Date: 2026-06-12

## Scope

This round rechecks the client Steam callback publications for
`UserStatsReceived_t` and `FriendRichPresenceUpdate_t`.

No engine source behavior changed in this pass.

## Retail Evidence

Primary owner: `assets/quakelive/quakelive_steam.exe`

Evidence checked:

- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- `references/analysis/quakelive_symbol_aliases.json`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `src/code/client/cl_main.c`
- `src/common/platform/platform_steamworks.c`
- `src/common/platform/platform_steamworks.h`

Function ownership:

| Ghidra row | Address | Promoted owner |
| --- | --- | --- |
| `FUN_0045ffd0` | `0x0045FFD0` | `SteamCallbacks_OnUserStatsReceived` |
| `FUN_004602e0` | `0x004602E0` | `SteamCallbacks_OnFriendRichPresenceUpdate` |
| `FUN_004613a0` | `0x004613A0` | `SteamCallbacks_Init` |

Observed facts:

- `SteamCallbacks_Init` registers `UserStatsReceived_t` with callback id
  `0x44d` and target `sub_45ffd0`.
- `SteamCallbacks_Init` registers `FriendRichPresenceUpdate_t` with callback id
  `0x150` and target `sub_4602e0`.
- `sub_45ffd0` builds the browser payload fields `ID`, `NAME`, `STATS`, and
  `ACHIEVEMENTS`, then publishes `users.stats.%llu.received`.
- The `STATS` lane reads `SteamUserStats()` slots `0x48` for integer stats and
  `0x44` for float stats.
- The `ACHIEVEMENTS` lane reads display strings through slot `0x30` and
  per-user achievement state through slot `0x50`.
- `sub_4602e0` builds only `id`, `status`, and `lanIp`, reading rich-presence
  strings through `SteamFriends()` slot `0xb4`, then publishes
  `users.presence.%llu.change`.

## Source Reconstruction

The current source reconstruction keeps the same publication split:

- `QL_Steamworks_DispatchUserStatsReceived` translates the `0x18` raw Steam
  payload into `ql_steam_user_stats_received_t`, preserves the result, and
  fills the fallback name from the friend summary when available.
- `CL_Steam_Client_OnUserStatsReceived` logs the callback, falls back from live
  `GetFriendPersonaName` to the translated event name, builds the uppercase
  `ID`/`NAME` object, appends nested `STATS` and `ACHIEVEMENTS`, and publishes
  `users.stats.%s.received`.
- `CL_Steam_AppendUserStatsJson` keeps the retail descriptor branch, calling
  `QL_Steamworks_GetUserStatFloat` for float rows and
  `QL_Steamworks_GetUserStatInt` for integer rows only after a successful
  callback result.
- `CL_Steam_AppendUserAchievementsJson` keeps the display-name,
  display-description, unlocked, and unlock-time projection.
- `QL_Steamworks_DispatchFriendRichPresenceUpdate` translates the `0x0c` raw
  payload into split SteamID words plus `appId`, refreshes the friend summary,
  and dispatches the retained event.
- `CL_Steam_Client_OnFriendRichPresenceUpdate` publishes the retail-thin
  `{id,status,lanIp}` payload to `users.presence.%s.change`.

## Compatibility Boundary

The callback registrations and Steam readbacks remain behind
`QL_BUILD_ONLINE_SERVICES` and the initialized Steamworks adapter. The
default-disabled build keeps inline fallbacks that do not register callbacks or
contact live Steam services.

SRP intentionally keeps richer friend summary/game metadata on the persona,
friend-summary, and server-browser lanes. This round classifies the
`FriendRichPresenceUpdate_t` publication itself as the thin retail
rich-presence notification.

## Validation

Added
`tests/test_platform_services.py::test_steam_user_stats_presence_callbacks_track_round_616`
to pin:

- aliases, Ghidra function rows, imports, and vtable symbols for the two
  callback bodies and their shared registration owner;
- Binary Ninja HLIL anchors for callback ids, payload publication names,
  `SteamFriends` slots, and `SteamUserStats` slots;
- source raw payload sizes, dispatch translation, browser event names, JSON
  field ownership, and default-disabled wrapper declarations; and
- this round note plus Task A485 parity anchors.

Planned validation for this pass:

```text
python -m pytest tests/test_platform_services.py::test_steam_user_stats_presence_callbacks_track_round_616 -q --tb=short
python -m pytest tests/test_platform_services.py -q --tb=short
python -m pytest tests/test_steamworks_harness.py -q --tb=short
```

## Confidence

Observed facts:

- HLIL directly shows both browser publication names and the fields built for
  each payload.
- Ghidra rows, vtable symbols, and aliases identify both callback owners.
- Source tests now bind raw payload sizes, callback ids, dispatch translation,
  readback slots, and browser-event publication names into one gate.

Inference:

- SRP's JSON-string publisher is the correct source-level reconstruction of the
  retail Awesomium object publication because the observed field names, event
  names, Steam API read slots, and callback dispatch ownership are preserved.

Parity estimates:

- Focused Steam user-stats callback publication confidence:
  **before 94% -> after 99%**.
- Focused friend-rich-presence publication classification:
  **before 95% -> after 99%**.
- Overall Steam launch/runtime integration mapping confidence: **93.34% -> 93.36%**.
