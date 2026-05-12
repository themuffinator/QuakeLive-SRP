# Quake Live Steam Mapping Round 181

## Scope

This round is source-only and closes the remaining stable `qz_instance`
server-browser method seam in `src/` without changing the host alias corpus.

The target gap was the broader browser/matchmaking block intentionally left
open at the end of round 180:

- round 179 rebuilt the stable lobby/social `qz_instance` dispatch surface
- round 180 restored `OpenSteamOverlayURL` and `SetClipboardText`
- the retained `RequestServers`, `RequestServerDetails`, `RefreshList`, and
  `NoOp` browser verbs were still absent from the live source bridge even
  though rounds 06 and 08 had already bounded their host ownership and event
  names

Primary evidence stayed inside the committed retail corpus and reconstructed
source tree:

- `docs/reverse-engineering/quakelive_steam_mapping_round_06.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_08.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_179.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_180.md`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `src/code/client/cl_cgame.c`
- `src/code/client/cl_main.c`
- `src/code/client/cl_ui.c`

## Reconstructed Source Closures

### `qz_instance` now exports the retained server-browser methods

`cl_cgame.c` now binds the remaining stable browser verbs back into the live
`qz_instance` surface with their retail numeric IDs:

- `RequestServers` (`14`)
- `RequestServerDetails` (`15`)
- `RefreshList` (`16`)
- `NoOp` (`30`)

`QLJSHandler_OnMethodCall` now dispatches them through source-owned client
helpers instead of leaving them absent from the browser method table:

- `RequestServers` forwards to `CL_Steam_RequestServers`
- `RequestServerDetails` forwards to `CL_Steam_RequestServerDetails`
- `RefreshList` forwards to `CL_Steam_RefreshServerList`
- `NoOp` now returns success explicitly

`Invite` stays deferred. The retained lobby-vs-direct-game split is still a
larger standalone seam than this browser pass.

### `cl_main.c` now owns a compatibility server-browser lane

This round reconstructs a client-owned browser state lane in `cl_main.c`
instead of pretending the Steam matchmaking-servers backend is already rebuilt
in `src/`.

The useful closure is that the source now has explicit owners for the retained
browser refresh/detail lifecycle:

- `CL_Steam_RequestServers`
- `CL_Steam_RequestServerDetails`
- `CL_Steam_RefreshServerList`
- `CL_SteamBrowser_Frame`

The retained request modes are mapped onto the closest source-owned browser
lists:

- mode `0` -> global/internet list
- mode `1` -> local/LAN list
- mode `3` -> favorites list

The retail friends/history lanes (`2` and `4`) stay as bounded compatibility
fallbacks on the nearest source browser lists until the deeper Steam server
browser is reconstructed.

### Refresh events now ride the existing LAN/global ping path

The new browser lane intentionally reuses the source tree’s existing
`localservers`, `globalservers`, favorites, and ping refresh plumbing instead
of introducing a fake Steam callback layer.

`CL_Steam_RequestServers` now:

- marks the chosen source visible
- resets the stored pings
- publishes `servers.refresh.start`
- kicks the appropriate source command or compatibility source

`CL_SteamBrowser_Frame` then mirrors the old UI refresh ownership pattern by
driving `CL_UpdateVisiblePings_f(...)` until the refresh settles, after which
it publishes `servers.refresh.end`.

### Server list/detail/rules/player events are now source-backed

The retained browser event names from rounds 06 and 08 are now published from
the live source owners:

- `CL_ServerInfoPacket` now promotes pinged `getinfo` replies into
  `servers.details.%u_%u.response`
- `CL_ServerStatusResponse` now promotes `getstatus` replies into:
  - `servers.details.%u_%u.response`
  - `servers.rules.%s.response`
  - `servers.rules.%s.end`
  - `servers.players.%s.response`
  - `servers.players.%s.end`

This is intentionally a compatibility reconstruction, not a claim that the
source already has the exact retained Steam backend. The event names and
payload ownership now line up with retail, while the data comes from the
existing source browser/status systems:

- `getinfo` drives list refresh payloads
- `getstatus` drives the richer detail/rules/player payloads
- fields such as `sv_keywords` and `g_needpass` are recovered from the source
  serverinfo/status strings where available

## Verification

Static/source verification only:

- `python -m pytest tests/test_platform_services.py tests/test_steamworks_harness.py -q`
- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
- `MSBuild` of `Debug|Win32` using
  `WindowsTargetPlatformVersion=10.0.26100.0`
- `git diff --check`

The updated tests pin:

- the retail `qz_instance` method IDs and binding entries for
  `RequestServers`, `RequestServerDetails`, `RefreshList`, and `NoOp`
- the new browser dispatcher cases in `QLJSHandler_OnMethodCall`
- the client shim prototypes in `client.h`
- the new `cl_main.c` request-mode mapping and refresh/detail helpers
- the event publication bridge from `CL_ServerInfoPacket` and
  `CL_ServerStatusResponse`

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
