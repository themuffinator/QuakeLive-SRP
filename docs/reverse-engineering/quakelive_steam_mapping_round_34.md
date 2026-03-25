# Quake Live Steam Host Mapping Round 34

## Scope

This round closes the raw native `cgamex86.dll` filesystem seam immediately before the already-mapped command/collision block at `data_5659AC`.

The focus was the stable wrapper block at host raw offsets `+0x38..+0x50`, plus the owning engine helpers behind that block. The goal was to promote only the entries whose public behavior is pinned by both:

- committed `functions.csv` rows in the `quakelive_steam` Ghidra corpus
- direct raw `data_1074CCCC + offset` call shapes in native `cgamex86.dll`
- source-backed filesystem helper bodies in `files.c`

The primary local evidence for this round is:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `src/code/qcommon/files.c`
- `src/code/qcommon/qcommon.h`
- `src/code/client/cl_ui.c`
- `src/code/client/ql_ui_imports.inc`
- `src/code/client/cl_cgame.c`
- `src/code/client/ql_cgame_imports.inc`

## Raw Filesystem Wrappers At `+0x38..+0x50`

The raw native cgame filesystem tail now closes cleanly.

Observed local facts:

1. The owning host slots are:
   - `data_565990 = sub_4EA330` (`+0x38`)
   - `data_565994 = sub_4EA340` (`+0x3C`)
   - `data_565998 = sub_4EA350` (`+0x40`)
   - `data_56599C = sub_4EA360` (`+0x44`)
   - `data_5659A0 = sub_4ED040` (`+0x48`)
   - `data_5659A4 = sub_4EA370` (`+0x4C`)
   - `data_5659A8 = sub_4EA380` (`+0x50`, already promoted earlier as `QLCGImport_SendConsoleCommand`)
2. The same helper sequence is mirrored in the retail UI import slab:
   - `data_567370 = sub_4EA330`
   - `data_567374 = sub_4EA340`
   - `data_567378 = sub_4EA350`
   - `data_56737C = sub_4EA360`
   - `data_567380 = sub_4ED040`
   - `data_567384 = sub_4EA370`
   - `data_567388 = sub_4EA380`
3. Native cgame uses raw `+0x38` as a file-open path:
   - `(*(data_1074CCCC + 0x38))("ui/country.txt", &__return_addr, 0)`
   - `(*(data_1074CCCC + 0x38))(arg1, &var_14, 0)`
   - `(*(data_1074CCCC + 0x38))("ui/hud.txt", &var_14, 0)`
4. `sub_4EA330` tailcalls `sub_4D22C0`, whose body switches on filesystem mode and emits:
   - `FSH_FOpenFile: bad mode`
5. Native cgame uses raw `+0x3C` as the paired read path:
   - `(*(data_1074CCCC + 0x3C))(&arg_424, eax_4, __return_addr)`
   - `(*(data_1074CCCC + 0x3C))(&data_100BBD10, esi, var_14)`
6. `sub_4EA340` tailcalls `sub_4D2A80`, matching the standard `FS_Read(buffer, len, f)` helper shape.
7. `sub_4EA350` tailcalls `sub_4D00F0`, whose body emits:
   - `FS_Write: 0 bytes written\n`
   - `FS_Write: -1 bytes written\n`
8. Native cgame uses raw `+0x44` as the paired close path:
   - `return (*(data_1074CCCC + 0x44))(var_14)`
   - `(*(data_1074CCCC + 0x44))(__return_addr)`
9. `sub_4EA360` tailcalls `sub_4CF320`, whose body closes the OS or zip-backed handle and clears the `fsh[]` slot, matching `FS_FCloseFile`.
10. Native cgame uses raw `+0x4C` with the exact list-file contract:
   - `(*(data_1074CCCC + 0x4C))("dlc_gibs", &data_100669B8, &var_404, 0x400)`
11. `sub_4EA370` tailcalls `sub_4D2D80`, whose body special-cases:
   - `if (Q_stricmp(path, "$modlist") == 0) { return FS_GetModList(listbuf, bufsize); }`
12. That exact `$modlist` branch matches the public `FS_GetFileList(path, extension, listbuf, bufsize)` source body in `files.c`.

That gives exact wrapper ownership for `FS_FOpenFile`, `FS_Read`, `FS_Write`, `FS_FCloseFile`, and `FS_GetFileList`, with `SendConsoleCommand` already serving as the right boundary.

## `FS_Seek` At Raw `+0x48`

The `+0x48` slot also closes as `FS_Seek`, even though this round did not turn up a direct raw native cgame callsite for it.

Observed local facts:

