# quakelive_steam.exe Mapping Round 202

Date: 2026-04-28

Scope: retained renderer backend quad submission helpers around the old
queue head `0x004368A0`.

## Summary

This round resolved `2` additional `quakelive_steam.exe` aliases.
Classification mix:

- `2` engine-owned functions
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The useful outcome is that the heavy renderer queue head at `0x004368A0` is
no longer anonymous, and the adjacent post-process fullscreen-quad helper now
reads with its real retained owner as well. The two closures are
`sub_4368A0 -> RB_StretchPic` and `sub_436C50 -> RBPP_DrawQuad`.

## Evidence Notes

- The decisive source anchors are
  [RB_StretchPic](</E:/Repositories/QuakeLive-reverse/src/code/renderer/tr_backend.c:2850>)
  and
  [RBPP_DrawQuad](</E:/Repositories/QuakeLive-reverse/src/code/renderer/tr_backend.c:1030>).
- `sub_4368A0` is exact as `RB_StretchPic`. Its retained HLIL carries the same
  `!backEnd.projection2D -> RB_SetGL2D()` guard, shader handoff into
  `RB_BeginSurface`, `RB_CHECKOVERFLOW( 4, 6 )` growth, fixed quad index
  pattern, `backEnd.color2D` color replication, and `x/y/w/h + s/t` command
  field layout as the checked-in backend source.
- `sub_436C50` is exact as `RBPP_DrawQuad`. The HLIL emits the same
  fullscreen `GL_QUADS` draw with paired `qglMultiTexCoord2fARB` writes for
  `GL_TEXTURE0_ARB` and `GL_TEXTURE1_ARB`, mirrored single-texture fallback
  coordinates, and the four `qglVertex2f` corners built from `(0,0)`,
  `(width,0)`, `(width,height)`, and `(0,height)`.
- I deliberately left the neighboring `sub_436DC0` seam deferred. It is
  clearly part of the recovered post-process backend, but it behaves as a
  larger stateful helper rather than a trivially promotable public owner, so
  `RB_StretchPic` plus `RBPP_DrawQuad` were the cleaner exact hits for this
  pass.

## Aliases Added

- `sub_4368A0` -> `RB_StretchPic`
- `sub_436C50` -> `RBPP_DrawQuad`

## Verification

Static mapping validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- scoped duplicate-key scan for the `quakelive_steam` alias block passed with
  `0` duplicates
- recount after this pass: `2149` raw alias entries, `2076` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `37.932%` of `5473` functions
- `git diff --check` passed aside from the repo's existing LF -> CRLF
  normalization warnings on touched text files
- no build or runtime launch was needed; this was mapping-only work on the
  committed evidence corpus

Parity estimate after this pass:

- strict-retail Windows replacement target: `100%` before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

After this round, the refreshed largest-unaliased queue begins with:

| # | Address | Ghidra name | Size |
| ---: | --- | --- | ---: |
| 1 | `0x004B3672` | `FUN_004b3672` | `495` |
| 2 | `0x00429DD0` | `FUN_00429dd0` | `483` |
| 3 | `0x004A4280` | `FUN_004a4280` | `483` |
| 4 | `0x004B6630` | `FUN_004b6630` | `483` |
| 5 | `0x004241C0` | `FUN_004241c0` | `482` |
| 6 | `0x0042A130` | `FUN_0042a130` | `480` |
| 7 | `0x00498890` | `FUN_00498890` | `480` |
| 8 | `0x00480DD0` | `FUN_00480dd0` | `479` |
| 9 | `0x004C84E0` | `FUN_004c84e0` | `479` |
| 10 | `0x0050EF80` | `FUN_0050ef80` | `476` |

The next pass can keep probing the `FUN_004b3672` console split, return to the
remaining engine-owned `0x00429***` / `0x004A4***` seams, or push deeper into
the recovered post-process backend once the larger stateful helper boundaries
around `sub_436DC0` stabilize.
