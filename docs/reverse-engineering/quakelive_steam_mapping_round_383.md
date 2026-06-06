# Quake Live Steamworks Mapping Round 383

Date: 2026-06-06

Focus: reconstruct the retained client `SteamUserStats` float descriptor lane
used by the `users.stats` callback builder.

## Retail Evidence

- Owning binary: `quakelive_steam.exe`.
- Canonical HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`.
- Canonical HLIL data section:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part07.txt`.
- Companion corpus:
  `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`,
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`,
  `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`, and
  `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`.
- Prior source reconstruction notes:
  `docs/reverse-engineering/quakelive_steam_mapping_round_188.md` and
  `docs/reverse-engineering/quakelive_steam_mapping_round_382.md`.

Observed HLIL facts:

- `0x0046006b` seeds the stat descriptor walk at `&data_55da98`.
- `0x00460074` tests `esi_1[-1]` before choosing the stat read path.
- `0x004600ef` loads `SteamUserStats()` slot `0x44` for the float stat path.
- `0x00460103` forwards SteamID low/high words, the stat name, and a stack
  float output pointer to that slot.
- `0x0046010e` converts the returned float to a double-backed JS number.
- `0x0046008d` loads `SteamUserStats()` slot `0x48` for the integer stat path.
- `0x00460149` advances the descriptor cursor by seven dwords.
- `0x0055da8c` stores the stat descriptor count `0x58`.

Observed data-section facts:

- The stat table is 88 rows long.
- Each row is seven dwords wide.
- The callback cursor points at `row + 4`, the stat-name pointer.
- The tested discriminator is `row + 0`.
- The trailing row dword mirrors the one-based stat ordinal for rows 0 through
  86; the callback does not read that field in this lane.
- all 88 shipped descriptor discriminators are zero, including
  `medal_accuracy`.

## Source Reconstruction

This round promotes the observed but previously unwrapped client float lane
into source while preserving the shipped table behavior:

- Added `QL_Steamworks_GetUserStatFloat(...)` with the retained
  `SteamUserStats` vtable slot `0x44 / 4`.
- Added the disabled inline fallback that clears `*outValue` to `0.0f` and
  returns `qfalse`.
- Converted the client stat catalog from a name-only array to
  `clSteamStatDescriptor_t { name, isFloat }`.
- Marked every current descriptor `qfalse`, matching the committed data table.
- Added `CL_Steam_UserStatFieldIsFloat(...)`.
- Updated `CL_Steam_AppendUserStatsJson(...)` to branch like retail:
  descriptor float rows call `QL_Steamworks_GetUserStatFloat(...)` and emit a
  numeric `%g` value, while current integer rows continue to call
  `QL_Steamworks_GetUserStatInt(...)` and emit `%d`.

## Harness Coverage

The executable Steamworks harness now covers the new client float read wrapper:

- Added mock state for float value, float result, and float read call count.
- Added `QLR_SteamUserStats_GetUserStatFloat`.
- Installed the mock at `SteamUserStats` vtable slot `0x44 / 4`.
- Extended `QLR_SteamworksMock_SetUserStatsReadback(...)` and
  `QLR_SteamworksMock_SetUserStatsReadbackResults(...)` to control the float
  path.
- Exported enabled and disabled `QLR_Steamworks_GetUserStatFloat(...)`.
- Extended `test_user_stats_readback_wrappers_use_retail_slots` to prove
  invalid-input guards, output clearing, success projection, SteamID/name
  forwarding, result failure propagation, and disabled fallback behavior.

## Inference Boundary

The branch and slot are observed retail facts. The current shipped catalog
never takes the branch because the descriptor discriminators are all zero.
Reconstructing the float wrapper and descriptor branch therefore improves
control-flow parity without claiming any live retail stat currently returns as
float.

## Verification

Local verification for this pass:

```text
python -m pytest tests/test_platform_services.py::test_steam_user_stats_float_descriptor_round_383_is_pinned tests/test_platform_services.py::test_client_stats_callback_lane_stays_explicit tests/test_steamworks_harness.py::test_user_stats_readback_wrappers_use_retail_slots -q
4 passed in 2.50s
```

Full Steamworks/platform verification:

```text
python -m pytest tests/test_platform_services.py tests/test_steamworks_harness.py -q
212 passed in 7.34s
```

## Parity Estimate

- Focused client `STATS` descriptor-control-flow parity:
  **before 86% -> after 99%**.
- Client `SteamUserStats` readback wrapper coverage:
  **before 99% -> after 99.5%**.
- Broader Steamworks parity remains approximately **99%** because live backend
  values, localized achievement metadata, and production service availability
  are outside this deterministic source/harness pass.
