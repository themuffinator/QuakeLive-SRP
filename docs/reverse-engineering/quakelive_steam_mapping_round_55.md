# Quake Live Steam Host Mapping Round 55

## Scope

This round maps the retained Quake III filesystem tranche inside
`quakelive_steam.exe`, using the original `files.c` source layout as the
primary guide for names that survived into the retail Quake Live host.

The promoted slice covers:

- the core `FS_FOpen*`, `FS_Read*`, `FS_Write*`, and `FS_ReadFile` path
- file-list, mod-list, and `dir` / `fdir` console helpers
- the retained `FS_LoadZipFile` pack loader
- loaded / referenced pak checksum and name string builders
- pure-server pak state and handle helpers such as `FS_FTell` / `FS_Flush`

Primary evidence for this round:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `src/code/qcommon/files.c`
- `assets/quake3/src/code/qcommon/files.c`
- `src/code/server/sv_client.c`

## Core Filesystem Closures

### File open, read, and write helpers

Observed facts:

1. `sub_4CF3E0`, `sub_4CF4D0`, and `sub_4CF640` preserve the exact Quake III
   debug and fatal strings for `FS_FOpenFileWrite`, `FS_FOpenFileAppend`, and
   `FS_FOpenFileRead`.
2. `sub_4D0010` preserves the exact `FS_Read: -1 bytes read` fatal and matches
   Quake III's partial-read retry loop, while `sub_4D2A80` is the small
   `FS_Read2` wrapper around it rather than the primary read routine.
3. `sub_4D01D0`, `sub_4D0510`, `sub_4D0570`, and `sub_4D2AF0` retain the
   expected `FS_Printf`, `FS_FreeFile`, `FS_WriteFile`, and `FS_ReadFile`
   behavior and diagnostics from the Quake III source.

These promotions close the retained Quake III file I/O spine:

- `FS_FOpenFileWrite`
- `FS_FOpenFileAppend`
- `FS_FilenameCompare`
- `FS_FOpenFileRead`
- `FS_Read`
- `FS_Read2`
- `FS_Printf`
- `FS_FileIsInPAK`
- `FS_FreeFile`
- `FS_WriteFile`
- `FS_ReadFile`

### File list, mod list, and console helpers

Observed facts:

1. `sub_4D09A0` deduplicates strings into the caller list with the same
   `0xFFF` entry cap as Quake III `FS_AddFileToList`.
2. `sub_4D09F0`, `sub_4D0DB0`, `sub_4D0DD0`, and `sub_4D0E20` line up with the
   `FS_ListFilteredFiles`, `FS_ListFiles`, `FS_FreeFileList`, and
   `Sys_ConcatenateFileLists` path in both source order and behavior.
3. `sub_4D12E0`, `sub_4D1510`, `sub_4D1610`, and `sub_4D1700` preserve the
   stock Quake III command strings for `dir`, `fdir`, `path`, and `touchFile`.

This round promotes:

- `FS_AddFileToList`
- `FS_ListFilteredFiles`
- `FS_ListFiles`
- `FS_FreeFileList`
- `Sys_ConcatenateFileLists`
- `FS_GetModList`
- `FS_Dir_f`
- `FS_PathCmp`
- `FS_SortFileList`
- `FS_NewDir_f`
- `FS_Path_f`
- `FS_TouchFile_f`
- `paksort`
- `FS_idPak`
- `FS_ComparePaks`

`0x004D1539` remains only as a Ghidra split inside `FS_NewDir_f`, not a true
standalone function.

## Pack Loader And Pure-Server Closures

### `sub_4D05F0`: `FS_LoadZipFile`

Observed facts:

1. The helper walks every entry in a zip through the `unz*` API, counts string
   storage, and allocates the same `fileInPack_t` build buffer layout used by
   Quake III.
2. It lowercases filenames, hashes them into the pack hash table, and records
   the zip file position for each entry.
3. It computes both `checksum` and `pure_checksum` from the collected header
   CRC list, exactly matching Quake III's `FS_LoadZipFile` role.

That makes `sub_4D05F0` the retained pack-loader core.

