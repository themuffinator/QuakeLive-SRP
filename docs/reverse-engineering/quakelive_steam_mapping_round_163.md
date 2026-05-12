# quakelive_steam.exe Mapping Round 163

Date: 2026-04-27

Scope: retained libvorbis `floor1.c` setup, lookup, and fit-helper recovery
around the old `0x00523B40`, `0x00524370`, and `0x00524580` queue heads. This
pass stayed mapping-only.

## Summary

This round resolved `15` additional `quakelive_steam.exe` rows.
Classification mix:

- `0` engine-owned functions
- `0` platform-service-owned functions
- `15` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The useful outcome is that the anonymous retained libvorbis floor1 scaffold
now reads cleanly end-to-end. The old queue heads at `0x00523B40`,
`0x00524370`, and `0x00524580` resolve as `floor1_unpack`, `fit_line`, and
`inspect_error`, while the adjacent setup/lookup/render helpers now line up
with the checked-in `floor1.c` ownership around the already-mapped
`floor1_fit`, `floor1_encode`, and `floor1_inverse1` lane.

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_523B40` | `520` | CRT/STL/support-library | `floor1_unpack` | High | Closed from the exact partition/class unpack, `postlist` load, duplicate-post rejection, and `floor1_free_info` failure path. |
| 2 | `sub_524370` | `520` | CRT/STL/support-library | `fit_line` | High | Closed from the exact weighted least-squares accumulation, optional endpoint pinning, `rint` endpoint solve, and `0..1023` clamp. |
| 3 | `sub_524580` | `520` | CRT/STL/support-library | `inspect_error` | High | Closed from the exact line-walk, `vorbis_dBquant` checks, `twofitatten` thresholding, max-over/max-under guards, and MSE gate. |
| 4 | `sub_523D70` | `506` | CRT/STL/support-library | `floor1_look` | High | Closed from the exact sorted-post lookup construction, `forward_index`/`reverse_index` population, multiplier-to-`quant_q` switch, and neighbor discovery loop. |
| 5 | `sub_5239A0` | `407` | CRT/STL/support-library | `floor1_pack` | High | Closed from the exact partition/class writer, `mult`/`rangebits` emission, and packed `postlist` loop. |
| 6 | `sub_524040` | `362` | CRT/STL/support-library | `render_line` | High | Closed from the exact Bresenham-style walk over `FLOOR1_fromdB_LOOKUP` with in-place float scaling. |
| 7 | `sub_524230` | `319` | CRT/STL/support-library | `accumulate_fit` | High | Closed from the exact split `xa/xb` accumulator families and the `twofitatten` branch that separates masked points. |
| 8 | `sub_5241B0` | `121` | CRT/STL/support-library | `render_line0` | High | Closed from the integer-valued companion to `render_line` that writes interpolated posts into an `int` buffer. |
| 9 | `sub_523FC0` | `67` | CRT/STL/support-library | `render_point` | High | Closed from the exact masked-endpoint interpolation helper used throughout floor1 prediction. |
| 10 | `sub_524010` | `43` | CRT/STL/support-library | `vorbis_dBquant` | High | Closed from the exact `*x * 7.3142857f + 1023.5f` quantizer and `0..1023` clamp. |
| 11 | `sub_523920` | `36` | CRT/STL/support-library | `floor1_free_info` | High | Closed from the exact zero-and-free destructor for the `0x460` floor1 info slab. |
| 12 | `sub_523950` | `36` | CRT/STL/support-library | `floor1_free_look` | High | Closed from the exact zero-and-free destructor for the `0x520` floor1 look slab. |
| 13 | `sub_524790` | `23` | CRT/STL/support-library | `post_Y` | High | Closed from the exact `A/B` post merge rule with the midpoint fallback. |
| 14 | `sub_523980` | `22` | CRT/STL/support-library | `ov_ilog` | High | Closed from the exact `for(ret=0; v; ret++) v >>= 1;` helper shared across libvorbis pack/unpack paths. |
| 15 | `sub_523D50` | `21` | CRT/STL/support-library | `icomp` | High | Closed from the exact comparator used by both `floor1_unpack` and `floor1_look` `qsort` calls. |

## Evidence Notes

- The recovered ownership maps directly onto the checked-in
  [floor1.c](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/floor1.c:53>)
  helper band:
  [floor1_free_info](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/floor1.c:53>),
  [floor1_free_look](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/floor1.c:61>),
  [floor1_pack](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/floor1.c:74>),
  [icomp](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/floor1.c:112>),
  [floor1_unpack](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/floor1.c:116>),
  [floor1_look](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/floor1.c:180>),
  [render_point](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/floor1.c:257>),
  [vorbis_dBquant](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/floor1.c:273>),
  [render_line](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/floor1.c:347>),
  [render_line0](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/floor1.c:376>),
  [accumulate_fit](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/floor1.c:406>),
  [fit_line](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/floor1.c:456>),
  [inspect_error](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/floor1.c:516>),
  and [post_Y](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/floor1.c:567>).
- `sub_523980` is the shared
  [ov_ilog](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/sharedbook.c:30>)
  helper from
  [sharedbook.c](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/sharedbook.c:30>).
  The tiny loop body matches exactly and is reused by the floor1 pack/unpack
  path.
- The strongest ownership anchors in this pass were the paired `qsort`
  comparator usage in `floor1_unpack`/`floor1_look`, the `quant_q` switch on
  `info->mult`, the preserved `FLOOR1_fromdB_LOOKUP` scaling loop in
  `render_line`, and the split `xa/xb` accumulator families in
  `accumulate_fit`.
- I intentionally stayed within the exact helper/setup scaffold in this round.
  The broader floor decoder path already has `floor1_inverse1` mapped, but the
  remaining decode-side pieces still deserve their own boundary check rather
  than being forced into this pass.

## Aliases Added

- `sub_523920` -> `floor1_free_info`
- `sub_523950` -> `floor1_free_look`
- `sub_523980` -> `ov_ilog`
- `sub_5239A0` -> `floor1_pack`
- `sub_523B40` -> `floor1_unpack`
- `sub_523D50` -> `icomp`
- `sub_523D70` -> `floor1_look`
- `sub_523FC0` -> `render_point`
- `sub_524010` -> `vorbis_dBquant`
- `sub_524040` -> `render_line`
- `sub_5241B0` -> `render_line0`
- `sub_524230` -> `accumulate_fit`
- `sub_524370` -> `fit_line`
- `sub_524580` -> `inspect_error`
- `sub_524790` -> `post_Y`

## Verification

Static mapping validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- scoped duplicate-key scan for the `quakelive_steam` alias block passed with
  `0` duplicates
- recount after this pass: `1864` raw alias entries, `1792` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `32.743%` of `5473` functions
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
| 1 | `0x004FC240` | `FUN_004fc240` | `537` |
| 2 | `0x004FAF60` | `FUN_004faf60` | `534` |
| 3 | `0x00417790` | `FUN_00417790` | `518` |
| 4 | `0x0041AD70` | `FUN_0041ad70` | `517` |
| 5 | `0x00512340` | `FUN_00512340` | `517` |
| 6 | `0x004F5200` | `FUN_004f5200` | `514` |
| 7 | `0x00437710` | `FUN_00437710` | `513` |
| 8 | `0x00421830` | `FUN_00421830` | `512` |
| 9 | `0x0043F590` | `FUN_0043f590` | `507` |
| 10 | `0x004F7B70` | `FUN_004f7b70` | `506` |

The next pass can return to the still-transformed `vorbisfile.c` search helper
at `sub_4FC240`, the opaque `sub_4FAF60` file-wrapper slab, or pivot back into
the unresolved engine/platform rows now that this `floor1.c` helper seam is no
longer anonymous.
