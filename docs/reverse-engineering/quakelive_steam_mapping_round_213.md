# quakelive_steam.exe Mapping Round 213

Date: 2026-04-28

Scope: the adjacent `qcommon/common.c` startup/profile/config-writing seam
around `0x004C9390` and `0x004C93E0`, plus source-structure cleanup in the
same neighborhood.

## Summary

This round resolved `2` additional `quakelive_steam.exe` aliases and performed
a source-reconstruction pass that removes several repo-only structural helpers
from the corresponding `common.c` lane.
Classification mix:

- `2` engine-owned functions
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main source wins are:

- [Com_RunAndTimeServerPacket](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:2388>)
  is now the thin `SV_PacketEvent(...)` wrapper the retail HLIL shows, instead
  of the older timing/profiling wrapper the checked-in tree had retained.
- [Com_Init](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:2922>)
  now inlines the pushed-event reset sequence that the retail executable keeps
  inside the common startup owner, so the repo-only `Com_InitPushEvent()`
  helper has been removed.
- [Com_WriteConfig_f](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:3230>)
  and
  [Com_WriteClientConfig_f](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:3272>)
  now restore the retail direct single-file write path instead of routing those
  cases back through the shared `Com_WriteConfigToFile(...)` helper.

## Evidence Notes

- `sub_4C9390` is now promoted as `Com_RunAndTimeServerPacket`. The committed
  HLIL shows a tiny wrapper that simply forwards the unpacked `netadr_t` and
  `msg_t` payload to `SV_PacketEvent(...)`; it does not retain the older
  `com_speeds` timing branch present in the checked-in source before this pass.
- `sub_4C93E0` is now promoted as `Com_ProfilePidIsCurrentProcess`. The HLIL
  matches the retained `profile.pid` check closely: it reads the file, rejects
  malformed or non-numeric contents, parses the retained PID, and returns
  `qfalse` only when the stored positive PID disagrees with `com_pid`.
- The startup evidence near `0x004CBFD0` still shows the pushed-event buffer
  reset inlined directly into `Com_Init` via a `memset( ... 0x6000 )` followed
  by head/tail counter zeroing. That is why the repo-only
  `Com_InitPushEvent()` helper was removed instead of merely being left unused.
- The config-command HLIL at `0x004CB4D0` and `0x004CB630` still shows the
  direct single-file writer paths opening the target file, printing the retail
  header, writing bindings/aliases/cvars directly, and then closing the handle.
  Reconstructing those direct paths brings the checked-in source much closer to
  the retail function boundaries than the prior shared-helper-only shape.

## Aliases Added

- `sub_4C9390` -> `Com_RunAndTimeServerPacket`
- `sub_4C93E0` -> `Com_ProfilePidIsCurrentProcess`

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
- recount after this pass: `2222` raw alias entries, `2144` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `39.174%` of `5473` functions
- `git diff --check` passed aside from the repo's existing LF -> CRLF
  normalization warnings on touched text files

Parity estimate after this pass:

- strict-retail Windows replacement target: `100%` before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

The next useful follow-up in this `common.c` neighborhood is the remaining
repo-only CD-key normalization helper layer around
`Com_IsPlaceholderCDKey(...)` and `Com_SetStoredCDKeyValue(...)`, which still
looks more abstract than the direct retail q3key load/write owners now do.
