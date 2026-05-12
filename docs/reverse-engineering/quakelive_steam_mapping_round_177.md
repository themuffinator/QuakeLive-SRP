# quakelive_steam.exe Mapping Round 177

Date: 2026-04-28

Scope: source-backed reconstruction of the retained client/browser `game.start`
publisher lane for `quakelive_steam.exe`. This pass keeps the round 175 alias
corpus and the round 176 advert-debug source work intact while closing the
next clean `src/code` ownership gap around `QLWebView_PublishGameStart`.

## Summary

This was a source-only pass. No new alias rows were added, but the writable
client source now reconstructs more of the retail `game.start` publication
lane instead of leaving it as the older stringified-address compatibility
shortcut.

The reconstruction landed:

- retail-style packed-IP `game.start` payload publication in
  `src/code/client/cl_main.c`
- the retained `status = "Playing a match"` write back under the
  `CL_WebView_PublishGameStart` owner instead of the earlier
  first-snapshot-only compromise in `cl_cgame.c`
- the connect-time resolved-address publication path in `CL_Connect_f`
- a small cross-platform `NET_GetLocalAddressIP(...)` seam in
  `qcommon.h`, `win_net.c`, `unix_net.c`, `null_net.c`, and `mac_net.c`
  so the LAN rich-presence branch can use a real cached local interface
  address

Alias coverage therefore remains unchanged from rounds 175 and 176:

- `2038` raw alias entries
- `1970` strict Ghidra address-backed aliases
- `35.995%` strict Ghidra address-backed coverage of `5473` functions

## Source Reconstruction Notes

- Retail `sub_4F38F0` has two observed owners:
  - a resolved-address caller that fires immediately after
    `cl_currentServerAddress` is updated
  - the first-snapshot / local-game caller that passes a null address blob
- The resolved-address lane is now restored directly in source:
  `CL_Connect_f()` still sets `cl_currentServerAddress`, and it now also
  publishes the packed-IP `game.start` payload through
  `CL_WebView_PublishGameStartForAddress( &clc.serverAddress )`.
- The payload shape is now aligned with the retail HLIL and the already
  reconstructed friend/lobby JSON lanes: `game.start` now publishes
  `{"ip":%u,"port":%u}` using the packed big-endian IPv4 word instead of the
  older stringified `NET_AdrToString(...)` fallback.
- The adjacent LAN rich-presence write is also restored. When the retained
  connection is loopback and the platform net layer can surface a cached local
  interface address, the source now writes `lanIp` as the retail decimal
  `"%lu:%u"` packed-IP/port pair before publishing the event.
- The exact retail null-address discriminator still lives behind an unresolved
  internal host state word (`data_13e1818 + 0x30` in the HLIL). Rather than
  forcing a brittle one-to-one guess, this pass uses the observable split that
  already exists in source:
  - loopback connection -> local interface IP when available
  - loopback fallback -> `QL_Steamworks_ServerGetPublicIP()`
  - non-loopback connection -> publish the resolved `netadr_t`
  This keeps the evidence trail explicit while still reconstructing the
  concrete packed-IP and LAN-presence behavior.

## Aliases Added

- none; this round consumed already-mapped owners in source

## Verification

Source validation:

- `python -m pytest tests/test_platform_services.py -q`
  passed (`73 passed`)
- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed; the alias corpus itself was not modified in this round
- `MSBuild.exe src\code\quakelive_steam.vcxproj /p:Configuration=Debug /p:Platform=Win32 /p:WindowsTargetPlatformVersion=10.0.26100.0 /m`
  succeeded using the local Visual Studio 2022 toolchain and the same SDK
  override used in recent source-backed rounds
- the current `Debug|Win32` build still reports the repo's pre-existing warning
  set outside this pass (`CL_Workshop_FinalizeInstalledItem`,
  `idZMQ_EnsureStatsPublisher`, `idZMQ_EnsureRconSocket`, and the longstanding
  `LNK4098` CRT warning), but this round did not add new build failures
- `git diff --check` only reported the repo's existing LF->CRLF normalization
  warnings
- no runtime launch was performed; this was static/source reconstruction work

Parity estimate after this pass remains unchanged:

- strict-retail Windows replacement target: `100%` before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

Because this was source-only, the largest-unaliased queue is unchanged from the
current round 175 alias baseline:

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

The next mapping-focused pass can return to the `0x004FC240` / `0x0041AD70` /
`0x004E6730` queue head now that the remaining high-signal `game.start`
source-exactness gap is no longer competing with it.
