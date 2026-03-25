# Quake Live Steam Host Mapping Round 18

## Scope

This round pushes the native `cgamex86.dll` host slab past the Round 17 state/query band and into the next stable retail cluster.

A fresh pass over the host table at `data_565ACC..data_565B14`, the retail `cgamex86.dll` HLIL callsites, and the local `cl_cgame.c` / `ql_cgame_imports.inc` reconstruction now splits that range into three coherent groups:

- the native cgame font/key input seam
- the cinematic wrapper band
- the shared parser imports reused by both native cgame and native UI

The primary local evidence for this round is:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `src/code/client/cl_cgame.c`
- `src/code/client/ql_cgame_imports.inc`
- `src/code/client/cl_keys.c`
- `src/code/client/cl_ui.c`

## Native Cgame Font And Key Slab At `0x174..0x18C`

The next cgame slab band after `MemoryRemaining` is now high-confidence.

Observed local facts:

1. The host slab resolves:
   - `data_565ACC = sub_4AFFF0`
   - `data_565AD0 = sub_4BEFD0`
   - `data_565AD4 = j_sub_4BF010`
   - `data_565AD8 = sub_4B0230`
   - `data_565ADC = sub_4B0240`
   - `data_565AE0 = sub_4B0250`
   - `data_565AE4 = sub_4B0260`
2. Retail cgame uses those entries with stable call shapes:
   - `data_10A25660 = *(result + 0x174)` and later `data_10A25660("fonts/smallfont", 0x10, fontInfo*)`
   - `(*(data_1074CCCC + 0x17C))()` as a bitmask getter used with `KEYCATCH_*` flags
   - `(*(data_1074CCCC + 0x180))(newMask)` to set those flags
   - `(*(data_1074CCCC + 0x184))("vote yes")` returning a key number
   - `(*(data_1074CCCC + 0x188))(keynum, buffer, len)` writing a printable key-name string
   - `(*(data_1074CCCC + 0x18C))(keynum, buffer, len)` writing the command bound to that key
3. `ql_cgame_imports.inc` still exposes the matching native wrappers for:
   - `QL_CG_trap_R_RegisterFont`
   - `QL_CG_trap_Key_IsDown`
   - `QL_CG_trap_Key_GetCatcher`
   - `QL_CG_trap_Key_SetCatcher`
   - `QL_CG_trap_Key_GetKey`
   - `QL_CG_trap_Key_KeynumToStringBuf`
4. `cl_ui.c` carries an exact local helper for the extra retail/native binding-string path:
   - `Key_GetBindingBuf( int keynum, char *buf, int buflen )`

That is enough to treat this band as a coherent cgame font/key seam, including one retail-native binding helper not exposed in the GPL cgame import enum.

### `sub_4AFFF0`

Observed local facts:

1. `sub_4AFFF0` is a pure jump through `data_146CCC8`.
2. The copied callback slot at `data_10A25660` is called as `(fontName, pointSize, fontInfo*)`.
3. `cl_cgame.c` implements `CG_R_REGISTERFONT` as `re.RegisterFont( VMA(1), args[2], VMA(3) )`.

This is the native `R_RegisterFont` wrapper.

### `sub_4BEFD0` And `sub_4B6B10`

Observed local facts:

1. `sub_4BEFD0` is a pure tailcall to `sub_4B6B10`.
2. `sub_4B6B10(int32_t arg1)` returns `0` for `-1`, otherwise returns `*(arg1 * 0xC + &data_1648060)`.
3. `cl_keys.c` implements `Key_IsDown` as `qfalse` for `-1`, otherwise `keys[keynum].down`.

This closes both the native key-down wrapper and its exact host helper.

### `j_sub_4BF010`, `sub_4B0230`, And `sub_4BEEB0`

Observed local facts:

1. `j_sub_4BF010` returns `data_1528BA4`.
2. Retail cgame treats `(*(data_1074CCCC + 0x17C))()` as a catcher bitmask getter and toggles bits `2`, `8`, and `0x10`.
3. `sub_4B0230` tailcalls `sub_4BEEB0`.
4. `sub_4BEEB0(int32_t arg1)` writes `data_1528BA4 = arg1`.

That state-sharing proves the retail `Key_GetCatcher` / `Key_SetCatcher` seam, even though the tiny getter thunk is not currently surfaced as a stable function row in the committed Ghidra `functions.csv`.

### `sub_4B0240` And `sub_4B6CB0`

Observed local facts:

1. `sub_4B0240` is a pure tailcall to `sub_4B6CB0`.
2. `sub_4B6CB0(char* arg1)` scans the key-binding table for a matching binding string and returns the key index or `0xFFFFFFFF`.
3. Retail cgame calls `(*(data_1074CCCC + 0x184))("vote yes")`, `("vote no")`, `("readyup")`, `("dropflag")`, and `("+moveup")`.
4. `cl_keys.c` implements `Key_GetKey( const char *binding )` with the same table scan.

This closes both the native `Key_GetKey` wrapper and its exact host helper.

### `sub_4B0250`, `sub_4B0260`, `sub_4B6570`, `sub_4B6C90`, `sub_4BEE50`, And `sub_4BEE80`

Observed local facts:

1. `sub_4B0250` tailcalls `sub_4BEE50`.
2. `sub_4BEE50(keynum, buf, len)` copies `sub_4B6570(keynum)` into the caller buffer.
3. `sub_4B6570` is the host key-number-to-name helper; `sub_4BEE50` therefore matches `Key_KeynumToStringBuf`.
4. Retail cgame uses `(*(data_1074CCCC + 0x188))(keynum, buffer, len)` exactly that way in vote/readyup/bind-display paths.
5. `sub_4B0260` tailcalls `sub_4BEE80`.
6. `sub_4BEE80(keynum, buf, len)` fetches `sub_4B6C90(keynum)` and copies it into the caller buffer or writes an empty string.
7. `sub_4B6C90` returns the binding string stored for a key number.
8. `cl_ui.c` implements `Key_GetBindingBuf` with the same `Key_GetBinding` plus bounded copy pattern.
9. Retail cgame uses `(*(data_1074CCCC + 0x18C))(keynum, buffer, len)` in `CG_KeyEvent` to recover the bound command string from a pressed key.

This closes both native string-buffer wrappers and the exact host-side helpers behind them.

## Native Cgame Cinematic Slab At `0x194..0x1A4`

The cinematic wrapper band is also stable now.

Observed local facts:

1. The host slab resolves:
   - `data_565AEC = sub_4B0300`
   - `data_565AF0 = sub_4B0310`
   - `data_565AF4 = sub_4BF2B0`
   - `data_565AF8 = sub_4B0320`
   - `data_565AFC = sub_4BF2C0`
2. `cl_cgame.c` implements the matching cgame traps as:
   - `CG_CIN_PLAYCINEMATIC -> CIN_PlayCinematic`
   - `CG_CIN_STOPCINEMATIC -> CIN_StopCinematic`
   - `CG_CIN_RUNCINEMATIC -> CIN_RunCinematic`
   - `CG_CIN_DRAWCINEMATIC -> CIN_DrawCinematic`
   - `CG_CIN_SETEXTENTS -> CIN_SetExtents`
3. Retail cgame wrapper stubs call those slots with the matching signatures:
   - `+0x194` with `(path, x, y, w, h, bits)`
   - `+0x198` with `(handle)`
   - `+0x19C` with `(handle)`
4. The host helper bodies match the cinematic ownership:
   - `sub_4B3160` prints `SCR_PlayCinematic( %s )`
   - `sub_4B2400` closes or transitions an FMV handle
   - `sub_4B2F40` advances and returns cinematic state
   - `sub_4B24D0` draws the active cinematic surface
   - `sub_4B2480` stores `(x, y, w, h)` extents for a handle

That is enough to promote both the import wrappers and the exact host cinematic helpers.

## Shared Parser Continuation At `0x1AC..0x1BC`

This round also closes the ownership of the next cgame parser band, but it does not need new aliases.

Observed local facts:

1. The cgame slab continues with:
   - `data_565B04 = sub_4E1740`
   - `data_565B08 = sub_4B0270`
   - `data_565B0C = sub_4B0290`
   - `data_565B10 = sub_4B02B0`
   - `data_565B14 = sub_4B02D0`
2. Retail cgame uses:
   - `(*(data_1074CCCC + 0x1B0))(path)` as `PC_LoadSource`
   - `(*(data_1074CCCC + 0x1B4))(handle)` as `PC_FreeSource`
   - `(*(data_1074CCCC + 0x1B8))(handle, token)` as `PC_ReadToken`
   - `(*(data_1074CCCC + 0x1BC))(handle, filename, line)` as `PC_SourceFileAndLine`
3. Those functions were already promoted earlier from the shared host parser seam.

