# Botlib Precompiler Directive Mapping - 2026-06-05

## Scope

This pass selects the `src/code/botlib/l_precomp.c` precompiler directive layer
as the next botlib slice after the source-handle and token-dispatch passes.
The slice covers:

- `PC_Directive_include`
- `PC_ReadLine`
- `PC_Directive_undef`
- `PC_Directive_define`
- `PC_DefineFromString`
- global define copy/free/apply helpers
- `#ifdef`, `#ifndef`, `#if`, `#elif`, `#else`, and `#endif`
- unsupported/simple directives: `#line`, `#error`, and `#pragma`
- `#eval` and `#evalfloat`
- `PC_ReadDirective`
- `$evalint`, `$evalfloat`, and `PC_ReadDollarDirective`
- related botlib/qagame wiring for `PC_AddGlobalDefine`

No runtime launch was needed. Static source, Binary Ninja HLIL, Ghidra function
rows, and focused pytest coverage answer this mapping question.

## Owning Retail Binary

Owning binary:

- `assets/quakelive/quakelive_steam.exe`

Reference corpus used:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/analysis/quakelive_symbol_aliases.json`
- `src/code/botlib/l_precomp.c`
- `src/code/botlib/l_precomp.h`
- `src/code/botlib/be_interface.c`
- `src/code/game/botlib.h`
- `src/code/game/g_public.h`
- `src/code/game/g_syscalls.c`
- `src/code/server/sv_game.c`
- `src/code/server/ql_game_imports.inc`

## Why This Slice

The previous token-dispatch pass stopped at `PC_ReadDirective` and
`PC_ReadDollarDirective` calls. This pass maps the directive bodies behind those
dispatchers. It is the next useful reconstruction boundary because it explains
how all source-level bot resources see includes, macros, conditional
compilation, global defines, and evaluated numeric pseudo-tokens.

The slice also matters for related wiring because `PC_AddGlobalDefine` is the
only precompiler directive-adjacent function exported directly through botlib
and qagame import surfaces.

## Retail Layout

The retail binary does not emit these functions in source-file order. Observed
layout:

- `0x004A9BD0`: `PC_ConvertPath`
- `0x004A9C50`: `PC_Directive_include`
- `0x004A9EA0`: `PC_ReadLine`
- `0x004A9F20`: `PC_Directive_undef`
- `0x004AA070`: `PC_RemoveAllGlobalDefines`
- `0x004AA0F0`: `PC_CopyDefine`
- `0x004AA250`: `PC_AddGlobalDefinesToSource`
- `0x004AA2E0`: `PC_Directive_if_def`
- `0x004AA3E0`: `PC_Directive_ifdef`
- `0x004AA400`: `PC_Directive_ifndef`
- `0x004AA420`: `PC_Directive_else`
- `0x004AA4E0`: `PC_Directive_endif`
- `0x004AB160`: `PC_Evaluate`
- `0x004AB450`: `PC_DollarEvaluate`
- `0x004AB780`: `PC_Directive_elif`
- `0x004AB810`: `PC_Directive_if`
- `0x004AB880`: `PC_Directive_line`
- `0x004AB8A0`: `PC_Directive_error`
- `0x004AB900`: `PC_Directive_pragma`
- `0x004AB9F0`: `UnreadSignToken`
- `0x004ABA70`: `PC_Directive_eval`
- `0x004ABB40`: `PC_Directive_evalfloat`
- `0x004ABC10`: `PC_ReadDirective`
- `0x004ABD20`: `PC_DollarDirective_evalint`
- `0x004ABE00`: `PC_DollarDirective_evalfloat`
- `0x004ABF10`: `PC_ReadDollarDirective`
- `0x004ACBC0`: `PC_Directive_define`
- `0x004AD0E0`: `PC_DefineFromString`
- `0x004AD200`: `PC_AddGlobalDefine`

The late placement of `PC_Directive_define` is an observed retail layout fact,
not a reason to move the source body.

## Retail Evidence

Alias-map promotions cover every selected retail body listed above. Ghidra
`functions.csv` corroborates the main bodies and sizes:

- `FUN_004a9c50,004a9c50,587,0,unknown`
- `FUN_004a9ea0,004a9ea0,115,0,unknown`
- `FUN_004a9f20,004a9f20,335,0,unknown`
- `FUN_004aa070,004aa070,117,0,unknown`
- `FUN_004aa0f0,004aa0f0,340,0,unknown`
- `FUN_004aa250,004aa250,130,0,unknown`
- `FUN_004aa2e0,004aa2e0,249,0,unknown`
- `FUN_004aa420,004aa420,179,0,unknown`
- `FUN_004aa4e0,004aa4e0,90,0,unknown`
- `FUN_004ab780,004ab780,137,0,unknown`
- `FUN_004ab810,004ab810,101,0,unknown`
- `FUN_004ab900,004ab900,239,0,unknown`
- `FUN_004aba70,004aba70,199,0,unknown`
- `FUN_004abb40,004abb40,208,0,unknown`
- `FUN_004abc10,004abc10,271,0,unknown`
- `FUN_004acbc0,004acbc0,1312,0,unknown`
- `FUN_004ad0e0,004ad0e0,285,0,unknown`
- `FUN_004ad200,004ad200,42,0,unknown`

Binary Ninja HLIL confirms these behavior anchors:

- Include handling exits early when `source->skip` at offset `0x818` is active.
- String includes strip double quotes, convert path separators, try the raw
  path, then retry with `source->includepath` at offset `0x400`.
- Angle-bracket includes build a path from source tokens, unread when a line is
  crossed, warn on missing trailing `>`, reject empty paths, convert separators,
  and push loaded scripts through `PC_PushScript`.
- `PC_ReadLine` reads raw source tokens and unreads the first token crossing the
  current logical line unless a backslash continuation was consumed.
- `#undef` hashes through `PC_NameHash`, walks the source define hash at offset
  `0x810`, warns for `DEFINE_FIXED`, and frees removable defines.
