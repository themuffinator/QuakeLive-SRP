# quakelive_steam.exe Mapping Round 167

Date: 2026-04-27

Scope: retained CZMQ regex/runtime recovery centered on the old `0x004F7B70`
queue head. This pass resolves the embedded `slre` compiler/matcher lane plus
the public `zrex` wrapper surface. It stayed mapping-only.

## Summary

This round added `23` exact `quakelive_steam.exe` aliases and corrected `1`
older over-specific alias.
Classification mix:

- `0` engine-owned functions
- `23` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The useful outcome is that the old anonymous regex slab from `sub_4F77C0`
through `sub_4F8920` now reads as a coherent retained subsystem instead of a
mix of ad hoc parser helpers and one guessed top-level name. The queue-head
`sub_4F7B70` closes as the real `compile` function from the embedded `slre`
engine, the larger VM core `sub_4F8060` is corrected from
`zrex_match_program` to the exact internal `match`, and the adjacent public
surface now reads cleanly as `slre_compile`, `slre_match`, `zrex_new`,
`zrex_matches`, `zrex_eq`, `zrex_hit`, and `zrex_fetch`.

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_4F8060` | `1339` | platform-service-owned | `match` | High | Corrected from the older over-broad `zrex_match_program`; the HLIL preserves the exact `BRANCH`/`EXACT`/`STAR`/`PLUS`/`ANYOF` opcode VM switch from retained `slre.inc_c`. |
| 2 | `sub_4F7B70` | `506` | platform-service-owned | `compile` | High | Closed from the exact parser switch over `$`, `(`, `)`, `*`, `+`, `.`, `?`, `[`, `\\`, `^`, and `|`, including the same `"No closing bracket"` / `"Unbalanced brackets"` error strings from `slre.inc_c`. |
| 3 | `sub_4F8740` | `362` | platform-service-owned | `zrex_matches` | High | Closed from the exact `slre_match` call, hit-count clamp to `MAX_HITS`, aggregate `hit_set` sizing/allocation, and per-capture memcpy setup from retained `zrex.c`. |
| 4 | `sub_4F79B0` | `188` | platform-service-owned | `anyof` | High | Closed from the exact `[^...]` vs `[...]` branch, embedded escaped-class handling, and `"No closing ']' bracket"` failure path in `slre.inc_c`. |
| 5 | `sub_4F7E20` | `162` | platform-service-owned | `slre_compile` | High | Closed from the exact reset of code/data/capture state, anchored-`^` flag, wrapping `OPEN 0`/`CLOSE 0`/`END` emission, and `code[2] == BRANCH` fixup path. |
| 6 | `sub_4F8670` | `157` | platform-service-owned | `zrex_new` | High | Closed from the exact `zmalloc(sizeof(zrex_t))`, `"No error"` init, optional `slre_compile`, `valid` flag store, and `num_caps < MAX_HITS` assertion in the slre-based `zrex.c`. |
| 7 | `sub_4F7ED0` | `133` | platform-service-owned | `loop_greedy` | High | Closed from the exact greedy inner-loop pattern: repeated `match(pc+2)`, probe of the tail branch, saved best offset, and final longest-match rewind. |
| 8 | `sub_4F7F60` | `128` | platform-service-owned | `loop_non_greedy` | High | Closed from the exact non-greedy sibling loop: advance one inner match at a time and stop as soon as the post-quantifier tail matches. |
| 9 | `sub_4F7AA0` | `115` | platform-service-owned | `quantifier` | High | Closed from the exact split-`EXACT` fast path, `relocate(..., 2)`, opcode rewrite to `STAR`/`PLUS`/`QUEST`/nongreedy variants, and `set_jump_offset` tail. |
| 10 | `sub_4F8600` | `107` | platform-service-owned | `slre_match` | High | Closed from the exact anchored-vs-searching outer loop that either calls `match(..., 0, ...)` once or slides the start offset across the buffer until a match is found. |
| 11 | `sub_4F78C0` | `104` | platform-service-owned | `get_escape_char` | High | Closed from the exact escape decoding for `\\n`, `\\r`, `\\t`, `\\0`, `\\s`, `\\S`, `\\d`, `\\D`, `\\a`, `\\A`, `\\w`, and `\\W`, including the high-byte opcode return path for character classes. |
| 12 | `sub_4F7850` | `101` | platform-service-owned | `exact` | High | Closed from the exact literal-run scanner that stops on `meta_chars`, copies bytes into the data area, and emits the `EXACT data_offset data_length` triplet. |
| 13 | `sub_4F88B0` | `67` | platform-service-owned | `zrex_eq` | High | Closed from the exact recompile-on-demand path: `slre_compile`, `valid`/`strerror` refresh, `num_caps` assertion, and `zrex_matches` tailcall on success. |
| 14 | `sub_4F8920` | `53` | platform-service-owned | `zrex_fetch` | High | Closed from the exact variadic fetch loop that walks caller-supplied output pointers and fills them from `zrex_hit(self, ++index)`. |
| 15 | `sub_4F7FE0` | `51` | platform-service-owned | `is_any_of` | High | Closed from the exact set-membership scan that advances the input offset only on a positive match. |
| 16 | `sub_4F8020` | `51` | platform-service-owned | `is_any_but` | High | Closed from the exact negated-set sibling that rejects on the first found byte and advances only when the byte is absent from the set. |
| 17 | `sub_4F77C0` | `47` | platform-service-owned | `set_jump_offset` | High | Closed from the exact forward-relative branch patcher and the retained `"Jump offset is too big"` diagnostic. |
| 18 | `sub_4F7820` | `47` | platform-service-owned | `store_char_in_data` | High | Closed from the exact data-area append helper and the retained `"RE is too long (data overflow)"` diagnostic. |
| 19 | `sub_4F8710` | `46` | platform-service-owned | `zrex_destroy` | High | Closed from the exact `zstr_free(&hit_set)` plus `free(self)` teardown path from the slre-based `zrex.c`. |
| 20 | `sub_4F77F0` | `43` | platform-service-owned | `emit` | High | Closed from the exact code-area append helper and the retained `"RE is too long (code overflow)"` diagnostic. |
| 21 | `sub_4F7A70` | `41` | platform-service-owned | `relocate` | High | Closed from the exact `emit(END)` plus `memmove` block-shift helper used during branch and quantifier rewriting. |
| 22 | `sub_4F7B20` | `38` | platform-service-owned | `exact_one_char` | High | Closed from the exact one-byte `EXACT` emission helper that stores the character in the data section. |
| 23 | `sub_4F8900` | `30` | platform-service-owned | `zrex_hit` | High | Closed from the exact bounds check against `self->hits` and indexed return from the prepared `hit[]` array. |
| 24 | `sub_4F7B50` | `24` | platform-service-owned | `fixup_branch` | High | Closed from the exact optional branch trailer emitter that appends `END` and patches the forward jump when `fixup > 0`. |

## Evidence Notes

- The core parser and VM helpers match the retained
  `E:\Temp\ql_zmq_upstream\czmq\src\foreign\slre\slre.inc_c` implementation,
  not the newer T-Rex node-based engine. The decisive anchors are the shared
  error strings `"Jump offset is too big"`, `"RE is too long (code overflow)"`,
  `"RE is too long (data overflow)"`, `"No closing ']' bracket"`,
  `"No closing bracket"`, and `"Unbalanced brackets"`, plus the identical
  bytecode opcodes `END`, `BRANCH`, `ANY`, `EXACT`, `ANYOF`, `ANYBUT`,
  `OPEN`, `CLOSE`, `BOL`, `EOL`, `STAR`, `PLUS`, `STARQ`, `PLUSQ`, and
  `QUEST`.
- The public wrapper surface matches the retained slre-based
  `E:\Temp\ql_zmq_upstream\czmq\src\zrex.c` generation whose fields are
  `slre`, `valid`, `strerror`, `hits`, `hit_set_len`, `hit_set`, `hit[]`,
  and `caps[]`. That ownership is a better fit for the retail binary than the
  later tagged `v2.2.0` T-Rex-based `zrex.c`, which uses a different object
  layout and lazy-hit API.
- `sub_4F8740`, `sub_4F88B0`, `sub_4F8900`, and `sub_4F8920` are especially
  stable because the HLIL preserves the exact `hit_set` allocation/copy lane,
  the `slre_compile` + `valid` refresh path, and the variadic `zrex_fetch`
  pointer walk used by upstream callers such as `zsock_bind`.
- I intentionally left the STL/iostream queue head `sub_41AD70` and the
  deferred `vorbisfile.c` helper `sub_4FC240` untouched in this round. The
  regex seam was exact and dense enough to close first without forcing weaker
  host names.

## Aliases Added

- `sub_4F77C0` -> `set_jump_offset`
- `sub_4F77F0` -> `emit`
- `sub_4F7820` -> `store_char_in_data`
- `sub_4F7850` -> `exact`
- `sub_4F78C0` -> `get_escape_char`
- `sub_4F79B0` -> `anyof`
- `sub_4F7A70` -> `relocate`
- `sub_4F7AA0` -> `quantifier`
- `sub_4F7B20` -> `exact_one_char`
- `sub_4F7B50` -> `fixup_branch`
- `sub_4F7B70` -> `compile`
- `sub_4F7E20` -> `slre_compile`
- `sub_4F7ED0` -> `loop_greedy`
- `sub_4F7F60` -> `loop_non_greedy`
- `sub_4F7FE0` -> `is_any_of`
- `sub_4F8020` -> `is_any_but`
- `sub_4F8600` -> `slre_match`
- `sub_4F8670` -> `zrex_new`
- `sub_4F8710` -> `zrex_destroy`
- `sub_4F8740` -> `zrex_matches`
- `sub_4F88B0` -> `zrex_eq`
- `sub_4F8900` -> `zrex_hit`
- `sub_4F8920` -> `zrex_fetch`

## Alias Correction

- `sub_4F8060`: `zrex_match_program` -> `match`

## Verification

Static mapping validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- scoped duplicate-key scan for the `quakelive_steam` alias block passed with
  `0` duplicates
- recount after this pass: `1933` raw alias entries, `1861` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `34.003%` of `5473` functions
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
| 3 | `0x0043F590` | `FUN_0043f590` | `507` |
| 4 | `0x00486D40` | `FUN_00486d40` | `504` |
| 5 | `0x004E6730` | `FUN_004e6730` | `504` |
| 6 | `0x0050C790` | `FUN_0050c790` | `503` |
| 7 | `0x004B4100` | `FUN_004b4100` | `502` |
| 8 | `0x00510050` | `FUN_00510050` | `501` |
| 9 | `0x00475200` | `FUN_00475200` | `497` |
| 10 | `0x0047DA20` | `FUN_0047da20` | `497` |

The next pass can go back to the deferred `vorbisfile.c` recursive search
helper at `sub_4FC240`, take the still-opaque STL/iostream queue head at
`sub_41AD70`, or pivot into the remaining unresolved client/host leftovers
around `sub_43F590`, `sub_486D40`, and `sub_4E6730`.
