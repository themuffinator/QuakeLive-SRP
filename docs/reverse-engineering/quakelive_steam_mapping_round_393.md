# Quake Live ZMQ/CZMQ Mapping Round 393

Date: 2026-06-06

Focus: recover the retained libzmq `stream_engine_t` message-state callbacks
that bridge identity exchange, ZAP/mechanism handshakes, normal session
pull/push, and the PUB/XPUB phantom-subscription compatibility path.

## Retail Evidence

- Owning binary: `assets/quakelive/quakelive_steam.exe`.
- Canonical HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt`
  and
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt`.
- Structured companion corpus:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`.
- Symbol/name support:
  `references/analysis/quakelive_symbol_aliases.json`.

Round 392 closed the `i_engine` class-edge and peer-address helpers. This pass
continues one layer inward and names the anonymous function-pointer callbacks
installed by the stream-engine constructor, greeting path, mechanism-ready path,
and backpressure path.

## Alias Reconstruction

This pass added 12 aliases to
`references/analysis/quakelive_symbol_aliases.json`.

| Symbol | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_422EA0` | `zmq_stream_engine_t_identity_msg` | High | Initializes a message to the configured identity size, copies the identity bytes, and advances the next-message callback to the session pull path. |
| `sub_422F50` | `zmq_stream_engine_t_process_identity_msg` | High | Handles the peer identity message, either forwards it to the session when `recv_identity` is enabled or closes/reinitializes it, then selects direct session push or the phantom-subscription writer. |
| `sub_423080` | `zmq_stream_engine_t_next_handshake_command` | High | Requires `mechanism != NULL`, asks the mechanism for the next handshake command, sets the command flag on success, and calls `mechanism_ready` once the mechanism is already ready. |
| `sub_423110` | `zmq_stream_engine_t_process_handshake_command` | High | Requires `mechanism != NULL`, processes inbound handshake commands through the mechanism, transitions to `mechanism_ready` on ready status, and restarts output when needed. |
| `sub_4231B0` | `zmq_stream_engine_t_zap_msg_available` | High | Final `i_engine` vtable slot; asks the mechanism to consume a ZAP message, converts `-1` into stream-engine error, and restarts stopped input/output lanes. |
| `sub_423250` | `zmq_stream_engine_t_mechanism_ready` | High | Transitions the stream engine from handshake to normal message flow by pushing pending credential/identity material when required, then installs `pull_and_encode` and `decode_and_push`. |
| `sub_423380` | `zmq_stream_engine_t_pull_msg_from_session` | High | Direct session-pipe read callback used by raw/identity-era output; calls the session pipe read helper and preserves the inbound-more bit. |
| `sub_4233D0` | `zmq_stream_engine_t_push_msg_to_session` | High | Direct session-pipe write callback; writes the received message to the session pipe and reinitializes the message on success. |
| `sub_423420` | `zmq_stream_engine_t_pull_and_encode` | High | Normal post-handshake output callback; pulls a message from the session, then passes it through the mechanism encoder. |
| `sub_4234E0` | `zmq_stream_engine_t_decode_and_push` | High | Normal post-handshake input callback; decodes through the mechanism, pushes to the session, and switches to the one-message retry callback on `EAGAIN`. |
| `sub_4235B0` | `zmq_stream_engine_t_push_one_then_decode_and_push` | High | Backpressure retry callback that pushes the already-decoded message and restores `decode_and_push` once the session accepts it. |
| `sub_423620` | `zmq_stream_engine_t_write_subscription_msg` | High | PUB/XPUB compatibility callback; injects a one-byte subscription message, switches to direct session push, and then forwards the pending identity/data message. |

## Observed Facts

- Quake Live's retained libzmq uses the older `identity_msg` /
  `process_identity_msg` naming lane. Modern libzmq source has mostly renamed
  the same concept to routing-id handling, but the retail HLIL keeps
  `options.recv_identity` evidence and the unversioned ZMTP identity exchange.
- The constructor seeds `identity_msg` and `process_identity_msg`. The raw-socket
  plug path bypasses mechanism negotiation and seeds direct
  `pull_msg_from_session` / `push_msg_to_session` callbacks instead.
- The ZMTP 3.x handshake branch allocates the mechanism, then installs
  `next_handshake_command` and `process_handshake_command`.
- `zap_msg_available` is the remaining `i_engine` slot after
  `restart_output`. It belongs to session/ZAP pipe activation rather than the
  ordinary application pipe path.
