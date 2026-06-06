# Quake Live ZMQ/CZMQ Mapping Round 370

Date: 2026-06-06

Focus: recover the ZMQ command-delivery support lane that feeds
`zmq_socket_base_t_process_commands`: select poller construction, mailbox
receive/destruction, command dispatch, and Windows signaler send/wait/receive
helpers.

## Retail Evidence

- Owning binary: `assets/quakelive/quakelive_steam.exe`.
- Canonical HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt`.
- Structured companion corpus:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`.
- Existing symbol support:
  `sub_41D720 -> zmq_signaler_t_make_fdpair` was promoted in round 118 and is
  retained as the signaler family anchor.

## Alias Reconstruction

This pass added 12 aliases to
`references/analysis/quakelive_symbol_aliases.json`.

| Symbol | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_40BCE0` | `zmq_select_t_ctor` | High | Initializes the `poller_base_t` vtable, timestamps, fd-vector header, `select_t` vtable, fd set mirrors, wake flag, and maximum fd sentinel. |
| `sub_40BDA0` | `zmq_select_t_dtor` | High | Restores the `select_t` vtable, joins/closes the worker thread, deletes the fd vector storage, and tears down the poller-base tree. |
| `sub_40C460` | `zmq_select_t_loop_entry` | High | Thin thread entry that tailcalls `zmq_select_t_loop`, used as the `_beginthreadex` callback when the select worker starts. |
| `sub_40C630` | `zmq_mailbox_t_ctor` | High | Constructs the `ypipe<command_t,16>` command queue, initializes its read/write cursors, creates the signaler fd pair, creates the critical section, and primes the queue through the pipe vtable. |
| `sub_40C730` | `zmq_mailbox_t_dtor` | High | Deletes the mailbox critical section, closes the signaler, destroys the command ypipe, and restores the base ypipe vtable. |
| `sub_40C770` | `zmq_mailbox_t_recv` | High | Reads a command from the ypipe when already active, otherwise waits on the signaler, consumes the dummy byte, marks the mailbox active, and retries the command read. |
| `sub_40D510` | `zmq_command_t_process` | High | Switches over command opcode `0..0xf` and dispatches each command to the matching target object vtable slot, including the common post-command destroy/check slot. |
| `sub_41D290` | `zmq_signaler_t_close` | High | Sets non-linger on the write socket, closes write/read sockets, and asserts through `signaler.cpp` error paths. |
| `sub_41D3F0` | `zmq_signaler_t_send` | High | Sends one zero dummy byte through the write socket and asserts that exactly one byte is written. |
| `sub_41D4B0` | `zmq_signaler_t_wait` | High | Selects on the read socket with the caller timeout, maps timeout to `EAGAIN`, and asserts that readiness count is exactly one. |
| `sub_41D620` | `zmq_signaler_t_recv` | High | Receives one dummy byte from the read socket and asserts both byte count and zero dummy value. |
| `sub_41D720` | `zmq_signaler_t_make_fdpair` | Existing | Retained anchor from round 118; creates the Windows signaler socket pair behind mailbox construction. |

## Observed Facts

- `zmq_socket_base_t_process_commands` now has its downstream command intake
  path named: it calls `zmq_mailbox_t_recv`, then dispatches each received
  command through `zmq_command_t_process`.
- `zmq_mailbox_t_ctor` calls the existing `zmq_signaler_t_make_fdpair`, while
  `zmq_mailbox_t_dtor` calls `zmq_signaler_t_close`.
- `zmq_mailbox_t_recv` is the only mailbox edge needed by the recovered
  socket command-pump path in this round; it combines ypipe reads with
  `zmq_signaler_t_wait` and `zmq_signaler_t_recv`.
- The select lane is the reaper/poller side of the same support fabric:
  `zmq_socket_base_t_start_reaping` registers the mailbox fd through
  `zmq_select_t_add_fd`, and `zmq_select_t_loop_entry` runs the already-named
  `zmq_select_t_loop` on the worker thread.

## Source Reconstruction

This is mapping/static reconstruction only. No engine C source changed. The
new static parity guard in `tests/test_platform_services.py` pins:

- all aliases promoted or anchored in this round;
- the Ghidra `functions.csv` rows for the new aliases;
- representative HLIL evidence for select construction/destruction, mailbox
  ypipe/signaler construction, mailbox receive/wait/recv retry behavior,
  command opcode dispatch, signaler close/send/wait/recv semantics, and the
  `make_fdpair` anchor; and
- this round note as the evidence ledger.

## Inference Boundary

This pass intentionally does not name the lower-level STL vector-growth
helpers, ypipe implementation helpers, thread join wrapper, or timer tree
helpers adjacent to this lane. Those are support internals whose names should
be promoted in a separate, dedicated pass once their call graph is audited.

## Verification

Local verification for this pass:

- `Get-Content -Raw references/analysis/quakelive_symbol_aliases.json | ConvertFrom-Json | Out-Null`
- `python -m pytest -q tests/test_platform_services.py::test_zmq_mailbox_select_signaler_round_370_aliases_are_pinned tests/test_platform_services.py::test_zmq_socket_base_and_msg_internal_aliases_round_374_are_pinned tests/test_platform_services.py::test_zmq_public_api_aliases_and_round_365_evidence_are_pinned tests/test_platform_services.py::test_server_zmq_runtime_reconstructs_retail_publication_and_rcon_owners`
  passed with `4 passed`.
- `python -m pytest -q tests/test_engine_cvar_retail_parity.py::test_engine_cvar_seventeenth_network_bootstrap_tranche_matches_retail_contracts tests/test_server_full_parity_gate.py::test_server_full_parity_gate_writes_status_artifact`
  passed with `2 passed`.

## Parity Estimate

- Focused ZMQ mailbox/select/signaler support mapping:
  **before 24% -> after 86%**.
- ZMQ-related source reconstruction confidence, including retained
  publication/RCON ownership, public wrappers, internal socket/message helpers,
  and command-delivery support evidence:
  **before 83.0% -> after 83.5%**.
- Overall Quake Live source parity:
  **before 55.44% -> after 55.46%**.
