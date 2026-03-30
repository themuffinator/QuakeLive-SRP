# Quake Live Steam Host Mapping Round 69

## Scope

This round continues the writable `quakelive_steam.exe` host reconstruction
work after round 68, targeting the next bounded Steam lobby/social seam that
was already mapped in the committed HLIL notes but still missing from source.

The target slice is the retail lobby bootstrap plus the adjacent matchmaking
and social wrapper surface bounded earlier in:

- Round 01: `SteamLobby_Init` and `SteamLobby_ConnectLobby_f`
- Round 07: `SteamLobby_CreateLobby`, `SteamLobby_JoinLobby`,
  `SteamLobby_ShowInviteOverlay`, `SteamLobby_SayLobby`, and the inlined
  `RequestUserStats` dispatcher method

Primary evidence for this source-reconstruction pass:

- `docs/reverse-engineering/quakelive_steam_mapping_round_01.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_07.md`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `src/common/platform/platform_steamworks.c`
- `src/code/client/cl_main.c`

## Reconstructed Source Closures

### `sub_465840`: `SteamLobby_Init`

Observed retail facts from the HLIL and prior mapping notes:

1. `SteamLobby_Init` registers cvar `lobby_autoconnect` with flag `0x100`.
2. It creates cvar `steam_maxLobbyClients` with default `"16"` and flag `1`.
3. It exposes the `connect_lobby` console command.

Writable source closure landed in this round:

- `cl_main.c` now registers `lobby_autoconnect` as `CVAR_TEMP`.
- `cl_main.c` now registers `steam_maxLobbyClients` as `CVAR_ARCHIVE` with the
  retail default `"16"`.
- `CL_Init` and `CL_Shutdown` now add and remove the `connect_lobby` command.

### `sub_464AA0`: `SteamLobby_ConnectLobby_f`

Observed retail facts from the HLIL:

1. The handler does not perform a larger control-flow dance.
2. It writes `Cmd_Argv(1)` directly into `lobby_autoconnect`.

Writable source closure landed in this round:

- `cl_main.c` now reconstructs `CL_Steam_ConnectLobby_f` with the same
  single-write behavior, closing the previously absent retail command seam.

### `sub_4649B0`, `sub_465630`, `sub_464BB0`, `sub_464AC0`, and `RequestUserStats`

Observed retail facts already bounded in Round 07:

1. `SteamLobby_CreateLobby` calls `SteamMatchmaking()->vtable[0x34]` with
   lobby type `2` and `steam_maxLobbyClients`.
2. `SteamLobby_JoinLobby` forwards the parsed 64-bit lobby identity into
   `SteamMatchmaking()->vtable[0x38]`.
3. `SteamLobby_ShowInviteOverlay` routes the current lobby identity through
   `SteamFriends()->vtable[0x84]`.
4. `SteamLobby_SayLobby` sends the message plus `strlen + 1` through
   `SteamMatchmaking()->vtable[0x68]`.
5. The inlined `RequestUserStats` dispatcher path calls
   `SteamUserStats()->vtable[0x40]`.

Writable source closure landed in this round:

- `platform_steamworks.h` / `platform_steamworks.c` now expose shared wrapper
  helpers for `CreateLobby`, `JoinLobby`, `ShowInviteOverlay`, `SayLobby`, and
  `RequestUserStats`.
- The Steamworks harness now exercises those slots directly so the writable
  source keeps the mapped offsets and argument shapes pinned.

This does not reconstruct the full browser/JS dispatcher yet. It closes the
retail-owned host shim layer first, which is the stable prerequisite for the
later browser-facing caller paths.

## Verification

This round extends the Steamworks harness and static host parity assertions
with coverage for the new lobby bootstrap and matchmaking/social wrapper seam.

Targeted result:

- `python -m pytest tests/test_steamworks_harness.py tests/test_platform_services.py tests/test_ui_menu_files.py -q`
- `52 passed`

The new assertions prove:

- `connect_lobby` is now registered and mirrors the retail
  `lobby_autoconnect = Cmd_Argv(1)` write path
- the retail `lobby_autoconnect` and `steam_maxLobbyClients` cvars now exist
  with the mapped defaults and flag classes
- the platform Steamworks wrappers reach the mapped
  `SteamMatchmaking`, `SteamFriends`, and `SteamUserStats` vtable slots for
  create/join/chat/invite/user-stats flows

## Completion Summary

No new alias rows were added in `references/analysis/quakelive_symbol_aliases.json`
this round; the mapping work here was consumed as source reconstruction against
already-promoted host ownership.

Current global `quakelive_steam.exe` mapping coverage remains:

- raw alias entries: `944`
- address-backed aliases: `943`
- Ghidra function coverage: `17.230%` of `5473`

Source reconstruction improved the writable Task 21 host baseline by closing
another retail Steam lobby/bootstrap gap: the lobby bootstrap cvars and
`connect_lobby` command now exist in the client host, and the surrounding
Steam matchmaking/social wrapper layer is now present in shared source instead
of remaining implicit only in the retail binary and mapping notes.
