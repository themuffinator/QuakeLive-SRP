# quakelive_steam.exe Mapping Round 212

Date: 2026-04-28

Scope: the retained `qcommon/common.c` millisecond/debug/config-command/CD-key
lane around `0x004CAF40` through `0x004CB630`.

## Summary

This round resolved `6` additional `quakelive_steam.exe` aliases and restored a
small but real source-structure split in `src/`.
Classification mix:

- `6` engine-owned functions
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main source reconstruction change is that
[Com_ReadCDKey](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:2680>)
and
[Com_AppendCDKey](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:2723>)
no longer route through the repo-only
`Com_LoadStoredCDKey(...)` helper. They now inline the retained q3key
load/validate/copy path directly, which matches the retail split much more
closely.

## Evidence Notes

- The decisive source anchors for the mapped owners are
  [Com_Milliseconds](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:2532>),
  [Com_Error_f](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:2557>),
  [Com_Freeze_f](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:2574>),
  [Com_ReadCDKey](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:2680>),
  [Com_AppendCDKey](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:2723>),
  and
  [Com_WriteClientConfig_f](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:3290>).
- `sub_4CAF40` is an exact `Com_Milliseconds` match in HLIL: it repeatedly
  pulls a real event with `sub_4CACE0`, re-queues every non-`SE_NONE` event
  through `sub_4CAE10`, and returns the null event's timestamp.
- `sub_4CAF90` and `sub_4CAFC0` are the retained `Com_Error_f` and
  `Com_Freeze_f` debug handlers. The `freeze` owner is especially distinctive
  because it parses `atof( Cmd_Argv(1) )`, captures the starting millisecond
  value through `sub_4CAF40`, and then spins on the same event-draining
  millisecond loop until the requested interval elapses.
- `sub_4CB070` and `sub_4CB170` are the two direct legacy CD-key readers. The
  committed HLIL shows both formatting `"%s/q3key"`, opening the file through
  `FS_SV_FOpenFileRead`, validating placeholder-or-checksummed contents, and
  copying into distinct global destinations. That direct wrapper split is why
  the repo-only `Com_LoadStoredCDKey(...)` abstraction was removed this round.
- `sub_4CB630` is an exact `Com_WriteClientConfig_f` match. The HLIL shows the
  single-argument usage string, `.cfg` default extension, `Writing %s.\n`
  banner, and the final `Com_WriteConfigToFile( filename, NULL, qtrue )`
  behavior.
- Accounting nuance: `sub_4CAF90 -> Com_Error_f` is backed by committed HLIL
  and source behavior, but that address is not enumerated as a standalone
  function in the committed Ghidra `functions.csv`. It therefore increases the
  raw alias total but not the strict address-backed count.

## Aliases Added

- `sub_4CAF40` -> `Com_Milliseconds`
- `sub_4CAF90` -> `Com_Error_f`
- `sub_4CAFC0` -> `Com_Freeze_f`
- `sub_4CB070` -> `Com_ReadCDKey`
- `sub_4CB170` -> `Com_AppendCDKey`
- `sub_4CB630` -> `Com_WriteClientConfig_f`

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
- recount after this pass: `2220` raw alias entries, `2142` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `39.138%` of `5473` functions
- `git diff --check` passed aside from the repo's existing LF -> CRLF
  normalization warnings on touched text files

Parity estimate after this pass:

- strict-retail Windows replacement target: `100%` before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

The next useful adjacent follow-up in this `common.c` neighborhood is the
still-anonymous packet timing/dispatch owner used by
[Com_EventLoop](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:2432>)
for loopback and network packet handling, which should line up with the source
`Com_RunAndTimeServerPacket(...)` seam.
