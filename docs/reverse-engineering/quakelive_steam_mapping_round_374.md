# Quake Live ZMQ/CZMQ Mapping Round 374

Date: 2026-06-06

Focus: recover the internal `socket_base_t` send/receive command pump and the
`msg_t` storage/refcount helpers that sit beneath the public ZMQ wrappers named
in round 365.

## Retail Evidence

- Owning binary: `assets/quakelive/quakelive_steam.exe`.
- Canonical HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt`.
- Structured companion corpus:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`.
- Symbol/name support:
  `references/analysis/quakelive_symbol_aliases.json`.

Round 365 promoted the public `zmq_*` wrapper lane at
`0x00401000..0x004015F0`. This pass names the object and message helpers those
wrappers tail-call once they validate the retained libzmq magic fields.

## Alias Reconstruction

This pass added 14 aliases to
`references/analysis/quakelive_symbol_aliases.json`.

| Symbol | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_409160` | `zmq_socket_base_t_send` | High | `src\socket_base.cpp` lane validates the `msg_t` type byte, drains commands through `sub_409510`, calls the socket vtable send slot, and handles `EAGAIN` retry/wait behavior. |
| `sub_4092D0` | `zmq_socket_base_t_recv` | High | Validates message storage, periodically pumps commands, calls the socket vtable receive slot, and follows the blocking/non-blocking `EAGAIN` path. |
| `sub_4094A0` | `zmq_socket_base_t_start_reaping` | High | Bridges socket shutdown into the reaper/poller corridor later tied to the round-370 select/mailbox mapping. |
| `sub_409510` | `zmq_socket_base_t_process_commands` | High | Pulls commands from the mailbox at object offset `0x2b0`, dispatches each through `sub_40D510`, asserts only `EAGAIN` is terminal, and honors the terminated flag. |
| `sub_409D10` | `zmq_socket_base_t_monitor_event` | High | Builds monitor event messages with `msg_t` helpers, sends event code/value and payload through `zmq_socket_base_t_send`, and exits when no monitor socket is installed. |
| `sub_40B480` | `zmq_msg_t_check` | High | Accepts only the retained `msg_t` discriminator range `0x65..0x68`. |
| `sub_40B4A0` | `zmq_msg_t_init_size` | High | Selects inline storage for messages up to `0x1d`, otherwise allocates `size + 0x14` and initializes large-message metadata. |
| `sub_40B520` | `zmq_msg_t_close` | High | Validates the discriminator, releases large-message storage when the shared refcount reaches zero, and clears the type byte. |
| `sub_40B580` | `zmq_msg_t_move` | High | Closes the destination, copies the source message record, and resets the source to the empty inline message type. |
| `sub_40B5E0` | `zmq_msg_t_copy` | High | Closes the destination, copies the source record, and increments/promotes large-message refcounts. |
| `sub_40B660` | `zmq_msg_t_data` | High | Asserts `msg_t::check`, returns inline data for small messages, dereferences large-message storage, and handles constant-buffer messages. |
| `sub_40B740` | `zmq_msg_t_size` | High | Asserts `msg_t::check` and returns the size from the matching inline, large, or constant-buffer representation. |
| `sub_40B820` | `zmq_msg_t_add_refs` | High | Asserts non-negative refs and promotes/increments the shared large-message refcount when present. |
| `sub_40B8A0` | `zmq_msg_t_rm_refs` | High | Asserts non-negative refs, subtracts shared refs atomically, releases storage at zero, or closes non-shared messages directly. |

## Observed Facts

- The public wrappers from round 365 call into this lane directly:
  `zmq_msg_send` reaches `zmq_msg_t_size` and `zmq_socket_base_t_send`, while
  `zmq_msg_recv` reaches `zmq_socket_base_t_recv`.
- The `socket_base_t` send/receive helpers are not Quake Live service code.
  Their HLIL source paths identify `..\..\..\src\socket_base.cpp`, and their
  behavior matches libzmq's command-pump, timeout, terminated-state, and
  vtable-dispatched pipe operations.
- `zmq_socket_base_t_process_commands` is the upstream owner of the round-370
  mailbox and command dispatcher evidence: it calls `zmq_mailbox_t_recv` at
  offset `0x2b0`, then dispatches each received command through
  `zmq_command_t_process`.
- `zmq_socket_base_t_monitor_event` proves the retained monitor path is built
  out of two ordinary `msg_t` sends: the event header and the attached endpoint
  or payload bytes.
- The `msg_t` helper block begins at the `0x0040B480` check helper and matches
  the expected small/large/constant-message storage model, including the
  `0x65..0x68` discriminator check, inline size byte, large-message
  allocation, destructor callback, and atomic reference updates.

## Source Reconstruction

This is mapping/static reconstruction only. No engine C source changed in this
pass. The static parity guard in `tests/test_platform_services.py` pins:

- all aliases promoted in this round;
- the matching Ghidra `functions.csv` rows;
- representative HLIL evidence for public wrapper calls into socket/message
  internals, send/receive command pumping, monitor-event publication, message
  allocation/close/move/copy/data/size/refcount behavior, and source path
  anchors; and
- this round note as the evidence ledger.

## Inference Boundary

It intentionally leaves nearby assertion thunks, pipe internals, lower-level
clock helpers, and object lifecycle functions unnamed. Rounds 370 and 371 cover
the mailbox/signaler and ypipe/yqueue command-delivery corridor downstream of
`zmq_socket_base_t_process_commands`; this pass only claims the socket base and
message storage layer.

## Verification

Local verification for this pass:

- `Get-Content -Raw references/analysis/quakelive_symbol_aliases.json | ConvertFrom-Json | Out-Null`
- `python -m pytest -q tests/test_platform_services.py::test_zmq_socket_base_and_msg_internal_aliases_round_374_are_pinned tests/test_platform_services.py::test_zmq_public_api_aliases_and_round_365_evidence_are_pinned`
  passed with `2 passed`.

## Parity Estimate

- Focused ZMQ socket/message internal mapping:
  **before 18% -> after 88%**.
- ZMQ-related source reconstruction confidence, including retained
  publication/RCON ownership, public wrappers, internal socket/message helpers,
  command-delivery support, and queue backing-store evidence:
  **before 84.0% -> after 84.3%**.
- Overall Quake Live source parity:
  **before 55.48% -> after 55.49%**.
