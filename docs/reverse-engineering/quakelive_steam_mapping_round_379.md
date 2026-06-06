# Quake Live ZMQ/CZMQ Mapping Round 379

Date: 2026-06-06

Focus: recover the retained libzmq `tcp_connecter_t` lifecycle and
nonblocking-connect wiring that bridges `session_base_t::start_connecting`,
the poller/io-object fd watch layer, reconnect timers, and stream-engine
handoff.

## Retail Evidence

- Owning binary: `assets/quakelive/quakelive_steam.exe`.
- Canonical HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt`
  and vtable/RTTI anchors in
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt`.
- Structured companion corpus:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`.
- Symbol/name support:
  `references/analysis/quakelive_symbol_aliases.json`.

Round 196 named the `session_base_t::start_connecting` caller. Round 377
named the poller/io-object timer and fd-watch helpers it relies on. This pass
fills the connecter class that sits between those two areas.

## Alias Reconstruction

This pass added 13 aliases to
`references/analysis/quakelive_symbol_aliases.json`.

| Symbol | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_423F50` | `zmq_tcp_connecter_t_scalar_deleting_dtor` | High | Scalar deleting destructor for the `tcp_connecter_t` own-vtable slot; calls the complete destructor and conditionally frees `this`. |
| `sub_423F80` | `zmq_tcp_connecter_t_dtor` | High | Complete destructor restores connecter vtables, asserts no reconnect timer/handle/socket remain live, frees the endpoint string, destroys `own_t` state, and restores `object_t`. |
| `sub_424120` | `zmq_tcp_connecter_t_process_plug` | High | Own-vtable plug slot chooses immediate `start_connecting` or delayed reconnect-timer arming based on the constructor's delayed-start flag. |
| `sub_424140` | `zmq_tcp_connecter_t_process_term` | High | Cancels reconnect timer id `1`, removes the poller fd handle, closes any live socket, then delegates to `own_t::process_term`. |
| `sub_4241B0` | `zmq_tcp_connecter_t_in_event` | High | IO-object vtable input slot tailcalls the output-event slot, matching the connecter shape where readiness completion is handled through the write-ready path. |
| `sub_4241C0` | `zmq_tcp_connecter_t_out_event` | High | Completes the nonblocking connection, removes the fd watch, creates a `stream_engine_t`, sends the bind command to the session owner, launches ownership checks, and emits a monitor-connected event. |
| `sub_4243B0` | `zmq_tcp_connecter_t_timer_event` | High | Asserts timer id `reconnect_timer_id` (`1`), clears the timer-started flag, and restarts connection attempts. |
| `sub_424420` | `zmq_tcp_connecter_t_start_connecting` | High | Opens the socket, adds the fd to the select poller, either completes immediately or arms write interest for `EINPROGRESS`, and schedules retry on failure. |
| `sub_424510` | `zmq_tcp_connecter_t_add_reconnect_timer` | High | Computes jittered reconnect interval from reconnect ivl/max state, adds poller timer id `1`, emits monitor-retry, and marks `timer_started`. |
| `sub_4245B0` | `zmq_tcp_connecter_t_open` | High | Creates a TCP socket, tunes nonblocking and TCP options, applies keepalive options, calls Winsock `connect`, and maps `WSAEINPROGRESS`/`WSAEWOULDBLOCK` to `EINPROGRESS`. |
| `sub_424720` | `zmq_tcp_connecter_t_connect` | High | Checks `SO_ERROR` after write readiness, filters connection-failure error codes, returns the connected socket on success, and retires the stored fd. |
| `sub_424830` | `zmq_tcp_connecter_t_close` | High | Asserts the socket is live, closes it, tolerates `WSAENOTSOCK`, emits a monitor-closed event when requested, and retires the stored fd. |
| `sub_424930` | `zmq_tcp_connecter_t_io_object_scalar_deleting_dtor` | High | IO-object subobject destructor thunk adjusts from the `io_object_t` base at offset `0x278` back to the complete connecter object. |

## Observed Facts

- The `tcp_connecter_t` own-vtable maps `process_plug` to `sub_424120` and
  `process_term` to `sub_424140`. Its `io_object_t` vtable maps the subobject
  destructor thunk, input event, output event, and timer event to the newly
  named helpers.
