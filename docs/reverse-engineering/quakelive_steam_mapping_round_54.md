# Quake Live Steam Host Mapping Round 54

## Scope

This round maps the substantive `SteamDataSource` avatar-response slice that
bridges the Steam Friends avatar APIs into the Awesomium `steam://` data
source.

The promoted slice covers:

- the RTTI-backed `ResponseThread` worker used to emit avatar responses
- the custom PNG buffer and encode helpers that feed `SendResponse`
- the `SteamDataSource` virtual request handler and deleting destructor
- the host helper that allocates and starts the avatar response worker

Primary evidence for this round:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `docs/launcher_awesomium_audit.md`

## Response Thread Closures

### `sub_463110`: `ResponseThread_PNGWriteCallback`

Observed facts:

1. `sub_463180` registers this helper as the libpng write callback.
2. The helper grows a heap buffer through `malloc` / `realloc` using the
   callback state fields that track `data` plus written byte count.
3. It copies the incoming chunk into the resized buffer and raises the exact
   `Write Error` failure on allocation failure.

That makes `sub_463110` the response-thread PNG write callback.

### `sub_463180`: `ResponseThread_EncodeAvatarPNG`

Observed facts:

1. The helper creates libpng write/info structs with the exact version string
   `1.2.24`.
2. It registers `sub_463110` as the custom write callback and configures an
   `8`-bit RGBA image (`color type 6`).
3. It builds a row-pointer table over the source RGBA buffer using `width * 4`
   byte stepping, writes the PNG, and frees the temporary row table.

That is the avatar PNG encoder used by the response thread.

### `sub_463440`: `ResponseThread_Run`

Observed facts:

1. The RTTI-backed `ResponseThread::vftable{for idSysThread}` points its run
   slot directly at this helper.
2. The helper calls `SteamUtils()` to fetch avatar dimensions and RGBA pixels
   for the stored image handle.
3. It encodes those pixels through `sub_463180`, sends the final payload via
   `Awesomium::DataSource::SendResponse(..., "image/png")`, and frees both the
   PNG buffer and raw pixel buffer.
4. It finishes with the `(**arg1)(1)` worker cleanup pattern expected for a
   self-owned `idSysThread` subclass.

That makes `sub_463440` exactly `ResponseThread_Run`.

## Steam Data Source Closures

### `sub_463550`: `SteamDataSource_StartResponseThread`

Observed facts:

1. The helper allocates a `0xA4`-byte object, runs the base `idSysThread`
   constructor, and then overwrites the vftable with the RTTI-backed
   `ResponseThread::vftable`.
2. It stores the owning `SteamDataSource*`, the Awesomium request id, and the
   resolved Steam avatar image handle into the thread object.
3. It starts the worker with the exact name format `request_%i`, normal thread
   priority, and a `0x100000` stack reservation.

The current source tree does not expose this as a named standalone helper, so
the promotion uses the descriptive host-side name
`SteamDataSource_StartResponseThread`.

### `sub_4640C0`: `SteamDataSource_OnRequest`

Observed facts:

1. The RTTI-backed `SteamDataSource::vftable{for Awesomium::DataSource}` uses
   this helper as slot `1`, matching the existing `*_OnRequest` naming pattern
   already used for `QLResourceInterceptor`.
2. The helper parses the incoming Awesomium path and filename, accepts only the
   `avatar` request family, and extracts the SteamID plus avatar-size token from
   the URL.
3. It queries `SteamFriends()->Get*Avatar`; when the image is immediately
   available it launches `sub_463550`, and when Steam returns `-1` it queues the
   request id in the internal pending-request tree keyed by SteamID.

That is exactly the `SteamDataSource` request handler.

### `sub_464510`: `SteamDataSource_Destroy`

Observed facts:

1. The same `SteamDataSource::vftable` uses this helper as slot `0`.
2. The body tailcalls `SteamDataSource_Shutdown`.
3. It then conditionally calls `operator delete` when the usual low-bit
   destructor flag is set, matching the deleting-destructor pattern already
   named as `*_Destroy` elsewhere in the Awesomium host.

That makes `sub_464510` the deleting destructor `SteamDataSource_Destroy`.

## Completion Summary

This round promotes:

- `ResponseThread_PNGWriteCallback`
- `ResponseThread_EncodeAvatarPNG`
- `ResponseThread_Run`
- `SteamDataSource_StartResponseThread`
- `SteamDataSource_OnRequest`
- `SteamDataSource_Destroy`

Focused band results after this pass:

- `0x463100-0x464520`: `24 -> 18` remaining standalone gaps
- `0x463100-0x463600`: `11 -> 7`
- `0x464000-0x464520`: `3 -> 1`

The remaining starts in this band are now concentrated in the shared
allocator/tree-helper layer around:

- `0x00463670`
- `0x00463980`
- `0x00463D80`
- `0x00463C20`
- `0x004638D0`
- `0x00463F20`
- `0x00463FC0`
- `0x00464060`

These helpers are still structurally useful, but they are shared container
operations rather than the source-backed `SteamDataSource` / `ResponseThread`
behavior that this round targeted.
