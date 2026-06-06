# Quake Live ZMQ/CZMQ Mapping Round 371

Date: 2026-06-06

Focus: recover the `ypipe<command_t,16>` and `yqueue<command_t,16>` helpers
that back the ZMQ mailbox command queue named in round 370.

## Retail Evidence

- Owning binary: `assets/quakelive/quakelive_steam.exe`.
- Canonical HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt`.
- Structured companion corpus:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`.
- Symbol/name support:
  `references/analysis/quakelive_symbol_aliases.json`.

Round 370 named `zmq_mailbox_t_ctor`, `zmq_mailbox_t_dtor`, and
`zmq_mailbox_t_recv`. This pass names the queue implementation those mailbox
helpers construct and consume.

## Alias Reconstruction

This pass added 12 aliases to
`references/analysis/quakelive_symbol_aliases.json`.

| Symbol | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_40C880` | `zmq_ypipe_t_dtor` | High | Restores the `ypipe_t<command_t,16>` vtable, destroys the backing yqueue, then restores the `ypipe_base_t` vtable. |
| `sub_40C8A0` | `zmq_ypipe_t_write` | High | Copies a 16-byte `command_t` into the current write slot, advances the yqueue write cursor, and updates the flush boundary when the write is complete. |
| `sub_40C8F0` | `zmq_ypipe_t_unwrite` | High | Refuses to unwrite past the flush boundary, steps the yqueue write cursor back, copies the last command into the caller buffer, and returns success. |
| `sub_40C940` | `zmq_ypipe_t_flush` | High | Publishes the flush boundary through an interlocked compare/exchange and reports whether the reader needs a signal. |
| `sub_40C980` | `zmq_ypipe_t_read` | High | Checks read availability, copies the current 16-byte command, advances the read cursor, and frees recycled chunks after crossing a 16-command page. |
| `sub_40C9F0` | `zmq_ypipe_t_probe` | High | Checks read availability and applies a caller predicate to the current command slot. |
| `sub_40CA60` | `zmq_ypipe_t_scalar_deleting_dtor` | High | Scalar deleting destructor for `ypipe_t<command_t,16>`, restoring the vtable, destroying the yqueue, and conditionally deleting `this`. |
| `sub_40CAA0` | `zmq_ypipe_base_t_scalar_deleting_dtor` | High | Scalar deleting destructor for the base `ypipe_base_t<command_t,16>` vtable. |
| `sub_40CAD0` | `zmq_yqueue_t_ctor` | High | Allocates the first `0x108`-byte chunk, initializes read/write chunk pointers and offsets, and leaves spare chunk storage empty. |
| `sub_40CB40` | `zmq_yqueue_t_dtor` | High | Frees each linked chunk from read to write, frees the current write chunk, and frees any interlocked spare chunk. |
| `sub_40CB90` | `zmq_yqueue_t_push` | High | Advances the write offset, allocates or reuses the next `0x108`-byte chunk when the 16-command page fills, links chunks, and resets the write offset. |
| `sub_40CC60` | `zmq_yqueue_t_unpush` | High | Moves the write cursor backward, walks to the previous chunk when needed, and frees the chunk beyond the new write position. |

## Observed Facts

- `zmq_mailbox_t_ctor` constructs a `ypipe_t<command_t,16>` inline by calling
  the recovered `zmq_yqueue_t_ctor`, then immediately advances the yqueue once
  so the read/write/flush pointers share the expected initial slot.
- `zmq_mailbox_t_recv` reaches `ypipe_t::read` through the mailbox vtable,
  only waiting on the signaler when the ypipe read path reports no active
  command.
- The queue storage uses `0x108`-byte chunks, i.e. 0x108-byte chunks:
  `0x100` bytes for 16 commands of
  16 bytes each, plus two link pointers at the end of the chunk.
- The `ypipe_t::flush` helper is the synchronization boundary between writers
  and readers; the compare/exchange result decides whether the writer must
  signal the mailbox.

## Source Reconstruction

This is mapping/static reconstruction only. No engine C source changed. The
new static parity guard in `tests/test_platform_services.py` pins:

- all aliases promoted in this round;
- the matching Ghidra `functions.csv` rows;
- representative HLIL evidence for ypipe write/unwrite/flush/read/probe,
  yqueue chunk allocation/destruction/push/unpush, and mailbox construction
  links into the recovered queue; and
- this round note as the evidence ledger.

## Inference Boundary

This pass does not name generic STL/vector helpers, thread wrappers, or the
remaining I/O-thread object lifecycle functions near this corridor. It also
does not claim game-owned behavior: these helpers are bundled libzmq command
queue mechanics used by the retained `idZMQ` runtime only through the public
and CZMQ-facing surfaces mapped in earlier rounds.

## Verification

Local verification for this pass:

- `Get-Content -Raw references/analysis/quakelive_symbol_aliases.json | ConvertFrom-Json | Out-Null`
- `python -m pytest -q tests/test_platform_services.py::test_zmq_ypipe_yqueue_round_371_aliases_are_pinned tests/test_platform_services.py::test_zmq_mailbox_select_signaler_round_370_aliases_are_pinned tests/test_platform_services.py::test_zmq_socket_base_and_msg_internal_aliases_round_374_are_pinned tests/test_platform_services.py::test_zmq_public_api_aliases_and_round_365_evidence_are_pinned`
  passed with `4 passed`.
- `python -m pytest -q tests/test_engine_cvar_retail_parity.py::test_engine_cvar_seventeenth_network_bootstrap_tranche_matches_retail_contracts tests/test_server_full_parity_gate.py::test_server_full_parity_gate_writes_status_artifact`
  passed with `2 passed`.

## Parity Estimate

- Focused ZMQ ypipe/yqueue command-queue mapping:
  **before 10% -> after 90%**.
- ZMQ-related source reconstruction confidence, including retained
  publication/RCON ownership, public wrappers, socket/message helpers,
  command-delivery support, and queue backing-store evidence:
  **before 83.5% -> after 84.0%**.
- Overall Quake Live source parity:
  **before 55.46% -> after 55.48%**.