- The constructor named in round 133 stores the delayed-start flag at
  `this + 0x28d`, initializes `s` to `retired_fd`, copies only `tcp` endpoint
  strings, and copies the reconnect interval state from the embedded options.
- `process_plug` is the split point: immediate connect attempts call
  `start_connecting`, while delayed starts call `add_reconnect_timer`.
- `process_term` cancels timer id `1`, removes a registered fd handle through
  the select poller, closes a live socket, then enters the already named
  `own_t` termination flow.
- `start_connecting` calls `open`; immediate success registers the fd and
  calls the readiness path, `EINPROGRESS` registers the fd for pollout, and
  hard failure closes/retires the socket before scheduling the reconnect timer.
- `out_event` uses the newly named `connect` completion helper, removes the
  fd watch, constructs a `stream_engine_t`, sends the bind command to the
  session, launches ownership checks, and emits a monitor event when the
  socket monitor mask requests it.
- `add_reconnect_timer` uses two `rand()` calls to jitter the current reconnect
  interval, doubles toward the configured maximum when applicable, adds poller
  timer id `1`, and marks the timer as active.
- `open`, `connect`, and `close` are all Windows-socket-specific in the retail
  binary: `socket`, `connect`, `getsockopt(SO_ERROR)`, and `closesocket` are
  visible in HLIL, with ZeroMQ errno mapping retained through the existing
  error helpers.

## Source Reconstruction

This is mapping/static reconstruction only. No engine C source changed in this
pass. The recovered names refine the private libzmq TCP connecter class behind
the repo-facing server ZMQ support in `src/code/server/sv_zmq.c`; they do not
require recreating the retained C++ connecter in GPL-side C.

The static parity guard in `tests/test_platform_services.py` pins:

- all aliases promoted in this round;
- the matching Ghidra `functions.csv` rows;
- representative HLIL evidence for construction invariants, vtable slots,
  destruction preconditions, plug/term behavior, fd-watch handoff, reconnect
  timers, socket open/connect/close helpers, stream-engine binding, and monitor
  event emission; and
- this round note as the evidence ledger.

## Inference Boundary

This pass intentionally stays inside `tcp_connecter_t`. It does not rename the
nearby TCP socket tuning helpers around `sub_4239C0`, `sub_423AD0`,
`sub_423B50`, `sub_4214A0`, and `sub_421520`; those are clearer as a future
socket-option/tuning pass spanning `tcp_connecter.cpp`, `ip.cpp`, and the
stream-engine socket helpers.

## Verification

Local verification for this pass:

- `Get-Content -Raw references/analysis/quakelive_symbol_aliases.json | ConvertFrom-Json | Out-Null`
- `python -m pytest -q tests/test_platform_services.py::test_zmq_tcp_connecter_round_379_aliases_are_pinned tests/test_platform_services.py::test_zmq_options_default_and_mask_vector_round_378_aliases_are_pinned tests/test_platform_services.py::test_zmq_poller_base_io_object_round_377_aliases_are_pinned tests/test_platform_services.py::test_zmq_io_thread_reaper_object_command_round_376_aliases_are_pinned tests/test_platform_services.py::test_zmq_public_api_aliases_and_round_365_evidence_are_pinned`
  passed with `5 passed`.
- `python -m pytest -q tests/test_platform_services.py::test_server_zmq_runtime_reconstructs_retail_publication_and_rcon_owners tests/test_server_full_parity_gate.py::test_server_full_parity_gate_writes_status_artifact`
  passed with `2 passed`.

## Parity Estimate

- Focused ZMQ TCP connecter lifecycle/nonblocking-connect mapping:
  **before 34% -> after 91%**.
- ZMQ-related source reconstruction confidence, including retained
  publication/RCON ownership, public wrappers, socket/message helpers,
  command-delivery support, queue backing-store evidence, object lifecycle
  ownership, event-loop timer/fd-watch wiring, option/default storage, and
  TCP connecter reconnect/stream-engine handoff:
  **before 85.7% -> after 86.1%**.
- Overall Quake Live source parity:
  **before 55.52% -> after 55.53%**.
