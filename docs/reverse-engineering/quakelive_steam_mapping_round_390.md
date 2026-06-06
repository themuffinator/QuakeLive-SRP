# Quake Live ZMQ/CZMQ Mapping Round 390

Date: 2026-06-06

Focus: recover the retained libzmq `tcp_listener_t` lifecycle, bind/listen
setup, accept event, endpoint publication, fd-watch registration, and
stream-engine handoff that sits opposite the `tcp_connecter_t` reconstruction
from round 379.

## Retail Evidence

- Owning binary: `assets/quakelive/quakelive_steam.exe`.
- Canonical HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt`
  and vtable/RTTI anchors in
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt`.
- Structured companion corpus:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`.
- Symbol/name support:
  `references/analysis/quakelive_symbol_aliases.json` and the promoted
  `tcp_listener_t` RTTI/vtable symbols in
  `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`.

Rounds 125, 126, and 128 had already identified the listener set-address,
accept, and input-event paths. This pass completes the surrounding class
lifecycle and endpoint wiring, and re-pins the earlier listener names under one
cohesive map.

## Alias Reconstruction

This pass added 8 aliases to
`references/analysis/quakelive_symbol_aliases.json` and re-pinned 3 earlier listener aliases.

| Symbol | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_419D90` | `zmq_tcp_listener_t_ctor` | High | Constructor installs the `own_t` and `io_object_t` listener vtables, initializes embedded `tcp_address_t`, retires the socket fd, stores the owning socket/options pointer, and clears the endpoint string. |
| `sub_419E30` | `zmq_tcp_listener_t_scalar_deleting_dtor` | High | Own-vtable destructor slot calls the complete listener destructor and conditionally frees `this`. |
| `sub_419E60` | `zmq_tcp_listener_t_dtor` | High | Complete destructor restores listener vtables, asserts `s == retired_fd` at `tcp_listener.cpp:0x3e`, frees the endpoint string, destroys the embedded address, and tears down inherited `own_t`/`object_t` state. |
| `sub_419F90` | `zmq_tcp_listener_t_process_plug` | High | Own-vtable plug slot registers the listener fd with the select poller and mirrors it into the read-interest table. |
| `sub_419FF0` | `zmq_tcp_listener_t_process_term` | High | Own-vtable term slot removes the fd watch, closes the listener socket, then delegates to `own_t::process_term`. |
| `sub_41A020` | `zmq_tcp_listener_t_in_event` | High | IO-object input-event slot accepts a socket, tunes TCP options, creates a `stream_engine_t` and `session_base_t`, sends the bind command, signals the session mailbox, and emits accepted/accept-failed monitor events. |
| `sub_41A2D0` | `zmq_tcp_listener_t_close` | High | Close helper asserts a live listener fd at `tcp_listener.cpp:0x73`, calls `closesocket`, tolerates the ZeroMQ-mapped transient close case, emits monitor-closed, and retires the fd. |
| `sub_41A3D0` | `zmq_tcp_listener_t_get_address` | High | Endpoint query helper calls `getsockname`, wraps the sockaddr in `tcp_address_t`, and serializes it with the already named `zmq_tcp_address_t_to_string`; the socket-base bind path uses it before registering the endpoint. |
| `sub_41A490` | `zmq_tcp_listener_t_set_address` | High | Bind/listen setup resolves the endpoint, creates and tunes a TCP socket, binds, listens with the configured backlog, stores the rendered endpoint string, and emits the listener monitor event. |
| `sub_41A7C0` | `zmq_tcp_listener_t_accept` | High | Accept helper asserts a live listener fd at `tcp_listener.cpp:0xf9`, accepts a connection, applies inheritable-handle protection, checks address-mask filters, closes rejected sockets, and maps transient accept failures. |
| `sub_41AAD0` | `zmq_tcp_listener_t_io_object_scalar_deleting_dtor` | High | IO-object subobject destructor thunk adjusts from the `io_object_t` base at offset `0x278` back to the complete listener object. |

## Observed Facts

