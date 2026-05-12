# quakelive_steam.exe Mapping Round 165

Date: 2026-04-27

Scope: retained ZeroMQ `xpub.cpp` / `xsub.cpp` socket-method recovery plus the
adjacent CZMQ `zsock.c` / `zfile.c` helper lane around the old queue heads
`0x00417790`, `0x004F5200`, and `0x004FAF60`. This pass stayed mapping-only.

## Summary

This round resolved `26` additional `quakelive_steam.exe` rows.
Classification mix:

- `0` engine-owned functions
- `26` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The useful outcome is that the retained ZeroMQ host/runtime band is now much
less anonymous. The old XPUB/XSUB slab around `sub_417790` and `sub_418620`
now reads as real `xpub.cpp` / `xsub.cpp` ownership, while the adjacent CZMQ
socket helper lane resolves cleanly as `zsock_bind`, `zsock_unbind`,
`zsock_connect`, `zsock_attach`, and `zfile_new` instead of opaque endpoint
or path glue.

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_417790` | `518` | platform-service-owned | `zmq_xpub_t_xrecv` | High | Closed from the exact pending-subscription dequeue, `msg_->close`, `msg_->init_size`, payload copy, pending-flags replay, and pending-bitset pop. |
| 2 | `sub_4F5200` | `514` | platform-service-owned | `zsock_bind` | High | Closed from the exact `^tcp://.*:(\\d+)$` and `^(tcp://.*):([*!])(\\[(\\d+)?-(\\d+)?\\])?$` parse lane, explicit dynamic-port scan, and stored successful endpoint path from CZMQ `zsock.c`. |
| 3 | `sub_4FAF60` | `534` | platform-service-owned | `zfile_new` | High | Closed from the exact full-path build, `.ln` symbolic-link resolution, first-line target read, and post-link `zfile_restat` setup from CZMQ `zfile.c`. |
| 4 | `sub_418620` | `296` | platform-service-owned | `zmq_xsub_t_xsend` | High | Closed from the exact subscribe/unsubscribe gate, trie add/remove, duplicate-drop behavior, `dist.send_to_all`, and empty-message rewrite on filtered unsubs. |
| 5 | `sub_418750` | `426` | platform-service-owned | `zmq_xsub_t_xrecv` | High | Closed from the exact prefetched-message fast path, fair-queue receive loop, topic-match filter, and multipart discard path. |
| 6 | `sub_418900` | `384` | platform-service-owned | `zmq_xsub_t_xhas_in` | High | Closed from the exact prefetched-message check, nonblocking fair-queue probe, match filter, and multipart skip loop. |
| 7 | `sub_417700` | `125` | platform-service-owned | `zmq_xpub_t_xsend` | High | Closed from the exact first-part topic match, distributor send-to-matching path, multipart tracking, and unmatch-on-final-part behavior. |
| 8 | `sub_4170B0` | `127` | platform-service-owned | `zmq_xpub_t_xattach_pipe` | High | Closed from the exact `pipe_` assert, distributor attach, optional subscribe-to-all trie insert, and immediate `xread_activated` tailcall. |
| 9 | `sub_4184B0` | `189` | platform-service-owned | `zmq_xsub_t_xattach_pipe` | High | Closed from the exact `pipe_` assert, `fq.attach`, `dist.attach`, cached-subscription replay, and pipe flush. |
| 10 | `sub_4179B0` | `235` | platform-service-owned | `zmq_xpub_t_send_unsubscription` | High | Closed from the exact `options.type != ZMQ_PUB` gate, `size + 1` blob allocation, leading `0` unsubscribe byte, and pending-queue push. |
| 11 | `sub_418A80` | `192` | platform-service-owned | `zmq_xsub_t_send_subscription` | High | Closed from the exact `size + 1` message build, leading `1` subscribe byte, payload copy, and `pipe->write` send. |
| 12 | `sub_4F54B0` | `322` | platform-service-owned | `zsock_attach` | High | Closed from the exact comma-split endpoint parser, `'@'` bind dispatch, `'>'` connect dispatch, and `serverish` fallback rules. |
| 13 | `sub_4F5460` | `69` | platform-service-owned | `zsock_connect` | High | Closed from the exact formatted-endpoint expansion and `zmq_connect` wrapper path used by `zsock_attach`. |
| 14 | `sub_4F5410` | `69` | platform-service-owned | `zsock_unbind` | High | Closed from the exact formatted-endpoint expansion and `zmq_unbind` wrapper path, reinforced by the `zauth.c` cleanup callsite. |
| 15 | `sub_416E20` | `391` | platform-service-owned | `zmq_xpub_t_ctor` | High | Closed from the exact base `socket_base_t` construction, XPUB vtable install, `options.type = ZMQ_XPUB`, and pending-container initialization. |
| 16 | `sub_416FE0` | `195` | platform-service-owned | `zmq_xpub_t_dtor` | High | Closed from the exact XPUB vtable restore, pending-container teardown, distributor/trie cleanup, and base `socket_base_t` destruction. |
| 17 | `sub_4182B0` | `201` | platform-service-owned | `zmq_xsub_t_ctor` | High | Closed from the exact base `socket_base_t` construction, XSUB vtable install, `options.type = ZMQ_XSUB`, linger-zero setup, and message-state initialization. |
| 18 | `sub_4183B0` | `242` | platform-service-owned | `zmq_xsub_t_dtor` | High | Closed from the exact message close assertion, XSUB vtable restore, trie/distributor/fair-queue teardown, and base `socket_base_t` destruction. |
| 19 | `sub_417670` | `58` | platform-service-owned | `zmq_xpub_t_xsetsockopt` | High | Closed from the exact `ZMQ_XPUB_VERBOSE` option gate, `sizeof(int)` check, and stored boolean verbose flag. |
| 20 | `sub_417650` | `21` | platform-service-owned | `zmq_xpub_t_xwrite_activated` | High | Closed from the exact one-line distributor activation tailcall. |
| 21 | `sub_4176B0` | `77` | platform-service-owned | `zmq_xpub_t_xterminated` | High | Closed from the exact trie removal with `send_unsubscription` callback plus distributor termination. |
| 22 | `sub_4179A0` | `12` | platform-service-owned | `zmq_xpub_t_xhas_in` | High | Closed from the exact pending-subscription nonempty test. |
| 23 | `sub_416C10` | `21` | platform-service-owned | `zmq_xsub_t_xread_activated` | High | Closed from the exact fair-queue activation tailcall. |
| 24 | `sub_418570` | `21` | platform-service-owned | `zmq_xsub_t_xwrite_activated` | High | Closed from the exact distributor activation tailcall. |
| 25 | `sub_418590` | `40` | platform-service-owned | `zmq_xsub_t_xterminated` | High | Closed from the exact paired fair-queue and distributor termination calls. |
| 26 | `sub_4185C0` | `96` | platform-service-owned | `zmq_xsub_t_xhiccuped` | High | Closed from the exact cached-subscription replay and pipe flush used after hiccups. |