### Loaded and referenced pak string builders

Observed facts:

1. `sub_4D1CC0`, `sub_4D1D10`, and `sub_4D1D70` build the loaded-pak checksum,
   name, and pure-checksum strings from the active search path in the same
   order as Quake III.
2. `sub_4D1DC0` matches the retained `FS_ReferencedPakChecksums` builder that
   appends checksum values for referenced or non-`baseq3` packs.
3. `sub_4D1E20` and `sub_4D1EC0` match the `pakGamename/pakBasename` builder
   and the ordered pure-checksum string with the `@` delimiter and final XOR
   checksum footer.

This round promotes:

- `FS_LoadedPakChecksums`
- `FS_LoadedPakNames`
- `FS_LoadedPakPureChecksums`
- `FS_ReferencedPakChecksums`
- `FS_ReferencedPakNames`
- `FS_ReferencedPakPureChecksums`

### Pure-server and handle helpers

Observed facts:

1. `sub_4D2080` is the direct Quake III `FS_ClearPakReferences` loop with the
   same `flags == 0 -> -1` behavior.
2. `sub_4D20C0` and `sub_4D21E0` retain the stock pure-server checksum/name
   tokenization flow for loaded and referenced pak lists.
3. `sub_4D2400` and `sub_4D2440` are the expected `FS_FTell` and `FS_Flush`
   wrappers used by the virtual-machine handle layer.

This round also promotes:

- `FS_ReorderPurePaks`
- `FS_ClearPakReferences`
- `FS_PureServerSetLoadedPaks`
- `FS_PureServerSetReferencedPaks`
- `FS_FOpenFileByMode`
- `FS_FTell`
- `FS_Flush`
- `FS_AddGameDirectory`
- `FS_Startup`
- `FS_Shutdown`

## Completion Summary

This round promotes `41` retained Quake III filesystem aliases:

- core file I/O and comparison: `FS_FOpenFileWrite`, `FS_FOpenFileAppend`,
  `FS_FilenameCompare`, `FS_FOpenFileRead`, `FS_Read`, `FS_Read2`,
  `FS_Printf`, `FS_FileIsInPAK`, `FS_FreeFile`, `FS_WriteFile`, `FS_ReadFile`
- file-list and console helpers: `FS_AddFileToList`, `FS_ListFilteredFiles`,
  `FS_ListFiles`, `FS_FreeFileList`, `Sys_ConcatenateFileLists`,
  `FS_GetModList`, `FS_Dir_f`, `FS_PathCmp`, `FS_SortFileList`, `FS_NewDir_f`,
  `FS_Path_f`, `FS_TouchFile_f`, `paksort`, `FS_idPak`, `FS_ComparePaks`
- pack/pure helpers: `FS_LoadZipFile`, `FS_LoadedPakChecksums`,
  `FS_LoadedPakNames`, `FS_LoadedPakPureChecksums`,
  `FS_ReferencedPakChecksums`, `FS_ReferencedPakNames`,
  `FS_ReferencedPakPureChecksums`, `FS_ClearPakReferences`,
  `FS_ReorderPurePaks`, `FS_PureServerSetLoadedPaks`,
  `FS_PureServerSetReferencedPaks`, `FS_FTell`, `FS_Flush`,
  `FS_AddGameDirectory`, `FS_Startup`, `FS_Shutdown`

Focused band results after this pass:

- `0x4CF320-0x4D30A0`: raw gaps `48 -> 7`, true gaps `47 -> 6`
- `0x4CF3E0-0x4D1870`: raw gaps `27 -> 2`, true gaps `26 -> 1`
- `0x4D1CC0-0x4D2440`: raw/true gaps `12 -> 1`

The remaining true unresolved starts in this retained-filesystem tranche are:

- `0x004CFF60`
- `0x004D2040`
- `0x004D2460`
- `0x004D25B0`
- `0x004D2670`
- `0x004D2750`

These are no longer stock Quake III `files.c` helpers. They sit in the Quake
Live-specific binary-pack, stats, and pure-validation path that wraps the
retained filesystem core.
