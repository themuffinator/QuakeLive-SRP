# Quake Live Steam Mapping Round 429

Date: 2026-06-08

## Scope

This round reconstructs the Steam callback object ABI used by the client
launch/runtime callback bundle. The focus is the `CCallbackBase` vtable slot
order and the split between normal callbacks registered through
`SteamAPI_RegisterCallback` and the `SteamUGCQueryCompleted_t` call-result
registered through `SteamAPI_RegisterCallResult`.

## Evidence

- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt` lists
  `SteamAPI_RegisterCallback`, `SteamAPI_RegisterCallResult`,
  `SteamAPI_UnregisterCallback`, `SteamAPI_UnregisterCallResult`, and
  `SteamAPI_RunCallbacks`.
- `references/analysis/quakelive_symbol_aliases.json` maps `sub_4613A0` to
  `SteamCallbacks_Init` and `sub_461D40` to `SteamClient_Frame`.
- Binary Ninja HLIL for `sub_4613A0` initializes a
  `CCallResult<class SteamCallbacks, struct SteamUGCQueryCompleted_t>` owner
  with callback id `0xd49`, then registers the normal client callback objects:
  - `GameRichPresenceJoinRequested_t` at `0x151`
  - `UserStatsReceived_t` at `0x44d`
  - `PersonaStateChange_t` at `0x130`
  - `P2PSessionRequest_t` at `0x4b2`
  - `GameServerChangeRequested_t` at `0x14c`
  - `FriendRichPresenceUpdate_t` at `0x150`
- Binary Ninja HLIL for `sub_461D40` calls `SteamAPI_RunCallbacks()` before
  the retained voice and P2P/stat packet lanes.
- The local Steamworks harness already dispatches `CCallbackBase` objects as
  `Run`, `RunCallResult`, then `GetCallbackSizeBytes`, matching the Steam
  callback ABI needed by the runtime dispatcher.

## Source Reconstruction

- Reordered `ql_steam_callback_vtable_t` in `platform_steamworks.c` to
  `run`, `runCallResult`, `getSize`.
- Reordered the shared `ql_steam_callback_vtable` initializer to place
  `QL_Steamworks_CallbackRun` in the first slot and
  `QL_Steamworks_CallbackRunCallResult` in the second slot.
- Left `UGCQueryCompleted_t` as a prepared-but-not-`RegisterCallback` object
  inside `QL_Steamworks_RegisterClientCallbacks`; it is bound only through
  `QL_Steamworks_BindUGCQueryCallResult()`, preserving the retail call-result
  split.
- Added a parity gate that pins both the callback-vtable field order and
  initializer order, in addition to the existing callback-id coverage.

## Deferred Notes

- The source still uses a compact C callback object instead of reconstructing
  the exact C++ `CCallback`/`CCallResult` class layout. That remains an
  intentional compatibility abstraction as long as the exposed ABI slots,
  callback ids, payload sizes, and register/unregister lanes match the retail
  runtime behavior.
- This round does not enable live online services by default; it only fixes the
  opted-in Steamworks callback ABI when `QL_BUILD_ONLINE_SERVICES` and
  `QL_BUILD_STEAMWORKS` are enabled.

## Parity

Focused Steam callback ABI confidence moves from 74% to 93%.
The broader Steam launch/runtime integration slice moves from 80% to 82%.