- `mechanism_ready` is the central state transition. It clears the handshake
  phase by installing `pull_and_encode` for outgoing messages and
  `decode_and_push` for incoming messages after any required identity or
  credential material has been delivered to the session.
- `decode_and_push` and `push_one_then_decode_and_push` form a backpressure
  pair: when the session pipe returns `EAGAIN`, the already-decoded message is
  not decoded a second time; the callback pointer is temporarily redirected to
  retry that single push.
- `write_subscription_msg` is only selected from `process_identity_msg` when the
  earlier greeting path marked PUB/XPUB subscription compatibility as required.
  It injects the one-byte subscription before normal session push resumes.

## Source Reconstruction

This round is mapping/static reconstruction only. The recovered source shape is
the stream-engine state machine, not new GPL-side runtime code:

```c
// conceptual reconstruction, not checked-in engine C source
identity_msg(msg)
{
	msg->init_size(options.identity_size);
	copy_identity_bytes(msg);
	next_msg = pull_msg_from_session;
}

process_handshake_command(msg)
{
	rc = mechanism->process_handshake_command(msg);
	if (rc == 0 && mechanism->status() == ready)
		mechanism_ready();
	if (output_stopped)
		restart_output();
	return rc;
}

mechanism_ready()
{
	deliver_pending_identity_or_credential_if_needed();
	next_msg = pull_and_encode;
	process_msg = decode_and_push;
}

decode_and_push(msg)
{
	if (mechanism->decode(msg) == -1)
		return -1;
	if (session->push_msg(msg) == -1 && errno == EAGAIN)
		process_msg = push_one_then_decode_and_push;
	return rc;
}
```

The repo-facing server path in `src/code/server/sv_zmq.c` remains unchanged and
continues to use the dynamically loaded public ZMQ API. The retained private
C++ stream-engine callbacks explain the retail library internals underneath
that service lane.

The static parity guard in `tests/test_platform_services.py` pins:

- all aliases promoted in this round;
- the matching Ghidra `functions.csv` rows;
- constructor/greeting call-site assignments into the `next_msg` and
  `process_msg` members;
- HLIL assertions and mechanism vtable calls for handshake and ZAP progress;
- direct pipe read/write helpers for session pull/push;
- mechanism encode/decode transitions;
- the backpressure retry callback switch; and
- this round note as the evidence ledger.

## Inference Boundary

This pass intentionally does not rename adjacent mechanism concrete classes or
their security-protocol callbacks. It references their vtable calls only as
evidence for the stream-engine callback names promoted here.

## Verification

Local verification for this pass:

- `Get-Content -Raw references/analysis/quakelive_symbol_aliases.json | ConvertFrom-Json | Out-Null`
- `python -m pytest -q tests/test_platform_services.py::test_zmq_stream_engine_state_machine_round_393_aliases_are_pinned`
- `python -m pytest -q tests/test_platform_services.py::test_zmq_stream_engine_state_machine_round_393_aliases_are_pinned tests/test_platform_services.py::test_zmq_stream_engine_peer_round_392_aliases_are_pinned tests/test_platform_services.py::test_zmq_tcp_socket_and_endpoint_round_391_aliases_are_pinned tests/test_platform_services.py::test_zmq_tcp_listener_round_390_aliases_are_pinned tests/test_platform_services.py::test_zmq_tcp_connecter_round_379_aliases_are_pinned tests/test_platform_services.py::test_zmq_options_default_and_mask_vector_round_378_aliases_are_pinned tests/test_platform_services.py::test_zmq_poller_base_io_object_round_377_aliases_are_pinned tests/test_platform_services.py::test_zmq_public_api_aliases_and_round_365_evidence_are_pinned`
- `python -m pytest -q tests/test_platform_services.py::test_server_zmq_runtime_reconstructs_retail_publication_and_rcon_owners tests/test_server_full_parity_gate.py::test_server_full_parity_gate_writes_status_artifact`

## Parity Estimate

- Focused stream-engine message-state callback mapping:
  **before 48% -> after 91%**.
- ZMQ-related source reconstruction confidence, including retained
  publication/RCON ownership, public wrappers, socket/message helpers,
  command-delivery support, queue backing-store evidence, object lifecycle
  ownership, event-loop timer/fd-watch wiring, option/default storage, TCP
  connecter reconnect/stream-engine handoff, TCP listener bind/accept handoff,
  shared TCP/IP helper wiring, stream-engine class-edge/peer-address helpers,
  and stream-engine message-state callbacks:
  **before 87.2% -> after 87.7%**.
- Overall Quake Live source parity:
  **before 55.56% -> after 55.57%**.
