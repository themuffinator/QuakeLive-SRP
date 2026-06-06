# Quake Live ZMQ/CZMQ Mapping Round 377

Date: 2026-06-06

Focus: recover the retained libzmq event-loop wiring that joins the select
poller, timer tree, and `io_object_t` fd-watch helpers used by sessions,
stream engines, listeners, and connectors.

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

Round 370 named the select poller constructor/destructor and mailbox signaler
lane. Round 376 named the `io_thread_t` and `reaper_t` command owners that
consume those pollers. This pass names the remaining event-loop owner APIs
that maintain poller timers and toggle `io_object_t` read/write interest.

## Alias Reconstruction

This pass added 12 aliases to
`references/analysis/quakelive_symbol_aliases.json`.

| Symbol | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_41C710` | `zmq_poller_base_t_scalar_deleting_dtor` | High | Scalar deleting destructor for the `poller_base_t` vtable; delegates to the complete destructor then conditionally frees `this`. |
| `sub_41C740` | `zmq_poller_base_t_dtor` | High | Restores the `poller_base_t` vtable, asserts `get_load() == 0`, erases the timer tree, deletes the sentinel node, and anchors to `src\poller_base.cpp`. |
| `sub_41C7F0` | `zmq_poller_base_t_add_timer` | High | Builds an absolute deadline from cached clock data, stores `{deadline, sink, id}`, creates a timer node, and inserts it through the round-148 timer-tree helper. |
| `sub_41C8A0` | `zmq_poller_base_t_cancel_timer` | High | Scans the timer tree for the matching sink/id pair, erases it through the round-148 timer erase helper, and asserts false when no matching timer exists. |
| `sub_41C970` | `zmq_poller_base_t_execute_timers` | High | Runs due timers in deadline order by calling the sink vtable timer slot with the stored id, erases executed nodes, and returns the next timeout for `select_t::loop`. |
| `sub_41D210` | `std_tree_create_zmq_timer_node` | High | Allocates and initializes the timer-tree node payload consumed by `zmq_poller_base_t_add_timer` and `std_tree_insert_zmq_timer_node`. |
| `sub_41DF50` | `zmq_i_poll_events_scalar_deleting_dtor` | High | Scalar deleting destructor for the `i_poll_events` base vtable. |
| `sub_41DF80` | `zmq_i_poll_events_dtor` | High | Complete base destructor shape for `i_poll_events`, restoring only the base vtable. |
| `sub_41DF90` | `zmq_io_object_t_plug` | High | Asserts a non-null `io_thread_t`, asserts no existing poller, resolves `io_thread_t::get_poller`, and stores the poller pointer in the `io_object_t`. |
| `sub_41E080` | `zmq_io_object_t_set_pollin` | High | Adds the object's fd handle to the select poller's read-interest array, eliding duplicates and respecting the `FD_SETSIZE`-sized mirror. |
| `sub_41E0C0` | `zmq_io_object_t_reset_pollin` | High | Removes the fd handle from the select poller's read-interest array; stream-engine input `EAGAIN` paths call this helper. |
| `sub_41E100` | `zmq_io_object_t_set_pollout` | High | Adds the fd handle to the select poller's write-interest array; tcp-connecter and stream-engine paths call this when they need write readiness. |

## Observed Facts

- `select_t::loop` now has its timer owner named: before each Windows
  `select()` call it invokes `zmq_poller_base_t_execute_timers`, copies fd sets,
  and uses the returned timeout.
- `zmq_session_base_t_process_term` and `zmq_tcp_connecter_t_start_connecting`
  both call `zmq_poller_base_t_add_timer` with class-owned ids. Their matching
  timer callbacks assert `linger_timer_id` (`0x20`) and
  `reconnect_timer_id` (`1`), respectively.
- `zmq_session_base_t` and `zmq_tcp_connecter_t` cancellation paths call
  `zmq_poller_base_t_cancel_timer`, tying the timer add/remove APIs back to
  owner classes already named in earlier ZMQ rounds.
- `stream_engine_t::plug`, `tcp_listener_t::set_address`,
  `session_base_t::process_plug`, and `tcp_connecter_t` construction paths
  call `zmq_io_object_t_plug`, which stores the select poller obtained from the
  owning `io_thread_t`.
- `zmq_io_object_t_set_pollin`, `reset_pollin`, and `set_pollout` directly
  manipulate the select poller's read/write interest mirrors. The call sites
  align with stream-engine read restart/input-EAGAIN handling and
  tcp-connecter nonblocking-connect completion.

## Source Reconstruction

This is mapping/static reconstruction only. No engine C source changed in this
pass. The recovered names refine the private libzmq wiring behind the
repo-facing direct-libzmq server fallback in `src/code/server/sv_zmq.c`; they
do not imply a need to recreate private C++ poller classes in the GPL-side C
source.

The static parity guard in `tests/test_platform_services.py` pins:

- all aliases promoted in this round;
- the matching Ghidra `functions.csv` rows;
- representative HLIL evidence for poller-base destruction, timer add/cancel,
  timer execution, timer-node creation, `i_poll_events` and `io_object_t`
  vtables, `io_object_t::plug`, read/write interest toggles, and selected
  session/stream/tcp call sites; and
- this round note as the evidence ledger.

## Inference Boundary

This pass intentionally leaves assertion-only `io_object_t` virtual failure
handlers unnamed. It also leaves the raw `select_t` fd-set reset helper near
`0x0040C1B0` for a later select-specific pass, because this round's evidence is
strongest at the `poller_base_t` / `io_object_t` owner layer.

## Verification

Local verification for this pass:

- `Get-Content -Raw references/analysis/quakelive_symbol_aliases.json | ConvertFrom-Json | Out-Null`
- `python -m pytest -q tests/test_platform_services.py::test_zmq_poller_base_io_object_round_377_aliases_are_pinned tests/test_platform_services.py::test_zmq_io_thread_reaper_object_command_round_376_aliases_are_pinned tests/test_platform_services.py::test_zmq_mailbox_select_signaler_round_370_aliases_are_pinned tests/test_platform_services.py::test_zmq_socket_base_and_msg_internal_aliases_round_374_are_pinned tests/test_platform_services.py::test_zmq_public_api_aliases_and_round_365_evidence_are_pinned`
  passed with `5 passed`.
- `python -m pytest -q tests/test_engine_cvar_retail_parity.py::test_engine_cvar_seventeenth_network_bootstrap_tranche_matches_retail_contracts tests/test_server_full_parity_gate.py::test_server_full_parity_gate_writes_status_artifact`
  passed with `2 passed`.

## Parity Estimate

- Focused ZMQ poller-base / io-object wiring mapping:
  **before 12% -> after 87%**.
- ZMQ-related source reconstruction confidence, including retained
  publication/RCON ownership, public wrappers, socket/message helpers,
  command-delivery support, queue backing-store evidence, object lifecycle
  ownership, and event-loop timer/fd-watch wiring:
  **before 84.9% -> after 85.3%**.
- Overall Quake Live source parity:
  **before 55.50% -> after 55.51%**.
