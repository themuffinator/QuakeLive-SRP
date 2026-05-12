# quakelive_steam.exe Mapping Round 173

Date: 2026-04-27

Scope: exact retained `libvorbis/res0.c` recovery across the residue-0 and
residue-1 lifecycle, pack/unpack, setup, and inverse helper lane from
`0x00522060` through `0x005234D0`. This pass stayed mapping-only and used
the committed HLIL corpus plus the checked-in Vorbis source in
`src/libs/_deps/libvorbis/lib/res0.c` as the exact naming anchor.

## Summary

This round resolved `12` additional `quakelive_steam.exe` rows and corrected
`1` earlier alias in the same retained support-library corridor.
Classification mix:

- `0` engine-owned functions
- `0` platform-service-owned functions
- `12` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The useful outcome is that the old anonymous residue seam between
`mapping0_inverse` and the already-mapped `res2_*` / `floor1_*` families now
reads cleanly as the exact retained `res0.c` ownership: lifecycle teardown,
the local `icount` bitcounter, `res0_pack`, `res0_unpack`, `res0_look`, the
residue-classification/encoding helpers, `_01inverse`, and the public
`res0_inverse` / `res1_class` / `res1_inverse` wrappers. I also corrected
`sub_522D40` from the older over-generic `vorbis_residue_01forward` to the
exact retained internal helper `_01forward`.

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_523030` | `491` | support-library | `_01inverse` | High | Closed from the exact retained inverse loop: phrasebook decode via `vorbis_book_decode`, `decodemap[temp]` lookup, staged partition iteration, and callback-driven stagebook decode through the function pointer tail. |
| 2 | `sub_522360` | `436` | support-library | `res0_look` | High | Closed from the exact look-builder path: `phrasebook`, `partbooks`, `partvals`, `maxstage`, and the `decodemap` expansion over the phrasebook dimension. |
| 3 | `sub_522D40` | `718` | support-library | `_01forward` | High | Corrected from the older placeholder `vorbis_residue_01forward`. The HLIL matches the exact retained staged forward encoder with per-channel partition codewords, `secondstages` gating, and `_encodepart`-driven residue writes. |
| 4 | `sub_5228E0` | `443` | support-library | `_01class` | High | Closed from the exact classifier that allocates `partword[ch]`, scans `max` and `ent`, scales by `100.0 / samples_per_partition`, and selects a partition class from `classmetric1` / `classmetric2`. |
| 5 | `sub_523220` | `87` | support-library | `res0_inverse` | High | Closed from the exact public wrapper that compacts `nonzero` channels and calls `_01inverse(..., vorbis_book_decodevs_add)`. |
| 6 | `sub_5234D0` | `87` | support-library | `res1_inverse` | High | Closed from the exact wrapper that compacts `nonzero` channels and calls `_01inverse(..., vorbis_book_decodev_add)`. |
| 7 | `sub_522230` | `295` | support-library | `res0_unpack` | High | Closed from the exact retained unpack path: `begin`, `end`, `grouping + 1`, `partitions + 1`, cascade expansion, `booklist`, range checks, and the guarded `partvals` multiplication. |
| 8 | `sub_522140` | `225` | support-library | `res0_pack` | High | Closed from the exact pack path that writes `begin`, `end`, `grouping - 1`, `partitions - 1`, `groupbook`, the split `secondstages` bitmask encoding, and the accumulated `booklist` entries. |
| 9 | `sub_522880` | `88` | support-library | `_encodepart` | High | Closed from the exact helper loop that batches `n / book->dim`, calls `local_book_besterror`, and feeds the returned entry into `vorbis_book_encode`. |
| 10 | `sub_523470` | `61` | support-library | `res1_class` | High | Closed from the exact wrapper that compacts `nonzero` channels and calls `_01class(vb, vl, in, used)`. |
| 11 | `sub_522090` | `120` | support-library | `res0_free_look` | High | Closed from the exact teardown lane that frees `partbooks`, frees each `decodemap[j]`, zeroes the look object, and frees it. |
| 12 | `sub_522060` | `36` | support-library | `res0_free_info` | High | Closed from the exact tiny teardown helper that zeroes `vorbis_info_residue0` and frees it when non-null. |
| 13 | `sub_522120` | `18` | support-library | `icount` | High | Closed from the exact local bitcounter body `result += arg1 & 1; arg1 >>= 1` used by both `res0_pack` and `res0_unpack`. |

## Evidence Notes

- The decisive source anchors are
  [res0_free_info](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/res0.c:65>),
  [res0_free_look](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/res0.c:73>),
  [icount](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/res0.c:151>),
  [res0_pack](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/res0.c:161>),
  [res0_unpack](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/res0.c:191>),
  [res0_look](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/res0.c:255>),
  [_encodepart](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/res0.c:381>),
  [_01class](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/res0.c:406>),
  [_01forward](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/res0.c:528>),
  [_01inverse](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/res0.c:643>),
  [res0_inverse](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/res0.c:703>),
  [res1_class](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/res0.c:735>),
  and [res1_inverse](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/res0.c:747>).
- The committed HLIL mirrors the retained source structure directly:
  `sub_522140` calls the local `ov_ilog`-style helper before the split
  `secondstages` write path, `sub_522230` rebuilds the same cascade mask and
  `partvals` guard, `sub_522360` constructs `partbooks` and `decodemap`,
  `sub_5228E0` uses the same `100.0 / samples_per_partition` scale, and
  `sub_523030` decodes phrasebook words into `look->decodemap[temp]` before
  walking the stagebooks.
- The residue wrapper ownership is also explicit in the HLIL call graph:
  `sub_523220` calls `_01inverse` with `vorbis_book_decodevs_add`,
  `sub_523470` calls `_01class`, and `sub_5234D0` calls `_01inverse` with
  `vorbis_book_decodev_add`, matching the exact retained `res0.c` wrappers.
- I intentionally left `sub_522110` unnamed in this pass. Its body is the
  duplicated `ov_ilog` helper loop, but the executable already has a cleaner
  exact retained `ov_ilog` anchor at `sub_523980`, so forcing a second alias
  here would not improve source ownership clarity.
- I also left `sub_523280` deferred. It sits in the same address corridor,
  but the HLIL is a compiler-transformed coupling/residue helper that does not
  map one-to-one onto a stable standalone `res0.c` function name.

## Aliases Added

- `sub_522060` -> `res0_free_info`
- `sub_522090` -> `res0_free_look`
- `sub_522120` -> `icount`
- `sub_522140` -> `res0_pack`
- `sub_522230` -> `res0_unpack`
- `sub_522360` -> `res0_look`
- `sub_522880` -> `_encodepart`
- `sub_5228E0` -> `_01class`
- `sub_523030` -> `_01inverse`
- `sub_523220` -> `res0_inverse`
- `sub_523470` -> `res1_class`
- `sub_5234D0` -> `res1_inverse`

## Alias Corrected

- `sub_522D40` -> `_01forward` (from the older placeholder
  `vorbis_residue_01forward`)

## Verification

Static mapping validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- scoped duplicate-key scan for the `quakelive_steam` alias block passed with
  `0` duplicates
- recount after this pass: `2026` raw alias entries, `1958` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `35.776%` of `5473` functions
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
| 2 | `0x0041AD70` | `FUN_0041ad70` | `517` |
| 3 | `0x004E6730` | `FUN_004e6730` | `504` |
| 4 | `0x004B4100` | `FUN_004b4100` | `502` |
| 5 | `0x00475200` | `FUN_00475200` | `497` |
| 6 | `0x0047DA20` | `FUN_0047da20` | `497` |
| 7 | `0x00409670` | `FUN_00409670` | `496` |
| 8 | `0x004B3672` | `FUN_004b3672` | `495` |
| 9 | `0x0051A990` | `FUN_0051a990` | `493` |
| 10 | `0x0041C400` | `FUN_0041c400` | `492` |

The next pass can still return to the transformed `vorbisfile.c` helper at
`sub_4FC240`, take the persistent STL/iostream queue head at `sub_41AD70`, or
keep pushing through the retained Vorbis block with the remaining transformed
residue helper at `sub_523280`.
