# quakelive_steam.exe Mapping Round 197

Date: 2026-04-28

Scope: retained libzmq lifecycle recovery across the old queue head
`0x00409670` and the adjacent `own.cpp` / `socket_base.cpp` command handlers
from `0x00409630` through `0x0040F710`.

## Summary

This round resolved `17` additional `quakelive_steam.exe` rows.
Classification mix:

- `0` engine-owned functions
- `17` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The useful outcome is that the anonymous libzmq lifecycle seam around the old
queue head now reads as real retained `own.cpp` and `socket_base.cpp`
ownership instead of opaque host glue. The largest closure is
`sub_409670 -> zmq_socket_base_t_process_term`, and the surrounding pass also
lands the retained socket stop/bind/destroy/monitor helpers plus the full
`own_t` ownership-tree termination lane.

## Evidence Notes

- `sub_409670` is exact as `zmq_socket_base_t_process_term` because the HLIL
  matches retained `socket_base.cpp` line-for-line: unregister inproc
  endpoints, iterate `_pipes`, send disconnect messages, run the inlined
  `pipe_t::terminate(false)` state machine, register one termination ack per
  pipe, then tail into `own_t::process_term(linger_)`. The inlined
  `pipe.cpp` assertion string at line `0x18a` is the strongest ownership
  anchor here.
- `sub_409630`, `sub_409650`, `sub_409A60`, `sub_409CA0`, and `sub_409E20`
  are exact as `zmq_socket_base_t_process_stop`, `process_bind`,
  `check_destroy`, `extract_flags`, and `stop_monitor`. Their HLIL preserves
  the retained wrapper shapes exactly: `process_stop` calls the monitor
  teardown owner then sets `_ctx_terminated`; `process_bind` is the one-line
  `attach_pipe` wrapper; `check_destroy` removes the socket from the poller,
  destroys it from the context, sends the reaped notification, and then
  delegates to `own_t::process_destroy`; `extract_flags` validates
  `routing_id` against `options.recv_routing_id` and updates `_rcvmore`; and
  `stop_monitor` emits the optional `MONITOR_STOPPED` event before tearing down
  `_monitor_socket`.
- `sub_40F050` and `sub_40F150` are exact as `zmq_own_t_ctor` and
  `zmq_own_t_dtor`. The constructor copies `options`, zeroes the sent/processed
  sequence counters, clears `_owner`, initializes the owned-set sentinel, and
  zeroes `_term_acks`, while the destructor tears down the retained owned-set
  node storage and option state before restoring the `object_t` vtable.
- `sub_40F1E0`, `sub_40F200`, `sub_40F270`, `sub_40F320`, `sub_40F3C0`, and
  `sub_40F450` are exact as `zmq_own_t_process_seqnum`, `launch_child`,
  `process_term_req`, `process_own`, `terminate`, and `process_term`. The
  clearest anchors are the hidden-command-argument patterns preserved in HLIL:
  `launch_child` sets `_owner` then sends `plug` and `own`; `process_term_req`
  erases the child from `_owned`, increments `_term_acks`, and sends `term`
  with `options.linger`; `process_own` either inserts into `_owned` or sends
  immediate zero-linger termination when `_terminating`; `terminate` either
  self-terminates as a root or sends `term_req` to `_owner`; and
  `process_term` iterates the owned set, sends `term` to each child, folds the
  owned-set size into `_term_acks`, clears the set, marks `_terminating`, and
  calls `check_term_acks()`.
- `sub_40F600`, `sub_40F670`, and `sub_40F710` are exact as
  `zmq_own_t_unregister_term_ack`, `check_term_acks`, and `process_destroy`.
  The HLIL preserves the same retained assertions from `own.cpp` (`term_acks >
  0` and `owned.empty()`) plus the final owner `send_term_ack` / `delete this`
  handoff.
- I deliberately left `sub_409D10` deferred. It clearly belongs to the
  monitor-event publisher lane, but this round already closed the stable
  lifecycle owners without forcing a more version-sensitive monitor payload
  wrapper name.

## Aliases Added

- `sub_409630` -> `zmq_socket_base_t_process_stop`
- `sub_409650` -> `zmq_socket_base_t_process_bind`
- `sub_409670` -> `zmq_socket_base_t_process_term`
- `sub_409A60` -> `zmq_socket_base_t_check_destroy`
- `sub_409CA0` -> `zmq_socket_base_t_extract_flags`
- `sub_409E20` -> `zmq_socket_base_t_stop_monitor`
- `sub_40F050` -> `zmq_own_t_ctor`
- `sub_40F150` -> `zmq_own_t_dtor`
- `sub_40F1E0` -> `zmq_own_t_process_seqnum`
- `sub_40F200` -> `zmq_own_t_launch_child`
- `sub_40F270` -> `zmq_own_t_process_term_req`
- `sub_40F320` -> `zmq_own_t_process_own`
- `sub_40F3C0` -> `zmq_own_t_terminate`
- `sub_40F450` -> `zmq_own_t_process_term`
- `sub_40F600` -> `zmq_own_t_unregister_term_ack`
- `sub_40F670` -> `zmq_own_t_check_term_acks`
- `sub_40F710` -> `zmq_own_t_process_destroy`

## Verification

Static mapping validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- scoped duplicate-key scan for the `quakelive_steam` alias block passed with
  `0` duplicates
- recount after this pass: `2110` raw alias entries, `2038` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `37.237%` of `5473` functions
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
| 1 | `0x004E6730` | `FUN_004e6730` | `504` |
| 2 | `0x004B4100` | `FUN_004b4100` | `502` |
| 3 | `0x004B3672` | `FUN_004b3672` | `495` |
| 4 | `0x0046A420` | `FUN_0046a420` | `490` |
| 5 | `0x004DC730` | `FUN_004dc730` | `490` |
| 6 | `0x004C12F0` | `FUN_004c12f0` | `488` |
| 7 | `0x004368A0` | `FUN_004368a0` | `484` |
| 8 | `0x00429DD0` | `FUN_00429dd0` | `483` |
| 9 | `0x004A4280` | `FUN_004a4280` | `483` |
| 10 | `0x004B6630` | `FUN_004b6630` | `483` |

The next pass can return to the still-heavy engine/client leftovers at
`sub_4E6730` and `sub_4B4100`, or continue the retained host-service cleanup
through the adjacent unresolved monitor/event seam now that the libzmq
lifecycle owners are no longer anonymous.
