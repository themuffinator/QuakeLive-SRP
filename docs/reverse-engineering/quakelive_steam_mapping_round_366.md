# Quake Live Steamworks Mapping Round 366

Date: 2026-06-06

Focus: close the retained legacy Steam P2P read-boundary harness gap for the
client `SteamNetworking` and server `SteamGameServerNetworking` wrapper lanes.

## Retail Evidence

- Owning binary: `assets/quakelive/quakelive_steam.exe`.
- Canonical HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`.
- Structured companion corpus:
  `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`,
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`, and
  `docs/mapping-ref/quakelive_steam_mapping_report.md`.
- Existing reconstruction anchors:
  `docs/reverse-engineering/quakelive_steam_mapping_round_349.md` and
  `docs/reverse-engineering/quakelive_steam_mapping_round_356.md`.

Observed import evidence remains the same as the earlier P2P mapping rounds:
`imports.txt` lists both `SteamNetworking` and `SteamGameServerNetworking`.

Observed HLIL evidence:

- `0x00461a9d` repeatedly calls `SteamNetworking()` slot `+4` on channel `1`
  before the client voice path reads the queued packet through slot `+8` at
  `0x00461ad8`.
- `0x00461d8f` uses the same `SteamNetworking()` availability slot on channel
  `0`, then reads through slot `+8` at `0x00461dc8`.
- `0x00466928` checks `SteamGameServerNetworking()` slot `+4` on channel `1`
  in `SteamServer_Frame`.
- `0x00466961` reads the server P2P packet through
  `SteamGameServerNetworking()` slot `+8`.
- `0x004668ca` and `0x00466a23` send through slot `0`, while `0x00465b70`
  remains the server P2P session-accept owner through slot `0x0c`.

## Observed Facts

- The source wrappers already retain the retail legacy slot layout:
  `SendP2PPacket` at vtable slot `0`, `IsP2PPacketAvailable` at slot `1`,
  `ReadP2PPacket` at slot `2`, and `AcceptP2PSessionWithUser` at slot
  `0x0c / 4`.
- The client wrappers dispatch through `QL_Steamworks_GetNetworkingInterface`.
- The server wrappers dispatch through `QL_Steamworks_GetGameServerNetworking`.
- Round 356 already normalized these Steam C++ interface calls to the explicit
  `QL_STEAMWORKS_FASTCALL self, unused, ...` ABI shape.
- The remaining local harness gap was not another vtable slot. It was the
  boundary behavior around a staged packet that is available but rejected by a
  too-small buffer during `ReadP2PPacket`.

## Source Reconstruction

This pass added executable and static reconstruction coverage, not production
Steamworks code:

- Extended `test_legacy_p2p_wrappers_use_mapped_steamnetworking_slots` so the
  client harness stages a valid packet, attempts to read it into a too-small
  buffer, and proves the read fails while stale `outSize` and remote Steam ID
  outputs are cleared.
- Extended
  `test_legacy_game_server_p2p_wrappers_use_mapped_networking_slots` with the
  same server-side too-small buffer rejection path.
- Added `test_legacy_p2p_read_boundary_round_366_is_pinned` to pin the retail
  import names, HLIL slot evidence, source wrapper slots, mock read-output
  clearing, and this mapping note.

## Inference Boundary

The retail binary proves the legacy `ISteamNetworking`-shape availability and
read slots. It does not expose a direct high-level contract for how Valve's SDK
clears caller-provided output storage on every failed read edge. Therefore this
round does not alter the production wrappers' early-return behavior.

The new clear-on-reject assertions are scoped to the deterministic harness
mock. They guard the reconstructed local ABI and keep failure projections from
leaking stale Python ctypes output state, while the retail-facing claim remains
limited to slot ownership and packet-pump topology.

Modern `ISteamNetworkingSockets` and `ISteamNetworkingMessages` replacement
design remains intentionally open and explicitly labeled outside the retail
legacy path.

## Verification

Local verification for this pass:

```text
python -m pytest tests/test_steamworks_harness.py::test_legacy_p2p_wrappers_use_mapped_steamnetworking_slots tests/test_steamworks_harness.py::test_legacy_game_server_p2p_wrappers_use_mapped_networking_slots -q
4 passed
```

Planned full Steamworks/platform verification:

```text
python -m pytest tests/test_platform_services.py tests/test_steamworks_harness.py -q
```

## Parity Estimate

- Focused legacy P2P read-boundary harness parity:
  **before 96% -> after 98%**.
- Legacy Steam P2P wrapper evidence confidence:
  **before 98% -> after 98.5%**.
- Broader Steamworks parity remains approximately **99%** because live Steam
  backend behavior and modern networking replacement design remain intentionally
  outside this opt-in reconstruction pass.
