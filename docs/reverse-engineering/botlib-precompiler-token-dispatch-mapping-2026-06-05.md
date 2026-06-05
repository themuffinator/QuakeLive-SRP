# Botlib Precompiler Token Dispatch Mapping - 2026-06-05

## Scope

This pass selects the `src/code/botlib/l_precomp.c` token-dispatch layer as the
next botlib slice after the public source-handle wrapper mapping. The slice
covers the internal token reader and the small expect/check/unread helper layer
used by bot resource parsers:

- `PC_ReadToken`
- `PC_ExpectTokenString`
- `PC_ExpectTokenType`
- `PC_ExpectAnyToken`
- `PC_CheckTokenString`
- `PC_CheckTokenType`
- `PC_SkipUntilString`
- `PC_UnreadLastToken`
- `PC_UnreadToken`
- related `PC_ExpandDefineIntoSource` source reconstruction detail

No runtime launch was needed. The committed Binary Ninja HLIL and Ghidra
function table expose the relevant retail bodies and optimized call shape.

## Owning Retail Binary

Owning binary:

- `assets/quakelive/quakelive_steam.exe`

Reference corpus used:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/analysis/quakelive_symbol_aliases.json`
- `src/code/botlib/l_precomp.c`
- `src/code/botlib/l_precomp.h`
- `src/code/botlib/l_struct.c`
- `src/code/botlib/be_ai_chat.c`
- `src/code/botlib/be_ai_char.c`
- `src/code/botlib/be_ai_weight.c`

## Why This Slice

`PC_ReadToken` is the central internal precompiler reader behind the resource
loaders already mapped in earlier passes. The item/weapon/projectile structure
reader, character parser, weight parser, and chat parser all sit above this
helper layer. Mapping it now closes the immediate gap between the public
`PC_ReadTokenHandle` wrapper and the higher-level parser behavior.

The selected slice is also a good source-reconstruction boundary because retail
optimization changes the call shape: the checked-in GPL-style source keeps
small helper bodies such as `PC_ExpandDefineIntoSource` and `PC_UnreadToken`,
while the retail HLIL for `PC_ReadToken` shows some of that work inlined.

## Retail Evidence

Observed alias promotions for the slice:

- `sub_4A8C90 -> PC_ReadSourceToken`
- `sub_4A8DB0 -> PC_UnreadSourceToken`
- `sub_4A9410 -> PC_FindHashedDefine`
- `sub_4A97B0 -> PC_ExpandDefine`
- `sub_4A9B70 -> PC_ExpandDefineIntoSource`
- `sub_4ABC10 -> PC_ReadDirective`
- `sub_4ABF10 -> PC_ReadDollarDirective`
- `sub_4AC030 -> PC_UnreadLastToken`
- `sub_4AC440 -> PC_ReadToken`
- `sub_4AC650 -> PC_ExpectTokenString`
- `sub_4AC710 -> PC_ExpectTokenType`
- `sub_4ACA30 -> PC_ExpectAnyToken`
- `sub_4ACA70 -> PC_CheckTokenString`
- `sub_4ACB10 -> PC_ReadTokenHandle`

Ghidra `functions.csv` corroborates the key retail bodies:

- `FUN_004a97b0,004a97b0,947,0,unknown`
- `FUN_004a9b70,004a9b70,88,0,unknown`
- `FUN_004ac030,004ac030,24,0,unknown`
- `FUN_004ac440,004ac440,521,0,unknown`
- `FUN_004ac650,004ac650,190,0,unknown`
- `FUN_004ac710,004ac710,790,0,unknown`
- `FUN_004aca30,004aca30,51,0,unknown`
- `FUN_004aca70,004aca70,146,0,unknown`
- `FUN_004acb10,004acb10,163,0,unknown`

Binary Ninja HLIL confirms the main body behavior:

- `0x004AC440` calls `PC_ReadSourceToken`.
- Punctuation token type `5` with first character `#` dispatches to
  `PC_ReadDirective`.
- Punctuation token type `5` with first character `$` dispatches to
  `PC_ReadDollarDirective`.
- String token type `1` recursively calls `PC_ReadToken`, concatenates adjacent
  strings, enforces `MAX_TOKEN` size `0x400`, and unread-pushes the non-string
  lookahead token through `PC_UnreadSourceToken`.
- The skip counter at source offset `0x818` suppresses normal token returns
  while conditional compilation is skipping source.
- Name token type `4` looks up hashed defines through `PC_FindHashedDefine`.
- Retail `PC_ReadToken` inlines the `PC_ExpandDefineIntoSource` push sequence:
  it calls `PC_ExpandDefine`, checks first/last token pointers, links the last
  expanded token to the source token stack at offset `0x808`, and makes the
  first expanded token the new stack head.
