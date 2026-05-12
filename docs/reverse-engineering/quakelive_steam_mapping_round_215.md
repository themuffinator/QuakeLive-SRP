# quakelive_steam.exe Mapping Round 215

Date: 2026-04-28

Scope: the `qcommon/common.c` startup/profile/runtime utility seam around
`0x004C91B0`, `0x004C93D0`, `0x004C93E0`, and `0x004C9E70`.

## Summary

This round combined source reconstruction with a small alias promotion tranche.
I resolved `3` additional `quakelive_steam.exe` owners and tightened the
remaining `profile.pid` crash-marker check so the checked-in source follows the
retail open/read/close flow instead of a repo-only whole-file helper path.

Classification mix:

- `3` engine-owned functions
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main source win is:

- [Com_ProfilePidIsCurrentProcess](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:218>)
  now opens `profile.pid` through `FS_FOpenFileRead(...)`, reads up to `31`
  bytes through `FS_Read(...)`, closes the file handle directly, and then runs
  `atoi(...)` over the retained buffer. That shape matches the committed HLIL
  much more closely than the previous `FS_ReadFile(...)` plus repo-only digit
  validation lane.

## Evidence Notes

- `sub_4C91B0` matches [Com_RealTime](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:1007>):
  the HLIL is a tiny `_time64(0)` / `_localtime64(...)` owner that conditionally
  copies the `tm_*` fields into the caller buffer and returns the raw time.
- `sub_4C93D0` matches [Com_Crash_f](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:2524>):
  the HLIL is just the intentional null write used for crash-path testing.
- `sub_4C9E70` matches [Com_Quit_f](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:551>):
  the HLIL performs the expected `SV_Shutdown("Server quit\n")`,
  `CL_Shutdown()`, `Com_Shutdown()`, filesystem shutdown, and final quit path.
- The retained `profile.pid` check at `0x004C93E0` does not use a whole-file
  buffer helper. It opens the file, reads a bounded stack buffer, closes the
  handle, and only then evaluates `atoi(...)`, which is why this pass removed
  the stronger repo-only `FS_ReadFile(...)` / per-character numeric validation
  structure.

## Aliases Added

- `sub_4C91B0` -> `Com_RealTime`
- `sub_4C93D0` -> `Com_Crash_f`
- `sub_4C9E70` -> `Com_Quit_f`

## Verification

Static/source validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- `pytest tests/test_engine_command_parity.py tests/test_client_config_parity.py -q --tb=no`
  passed (`19 passed`)
- `pytest tests/test_engine_cvar_retail_parity.py -q --tb=no`
  still reports the same `3` unrelated pre-existing failures in the current
  dirty tree:
  `test_engine_cvar_third_server_tranche_matches_retail_contracts`,
  `test_engine_cvar_fourteenth_core_timing_tranche_matches_retail_contracts`,
  and
  `test_engine_cvar_fifteenth_server_state_tranche_matches_retail_contracts`
  The fifteenth tranche is still failing on the pre-existing
  `QL_Steamworks_ServerSetServerName( sv_hostname->string );` expectation in
  `sv_main.c`, not on this round's `common.c` changes.
- `git diff --check` passed aside from the repo's existing LF -> CRLF
  normalization warnings on touched text files

Alias accounting for the current dirty worktree:

- before this pass: `2222` raw `quakelive_steam` aliases, `2215` strict
  address-backed aliases
- after this pass: `2225` raw `quakelive_steam` aliases, `2218` strict
  address-backed aliases
- strict Ghidra address-backed coverage after this pass: `40.526%` of `5473`
  committed functions

Parity estimate after this pass:

- strict-retail Windows replacement target: `100%` before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

The next useful nearby mapping pass is the remaining `common.c` utility gap
around [Com_HashKey](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:998>)
and the surrounding hash helpers, where the committed HLIL still needs to be
carefully separated from the filename-hash owners in `files.c` and `cvar.c`
before more promotions are safe.
