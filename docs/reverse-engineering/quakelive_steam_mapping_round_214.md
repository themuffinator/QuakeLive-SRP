# quakelive_steam.exe Mapping Round 214

Date: 2026-04-28

Scope: source-structure reconstruction in the adjacent `qcommon/common.c`
profile-marker, config-writer, and CD-key persistence seam.

## Summary

This round was reconstruction-dominant rather than alias-dominant: no new
`quakelive_steam.exe` names were promoted, but several remaining repo-only
helper shells were folded back into the retail owners that the HLIL already
shows.

The main source wins are:

- [Com_Init](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:2823>)
  now formats `com_pid` locally and writes the retained `profile.pid` marker
  directly, instead of routing through the source-only
  `Com_CurrentProcessIdString()` and `Com_WriteProfilePidMarker()` helpers.
- [Com_Shutdown](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:3441>)
  now mirrors the retail `profile.pid` clear more directly with an inline
  `FS_WriteFile( "profile.pid", "0", 1 )` path.
- [Com_WriteConfigToFile](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:3044>)
  now opens and headers the hardware/replicate config files inline, which
  matches the HLIL shape at `0x004CB370` more closely than the old
  `Com_OpenRetailConfigFile(...)` wrapper.
- [Com_ReadCDKey](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:2548>),
  [Com_AppendCDKey](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:2591>),
  and
  [Com_WriteCDKey](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:2635>)
  now follow the retail q3key flow more closely by defaulting to the retained
  blank placeholder, copying validated 16-byte keys directly, and dropping the
  extra source-only `Com_IsPlaceholderCDKey(...)` /
  `Com_SetStoredCDKeyValue(...)` abstraction layer.

## Evidence Notes

- The committed HLIL around `0x004CC106` shows `Com_Init` formatting the live
  process id immediately before registering `com_pid`, rather than calling out
  to a separate helper owner.
- The startup tail near `0x004CC660` and shutdown tail near `0x004C953E`
  perform direct `profile.pid` writes inside the owning functions, which is why
  this pass removed the tiny wrapper layer instead of preserving it as
  repository-only structure.
- The config-writing owner at `0x004CB370` performs the hardware/replicate
  open-and-header sequence inline before emitting bindings, aliases, and cvars.
  That evidence supports deleting `Com_OpenRetailConfigFile(...)`.
- The q3key owners at `0x004CB070`, `0x004CB170`, and `0x004CB2B0` operate on
  direct 16-byte copies and a single validation gate, rather than the checked-in
  placeholder-detection/copier helpers the repo had retained before this pass.

## Aliases Added

- none

## Verification

Static/source validation:

- `pytest tests/test_engine_command_parity.py tests/test_client_config_parity.py -q --tb=no`
  passed (`19 passed`)
- `pytest tests/test_engine_cvar_retail_parity.py -q --tb=no`
  still reports the same `3` unrelated pre-existing failures in the current
  dirty tree:
  `test_engine_cvar_third_server_tranche_matches_retail_contracts`,
  `test_engine_cvar_fourteenth_core_timing_tranche_matches_retail_contracts`,
  and
  `test_engine_cvar_fifteenth_server_state_tranche_matches_retail_contracts`
- alias corpus unchanged from round 213: `2222` raw `quakelive_steam` aliases,
  `2144` strict address-backed aliases, `39.174%` of `5473` committed Ghidra
  functions
- `git diff --check` passed aside from the repo's existing LF -> CRLF
  normalization warnings on touched text files

Parity estimate after this pass:

- strict-retail Windows replacement target: `100%` before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

The next useful pass in this `common.c` neighborhood is the still-more-strict
than retail `Com_ProfilePidIsCurrentProcess(...)` read/parse contract, whose
current checked-in source still performs stronger buffer and digit validation
than the committed HLIL appears to retain.
