# Quake Live ZMQ/CZMQ Mapping Round 392

Date: 2026-06-06

Focus: recover the retained libzmq `i_engine` base-interface destructor
wrappers, the missing `stream_engine_t::restart_output` vtable slot, and the
shared peer-address helper used by the stream-engine constructor.

## Retail Evidence

- Owning binary: `assets/quakelive/quakelive_steam.exe`.
- Canonical HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt`
  and
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt`.
- Structured companion corpus:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`,
  `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`, and
  `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`.
- Symbol/name support:
  `references/analysis/quakelive_symbol_aliases.json`.

Rounds 166, 379, 390, and 391 already pinned the stream-engine constructor,
main destructor, socket read/write helpers, listener/connecter handoff, and
shared TCP/IP socket tuning helpers. This pass closes the remaining class-edge
and endpoint-name helper around that island instead of forcing the larger
handshake callback cluster early.

## Alias Reconstruction

This pass added 6 aliases to
`references/analysis/quakelive_symbol_aliases.json`.

| Symbol | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_421670` | `zmq_i_engine_t_dtor` | High | Tiny base destructor that writes `zmq::i_engine::vftable`; adjacent to the complete object construction in `stream_engine_t` and backed by the `i_engine` RTTI/vtable symbols. |
| `sub_421680` | `zmq_i_engine_t_scalar_deleting_dtor` | High | Scalar deleting destructor for `zmq::i_engine`: restores the base vtable and conditionally calls `operator delete` when the low delete flag is set; vtable slot `zmq::i_engine::vftable::vFunc_0`. |
| `sub_421800` | `zmq_stream_engine_t_scalar_deleting_dtor` | High | IO-object-side scalar deleting destructor for `stream_engine_t`: calls the already-promoted `zmq_stream_engine_t_dtor`, then conditionally frees the allocation. |
| `sub_422220` | `zmq_stream_engine_t_restart_output` | High | `i_engine` vtable slot immediately paired with `restart_input`; it clears the output-stopped latch, re-enables pollout via `io_object_t`, and dispatches the output-event slot. |
| `sub_4239B0` | `zmq_stream_engine_t_i_engine_scalar_deleting_dtor` | High | `i_engine`-subobject deleting-destructor thunk for `stream_engine_t`; subtracts the `i_engine` base offset and tail-calls the complete scalar deleting destructor. |
| `sub_423BD0` | `zmq_get_peer_ip_address` | High | Shared `ip.cpp` helper called from the stream-engine constructor; uses `getpeername`, `getnameinfo(..., NI_NUMERICHOST)`, writes the host string, and returns a boolean success byte with Windows socket-error assertion handling. |

## Observed Facts

- `sub_421670` and `sub_421680` are base-interface lifecycle helpers, not
  stream-engine methods. The direct vtable write to `zmq::i_engine::vftable`
  and the standalone `i_engine` vtable slot make the ownership boundary exact.
- `sub_421800` is the complete-object deleting destructor seen through the
  `stream_engine_t` IO-object vtable. Its body has no policy logic: it calls
  `sub_421830` and only then applies the C++ scalar-delete flag.
- `sub_4239B0` is the second deleting-destructor entry needed for multiple
  inheritance. Its `arg1 - 8` adjustment matches the `i_engine` subobject offset
  already visible in `terminate()` and the `stream_engine_t` vtable layout.
- `sub_422220` sits in the `i_engine` vtable directly after
  `restart_input`. Its control flow mirrors the output half of the stream
  engine: if output is not already stopped, it clears the output-stopped state,
  calls the poller helper that enables pollout, and then dispatches the
  IO-object output event slot.
- `sub_423BD0` is not a class method. It belongs to the shared IP helper layer:
  the constructor first makes the socket nonblocking, then calls this helper to
  populate the peer-address string, falling back to an empty/default endpoint
  string when peer-name discovery fails.

## Source Reconstruction

This round stays mapping/static reconstruction only. The recovered source shape
is narrow and mechanical:

```c
// conceptual reconstruction, not checked-in engine C source
i_engine_t::~i_engine_t()
{
	this->vptr = &zmq::i_engine::vftable;
}

stream_engine_t::restart_output()
{
	if (output_stopped)
		return;
	if (pollout_disabled) {
		io_object_t::set_pollout(handle);
		pollout_disabled = false;
	}
	out_event();
}

bool get_peer_ip_address(string_t *out, fd_t fd)
{
	if (getpeername(fd, &addr, &addr_len) == -1)
		return false after allowed transient-error handling;
	if (getnameinfo(&addr, addr_len, host, sizeof(host), NULL, 0, NI_NUMERICHOST) != 0)
		return false;
	out->assign(host);
	return true;
}
```

The GPL-side server remains correctly wired through the public ZMQ API in
`src/code/server/sv_zmq.c`. These private C++ helpers document the retained
retail libzmq implementation that sits behind Quake Live's publication/RCON
service path; no live online-service behavior is introduced.

The static parity guard in `tests/test_platform_services.py` pins:

- all aliases promoted in this round;
- the matching Ghidra `functions.csv` rows;
- import evidence for `getpeername` and `getnameinfo`;
- analysis-symbol evidence for the `i_engine` and `stream_engine_t` vtables;
- HLIL evidence for the base vtable writes, scalar-delete branches,
  multiple-inheritance thunk, `restart_output` state/pollout path, and
  peer-name string assignment; and
- this round note as the evidence ledger.

## Inference Boundary

This pass intentionally does not promote `sub_4231B0` or the adjacent
`sub_422EA0`/`sub_422F50` callback pair. They are clearly inside the
stream-engine mechanism/encoder/decoder lane, but their stable retail names
need a separate handshake-state pass rather than being inferred from proximity.

## Verification

Local verification for this pass:

- `Get-Content -Raw references/analysis/quakelive_symbol_aliases.json | ConvertFrom-Json | Out-Null`
- `python -m pytest -q tests/test_platform_services.py::test_zmq_stream_engine_peer_round_392_aliases_are_pinned`
- `python -m pytest -q tests/test_platform_services.py::test_zmq_stream_engine_peer_round_392_aliases_are_pinned tests/test_platform_services.py::test_zmq_tcp_socket_and_endpoint_round_391_aliases_are_pinned tests/test_platform_services.py::test_zmq_tcp_listener_round_390_aliases_are_pinned tests/test_platform_services.py::test_zmq_tcp_connecter_round_379_aliases_are_pinned tests/test_platform_services.py::test_zmq_options_default_and_mask_vector_round_378_aliases_are_pinned tests/test_platform_services.py::test_zmq_poller_base_io_object_round_377_aliases_are_pinned tests/test_platform_services.py::test_zmq_public_api_aliases_and_round_365_evidence_are_pinned`
- `python -m pytest -q tests/test_platform_services.py::test_server_zmq_runtime_reconstructs_retail_publication_and_rcon_owners tests/test_server_full_parity_gate.py::test_server_full_parity_gate_writes_status_artifact`

## Parity Estimate

- Focused stream-engine class-edge and peer-address helper mapping:
  **before 46% -> after 90%**.
- ZMQ-related source reconstruction confidence, including retained
  publication/RCON ownership, public wrappers, socket/message helpers,
  command-delivery support, queue backing-store evidence, object lifecycle
  ownership, event-loop timer/fd-watch wiring, option/default storage, TCP
  connecter reconnect/stream-engine handoff, TCP listener bind/accept handoff,
  shared TCP/IP helper wiring, and stream-engine class-edge/peer-address
  helpers:
  **before 86.9% -> after 87.2%**.
- Overall Quake Live source parity:
  **before 55.55% -> after 55.56%**.
