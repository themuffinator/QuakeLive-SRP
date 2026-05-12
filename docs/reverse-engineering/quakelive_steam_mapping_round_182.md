# Quake Live Steam Mapping Round 182

## Scope

This round is source-only and closes the remaining stable `qz_instance`
`Invite` seam in `src/` without changing the host alias corpus.

The previous browser rounds intentionally left this method alone because the
retail split was larger than a normal one-wrapper lobby command:

- round 179 rebuilt the stable lobby/social browser surface
- round 180 restored `OpenSteamOverlayURL` and `SetClipboardText`
- round 181 restored the retained server-browser request/detail/refresh lane
- `Invite` still remained deferred because retail routes it through two
  different Steam API paths depending on client state

Primary evidence stayed inside the committed retail corpus and reconstructed
source tree:

- `docs/reverse-engineering/quakelive_steam_mapping_round_07.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_179.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_181.md`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`
- `src/code/client/cl_cgame.c`
- `src/code/client/cl_main.c`
- `src/common/platform/platform_steamworks.c`
- `src/common/platform/platform_steamworks.h`

## Reconstructed Source Closures

### `qz_instance` now binds the retained `Invite` browser verb

`cl_cgame.c` already carried the retained numeric method ID
`CL_WEB_METHOD_INVITE = 26`, but the browser binding table and dispatcher did
not expose it into the live `qz_instance` surface.

This round restores both missing pieces:

- the `Invite` entry is now present in `cl_webMethodBindings`
- `QLJSHandler_OnMethodCall` now forwards it into a new source-owned
  `CL_Steam_Invite(...)` helper

That closes the last stable social/browser method that rounds 179 through 181
had intentionally deferred.

### `cl_main.c` now mirrors retail lobby-vs-direct invite ownership

The important control-flow anchor from the retail HLIL is that `Invite` does
not always mean the same Steam call:

- when the client is not in an active match, retail invites into the current
  lobby through `SteamMatchmaking()->vtable[0x40]`
- when the client is in `CA_ACTIVE`, retail builds a direct-game `+connect`
  payload and sends it through `SteamFriends()->vtable[0xC4]`

The new `CL_Steam_Invite(...)` reconstruction mirrors that split in source:

- `cls.state != CA_ACTIVE` routes through the cached current-lobby identity
- `cls.state == CA_ACTIVE` routes through a new direct-game connect-string
  helper

If neither a valid lobby nor a valid active-game connect target exists, the
source now declines the browser request explicitly rather than inventing a
fallback path.

### Direct-game invite payloads now use retail source-side address rules

The active-game branch is backed by a new
`CL_Steam_BuildInviteConnectString(...)` helper in `cl_main.c`.

It mirrors the retail address split recovered from the HLIL and Ghidra
decompile:

- if `sv_running` is false, invite the currently connected remote server with
  `+connect %s`
- if `sv_running` is true and `sv_serverType == 1`, use the local interface IP
  plus `net_port`
- otherwise use `QL_Steamworks_ServerGetPublicIP()` plus `net_port`

The hosted-server branch intentionally keeps the packed-integer retail shape
`+connect %lu:%s` rather than normalizing it into a dotted-quad string.

## Steam Wrapper Reconstruction

The retail `Invite` lane also depended on two Steam wrapper gaps that were not
yet source-backed in `platform_steamworks.c`.

This round adds both missing wrappers:

- `QL_Steamworks_InviteUserToLobby(...)`
  - `SteamMatchmaking()->vtable[0x40]`
  - split lobby ID plus split target user ID
- `QL_Steamworks_InviteUserToGame(...)`
  - `SteamFriends()->vtable[0xC4]`
  - split target user ID plus retained connect string

The null/offline inline stubs in `platform_steamworks.h` were updated as well,
so `QL_BUILD_ONLINE_SERVICES` stays bounded cleanly in non-Steam builds.

## Verification

Static/source verification only:

- `python -m pytest tests/test_platform_services.py tests/test_steamworks_harness.py -q`
- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
- `MSBuild` of `Debug|Win32` using
  `WindowsTargetPlatformVersion=10.0.26100.0`
- `git diff --check`

The updated tests pin:

- the `Invite` binding entry in `cl_webMethodBindings`
- the `QLJSHandler_OnMethodCall` dispatch case for method `26`
- the new `CL_Steam_Invite(...)` and
  `CL_Steam_BuildInviteConnectString(...)` source shape
- the new Steam wrapper slots `0x40` and `0xC4`
- harness-level wrapper behavior for lobby invites and direct-game invites

## Coverage Impact

This round is source-only. Host alias totals stay unchanged:

- raw aliases: `2038`
- strict Ghidra address-backed aliases: `1970`
- strict Ghidra address-backed coverage: `35.995%`

The largest-unaliased host queue is therefore unchanged as well:

1. `0x004FC240`
2. `0x0041AD70`
3. `0x004E6730`

## Parity Estimate

- strict-retail Windows target: `100% -> 100%`
- repo-wide reconstructed source base: `98% -> 98%`