- Global define cleanup walks `data_16dd7e0`, freeing token chains at offsets
  `0x10` and `0x14`.
- Global define copy duplicates both replacement tokens and parameter tokens,
  each with token link offset `0x428`.
- `PC_AddGlobalDefinesToSource` copies global defines and inserts each clone
  into the source define hash.
- Conditional directives use the indent stack at offset `0x814`, source skip
  count at `0x818`, and script stack at `0x804`.
- `#ifdef` and `#ifndef` are compact wrappers around `PC_Directive_if_def` with
  retail type constants `8` and `0x10`.
- `#else`, `#endif`, and `#elif` pop or replace the active indent node and
  preserve the same diagnostics as source.
- `#line` returns an unsupported-directive error; `#error` reads one token and
  errors with that token; `#pragma` warns and drains the logical line.
- `#eval` and `#evalfloat` call `PC_Evaluate`, synthesize numeric tokens, unread
  the synthesized token, and push a separate sign token for negative values.
- `PC_ReadDirective` reads the directive name, rejects missing or cross-line
  names, scans the directive table at `data_5645f0`, and calls the matching
  handler.
- `PC_Directive_define` validates same-line names, rejects fixed redefinitions,
  warns and undefines mutable redefinitions, captures parameter lists, clears
  token whitespace fields, rejects duplicate parameters, blocks recursive
  self-reference, and rejects `##` at the beginning or end of the replacement
  list.
- `PC_DefineFromString` loads a `*extern` memory script, calls the late
  `PC_Directive_define` body, extracts the first resulting define from the hash
  table, and frees temporary script/source state.
- `PC_AddGlobalDefine` wraps `PC_DefineFromString` and pushes the resulting
  define onto `globaldefines`.

## Source Reconstruction Notes

Observed facts:

