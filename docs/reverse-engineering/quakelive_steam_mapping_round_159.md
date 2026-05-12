# quakelive_steam.exe Mapping Round 159

Date: 2026-04-27

Scope: retained `zlib` `trees.c` Huffman-tree and block-flush recovery around
the old `0x00501ED0` queue head. This pass stayed mapping-only.

## Summary

This round resolved `15` additional `quakelive_steam.exe` rows.
Classification mix:

- `0` engine-owned functions
- `0` platform-service-owned functions
- `15` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main outcome is that the old anonymous `0x00501***` through `0x005036**`
slab now reads cleanly as the retained `zlib/trees.c` Huffman-management lane:
block initialization, heap maintenance, code-length generation, bit-length-tree
scan/build, data-type detection, stored/static/dynamic block selection, and the
public `_tr_*` flush helpers. This turns the former queue-head band into a
coherent compression subsystem centered on the already-mapped `send_tree`,
`send_all_trees`, and `compress_block` helpers.

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_501ED0` | `529` | support-library | `gen_bitlen` | High | Closed from the exact `bl_count` zeroing, heap-root `Len = 0` seed, overflow rebalance loop, and `opt_len` / `static_len` accounting. |
| 2 | `sub_503630` | `526` | support-library | `_tr_flush_block` | High | Closed from the exact `detect_data_type` gate, paired literal/distance `build_tree` calls, `build_bl_tree`, stored-vs-static-vs-dynamic selection, `init_block`, and optional final `bi_windup` path. |
| 3 | `sub_5030D0` | `503` | support-library | `build_tree` | High | Closed from the exact heap construction, forced two-code minimum, repeated least-frequency combine loop, then final `gen_bitlen` and `gen_codes` tail. |
| 4 | `sub_503440` | `493` | support-library | `_tr_align` | High | Closed from the exact `STATIC_TREES` block-type write, `END_BLOCK` send on `static_ltree`, follow-up `bi_flush`, and optional second empty static block when lookahead is too small. |
| 5 | `sub_5020F0` | `226` | support-library | `scan_tree` | High | Closed from the exact repeat-count walk over `tree[n].Len`, `REP_3_6`, `REPZ_3_10`, and `REPZ_11_138` frequency accumulation into `bl_tree`. |
| 6 | `sub_502D60` | `203` | support-library | `detect_data_type` | High | Closed from the compiler-unrolled scan of the block-listed and allow-listed literal-frequency sets that writes `Z_BINARY` or `Z_TEXT` into `strm->data_type`. |
| 7 | `sub_501E00` | `198` | support-library | `pqdownheap` | High | Closed from the exact left-son walk, `smaller(...)` tie-breaker on tree depth, and sift-down heap restore over `s->heap`. |
| 8 | `sub_5032D0` | `198` | support-library | `build_bl_tree` | High | Closed from the exact paired `scan_tree` calls on `dyn_ltree` and `dyn_dtree`, `build_tree(&s->bl_desc)`, trailing `bl_order` reverse scan, and `opt_len += 3*(max_blindex+1)+5+5+4`. |
| 9 | `sub_5033A0` | `159` | support-library | `_tr_stored_block` | High | Closed from the exact stored-block type write followed by the helper that byte-aligns and copies the literal payload with header words. |
| 10 | `sub_503050` | `125` | support-library | `gen_codes` | High | Closed from the exact `next_code[MAX_BITS+1]` build, consistency check, and `bi_reverse(next_code[len]++, len)` code assignment. |
| 11 | `sub_502E50` | `117` | support-library | `bi_flush` | High | Closed from the exact `bi_valid == 16` and `bi_valid >= 8` flush cases that keep at most seven bits buffered. |
| 12 | `sub_502ED0` | `115` | support-library | `bi_windup` | High | Closed from the exact byte-alignment flush that writes either one or two bytes, then zeroes `bi_buf` and `bi_valid`. |
| 13 | `sub_501D90` | `110` | support-library | `init_block` | High | Closed from the exact zeroing of `dyn_ltree`, `dyn_dtree`, and `bl_tree`, plus `END_BLOCK` seed and `opt_len` / `static_len` / `sym_next` / `matches` reset. |
| 14 | `sub_502FE0` | `100` | support-library | `_tr_init` | High | Closed from the exact descriptor wiring for `l_desc`, `d_desc`, and `bl_desc`, `bi_buf` / `bi_valid` reset, and final `init_block` tail. |
| 15 | `sub_502E30` | `25` | support-library | `bi_reverse` | High | Closed from the exact bit-at-a-time reverse loop used by `gen_codes` and the static tree initialization path. |

## Evidence Notes

- The recovered tranche maps directly onto the checked-in
  [trees.c](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/zlib/trees.c:154>)
  helper lane:
  [bi_reverse](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/zlib/trees.c:154>),
  [bi_flush](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/zlib/trees.c:166>),
  [bi_windup](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/zlib/trees.c:181>),
  [gen_codes](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/zlib/trees.c:202>),
  [init_block](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/zlib/trees.c:439>),
  [_tr_init](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/zlib/trees.c:455>),
  [pqdownheap](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/zlib/trees.c:507>),
  [gen_bitlen](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/zlib/trees.c:538>),
  [build_tree](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/zlib/trees.c:625>),
  [scan_tree](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/zlib/trees.c:710>),
  [build_bl_tree](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/zlib/trees.c:798>),
  [_tr_stored_block](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/zlib/trees.c:858>),
  [_tr_align](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/zlib/trees.c:886>),
  [compress_block](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/zlib/trees.c:898>),
  [detect_data_type](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/zlib/trees.c:964>),
  and [_tr_flush_block](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/zlib/trees.c:995>).
- `sub_503630` is the key ownership anchor for this pass. The body first runs
  the optional data-type detector, builds the literal and distance trees,
  derives `max_blindex` through `build_bl_tree`, compares stored, static, and
  dynamic block costs, dispatches into the matching block writer, resets the
  block through `init_block`, and conditionally calls `bi_windup` on `last`.
- `sub_502D60` is an exact `detect_data_type` hit despite the compiler turning
  the original block-mask loop into a sparse literal-frequency probe. The HLIL
  still preserves the exact `0..6`, `14..25`, `28..31` block-list behavior and
  the `9`, `10`, `13`, `32..255` text allow-list outcome that writes back to
  `strm->data_type`.
- `sub_5033A0` is promoted as `_tr_stored_block` even though the retail build
  keeps the payload-copy mechanics in the separate `sub_502F50` helper. The
  public wrapper's role is stable from the stored-block header write and the
  exact call relationship into that byte-aligned copy path.
- I intentionally left `sub_502F50` unnamed in this pass. Its behavior clearly
  matches the stored-block payload copy helper, but the checked-in `trees.c`
  keeps that logic inlined inside `_tr_stored_block`, so I preferred not to
  force an extra non-committed helper alias.

## Aliases Added

- `sub_501D90` -> `init_block`
- `sub_501E00` -> `pqdownheap`
- `sub_501ED0` -> `gen_bitlen`
- `sub_5020F0` -> `scan_tree`
- `sub_502D60` -> `detect_data_type`
- `sub_502E30` -> `bi_reverse`
- `sub_502E50` -> `bi_flush`
- `sub_502ED0` -> `bi_windup`
- `sub_502FE0` -> `_tr_init`
- `sub_503050` -> `gen_codes`
- `sub_5030D0` -> `build_tree`
- `sub_5032D0` -> `build_bl_tree`
- `sub_5033A0` -> `_tr_stored_block`
- `sub_503440` -> `_tr_align`
- `sub_503630` -> `_tr_flush_block`

## Verification

Static mapping validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- scoped duplicate-key scan for the `quakelive_steam` alias block passed with
  `0` duplicates
- recount after this pass: `1820` raw alias entries, `1749` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `31.957%` of `5473` functions
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
| 3 | `0x00498BB0` | `FUN_00498bb0` | `526` |
| 4 | `0x004AC440` | `FUN_004ac440` | `521` |
| 5 | `0x00511670` | `FUN_00511670` | `520` |
| 6 | `0x00523B40` | `FUN_00523b40` | `520` |
| 7 | `0x00524370` | `FUN_00524370` | `520` |
| 8 | `0x00524580` | `FUN_00524580` | `520` |
| 9 | `0x00417790` | `FUN_00417790` | `518` |
| 10 | `0x0041AD70` | `FUN_0041ad70` | `517` |

The next pass can return to the still-transformed `vorbisfile.c` search helper
at `sub_4FC240`, the opaque `sub_4FAF60` file-wrapper slab, or pivot back to
the larger engine-owned leftovers now that the `trees.c` queue head is closed.
