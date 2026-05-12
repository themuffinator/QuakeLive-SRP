# Quake Live Steam Mapping Round 188

## Scope

This round is source-only and closes the retained Steam user-stats callback
payload lane in `src/` without changing the host alias corpus.

The target gap was the remaining mismatch between the retail
`SteamCallbacks_OnUserStatsReceived` callback and the checked-in client source:

- `CL_Steam_Client_OnUserStatsReceived(...)` still published the older thin
  compatibility payload with lowercase `id` / `name` plus `gameId` and
  `result`
- the source tree still lacked the client-side `SteamUserStats` read wrappers
  needed to reconstruct the retail `STATS` and `ACHIEVEMENTS` JSON objects
- the browser event payload cache was still sized for small status objects
  rather than the full retail stats payload

Primary evidence stayed inside the committed retail corpus and reconstructed
source tree:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `docs/reverse-engineering/quakelive_steam_mapping_round_01.md`
- `src/code/client/cl_main.c`
- `src/code/server/sv_client.c`
- `src/common/platform/platform_steamworks.c`
- `src/common/platform/platform_steamworks.h`
- `tests/test_platform_services.py`

## Reconstructed Source Closures

### The client callback now rebuilds the retained `users.stats` payload

Retail `sub_45FFD0` does not publish a minimal acknowledgement object. The
HLIL shows it building:

- top-level `ID`
- top-level `NAME`
- nested `STATS`
- nested `ACHIEVEMENTS`

This round reconstructs that ownership in `CL_Steam_Client_OnUserStatsReceived`
by:

- restoring the uppercase `ID` / `NAME` payload vocabulary
- rebuilding the retained Steam stat table in `CL_Steam_AppendUserStatsJson(...)`
- rebuilding the retained achievement metadata map in
  `CL_Steam_AppendUserAchievementsJson(...)`
- falling back to the callback-provided name only when the live
  `GetFriendPersonaName(...)` read does not return a usable value

The retail callback still publishes `users.stats.%llu.received`; only the JSON
shape changes here.

### The missing client-side SteamUserStats read wrappers now exist

The client source already had the request wrapper, but not the read-side
owners used by the retail callback body.

This round adds:

- `QL_Steamworks_GetUserStatInt(...)`
- `QL_Steamworks_GetUserAchievement(...)`
- `QL_Steamworks_GetAchievementDisplayAttribute(...)`

Those wrappers now own the retained SteamUserStats vtable slots:

- `0x48 / 4` for per-user integer stats
- `0x50 / 4` for per-user achievement + unlock-time reads
- `0x30 / 4` for achievement display strings

That gives the client callback a first-class source owner instead of forcing
the JSON lane to stay compatibility-only.

### The browser-event cache now accommodates the retained payload size

The earlier `2048`-byte event payload cache was sized for the smaller callback
objects reconstructed in rounds 178 through 187. The retained stats payload is
materially larger because it carries the whole stat map plus achievement
metadata.

This round raises `CL_STEAM_BROWSER_EVENT_PAYLOAD_LENGTH` to `16384` and
widens the internal JSON fragment scratch buffer so the reconstructed retail
payload can be built without truncating the longer achievement-description
fragments.

## Verification

Static/source verification only:

- `python -m pytest tests/test_platform_services.py tests/test_steamworks_harness.py -q`
- `MSBuild` of `Debug|Win32` using
  `WindowsTargetPlatformVersion=10.0.26100.0`
- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
- `git diff --check`

The updated tests pin:

- the new client-side SteamUserStats read wrappers and their exact vtable slots
- the widened callback payload budget
- the retained uppercase `ID` / `NAME` plus nested `STATS` /
  `ACHIEVEMENTS` payload shape
- reuse of the shared client stat and achievement tables inside the callback
  owner

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
