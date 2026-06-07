# Quake Live Steam Mapping Round 425

Date: 2026-06-07

## Scope

This round tightens the Steam avatar runtime import seam used by native cgame
scoreboard/player-card rendering. The focus is the retail split between the
cgame-facing import wrapper and the client-owned Steam avatar image helper.

## Evidence

- `references/analysis/quakelive_symbol_aliases.json` promotes
  `sub_460F30` as `SteamClient_GetAvatarImageHandle` and `sub_4B0440` as
  `QLCGImport_GetAvatarImageHandle`.
- Binary Ninja HLIL for `quakelive_steam.exe` shows `sub_4B0440` as a direct
  `return sub_460f30(arg1, arg2)` wrapper.
- Binary Ninja HLIL for `sub_460F30` checks the retained Steam-client
  initialized flag, probes the renderer image cache with a `steam_%llu` name,
  requests the large Steam avatar through `SteamFriends()->vtable[0x90]`, reads
  dimensions and RGBA pixels through `SteamUtils()->vtable[0x14]` and
  `SteamUtils()->vtable[0x18]`, creates an engine image, and returns the
  renderer handle.
- The earlier avatar data-source rounds already reconstructed the bounded
  source-side Steam avatar bridge through `CL_Steam_RegisterShader` and
  `QL_Steamworks_LoadAvatarRGBA`.

## Source Reconstruction

- Added the named client helper
  `SteamClient_GetAvatarImageHandle(identityLow, identityHigh)` in
  `cl_steam_resources.c`.
- Moved the SteamID-word composition and `steam://avatar/large/%llu` request
  construction out of `QL_CG_trap_GetAvatarImageHandle` and into the client
  helper boundary.
- Changed `QL_CG_trap_GetAvatarImageHandle` to the retail-shaped direct
  forwarder over `SteamClient_GetAvatarImageHandle`.
- Exposed the helper in `client.h` so the native cgame import table owner uses
  the same named surface as the promoted retail symbol.

## Deferred Notes

- The source still resolves the final image through the reconstructed
  `steam://avatar/large/...` resource bridge rather than directly creating the
  retail `steam_%llu` renderer image inside the helper. That keeps the
  default-disabled online-service policy intact and preserves the existing
  pending-avatar callback behavior while making the public runtime seam match
  retail.
- The adjacent persona-name lane was surveyed. Retail gates
  `SteamClient_SyncPersonaNameCvar` on the absence of `com_build`, but the
  current source registers `com_build` earlier than retail. A broad startup
  order change is left for a dedicated launch-integration pass.

## Parity

Focused native cgame Steam-avatar import confidence moves from 84% to 93%.
The broader Steam launch/runtime integration slice moves from 77% to 78%.
