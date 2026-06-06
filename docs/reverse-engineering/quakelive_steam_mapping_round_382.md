# Quake Live Steamworks Mapping Round 382

Date: 2026-06-06

Focus: add executable harness coverage for the retained client
`SteamUserStats` readback wrappers used by the `users.stats` browser payload.

## Retail Evidence

- Owning binary: `assets/quakelive/quakelive_steam.exe`.
- Canonical HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`.
- Companion corpus:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`,
  `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`, and
  `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`.
- Existing source reconstruction note:
  `docs/reverse-engineering/quakelive_steam_mapping_round_188.md`.

Observed HLIL facts:

- `0x0046008d` loads `SteamUserStats()` slot `0x48` for per-user integer
  stat reads in the retained `STATS` JSON builder.
- `0x0046018e` and `0x004601a6` call `SteamUserStats()` slot `0x30` for
  achievement display attributes `"name"` and `"desc"`.
- `0x004601c6` loads `SteamUserStats()` slot `0x50` for achievement unlocked
  state and unlock-time reads.
- The adjacent `0x004600ef` float-stat slot remains observed retail evidence,
  but this pass intentionally covers only the source-owned wrappers currently
  reconstructed in `platform_steamworks.c`.

## Observed Facts

- Round 188 reconstructed the client callback payload and added
  `QL_Steamworks_GetUserStatInt`, `QL_Steamworks_GetUserAchievement`, and
  `QL_Steamworks_GetAchievementDisplayAttribute`.
- The production wrappers already route through slots `0x48 / 4`,
  `0x50 / 4`, and `0x30 / 4` with the expected x86 C++ vtable ABI shape.
- Before this pass, the executable Steamworks harness only mocked
  `RequestUserStats` and `ResetAllStats` on the client `SteamUserStats`
  interface.

## Source Reconstruction

This pass adds deterministic harness coverage without changing production
Steamworks behavior:

- Added mock state for user-stat integer value, achievement state,
  unlock time, display attribute text, last SteamID, last stat/achievement
  name, last display-attribute key, call counts, and result toggles.
- Added `QLR_SteamUserStats_GetUserStatInt`,
  `QLR_SteamUserStats_GetUserAchievement`, and
  `QLR_SteamUserStats_GetAchievementDisplayAttribute`.
- Installed the mocks in the `SteamUserStats` vtable at `0x48 / 4`,
  `0x50 / 4`, and `0x30 / 4`.
- Exported enabled and disabled harness wrappers for the three production
  readback helpers.
- Added `test_user_stats_readback_wrappers_use_retail_slots` to prove
  invalid-input guards, output clearing, successful value projection,
  SteamID/name/key forwarding, result failure propagation, disabled fallback,
  and the display-attribute `NULL` to empty-string normalization.
- Added `test_steam_user_stats_readback_round_382_is_pinned` to tie the HLIL
  anchors, Round 188 note, production wrappers, mock vtable slots, executable
  test, plan entry, and this note together.

## Inference Boundary

This round proves local wrapper ABI and harness readback behavior. It does not
claim live Steam backend stat values, achievement catalog completeness,
localized display text behavior, or callback timing. The observed retail
float-stat slot remains documented evidence but is not promoted into a new
source wrapper by this pass.

## Verification

Local verification for this pass:

```text
python -m pytest tests/test_platform_services.py::test_steam_user_stats_readback_round_382_is_pinned tests/test_steamworks_harness.py::test_user_stats_readback_wrappers_use_retail_slots -q
3 passed in 0.76s
```

Full Steamworks/platform verification:

```text
python -m pytest tests/test_platform_services.py tests/test_steamworks_harness.py -q
208 passed in 6.28s
```

## Parity Estimate

- Focused client SteamUserStats readback harness parity:
  **before 58% -> after 98%**.
- Retained `users.stats` readback wrapper evidence confidence:
  **before 96% -> after 99%**.
- Broader Steamworks parity remains approximately **99%** because live backend
  values, localized achievement metadata, and the observed-but-unwrapped
  float-stat lane are outside this deterministic harness pass.
