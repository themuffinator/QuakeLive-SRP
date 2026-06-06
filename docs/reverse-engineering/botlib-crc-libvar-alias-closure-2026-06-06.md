# Botlib CRC And Libvar Alias Closure - 2026-06-06

## Scope

This pass closes the unpromoted support-runtime rows immediately after
`GetBotLibAPI` in `quakelive_steam.exe`. The selected range is
`0x004A84B0..0x004A8790`, covering the botlib CRC16 route-cache helper and the
runtime libvar helpers used by AAS setup, routing, and qagame bot bootstrap
wiring.

No C source body change was needed. The checked-in source already matches the
retail static shape for this slice.

## Evidence

- `references/analysis/quakelive_symbol_aliases.json`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part03.txt`
- `src/code/botlib/l_crc.c`
- `src/code/botlib/l_libvar.c`
- `src/code/botlib/be_aas_route.c`
- `src/code/botlib/be_interface.c`
- `tests/test_botlib_crc_libvar_alias_closure_parity.py`

## Promotions

| Address | Alias | Evidence |
| --- | --- | --- |
| `0x004A84B0` | `CRC_ProcessString` | HLIL initializes `0xffff`, folds each byte through `data_5643e8`, and returns the CRC. Source route-cache read/write calls `CRC_ProcessString` over AAS area and cluster tables. |
| `0x004A8500` | `LibVarStringValue` | Decimal-only parser; rejects second decimal point and non-digit bytes. |
| `0x004A8590` | `LibVarAlloc` | Allocates `0x18 + strlen(name) + 1`, clears `0x18`, stores inline name, and pushes onto `libvarlist`. |
| `0x004A85F0` | `LibVarDeAllocAll` | Walks `libvarlist`, frees value strings, frees nodes, and clears the head. |
| `0x004A8640` | `LibVarGetString` | Case-insensitive lookup, returns string or the static empty string. |
| `0x004A8680` | `LibVarGetValue` | Case-insensitive lookup, returns cached float or `0`. |
| `0x004A86C0` | `LibVar` | Find-or-create path, value-string allocation, cached float parse, modified flag. |
| `0x004A8750` | `LibVarString` | Thin wrapper returning `LibVar(...)->string`. |
| `0x004A8770` | `LibVarValue` | Thin wrapper returning `LibVar(...)->value`. |
| `0x004A8790` | `LibVarSet` | Find-or-create path, frees old string when present, reparses value, marks modified. |

## Negative Classification

`LibVarGet` and `LibVarDeAlloc` remain source-visible helpers but are not
promoted as standalone retail aliases. Their source behavior is visible in the
emitted callers:

- `LibVarGet` is inlined into `LibVarGetString`, `LibVarGetValue`, `LibVar`,
  and `LibVarSet` as repeated `libvarlist` traversal plus `Q_stricmp`.
- `LibVarDeAlloc` is inlined into `LibVarDeAllocAll` as the value-string free
  followed by the node free.

This matches the existing reconstruction posture: keep useful source helpers
for readability, but promote only owners emitted as retail functions.

## Wiring Notes

- `CRC_ProcessString` feeds `routecacheheader.areacrc` and
  `routecacheheader.clustercrc` during `AAS_WriteRouteCache`, then validates
  the same AAS area and cluster tables during `AAS_ReadRouteCache`.
- `Export_BotLibVarSet` calls `LibVarSet` and returns `BLERR_NOERROR`.
- `Export_BotLibVarGet` calls `LibVarGetString`, copies into the caller buffer,
  terminates at `size - 1`, and returns `BLERR_NOERROR`.
- The existing qagame bridge maps `BOTLIB_LIBVAR_SET/GET` through both the
  legacy VM syscall switch and the Quake Live native import table.

## Parity Estimate

- Focused CRC/libvar alias ownership:
  **before 76% -> after 99%**
- Route-cache CRC owner mapping:
  **before 88% -> after 98%**
- Overall botlib support/runtime mapping:
  **before 83% -> after 84%**

The overall movement is modest because this pass promotes source owners and
guards already reconstructed behavior rather than adding new bot runtime
behavior.

## Validation

- `python -m pytest tests/test_botlib_crc_libvar_alias_closure_parity.py -q`
  - `3 passed`
