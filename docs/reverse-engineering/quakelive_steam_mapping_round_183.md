# Quake Live Steam Mapping Round 183

## Scope

This round is source-only and closes the next stable Steam resource bridge
seam in `src/` without changing the host alias corpus.

The target gap was the retained avatar-resource ownership lane around
`SteamDataSource_OnAvatarImageLoaded`, which earlier source rounds had left as
a bounded compatibility path:

- rounds 176 through 182 rebuilt the stable advert, social, overlay, browser,
  and invite surfaces
- `cl_steam_resources.c` still treated avatar image misses as simple hard
  failure even though the retail bridge distinguishes “not ready yet” from
  “unavailable”
- the Steam wrapper still lacked the dedicated `AvatarImageLoaded_t` callback
  bundle that owns the retry notification in retail

Primary evidence stayed inside the committed retail corpus and reconstructed
source tree:

- `docs/reverse-engineering/quakelive_steam_mapping_round_07.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_177.md`
- `docs/reverse-engineering/source-file-gap-notes/rw-g01-client-steam-resources.md`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`
- `src/code/client/cl_steam_resources.c`
- `src/common/platform/platform_steamworks.c`
- `src/common/platform/platform_steamworks.h`

## Reconstructed Source Closures

### Steam avatar requests now distinguish pending from hard failure

The important retail behavior seam is that avatar fetches are not purely
synchronous:

- a valid avatar image handle can be returned immediately
- a missing image returns failure
- a not-yet-ready image returns `-1` and completion later arrives through
  `AvatarImageLoaded_t`

This round restores that source-side distinction instead of collapsing all
non-ready cases into one failure branch.

`platform_steamworks.c` now exposes
`QL_Steamworks_RequestAvatarImage(...)`, which returns one of:

- `QL_STEAM_AVATAR_IMAGE_READY`
- `QL_STEAM_AVATAR_IMAGE_PENDING`
- `QL_STEAM_AVATAR_IMAGE_UNAVAILABLE`

`QL_Steamworks_LoadAvatarRGBA(...)` now depends on that lower-level owner
instead of rediscovering the avatar state privately.

### `cl_steam_resources.c` now tracks pending avatar retries explicitly

The client resource bridge now mirrors the retail retry owner more closely.

`CL_SteamResources_RequestAvatarRGBA(...)` now:

- checks the avatar image state first
- records pending SteamIDs when Steam reports “not ready yet”
- clears pending state when a later request or callback resolves that SteamID

The useful closure is that the source no longer logs every unresolved avatar as
a generic missing resource. It now preserves the real distinction between:

- avatar image still pending callback completion
- avatar image genuinely unavailable

The existing compatibility resource bridge remains synchronous, but its state
tracking now matches retail much more closely.

### The Steam wrapper now owns the retained `AvatarImageLoaded_t` callback lane

`platform_steamworks.h` / `platform_steamworks.c` now reconstruct the missing
callback registration surface:

- `QL_Steamworks_RegisterAvatarCallbacks(...)`
- `QL_Steamworks_UnregisterAvatarCallbacks(...)`
- `ql_steam_avatar_callback_bindings_t`
- `ql_steam_avatar_image_loaded_t`

The wrapper now registers a dedicated callback object for the retained
`AvatarImageLoaded_t` dispatch and tears it down during Steam shutdown.

On the client side, `CL_InitSteamResources()` and
`CL_ShutdownSteamResources()` now own the registration lifecycle for the
avatar callback bundle, and `CL_SteamResources_OnAvatarImageLoaded(...)`
clears the pending retry bookkeeping when the retail-style notification
arrives.

## Remaining Bounded Gap

This round intentionally stops short of inventing a fake delayed Awesomium
response object.

Observed fact:

- retail keeps the original resource request alive and completes it
  asynchronously once `AvatarImageLoaded_t` fires

Bounded source gap:

- the checked-in resource bridge still answers synchronously, so a pending
  avatar request can only be retried later instead of finishing the original
  browser request in place

That means the callback owner is now reconstructed, but the final delayed
`SendResponse` path remains a documented compatibility gap rather than a
forced approximation.

## Verification

Static/source verification only:

- `python -m pytest tests/test_platform_services.py tests/test_steamworks_harness.py -q`
- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
- `MSBuild` of `Debug|Win32` using
  `WindowsTargetPlatformVersion=10.0.26100.0`
- `git diff --check`

The updated tests pin:

- the new pending/ready/unavailable avatar-image state split
- the dedicated `AvatarImageLoaded_t` callback registration bundle
- the client-owned pending-avatar bookkeeping in `cl_steam_resources.c`
- harness-level callback dispatch for avatar image completion
- the unchanged bounded source gap around delayed browser response delivery

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
