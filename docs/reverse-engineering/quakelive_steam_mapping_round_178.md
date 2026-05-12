# quakelive_steam.exe Mapping Round 178

Date: 2026-04-28

Scope: source-backed reconstruction of the retained Steam lobby enter/leave
browser-event lane for `quakelive_steam.exe`. This pass leaves the current
alias corpus untouched while closing the next clear `src/code` ownership gap
around `LobbyEnter_t`, the current-lobby leave handoff, and the shared
Steamworks wrapper surface those client owners consume.

## Summary

This was a source-only pass. No new alias rows were added, but the writable
client source now reconstructs substantially more of the retail Steam lobby
callback behavior instead of stopping at the earlier thin compatibility
payload.

The reconstruction landed:

- retained `lobby.%s.left` ownership in `src/code/client/cl_main.c` through
  `CL_Steam_LeaveCurrentLobby()`
- the retail lobby-enter response-message table in
  `CL_Steam_GetLobbyEnterResponseMessage()`
- the richer success payload in `CL_Steam_Lobby_OnLobbyEnter()`:
  `id`, `is_owner`, `owner`, `lobbydata`, `num_players`, `max_players`, and
  the keyed `players` object
- the retail-style error payload in `CL_Steam_Lobby_OnLobbyEnter()`:
  `{"code":...,"id":"...","message":"..."}`
- shared Steamworks lobby/friends accessors in
  `src/common/platform/platform_steamworks.c` and
  `src/common/platform/platform_steamworks.h` for lobby owner, metadata,
  member count, member limit, member enumeration, and direct persona-name
  lookup

Alias coverage therefore remains unchanged from rounds 175 through 177:

- `2038` raw alias entries
- `1970` strict Ghidra address-backed aliases
- `35.995%` strict Ghidra address-backed coverage of `5473` functions

## Source Reconstruction Notes

- Retail `sub_464D90` owns more than the older retained callback surface. The
  success path first leaves any currently retained lobby via `sub_4649E0()`,
  then republishes the new lobby using a richer object that includes the
  lobby owner, full lobby key/value metadata, the current player count, the
  member limit, and a keyed player list.
- `CL_Steam_LeaveCurrentLobby()` now mirrors the observed `sub_4649E0()`
  payload owner:
  - calls `QL_Steamworks_LeaveLobby( low, high )`
  - publishes `lobby.%s.left`
  - sends the exact retained payload shape `{"id":"%s"}`
  - clears the retained current-lobby identity afterward
- `CL_Steam_Lobby_OnLobbyEnter()` now mirrors the retail success-path shape
  instead of the earlier compatibility payload that only forwarded
  `permissions`, `locked`, and `response`.
- The new shared Steamworks accessors map directly to the observed retail
  matchmaking/friends slots:
  - `0x8c / 4` for lobby owner
  - `0x54 / 4` and `0x58 / 4` for lobby metadata count and indexed lookup
  - `0x44 / 4`, `0x80 / 4`, and `0x48 / 4` for member count, member limit,
    and indexed member enumeration
  - `0x1c / 4` on `ISteamFriends` for direct persona-name lookup
- The error path now uses the exact retained message table recovered from the
  HLIL string block:
  - `OK`
  - `Lobby does not exist`
  - `Access denied`
  - `Lobby is full`
  - `Unexpected error`
  - `You are banned from this lobby`
  - `Cannot join as a limited user`
  - `Locked to a clan you are not in`
  - `You are banned from Steam Community`
  - `You have been blocked from joining by a member`
  - `Cannot join lobby with blocked member`
- I intentionally left the broader browser verb surface alone in this round.
  Retail `sub_4649E0()` is also reachable from the JS bridge dispatch table,
  but the current pass focuses on the directly observed callback owner and the
  shared wrapper surface it needed.

## Aliases Added

- none; this round consumed already-mapped owners in source

## Verification

Source validation:

- `python -m pytest tests/test_platform_services.py -q`
  passed (`73 passed`)
- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed; the alias corpus itself was not modified in this round
- `C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe src\code\quakelive_steam.vcxproj /p:Configuration=Debug /p:Platform=Win32 /p:WindowsTargetPlatformVersion=10.0.26100.0 /m`
  succeeded
- the current `Debug|Win32` build still reports the repo's existing warning
  set outside this pass (`CL_Workshop_FinalizeInstalledItem` and the
  longstanding `LNK4098` CRT warning in this build configuration), but this
  round did not add new build failures
- `git diff --check` only reported the repo's existing LF->CRLF normalization
  warnings plus unrelated worktree edits left untouched
- no runtime launch was performed; this was static/source reconstruction work

Parity estimate after this pass remains unchanged:

- strict-retail Windows replacement target: `100%` before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

Because this was source-only, the largest-unaliased queue is unchanged from
the current round 175 alias baseline and the source-only rounds 176 through
177:

| Rank | Address | Raw symbol | Size |
| ---: | --- | --- | ---: |
| 1 | `0x004FC240` | `FUN_004fc240` | `537` |
| 2 | `0x0041AD70` | `FUN_0041ad70` | `517` |
| 3 | `0x004E6730` | `FUN_004e6730` | `504` |
| 4 | `0x004B4100` | `FUN_004b4100` | `502` |
| 5 | `0x00475200` | `FUN_00475200` | `497` |
| 6 | `0x0047DA20` | `FUN_0047da20` | `497` |
| 7 | `0x00409670` | `FUN_00409670` | `496` |
| 8 | `0x004B3672` | `FUN_004b3672` | `495` |
| 9 | `0x0041C400` | `FUN_0041c400` | `492` |
| 10 | `0x00414AC0` | `FUN_00414ac0` | `490` |

The next mapping-focused pass can still return directly to the
`0x004FC240` / `0x0041AD70` / `0x004E6730` queue head now that the richer
Steam lobby callback/source exactness gap is no longer competing with it.
