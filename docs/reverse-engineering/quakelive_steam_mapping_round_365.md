# Quake Live ZMQ/CZMQ Mapping Round 365

Date: 2026-06-06

Focus: recover the anonymous public ZeroMQ `zmq.cpp` wrapper strip and the
adjacent context/Z85 helpers that feed the retained CZMQ and `idZMQ` wiring.

## Retail Evidence

- Owning binary: `assets/quakelive/quakelive_steam.exe`.
- Canonical HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt`.
- Structured companion corpus:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`.
- Symbol/name support:
  `references/analysis/quakelive_symbol_aliases.json`.

The recovered lane is centered on `0x00401000..0x004015F0`, followed by
`zmq_poll` at `0x00401600` and the Z85 encode/decode helpers at
`0x00401B70..0x00401C10`.

## Alias Reconstruction

This pass added 23 aliases to
`references/analysis/quakelive_symbol_aliases.json`.

| Symbol | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_401000` | `zmq_ctx_new` | High | Calls `WSAStartup(0x0202)`, validates Winsock 2.2, allocates the 0x10c-byte context, and stamps the `0xabadcafe` context magic before returning the new context. |
| `sub_401140` | `zmq_ctx_term` | High | Validates the `0xabadcafe` context magic, calls the internal `zmq_ctx_t_term`, preserves errno around termination, and performs the paired `WSACleanup`. |
| `sub_401200` | `zmq_ctx_set` | High | Public context wrapper that validates the context magic and forwards `(option, context, value)` into the internal setter. |
| `sub_401240` | `zmq_init` | High | Legacy compatibility wrapper: rejects negative I/O-thread counts, calls `zmq_ctx_new`, then writes the context I/O-thread field under the context lock. |
| `sub_4012B0` | `zmq_term` | High | Thin legacy compatibility tailcall into the context termination wrapper. |
| `sub_4012C0` | `zmq_socket` | High | Validates the context magic, stages the requested socket type, and dispatches to `zmq_ctx_t_create_socket`. |
| `sub_4012F0` | `zmq_close` | High | Validates socket magic `0xbaddecaf`, marks the socket dead with `0xdeadbeef`, and sends the terminate command through the owning context/thread lane. |
| `sub_401390` | `zmq_setsockopt` | High | Validates socket magic and dispatches directly to `zmq_socket_base_t_setsockopt`. |
| `sub_4013D0` | `zmq_getsockopt` | High | Validates socket magic and dispatches directly to `zmq_socket_base_t_getsockopt`. |
| `sub_401410` | `zmq_bind` | High | Validates socket magic and dispatches endpoint text to `zmq_socket_base_t_bind`; CZMQ `zsock_bind` reaches this wrapper. |
| `sub_401450` | `zmq_connect` | High | Validates socket magic and dispatches endpoint text to `zmq_socket_base_t_connect`; CZMQ `zsock_connect` reaches this wrapper. |
| `sub_401490` | `zmq_unbind` | High | Validates socket magic and dispatches endpoint termination to `zmq_socket_base_t_term_endpoint`; CZMQ `zsock_unbind` reaches this wrapper. |
| `sub_4014D0` | `zmq_msg_send` | High | Validates socket magic, sends a `zmq_msg_t` through the socket-base send lane, and returns the message size on success. |
| `sub_401520` | `zmq_msg_recv` | High | Validates socket magic, receives into a `zmq_msg_t`, and returns the message size on success. |
| `sub_401570` | `zmq_msg_init` | High | Initializes the small message header state directly and returns success. |
| `sub_401590` | `zmq_msg_init_size` | High | Thin wrapper over the internal message-size initializer. |
| `sub_4015B0` | `zmq_msg_close` | High | Thin wrapper over the internal message close helper. |
| `sub_4015C0` | `zmq_msg_copy` | High | Thin wrapper over the internal message copy helper. |
| `sub_4015E0` | `zmq_msg_data` | High | Thin wrapper over the internal message data accessor. |
| `sub_4015F0` | `zmq_msg_size` | High | Thin wrapper over the internal message size accessor. |
| `sub_401B70` | `zmq_z85_encode` | High | Converts four-byte groups into five glyphs using divisor `0x55` and the Z85 alphabet, rejects non-multiple-of-four input lengths, and null-terminates the output string. |
| `sub_401C10` | `zmq_z85_decode` | High | Rejects strings whose length is not divisible by five, folds five Z85 glyphs into a 32-bit value, and writes the four decoded bytes. |
| `sub_402BA0` | `zmq_ctx_t_set` | High | Internal context setter for options `1`, `2`, and `0x2a`; writes the I/O-thread count, max socket count, and boolean context flag under the context lock. |

## Observed Facts

- The public wrapper strip from `0x00401000..0x004015F0` now has stable
  ZeroMQ API names in the alias artifact instead of only the already-promoted
  `zmq_poll` tail.
- `zsys_init` reaches the legacy `zmq_init` wrapper and immediately calls the
  recovered `zmq_ctx_set` wrapper with option `2`, matching the retained CZMQ
  context-configuration flow.
- `zsock_bind`, `zsock_connect`, and `zsock_unbind` corroborate the endpoint
  wrapper trio through their direct callsites.
- `zstr` and `zframe` message movement call into the recovered message
  send/receive/init/data/size/copy/close wrapper family.
- The Z85 helper lane is corroborated by `zcert_new` and `zcert_load`: the
  encoder writes public/secret key text from 32-byte raw keys, while the
  decoder consumes 40-character config key strings back into binary key
  buffers.

## Source Reconstruction

This is primarily a mapping pass. No engine C source changed in this round.
The reconstruction artifact is a focused static parity guard in
`tests/test_platform_services.py` that pins:

- all promoted aliases from this round;
- the matching Ghidra `functions.csv` rows;
- the representative HLIL evidence for context magic, socket magic,
  `zmq_ctx_t_set`, and Z85 encode/decode mechanics; and
- this mapping note as the evidence ledger.

## Inference Boundary

The names above are limited to the observed static wrapper lane and CZMQ
callsite evidence. This pass does not claim complete bundled libzmq naming,
does not enable live online services, and does not reconstruct live
ZAP/CURVE/auth actor behavior beyond the key encode/decode helper ownership.

One remaining naming wrinkle is that the retail binary exposes the endpoint
termination wrapper through the observed `zsock_unbind` path. If a later pass
finds a separate CZMQ `disconnect` callsite sharing the same wrapper, the
source-facing note should record that as a shared `term_endpoint` public
compatibility edge rather than split the current alias prematurely.

## Verification

Local verification for this pass:

- `Get-Content -Raw references/analysis/quakelive_symbol_aliases.json | ConvertFrom-Json | Out-Null`
- `python -m pytest -q tests/test_platform_services.py::test_zmq_public_api_aliases_and_round_365_evidence_are_pinned tests/test_platform_services.py::test_server_zmq_runtime_reconstructs_retail_publication_and_rcon_owners tests/test_engine_cvar_retail_parity.py::test_engine_cvar_seventeenth_network_bootstrap_tranche_matches_retail_contracts tests/test_server_full_parity_gate.py::test_server_full_parity_gate_writes_status_artifact`
  passed with `4 passed`.

## Parity Estimate

- Focused `zmq.cpp` public API wrapper mapping:
  **before 6% -> after 96%**.
- ZMQ-related source reconstruction confidence, including retained
  publication/RCON ownership and static wrapper evidence:
  **before 82% -> after 82.5%**.
- Overall Quake Live source parity:
  **before 55.40% -> after 55.42%**.