- The listener constructor is allocated from the socket-base bind path for
  `tcp` endpoints, then `set_address` is invoked. On success, the resolved
  bound endpoint is fetched through `get_address` and registered by
  `socket_base_t`.
- The listener own-vtable maps the scalar deleting destructor, `process_plug`,
  and `process_term` to `sub_419E30`, `sub_419F90`, and `sub_419FF0`.
- The listener `io_object_t` vtable maps the subobject destructor thunk and
  input-event slot to `sub_41AAD0` and `sub_41A020`. The inherited output and
  timer slots still resolve to the generic io-object empty handlers.
- `process_plug` registers `this + 0x278` as the poll-events object for the
  live listener socket and mirrors the handle into the select read-interest
  array.
- `process_term` removes that fd watch, closes the listener socket through the
  new `close` alias, and then enters the already named `own_t` term path.
- `in_event` is the accept-to-session bridge: it calls `accept`, configures the
  accepted socket, constructs `stream_engine_t`, creates a session on the next
  io-thread, launches ownership, sends the bind command, signals the mailbox,
  and emits monitor events for accepted or failed accepts.
- `set_address` is Windows-socket-specific in this retail binary: `socket`,
  `SetHandleInformation`, `setsockopt`, `bind`, `listen`, and `closesocket`
  are visible in HLIL, with errno preservation around failed bind/listen close
  cleanup.
- `accept` applies the options-owned address-mask vector before exposing the
  accepted socket; rejected sockets are immediately closed.

## Source Reconstruction

This is mapping/static reconstruction only. No engine C source changed in this
pass. The recovered names refine the private retained libzmq listener class
behind the repo-facing server ZMQ support in `src/code/server/sv_zmq.c`; they
do not require recreating the retained C++ listener in GPL-side C.

The static parity guard in `tests/test_platform_services.py` pins:

- all listener aliases promoted or re-pinned in this round;
- the matching Ghidra `functions.csv` rows;
- representative HLIL evidence for socket-base construction, vtables,
  constructor/destructor invariants, plug/term fd-watch lifecycle, endpoint
  query, bind/listen setup, accept filtering, close behavior, session and
  stream-engine handoff, mailbox signaling, and monitor events; and
- this round note as the evidence ledger.

## Inference Boundary

This pass intentionally stays inside `tcp_listener_t`. It does not rename the
nearby generic endpoint-pair string helpers around `sub_41AAE0`/`sub_41AB60`
or the cross-cutting endpoint URI formatter around `sub_41AC10`; those span
listener, connecter, and socket-base evidence and are better handled as a
future endpoint-format pass.

## Verification

Local verification for this pass:

- `Get-Content -Raw references/analysis/quakelive_symbol_aliases.json | ConvertFrom-Json | Out-Null`
- `python -m pytest -q tests/test_platform_services.py::test_zmq_tcp_listener_round_390_aliases_are_pinned tests/test_platform_services.py::test_zmq_tcp_connecter_round_379_aliases_are_pinned tests/test_platform_services.py::test_zmq_options_default_and_mask_vector_round_378_aliases_are_pinned tests/test_platform_services.py::test_zmq_poller_base_io_object_round_377_aliases_are_pinned tests/test_platform_services.py::test_zmq_public_api_aliases_and_round_365_evidence_are_pinned`
- `python -m pytest -q tests/test_platform_services.py::test_server_zmq_runtime_reconstructs_retail_publication_and_rcon_owners tests/test_server_full_parity_gate.py::test_server_full_parity_gate_writes_status_artifact`

## Parity Estimate

- Focused ZMQ TCP listener lifecycle/bind/accept mapping:
  **before 39% -> after 90%**.
- ZMQ-related source reconstruction confidence, including retained
  publication/RCON ownership, public wrappers, socket/message helpers,
  command-delivery support, queue backing-store evidence, object lifecycle
  ownership, event-loop timer/fd-watch wiring, option/default storage, TCP
  connecter reconnect/stream-engine handoff, and TCP listener bind/accept
  handoff:
  **before 86.1% -> after 86.5%**.
- Overall Quake Live source parity:
  **before 55.53% -> after 55.54%**.