- On normal success, retail copies the accepted token into the source last-token
  cache at source offset `0x820` with size `0x430`.

HLIL for the helper layer matches the checked-in source:

- `0x004AC030` unreads the cached last token by passing `source + 0x820` to
  `PC_UnreadSourceToken`.
- `0x004AC650` wraps `PC_ReadToken`, emits `couldn't find expected %s` on EOF,
  compares strings, and emits `expected %s, found %s` on mismatch.
- `0x004AC710` wraps `PC_ReadToken`, maps expected token types to user-facing
  strings, checks number subtype bits, checks exact punctuation subtype, and
  emits the same diagnostics as the source.
- `0x004ACA30` is the compact `PC_ExpectAnyToken` wrapper.
- `0x004ACA70` is `PC_CheckTokenString`, which reads through `PC_ReadToken`,
  returns success on string match, otherwise unreads the lookahead token.
- `0x004ACB10` remains the public handle wrapper above this slice and calls
  `PC_ReadToken`.

## Source Reconstruction Notes

The checked-in source preserves GPL-era helper bodies that are useful for
readability and future reconstruction, even when retail optimization does not
leave standalone promoted retail bodies for all of them:

- `PC_ExpandDefineIntoSource` exists at `0x004A9B70`, but the retail
  `PC_ReadToken` body embeds the same expand-then-link logic instead of calling
  that wrapper.
- `PC_UnreadToken` has one source caller inside `PC_ReadToken`; retail HLIL shows
  the equivalent direct call to `PC_UnreadSourceToken`.
- `PC_CheckTokenType` and `PC_SkipUntilString` are declared and implemented in
  source, but they are unused in the current botlib C tree. No retail alias or
  Ghidra function-table row is present for them in `quakelive_steam.exe`.

These are source-reconstruction facts, not evidence that the retail binary has
separate emitted functions for every helper in the source file.

## Related Parser Wiring

The mapped helper layer is reached by multiple already-reconstructed parsers:

- `l_struct.c` uses `PC_ExpectAnyToken`, `PC_ExpectTokenType`,
  `PC_ExpectTokenString`, `PC_CheckTokenString`, and `PC_UnreadLastToken`.
- `be_ai_char.c` uses `PC_ReadToken`, `PC_ExpectTokenType`, and
  `PC_ExpectAnyToken` for character files.
- `be_ai_weight.c` uses `PC_ExpectAnyToken`, `PC_ExpectTokenType`,
  `PC_ExpectTokenString`, and `PC_CheckTokenString` for fuzzy-weight files.
- `be_ai_chat.c` uses the same helper family heavily for chat, synonyms, and
  random-string parsing.

Inference:

- The token-dispatch slice should be treated as the immediate common parser
  substrate for bot resource reconstruction. Future parser fixes should first
  determine whether behavior belongs in this layer, in the lower `l_script.c`
  token scanner, or in the consumer parser.

## Changes

- Added `tests/test_botlib_precompiler_token_parity.py`.
- The new test pins:
  - source prototypes and helper bodies
  - `PC_ReadToken` directive, string concatenation, skip, define expansion, and
    last-token cache shape
  - `PC_ExpandDefineIntoSource` push semantics and retail inlining evidence
  - expect/check/unread helper source shape
  - related parser usage in structure, character, weight, and chat code
  - retail Binary Ninja HLIL anchors
  - Ghidra function-table rows
  - absence of separate retail aliases for unused or inlined source helpers
- No C source body change was needed.
- Central queue files were intentionally left alone in this continuation to
  avoid colliding with the named concurrent sessions.

## Validation

Focused validation performed:

- `python -m pytest tests/test_botlib_precompiler_token_parity.py -q`

Observed result:

- `1 passed`

No game launch was performed. Static source, HLIL, Ghidra, and pytest coverage
answer this mapping question.

## Parity Estimate

- Focused precompiler token-dispatch slice: `70% -> 94%`. Before this round,
  aliases existed for several functions, but the source shape, retail inlining
  detail, optimized-away helper status, and consumer parser wiring were not
  captured together.
- Overall botlib parser/API wiring: approximately `69% -> 70%`.
- Strict-retail Windows replacement target: unchanged at `100%`.

## Next Candidate Slices

Good follow-on slices:

- `l_precomp.c` directive handlers around `#define`, `#include`, `#if`,
  `#elif`, `#else`, and `#endif`.
- `l_precomp.c` macro expansion internals around `PC_ExpandDefine` and
  parameter token handling.
- `l_script.c` primitive token scanning, especially number and punctuation
  behavior used by the resource parsers.
