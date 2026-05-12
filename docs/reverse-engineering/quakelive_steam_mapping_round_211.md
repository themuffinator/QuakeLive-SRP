# quakelive_steam.exe Mapping Round 211

Date: 2026-04-28

Scope: the retained `qcommon/common.c` memory, hunk, journaling, and pushed
event lane around `0x004CA010` through `0x004CAEB0`.

## Summary

This round resolved `16` additional `quakelive_steam.exe` aliases across a
single high-confidence `common.c` owner block.
Classification mix:

- `16` engine-owned functions
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

This was a mapping-dominant pass rather than a reconstruction pass. The
checked-in source already matches the retail behaviors in this lane closely
enough that the main value was promoting the anonymous owners and extending the
focused parity fence around them.

## Evidence Notes

- The decisive source anchors are
  [Info_Print](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:847>),
  [Z_Free](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:1172>),
  [Z_TagMalloc](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:1276>),
  [Z_Malloc](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:1367>),
  [S_Malloc](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:1388>),
  [Z_CheckHeap](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:1398>),
  [CopyString](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:1509>),
  [Com_InitSmallZoneMemory](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:1742>),
  [Com_InitZoneMemory](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:1754>),
  [Hunk_Clear](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:1971>),
  [Hunk_AllocateTempMemory](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:2102>),
  [Hunk_FreeTempMemory](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:2151>),
  [Com_InitJournaling](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:2270>),
  [Com_GetRealEvent](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:2300>),
  [Com_PushEvent](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:2361>),
  and
  [Com_GetEvent](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:2392>).
- HLIL matches were especially direct in this block:
  `sub_4CA010` shows the retained backslash-delimited info printer with the
  `20`-column key padding and `"MISSING VALUE\n"` fallback;
  `sub_4CA1D0` through `sub_4CA470` are the zone allocator/free/copy string
  cluster;
  `sub_4CA790` and `sub_4CA840` are the small/main zone allocators;
  `sub_4CA910`, `sub_4CAAA0`, and `sub_4CAB80` cover the hunk reset/temp
  allocation lane;
  and `sub_4CAC00` through `sub_4CAEB0` are the journaling plus pushed-event
  queue owners.
- The journaling/event subsection is backed by distinctive retained literals
  and control flow, including `"journal.dat"`,
  `"Couldn't open journal files\n"`,
  `"Error reading from journal file"`,
  `"Error writing to journal file"`,
  and `"WARNING: Com_PushEvent overflow\n"`.
- One nearby nuance worth preserving for future passes:
  the retail `Com_Init` body appears to inline the pushed-event reset sequence
  that the checked-in tree still exposes as
  [Com_InitPushEvent](</E:/Repositories/QuakeLive-reverse/src/code/qcommon/common.c:2345>).
  That is a good reminder not to over-interpret helper boundaries when the
  behavioral owner is already clear.

## Aliases Added

- `sub_4CA010` -> `Info_Print`
- `sub_4CA1D0` -> `Z_Free`
- `sub_4CA2C0` -> `Z_TagMalloc`
- `sub_4CA3A0` -> `Z_Malloc`
- `sub_4CA3D0` -> `S_Malloc`
- `sub_4CA3F0` -> `Z_CheckHeap`
- `sub_4CA470` -> `CopyString`
- `sub_4CA790` -> `Com_InitSmallZoneMemory`
- `sub_4CA840` -> `Com_InitZoneMemory`
- `sub_4CA910` -> `Hunk_Clear`
- `sub_4CAAA0` -> `Hunk_AllocateTempMemory`
- `sub_4CAB80` -> `Hunk_FreeTempMemory`
- `sub_4CAC00` -> `Com_InitJournaling`
- `sub_4CACE0` -> `Com_GetRealEvent`
- `sub_4CAE10` -> `Com_PushEvent`
- `sub_4CAEB0` -> `Com_GetEvent`

## Verification

Static/source validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- `pytest tests/test_engine_command_parity.py -q --tb=no`
  passed (`14 passed`)
- `pytest tests/test_engine_cvar_retail_parity.py -q --tb=no`
  still reports the same `3` unrelated pre-existing failures in the current
  dirty tree:
  `test_engine_cvar_third_server_tranche_matches_retail_contracts`,
  `test_engine_cvar_fourteenth_core_timing_tranche_matches_retail_contracts`,
  and
  `test_engine_cvar_fifteenth_server_state_tranche_matches_retail_contracts`
- recount after this pass: `2214` raw alias entries, `2137` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `39.046%` of `5473` functions
- `git diff --check` passed aside from the repo's existing LF -> CRLF
  normalization warnings on touched text files

Parity estimate after this pass:

- strict-retail Windows replacement target: `100%` before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

The next useful nearby follow-up is the surrounding `Com_Init(...)` ownership
lane around `0x004CC07C`, where the retail binary inlines the pushed-event
reset/setup sequence before entering the rest of common-system initialization.
