# Quake Live ZMQ/CZMQ Mapping Round 376

Date: 2026-06-06

Focus: recover the retained libzmq `io_thread_t`, `reaper_t`, and
`object_t` command lifecycle lane that sits between the round-370
mailbox/select/signaler mapping and the round-197 `own_t` /
`socket_base_t` command handlers.

## Retail Evidence

- Owning binary: `assets/quakelive/quakelive_steam.exe`.
- Canonical HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt`
  and the vtable lane in
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt`.
- Structured companion corpus:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`.
- Symbol/name support:
  `references/analysis/quakelive_symbol_aliases.json`.

Rounds 370, 371, and 374 named the command queue, signaler, public socket, and
message layers. This pass names the object lifecycle owners that create the
mailboxes, register them with the select poller, drain them through
`zmq_command_t_process`, and emit object commands back into the same queue.

## Alias Reconstruction

This pass added 25 aliases to
`references/analysis/quakelive_symbol_aliases.json`.

| Symbol | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_40CCC0` | `zmq_io_thread_t_ctor` | High | Builds the `io_thread_t` object and `i_poll_events` vtables, constructs an inline mailbox, allocates the select poller, registers the mailbox fd, and anchors to `src\io_thread.cpp`. |
| `sub_40CDE0` | `zmq_io_thread_t_scalar_deleting_dtor` | High | Scalar deleting destructor that delegates to the complete `io_thread_t` destructor and conditionally frees `this`. |
| `sub_40CE10` | `zmq_io_thread_t_dtor` | High | Restores `io_thread_t` vtables, destroys the poller, mailbox critical section, signaler, and command yqueue, then restores base vtables. |
| `sub_40CEC0` | `zmq_io_thread_t_in_event` | High | `i_poll_events` vtable slot drains commands from the mailbox through `zmq_mailbox_t_recv` and dispatches each command through `zmq_command_t_process`, with `io_thread.cpp` error anchors. |
| `sub_40D000` | `zmq_io_thread_t_process_stop` | High | `io_thread_t` object vtable slot 1 removes its mailbox fd from the select poller and marks the poller stop flag. |
| `sub_40D020` | `zmq_io_thread_t_i_poll_events_scalar_deleting_dtor` | High | Secondary `i_poll_events` vtable destructor thunk that adjusts `this` back to the enclosing `io_thread_t`. |
| `sub_40D030` | `zmq_reaper_t_ctor` | High | Builds the `reaper_t` object and `i_poll_events` vtables, constructs an inline mailbox, initializes socket-count and terminating flags, allocates/registers the select poller, and anchors to `src\reaper.cpp`. |
| `sub_40D160` | `zmq_reaper_t_scalar_deleting_dtor` | High | Scalar deleting destructor that delegates to the complete `reaper_t` destructor and conditionally frees `this`. |
| `sub_40D190` | `zmq_reaper_t_dtor` | High | Restores `reaper_t` vtables, destroys the poller, mailbox critical section, signaler, and command yqueue, then restores base vtables. |
| `sub_40D240` | `zmq_reaper_t_in_event` | High | `i_poll_events` vtable slot drains reaper mailbox commands through `zmq_mailbox_t_recv` and `zmq_command_t_process`, with `reaper.cpp` error anchors. |
| `sub_40D380` | `zmq_reaper_t_process_stop` | High | `reaper_t` object vtable slot 1 sets the terminating flag, sends the context `done` command when no sockets remain, removes its mailbox fd, and stops the poller. |
| `sub_40D410` | `zmq_reaper_t_process_reap` | High | `reaper_t` object vtable slot 14 calls `zmq_socket_base_t_start_reaping` with the select poller and increments the active socket count. |
| `sub_40D430` | `zmq_reaper_t_process_reaped` | High | `reaper_t` object vtable slot 15 decrements the active socket count and, when terminating reaches zero, sends the context `done` command and stops the poller. |
| `sub_40D4C0` | `zmq_reaper_t_i_poll_events_scalar_deleting_dtor` | High | Secondary `i_poll_events` vtable destructor thunk that adjusts `this` back to the enclosing `reaper_t`. |
| `sub_40D4D0` | `zmq_object_t_scalar_deleting_dtor` | High | `object_t` vtable destructor restores the base vtable and conditionally frees `this`. |
| `sub_40D500` | `zmq_object_t_dtor` | High | Complete base `object_t` destructor shape that restores the `object_t` vtable. |
| `sub_40D6C0` | `zmq_object_t_send_stop` | High | Builds the command opcode-0 stop message and sends it through the owning context command mailbox. |
| `sub_40D6E0` | `zmq_object_t_send_plug` | High | Increments the destination sequence counter, emits command opcode 1, writes to the target mailbox, and signals when the ypipe flush requires it. |
| `sub_40D760` | `zmq_object_t_send_own` | High | Increments the destination sequence counter, emits command opcode 2 with the owned object argument, and signals the target mailbox when needed. |
| `sub_40D7E0` | `zmq_object_t_send_bind` | High | Optionally increments the destination sequence counter, emits command opcode 4 with the pipe argument, and signals the target mailbox when needed. |
| `sub_40D860` | `zmq_object_t_send_activate_read` | High | Emits command opcode 5 into the target mailbox, matching the command dispatcher's activate-read vtable slot. |
| `sub_40D8C0` | `zmq_object_t_send_activate_write` | High | Emits command opcode 6 with both activation arguments into the target mailbox. |
| `sub_40D930` | `zmq_object_t_send_pipe_term` | High | Emits command opcode 8 into the target mailbox, matching the pipe termination dispatcher slot. |
| `sub_40D990` | `zmq_object_t_send_pipe_term_ack` | High | Emits command opcode 9 into the target mailbox, matching the pipe termination-ack dispatcher slot. |
| `sub_40D9F0` | `zmq_object_t_send_term_ack` | High | Emits command opcode `0xc` into the owner mailbox; round 197's `own_t::check_term_acks` calls this exact helper when final termination completes. |

