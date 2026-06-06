# Quake Live Steamworks Mapping Round 356

Date: 2026-06-06

Focus: x86 Steam C++ vtable ABI normalization for the Steam GameServer and
legacy P2P wrapper family.

## Retail Evidence

- Owning binary: `assets/quakelive/quakelive_steam.exe`.
- Primary HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`.
- Companion Ghidra rows:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  identifies the adjacent Steam server owner functions including
  `FUN_00465a40`, `FUN_00465a60`, `FUN_00465b00`, `FUN_00465b70`,
  `FUN_00465d50`, and `FUN_00465e00`.
- Symbol/name support:
  `references/analysis/quakelive_symbol_aliases.json` and the existing
  Steamworks mapping rounds identify the server metadata, identity,
  networking, and callback owners around this range.

## Observed Facts

The retail host dispatches these lanes through Steam C++ interface vtables:

- `0x00465A40` calls `SteamGameServer` slot `0x30` for max-player count.
- `0x00465A60` walks an infostring and calls `SteamGameServer` slot `0x50`
  for each non-empty key/value pair.
- `0x00465B00` obtains the game-server SteamID through slot `0x28` before
  publishing configstrings `0x2ca` and `0x2cb`.
- `0x00465B70` accepts server P2P sessions through
  `SteamGameServerNetworking` slot `0x0c`.
- `0x00465D50` forwards incoming UDP packets through `SteamGameServer` slot
  `0x94`.
- The adjacent outgoing packet drain uses the paired `SteamGameServer` slot
  `0x98`.
- The server-stats request gate reconstructed in round 354 uses
  `SteamGameServer` slot `0x20`.

These are C++ interface methods in the retail 32-bit host. Other reconstructed
Steam interface wrappers in `platform_steamworks.c` already model this with a
fastcall-style `self, unused, ...` call shape so ECX carries the interface
pointer while EDX is explicitly consumed.

## Source Reconstruction

- Added `QL_STEAMWORKS_FASTCALL` as the shared ABI marker for Steam interface
  vtable typedefs that use the `self, unused, ...` form.
- Converted the retained `ISteamNetworking`, `ISteamGameServer`, and
  `ISteamGameServerNetworking` wrapper typedefs from plain C function pointers
  to the explicit fastcall wrapper shape.
- Updated GameServer metadata, identity, logged-on, public-IP, incoming/outgoing
  packet, and legacy P2P call sites to pass the unused second argument.
- Updated the Steamworks harness vtable mocks to the same ABI shape so 64-bit
  harness coverage no longer masks a 32-bit argument-shift hazard.
- Tightened static parity coverage for the ABI marker, representative typedefs,
  and corrected dispatch calls through the mapped slots.

## Inference Boundary

Confidence is high that these calls are C++ vtable method dispatches because
the HLIL consistently dereferences interface vtables before calling the
observed slots. The exact SDK compiler spelling is not recovered from the
retail binary, so the source keeps the project-standard `self, unused, ...`
fastcall convention already used for the rest of the Steam wrapper layer.
Live Steam backend behavior remains intentionally unvalidated behind
`QL_BUILD_ONLINE_SERVICES`.

## Parity Estimate

- Focused GameServer/P2P vtable ABI wrapper family:
  **before 70% -> after 96%**.
- Steam GameServer metadata, identity, packet bridge, and legacy P2P wrapper
  surfaces together:
  **before 95% -> after 98%**.
- Broader Steamworks parity remains approximately **99%**; this pass closes a
  static ABI reconstruction risk without claiming live backend validation.
