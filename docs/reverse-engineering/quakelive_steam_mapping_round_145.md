# quakelive_steam.exe Mapping Round 145

Date: 2026-04-27

Scope: refreshed largest-unaliased queue after round 144. This pass consumed
the stb_truetype helper lane headed by `sub_440AD0` and promoted the exact
support-library sort/tessellation helpers that sit between the already-mapped
`stbtt_FlattenCurves` and `stbtt__rasterize_sorted_edges`.

## Summary

This round resolved `3` support-library-owned `quakelive_steam.exe` rows:
`3` previously unresolved exact aliases from the bundled stb_truetype raster
pipeline. Classification mix:

- `0` engine-owned functions
- `0` platform-service-owned functions
- `3` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

No source debt was opened. The promoted helpers close the exact edge-sort and
quadratic curve-tessellation lane that feeds Quake Live's fontstash glyph
raster path, so they reduce host-map noise without changing any engine-owned
parity conclusions.

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_440AD0` | `560` | CRT/STL/support-library | `stbtt__sort_edges_quicksort` | High | No engine debt; exact stb_truetype median-of-three quicksort over `stbtt__edge` records. |
| 2 | `sub_440920` | `431` | CRT/STL/support-library | `stbtt__sort_edges_ins_sort` | High | No engine debt; exact insertion-sort cleanup pass over the same 20-byte edge records. |
| 3 | `sub_440D00` | `403` | CRT/STL/support-library | `stbtt__tesselate_curve` | High | No engine debt; exact quadratic midpoint tessellator used by `stbtt_FlattenCurves`. |

## Evidence Notes

- `sub_440920` is an exact `stbtt__sort_edges_ins_sort` hit. The body walks
  an array of `0x14`-byte records, compares only the float at offset `+4`,
  shifts prior records upward while the incoming `y0` key sorts earlier, and
  writes the saved 5-dword record back only when the insertion index changed.
  That matches stb_truetype's insertion-sort cleanup pass exactly.
- `sub_440AD0` is an exact `stbtt__sort_edges_quicksort` match. It keeps the
  same `n > 12` threshold, uses the median-of-three pivot selection on the
  first/middle/last edge `y0`, partitions with the same equality handling, and
  recurses only on the smaller side while iterating on the larger side. The
  caller sequence in `sub_443160`'s raster lane also matches stb exactly:
  quicksort first, insertion sort second, then `sub_442C10`.
- `sub_440D00` is the exact quadratic `stbtt__tesselate_curve` helper used by
  `stbtt_FlattenCurves`. The body computes the midpoint
  `(x0 + 2*x1 + x2) / 4`, compares squared deviation from the direct line
  against `objspace_flatness_squared`, enforces the same `n > 16` recursion
  guard, recursively subdivides both halves when needed, and otherwise appends
  the curve endpoint. `sub_443160` calls it from the `STBTT_vcurve` branch,
  which locks ownership to stb_truetype rather than engine code.

## Aliases Added

- `sub_440920` -> `stbtt__sort_edges_ins_sort`
- `sub_440AD0` -> `stbtt__sort_edges_quicksort`
- `sub_440D00` -> `stbtt__tesselate_curve`

## Verification

Alias artifact validation:

- `references/analysis/quakelive_symbol_aliases.json` parses through
  `python -m json.tool`
- duplicate-key scan passed after the alias update
- recount after this pass: `1663` raw alias entries, `1592` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `29.088%` of `5473` functions
- refreshed unresolved queue was recomputed against the committed Ghidra
  function-start corpus after the alias update
- no game/runtime launch was performed; this was a static mapping pass

Parity estimate after this mapping-only pass remains unchanged:

- strict-retail Windows replacement target: `100%` before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

After this round, the refreshed largest-unaliased queue begins with:

| # | Address | Ghidra name | Size |
| ---: | --- | --- | ---: |
| 1 | `0x00435070` | `FUN_00435070` | `566` |
| 2 | `0x0040B050` | `FUN_0040b050` | `555` |
| 3 | `0x00419AD0` | `FUN_00419ad0` | `555` |
| 4 | `0x0040F7E0` | `FUN_0040f7e0` | `549` |
| 5 | `0x0041CFB0` | `FUN_0041cfb0` | `549` |
| 6 | `0x0042BA60` | `FUN_0042ba60` | `549` |
| 7 | `0x004940D0` | `FUN_004940d0` | `547` |
| 8 | `0x004F4410` | `FUN_004f4410` | `546` |
| 9 | `0x00475CA0` | `FUN_00475ca0` | `545` |
| 10 | `0x004999C0` | `FUN_004999c0` | `541` |

The next pass should return to the still-unresolved renderer debug lane at
`sub_435070`, then keep working down the remaining queue head while preserving
the existing classification guardrails on engine, platform-service, and
support-library rows.
