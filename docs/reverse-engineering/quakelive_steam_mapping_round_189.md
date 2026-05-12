# Quake Live Steam Mapping Round 189

## Scope

This round is source-only and closes the retained Steam UGC browser query lane
in `src/` without changing the host alias corpus.

The target gap was the remaining mismatch between the retail
`SteamClient_RequestUGCQuery` / `SteamCallbacks_OnUGCQueryCompleted` pair and
the checked-in compatibility source:

- `GetAllUGC` in `cl_cgame.c` still used the older synchronous subscribed-item
  export helper instead of the retained async SteamUGC query path
- `CL_Steam_Client_OnUGCQueryCompleted(...)` still published a thin query
  metadata object rather than rebuilding the retained workshop row array
- the source tree still lacked the client-side SteamUGC query wrappers needed
  to own the retail request / read / release surface directly

Primary evidence stayed inside the committed retail corpus and reconstructed
source tree, with the Steamworks API reference used as a secondary slot/struct
sanity check:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `src/code/client/cl_cgame.c`
- `src/code/client/cl_main.c`
- `src/common/platform/platform_steamworks.c`
- `src/common/platform/platform_steamworks.h`
- `tests/test_platform_services.py`
- [Steamworks ISteamUGC reference](https://partner.steamgames.com/doc/api/isteamugc?language=english)

## Reconstructed Source Closures

### `GetAllUGC` now mirrors the retained async request handoff

Retail does not enumerate the local subscribed-item cache from the browser
method owner. The `GetAllUGC` method validates that a page argument exists,
converts it to an integer, and forwards it into the shared SteamUGC query
request owner.

This round reconstructs that behavior by:

- removing the older `CL_WebHost_BuildUGCResultsJson(...)` compatibility lane
- requiring one page argument in the `CL_WEB_METHOD_GET_ALL_UGC` dispatch case
- forwarding the parsed page into the new `CL_Steam_RequestAllUGC(...)` owner

That moves the query back to the same split the retail executable uses:
browser bridge on request, callback owner on result publication.

### The missing SteamUGC query wrappers now exist in source

The source tree already owned workshop download wrappers, but not the query
request / result / preview-url / release seam used by the retained browser UGC
surface.

This round adds:

- `QL_Steamworks_RequestAllUGCQuery(...)`
- `QL_Steamworks_GetQueryUGCResult(...)`
- `QL_Steamworks_GetQueryUGCPreviewURL(...)`
- `QL_Steamworks_ReleaseQueryUGCRequest(...)`

Those wrappers now own the retained SteamUGC vtable slots observed in HLIL:

- `0x04 / 4` for `CreateQueryAllUGCRequest`
- `0x0c / 4` for `SendQueryUGCRequest`
- `0x10 / 4` for `GetQueryUGCResult`
- `0x14 / 4` for `GetQueryUGCPreviewURL`
- `0x34 / 4` for `ReleaseQueryUGCRequest`

The result wrapper also reconstructs the retained local `SteamUGCDetails_t`
read surface by copying the published-file id plus the title/description
strings out of the callback-owned details buffer.

### The callback now rebuilds the retained workshop results payload

Retail `SteamCallbacks_OnUGCQueryCompleted` does not publish a thin status
object. On success it walks the returned rows, reads the title/description/id
and preview URL for each item, builds the `web.ugc.results` JSON array, and
then releases the query handle. On failure it still releases the query handle
and publishes `web.ugc.failed` with no payload.

This round reconstructs that ownership in
`CL_Steam_Client_OnUGCQueryCompleted(...)` by:

- adding `CL_Steam_BuildUGCQueryResultsJson(...)`
- rebuilding each row as
  `{"title":"...","description":"...","id":"...","image":"..."}`
- publishing the array only from the callback owner
- releasing the SteamUGC query handle from the callback owner on both success
  and failure paths

### The browser-event payload budget now covers retained UGC arrays

The earlier `16384`-byte browser-event payload cache was sized for the smaller
social/stats payloads reconstructed in rounds 178 through 188. The retained
UGC query results can carry a much larger array of title/description rows.

This round raises `CL_STEAM_BROWSER_EVENT_PAYLOAD_LENGTH` to `65536` so the
reconstructed `web.ugc.results` payload can be built without immediately
truncating longer workshop query pages.

## Verification

Static/source verification only:

- `python -m pytest tests/test_platform_services.py tests/test_steamworks_harness.py -q`
- `MSBuild` of `Debug|Win32` using
  `WindowsTargetPlatformVersion=10.0.26100.0`
- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
- `git diff --check`

The updated tests pin:

- the browser-method handoff to `CL_Steam_RequestAllUGC(...)`
- the new SteamUGC request/result/preview/release wrappers and their exact
  vtable slots
- the retained callback-owned workshop row array shape
- query-handle release ownership in the callback lane
- the widened browser-event payload budget needed for larger retained UGC
  arrays

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
