# Botlib Precompiler Macro Expansion Mapping - 2026-06-05

## Scope

This pass selects the `src/code/botlib/l_precomp.c` macro expansion internals
as the next botlib slice after directive dispatch and token reading. The slice
covers:

- `PC_ReadDefineParms`
- `PC_StringizeTokens`
- `PC_MergeTokens`
- define hash and lookup helpers used by expansion
- `PC_FreeDefine`
- `PC_AddBuiltinDefines`
- `PC_ExpandBuiltinDefine`
- `PC_ExpandDefine`
- `PC_ExpandDefineIntoSource`
- related wiring from define creation, `PC_ReadToken`, `PC_Evaluate`, and
  `PC_DollarEvaluate`

No runtime launch was needed. Static source, Binary Ninja HLIL, Ghidra function
rows, and focused pytest coverage answer this mapping question.

## Owning Retail Binary

Owning binary:

- `assets/quakelive/quakelive_steam.exe`

Reference corpus used:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part03.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/analysis/quakelive_symbol_aliases.json`
- `src/code/botlib/l_precomp.c`

## Why This Slice

The previous directive pass mapped macro definition parsing, but stopped before
the expansion engine that consumes those definitions. This slice is the next
retail-backed reconstruction boundary because it explains how macro arguments
are captured, substituted, stringized, merged, and finally pushed back into the
source token stream.

This logic is shared by normal token reading and by conditional/directive
evaluation, so it is a central precompiler behavior surface even though it has
no direct qagame ABI entry of its own.

## Retail Evidence

Alias-map promotions for the selected slice:

- `sub_4A8C30 -> PC_CopyToken`
- `sub_4A8C90 -> PC_ReadSourceToken`
- `sub_4A8DB0 -> PC_UnreadSourceToken`
- `sub_4A8E20 -> PC_ReadDefineParms`
- `sub_4A9230 -> PC_StringizeTokens`
- `sub_4A92D0 -> PC_MergeTokens`
- `sub_4A9370 -> PC_NameHash`
- `sub_4A93B0 -> PC_AddDefineToHash`
- `sub_4A9410 -> PC_FindHashedDefine`
- `sub_4A94A0 -> PC_FindDefineParm`
- `sub_4A9500 -> PC_FreeDefine`
- `sub_4A9570 -> PC_ExpandBuiltinDefine`
- `sub_4A97B0 -> PC_ExpandDefine`
- `sub_4A9B70 -> PC_ExpandDefineIntoSource`

Ghidra `functions.csv` corroborates the selected retail bodies and sizes:

- `FUN_004a8e20,004a8e20,1012,0,unknown`
- `FUN_004a9230,004a9230,157,0,unknown`
- `FUN_004a92d0,004a92d0,145,0,unknown`
- `FUN_004a9370,004a9370,63,0,unknown`
- `FUN_004a93b0,004a93b0,85,0,unknown`
- `FUN_004a9410,004a9410,138,0,unknown`
- `FUN_004a94a0,004a94a0,92,0,unknown`
- `FUN_004a9500,004a9500,98,0,unknown`
- `FUN_004a9570,004a9570,556,0,unknown`
- `FUN_004a97b0,004a97b0,947,0,unknown`
- `FUN_004a9b70,004a9b70,88,0,unknown`

Binary Ninja HLIL confirms these behavior anchors:

- `0x004A8E20` reads the opening macro-argument token with
  `PC_ReadSourceToken`, rejects a missing `(` by unreading the token, and
  reports `define %s missing parms`.
- `PC_ReadDefineParms` enforces the caller-provided maximum parameter count,
  clears the parameter-list array, tracks nested parentheses, warns on repeated
  commas and too few parameters, and copies argument tokens into linked lists
  with token link offset `0x428`.
- `0x004A9230` creates a `TT_STRING` token, clears whitespace metadata, writes
  leading and trailing quote characters, and appends each argument-token string.
- `0x004A92D0` permits token merging for name plus name/number and string plus
  string, and returns failure for unsupported combinations.
- `0x004A9370` hashes names with the `(119 + i)` multiplier and folds through
  the 1024-entry define hash.
- `0x004A93B0` inserts a define into the hash chain.
- `0x004A9410` hashes a name and walks hash-next links to find a matching
  define.
- `0x004A94A0` walks the define parameter list and returns the parameter index
  or `-1`.
- `0x004A9500` frees parameter-token and replacement-token chains before
  freeing the define.
- `0x004A9570` handles builtin definitions. Retail cases match `__LINE__`,
  `__FILE__`, `__DATE__`, and `__TIME__`, with line tokens emitted as numbers
  and file/date/time emitted as name-like string contents.
- `0x004A97B0` is the main `PC_ExpandDefine` body. It dispatches builtins,
  reads parameter lists for parameterized macros, substitutes argument token
  chains, handles `#` stringizing, handles `##` merging, reports stringize and
  merge errors, stores first/last expansion tokens, and frees captured parameter
  token chains before returning.
- `0x004A9B70` wraps `PC_ExpandDefine` and pushes a successful expansion onto
  `source->tokens` at source offset `0x808`.

## Source Reconstruction Notes

Observed facts:

- The checked-in source preserves the same readable helper boundaries found in
  the retail symbol map: argument capture, stringize, merge, lookup/free,
  builtin expansion, full expansion, and source-stack injection.
- Token ownership is explicit: `PC_ReadDefineParms` allocates copied argument
  token chains, `PC_ExpandDefine` copies from those chains into the expansion
  list, and then frees the parameter chains before returning.
- `PC_ExpandDefineIntoSource` links `lasttoken->next` to the existing
  `source->tokens` stack and makes `firsttoken` the new stack head.
- Retail `PC_ReadToken` sometimes shows the expansion/link pattern inlined in
  HLIL, but `PC_ExpandDefineIntoSource` remains emitted and called by
  expression-evaluation paths.

Inference:

- Future behavior fixes in this area should be careful about token ownership and
  linked-list rewrites. Most likely defects would be leaks, double-frees, or
  subtle differences in how `#` and `##` consume neighboring tokens.

## Related Wiring

Producer side:

- `PC_Directive_define` creates the parameter list used by `PC_FindDefineParm`.
- `PC_Directive_define` creates replacement token lists, rejects recursive
  self-reference, and rejects `##` at the beginning or end of the replacement
  list.

Consumer side:

- `PC_ReadToken` expands normal names by finding hashed defines and calling
  `PC_ExpandDefineIntoSource`.
- `PC_Evaluate` expands named defines while evaluating `#if`, `#elif`, `#eval`,
  and `#evalfloat` expressions.
- `PC_DollarEvaluate` expands named defines while evaluating `$evalint` and
  `$evalfloat`.

There is no direct qagame/server ABI for these helpers. External callers reach
them through source loading/token reading and through global define insertion.

## Changes

- Added `tests/test_botlib_precompiler_macro_parity.py`.
- The new test pins:
  - source shape for macro parameter capture
  - stringize and merge source behavior
  - hash, lookup, free, and builtin expansion helpers
  - full `PC_ExpandDefine` source behavior
  - source-stack injection in `PC_ExpandDefineIntoSource`
  - producer/consumer wiring through directive definition, token reading, and
    expression evaluation
  - alias-map promotions
  - Ghidra function rows
  - Binary Ninja HLIL behavior anchors across part03/part04
- No C source body change was needed.
- Central queue files were intentionally left alone to avoid colliding with
  concurrent sessions.

## Validation

Validation performed:

- `python -m pytest tests/test_botlib_precompiler_macro_parity.py -q`
- `python -m pytest tests/test_botlib_precompiler_directive_parity.py tests/test_botlib_precompiler_token_parity.py -q`
- `python -m pytest tests/test_botlib_internal_parity.py -q`
- `python -m pytest tests/test_bot_resource_loading.py -q`

Observed results:

- `1 passed`
- adjacent directive/token precompiler coverage: `2 passed`
- full botlib internal parity file: `31 passed`
- bot resource loading: `3 passed`

No game launch was performed.

## Parity Estimate

- Focused precompiler macro-expansion slice: `62% -> 93%`. Before this round,
  aliases existed, but argument capture, token ownership, stringize/merge
  behavior, builtin expansion, and consumer wiring were not documented and
  pinned together.
- Overall botlib parser/API wiring: approximately `71% -> 72%`.
- Strict-retail Windows replacement target: unchanged at `100%`.

## Next Candidate Slices

Good follow-on slices:

- `PC_EvaluateTokens`, including operator precedence, ternary handling, and
  integer versus floating-point restrictions.
- Lower `l_script.c` token scanning, especially number and punctuation behavior
  shared by bot resource parsers.
- `PC_AddBuiltinDefines` source lifecycle around `LoadSourceFile` and
  `LoadSourceMemory`, if future evidence shows builtins are enabled in a retail
  path not already covered by this pass.
