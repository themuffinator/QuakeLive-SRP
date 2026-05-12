# Quake Live Steam Mapping Round 192

## Scope

This round returns to mapping-only work in the retained Vorbis support
corridor and closes four exact helper owners that had been left deferred as
compiler-transformed internals.

Primary evidence for this pass:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `src/libs/_deps/libvorbis/lib/envelope.c`
- `src/libs/_deps/libvorbis/lib/window.c`
- `src/libs/_deps/libvorbis/lib/res0.c`
- `src/libs/_deps/libvorbis/lib/vorbisfile.c`

## Summary

This round resolves `4` additional `quakelive_steam.exe` rows.
Classification mix:

- `0` engine-owned functions
- `0` platform-service-owned functions
- `4` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The useful outcome is that the remaining anonymous seam between the retained
Vorbis analysis/setup owners and the already-mapped `mapping0_forward`,
`res1_class`, and `vorbisfile.c` page walkers now reads cleanly as exact
library ownership:

- `_ve_envelope_clear`
- `_vorbis_apply_window`
- `res1_forward`
- the split `_bisect_forward_serialno` body at `sub_4FC240`

That closes three long-deferred queue entries directly and removes the old
largest-unaliased head at `0x004FC240`.

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_4FC240` | `537` | support-library | `_bisect_forward_serialno` | High | Closed from the exact recursive seek/index bisector in `vorbisfile.c`: midpoint seek through `_seek_helper`, page walk via `_get_next_page`, serial-list tests through `_lookup_page_serialno`, recursive descent, and final link-offset allocation. This is a second split body around the already-mapped corridor, not a new engine debt. |
| 2 | `sub_523280` | `490` | support-library | `res1_forward` | High | Closed from the residue1 export bundle slot and the exact retained wrapper shape in `res0.c`: compact `nonzero` channels, call `_01forward`, and route `_encodepart` through the shared staged encoder path. |
| 3 | `sub_520CF0` | `489` | support-library | `_vorbis_apply_window` | High | Closed from the exact `mapping0_forward` callsite and body shape in `window.c`: choose left/right windows from `vwin[winno[*]]`, zero the outer quarters, scale the active edges by the matching long/short window halves, and leave the center untouched. |
| 4 | `sub_520C70` | `102` | support-library | `_ve_envelope_clear` | High | Closed from the exact `envelope.c` teardown path: `mdct_clear(&e->mdct)`, free all seven `band[i].window` owners, then free `mdct_win`, `filter`, `mark`, and `memset(e,0,sizeof(*e))`. |

## Evidence Notes

- The decisive source anchors are
  [_ve_envelope_clear](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/envelope.c:75>),
  [_vorbis_apply_window](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/window.c:2102>),
  [res1_forward](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/res0.c:715>),
  and [_bisect_forward_serialno](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/vorbisfile.c:471>).
- `sub_520CF0` is anchored especially strongly because the already-mapped
  `mapping0_forward` body calls it in the exact public-source order:
  `_vorbis_apply_window(...)`, `mdct_forward(...)`, then `drft_forward(...)`.
- `sub_523280` is anchored by the retained residue1 export bundle order in the
  executable: `class -> forward -> inverse` maps to the already-named
  `sub_523470`, this pass's `sub_523280`, and the already-named `sub_5234D0`.
- `sub_4FC240` sits in the split `vorbisfile.c` bisector seam that earlier
  rounds had partially named. The recursive structure, link-array allocation,
  and serial-list walk make this a stable second `_bisect_forward_serialno`
  body rather than a different `ov_*` owner.

## Aliases Added

- `sub_4FC240` -> `_bisect_forward_serialno`
- `sub_520C70` -> `_ve_envelope_clear`
- `sub_520CF0` -> `_vorbis_apply_window`
- `sub_523280` -> `res1_forward`

## Verification

Static mapping validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- scoped duplicate-key scan for the `quakelive_steam` alias block passed with
  `0` duplicates
- recount after this pass: `2042` raw alias entries, `1970` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `35.995%` of `5473` functions
- `git diff --check` passed aside from the repo's existing LF -> CRLF
  normalization warnings on touched text files
- no build or runtime launch was needed; this was mapping-only work on the
  committed evidence corpus

## Parity Estimate

- strict-retail Windows replacement target: `100%` before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

After this round, the refreshed largest-unaliased queue begins with:

| # | Address | Ghidra name | Size |
| ---: | --- | --- | ---: |
| 1 | `0x0041AD70` | `FUN_0041ad70` | `517` |
| 2 | `0x004E6730` | `FUN_004e6730` | `504` |
| 3 | `0x004B4100` | `FUN_004b4100` | `502` |
| 4 | `0x00475200` | `FUN_00475200` | `497` |
| 5 | `0x0047DA20` | `FUN_0047da20` | `497` |
| 6 | `0x00409670` | `FUN_00409670` | `496` |
| 7 | `0x004B3672` | `FUN_004b3672` | `495` |
| 8 | `0x0041C400` | `FUN_0041c400` | `492` |
| 9 | `0x00414AC0` | `FUN_00414ac0` | `490` |
| 10 | `0x0046A420` | `FUN_0046a420` | `490` |

The next pass can return to the persistent host/STL queue head at
`sub_41AD70`, stay in the host/Vorbisfile seam at `sub_4E6730`, or pivot to
the still-large client/host leftover at `sub_4B4100`.
