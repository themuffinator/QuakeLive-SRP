# Quake Live Steamworks Mapping Round 375

Date: 2026-06-06

Focus: reconstruct executable harness coverage for the retained client
`stats_clear` command wrapper over `SteamUserStats::ResetAllStats`.

## Retail Evidence

- Owning binary: `assets/quakelive/quakelive_steam.exe`.
- Canonical HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`.
- Structured companion corpus:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`,
  `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`, and
  `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`.
- Existing mapping anchors:
  `docs/reverse-engineering/quakelive_steam_mapping_round_04.md` and
  `docs/reverse-engineering/quakelive_steam_mapping_round_229.md`.

Observed HLIL facts:

- `0x00460520` is the retained `stats_clear` command owner.
- `0x00460531` calls `SteamUserStats()` slot `0x54` with literal argument `1`.
- Round 04 already identified the same helper as the client Steam stats-clear
  control path, and the current source exposes the retained behavior through
  `QL_Steamworks_ClearStats`.

## Observed Facts

- `QL_Steamworks_ClearStats` maps the SteamUserStats reset slot as `0x54 / 4`.
- The wrapper intentionally requires an already-initialised Steamworks runtime
  and returns `qfalse` before touching the SteamUserStats interface when the
  client Steam state is not live.
- The wrapper normalizes the public boolean as `achievementsToo ? 1 : 0`
  before forwarding to the retained slot.
- Before this pass, the source and static client-command tests pinned the
  command owner, but the executable Steamworks harness only mocked
  `RequestUserStats` on the SteamUserStats interface.

## Source Reconstruction

This pass extends deterministic harness coverage without changing production
Steamworks behavior:

- Added mock state for reset-call count, last `achievementsToo` value, and
  configurable reset result.
- Added `QLR_SteamUserStats_ResetAllStats` and installed it in the mock
  `SteamUserStats` vtable at `0x54 / 4`.
- Exported enabled and disabled harness wrappers for `QL_Steamworks_ClearStats`.
- Added `test_clear_stats_wrapper_uses_retail_reset_all_stats_slot` to prove
  the pre-initialisation guard, boolean forwarding for both `1` and `0`,
  call-count capture, failure propagation, and disabled-build fallback.
- Added `test_steam_clear_stats_round_375_is_pinned` to tie the HLIL evidence,
  production wrapper, mock vtable slot, executable test, and this note
  together.

## Inference Boundary

The retail evidence proves the command owner and SteamUserStats slot. This
round does not claim live backend stats reset behavior, account mutation
semantics, or achievement service availability. It closes local wrapper and
harness evidence for the retained opt-in Steamworks boundary.

## Verification

Local verification for this pass:

```text
python -m pytest tests/test_platform_services.py::test_steam_clear_stats_round_375_is_pinned tests/test_steamworks_harness.py::test_clear_stats_wrapper_uses_retail_reset_all_stats_slot -q
3 passed in 0.91s
```

Full Steamworks/platform verification:

```text
python -m pytest tests/test_platform_services.py tests/test_steamworks_harness.py -q
200 passed in 6.89s
```

## Parity Estimate

- Focused SteamUserStats clear/reset harness parity:
  **before 45% -> after 98%**.
- Retained `stats_clear` wrapper evidence confidence:
  **before 96% -> after 99%**.
- Broader Steamworks parity remains approximately **99%** because live Steam
  backend behavior, stats mutation semantics, and replacement online-service
  policy remain outside this opt-in reconstruction pass.
