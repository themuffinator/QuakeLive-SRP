# Quake Live ZMQ/CZMQ Mapping Round 369

Date: 2026-06-06

Focus: recover the internal `zmq::socket_base_t` send/receive command-pump
lane and the adjacent `zmq::msg_t` payload helpers used by the retained
Windows ZMQ runtime bundled in `quakelive_steam.exe`.

## Retail Evidence

- Owning binary: `assets/quakelive/quakelive_steam.exe`.
- Canonical HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt`.
- Structured companion corpus:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`.
- Symbol/name support:
  `references/analysis/quakelive_symbol_aliases.json`.

The HLIL preserves source-path strings for both owners:

- `..\..\..\src\socket_base.cpp`
- `..\..\..\src\msg.cpp`

Those source paths, the surrounding call graph, and repeated message layout
accesses are enough to promote the following high-confidence aliases.

## Alias Reconstruction

| Symbol | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_409160` | `zmq_socket_base_t_send` | High | Sends a prepared `msg_t`, drains command messages when the socket reports `EAGAIN`, and is reached by the CZMQ/pub-server publication lane. |
| `sub_4092D0` | `zmq_socket_base_t_recv` | High | Receives into a caller `msg_t`, retries command processing on transient `EAGAIN`, and mirrors the retained socket-base receive path. |
| `sub_4094A0` | `zmq_socket_base_t_start_reaping` | High | Registers the socket mailbox fd with the reaper/poller and marks the socket for reaping. |
| `sub_409510` | `zmq_socket_base_t_process_commands` | High | Pulls pending mailbox commands, dispatches them, handles timeout/interruption state, and is called by both send and receive retry loops. |
| `sub_409D10` | `zmq_socket_base_t_monitor_event` | High | Builds monitor event messages and publishes them through the socket-base send helper. |
| `sub_40B480` | `zmq_msg_t_check` | High | Validates retained `msg_t` type bytes before data/size/reference operations. |
| `sub_40B4A0` | `zmq_msg_t_init_size` | High | Allocates the large-message backing store with `malloc(arg2 + 0x14)` and initializes inline/small-message metadata. |
| `sub_40B520` | `zmq_msg_t_close` | High | Drops retained message references through `InterlockedExchangeAdd`, freeing large-message storage when the final reference is released. |
| `sub_40B580` | `zmq_msg_t_move` | High | Moves a message body into the destination and resets the source type to the empty-message marker. |
| `sub_40B5E0` | `zmq_msg_t_copy` | High | Copies message metadata and bumps large-message references when needed. |
| `sub_40B660` | `zmq_msg_t_data` | High | Returns the active data pointer for small, large, delimiter, and command-message representations. |
| `sub_40B740` | `zmq_msg_t_size` | High | Returns the active payload size from the same retained `msg_t` representation family. |
| `sub_40B820` | `zmq_msg_t_add_refs` | High | Adds caller-requested references to the retained shared large-message storage. |
| `sub_40B8A0` | `zmq_msg_t_rm_refs` | High | Removes caller-requested references and reports when the final shared reference is gone. |

## Observed Facts

- `zmq_socket_base_t_send` reaches `zmq_socket_base_t_process_commands` when
  the lower socket send vtable returns a retryable result.
- `zmq_socket_base_t_recv` uses the same process-command helper from its
  receive retry loop.
- `zmq_socket_base_t_start_reaping` ties this internal socket lane to the
  mailbox/select support later mapped in round 370.
- `zmq_socket_base_t_monitor_event` constructs monitor messages and sends
  them through the recovered send helper, so the message helpers and socket
  helpers form one ownership corridor.
- `0x0040B480` starts the retained message helper cluster. The type checks,
  `0x65..0x68` message byte family, large-message allocation, and interlocked
  reference updates all match libzmq `msg_t` internals rather than game-owned
  message structures.

## Source Reconstruction

This is mapping/static reconstruction only. No engine C source changed. The
static parity guard pins:

- all aliases promoted in this round;
- the Ghidra `functions.csv` rows for the aliases;
- representative HLIL evidence for socket send/receive retry behavior,
  process-command polling, monitor event publication, message type checks,
  large-message allocation, move/copy/data/size helpers, and reference-count
  adjustment; and
- this round note as the evidence ledger.

It intentionally leaves nearby assertion thunks, allocator wrappers,
std::string helpers, and lower poller internals unnamed until their own focused
passes can separate generic library support from owner-specific behavior.

## Verification

Local verification for this pass:

- `Get-Content -Raw references/analysis/quakelive_symbol_aliases.json | ConvertFrom-Json | Out-Null`
- `python -m pytest -q tests/test_platform_services.py::test_zmq_socket_base_and_msg_internal_aliases_round_369_are_pinned tests/test_platform_services.py::test_zmq_public_api_aliases_and_round_365_evidence_are_pinned tests/test_platform_services.py::test_server_zmq_runtime_reconstructs_retail_publication_and_rcon_owners`

## Parity Estimate

- Focused ZMQ socket-base/message-helper mapping:
  **before 18% -> after 84%**.
- ZMQ-related source reconstruction confidence, including retained
  publication/RCON ownership and public wrapper evidence:
  **before 82.0% -> after 83.0%**.
- Overall Quake Live source parity:
  **before 55.42% -> after 55.44%**.
