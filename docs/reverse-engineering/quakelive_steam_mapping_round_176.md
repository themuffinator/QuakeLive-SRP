# quakelive_steam.exe Mapping Round 176

Date: 2026-04-28

Scope: source-backed closure of the remaining renderer advert debug overlay gap
for `quakelive_steam.exe`. This pass keeps the existing round 175 alias corpus
intact and reconstructs the missing `src/code` ownership needed for the retail
`R_DebugAdvertisements` path to exist in the split client/renderer source tree.

## Summary

This was a source-only pass. No new alias rows were added, but the previously
open renderer advert debug overlay gap is now closed in writable source.

The reconstruction landed:

- client-owned advert debug bridge callbacks in `cl_cgame.c`
- the client-to-renderer advert debug import seam in `client.h`,
  `cl_main.c`, and `tr_public.h`
- the renderer-owned `r_debugAds` cvar and `R_DebugAdvertisements` owner in
  `tr_init.c`, `tr_local.h`, `tr_main.c`, and `tr_world.c`

Alias coverage therefore remains unchanged from round 175:

- `2038` raw alias entries
- `1970` strict Ghidra address-backed aliases
- `35.995%` strict Ghidra address-backed coverage of `5473` functions

## Source Reconstruction Notes

- Retail `sub_435070` sits after the `R_DebugGraphics` tail in
  `R_RenderView`, guards on `r_debugAds` plus `frameSceneNum == 1`, syncs the
  render thread, and then walks the loaded advertisement cells. The new source
  mirrors that ordering by calling `R_DebugAdvertisements()` immediately after
  `R_DebugGraphics()`.
- The HLIL palette constants are explicit:
  - state `0`: `(0.5, 0.0, 0.0)`
  - state `1`: `(0.5, 0.5, 0.0)`
  - state `2`: `(0.0, 0.5, 0.0)`
  The renderer overlay now uses that same three-color split for per-cell debug
  text and quad outlines.
- The mapped bridge helpers at `sub_4F2040`, `sub_4F2080`, `sub_4F2160`,
  `sub_4F2180`, `sub_4F2260`, and `sub_4F2280` are just host callbacks with
  empty-string / zero fallbacks when no advert bridge object is present. That
  made the split-source reconstruction straightforward: the client bridge now
  formats labels and summary lines from the retained compatibility state it
  already tracks (`activeAdvertCellId`, `activatedAdvertCellId`, provider,
  policy, overlay availability, frame time, and view size), and the renderer
  consumes those values through a small `refimport_t` extension instead of
  hardwiring client state into renderer code.
- The renderer overlay also restores the immediate-mode world annotations that
  sit beside the text list: colored cell quad outlines plus a white cell normal
  vector from `center` to `center + normal * 100`.

## Aliases Added

- none; this round consumed already-mapped owners in source

## Verification

Source validation:

- `MSBuild.exe src\code\quakelive_steam.vcxproj /p:Configuration=Debug /p:Platform=Win32 /p:WindowsTargetPlatformVersion=10.0.26100.0 /m`
  succeeded using the local Visual Studio 2022 toolchain and the same one-off
  SDK override used in the earlier advert-runtime source pass
- the current `Debug|Win32` build completed cleanly under that override with
  no compiler or linker warnings emitted in this pass
- `python -m json.tool` passed, the scoped `quakelive_steam` duplicate-key scan
  stayed at `0`, and a fresh strict recount confirmed the round 175 alias
  baseline remains `2038 / 1970 / 35.995%`
- no runtime launch was performed; this was static/source reconstruction work

Parity estimate after this pass remains unchanged:

- strict-retail Windows replacement target: `100%` before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

Because this was source-only, the largest-unaliased queue is unchanged from the
current round 175 alias baseline:

| Rank | Address | Raw symbol | Size |
| ---: | --- | --- | ---: |
| 1 | `0x004FC240` | `FUN_004fc240` | `537` |
| 2 | `0x0041AD70` | `FUN_0041ad70` | `517` |
| 3 | `0x004E6730` | `FUN_004e6730` | `504` |
| 4 | `0x004B4100` | `FUN_004b4100` | `502` |
| 5 | `0x00475200` | `FUN_00475200` | `497` |
| 6 | `0x0047DA20` | `FUN_0047da20` | `497` |
| 7 | `0x00409670` | `FUN_00409670` | `496` |
| 8 | `0x004B3672` | `FUN_004b3672` | `495` |
| 9 | `0x0041C400` | `FUN_0041c400` | `492` |
| 10 | `0x00414AC0` | `FUN_00414ac0` | `490` |

The next mapping-focused pass can return to the `0x004FC240` / `0x0041AD70` /
`0x004E6730` queue head now that the lingering advert overlay source hole is no
longer competing with it.