1. `data_5659A0 = sub_4ED040` in the raw cgame slab, and the mirrored UI slot at `data_567380` uses that same helper.
2. `sub_4ED040` tailcalls `sub_4D0240`.
3. `sub_4D0240` contains the exact `FS_Seek` body-level signatures:
   - `ZIP FILE FSEEK NOT YET IMPLEMENTED\n`
   - `Bad origin in FS_Seek\n`
   - the zip-file reopen/rewind special case
   - the final `fseek(file, offset, _origin)` path
4. The already reconstructed UI import order in `cl_ui.c` matches the same tail exactly:
   - `[14] = QL_UI_trap_FS_FOpenFile`
   - `[15] = QL_UI_trap_FS_Read`
   - `[16] = QL_UI_trap_FS_Write`
   - `[17] = QL_UI_trap_FS_FCloseFile`
   - `[18] = QL_UI_trap_FS_Seek`
   - `[19] = QL_UI_trap_FS_GetFileList`
5. The raw cgame slab places `sub_4ED040` between the already-observed `FS_FCloseFile` and `FS_GetFileList` wrappers.

That is enough to promote `sub_4ED040` as `QLCGImport_FS_Seek` and `sub_4D0240` as `FS_Seek` on observed body plus surrounding slot order, not on slot position alone.

## Owning Engine Helpers

The wrapper tails also close the underlying engine helpers behind this seam.

Observed local facts:

1. `sub_4D22C0` is the filesystem mode-dispatch helper used by `sub_4EA330`, matching `FS_FOpenFileByMode`.
2. `sub_4D2A80` is the read helper used by `sub_4EA340`, matching `FS_Read`.
3. `sub_4D00F0` is the write helper used by `sub_4EA350`, matching `FS_Write`.
4. `sub_4CF320` is the handle-close helper used by `sub_4EA360`, matching `FS_FCloseFile`.
5. `sub_4D0240` is the seek helper used by `sub_4ED040`, matching `FS_Seek`.
6. `sub_4D2D80` is the list-file helper used by `sub_4EA370`, matching `FS_GetFileList`.
7. All six helpers have committed stable rows in `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`:
   - `004CF320`
   - `004D00F0`
   - `004D0240`
   - `004D22C0`
   - `004D2A80`
   - `004D2D80`

That makes the owning helper names promotable in the same round instead of keeping them note-only.

## Promoted Aliases

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4EA330` (`0x004EA330`) | `QLCGImport_FS_FOpenFile` | Observed | Raw native cgame import wrapper for the file-open syscall, forwarding to the retail mode-dispatch helper. |
| `sub_4EA340` (`0x004EA340`) | `QLCGImport_FS_Read` | Observed | Raw native cgame import wrapper for filesystem reads. |
| `sub_4EA350` (`0x004EA350`) | `QLCGImport_FS_Write` | Observed | Raw native cgame import wrapper for filesystem writes. |
| `sub_4EA360` (`0x004EA360`) | `QLCGImport_FS_FCloseFile` | Observed | Raw native cgame import wrapper for filesystem handle close. |
| `sub_4ED040` (`0x004ED040`) | `QLCGImport_FS_Seek` | Observed | Raw native cgame import wrapper for filesystem seek; pinned by exact helper body plus mirrored slot order. |
| `sub_4EA370` (`0x004EA370`) | `QLCGImport_FS_GetFileList` | Observed | Raw native cgame import wrapper for filesystem enumeration and the `$modlist` special case. |
| `sub_4CF320` (`0x004CF320`) | `FS_FCloseFile` | Observed | Retail filesystem close helper. |
| `sub_4D00F0` (`0x004D00F0`) | `FS_Write` | Observed | Retail filesystem write helper. |
| `sub_4D0240` (`0x004D0240`) | `FS_Seek` | Observed | Retail filesystem seek helper with the exact zip-file and bad-origin branches. |
| `sub_4D22C0` (`0x004D22C0`) | `FS_FOpenFileByMode` | Observed | Retail filesystem mode-dispatch helper used by the raw open wrapper. |
| `sub_4D2A80` (`0x004D2A80`) | `FS_Read` | Observed | Retail filesystem read helper. |
| `sub_4D2D80` (`0x004D2D80`) | `FS_GetFileList` | Observed | Retail filesystem list helper, including the `$modlist` handoff to `FS_GetModList`. |

## Open Questions

1. This round closes the stable filesystem seam only. It does not change the earlier documented-only `UpdateScreen` or `CM_NumInlineModels` thunks from Round 33.
2. I did not find a direct raw native cgame caller for `+0x48` in the current pass, but the `FS_Seek` promotion is still stable because the helper body matches exactly and the mirrored UI slot order removes the remaining ambiguity.
