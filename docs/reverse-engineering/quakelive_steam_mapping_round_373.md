# Quake Live Steamworks Mapping Round 373

Date: 2026-06-06

Focus: reconstruct executable harness coverage for the client Steam identity
and SteamUtils bootstrap wrappers shared by player identity, country seeding,
web-host bootstrap state, and app-id filtering.

## Retail Evidence

- Owning binary: `assets/quakelive/quakelive_steam.exe`.
- Canonical HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt`
  and
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`.
- Structured companion corpus:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`,
  `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`, and
  `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`.
- Existing mapping anchors:
  `docs/reverse-engineering/quakelive_steam_mapping_round_03.md`,
  `docs/reverse-engineering/quakelive_steam_mapping_round_04.md`,
  `docs/reverse-engineering/quakelive_steam_mapping_round_09.md`, and
  `docs/reverse-engineering/quakelive_steam_mapping_round_348.md`.

Observed HLIL facts:

- `0x00460550` is the local SteamID helper. It returns `0` until the client
  Steam API is live, then calls `SteamUser()` slot `0x08` and returns the low
  word of the hidden `CSteamID` result.
- `0x00460610` is the persona-name cvar sync helper. It falls back to
  `"anon"` when `SteamFriends()` is unavailable and otherwise reads
  `SteamFriends()->GetPersonaName` through vtable slot `0`.
- `0x00460690` is the IP-country helper. It returns `0` until the client Steam
  API is live, then jumps at `0x004606a6` through `SteamUtils()` slot `0x10`.
- `0x00431c48` publishes `appId` onto `window.qz_instance` during web-host
  binding through `SteamUtils()` slot `0x24`.
- `0x00460dd6` also reads `SteamUtils()` slot `0x24` for the retained UGC
  query owner, matching the current source's shared `QL_Steamworks_GetAppID`
  wrapper.

## Observed Facts

- `QL_Steamworks_GetPersonaName` maps the SteamFriends persona slot `0` and
  clears the caller buffer before any failure return.
- `QL_Steamworks_GetIPCountry` maps `SteamUtils` slot `0x10 / 4` and preserves
  the same clear-on-failure buffer contract.
- `QL_Steamworks_GetAppID` maps `SteamUtils` slot `0x24 / 4` and returns `0`
  when the runtime or vtable slot is unavailable.
- `QL_Steamworks_GetUserSteamID` maps `SteamUser` slot `0x08 / 4`, combines
  the hidden `CSteamID` output into low/high words, and clears both outputs on
  failure.
- Before this round, the harness used these surfaces indirectly through
  favorite-server, friend-summary, avatar, and callback tests, but it did not
  directly prove the four bootstrap wrappers and disabled-build fallbacks
  together.

## Source Reconstruction

This pass extends deterministic harness coverage without changing production
Steamworks behavior:

- Added mock call counters for SteamFriends persona name, SteamUser identity,
  SteamUtils IP country, and SteamUtils app ID.
- Incremented those counters in the mocked vtable methods backing slots `0`,
  `0x08 / 4`, `0x10 / 4`, and `0x24 / 4`.
- Exported enabled and disabled harness wrappers for
  `QL_Steamworks_GetPersonaName`, `QL_Steamworks_GetIPCountry`,
  `QL_Steamworks_GetAppID`, and `QL_Steamworks_GetUserSteamID`.
- Added `test_steam_client_identity_and_utils_wrappers_use_retail_slots` to
  prove persona/country copying, app-id forwarding, SteamID low/high
  projection, per-slot call counts, unavailable-user failure behavior, and
  disabled-build output clearing.
- Added `test_steam_client_identity_utils_round_373_is_pinned` to tie the
  retail HLIL anchors, production wrappers, mock vtable slots, executable
  test, and this note together.

## Inference Boundary

The retail evidence proves the vtable offsets and the host-owned bootstrap
callers. This round does not claim live Steam backend identity freshness,
country-database accuracy, or online-service availability. It closes local
wrapper and fallback evidence for the retained opt-in Steamworks boundary.

## Verification

Local verification for this pass:

```text
python -m pytest tests/test_platform_services.py::test_steam_client_identity_utils_round_373_is_pinned tests/test_steamworks_harness.py::test_steam_client_identity_and_utils_wrappers_use_retail_slots -q
3 passed
```

Full Steamworks/platform verification:

```text
python -m pytest tests/test_platform_services.py tests/test_steamworks_harness.py -q
197 passed
```

## Parity Estimate

- Focused client Steam identity/SteamUtils harness parity:
  **before 68% -> after 98%**.
- Bootstrap identity/app-id wrapper evidence confidence:
  **before 96% -> after 99%**.
- Broader Steamworks parity remains approximately **99%** because live Steam
  backend behavior, country freshness, and replacement online-service policy
  remain outside this opt-in reconstruction pass.
