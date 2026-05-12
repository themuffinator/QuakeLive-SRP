# quakelive_steam.exe Mapping Round 142

Date: 2026-04-27

Scope: refreshed largest-unaliased queue after round 141. This pass consumed
the queue-head libzmq `pipe.cpp` termination candidate at `sub_4109D0` and
promoted the contiguous `zmq::pipe_t` lifecycle lane from `sub_410070`
through `sub_410DF0`.

## Summary

This round mapped `18` `quakelive_steam.exe` functions from the refreshed
largest-unaliased queue and exact adjacent platform-service neighbors.
Classification mix:

- `0` engine-owned functions
- `18` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

No source debt was opened. This tranche is exact bundled libzmq support: the
retained `pipe.cpp` constructor, read/write, activation, termination, and
hiccup lane used by the already-mapped `zmq_pipepair` path and adjacent socket
runtime support.

This round also closes the previously bounded `sub_4109D0` ownership/name gap.
The local HLIL carries direct `..\..\..\src\pipe.cpp` assertions and enough
contiguous method behavior to promote the public `zmq::pipe_t` method names
without relying on speculative owner naming.

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_410070` | `195` | platform-service-owned | `zmq_pipe_t_ctor` | High | No engine debt; exact `zmq::pipe_t` constructor wiring the inbound/outbound pipes, peer-credit threshold, state fields, and conflate flag. |
| 2 | `sub_410170` | `89` | platform-service-owned | `zmq_pipe_t_dtor` | High | No engine debt; exact destructor restoring base vtables and releasing inline string storage. |
| 3 | `sub_4101D0` | `79` | platform-service-owned | `zmq_pipe_t_set_event_sink` | High | No engine debt; exact one-time sink registration guarded by the `!sink` assertion. |
| 4 | `sub_410250` | `212` | platform-service-owned | `zmq_pipe_t_check_read` | High | No engine debt; exact inbound-availability probe with delimiter detection and `process_delimiter` handoff. |
| 5 | `sub_410330` | `140` | platform-service-owned | `zmq_pipe_t_read` | High | No engine debt; exact inbound message pop with message-count accounting and delimiter fast path. |
| 6 | `sub_4103C0` | `58` | platform-service-owned | `zmq_pipe_t_check_write` | High | No engine debt; exact outbound-credit gate over the low-watermark accounting fields. |
| 7 | `sub_410400` | `116` | platform-service-owned | `zmq_pipe_t_write` | High | No engine debt; exact outbound message write path with multipart-aware credit tracking. |
| 8 | `sub_410480` | `358` | platform-service-owned | `zmq_pipe_t_rollback` | High | No engine debt; exact rollback helper that drains unfinished multipart messages from the outbound pipe. |
| 9 | `sub_4105F0` | `39` | platform-service-owned | `zmq_pipe_t_flush` | High | No engine debt; exact flush helper over the outbound ypipe plus peer activation notification. |
| 10 | `sub_410620` | `36` | platform-service-owned | `zmq_pipe_t_process_activate_read` | High | No engine debt; exact read-activation callback that flips `in_active` and notifies the sink. |
| 11 | `sub_410650` | `48` | platform-service-owned | `zmq_pipe_t_process_activate_write` | High | No engine debt; exact write-activation callback that restores peer credits and notifies the sink. |
| 12 | `sub_410680` | `484` | platform-service-owned | `zmq_pipe_t_process_hiccup` | High | No engine debt; exact hiccup-command handler that drains and replaces the outbound pipe, then reattaches the peer pipe. |
| 13 | `sub_410870` | `340` | platform-service-owned | `zmq_pipe_t_process_pipe_term` | High | No engine debt; exact termination-request handler over the active, delimiter-wait, and delayed-ack states. |
| 14 | `sub_4109D0` | `559` | platform-service-owned | `zmq_pipe_t_process_pipe_term_ack` | High | No engine debt; exact termination-ack handler that drains pending outbound frames, optionally returns a delayed ack, destroys the sink, and self-destructs. |
| 15 | `sub_410C00` | `253` | platform-service-owned | `zmq_pipe_t_terminate` | High | No engine debt; exact public `terminate(bool delay_)` entry handling active/waiting/ack states plus delimiter injection. |
| 16 | `sub_410D00` | `17` | platform-service-owned | `zmq_pipe_t_is_delimiter` | High | No engine debt; exact delimiter predicate over the retained `msg_t` delimiter marker. |
| 17 | `sub_410D20` | `207` | platform-service-owned | `zmq_pipe_t_process_delimiter` | High | No engine debt; exact delimiter handler transitioning active pipes to delimiter-wait or forwarding the final termination ack. |
| 18 | `sub_410DF0` | `251` | platform-service-owned | `zmq_pipe_t_hiccup` | High | No engine debt; exact public hiccup helper allocating a replacement inbound pipe and notifying the peer. |

## Evidence Notes

- The already-mapped `sub_40FD50 -> zmq_pipepair` path allocates the two
  ypipe/conflate instances, constructs a pair of `pipe_t` objects through
  `sub_410070`, then links the peer fields with the `!peer` assertion at
  `pipe.cpp:0x5d`. That local creation sequence makes `sub_410070` the exact
  `zmq::pipe_t` constructor anchor for the surrounding lane.
- `sub_410170` and `sub_4101D0` close the constructor-adjacent support pair.
  `sub_410170` reinstalls the `pipe_t` and inherited base vtables in teardown
  order before freeing inline string storage; `sub_4101D0` is pinned by the
  direct `!sink` assertion at `pipe.cpp:0x64`.
- `sub_410250`, `sub_410330`, `sub_4103C0`, `sub_410400`, `sub_410480`, and
  `sub_4105F0` form the exact read/write lane. The local HLIL shows the
  delimiter predicate dispatch through `sub_410D00`, the
  `msg.flags () & msg_t::more` assertion at `pipe.cpp:0xca`, and the same
  message-credit / low-watermark notification behavior expected from
  `pipe.cpp`.
- `sub_410620`, `sub_410650`, and `sub_410680` are the activation and hiccup
  callbacks. The `outpipe` and `pipe_` assertions at `pipe.cpp:0xf2` and
  `pipe.cpp:0xfe`, plus the outbound-pipe drain/replacement behavior, make the
  exact public names stable.
- `sub_410870`, `sub_4109D0`, `sub_410C00`, `sub_410D20`, and `sub_410DF0`
  close the termination lane exactly. `sub_4109D0` is anchored by the
  `sink` assertion at `pipe.cpp:0x133`, the
  `state == term_ack_sent || state ...` assertion at `pipe.cpp:0x13f`, the
  delayed-ack return path, and the final sink/self teardown. `sub_410D20`
  carries the `state == active || state == wait...` assertion at
  `pipe.cpp:0x1c1`, while `sub_410DF0` allocates a replacement inbound pipe
  before sending the peer hiccup command.
- These rows stay in the retained platform-service lane rather than opening
  engine/source debt. The repo already treats bundled libzmq support as part
  of the bounded `quakelive_steam.exe` host/runtime reconstruction surface.

## Aliases Added

- `sub_410070` -> `zmq_pipe_t_ctor`
- `sub_410170` -> `zmq_pipe_t_dtor`
- `sub_4101D0` -> `zmq_pipe_t_set_event_sink`
- `sub_410250` -> `zmq_pipe_t_check_read`
- `sub_410330` -> `zmq_pipe_t_read`
- `sub_4103C0` -> `zmq_pipe_t_check_write`
- `sub_410400` -> `zmq_pipe_t_write`
- `sub_410480` -> `zmq_pipe_t_rollback`
- `sub_4105F0` -> `zmq_pipe_t_flush`
- `sub_410620` -> `zmq_pipe_t_process_activate_read`
- `sub_410650` -> `zmq_pipe_t_process_activate_write`
- `sub_410680` -> `zmq_pipe_t_process_hiccup`
- `sub_410870` -> `zmq_pipe_t_process_pipe_term`
- `sub_4109D0` -> `zmq_pipe_t_process_pipe_term_ack`
- `sub_410C00` -> `zmq_pipe_t_terminate`
- `sub_410D00` -> `zmq_pipe_t_is_delimiter`
- `sub_410D20` -> `zmq_pipe_t_process_delimiter`
- `sub_410DF0` -> `zmq_pipe_t_hiccup`

## Verification

Alias artifact validation:

- `references/analysis/quakelive_symbol_aliases.json` parses through
  `python -m json.tool`
- duplicate-key scan passed after the alias update
- recount after this pass: `1634` raw alias entries, `1563` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `28.558%` of `5473` functions
- refreshed unresolved queue was recomputed against the committed Ghidra
  function-start corpus after the alias update
- no game/runtime launch was performed; this was a static mapping pass

Parity estimate after this mapping-only pass remains unchanged:

- strict-retail Windows replacement target: `100%` before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

After this round, the refreshed largest-unaliased queue begins with:

| # | Address | Ghidra name | Size |
| ---: | --- | --- | ---: |
| 1 | `0x00463980` | `FUN_00463980` | `592` |
| 2 | `0x00435070` | `FUN_00435070` | `566` |
| 3 | `0x00440AD0` | `FUN_00440ad0` | `560` |
| 4 | `0x004C6BD0` | `FUN_004c6bd0` | `558` |
| 5 | `0x0040B050` | `FUN_0040b050` | `555` |
| 6 | `0x00419AD0` | `FUN_00419ad0` | `555` |
| 7 | `0x0040F7E0` | `FUN_0040f7e0` | `549` |
| 8 | `0x0041CFB0` | `FUN_0041cfb0` | `549` |
| 9 | `0x0042BA60` | `FUN_0042ba60` | `549` |
| 10 | `0x004940D0` | `FUN_004940d0` | `547` |

The next pass should return to `sub_463980`, `sub_435070`, and `sub_440AD0`,
then keep working down the remaining top queue while preserving the existing
classification guardrails on unresolved engine, platform-service, and
support-library rows.
