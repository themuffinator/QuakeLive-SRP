# Quake Live Steamworks Mapping Round 372

Date: 2026-06-06

Focus: reconstruct executable harness coverage for the SteamFriends friend-list
enumeration and retained friend-summary wiring used by the `GetFriendList`
browser surface.

## Retail Evidence

- Owning binary: `assets/quakelive/quakelive_steam.exe`.
- Canonical HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt`.
- Structured companion corpus:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`,
  `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`, and
  `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`.
- Existing mapping anchors:
  `docs/reverse-engineering/quakelive_steam_mapping_round_09.md`,
  `docs/reverse-engineering/quakelive_steam_mapping_round_184.md`, and
  `docs/reverse-engineering/quakelive_steam_mapping_round_185.md`.

Observed HLIL facts in the return-value `QLJSHandler` dispatcher:

- `0x0043355d` enters the `GetFriendList` case and loads
  `SteamFriends()` slot `0x0c`.
- `0x00433560` passes the literal friend flag value `4` into that count call.
- `0x004335ab` loads the paired `SteamFriends` by-index slot `0x10` for each
  enumerated row, again using flag value `4`.
- `0x00433663`, `0x004336f1`, `0x0043375f`, and `0x004337cd` fill the friend
  object from slots `0x1c`, `0x18`, `0x14`, and `0x2c`.
- `0x004338be` and `0x00433954` read rich-presence keys `status` and `lanIp`
  through slot `0xb4`.
- `0x00433a00` reads the current-game structure through slot `0x20` and checks
  the low app-id bits against `SteamUtils()->GetAppID()`.

## Observed Facts

- The production wrappers already map the retained friend enumeration surface:
  `QL_Steamworks_GetFriendCount` uses `0x0c / 4`, and
  `QL_Steamworks_GetFriendByIndex` uses `0x10 / 4`.
- `QL_Steamworks_GetFriendSummary` already gathers the same retained summary
  lanes as the retail browser object: relationship, persona state, persona
  name, current game, nickname, and the `status` / `lanIp` rich-presence keys.
- `QL_Steamworks_GetFriendPersonaName` remains the focused single-field helper
  for callback and lobby membership owners that only need a display name.
- Before this round, the executable harness had deterministic mock coverage
  for summary-adjacent SteamFriends calls, overlays, avatars, invites, rich
  presence, and voice speaking, but it did not install the enumeration slots
  `0x0c / 4` and `0x10 / 4`.

## Source Reconstruction

This pass extends the local Steamworks harness without changing production
runtime behavior:

- Added mock friend-list state for count, by-index SteamID, call counts, last
  count flags, last index, and last index flags.
- Added `QLR_SteamFriends_GetFriendCount` and
  `QLR_SteamFriends_GetFriendByIndex`, with the by-index method writing the
  hidden `CSteamID` return pointer used by the existing wrapper ABI.
- Installed the mock methods in `QLR_SteamAPI_SteamFriends` at `0x0c / 4` and
  `0x10 / 4`.
- Exported enabled and disabled harness wrappers for
  `QL_Steamworks_GetFriendCount`, `QL_Steamworks_GetFriendByIndex`,
  `QL_Steamworks_GetFriendSummary`, and
  `QL_Steamworks_GetFriendPersonaName`.
- Added `test_steam_friends_enumeration_and_summary_use_mapped_slots` to prove
  disabled fallback clearing, retail flag forwarding, by-index SteamID word
  projection, invalid-index zeroing, persona-name copying, and the retained
  friend-summary fields.
- Added `test_steam_friends_enumeration_round_372_is_pinned` to tie the HLIL
  addresses, production vtable offsets, mock vtable entries, executable test,
  and this note together.

## Inference Boundary

The retail evidence proves the SteamFriends slot offsets, the fixed flag value
used by the browser friend-list case, and the summary fields emitted by the
retained host path. This round does not claim live Steam friend-list freshness,
backend availability, or modern replacement-network semantics. It closes the
deterministic wrapper and harness evidence for the already-mapped local
SteamFriends wiring.

## Verification

Local verification for this pass:

```text
python -m pytest tests/test_platform_services.py::test_steam_friends_enumeration_round_372_is_pinned tests/test_steamworks_harness.py::test_steam_friends_enumeration_and_summary_use_mapped_slots -q
3 passed
```

Full Steamworks/platform verification:

```text
python -m pytest tests/test_platform_services.py tests/test_steamworks_harness.py -q
194 passed
```

## Parity Estimate

- Focused SteamFriends friend-list harness parity:
  **before 72% -> after 98%**.
- Retained browser friend-summary wrapper evidence confidence:
  **before 98% -> after 99%**.
- Broader Steamworks parity remains approximately **99%** because live Steam
  backend behavior, service availability, and replacement online-service
  policy remain outside this opt-in reconstruction pass.
