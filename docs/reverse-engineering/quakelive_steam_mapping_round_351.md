# Quake Live Steamworks Mapping Round 351

Date: 2026-06-06

Focus: `idSteamStats` GameServerStats value wiring for int, float, and
average-rate stat descriptors.

## Retail evidence

- Owning binary: `assets/quakelive/quakelive_steam.exe`.
- Primary HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`.
- Companion Ghidra rows:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  lists `FUN_004670c0`, `FUN_004671d0`, and `FUN_00467360`.
- Import evidence:
  `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
  lists `STEAM_API.DLL!SteamGameServerStats`.
- Symbol support:
  `references/analysis/quakelive_symbol_aliases.json` promotes
  `sub_4670C0` as `SteamStats_FlushPendingValues`,
  `sub_4671D0` as `SteamStats_OnStatsReceived`, and `sub_467360` as
  `SteamStats_OnStatsStored`.

## Observed slot map

`SteamStats_FlushPendingValues` (`0x004670c0`) walks the retained descriptor
array at stride `0x1c` after the ready flag is set.

Observed descriptor behavior:

- Type `0` calls `SteamGameServerStats` slot `0x14` with the descriptor name
  and the int value at descriptor offset `0x0c`.
- Type `1` calls slot `0x10` with the descriptor name and the float value
  derived from descriptor offset `0x10`.
- Type `2` calls slot `0x18` with the descriptor name, count from descriptor
  offset `0x14`, and session length from descriptor offset `0x18`, then calls
  slot `0x04` to refresh the resulting float value into descriptor offset
  `0x10`.
- After the descriptor loop, retail calls slot `0x24` to store the user stats.

`SteamStats_OnStatsReceived` (`0x004671d0`) confirms the readback side:

- Type `0` reads int values through slot `0x08` into descriptor offset `0x0c`.
- Types `1` and `2` read float values through slot `0x04` into descriptor
  offset `0x10`.
- A successful received callback sets the session ready flag.

`SteamStats_OnStatsStored` (`0x00467360`) is retained from the previous round:
result `1` is success, result `8` is partial validation and re-enters the
stats-received path, and other results log failure.

## Reconstructed source surface

- Added `QL_Steamworks_ServerGetUserStatFloat` at slot `0x04`.
- Added `QL_Steamworks_ServerSetUserStatFloat` at slot `0x10`.
- Added `QL_Steamworks_ServerUpdateAvgRateStat` at slot `0x18`.
- Kept the existing int, achievement, and store slots:
  request `0x00`, int get `0x08`, achievement get `0x0c`, int set `0x14`,
  achievement set `0x1c`, and store `0x24`.
- Mirrored these wrappers with disabled-build stubs so live Steam service usage
  remains behind `QL_BUILD_ONLINE_SERVICES` / `QL_BUILD_STEAMWORKS`.
- Extended the Steamworks harness with a full `SteamGameServerStats` mock
  import and vtable so wrapper tests exercise the retail slot map directly.

## Tests

- `tests/test_steamworks_harness.py` now exercises request, int/float read,
  int/float write, average-rate update, achievement, store, disabled stubs,
  and failure zeroing through the harness.
- `tests/test_platform_services.py` pins the public declarations and the
  source-level vtable offsets for the new float and average-rate wrappers.

## Inference boundary

The retail evidence proves the `SteamGameServerStats` import, descriptor type
branches, value offsets, callback readback path, and vtable slots. This round
does not claim the complete semantic meaning of every descriptor name, nor does
it validate live Steam backend behavior. Full descriptor-table replay remains a
future task because it needs either stronger table evidence or a deliberately
scoped live-service validation pass.

## Parity estimate

- Focused GameServerStats value-wrapper lane: **before 72% -> after 94%**.
- Overall focused `idSteamStats` reconstruction after rounds 350 and 351:
  **before 97% -> after 98%**.
- Broader Steamworks parity remains approximately **99%**, with live backend
  validation and full descriptor-table replay still explicitly bounded.