So this pass does not rename them again; it just records that native cgame reuses the same shared parser wrappers already mapped in prior rounds.

## Promoted Aliases

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4AFFF0` (`0x004AFFF0`) | `QLCGImport_R_RegisterFont` | Observed | Native cgame import wrapper for `RegisterFont(fontName, pointSize, fontInfo*)`. |
| `sub_4BEFD0` (`0x004BEFD0`) | `QLCGImport_Key_IsDown` | Observed | Native cgame import wrapper for key-down queries. |
| `sub_4B0230` (`0x004B0230`) | `QLCGImport_Key_SetCatcher` | Observed | Native cgame import wrapper for the key-catcher mask setter. |
| `sub_4B0240` (`0x004B0240`) | `QLCGImport_Key_GetKey` | Observed | Native cgame import wrapper for binding-string to keynum lookup. |
| `sub_4B0250` (`0x004B0250`) | `QLCGImport_Key_KeynumToStringBuf` | Observed | Native cgame import wrapper for keynum-to-name string conversion. |
| `sub_4B0260` (`0x004B0260`) | `QLCGImport_Key_GetBindingBuf` | Observed | Native cgame import wrapper for keynum-to-bound-command string lookup. |
| `sub_4B0300` (`0x004B0300`) | `QLCGImport_CIN_PlayCinematic` | Observed | Native cgame import wrapper for cinematic startup. |
| `sub_4B0310` (`0x004B0310`) | `QLCGImport_CIN_StopCinematic` | Observed | Native cgame import wrapper for cinematic stop/close. |
| `sub_4BF2B0` (`0x004BF2B0`) | `QLCGImport_CIN_RunCinematic` | Observed | Native cgame import wrapper for per-frame cinematic advancement. |
| `sub_4B0320` (`0x004B0320`) | `QLCGImport_CIN_DrawCinematic` | Observed | Native cgame import wrapper for cinematic drawing. |
| `sub_4BF2C0` (`0x004BF2C0`) | `QLCGImport_CIN_SetExtents` | Observed | Native cgame import wrapper for cinematic rectangle updates. |
| `sub_4B6570` (`0x004B6570`) | `Key_KeynumToString` | Observed | Host helper returning the printable key-name string for one key number. |
| `sub_4B6B10` (`0x004B6B10`) | `Key_IsDown` | Observed | Exact host key-down helper over the key-state table. |
| `sub_4B6C90` (`0x004B6C90`) | `Key_GetBinding` | Observed | Host helper returning the binding string stored for one key number. |
| `sub_4B6CB0` (`0x004B6CB0`) | `Key_GetKey` | Observed | Exact host binding-string to keynum lookup helper. |
| `sub_4BEE50` (`0x004BEE50`) | `Key_KeynumToStringBuf` | Observed | Host helper copying the printable key-name string into a caller buffer. |
| `sub_4BEE80` (`0x004BEE80`) | `Key_GetBindingBuf` | Observed | Host helper copying the bound command string into a caller buffer. |
| `sub_4BEEB0` (`0x004BEEB0`) | `Key_SetCatcher` | Observed | Exact host setter for the key-catcher mask at `data_1528BA4`. |
| `sub_4B2400` (`0x004B2400`) | `CIN_StopCinematic` | Observed | Exact host cinematic stop/close helper. |
| `sub_4B2480` (`0x004B2480`) | `CIN_SetExtents` | Observed | Exact host cinematic extents setter. |
| `sub_4B24D0` (`0x004B24D0`) | `CIN_DrawCinematic` | Observed | Exact host cinematic draw helper. |
| `sub_4B2F40` (`0x004B2F40`) | `CIN_RunCinematic` | Observed | Exact host cinematic frame-advance helper. |
| `sub_4B3160` (`0x004B3160`) | `CIN_PlayCinematic` | Observed | Exact host cinematic startup helper. |

## Open Questions

1. The `Key_GetCatcher` getter entry is semantically closed, but I am not promoting a new alias for the tiny `j_sub_4BF010` thunk this round because the committed Ghidra `functions.csv` does not currently surface a stable `004BF010` function row.
2. Import `0x1A8` (`sub_4B0330`) still needs a direct cgame callsite before promotion; it likely lives in the `GetEntityToken` / `inPVS` neighborhood, but I do not yet have the second signal needed to rename it safely.
3. Import `0x1C8` (`sub_4B0350`) is still only weakly constrained by the no-arg call at `100115D8`; it likely belongs to the small post-cinematic utility band, but not tightly enough to promote.
