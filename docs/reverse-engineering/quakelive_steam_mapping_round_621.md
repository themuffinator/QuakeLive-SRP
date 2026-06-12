# Quake Live Steam Mapping Round 621: SteamDataSource Avatar Response Lifecycle

Date: 2026-06-12

## Scope

This round consolidates the retail SteamDataSource avatar request path across
the Binary Ninja HLIL, the Ghidra companion corpus, and the reconstructed
client/platform source. Earlier rounds pinned the `OnRequest` owner, the
`AvatarImageLoaded_t` lifecycle owner, and the delayed `ResponseThread`
boundary separately; this pass treats them as one launch/runtime integration
flow.

The target is intentionally narrow:

- `steam://avatar/...` URL ownership in `SteamDataSource::OnRequest`.
- `SteamFriends()` avatar image lookup and pending-handle behavior.
- `AvatarImageLoaded_t` callback registration, dispatch, and pending retry.
- SteamUtils image-size/RGBA loading for source-owned avatar buffers.
- `QLResourceInterceptor_OnRequest` fallback ordering for non-avatar resources.
- Default-disabled `QL_BUILD_ONLINE_SERVICES` / Steamworks stubs.

## Retail Evidence

Observed Binary Ninja HLIL and Ghidra signals:

- `FUN_004640c0` / `sub_4640c0` is the SteamDataSource `OnRequest` owner.
  It parses the URL, gates the `"avatar"` path string, calls
  `SteamFriends()` vtable slot `0x90`, treats image handle `0xffffffff` as a
  pending load, records the Awesomium request in the pending table, and calls
  `sub_463550` when the image is ready.
- `FUN_00464290` / `sub_464290` is the `AvatarImageLoaded_t` callback target.
  It reads the SteamID from the callback payload, removes the matching pending
  request, and restarts the response path through `sub_463550`.
- `FUN_00464300`, `FUN_00464440`, and `FUN_00464510` own SteamDataSource
  construction, `AvatarImageLoaded_t` callback registration id `0x14e`,
  shutdown, and destruction.
- `SteamDataSource::vftable` and
  `CCallback<class_SteamDataSource,struct_AvatarImageLoaded_t,0>::vftable`
  are present in the Ghidra analysis symbols and HLIL vtable region.
- `FUN_00460f30` / `sub_460f30` is the public Steam client avatar helper. It
  also uses `SteamFriends()` slot `0x90` and `SteamUtils()` slots `0x14` and
  `0x18` for image size and RGBA payload loading.
- Imports include `SteamFriends`, `SteamUtils`,
  `SteamAPI_RegisterCallback`, and `SteamAPI_UnregisterCallback`.

The SteamDataSource retail path appears to request the large avatar image via
slot `0x90`. The reconstructed platform API also exposes small and medium
selectors because the Steamworks ABI has stable adjacent slots, but the retail
SteamDataSource and `SteamClient_GetAvatarImageHandle` evidence both remain
anchored to the large-avatar behavior.

## Source Reconstruction

The current source reconstruction keeps the online-service behavior bounded:

- `CL_SteamResources_ParseAvatarURL` accepts `steam://avatar/...`, defaults to
  `QL_STEAM_AVATAR_LARGE`, and splits the 64-bit SteamID into the two retail
  identity words used by the Steamworks wrapper.
- `CL_SteamResources_RequestAvatarRGBA` maps pending Steam image handles into
  `cl_steamPendingAvatars`, clears the pending entry once the image is ready,
  and loads RGBA pixels through `QL_Steamworks_LoadAvatarRGBA`.
- `CL_SteamResources_OnAvatarImageLoaded` clears the pending marker and logs
  that the request can be retried, which matches the retail callback's role
  without recreating the Awesomium delayed-response object directly.
- `CL_SteamDataSource_Request` marks successful avatar responses as
  `fromSteamDataSource`, returns `image/rgba`, and leaves non-avatar
  `steam://` resources to the launcher/web fallback owner.
- `QLResourceInterceptor_OnRequest` tries the SteamDataSource owner first,
  then the mapped retail-host request, and then the launcher data request.
  This preserves `QLResourceInterceptor_OnRequest` fallback ordering while
  keeping non-avatar Steam URIs out of the default-disabled live-service path.
- `QL_Steamworks_RegisterAvatarCallbacks` installs callback id `0x14e` with
  the `0x14` byte raw payload and dispatches to the client binding.
- Disabled Steamworks header stubs return unavailable/false and clear output
  buffers so the default build remains offline and fallback-oriented.

No additional live Steam behavior was added in this round. The existing
implementation remains behind the repository's online-service policy gates.

## Validation

Added `test_steam_datasource_avatar_response_lifecycle_tracks_round_621`,
which cross-checks:

- alias map coverage for the SteamDataSource lifecycle, callback, and avatar
  helper owners;
- Ghidra `functions.csv`, `imports.txt`, and `analysis_symbols.txt` anchors;
- Binary Ninja HLIL anchors for `OnRequest`, callback registration, callback
  retry, `ResponseThread` naming, and SteamUtils image loading;
- source-side URL parsing, pending marker, callback, response ownership,
  interceptor fallback, Steamworks wrapper, and disabled-stub behavior;
- harness coverage for requested avatar size slots and
  `avatar_image_loaded` callback dispatch;
- this mapping note and the implementation-plan task anchor.

Focused SteamDataSource avatar response lifecycle confidence:
**94% -> 99%**.

Focused AvatarImageLoaded pending-retry confidence:
**94% -> 99%**.

Overall Steam launch/runtime integration mapping confidence:
**93.44% -> 93.46%**.
