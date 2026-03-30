# Quake Live Steam Host Mapping Round 66

## Scope

This round carries already-mapped `quakelive_steam.exe` avatar behavior into
the writable source tree instead of promoting another fresh alias batch.

The target slice is the retail Steam avatar path bounded earlier in:

- Round 01: `SteamDataSource` accepts `avatar` requests with a size token
- Round 06: `sub_460F30 -> SteamClient_GetAvatarImageHandle`
- Round 19: `sub_4B0440 -> QLCGImport_GetAvatarImageHandle`
- Round 54: `SteamDataSource_OnRequest` and `ResponseThread_Run`

Primary evidence for this source-reconstruction pass:

- `docs/reverse-engineering/quakelive_steam_mapping_round_01.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_06.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_19.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_54.md`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `src/common/platform/platform_steamworks.c`
- `src/code/client/cl_steam_resources.c`
- `src/code/client/cl_cgame.c`

## Reconstructed Source Closures

### `sub_460F30`: `SteamClient_GetAvatarImageHandle`

Observed retail facts already documented in Round 06:

1. The host requests a Steam avatar image through `SteamFriends()->Get*Avatar`.
2. It resolves dimensions and RGBA pixels through `SteamUtils`.
3. It produces an engine-visible cached image handle for the caller.

Writable source closure landed in this round:

- `QL_Steamworks_LoadAvatarRGBA` now reconstructs the SteamFriends/SteamUtils
  half of that contract in `src/common/platform/platform_steamworks.c`.
- The implementation supports the retail small/medium/large avatar selector
  split that the browser data-source path also uses.

### `sub_4640C0`: `SteamDataSource_OnRequest`

Observed retail facts already documented in Rounds 01 and 54:

1. The browser-side source accepts `steam://avatar/...` requests.
2. It parses a SteamID plus avatar-size token.
3. It serves image bytes back into the host-side resource path.

Writable source closure landed in this round:

- `cl_steam_resources.c` now parses `steam://avatar/<steamid>` and
  `steam://avatar/<size>/<steamid>` URLs.
- The client bridge converts the fetched RGBA avatar into a cacheable TGA
  payload so `re.RegisterShaderNoMip` can consume it through the existing Steam
  resource cache path.

### `sub_4B0440`: `QLCGImport_GetAvatarImageHandle`

Observed retail facts already documented in Round 19:

1. Native cgame calls the host import at `+0x1FC` for scoreboard/player-card
   avatars.
2. The wrapper is a direct forwarder into `SteamClient_GetAvatarImageHandle`.

Writable source closure landed in this round:

- `QL_CG_trap_GetAvatarImageHandle` no longer returns a hard stub.
- The native cgame import seam now resolves `steam://avatar/large/%llu`
  through `CL_Steam_RegisterShader`, which gives native cgame a real renderer
  handle instead of a constant zero.

## Verification

This round adds source-backed verification at two levels:

- runtime mock coverage in `tests/steamworks_harness.c` /
  `tests/test_steamworks_harness.py` for the SteamFriends/SteamUtils avatar
  path, including size-slot selection
- static parity checks in `tests/test_platform_services.py` proving that the
  native cgame import seam, Steam URL bridge, and platform avatar loader stay
  wired together

Targeted result:

- `python -m pytest tests/test_steamworks_harness.py tests/test_platform_services.py -q`
- `14 passed`

## Completion Summary

No new alias rows were added in `references/analysis/quakelive_symbol_aliases.json`
this round; the mapping work here was used to close a concrete source-visible
host gap.

Current global `quakelive_steam.exe` mapping coverage remains:

- raw alias entries: `944`
- address-backed aliases: `943`
- Ghidra function coverage: `17.230%` of `5473`

Source reconstruction improved the writable Task 21 host baseline by removing
the hard-stub avatar path across the platform layer, Steam resource bridge, and
native cgame import seam.