- `l_precomp.c` source shape matches the retail semantics above.
- `PC_Directive_define` source placement does not match retail address order,
  but the late retail body at `0x004ACBC0` is the same logical source function.
- `PC_AddDefine` remains a source helper around `PC_DefineFromString`; this pass
  does not assert a separate retail-public body for it.
- `PC_RemoveGlobalDefine` exists in source, but the retail/wiring evidence for
  this pass centers on `PC_RemoveAllGlobalDefines` and `PC_AddGlobalDefine`.

Inference:

- Future macro-expansion work should treat this slice as the directive-front-end
  boundary. The deeper expression engine (`PC_EvaluateTokens`) and macro
  expansion internals (`PC_ExpandDefine`) are adjacent but separate candidate
  slices.

## Related Wiring

The directive layer reaches external callers through global defines:

- `botlib_export_t` exposes `PC_AddGlobalDefine` immediately before source
  handle calls.
- `GetBotLibAPI` assigns `be_botlib_export.PC_AddGlobalDefine` before
  `PC_LoadSourceHandle`.
- `LoadSourceFile` and `LoadSourceMemory` both call
  `PC_AddGlobalDefinesToSource` before returning a source.
- Botlib shutdown calls `PC_RemoveAllGlobalDefines` after `LibVarDeAllocAll`
  and before `Log_Shutdown`.
- qagame legacy VM syscalls dispatch `BOTLIB_PC_ADD_GLOBAL_DEFINE` to
  `botlib_export->PC_AddGlobalDefine`.
- qagame native import wiring maps
  `G_QL_IMPORT_BOTLIB_PC_ADD_GLOBAL_DEFINE` to `QL_G_trap_BotLibDefine`.
- `ql_game_imports.inc` forwards the compatibility wrapper through
  `G_Import_Syscall(BOTLIB_PC_ADD_GLOBAL_DEFINE, string)`.

## Changes

- Added `tests/test_botlib_precompiler_directive_parity.py`.
- The new test pins:
  - source prototypes and directive helper bodies
  - include, undef, define, global-define, conditional, eval, and dispatch
    source shape
  - source creation and shutdown wiring for global defines
  - botlib export table and qagame import/syscall wiring for
    `PC_AddGlobalDefine`
  - alias-map promotions
  - Ghidra function rows
  - Binary Ninja HLIL behavior anchors
- No C source body change was needed.
- Central queue files were intentionally left alone to avoid colliding with
  concurrent sessions.

## Validation

Validation performed:

- `python -m pytest tests/test_botlib_precompiler_directive_parity.py -q`
- `python -m pytest tests/test_botlib_precompiler_token_parity.py -q`
- `python -m pytest tests/test_botlib_internal_parity.py -q`
- `python -m pytest tests/test_bot_resource_loading.py -q`
- `python -m pytest tests/test_game_native_export_helper_parity.py -q`

Observed results:

- `1 passed`
- token-dispatch adjacency: `1 passed`
- full botlib internal parity file: `31 passed`
- bot resource loading: `3 passed`
- native export/import helper parity: `11 passed`

No game launch was performed.

## Parity Estimate

- Focused precompiler directive slice: `64% -> 92%`. Before this round, the
  symbols were mostly promoted, but source body shape, retail non-contiguous
  layout, directive table dispatch, global define lifecycle, and qagame wiring
  were not captured together.
- Overall botlib parser/API wiring: approximately `70% -> 71%`.
- Strict-retail Windows replacement target: unchanged at `100%`.

## Next Candidate Slices

Good follow-on slices:

- `PC_ExpandDefine`, `PC_ReadDefineParms`, `PC_StringizeTokens`, and
  `PC_MergeTokens`.
- `PC_EvaluateTokens`, including operator precedence, ternary handling, and
  integer versus floating-point restrictions.
- Lower `l_script.c` token scanning, especially number and punctuation behavior
  shared by bot resource parsers.
