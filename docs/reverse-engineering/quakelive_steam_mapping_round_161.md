# quakelive_steam.exe Mapping Round 161

Date: 2026-04-27

Scope: `l_precomp.c` precompiler token and handle-wrapper recovery around the
old `0x004AC440` queue head. This pass stayed mapping-only.

## Summary

This round resolved `8` additional `quakelive_steam.exe` rows.
Classification mix:

- `8` engine-owned functions
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main outcome is that the old anonymous precompiler seam around
`0x004AC440` now reads cleanly as the checked-in `l_precomp.c` public token
API: handle-to-source filename/line reporting, base-folder setup, open-source
handle diagnostics, the recursive `PC_ReadToken` front-end, and the small
expect/check wrappers used across botlib parsers. This closes a useful exact
ownership band around the already-mapped `PC_ExpectTokenType`,
`PC_Directive_define`, `PC_ExpandDefine`, and `PC_ReadDefineParms` lane.

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_4AC440` | `521` | engine-owned | `PC_ReadToken` | High | Closed from the exact `#` and `$` directive handling, recursive adjacent-string concatenation, `source->skip` filter, define lookup/expand path, and copied unread token tail. |
| 2 | `sub_4AC650` | `190` | engine-owned | `PC_ExpectTokenString` | High | Closed from the exact `couldn't find expected %s` and `expected %s, found %s` error path wrapped around `PC_ReadToken`. |
| 3 | `sub_4ACB10` | `163` | engine-owned | `PC_ReadTokenHandle` | High | Closed from the exact source-handle bounds check, copied `pc_token_t` fields, and `StripDoubleQuotes` tail for string tokens. |
| 4 | `sub_4ACA70` | `146` | engine-owned | `PC_CheckTokenString` | High | Closed from the exact `PC_ReadToken`, `strcmp`, and unread-on-mismatch behavior. |
| 5 | `sub_4AC390` | `100` | engine-owned | `PC_SourceFileAndLine` | High | Closed from the exact handle validation, filename copy from `sourceFiles[handle]`, and conditional script-stack line return. |
| 6 | `sub_4ACA30` | `51` | engine-owned | `PC_ExpectAnyToken` | High | Closed from the exact `PC_ReadToken` gate and single `couldn't read expected token` failure string. |
| 7 | `sub_4AC410` | `48` | engine-owned | `PC_CheckOpenSourceHandles` | High | Closed from the exact loop over open `sourceFiles[]` slots and `file %s still open in precompiler` diagnostic. |
| 8 | `sub_4AC400` | `9` | engine-owned | `PC_SetBaseFolder` | High | Closed from the exact tailcall wrapper into `PS_SetBaseFolder`. |

## Evidence Notes

- The recovered tranche maps directly onto the checked-in
  [l_precomp.c](</E:/Repositories/QuakeLive-reverse/src/code/botlib/l_precomp.c:2704>)
  helper lane:
  [PC_ReadToken](</E:/Repositories/QuakeLive-reverse/src/code/botlib/l_precomp.c:2704>),
  [PC_ExpectTokenString](</E:/Repositories/QuakeLive-reverse/src/code/botlib/l_precomp.c:2787>),
  [PC_ExpectAnyToken](</E:/Repositories/QuakeLive-reverse/src/code/botlib/l_precomp.c:2863>),
  [PC_CheckTokenString](</E:/Repositories/QuakeLive-reverse/src/code/botlib/l_precomp.c:2881>),
  [PC_ReadTokenHandle](</E:/Repositories/QuakeLive-reverse/src/code/botlib/l_precomp.c:3158>),
  [PC_SourceFileAndLine](</E:/Repositories/QuakeLive-reverse/src/code/botlib/l_precomp.c:3184>),
  [PC_SetBaseFolder](</E:/Repositories/QuakeLive-reverse/src/code/botlib/l_precomp.c:3204>),
  and [PC_CheckOpenSourceHandles](</E:/Repositories/QuakeLive-reverse/src/code/botlib/l_precomp.c:3214>).
- `sub_4AC440` is the key ownership anchor for this pass. The HLIL preserves
  the exact front-end structure from `PC_ReadToken`: raw source-token read,
  precompiler and dollar-directive interception, recursive string
  concatenation with `MAX_TOKEN` bounds checking, skip-mode filtering, define
  expansion, and final copy into `source->token`.
- `sub_4AC400` is promoted as `PC_SetBaseFolder` from the exact one-line
  wrapper in [l_precomp.c](</E:/Repositories/QuakeLive-reverse/src/code/botlib/l_precomp.c:3204>)
  and its preserved tailcall into
  [PS_SetBaseFolder](</E:/Repositories/QuakeLive-reverse/src/code/botlib/l_script.c:1426>).
- `sub_4ACB10` closes the retail handle wrapper that feeds the client/server/UI
  botlib import layer. The field copy order, string stripping, and shared
  `PC_ReadToken` call relationship match the checked-in source exactly.
- I intentionally left the surrounding unread/check/set-path/source-lifetime
  helpers unmapped in this round. They are clearly nearby in `l_precomp.c`,
  but I did not want to force additional starts without the same exact
  function-boundary confidence as this tranche.

## Aliases Added

- `sub_4AC390` -> `PC_SourceFileAndLine`
- `sub_4AC400` -> `PC_SetBaseFolder`
- `sub_4AC410` -> `PC_CheckOpenSourceHandles`
- `sub_4AC440` -> `PC_ReadToken`
- `sub_4AC650` -> `PC_ExpectTokenString`
- `sub_4ACA30` -> `PC_ExpectAnyToken`
- `sub_4ACA70` -> `PC_CheckTokenString`
- `sub_4ACB10` -> `PC_ReadTokenHandle`

## Verification

Static mapping validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- scoped duplicate-key scan for the `quakelive_steam` alias block passed with
  `0` duplicates
- recount after this pass: `1842` raw alias entries, `1770` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `32.341%` of `5473` functions
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
| 3 | `0x00511670` | `FUN_00511670` | `520` |
| 4 | `0x00523B40` | `FUN_00523b40` | `520` |
| 5 | `0x00524370` | `FUN_00524370` | `520` |
| 6 | `0x00524580` | `FUN_00524580` | `520` |
| 7 | `0x00417790` | `FUN_00417790` | `518` |
| 8 | `0x0041AD70` | `FUN_0041ad70` | `517` |
| 9 | `0x00512340` | `FUN_00512340` | `517` |
| 10 | `0x004F5200` | `FUN_004f5200` | `514` |

The next pass can return to the still-transformed `vorbisfile.c` search helper
at `sub_4FC240`, the opaque `sub_4FAF60` file-wrapper slab, or keep pushing
through the larger support-library queue heads now that the `l_precomp.c`
public token API is less anonymous.
