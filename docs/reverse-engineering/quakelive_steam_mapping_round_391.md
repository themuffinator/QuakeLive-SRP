# Quake Live ZMQ/CZMQ Mapping Round 391

Date: 2026-06-06

Focus: recover shared retained libzmq TCP socket tuning, IP socket setup, and
endpoint URI rendering helpers that wire the listener, connecter, mailbox, and
stream-engine paths together.

## Retail Evidence

- Owning binary: `assets/quakelive/quakelive_steam.exe`.
- Canonical HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt`.
- Structured companion corpus:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv` and
  `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`.
- Symbol/name support:
  `references/analysis/quakelive_symbol_aliases.json`.

Rounds 379 and 390 explicitly deferred the shared socket-option and endpoint
helpers because their evidence spans `tcp_connecter_t`, `tcp_listener_t`,
`stream_engine_t`, `socket_base_t`, `mailbox_t`, `tcp.cpp`, and `ip.cpp`. This
pass closes that shared helper layer.

## Alias Reconstruction

This pass added 8 aliases to
`references/analysis/quakelive_symbol_aliases.json`.

| Symbol | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_41AC10` | `zmq_endpoint_t_to_string` | High | Cross-cutting endpoint renderer used by socket-base connect and `tcp_connecter_t` construction; it dispatches to the concrete TCP address stringifier when a TCP address object exists, otherwise builds `protocol://address` from endpoint strings. |
| `sub_421420` | `zmq_tune_tcp_socket` | High | `tcp.cpp` helper sets `TCP_NODELAY` through `setsockopt(level: 6, optname: 1)` and is called immediately after listener/connecter sockets are accepted or connected. |
| `sub_4214A0` | `zmq_tune_tcp_sndbuf` | High | `tcp.cpp` helper sets `SO_SNDBUF` through `setsockopt(SOL_SOCKET, 0x1001)` from the options send-buffer lane before bind/connect socket use. |
| `sub_421520` | `zmq_tune_tcp_rcvbuf` | High | `tcp.cpp` helper sets `SO_RCVBUF` through `setsockopt(SOL_SOCKET, 0x1002)` from the options receive-buffer lane before bind/connect socket use. |
| `sub_4215A0` | `zmq_tune_tcp_keepalives` | High | `tcp.cpp` helper builds the Windows keepalive-values structure and calls `WSAIoctl(SIO_KEEPALIVE_VALS)`, with default idle/interval fallbacks. |
| `sub_4239C0` | `zmq_make_socket_noninheritable` | High | `ip.cpp` helper calls `SetHandleInformation(HANDLE_FLAG_INHERIT, 0)` after socket/fd-pair creation and asserts on the formatted Windows error path. |
| `sub_423AD0` | `zmq_unblock_socket` | High | `ip.cpp` helper calls `ioctlsocket(FIONBIO, 1)` and is used for mailbox fdpairs, stream-engine sockets, and TCP connecter sockets. |
| `sub_423B50` | `zmq_enable_ipv4_mapping` | High | `ip.cpp` helper clears `IPV6_V6ONLY` through `setsockopt(IPPROTO_IPV6, IPV6_V6ONLY, 0)` for IPv6 sockets in listener and connecter setup. |

## Observed Facts

- `zmq_endpoint_t_to_string` is shared by the socket-base connect path and
  the TCP connecter constructor. For TCP endpoints with a concrete address
  object, it calls that object's virtual `to_string`; otherwise it constructs
  the literal `protocol://address` form used when registering endpoints.
- `zmq_tune_tcp_socket` is called by both accepted listener sockets and
  completed connecter sockets before stream-engine construction; it pins the
  `TCP_NODELAY` behavior that removes Nagle latency from retained ZMQ traffic.
- The send/receive buffer helpers are gated by options fields before listener
  bind/listen setup and connecter open/connect setup. The call sites preserve
  the configured option value in the decompiler's stack-temporary lane before
  calling the helper.
- `zmq_tune_tcp_keepalives` is called only when the keepalive option is not
  `-1`. Its HLIL keeps the Windows `SIO_KEEPALIVE_VALS` code
  `0x98000004`, the millisecond conversion, and the default idle/interval
  fallbacks.
- `zmq_make_socket_noninheritable` is used after listener socket creation,
  select/signaler fd-pair creation, and connecter socket creation; the helper
  belongs to `ip.cpp`, not a particular class.
- `zmq_unblock_socket` is likewise shared by mailbox/signaler fd pairs,
  stream-engine construction, and the connecter open path.
- `zmq_enable_ipv4_mapping` is invoked when the resolved address family is
  IPv6 (`0x17`) so dual-stack TCP listeners/connecters can accept IPv4-mapped
  traffic.

## Source Reconstruction

This is mapping/static reconstruction only. No engine C source changed in this
pass. The recovered helpers explain the retained libzmq socket setup layer
under the repo-facing ZMQ support in `src/code/server/sv_zmq.c`; the GPL-side
runtime continues to use the dynamically loaded public ZMQ API rather than
rebuilding these private C++ helpers.

The static parity guard in `tests/test_platform_services.py` pins:

- all aliases promoted in this round;
- the matching Ghidra `functions.csv` rows;
- import evidence for `SetHandleInformation`, `ioctlsocket`, `setsockopt`, and
  `WSAIoctl`;
- representative HLIL evidence for endpoint string rendering, `TCP_NODELAY`,
  send/receive buffer tuning, keepalive ioctl setup, non-inheritable sockets,
  nonblocking sockets, IPv4 mapping, and listener/connecter/stream-engine
  call-site wiring; and
- this round note as the evidence ledger.

## Inference Boundary

This pass intentionally does not rename the adjacent endpoint string-pair constructor/destructor
around `sub_41AAE0` and `sub_41AB60`. They are clearly endpoint container
lifecycle helpers, but their final retail type boundary is less stable than
the renderer and socket helpers named here.

## Verification

Local verification for this pass:

- `Get-Content -Raw references/analysis/quakelive_symbol_aliases.json | ConvertFrom-Json | Out-Null`
- `python -m pytest -q tests/test_platform_services.py::test_zmq_tcp_socket_and_endpoint_round_391_aliases_are_pinned tests/test_platform_services.py::test_zmq_tcp_listener_round_390_aliases_are_pinned tests/test_platform_services.py::test_zmq_tcp_connecter_round_379_aliases_are_pinned tests/test_platform_services.py::test_zmq_options_default_and_mask_vector_round_378_aliases_are_pinned tests/test_platform_services.py::test_zmq_poller_base_io_object_round_377_aliases_are_pinned tests/test_platform_services.py::test_zmq_public_api_aliases_and_round_365_evidence_are_pinned`
- `python -m pytest -q tests/test_platform_services.py::test_server_zmq_runtime_reconstructs_retail_publication_and_rcon_owners tests/test_server_full_parity_gate.py::test_server_full_parity_gate_writes_status_artifact`

## Parity Estimate

- Focused shared TCP/IP/endpoint helper mapping:
  **before 42% -> after 92%**.
- ZMQ-related source reconstruction confidence, including retained
  publication/RCON ownership, public wrappers, socket/message helpers,
  command-delivery support, queue backing-store evidence, object lifecycle
  ownership, event-loop timer/fd-watch wiring, option/default storage, TCP
  connecter reconnect/stream-engine handoff, TCP listener bind/accept handoff,
  and shared TCP/IP helper wiring:
  **before 86.5% -> after 86.9%**.
- Overall Quake Live source parity:
  **before 55.54% -> after 55.55%**.
