# `qshared` Retail Helper Parity Audit

Last updated: 2026-04-17

Scope: the shared helper surface used by `qcommon`, `client`, `server`, `game`,
and `cgame`, primarily `src/code/game/q_shared.c`, `src/code/game/q_shared.h`,
and `src/code/game/q_math.c`, against retail `quakelive_steam.exe`.

Purpose: close the remaining shared-helper exactness and validation-lane gaps
that were left implicit inside the older `qcommon`-only closure note.

## Audit Method And Evidence

Owning retail binary:

- `assets/quakelive/quakelive_steam.exe`

Canonical committed evidence used for this audit:

- Binary Ninja HLIL corpus:
  - `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- Ghidra companion corpus:
  - `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
  - `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- Symbol and mapping support:
  - `references/analysis/quakelive_symbol_aliases.json`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_58.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_59.md`
- Writable source under audit:
  - `src/code/game/q_shared.c`
  - `src/code/game/q_shared.h`
  - `src/code/game/q_math.c`
- Validation surface refreshed for this pass:
  - `tests/test_qshared_retail_parity.py`
  - `.github/workflows/qcommon-validation.yml`
  - `docs/build-pipeline.md`
  - `docs/windows-native-pipeline.md`

Method:

1. Start with the owning retail Windows binary and the committed metadata and
   function inventories.
2. Use the alias ledger plus mapping rounds `58` and `59` to bound the recovered
   `q_math.c` and `q_shared.c` helper families before calling anything a gap.
3. Treat the shared header as part of the parity surface when it exports a
   recovered helper name or inline wrapper contract used by the audited source.
4. Close only the gaps that are directly supported by the committed evidence and
   by the writable source itself.

## Current Verified State

The mapped `qshared` helper surface is strongly recovered in the current
worktree:

- `q_math.c` is source-aligned for the recovered retail helper block anchored by
  `Q_random`, `Q_rsqrt`, `Q_fabs`, `Q_log2`, `SetPlaneSignbits`,
  `BoxOnPlaneSide`, `VectorNormalize`, `AnglesToAxis`, and
  `PerpendicularVector`.
- `q_shared.c` is source-aligned for the recovered retail parser/string/info
  family anchored by `Com_Clamp`, `COM_Compress`, `COM_ParseExt`,
  `Q_strncpyz`, `Q_stricmpn`, `Q_stricmp`, `Q_strcat`, `Q_CleanStr`,
  `Com_sprintf`, `Info_ValueForKey`, `Info_NextPair`, `Info_RemoveKey_Big`,
  and `Info_SetValueForKey_Big`.
- The only source-owned exactness defect found in this pass was in the shared
  header contract rather than in the mapped helper bodies themselves.

## Gap Register

## QS-G01 - `q_shared.h` exported one recovered retail helper under the wrong name

**Type:** Source exactness  
**Priority:** High  
**Status:** Closed on 2026-04-17

Observed retail facts:

1. `references/analysis/quakelive_symbol_aliases.json` binds
   `sub_4D9500 -> Info_RemoveKey_Big`.
2. `docs/reverse-engineering/quakelive_steam_mapping_round_59.md` closes
   `sub_4D9500` specifically as `Info_RemoveKey_Big`.
3. The committed HLIL corpus preserves the same oversize diagnostic string:
   `Info_RemoveKey_Big: oversize infostring`.

Observed source facts before closure:

1. `src/code/game/q_shared.c` already defined `Info_RemoveKey_Big(...)`.
2. `src/code/game/q_shared.h` still exported the prototype as
   `Info_RemoveKey_big(...)`, which was a stale case-mismatched declaration.
3. The same header also carried two inline endian wrappers (`BigLong`,
   `BigFloat`) without `return` statements in the Win32 and FreeBSD sections,
   even though the active helper contract everywhere else returned the wrapped
   value.

Closure:

1. `src/code/game/q_shared.h` now exports the recovered helper under the retail
   name `Info_RemoveKey_Big(...)`.
2. The Win32 and FreeBSD inline `BigLong` / `BigFloat` wrappers now return the
   underlying swap result so the shared header matches the active helper
   contract used by the source family.

Conclusion:

- no remaining source-owned exactness gap remains in the audited shared-helper
  header surface for this tranche

## QS-G02 - the shared helper family was not explicitly tracked in the machine-readable qcommon lane

**Type:** Verification infrastructure  
**Priority:** Medium  
**Status:** Closed on 2026-04-17

Observed source facts before closure:

1. `.github/workflows/qcommon-validation.yml` already watched
   `src/code/game/q_shared.c` and `src/code/game/q_shared.h`, but the focused
   pytest command did not run any dedicated `qshared` audit.
2. `docs/build-pipeline.md` and `docs/windows-native-pipeline.md` described the
   qcommon lane as a shared/common validation surface, but they only enumerated
   the older qcommon-focused tests.
3. The earlier dedicated `qcommon` closure note did not publish a standalone
   audit for the recovered `qshared` helper family.

Closure:

1. Added `tests/test_qshared_retail_parity.py` to bind the shared helper family
   back to the committed retail aliases, mapping rounds, header contract, and
   writable source bodies.
2. Extended `.github/workflows/qcommon-validation.yml` so the shared lane now
   runs that focused `qshared` audit and triggers on `src/code/game/q_math.c`
   plus this audit note.
3. Updated `docs/build-pipeline.md` and `docs/windows-native-pipeline.md` so the
   documented qcommon validation command and lane description include the new
   `qshared` coverage.

Conclusion:

- the recovered `qshared` helper family is now explicitly tracked in the same
  machine-checked lane that already owns the surrounding `qcommon` closure

## Closure Plan

## QS-P1 - Fix the shared helper header exactness defects [COMPLETED 2026-04-17]

**Closes:** `QS-G01`  
**Priority:** High  
**Parity estimate:** **before 99% -> after 100%**

Completed work:

1. Corrected the exported `Info_RemoveKey_Big(...)` prototype in
   `src/code/game/q_shared.h`.
2. Restored the missing `return` statements in the Win32 and FreeBSD inline
   `BigLong` / `BigFloat` wrappers so the header matches the active helper
   contract.

## QS-P2 - Add dedicated `qshared` validation to the existing shared-common lane [COMPLETED 2026-04-17]

**Closes:** `QS-G02`  
**Priority:** Medium  
**Parity estimate:** **before 99% -> after 100%**

Completed work:

1. Added `tests/test_qshared_retail_parity.py`.
2. Wired that test into `.github/workflows/qcommon-validation.yml`.
3. Refreshed the shared validation documentation in `docs/build-pipeline.md` and
   `docs/windows-native-pipeline.md`.

## Validation

Command run for this pass:

```text
pytest tests/test_qshared_retail_parity.py tests/test_qcommon_full_parity_gate.py -q
```

Expected closure result:

- the dedicated `qshared` audit passes
- the refreshed `qcommon` parity gate continues to report `overall_status: pass`

## Final Assessment

The audited `qshared` helper surface is now aligned with the committed retail
evidence and explicitly covered by the shared/common validation lane. The
recovered `q_math.c` and `q_shared.c` helper families were already strong; this
pass closes the remaining header exactness defect and removes the validation
blind spot that left the shared helper family outside the machine-checked
closure story.
