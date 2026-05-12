# quakelive_steam.exe Mapping Round 160

Date: 2026-04-27

Scope: `be_ai_chat.c` parser, chat-file loader/cache, and chat-state lifecycle
recovery around the old `0x00498BB0` queue head. This pass stayed
mapping-only.

## Summary

This round resolved `14` additional `quakelive_steam.exe` rows.
Classification mix:

- `14` engine-owned functions
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main outcome is that the old anonymous `0x00498BB0` through `0x0049C5F0`
bot-chat slab now reads cleanly as the retained `be_ai_chat.c` parser and
public chat-state API: chat-message token loading, per-character chat-file
retention and reuse, initial-chat selection/counting, and the public
chat-state lifetime helpers. The useful subsystem result is that the
high-level bot chat ownership around the already-mapped
`BotLoadReplyChat` / `BotLoadInitialChat` / `BotConstructChatMessage` /
`BotInitialChat` / `BotReplyChat` lane is now much more explicit instead of
alternating between named public entry points and anonymous loader/state glue.

One important accounting detail is that `sub_49C440 -> BotAllocChatState` is a
stable HLIL-backed recovery, but it does not appear as a separate committed
Ghidra `functions.csv` row. Raw alias coverage therefore moved by `14`, while
strict Ghidra address-backed coverage moved by `13`.

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_498BB0` | `526` | engine-owned | `BotLoadChatMessage` | High | Closed from the exact `TT_STRING` / `TT_NUMBER` / `TT_NAME` token split, `chat message too long`, `unknown message component %s`, and `%cv%ld%c` / `%cr%s%c` escape-string builders. |
| 2 | `sub_49AF40` | `97` | engine-owned | `BotFreeChatFile` | High | Closed from the exact chat-state lookup, `cs->chat` free, and null reset at offset `0x138`. |
| 3 | `sub_49AFB0` | `437` | engine-owned | `BotLoadChatFile` | High | Closed from the exact `bot_reloadcharacters` gate, retained `ichatdata` reuse scan, fatal `ichatdata table full` / `couldn't load chat` strings, and `BotLoadInitialChat` tail. |
| 4 | `sub_49B4D0` | `307` | engine-owned | `BotChooseInitialChatMessage` | High | Closed from the exact chat-type name match, `m->time > AAS_Time()` recent-message filter, fallback oldest-message path, and random available-message selection. |
| 5 | `sub_49B610` | `176` | engine-owned | `BotNumInitialChats` | High | Closed from the exact type scan, optional `bot_testichat` logging, and `t->numchatmessages` return. |
| 6 | `sub_49C1B0` | `91` | engine-owned | `BotChatLength` | High | Closed from the exact chat-state validation and `strlen(cs->chatmessage)` return. |
| 7 | `sub_49C210` | `229` | engine-owned | `BotEnterChat` | High | Closed from the exact `bot_testichat` print path, `say_team %s` / `tell %d %s` / `say %s` command fan-out, and final message clear. |
| 8 | `sub_49C300` | `109` | engine-owned | `BotGetChatMessage` | High | Closed from the exact `BotRemoveTildes`, `strncpy(buf, cs->chatmessage, size - 1)`, terminator write, and clear tail. |
| 9 | `sub_49C370` | `96` | engine-owned | `BotSetChatGender` | High | Closed from the exact `CHAT_GENDERFEMALE` / `CHAT_GENDERMALE` / default `CHAT_GENDERLESS` switch. |
| 10 | `sub_49C3D0` | `109` | engine-owned | `BotSetChatName` | High | Closed from the exact `client` write, `Com_Memset(name, 0, 0x20)`, bounded `strncpy`, and forced terminator. |
| 11 | `sub_49C440` | `64` | engine-owned | `BotAllocChatState` | High | Closed from the exact `1..MAX_CLIENTS` free-slot scan, `GetClearedMemory(sizeof(bot_chatstate_t))`, and handle return. Promoted as HLIL-only because the start is absent from committed `functions.csv`. |
| 12 | `sub_49C480` | `213` | engine-owned | `BotFreeChatState` | High | Closed from the exact handle validation strings, optional `BotFreeChatFile` under `bot_reloadcharacters`, console-message drain loop, and final state free/null reset. |
| 13 | `sub_49C560` | `144` | engine-owned | `BotSetupChatAI` | High | Closed from the exact `synfile` / `rndfile` / `matchfile` / `rchatfile` loads, `nochat` gate, and `InitConsoleMessageHeap` tail. |
| 14 | `sub_49C5F0` | `196` | engine-owned | `BotShutdownChatAI` | High | Closed from the exact remaining chat-state walk, cached `ichatdata` release loop, console heap free, and `matchtemplates` / `randomstrings` / `synonyms` / `replychats` teardown. |

## Evidence Notes

