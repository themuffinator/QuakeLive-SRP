# quakelive_steam.exe Mapping Round 216

Date: 2026-04-28

Scope: the `qcommon/common.c` utility seam around `0x004C9160` and the
Windows client idle-sleep helper at `0x004ED7E0`.

## Summary

This round resolved `2` additional `quakelive_steam.exe` aliases and performed
one small retail-shape cleanup in the same source lane.

Classification mix:

- `2` engine-owned functions
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main source win is:

- [Com_IdleSleep](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:161>)
  now mirrors the retail Windows owner more closely by issuing the waitable
  timer create/set/wait/close sequence directly, instead of retaining the
  extra repo-only `!timer` fallback and `SetWaitableTimer(...)` success guard.

## Evidence Notes

- `sub_4C9160` matches [Com_HashKey](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:984>):
  the HLIL shows the exact bounded loop over `arg2`, the `(119 + i)` weighted
  accumulation, and the final `hash ^ (hash >> 10) ^ (hash >> 20)` reduction.
  Unlike the later filename-hash owners in `files.c` and `cvar.c`, this owner
  does not lowercase characters or normalize path separators.
- `sub_4ED7E0` matches [Com_IdleSleep](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:161>):
  the HLIL is the straight Windows waitable-timer helper used from
  [Com_Frame](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:3236>)
  when the client-side idle throttle path is active.
- The retail helper at `0x004ED7E0` calls `CreateWaitableTimerA(...)`,
  `SetWaitableTimer(...)`, `WaitForSingleObject(...)`, and `CloseHandle(...)`
  directly. That evidence is why this pass removed the source-only fallback
  `Sleep( msec )` path and the conditional wait wrapper.

## Aliases Added

- `sub_4C9160` -> `Com_HashKey`
- `sub_4ED7E0` -> `Com_IdleSleep`

## Verification

Static/source validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- `pytest tests/test_engine_command_parity.py tests/test_client_config_parity.py -q --tb=no`
  passed (`19 passed`)
- `pytest tests/test_engine_cvar_retail_parity.py -q --tb=no`
  still reports the same `3` dirty-tree failures:
  `test_engine_cvar_third_server_tranche_matches_retail_contracts`,
  `test_engine_cvar_fourteenth_core_timing_tranche_matches_retail_contracts`,
  and
  `test_engine_cvar_fifteenth_server_state_tranche_matches_retail_contracts`
  The touched core-timing tranche still fails on the pre-existing
  `g_main.c` `g_timelimit` expectation, not on this round's `Com_IdleSleep`
  reconstruction.
- `git diff --check` passed aside from the repo's existing LF -> CRLF
  normalization warnings on touched text files

Alias accounting for the current dirty worktree:

- before this pass: `2225` raw `quakelive_steam` aliases, `2218` strict
  address-backed aliases
- after this pass: `2227` raw `quakelive_steam` aliases, `2220` strict
  address-backed aliases
- strict Ghidra address-backed coverage after this pass: `40.563%` of `5473`
  committed functions

Parity estimate after this pass:

- strict-retail Windows replacement target: `100%` before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

The next useful nearby pass is the remaining startup-policy/helper lane around
`Com_ShouldDefaultDedicatedFromExecutable(...)`, where the checked-in source
still carries local executable-name compatibility logic that should be kept
carefully separated from strict retail-owner naming.