## Evidence Notes

- The XPUB and XSUB virtual-slot ownership is pinned by upstream
  [`socket_base.hpp`](https://github.com/zeromq/libzmq/blob/v3.2.5/src/socket_base.hpp),
  which fixes the retained method order as `xattach_pipe`, `xsetsockopt`,
  `xhas_out`, `xsend`, `xhas_in`, `xrecv`, `xread_activated`,
  `xwrite_activated`, `xhiccuped`, and `xterminated`.
- The concrete method bodies then line up with upstream
  [`xpub.cpp`](https://github.com/zeromq/libzmq/blob/v3.2.5/src/xpub.cpp),
  [`xpub.hpp`](https://github.com/zeromq/libzmq/blob/v3.2.5/src/xpub.hpp),
  [`xsub.cpp`](https://github.com/zeromq/libzmq/blob/v3.2.5/src/xsub.cpp),
  and [`xsub.hpp`](https://github.com/zeromq/libzmq/blob/v3.2.5/src/xsub.hpp):
  the retained `pipe_` assertions, `ZMQ_XPUB_VERBOSE` check, fair-queue /
  distributor helpers, trie callbacks, and message close/init error paths all
  match one-to-one.
- `sub_4F5200` is anchored by the exact CZMQ
  [`zsock_bind`](https://github.com/zeromq/czmq/blob/v2.2.0/src/zsock.c)
  regex pair and dynamic-port selection loop. The retained HLIL preserves both
  regular expressions and the retry scan over the selected port range.
- `sub_4F5410`, `sub_4F5460`, and `sub_4F54B0` are the adjacent
  [`zsock_unbind`](https://github.com/zeromq/czmq/blob/v2.2.0/src/zsock.c),
  [`zsock_connect`](https://github.com/zeromq/czmq/blob/v2.2.0/src/zsock.c),
  and [`zsock_attach`](https://github.com/zeromq/czmq/blob/v2.2.0/src/zsock.c)
  wrappers. `zsock_attach` is especially stable because the HLIL keeps the
  same `@` / `>` / `serverish` dispatch structure from source.
- `sub_4FAF60` is the exact CZMQ
  [`zfile_new`](https://github.com/zeromq/czmq/blob/v2.2.0/src/zfile.c)
  constructor. The `.ln` extension test, first-line symlink target read,
  newline trim, and chop-`".ln"` behavior are all preserved in the retail
  binary.
- I intentionally left the small compiler thunks and merged tiny bodies
  untouched in this pass:
  `sub_416FB0`, `sub_418380`, `sub_418280`, `sub_418290`, `sub_4182A0`,
  `sub_418B40`, `sub_418B50`, `sub_418B60`, and the already-aliased
  `sub_417780`. The source owners are understood, but those wrappers do not
  improve the queue as much as the concrete method bodies above.

## Aliases Added

- `sub_416C10` -> `zmq_xsub_t_xread_activated`
- `sub_416E20` -> `zmq_xpub_t_ctor`
- `sub_416FE0` -> `zmq_xpub_t_dtor`
- `sub_4170B0` -> `zmq_xpub_t_xattach_pipe`
- `sub_417650` -> `zmq_xpub_t_xwrite_activated`
- `sub_417670` -> `zmq_xpub_t_xsetsockopt`
- `sub_4176B0` -> `zmq_xpub_t_xterminated`
- `sub_417700` -> `zmq_xpub_t_xsend`
- `sub_417790` -> `zmq_xpub_t_xrecv`
- `sub_4179A0` -> `zmq_xpub_t_xhas_in`
- `sub_4179B0` -> `zmq_xpub_t_send_unsubscription`
- `sub_4182B0` -> `zmq_xsub_t_ctor`
- `sub_4183B0` -> `zmq_xsub_t_dtor`
- `sub_4184B0` -> `zmq_xsub_t_xattach_pipe`
- `sub_418570` -> `zmq_xsub_t_xwrite_activated`
- `sub_418590` -> `zmq_xsub_t_xterminated`
- `sub_4185C0` -> `zmq_xsub_t_xhiccuped`
- `sub_418620` -> `zmq_xsub_t_xsend`
- `sub_418750` -> `zmq_xsub_t_xrecv`
- `sub_418900` -> `zmq_xsub_t_xhas_in`
- `sub_418A80` -> `zmq_xsub_t_send_subscription`
- `sub_4F5200` -> `zsock_bind`
- `sub_4F5410` -> `zsock_unbind`
- `sub_4F5460` -> `zsock_connect`
- `sub_4F54B0` -> `zsock_attach`
- `sub_4FAF60` -> `zfile_new`

## Verification

Static mapping validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- scoped duplicate-key scan for the `quakelive_steam` alias block passed with
  `0` duplicates
- recount after this pass: `1900` raw alias entries, `1832` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `33.473%` of `5473` functions
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
| 3 | `0x00437710` | `FUN_00437710` | `513` |
| 4 | `0x00421830` | `FUN_00421830` | `512` |
| 5 | `0x0043F590` | `FUN_0043f590` | `507` |
| 6 | `0x004F7B70` | `FUN_004f7b70` | `506` |
| 7 | `0x004EE260` | `FUN_004ee260` | `505` |
| 8 | `0x00486D40` | `FUN_00486d40` | `504` |
| 9 | `0x004E6730` | `FUN_004e6730` | `504` |
| 10 | `0x0050C790` | `FUN_0050c790` | `503` |

The next pass can return to the still-transformed `vorbisfile.c` search helper
at `sub_4FC240`, pivot back into the unresolved engine/client leftovers around
`sub_41AD70` and `sub_437710`, or continue following the remaining CZMQ /
ZeroMQ host seam now that the `xpub`, `xsub`, `zsock`, and `zfile` slab is no
longer anonymous.
