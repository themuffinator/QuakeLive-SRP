# quakelive_steam.exe Mapping Round 203

Date: 2026-04-28

Scope: retained JsonCpp `json_value.cpp` ownership around the old engine queue
heads `0x00429DD0` and `0x0042A130`.

## Summary

This round resolved `6` additional `quakelive_steam.exe` aliases.
Classification mix:

- `0` engine-owned functions
- `0` platform-service-owned functions
- `6` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The useful outcome is that the heavy anonymous `0x00429***` Json seam now reads
as exact retained JsonCpp ownership instead of generic host glue. The two old
queue heads are gone, and the adjacent copy/destroy/assign/storage helpers now
carry their upstream names too.

## Evidence Notes

- The primary cross-binary anchor is the closed qagame JsonCpp lane already
  recorded in
  [references/symbol-maps/qagame.json](</E:/Repositories/QuakeLive-reverse/references/symbol-maps/qagame.json>)
  and summarized in
  [docs/reverse-engineering/qagame-mapping.md](</E:/Repositories/QuakeLive-reverse/docs/reverse-engineering/qagame-mapping.md:55>).
- `sub_429DD0` is exact as `JsonValueOperatorIndexArrayIndex`. Its HLIL
  promotes null values to type `6`, allocates a `0x10` map header, initializes
  that header through `sub_42A8F0`, performs the numeric member lookup through
  `sub_42B1F0`, inserts a default `null` payload through `sub_42B760`, and
  returns the nested value slot at `&node[6]`, which matches the retained
  JsonCpp `operator[]( ArrayIndex )` body.
- `sub_42A130` is exact as `JsonValueOperatorIndexCString`. The retained body
  mirrors the same null-to-object promotion and map lookup/insert flow, but it
  seeds the temporary key from the incoming `const char *` and follows the
  inlined `resolveReference( key, false )` member path described in the qagame
  map comments.
- `sub_42A8F0` is exact as `JsonValueInitMapStorage`. The HLIL allocates the
  `0x30` red-black-tree sentinel node, points the root/left/right links back to
  that sentinel, zeroes the stored size, and seeds the empty-tree color flags
  exactly like the descriptive qagame owner.
- The adjacent helper trio also matches qagame exactly:
  `sub_4294C0 -> JsonValueCopyConstruct`,
  `sub_429620 -> JsonValueDestructor`, and
  `sub_4296C0 -> JsonValueOperatorAssign`. Their retained HLIL still shows the
  expected scalar/string/map copy branches, the map/comment teardown path, and
  the copy-swap style assignment sequence around a stack temporary.
- I left `sub_42B1F0` unnamed in this round. Its role as the shared Json object
  member lower-bound walker is clear, but the committed naming scheme in this
  repo prefers the already-established descriptive STL helper aliases there over
  forcing a new exact JsonCpp wrapper name that qagame does not currently carry.

## Aliases Added

- `sub_4294C0` -> `JsonValueCopyConstruct`
- `sub_429620` -> `JsonValueDestructor`
- `sub_4296C0` -> `JsonValueOperatorAssign`
- `sub_429DD0` -> `JsonValueOperatorIndexArrayIndex`
- `sub_42A130` -> `JsonValueOperatorIndexCString`
- `sub_42A8F0` -> `JsonValueInitMapStorage`

## Verification

Static mapping validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- scoped duplicate-key scan for the `quakelive_steam` alias block passed with
  `0` duplicates
- recount after this pass: `2155` raw alias entries, `2082` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `38.041%` of `5473` functions
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
| 2 | `0x004A4280` | `FUN_004a4280` | `483` |
| 3 | `0x004B6630` | `FUN_004b6630` | `483` |
| 4 | `0x004241C0` | `FUN_004241c0` | `482` |
| 5 | `0x00498890` | `FUN_00498890` | `480` |
| 6 | `0x00480DD0` | `FUN_00480dd0` | `479` |
| 7 | `0x004C84E0` | `FUN_004c84e0` | `479` |
| 8 | `0x0050EF80` | `FUN_0050ef80` | `476` |
| 9 | `0x00412970` | `FUN_00412970` | `472` |
| 10 | `0x004A21A0` | `FUN_004a21a0` | `470` |

The next pass can keep probing the `FUN_004b3672` console split, return to the
remaining engine-owned `0x004A4***` seam, or continue harvesting the adjacent
retained support-library slabs where the cross-binary qagame evidence stays
strong.
