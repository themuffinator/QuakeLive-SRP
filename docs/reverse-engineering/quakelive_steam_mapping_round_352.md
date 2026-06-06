# Quake Live Steamworks Mapping Round 352

Date: 2026-06-06

Focus: `idSteamStats` descriptor-table replay in the server-owned stats
session.

## Retail evidence

- Owning binary: `assets/quakelive/quakelive_steam.exe`.
- Primary HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`.
- Data-table HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part07.txt`.
- Ghidra companion rows:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  lists `FUN_004670c0`, `FUN_004671d0`, `FUN_004672d0`, and
  `FUN_00467360`.
- Symbol support:
  `references/analysis/quakelive_symbol_aliases.json` maps those functions to
  `SteamStats_FlushPendingValues`, `SteamStats_OnStatsReceived`,
  `SteamStats_SetAchievement`, and `SteamStats_OnStatsStored`.

## Observed facts

The retail `idSteamStats` object carries a descriptor array:

- `arg1 + 0x10` is the stat descriptor count.
- `arg1 + 0x18` points at the descriptor array.
- Each descriptor is advanced by `0x1c` bytes.
- Descriptor offset `+0x04` is the stat type.
- Descriptor offset `+0x08` is the Steam stat name.
- Descriptor offset `+0x0c` is the int value slot for type `0`.
- Descriptor offset `+0x10` is the float/current-value slot for types `1`
  and `2`.
- Descriptor offsets `+0x14` and `+0x18` feed the average-rate update for
  type `2`.

`SteamStats_FlushPendingValues` dispatches by descriptor type:

- Type `0` calls `SteamGameServerStats::SetUserStat(int)` at vtable slot
  `0x14`.
- Type `1` calls `SteamGameServerStats::SetUserStat(float)` at vtable slot
  `0x10`.
- Type `2` calls `SteamGameServerStats::UpdateAvgRateStat` at slot `0x18`,
  then refreshes the float value through `GetUserStat(float)` at slot `0x04`.
- The loop is followed by `StoreUserStats` at slot `0x24`.

`SteamStats_OnStatsReceived` confirms readback:

- Type `0` reads through `GetUserStat(int)` at slot `0x08`.
- Types `1` and `2` read through `GetUserStat(float)` at slot `0x04`.

The committed static data exposes the recovered 88 stat names through
`data_561060` and the 59 achievement names through `data_561c00`. The current
source still has strong name evidence for the 88 qagame-facing stat fields, but
not enough evidence to promote any of those recovered names to type `1` or
type `2`.

## Source reconstruction

- Replaced the bare server stat-name table with
  `sv_steam_stat_descriptor_t`, carrying `name` plus retail descriptor type.
- Added the retail type IDs:
  - `SV_STEAM_STAT_INT = 0`
  - `SV_STEAM_STAT_FLOAT = 1`
  - `SV_STEAM_STAT_AVG_RATE = 2`
- Kept the recovered 88 qagame-facing names as `SV_STEAM_STAT_INT`
  descriptors because no stronger name/type evidence is committed.
- Extended `sv_steam_stats_session_t` with float and average-rate storage:
  current float value, pending float delta, pending average-rate count, and
  pending average-rate session length.
- Changed the value-query path to dispatch by descriptor type:
  int uses `QL_Steamworks_ServerGetUserStatInt`, float and average-rate use
  `QL_Steamworks_ServerGetUserStatFloat`.
- Changed the flush path to dispatch by descriptor type:
  int uses `QL_Steamworks_ServerSetUserStatInt`, float uses
  `QL_Steamworks_ServerSetUserStatFloat`, and average-rate uses
  `QL_Steamworks_ServerUpdateAvgRateStat` plus a float refresh.
- Kept `SV_SteamStats_AddFieldValue` conservative: the qagame import remains
  an int-delta API and declines non-int descriptors instead of inventing
  missing average-rate session semantics.

## Tests

- `tests/test_platform_services.py` now pins:
  - descriptor type constants,
  - the descriptor struct/table,
  - recovered qagame stat names as int descriptors,
  - float and average-rate session fields,
  - type-label diagnostics,
  - int/float/average-rate query and flush wrapper calls.
- Existing Steamworks harness coverage from round 351 continues to pin the
  underlying wrapper vtable slots.

## Inference boundary

This round reconstructs the server owner so it can replay the retail descriptor
types, but it deliberately does not assign float or average-rate types to any
recovered qagame-facing stat names. The exact type map for any non-int retail
descriptors remains open until the committed corpus yields stronger descriptor
initialization evidence or a deliberately scoped live validation pass is run.

## Parity estimate

- Focused server-side descriptor replay lane: **before 54% -> after 86%**.
- Combined focused `idSteamStats` callback/value/descriptor lane:
  **98% -> 99%**.
- Broader Steamworks parity remains approximately **99%**, with live backend
  validation and exact non-int descriptor-name promotion still explicitly
  bounded.
