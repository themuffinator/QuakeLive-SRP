# Quake Live Steamworks Mapping Round 358

Date: 2026-06-06

Focus: Steam lobby callback bundle dispatch mapping and executable harness
coverage.

## Retail Evidence

- Owning binary: `assets/quakelive/quakelive_steam.exe`.
- Primary HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
  shows `sub_4656a0` constructing the `SteamLobbyCallbacks` callback bundle
  and assigning callback vtables for `LobbyCreated_t`, `LobbyEnter_t`,
  `LobbyChatUpdate_t`, `LobbyChatMsg_t`, `LobbyDataUpdate_t`,
  `LobbyGameCreated_t`, `LobbyKicked_t`, and
  `GameLobbyJoinRequested_t`.
- Structured companion evidence:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  contains the lobby callback owner rows from `FUN_00464720` through
  `FUN_004656a0`.
- Symbol/name support:
  `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
  has the corresponding imported `CCallback<class_SteamLobbyCallbacks,...>`
  vtable metadata at `0x00532e70`, `0x00532e80`, `0x00532e90`,
  `0x00532ea0`, `0x00532eb0`, `0x00532ec0`, `0x00532ed0`, and
  `0x00532ee0`.
- The existing Steamworks mapping report names `SteamLobbyCallbacks_Init`
  (`0x004656A0`) as the owner that registers the same eight lobby callback
  payload types.

## Observed Facts

The retail lobby callback owner is an eight-callback bundle, not a single
`LobbyEnter_t` path. The current source already mirrors that shape in
`QL_Steamworks_RegisterLobbyCallbacks` by preparing and registering these
callback IDs:

- `QL_STEAM_CALLBACK_LOBBY_CREATED` (`0x201`)
- `QL_STEAM_CALLBACK_LOBBY_ENTER` (`0x1f8`)
- `QL_STEAM_CALLBACK_LOBBY_CHAT_UPDATE` (`0x1fa`)
- `QL_STEAM_CALLBACK_LOBBY_CHAT_MESSAGE` (`0x1fb`)
- `QL_STEAM_CALLBACK_LOBBY_DATA_UPDATE` (`0x1f9`)
- `QL_STEAM_CALLBACK_LOBBY_GAME_CREATED` (`0x1fd`)
- `QL_STEAM_CALLBACK_LOBBY_KICKED` (`0x200`)
- `QL_STEAM_CALLBACK_GAME_LOBBY_JOIN_REQUESTED` (`0x14d`)

The existing harness registered the full callback bundle through the platform
layer, but only supplied a callback target and queue helper for `LobbyEnter_t`.
That meant the callback count could prove registration breadth, while the
runtime pump only proved one lobby payload projection.

## Source Reconstruction

- Added harness callback targets for `LobbyCreated_t`,
  `LobbyChatUpdate_t`, `LobbyChatMsg_t`, `LobbyDataUpdate_t`,
  `LobbyGameCreated_t`, `LobbyKicked_t`, and
  `GameLobbyJoinRequested_t`.
- Bound all eight lobby targets in `QLR_Steamworks_RegisterHarnessCallbacks`.
- Added raw-payload queue helpers for the seven previously unqueued lobby
  callbacks and switched the existing `LobbyEnter_t` queue helper to the named
  callback ID.
- Extended the ctypes callback-bundle test so every retained lobby callback
  payload crosses `QL_Steamworks_RunCallbacks`.
- Tightened static callback-bundle coverage so all eight lobby callback IDs,
  object preparations, and object registrations stay pinned.

## Inference Boundary

Confidence is high for the callback bundle membership because HLIL vtable
assignment, Ghidra imported symbols, and the existing mapping report agree on
the same eight callback payload types. This round does not claim live Steam
backend timing, lobby membership semantics, or web-menu event ordering beyond
the reconstructed callback-pump projection. Online-service behavior remains
bounded behind the opt-in Steamworks policy.

## Parity Estimate

- Focused lobby callback pump coverage:
  **before 58% -> after 96%**.
- Steam lobby callback registration and payload projection together:
  **before 90% -> after 98%**.
- Broader Steamworks parity remains approximately **99%**; this pass closes an
  executable-test gap in an already reconstructed callback registration
  surface without claiming live backend validation.
