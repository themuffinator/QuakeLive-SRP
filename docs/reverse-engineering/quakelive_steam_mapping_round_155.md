# quakelive_steam.exe Mapping Round 155

Date: 2026-04-27

Scope: source-backed botlib mapping for the retained `be_ai_chat.c` match and
chat-integrity lane, plus a small companion STL pass for the retail ZMQ RCON
peer tree helpers that still sit underneath the already mapped
`idZMQ_*RconPeer` entry points. This pass stayed mapping-only.

## Summary

This round resolved `12` additional `quakelive_steam.exe` rows. Classification
mix:

- `10` engine-owned functions
- `0` platform-service-owned functions
- `2` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main outcome is that the old `0x498020` through `0x49A080` anonymous bot
chat slab now reads as real `be_ai_chat.c` ownership instead of mixed parser
glue. In the same pass, the retail ZMQ RCON peer map now has its previously
anonymous lower-bound and rebalance helpers named, which makes the binary-only
tree-backed implementation read cleanly alongside the checked-in higher-level
`idZMQ_FindRconPeer`, `idZMQ_InsertRconPeer`, `idZMQ_EraseRconPeer`, and
`idZMQ_ClearRconPeers` entry points.

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_4F4410` | `546` | support-library | `std_tree_insert_zmq_rcon_peer_node_rebalance` | High | Closed from the exact red-black-tree insert fixup flow directly underneath `idZMQ_InsertRconPeer`, including the standard parent/uncle recolor path and both rotation cases. |
| 2 | `sub_4999C0` | `541` | engine | `BotFindMatch` | High | Closed from the exact `match->string` copy, trailing `'\n'` trim loop, context mask gate, variable-offset reset, and `StringsMatch` walk across `matchtemplates`. |
| 3 | `sub_499C60` | `507` | engine | `BotCheckInitialChatIntegrety` | High | Closed from the exact `bot_chat_t -> bot_chattype_t -> bot_chatmessage_t` traversal and the inlined missing-random scan/free-list cleanup path. |
| 4 | `sub_499E70` | `504` | engine | `BotCheckReplyChatIntegrety` | High | Closed from the identical integrity walk over `bot_replychat_t -> firstchatmessage`, again with the inlined random-keyword verification and duplicate suppression. |
| 5 | `sub_498020` | `222` | engine | `StringContains` | High | Closed from the exact length-difference bound, case-sensitive toggle, and `toupper` comparison path used by the chat-template and reply-key validators. |

## Evidence Notes

- `sub_498020` and `sub_498100` match `StringContains` and
  `StringContainsWord` exactly against
  [be_ai_chat.c](</E:/Repositories/QuakeLive-reverse/src/code/botlib/be_ai_chat.c:464>).
  The HLIL preserves the same case-sensitivity switch, `toupper` fallback, and
  word-boundary punctuation checks on `' '`, `'.'`, `','`, and `'!'`.
- `sub_4990D0`, `sub_499170`, `sub_499510`, `sub_4999C0`, and `sub_499BF0`
  are all one-to-one matches for `RandomString`, `BotFreeMatchPieces`,
  `BotFreeMatchTemplates`, `BotFindMatch`, and `BotMatchVariable` from
  [be_ai_chat.c](</E:/Repositories/QuakeLive-reverse/src/code/botlib/be_ai_chat.c:1048>).
  The control flow and data layout match directly with no ambiguity.
- `sub_499C60` and `sub_499E70` do not correspond to the standalone
  `BotCheckChatMessageIntegrety` helper. Instead, they are the outer
  `BotCheckInitialChatIntegrety` and `BotCheckReplyChatIntegrety` walkers from
  [be_ai_chat.c](</E:/Repositories/QuakeLive-reverse/src/code/botlib/be_ai_chat.c:1584>),
  with both `BotCheckChatMessageIntegrety` and `BotFindStringInList` compiled
  inline. The preserved offsets line up cleanly with `bot_chattype_t` /
  `bot_replychat_t` and `bot_chatmessage_t`.
- `sub_49A080` is exact `BotFreeReplyChat`. The HLIL frees key matchpieces,
  optional key strings, chat-message lists, and the reply-chat nodes in the
  same order as
  [be_ai_chat.c](</E:/Repositories/QuakeLive-reverse/src/code/botlib/be_ai_chat.c:1691>).
- `sub_4F41B0` and `sub_4F4410` are the missing retail tree helpers under the
  RCON peer lane. `sub_4F41B0` is the lower-bound walk used by
  `idZMQ_FindRconPeer`, and `sub_4F4410` is the exact red-black-tree
  rebalance helper used by `idZMQ_InsertRconPeer`. This is a useful retail
  divergence marker because the checked-in
  [sv_zmq.c](</E:/Repositories/QuakeLive-reverse/src/code/server/sv_zmq.c:416>)
  still expresses the same high-level behavior with a linked-list fallback
  rather than the retail tree container.

## Aliases Added

- `sub_498020` -> `StringContains`
- `sub_498100` -> `StringContainsWord`
- `sub_4990D0` -> `RandomString`
- `sub_499170` -> `BotFreeMatchPieces`
- `sub_499510` -> `BotFreeMatchTemplates`
- `sub_4999C0` -> `BotFindMatch`
- `sub_499BF0` -> `BotMatchVariable`
- `sub_499C60` -> `BotCheckInitialChatIntegrety`
- `sub_499E70` -> `BotCheckReplyChatIntegrety`
- `sub_49A080` -> `BotFreeReplyChat`
- `sub_4F41B0` -> `std_tree_lower_bound_zmq_rcon_peer_node`
- `sub_4F4410` -> `std_tree_insert_zmq_rcon_peer_node_rebalance`

## Verification

Static mapping validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- scoped duplicate-key scan for the `quakelive_steam` alias block passed with
  `0` duplicates
- recount after this pass: `1777` raw alias entries, `1706` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `31.171%` of `5473` functions
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
| 1 | `0x004940D0` | `FUN_004940d0` | `547` |
| 2 | `0x004FC240` | `FUN_004fc240` | `537` |
| 3 | `0x00466B90` | `FUN_00466b90` | `535` |
| 4 | `0x0051FF40` | `FUN_0051ff40` | `535` |
| 5 | `0x004FAF60` | `FUN_004faf60` | `534` |
| 6 | `0x00510410` | `FUN_00510410` | `533` |
| 7 | `0x00501ED0` | `FUN_00501ed0` | `529` |
| 8 | `0x00498BB0` | `FUN_00498bb0` | `526` |
| 9 | `0x00503630` | `FUN_00503630` | `526` |
| 10 | `0x004AC440` | `FUN_004ac440` | `521` |

The next pass can return to the still-large unresolved host leftover
`sub_4940D0`, keep pushing through the adjacent opaque host/botlib queue at
`sub_4FC240` and `sub_466B90`, or continue harvesting the bot parser/template
lane where the checked-in source remains one-to-one with the retail code.
