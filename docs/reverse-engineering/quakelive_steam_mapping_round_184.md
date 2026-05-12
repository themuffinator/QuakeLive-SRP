# Quake Live Steam Mapping Round 184

## Scope

This round is source-only and closes the next stable Steam social/browser
payload seam in `src/` without changing the host alias corpus.

The target gap was the retained friend-summary export family shared by the web
host browser list and the Steam social callback lane:

- `GetFriendList` in `cl_cgame.c` still emitted an over-specific compatibility
  object with `game.id`, `serverIp`, `queryPort`, and `gameServer`
- `CL_Steam_FormatFriendSummaryJson(...)` in `cl_main.c` still emitted a
  different flat payload shape for persona and presence callbacks
- retail `quakelive_steam.exe` uses a shared friend summary vocabulary with a
  nested `game` object and exact keys such as `appid`, `ip`, `port`, and
  lowercase `queryport`

Primary evidence stayed inside the committed retail corpus and reconstructed
source tree:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`
- `src/code/client/cl_cgame.c`
- `src/code/client/cl_main.c`
- `src/common/platform/platform_steamworks.c`
- `src/common/platform/platform_steamworks.h`

## Reconstructed Source Closures

### Steam friend summaries now retain the retail app-id owner

`QL_Steamworks_GetFriendSummary(...)` already mirrored the retained
`GetFriendGamePlayed` lane, but it still threw away one concrete retail field:
the app id packed into the game-info record.

This round adds `appId` to `ql_steam_friend_summary_t` and now fills it from
the lower 24 bits of the retained `gameId` payload before the existing
`playingQuake` check runs.

That removes a source-side re-derivation gap and gives both the browser list
and the callback lane the same explicit retail app-id owner.

### The shared friend-summary formatter now matches the retail nested game shape

`CL_Steam_FormatFriendSummaryJson(...)` previously emitted a flatter
compatibility object:

- top-level `game` as a numeric/string id
- top-level `lobby`
- top-level `ip`, `port`, `queryport`
- top-level `server`

The retail callback blocks do not publish that shape. They carry a nested
`game` object and the exact retained keys:

- `lobby`
- `appid`
- `ip`
- `port`
- `queryport`

This round restores that vocabulary in source through a dedicated
`CL_Steam_FormatFriendGameJson(...)` helper and routes
`CL_Steam_FormatFriendSummaryJson(...)` through it, so the persona and rich
presence callback payloads now follow the retail structure instead of the older
compatibility-only flat summary.

### `GetFriendList` now reuses the same retained social payload owner

`CL_WebHost_BuildFriendListJson(...)` in `cl_cgame.c` no longer hand-builds a
second, divergent friend JSON shape.

Instead, it now reuses `CL_Steam_FormatFriendSummaryJson(...)` directly. The
useful closure is that the browser list and the callback lane no longer drift
apart on key names or payload depth:

- the old `game.id` / `serverIp` / `queryPort` / `gameServer` lane is gone
- the web-host export now follows the same retained nested `game` shape as the
  Steam callback path

That is a cleaner source reconstruction than keeping two parallel summaries and
trying to remember to update both whenever the retail evidence changes.

## Verification

Static/source verification only:

- `python -m pytest tests/test_platform_services.py tests/test_steamworks_harness.py -q`
- `MSBuild` of `Debug|Win32` using
  `WindowsTargetPlatformVersion=10.0.26100.0`
- `git diff --check`

The updated tests pin:

- the retained `appId` owner inside `QL_Steamworks_GetFriendSummary(...)`
- the nested `game` formatter shape with `appid`, `ip`, `port`, and
  lowercase `queryport`
- reuse of `CL_Steam_FormatFriendSummaryJson(...)` inside
  `CL_WebHost_BuildFriendListJson(...)`
- the unchanged persona and rich-presence callback owners that continue to
  publish `users.persona.%s.change` and `users.presence.%s.change`

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
