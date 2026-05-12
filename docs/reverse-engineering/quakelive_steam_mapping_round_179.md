# Quake Live Steam Mapping Round 179

## Scope

This round is source-only and closes the retained `qz_instance` lobby/social
method block in `src/` without changing the host alias corpus.

The target seam was the gap between the earlier wrapper reconstruction in
round 69 and the newer callback/event work from rounds 177 and 178:

- round 69 already reconstructed the shared Steamworks wrappers for
  `CreateLobby`, `JoinLobby`, `SetLobbyServer`, `ShowInviteOverlay`,
  `SayLobby`, and `RequestUserStats`
- round 178 rebuilt the richer lobby enter/leave callback payloads and owner
  tracking in `cl_main.c`
- the browser-facing `QLJSHandler_OnMethodCall` surface in `cl_cgame.c` still
  exposed the older reduced method table instead of the retail lobby/social
  block bounded in rounds 07 and 09

Primary evidence stayed inside the committed retail corpus and reconstructed
source tree:

- `docs/reverse-engineering/quakelive_steam_mapping_round_07.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_09.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_69.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_178.md`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `src/code/client/cl_cgame.c`
- `src/code/client/cl_main.c`
- `src/common/platform/platform_steamworks.c`

## Reconstructed Source Closures

### Retail `qz_instance` IDs and binding order

The retained method enum in `cl_cgame.c` now carries the retail numeric IDs
for the stable `qz_instance` slice instead of the earlier local-only numbering.
The useful closure is that the source now matches the committed HLIL table for:

- `CreateLobby` (`17`)
- `LeaveLobby` (`18`)
- `JoinLobby` (`19`)
- `SetLobbyServer` (`20`)
- `ShowInviteOverlay` (`21`)
- `SayLobby` (`22`)
- `RequestUserStats` (`23`)
- `GetFriendList` (`24`)
- `ActivateGameOverlayToUser` (`25`)
- `FileExists` (`27`)
- `GetConfig` (`28`)
- `GetCursorPosition` (`29`)
- `GetAllUGC` (`31`)
- `GetNextKeyDown` (`32`)
- `SetFavoriteServer` (`33`)

I left the still-unreconstructed retail-only verbs out of the live binding
array rather than registering unstable placeholders:

- `OpenSteamOverlayURL`
- `SetClipboardText`
- `RequestServers`
- `RequestServerDetails`
- `RefreshList`
- `Invite`
- `NoOp`

### Browser dispatch now reaches the retained Steam lobby/social shim layer

`QLJSHandler_OnMethodCall` now forwards the stable lobby/social verbs through
client-owned shims instead of leaving them absent from the browser surface:

- `CreateLobby`
- `LeaveLobby`
- `JoinLobby`
- `SetLobbyServer`
- `ShowInviteOverlay`
- `SayLobby`
- `RequestUserStats`
- `ActivateGameOverlayToUser`

This keeps the Awesomium-facing dispatcher in `cl_cgame.c` aligned with the
retail method-table ownership already mapped in the host notes.

### `cl_main.c` now owns the browser-side Steam lobby/social shims

To avoid reaching into static callback state from `cl_cgame.c`, this round
reconstructed a small public client shim layer in `cl_main.c`:

- `CL_Steam_CreateLobby`
- `CL_Steam_LeaveLobby`
- `CL_Steam_JoinLobby`
- `CL_Steam_SetLobbyServer`
- `CL_Steam_ShowInviteOverlay`
- `CL_Steam_SayLobby`
- `CL_Steam_RequestUserStats`
- `CL_Steam_ActivateOverlayToUser`

Supporting closures:

1. `CL_Steam_ParseIdentityArgument` now mirrors the retained decimal SteamID
   parse step used by the browser methods before the shared Steamworks wrappers.
2. `CL_Steam_GetCurrentLobbyIdentityWords` centralizes the cached current
   lobby lookup already owned by the callback/event layer.
3. `CL_Steam_LeaveLobby` reuses the source-backed `CL_Steam_LeaveCurrentLobby`
   owner added in round 178, so explicit browser leave requests and callback-
   driven leave transitions share the same event publication path.

## Verification

Static/source verification only:

- `python -m pytest tests/test_platform_services.py -q`
- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
- `MSBuild` of `Debug|Win32` using
  `WindowsTargetPlatformVersion=10.0.26100.0`
- `git diff --check`

The updated tests pin:

- the retail numeric `qz_instance` IDs for the newly promoted lobby/social
  method slice
- the browser dispatcher cases in `QLJSHandler_OnMethodCall`
- the new client shim prototypes in `client.h`
- the client-owned SteamID parsing/current-lobby helpers and their wrapper
  calls into `platform_steamworks.c`

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
