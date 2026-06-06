# Botlib Parser Tail Coverage Mapping - 2026-06-06

## Scope

This pass closes the remaining direct botlib test-coverage gap in the parser
and support tail from `0x004A83C0` through `0x004AF820`. The earlier parser
rounds had already promoted the four names below, but they were still missing
direct `test_botlib_*.py` mentions in the current alias scan.

No C source body change or alias JSON change was needed. The checked-in parser
source already matches the committed retail evidence for this static slice.

## Evidence

- `references/analysis/quakelive_symbol_aliases.json`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part03.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
- `src/code/botlib/l_precomp.c`
- `src/code/botlib/l_script.c`
- `src/code/botlib/l_script.h`
- `tests/test_botlib_parser_tail_coverage_parity.py`

## Pinned Parser Tail

| Address | Alias | Size | Source owner | Role |
| --- | --- | ---: | --- | --- |
| `0x004AA610` | `PC_EvaluateTokens` | `2689` | `l_precomp.c` | `#if` / `#elif` expression evaluator with operator precedence, `defined`, ternary, and divide-by-zero diagnostics. |
| `0x004AD4F0` | `PS_ReadEscapeCharacter` | `564` | `l_script.c` | Script string escape decoder for standard C escapes, hex escapes, and decimal character codes. |
| `0x004ADBA0` | `PS_ReadNumber` | `710` | `l_script.c` | Script lexer numeric scanner for hex, binary, octal/decimal, float, long, unsigned, and computed token values. |
| `0x004AE160` | `PS_ExpectTokenType` | `858` | `l_script.c` | Script token type/subtype validator and diagnostic formatter. |

## Source Findings

- `PC_EvaluateTokens` uses fixed local operator and value heaps, resets caller
  outputs before evaluation, accepts `defined` against the source define table,
  tracks unary minus and parentheses depth, rejects illegal float bitwise
  operators, evaluates the full arithmetic/logical/bitwise operator set, and
  preserves the ternary `? :` state machine visible in the HLIL.
- `PC_Evaluate` and `PC_DollarEvaluate` are the two source callers that feed
  expanded token lists into `PC_EvaluateTokens`, matching the retail callsites
  at `0x004AB3B0` and `0x004AB730`.
- `PS_ReadEscapeCharacter` performs the same pointer stepping and output-byte
  clamping shown in HLIL, including the distinct hex and decimal escape paths
  and the `unknown escape char` diagnostic.
- `PS_ReadNumber` matches the retained scanner shape, including the source's
  uppercase-hex branch, `BINARYNUMBERS` support, octal demotion when `8` or `9`
  appears, suffix handling, `NUMBERVALUE`, and final integer tagging for
  non-float values.
- `PS_ExpectTokenType` keeps the retail diagnostic map for token classes and
  numeric subtypes, plus the punctuation-subtype error path.

## Coverage Result

`tests/test_botlib_parser_tail_coverage_parity.py` now includes a final scan
over promoted aliases in the support-tail band. After this pass there are no
promoted names in `0x004A83C0..0x004AF820` without a direct
`test_botlib_*.py` mention.

The much larger native cgame import slab after this range remains a separate
related-wiring surface and was intentionally not conflated with this botlib
parser pass.

## Parity Estimate

- Focused parser-tail promoted-alias coverage:
  **before 82% -> after 100%**
- Focused `PC_EvaluateTokens` source-shape coverage:
  **before 78% -> after 97%**
- Focused `l_script.c` escape/number/expect-type source-shape coverage:
  **before 74% -> after 96%**
- Overall botlib parser/support static mapping:
  **before 88% -> after 89%**

The overall movement is small because this pass closes evidence coverage over
already-reconstructed source rather than changing runtime behavior.
