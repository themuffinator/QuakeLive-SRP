# quakelive_steam.exe Mapping Round 196

Date: 2026-04-28

Scope: retained STL/iostream and libzmq host-service recovery centered on the
old queue heads at `0x0041AD70`, `0x0041C400`, and `0x00414AC0`, plus the
adjacent `session_base.cpp` callback/termination helpers around
`0x0041B630` through `0x0041C400`.

## Summary

This round resolved `14` additional `quakelive_steam.exe` rows.
Classification mix:

- `0` engine-owned functions
- `13` platform-service-owned functions
- `1` CRT/STL/support-library function
- `0` Awesomium functions
- `0` Steam SDK support functions

The useful outcome is that the old mixed STL/ZeroMQ queue slab now reads as a
real retained `session_base.cpp` / `router.cpp` family rather than opaque host
glue. The iostream queue head `sub_41AD70` is no longer anonymous, the router
constructor at `sub_414AC0` is now explicit, and the retained session lane now
carries exact ownership for `create`, `flush`, `clean_pipes`,
`pipe_terminated`, `read_activated`, `write_activated`, `hiccuped`,
`process_plug`, `zap_enabled`, `process_term`, `timer_event`, and
`start_connecting`.

## Evidence Notes

- `sub_41AD70` is exact as `std_ostream_insert_string` because the committed
  HLIL preserves the full `ostream << std::string` shape: sentry/flush setup,
  width/fill accounting, leading and trailing `std::streambuf::sputc` padding,
  the central `std::streambuf::sputn` over the string payload, width reset to
  zero, `std::ios::setstate`, and the final `std::ostream::_Osfx` path. This
  matches the repository's earlier `std_ostream_insert_cstr` naming style.
- `sub_414AC0` is exact as `zmq_router_t_ctor` because it first runs the
  retained `zmq_socket_base_t_ctor`, then installs the four `router_t`
  vtables, allocates the anonymous-pipe and out-pipe container nodes, seeds
  the random routing-id state, and writes the same option defaults preserved
  in the retained `router.cpp` constructor (`type = ZMQ_ROUTER`,
  `recv_routing_id = true`, `raw_socket = false`,
  `can_send_hello_msg = true`, and `can_recv_disconnect_msg = true`).
- `sub_41AFA0` is exact as `zmq_session_base_t_create` because the HLIL is the
  retained allocator switch from `session_base.cpp`: it selects the session
  subtype from `options.type`, allocates the right concrete session object,
  sets `errno = EINVAL` for unsupported types, and raises the same fatal
  out-of-memory path on allocator failure.
- `sub_41B630` and `sub_41B670` are exact as
  `zmq_session_base_t_flush` and `zmq_session_base_t_clean_pipes`. The former
  is the one-line `_pipe->flush()` wrapper with the retained inlined pipe flush
  logic, while the latter inlines the upstream `rollback` + `flush` cleanup and
  then drains `_incomplete_in` by repeatedly `pull_msg`-ing and closing
  half-read messages.
- `sub_41B820`, `sub_41B970`, `sub_41BA40`, and `sub_41BAF0` are exact as
  `pipe_terminated`, `read_activated`, `write_activated`, and `hiccuped`.
  Their HLIL bodies preserve the same branch structure as retained
  `session_base.cpp`: detached-pipe set checks, linger-timer cancellation,
  pending termination release, engine restart / ZAP notification dispatch, and
  the unconditional `assert(false)` hiccup owner.
- `sub_41BB40`, `sub_41BE90`, `sub_41C120`, `sub_41C260`, and `sub_41C400`
  are exact as `process_plug`, `zap_enabled`, `process_term`, `timer_event`,
  and `start_connecting`. The strongest anchors are the retained assertion
  strings and control flow: `process_term` asserts `!pending`, arms the linger
  timer with `linger_timer_id`, and terminates both main and ZAP pipes;
  `timer_event` asserts `id_ == linger_timer_id` then forces non-lingering
  termination; `start_connecting` asserts `connect` and `io_thread`, allocates
  the retained TCP connecter object through the already-mapped
  `zmq_tcp_connecter_t_ctor`, and launches it through the usual child-object
  handoff.
- I deliberately left the adjacent `engine_error` / `reconnect` body deferred.
  The retail compiler has transformed that seam more heavily, and this round
  already closed the stable `session_base.cpp` surface without needing to force
  the still-noisier reconnect/error ownership.

## Aliases Added

- `sub_414AC0` -> `zmq_router_t_ctor`
- `sub_41AD70` -> `std_ostream_insert_string`
- `sub_41AFA0` -> `zmq_session_base_t_create`
- `sub_41B630` -> `zmq_session_base_t_flush`
- `sub_41B670` -> `zmq_session_base_t_clean_pipes`
- `sub_41B820` -> `zmq_session_base_t_pipe_terminated`
- `sub_41B970` -> `zmq_session_base_t_read_activated`
- `sub_41BA40` -> `zmq_session_base_t_write_activated`
- `sub_41BAF0` -> `zmq_session_base_t_hiccuped`
- `sub_41BB40` -> `zmq_session_base_t_process_plug`
- `sub_41BE90` -> `zmq_session_base_t_zap_enabled`
- `sub_41C120` -> `zmq_session_base_t_process_term`
- `sub_41C260` -> `zmq_session_base_t_timer_event`
- `sub_41C400` -> `zmq_session_base_t_start_connecting`

## Verification

Static mapping validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- scoped duplicate-key scan for the `quakelive_steam` alias block passed with
  `0` duplicates
- recount after this pass: `2093` raw alias entries, `2021` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `36.927%` of `5473` functions
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
| 3 | `0x00409670` | `FUN_00409670` | `496` |
| 4 | `0x004B3672` | `FUN_004b3672` | `495` |
| 5 | `0x0046A420` | `FUN_0046a420` | `490` |
| 6 | `0x004DC730` | `FUN_004dc730` | `490` |
| 7 | `0x004C12F0` | `FUN_004c12f0` | `488` |
| 8 | `0x004368A0` | `FUN_004368a0` | `484` |
| 9 | `0x00429DD0` | `FUN_00429dd0` | `483` |
| 10 | `0x004A4280` | `FUN_004a4280` | `483` |

The next pass can return to the heavier host leftovers at `sub_4E6730` and
`sub_4B4100`, or come back to the still-inference-heavy ZeroMQ seam at
`sub_409670` now that the stable `session_base.cpp` / `router.cpp` ownership
has been promoted.
