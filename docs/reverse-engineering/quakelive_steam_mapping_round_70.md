# Quake Live Steam Host Mapping Round 70

## Scope

This round continues the writable `quakelive_steam.exe` host reconstruction
work after round 69, targeting the next bounded Steam client callback and
rich-presence seam that was already mapped in the committed HLIL notes but was
still missing from source.

The target slice is the retail rich-presence/connect handoff plus the shared
SteamFriends rich-presence setter bounded earlier in:

- Round 01: `SteamCallbacks_OnRichPresenceJoinRequested`,
  `SteamCallbacks_OnGameServerChangeRequested`, and `SteamClient_Init`
- Round 02: `QLWebView_PublishGameStart`

Primary evidence for this source-reconstruction pass:

- `docs/reverse-engineering/quakelive_steam_mapping_round_01.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_02.md`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `src/common/platform/platform_steamworks.c`
- `src/code/client/cl_main.c`

## Reconstructed Source Closures

### `sub_45FF50`: `SteamCallbacks_OnRichPresenceJoinRequested`

Observed retail facts from the HLIL and prior mapping notes:

1. The callback body is very small.
2. It forwards the callback-provided join payload directly into the immediate
   command execution path.
3. It does not synthesize a new `connect %s\n` string locally.

Writable source closure landed in this round:

- `cl_main.c` now exposes `CL_Steam_OnRichPresenceJoinRequested`.
- The helper routes the provided command string through a shared
  `CL_Steam_ExecuteImmediateCommand` helper, using `Cbuf_ExecuteText(
  EXEC_NOW, ... )` to mirror the retail immediate handoff path.

### `sub_45FF70`: `SteamCallbacks_OnGameServerChangeRequested`

Observed retail facts from the HLIL:

1. The callback walks the password field at offset `0x40` and only writes the
   `password` cvar when the supplied string is non-empty.
2. It then formats `connect %s\n` from the callback-provided server field.
3. The formatted command is also routed through the immediate command path.

Writable source closure landed in this round:

- `cl_main.c` now exposes `CL_Steam_OnGameServerChangeRequested`.
- The helper mirrors the password gate and writes `password` only when the
  supplied string is populated.
- The helper then routes `va( "connect %s\n", server )` through the same
  immediate command helper used by the rich-presence join path.

These helpers do not reconstruct the callback-object allocation or
registration yet. They close the client-owned behavior that those callbacks
dispatch into, which is the stable prerequisite for the later callback-bundle
reconstruction.

### `sub_461500`: `SteamClient_Init`

Observed retail facts from the HLIL and prior mapping notes:

1. After `SteamAPI_Init`, callback allocation, lobby bootstrap, and command
   registration, `SteamClient_Init` calls `SteamFriends()->vtable[0xAC]`.
2. The call writes rich presence key `status` with value `At the main menu`.

Writable source closure landed in this round:

- `platform_steamworks.h` / `platform_steamworks.c` now expose
  `QL_Steamworks_SetRichPresence`, pinned to `SteamFriends()->vtable[0xAC]`.
- `cl_main.c` now reconstructs `CL_Steam_SetMainMenuRichPresence`.
- `CL_Init` now seeds the retail `status = "At the main menu"` value during
  client bootstrap through the shared platform wrapper.

### `sub_4F38F0`: `QLWebView_PublishGameStart`

Observed retail fact retained from round 02:

1. The browser/game-start publisher also updates Steam rich presence to
   `Playing a match`.

Writable source result from this round:

- the shared `QL_Steamworks_SetRichPresence` wrapper now exists in source, so
  the later browser/game-start owner can call the mapped SteamFriends slot
  without needing to rediscover the platform-layer contract.

The browser/game-start publisher itself remains outside this round’s bounded
write scope.

## Verification

This round extends the Steamworks harness and static host parity assertions
with coverage for the new SteamFriends rich-presence slot plus the client-side
join/server-change handoff helpers.

Targeted result:

- `python -m pytest tests/test_steamworks_harness.py tests/test_platform_services.py tests/test_ui_menu_files.py -q`
- `56 passed`

The new assertions prove:

- the shared SteamFriends rich-presence wrapper now reaches the mapped
  `vtable[0xAC]` slot and preserves the `status = "At the main menu"` payload
- the client bootstrap now seeds the retail main-menu rich-presence state
- the reconstructed rich-presence join and server-change helpers now route
  through the retail immediate command path, preserving the password cvar gate
  on the server-change seam

## Completion Summary

No new alias rows were added in
`references/analysis/quakelive_symbol_aliases.json` this round; the mapping
work here was consumed as source reconstruction against already-promoted host
ownership.

Current global `quakelive_steam.exe` mapping coverage remains:

- raw alias entries: `944`
- address-backed aliases: `943`
- Ghidra function coverage: `17.230%` of `5473`

Source reconstruction improved the writable Task 21 host baseline by closing
another retail Steam callback/bootstrap gap: the rich-presence setter now
exists in the shared Steamworks layer, the retail main-menu status seed now
exists in client bootstrap, and the mapped rich-presence join and
game-server-change callback handoff logic now exists in writable client code
instead of remaining implicit only in the retail binary and mapping notes.
