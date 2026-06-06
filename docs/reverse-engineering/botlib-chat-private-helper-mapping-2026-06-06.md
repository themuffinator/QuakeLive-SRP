# Botlib Chat Private Helper Mapping - 2026-06-06

## Scope

This pass maps a private-helper tranche inside `src/code/botlib/be_ai_chat.c`
against the retail `quakelive_steam.exe` botlib image. The existing public chat
API and broad loader/matcher surfaces were already covered by the earlier chat
tail pass; this round closes the unpromoted helper owners behind console-message
heap setup, tilde removal, synonym expansion, and match-piece evaluation.

No C source rewrite is currently justified. The checked-in source already
matches the observed retail shape for this corridor, so the reconstruction work
is alias promotion plus focused parity coverage.

## Evidence Inputs

- Canonical binary: `assets/quakelive/quakelive_steam.exe`
- Binary Ninja HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part03.txt`
- Ghidra function rows:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- Source and wiring owners:
  `src/code/botlib/be_ai_chat.c`,
  `src/code/botlib/be_interface.c`,
  `src/code/game/botlib.h`,
  and `references/analysis/quakelive_symbol_aliases.json`

## Promoted Names

| Retail address | Promoted name | Evidence summary |
|---|---|---|
| `sub_497B00` | `InitConsoleMessageHeap` | Reads `max_messages`, allocates `0x114`-byte message records, links prev/next free-list pointers, and stores the free-list head. |
| `sub_497EB0` | `BotRemoveTildes` | Scans a mutable chat string for `~` and removes each occurrence with `memmove`. |
| `sub_498890` | `BotReplaceWeightedSynonyms` | Walks synonym lists by context, chooses a weighted replacement through retail `rand()/32767.0`, and replaces all other synonyms with the chosen entry. |
| `sub_498A70` | `BotReplaceReplySynonyms` | Walks reply text word-by-word, only replaces front-of-word reply synonyms, and avoids replacement recursion at the same position. |
| `sub_499880` | `StringsMatch` | Evaluates match-piece lists against `match->string`, records variable offsets/lengths, and accepts trailing variable captures or exact string exhaustion. |

The already-promoted public owners `BotFindMatch`, `BotConstructChatMessage`,
`BotReplyChat`, `BotSetupChatAI`, and `BotShutdownChatAI` were rechecked as the
callers that make these private helpers meaningful.

## Observed Retail Shape

Ghidra rows pin the new helper band:

- `FUN_00497b00,00497b00,208,0,unknown` -> `InitConsoleMessageHeap`
- `FUN_00497eb0,00497eb0,71,0,unknown` -> `BotRemoveTildes`
- `FUN_00498890,00498890,480,0,unknown` -> `BotReplaceWeightedSynonyms`
- `FUN_00498a70,00498a70,316,0,unknown` -> `BotReplaceReplySynonyms`
- `FUN_00499880,00499880,303,0,unknown` -> `StringsMatch`

Binary Ninja HLIL confirms:

- `sub_497B00` is called by `BotSetupChatAI` after synonyms, random strings,
  match templates, and optional reply chats are loaded.
- `sub_497EB0` is called by `BotReplyChat`, `BotEnterChat`, and
  `BotGetChatMessage`.
- `sub_498890` is called by `BotConstructChatMessage` after message expansion,
  matching source-side weighted synonym replacement in message context.
- `sub_498A70` is called from the reply-variable expansion path before final
  weighted replacement.
- `sub_499880` is called by `BotReplyChat` while scoring reply-chat match keys,
  and `BotFindMatch` also routes match templates through the same source helper.

## Source Reconstruction Notes

- `InitConsoleMessageHeap` keeps the retail fixed-size heap model and links the
  first, interior, and final message records explicitly. There is no evidence
  for replacing this with a dynamic allocation list.
- `BotRemoveTildes` remains a destructive in-place scrubber used immediately
  before chat text is sent or copied out.
- `BotReplaceWeightedSynonyms` calls the source-visible `StringReplaceWords`
  helper. Inference: retail folds that replacement body into the weighted
  synonym owner, so `StringReplaceWords` is not promoted as a separate alias.
- `BotReplaceReplySynonyms` is intentionally stricter than the generic synonym
  path: it only handles synonyms at the current word front and skips when the
  canonical replacement is already there.
- `StringsMatch` keeps the match-variable offset/length layout used by
  `BotMatchVariable`.
- `BotChatStateFromHandle`, `AllocConsoleMessage`, and `FreeConsoleMessage`
  remain source-visible but unpromoted. Inference: the retail helper bodies are
  folded into public chat functions or otherwise absent as standalone rows in
  this optimized retail build.

## Validation

Added `tests/test_botlib_chat_private_helper_parity.py` to pin:

1. The five new aliases, Ghidra function sizes, HLIL helper headers, and caller
   call sites.
2. Source shape for console-message heap initialization, tilde removal,
   weighted synonym replacement, reply synonym replacement, and match-piece
   evaluation.
3. Integration back into `BotSetupChatAI`, `BotShutdownChatAI`,
   `BotFindMatch`, `BotExpandChatMessage`, `BotReplyChat`, `BotEnterChat`, and
   `BotGetChatMessage`.
4. The private/public boundary: these helpers remain out of `ai_export_t`, while
   the public chat APIs stay exported through `Init_AI_Export`.

Focused validation:

```text
python -m pytest tests/test_botlib_chat_private_helper_parity.py -q
```

Observed result:

```text
3 passed in 0.13s
```

## Confidence

High for static helper ownership and source shape. Remaining uncertainty is
limited to live chat-data behavior across retail `syn.c`, `rnd.c`, `match.c`,
`rchat.c`, and per-bot initial chat files, not the private helper ownership or
public export boundary covered by this pass.

## Parity Estimate

- Focused chat private-helper corridor: approximately `82% -> 96%`.
- Overall botlib chat mapping plus public chat export/import wiring:
  approximately `90% -> 91%`.
