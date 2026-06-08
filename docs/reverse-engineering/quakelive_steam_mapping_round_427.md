# Quake Live Steam Mapping Round 427

Date: 2026-06-08

## Scope

This round pins the SteamID-scoped native-DLL launch lane: `FS_Startup`
derives `fs_homepath` from the active Steam user, and `Sys_LoadDll` uses that
root when loading or materializing `uix86.dll`, `cgamex86.dll`, and
`qagamex86.dll`.

## Evidence

- `references/analysis/quakelive_symbol_aliases.json` maps `sub_4ECEB0` to
  `Sys_LoadDll`.
- Binary Ninja HLIL for retail `sub_4ECEB0` fetches `fs_homepath`,
  `fs_basepath`, `fs_cdpath`, and `fs_game`, builds `"%sx86.dll"`, then probes
  `LoadLibraryA(FS_BuildOSPath(fs_basepath, fs_game, dll))`,
  `LoadLibraryA(FS_BuildOSPath(fs_homepath, fs_game, dll))`, and finally
  `LoadLibraryA(FS_BuildOSPath(fs_cdpath, fs_game, dll))`.
- Binary Ninja HLIL for retail `FS_Startup` still shows the Steam launch root
  pivot: when `SteamClient_IsInitialized()` is live, it calls
  `SteamClient_GetSteamID()` and formats `fs_homepath` as
  `"%s/%llu"` from `fs_basepath` plus the local SteamID.

## Source Reconstruction

- The current source keeps the retail `FS_ResolveHomePath()` contract:
  no active Steam user means `fs_homepath == fs_basepath`, while an active
  Steam user produces `fs_basepath/<steamid>`.
- `Sys_LoadDll()` intentionally probes `fs_homepath` before `fs_basepath`.
  This differs from the retail `sub_4ECEB0` order, but preserves the
  replacement-launch requirement that SteamID-scoped modules under
  `<retail root>/<steamid>/baseq3` take precedence over immutable retail files.
- The same root order is used for `bin.pk3` materialization. If the native
  module is only present in retail `baseq3/bin.pk3`, the source extracts it
  into the preferred home root before loading, which keeps the runtime working
  toward the `${steam_id}/baseq3` DLL path instead of requiring manual
  extraction beside retail assets.

## Deferred Notes

- Retail exactness for `sub_4ECEB0` remains base-first. The source divergence is
  documented and test-pinned because direct retail replacement launches need a
  writable SteamID-scoped override layer.
- No live Steam launch was run in this round; this is a static reconstruction
  guard around the launch/runtime path.

## Parity

Focused SteamID native-DLL launch/root confidence moves from 83% to 91%.
The broader Steam launch/runtime integration slice moves from 79% to 80%.
