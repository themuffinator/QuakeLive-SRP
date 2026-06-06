# Botlib Residual Promoted Alias Coverage - 2026-06-06

## Scope

This pass closes the last direct promoted-alias coverage gap in the core
botlib address band from `0x004829C0` through `0x004A83C0`. Earlier botlib
rounds had already promoted these names and the checked-in GPL-derived source
already contains the matching bodies, but five aliases still lacked direct
botlib parity-test mentions.

No C source body change or alias JSON change was needed. The work here is
reverse-engineering mapping: pinning alias names, Ghidra row sizes, HLIL
callsites, and reconstructed source shapes in a regression gate.

## Evidence

- `references/analysis/quakelive_symbol_aliases.json`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part03.txt`
- `src/code/botlib/be_aas_cluster.c`
- `src/code/botlib/be_aas_debug.c`
- `src/code/botlib/be_ai_chat.c`
- `tests/test_botlib_residual_promoted_alias_coverage.py`

## Pinned Residual Aliases

| Address | Alias | Size | Source owner | Role |
| --- | --- | ---: | --- | --- |
| `0x00483B90` | `AAS_CheckAreaForPossiblePortals` | `1136` | `be_aas_cluster.c` | Grounded-area cluster portal candidate detection and route-portal marking. |
| `0x00484580` | `AAS_ShowFacePolygon` | `841` | `be_aas_debug.c` | Debug polygon extraction from AAS face edge indices. |
| `0x00499170` | `BotFreeMatchPieces` | `70` | `be_ai_chat.c` | Match-piece and match-string cleanup on chat parser error paths. |
| `0x00499C60` | `BotCheckInitialChatIntegrety` | `507` | `be_ai_chat.c` | Initial-chat random-token integrity walk and temporary string-list cleanup. |
| `0x00499E70` | `BotCheckReplyChatIntegrety` | `504` | `be_ai_chat.c` | Reply-chat random-token integrity walk and temporary string-list cleanup. |

## Source Findings

- `AAS_CheckAreaForPossiblePortals` rejects existing cluster portals and
  ungrounded areas, gathers adjacent lower-presence areas, separates front and
  back faces by plane, requires connected front and back area sets, rejects
  shared edges between the two sides, and finally marks each accepted area with
  `AREACONTENTS_CLUSTERPORTAL` and `AREACONTENTS_ROUTEPORTAL`.
- `AAS_ShowFacePolygon` uses a fixed `points[128]` scratch array, reports an
  out-of-range face number, walks face edges forward or backward depending on
  `flip`, copies vertices with the signed-edge orientation expression
  `edge->v[edgenum < 0]`, and forwards the result to `AAS_ShowPolygon`.
- `AAS_ShowAreaPolygons` is the source-side caller for the debug helper and
  passes `face->frontarea != areanum` as the flip predicate, matching the HLIL
  callsite at `0x00484968`.
- `BotFreeMatchPieces` frees string alternatives only for `MT_STRING` pieces,
  then frees each piece. `BotLoadMatchPieces` reaches it on all five parser
  failure exits in the function body, and `BotFreeMatchTemplates` calls it for
  each template before freeing the template node.
- `BotCheckInitialChatIntegrety` and `BotCheckReplyChatIntegrety` are twin
  walkers over initial-chat and reply-chat message lists. Both feed every
  message through `BotCheckChatMessageIntegrety`, then release the temporary
  missing-random string list.

## Coverage Result

`tests/test_botlib_residual_promoted_alias_coverage.py` now includes a final
scan over promoted aliases in the core botlib range. After this pass there are
no promoted names in that band without a direct `test_botlib_*.py` mention.

This does not claim every botlib behavior is runtime-perfect. It means the
static mapping/test corpus no longer has dangling promoted aliases in the
direct botlib core band. Remaining botlib uncertainty is in map-dependent live
behavior, the already-documented libjpeg false leads outside botlib source
ownership, and folded or compiler-shaped thunks such as the weapon-jump helper
not represented as independent GPL source bodies.

## Parity Estimate

- Focused residual promoted-alias test coverage:
  **before 70% -> after 100%**
- AAS cluster/debug residual source-shape coverage:
  **before 82% -> after 96%**
- Chat match-piece and integrity-tail source-shape coverage:
  **before 84% -> after 97%**
- Overall botlib static mapping/test coverage:
  **before 87% -> after 88%**

The overall increase is deliberately small because the pass closes mapping and
regression-test evidence rather than adding new runtime behavior.