- The recovered tranche maps directly onto the checked-in
  [be_ai_chat.c](</E:/Repositories/QuakeLive-reverse/src/code/botlib/be_ai_chat.c:862>)
  loader and chat-state lane:
  [BotLoadChatMessage](</E:/Repositories/QuakeLive-reverse/src/code/botlib/be_ai_chat.c:862>),
  [BotFreeChatFile](</E:/Repositories/QuakeLive-reverse/src/code/botlib/be_ai_chat.c:2185>),
  [BotLoadChatFile](</E:/Repositories/QuakeLive-reverse/src/code/botlib/be_ai_chat.c:2200>),
  [BotChooseInitialChatMessage](</E:/Repositories/QuakeLive-reverse/src/code/botlib/be_ai_chat.c:2407>),
  [BotNumInitialChats](</E:/Repositories/QuakeLive-reverse/src/code/botlib/be_ai_chat.c:2465>),
  [BotChatLength](</E:/Repositories/QuakeLive-reverse/src/code/botlib/be_ai_chat.c:2771>),
  [BotEnterChat](</E:/Repositories/QuakeLive-reverse/src/code/botlib/be_ai_chat.c:2785>),
  [BotGetChatMessage](</E:/Repositories/QuakeLive-reverse/src/code/botlib/be_ai_chat.c:2821>),
  [BotSetChatGender](</E:/Repositories/QuakeLive-reverse/src/code/botlib/be_ai_chat.c:2840>),
  [BotSetChatName](</E:/Repositories/QuakeLive-reverse/src/code/botlib/be_ai_chat.c:2859>),
  [BotAllocChatState](</E:/Repositories/QuakeLive-reverse/src/code/botlib/be_ai_chat.c:2895>),
  [BotFreeChatState](</E:/Repositories/QuakeLive-reverse/src/code/botlib/be_ai_chat.c:2915>),
  [BotSetupChatAI](</E:/Repositories/QuakeLive-reverse/src/code/botlib/be_ai_chat.c:2951>),
  and [BotShutdownChatAI](</E:/Repositories/QuakeLive-reverse/src/code/botlib/be_ai_chat.c:2985>).
- `sub_49AFB0` is the key ownership anchor for this pass. The body first frees
  any existing chat file, probes `bot_reloadcharacters`, scans the retained
  `ichatdata` cache for matching `(chatfile, chatname)` pairs, emits the exact
  fatal strings on table exhaustion or load failure, and otherwise installs the
  `BotLoadInitialChat` result back into the state and cache.
- `sub_49B4D0` and `sub_49B610` close the previously anonymous initial-chat
  public API immediately above the already-mapped `BotInitialChat` entry.
  Their HLIL matches the checked-in source exactly enough that the type scan,
  recent-message filter, and optional `bot_testichat` logging are stable.
- I intentionally did not promote a separate `BotExpandChatMessage` alias in
  this pass. The retail build keeps the expansion behavior merged into the
  already-mapped `BotConstructChatMessage` lane rather than exposing a clean
  standalone public helper at a separate committed address.
- I also left `BotResetChatAI` unmapped in this tranche. The surrounding
  lifecycle helpers were straightforward, but I did not yet isolate a stable
  standalone retail start for the reply-chat time-reset loop from the current
  evidence scan.

## Aliases Added

- `sub_498BB0` -> `BotLoadChatMessage`
- `sub_49AF40` -> `BotFreeChatFile`
- `sub_49AFB0` -> `BotLoadChatFile`
- `sub_49B4D0` -> `BotChooseInitialChatMessage`
- `sub_49B610` -> `BotNumInitialChats`
- `sub_49C1B0` -> `BotChatLength`
- `sub_49C210` -> `BotEnterChat`
- `sub_49C300` -> `BotGetChatMessage`
- `sub_49C370` -> `BotSetChatGender`
- `sub_49C3D0` -> `BotSetChatName`
- `sub_49C440` -> `BotAllocChatState`
- `sub_49C480` -> `BotFreeChatState`
- `sub_49C560` -> `BotSetupChatAI`
- `sub_49C5F0` -> `BotShutdownChatAI`

## Verification

Static mapping validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- scoped duplicate-key scan for the `quakelive_steam` alias block passed with
  `0` duplicates
- recount after this pass: `1834` raw alias entries, `1762` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `32.194%` of `5473` functions
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
| 3 | `0x004AC440` | `FUN_004ac440` | `521` |
| 4 | `0x00511670` | `FUN_00511670` | `520` |
| 5 | `0x00523B40` | `FUN_00523b40` | `520` |
| 6 | `0x00524370` | `FUN_00524370` | `520` |
| 7 | `0x00524580` | `FUN_00524580` | `520` |
| 8 | `0x00417790` | `FUN_00417790` | `518` |
| 9 | `0x0041AD70` | `FUN_0041ad70` | `517` |
| 10 | `0x00512340` | `FUN_00512340` | `517` |

The next pass can return to the still-transformed `vorbisfile.c` search helper
at `sub_4FC240`, the opaque `sub_4FAF60` file-wrapper slab, or keep advancing
through the remaining engine-owned host leftovers now that the bot chat loader
and chat-state API are much less anonymous.