## Observed Facts

- `ctx.cpp` constructs the recovered reaper with `sub_40D030`, stores its
  mailbox in the context slot array, and starts the select poller lane. The
  same context bootstrap loop constructs each `io_thread_t` with
  `sub_40CCC0`, stores each thread mailbox, and starts its select poller.
- The part-06 vtable dump gives a second, independent signal for the promoted
  process names: `io_thread_t` vtable slot 1 points at `sub_40D000`,
  `reaper_t` vtable slot 1 points at `sub_40D380`, slot 14 points at
  `sub_40D410`, and slot 15 points at `sub_40D430`.
- `io_thread_t::in_event` and `reaper_t::in_event` both use the round-370
  `zmq_mailbox_t_recv` and `zmq_command_t_process` path, so command delivery
  now has named owners on both the producer and consumer sides.
- The reaper stop/reaped helpers send `command_t::done` (`0x10`) back to the
  context mailbox only after active reaping socket count reaches zero. That
  matches the `ctx.cpp` shutdown wait that asserts `cmd.type ==
  command_t::done`.
- The object send helpers all share the same mailbox write pattern:
  locate the destination mailbox from the context mailbox vector, enter the
  mailbox critical section, enqueue a 16-byte command through the ypipe vtable,
  test the flush result, leave the critical section, and signal the mailbox
  through `zmq_signaler_t_send` when needed.
- The command opcode evidence lines up with the round-370 dispatcher: plug
  `1`, own `2`, bind `4`, activate-read `5`, activate-write `6`, pipe-term
  `8`, pipe-term-ack `9`, and term-ack `0xc`.

## Source Reconstruction

This is mapping/static reconstruction only. No engine C source changed in this
pass. The recovered names clarify that the retained ZMQ runtime is ordinary
bundled libzmq lifecycle code, while the reconstructed Quake-facing source
continues to use the direct-libzmq fallback in `src/code/server/sv_zmq.c`
instead of recreating these private C++ classes.

The static parity guard in `tests/test_platform_services.py` pins:

- all aliases promoted in this round;
- the matching Ghidra `functions.csv` rows;
- representative HLIL evidence for constructor/destructor wiring, vtable slot
  ownership, command-pump dispatch, reaper stop/reap/reaped behavior, object
  command sends, mailbox locking/signaling, and context bootstrap/shutdown
  ownership; and
- this round note as the evidence ledger.

## Inference Boundary

This pass intentionally leaves the shared assertion thunks and base virtual
failure handlers unnamed. They are reused by several ZMQ classes and should not
be promoted as class-specific behavior without a separate vtable-wide audit.
It also does not claim live-service behavior: this is bundled libzmq plumbing,
not Quake Live online-service replacement work.

## Verification

Local verification for this pass:

- `Get-Content -Raw references/analysis/quakelive_symbol_aliases.json | ConvertFrom-Json | Out-Null`
- `python -m pytest -q tests/test_platform_services.py::test_zmq_io_thread_reaper_object_command_round_376_aliases_are_pinned tests/test_platform_services.py::test_zmq_ypipe_yqueue_round_371_aliases_are_pinned tests/test_platform_services.py::test_zmq_mailbox_select_signaler_round_370_aliases_are_pinned tests/test_platform_services.py::test_zmq_socket_base_and_msg_internal_aliases_round_374_are_pinned tests/test_platform_services.py::test_zmq_public_api_aliases_and_round_365_evidence_are_pinned`
  passed with `5 passed`.
- `python -m pytest -q tests/test_engine_cvar_retail_parity.py::test_engine_cvar_seventeenth_network_bootstrap_tranche_matches_retail_contracts tests/test_server_full_parity_gate.py::test_server_full_parity_gate_writes_status_artifact`
  passed with `2 passed`.

## Parity Estimate

- Focused ZMQ `io_thread_t`/`reaper_t`/`object_t` command lifecycle mapping:
  **before 16% -> after 88%**.
- ZMQ-related source reconstruction confidence, including retained
  publication/RCON ownership, public wrappers, socket/message helpers,
  command-delivery support, queue backing-store evidence, and object lifecycle
  ownership:
  **before 84.3% -> after 84.9%**.
- Overall Quake Live source parity:
  **before 55.49% -> after 55.50%**.
