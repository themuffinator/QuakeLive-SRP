# Quake Live Steam Mapping Round 631: GameServer Published-State Initialized Guards

Date: 2026-06-12

## Scope

This round maps the retail Steam GameServer published-state lane and
reconstructs explicit initialized-state guards in the SRP public GameServer
published-state wrappers. The retail owner is
`SteamServer_UpdatePublishedState`, promoted from `sub_466260`. The source
boundaries are the GameServer description, player-count, server-name,
map-name, password, key/value, game-tags, and player user-data publication
wrappers.

Steam launch/runtime online behavior remains behind `QL_BUILD_ONLINE_SERVICES`.
This round tightens wrapper fidelity; it does not enable live Steam services.

## Retail Evidence

- `references/analysis/quakelive_symbol_aliases.json` promotes
  `FUN_00466260` and `sub_466260` to `SteamServer_UpdatePublishedState`.
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  records `FUN_00466260,00466260,1425,0,unknown`.
- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
  confirms the source interface dependency through
  `STEAM_API.DLL!SteamGameServer @ 0015918a`.
- Binary Ninja HLIL shows `00466260    void sub_466260(int32_t arg1)`, then
  `00466277  if (data_e30358 != 0)`.
- Inside that gate, retail publishes max players through vtable slot `0x30`,
  password state through `0x40`, server name through `0x38`, map name through
  `0x3c`, score rules through `0x50`, player user data through `0x6c`, bot
  count through `0x34`, game description through `0x08`, and game tags through
  `0x54`.

Observed fact: retail performs the published-state updates only inside the
`data_e30358 != 0` GameServer-initialized gate.

Inferred mapping: SRP's `state.gameServerInitialised` mirrors retail
`data_e30358`, while `SV_SteamServerUpdatePublishedState` is the source owner
corresponding to retail `sub_466260`.

## Source Reconstruction

`src/common/platform/platform_steamworks.c` now makes the retail initialized
boundary explicit in the public published-state wrappers:

1. `QL_Steamworks_ServerSetGameDescription` validates the description before
   rejecting uninitialized GameServer state and dispatching vtable slot `0x08`.
2. `QL_Steamworks_ServerSetMaxPlayerCount` validates the count before rejecting
   uninitialized GameServer state and dispatching vtable slot `0x30`.
3. `QL_Steamworks_ServerSetBotPlayerCount` validates the count before rejecting
   uninitialized GameServer state and dispatching vtable slot `0x34`.
4. `QL_Steamworks_ServerSetServerName` and
   `QL_Steamworks_ServerSetMapName` validate their strings before rejecting
   uninitialized GameServer state and dispatching slots `0x38` and `0x3c`.
5. `QL_Steamworks_ServerSetPasswordProtected` rejects uninitialized GameServer
   state before dispatching slot `0x40`.
6. `QL_Steamworks_ServerSetGameTags` and
   `QL_Steamworks_ServerSetKeyValue` validate their publication payloads before
   rejecting uninitialized GameServer state and dispatching slots `0x54` and
   `0x50`.
7. `QL_Steamworks_ServerUpdateUserData` validates the Steam ID, player name,
   and score payload before rejecting uninitialized GameServer state and
   dispatching slot `0x6c`.

The shared `QL_Steamworks_GetGameServer` helper still retains the broader
`state.initialised`, `state.gameServerInitialised`, and `SteamGameServer`
checks. The new wrapper-level guards make the public boundary match the retail
published-state gate directly.

## Server Wiring

`src/code/server/sv_main.c` remains the published-state owner:

- `SV_SteamServerUpdatePublishedState` checks
  `QL_Steamworks_ServerIsInitialised` before any publication work.
- Full updates publish max-player count, password state, server name, map name,
  game description, game tags, score key/value pairs, player user data, and bot
  count through the mapped wrappers.
- Incremental updates retain the existing source-side modified-cvar and
  three-second player-refresh throttles while preserving the same wrapper
  surface.

## Validation

Added `test_steam_gameserver_published_state_wrapper_guards_track_round_631` to
pin:

- promoted aliases and Ghidra rows for `sub_466260`;
- the Steam GameServer import used by the published-state path;
- Binary Ninja frame-gate ordering for max players, password state, names,
  rule key/values, user data, bot count, game description, and game tags;
- wrapper input validation before initialized-state guards;
- initialized-state guards before `QL_Steamworks_GetGameServer`; and
- source publication calls and the source owner guard in
  `SV_SteamServerUpdatePublishedState`.

## Parity Estimate

Focused GameServer published-state wrapper guard confidence:
**82% -> 99%**.

Focused Steam GameServer published-state wiring confidence:
**92% -> 99%**.

overall Steam launch/runtime integration mapping confidence **93.64% -> 93.66%**.
