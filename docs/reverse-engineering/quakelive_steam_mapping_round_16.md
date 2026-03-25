# Quake Live Steam Host Mapping Round 16

## Scope

This round cleans up the last straightforward native UI import-slab entries after the advertisement extension work in Rounds 14 and 15.

The remaining unmapped UI slab tail at `0x158..0x160` turns out to split cleanly into:

- two retained host cursor-position wrappers around Win32 APIs
- the missing parser `PC_AddGlobalDefine` import immediately before the already-mapped `PC_LoadSource/FreeSource/ReadToken/SourceFileAndLine` block

The primary local evidence for this round is:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/hlil/quakelive/uix86.all/uix86.dll_hlil.txt`
- `src/code/client/cl_ui.c`
- `src/code/client/ql_ui_imports.inc`

## UI Slab Tail At `0x158..0x160`

The owning host entries are now stable enough to document directly.

Observed local facts:

1. The native UI slab still maps:
   - `data_567490 = sub_4B0340` at import `86` / offset `0x158`
   - `data_567494 = sub_4BEF20` at import `87` / offset `0x15C`
   - `data_567498 = sub_4E1740` at import `88` / offset `0x160`
2. The next four entries are the already-promoted parser wrappers:
   - `sub_4B0270`, `sub_4B0290`, `sub_4B02B0`, `sub_4B02D0`
3. `cl_ui.c` and `ql_ui_imports.inc` still expose `UI_PC_ADD_GLOBAL_DEFINE` locally even though the native UI import slab had not yet been named at that offset.

That is enough to treat `0x160` as part of the parser subcluster, and `0x158/0x15C` as retained UI host utilities immediately ahead of it.

## Import `0x160`: `PC_AddGlobalDefine`

The missing parser import is now high-confidence.

Observed local facts:

1. `sub_4E1740` is a jump wrapper through `data_13E1844 + 0x200`.
2. The four parser imports mapped in Round 14 use the immediately following targets:
   - `sub_4B0270 -> data_13E1844 + 0x204`
   - `sub_4B0290 -> data_13E1844 + 0x208`
   - `sub_4B02B0 -> data_13E1844 + 0x20C`
   - `sub_4B02D0 -> data_13E1844 + 0x210`
3. In `cl_ui.c`, the parser syscall order is:
   - `UI_PC_ADD_GLOBAL_DEFINE`
   - `UI_PC_LOAD_SOURCE`
   - `UI_PC_FREE_SOURCE`
   - `UI_PC_READ_TOKEN`
   - `UI_PC_SOURCE_FILE_AND_LINE`
4. `ql_ui_imports.inc` still carries the matching `QL_UI_trap_PC_AddGlobalDefine` wrapper.

That ordering makes `sub_4E1740` the natural and stable host-side `PC_AddGlobalDefine` wrapper.

## Imports `0x158` And `0x15C`: Cursor Position Wrappers

The two preceding host helpers are exact Win32 shims.

### `sub_4B0340`

Observed local facts:

1. `sub_4B0340` is a pure tailcall to `sub_4EAB30`.
2. `sub_4EAB30(int32_t arg1, int32_t arg2)` calls `SetCursorPos(X: arg1, Y: arg2)` directly and returns its `BOOL`.

This is not a generic UI callback anymore; it is a direct host cursor-position setter retained in the UI slab.

### `sub_4BEF20`

Observed local facts:

1. `sub_4BEF20` is a pure tailcall to `sub_4EAB50`.
2. `sub_4EAB50(int32_t* arg1, int32_t* arg2)` calls `GetCursorPos(&point)` and writes `point.x` / `point.y` back through the two out-pointers.

This is the paired host cursor-position getter retained in the same slab.

## Retail UI Usage Notes

The retail `uix86.dll` HLIL does not currently show direct calls through `data_106B40A8 + 0x158` or `+ 0x15C`.

Observed local facts:

1. Raw import-offset scans in `uix86.dll` do not currently show direct `(*(data_106B40A8 + 0x158))` or `(*(data_106B40A8 + 0x15C))` callsites.
2. The retail UI still keeps those wrappers in the native host slab even though the current menu code appears not to call them directly.

So these are stable host mappings, but likely retained utility imports rather than hot retail UI paths.

## Promoted Aliases

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4B0340` (`0x004B0340`) | `QLUIImport_SetCursorPos` | Observed | UI slab wrapper around the host cursor-position setter. |
| `sub_4BEF20` (`0x004BEF20`) | `QLUIImport_GetCursorPos` | Observed | UI slab wrapper around the host cursor-position getter. |
| `sub_4E1740` (`0x004E1740`) | `QLUIImport_PC_AddGlobalDefine` | Observed | UI slab wrapper for the parser `PC_AddGlobalDefine` import immediately preceding the already-mapped parser block. |
| `sub_4EAB30` (`0x004EAB30`) | `Win32_SetCursorPos` | Observed | Direct host wrapper over `SetCursorPos`. |
| `sub_4EAB50` (`0x004EAB50`) | `Win32_GetCursorPos` | Observed | Direct host wrapper over `GetCursorPos`. |

## Open Questions

1. The retail UI still appears not to call imports `86` and `87` directly, so their original higher-level Quake Live ownership remains thin even though the host semantics are exact.
2. UI import `85` (`j_sub_4D7980`) remains a no-op placeholder.
3. The lower advertisement shader suppliers `sub_4F20E0` and `sub_4F2120` are still constrained but not finally named at the bridge level.
