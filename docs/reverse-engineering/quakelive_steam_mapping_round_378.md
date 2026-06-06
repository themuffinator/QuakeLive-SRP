# Quake Live ZMQ/CZMQ Mapping Round 378

Date: 2026-06-06

Focus: recover the retained libzmq option-default wiring around
`options_t`, the TCP address-mask vector helpers used by the socket option
switches, and the default-options `own_t` constructor/destructor path that
embeds those options in owner classes.

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

Earlier ZMQ rounds named the public API wrappers, socket/message internals,
command/object ownership, and event-loop poller wiring. This pass stays one
layer lower than socket behavior and names the option storage helpers that the
already-promoted `zmq_options_t_setsockopt` and
`zmq_options_t_getsockopt` switches consume.

## Alias Reconstruction

This pass added 10 aliases to
`references/analysis/quakelive_symbol_aliases.json`.

| Symbol | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_40DF50` | `zmq_options_t_ctor` | High | Initializes the full `options_t` layout: HWM defaults, affinity/identity zeroing, rate/recovery/multicast defaults, `-1` timeout/fd slots, empty address-mask vector, short-string capacities, and trailing zeroed storage. |
| `sub_40EB00` | `std_string_ctor_assign_zmq_option_bytes` | High | Builds the temporary short-string buffer for byte-valued option payloads, sets capacity `0xf`, clears length/data, and delegates to the string assign helper. |
| `sub_40EB20` | `std_vector_zmq_tcp_address_mask_push_back` | High | Copies a resolved `tcp_address_mask_t` into the vector, grows when begin/end/capacity collide, lays down the `tcp_address_t` then derived mask vtables, and advances by `0x24` bytes. |
| `sub_40EBF0` | `std_vector_zmq_tcp_address_mask_erase_range` | High | Erases a range from the address-mask vector by moving the tail down, destroying removed mask elements through their vtables, and updating the vector end pointer. |
| `sub_40EC60` | `std_vector_zmq_tcp_address_mask_grow` | High | Computes current size/capacity using the `0x24` element stride, checks the vector max count, and picks the next reserve size. |
| `sub_40ECE0` | `std_vector_zmq_tcp_address_mask_reserve` | High | Allocates new mask storage, uninitialized-copies existing elements, destroys old elements, frees old storage, and rewrites begin/end/capacity. |
| `sub_40EE00` | `std_uninitialized_move_zmq_tcp_address_mask` | High | Moves raw `tcp_address_mask_t` element payloads in `0x24`-byte steps for erase-range compaction. |
| `sub_40EE50` | `std_uninitialized_copy_zmq_tcp_address_mask` | High | Copies mask elements into uninitialized storage while restoring the base `tcp_address_t` and derived `tcp_address_mask_t` vtables. |
| `sub_40EEB0` | `zmq_own_t_default_options_ctor` | High | Constructs `own_t` from an owner/thread id path, installs the `own_t` vtable, invokes the default `options_t` constructor at `this + 4`, and initializes sequence/owned-tree bookkeeping. |
| `sub_40EFB0` | `zmq_own_t_scalar_deleting_dtor` | High | Vtable slot 0 for `own_t`; erases the owned tree, deletes the sentinel, destroys embedded options, restores the base `object_t` vtable, and conditionally frees `this`. |

## Observed Facts

- `zmq_options_t_ctor` sets send and receive HWM to `1000`, clears affinity
  and identity state, sets rate to `100`, recovery interval to `10000`,
  multicast hops to `1`, leaves many timeout/fd-related fields at `-1`, and
  creates empty short-string/vector storage.
- The existing `setsockopt` switch already stores identity, high-water marks,
  linger/reconnect fields, IPv6/boolean toggles, ZAP strings, and address-mask
  data. This pass names the helper layer behind the default values and
  address-mask storage rather than changing those switch aliases.
- The address-mask option path constructs a temporary string, resolves it via
  the `tcp_address_mask_t` vtable path and `sub_4124E0`, then stores the
  resolved mask through the newly named vector `push_back` helper.
- Passing a null address-mask payload with a null pointer clears the existing
  vector by calling the newly named erase-range helper with begin/end.
- The default-options `own_t` constructor differs from the already named
  `zmq_own_t_ctor` at `sub_40F050`: `sub_40F050` copies caller-provided
  options, while `sub_40EEB0` constructs the embedded options from defaults.
- The `own_t` vtable in HLIL part 06 points slot 0 at `sub_40EFB0`, confirming
  that this is the scalar deleting destructor wrapper around the complete
  destructor behavior already represented by `sub_40F150`.

## Source Reconstruction

This is mapping/static reconstruction only. No engine C source changed in this
pass. The newly recovered names refine the private libzmq option and ownership
layout behind the repo-facing ZMQ server support in `src/code/server/sv_zmq.c`.
They do not require recreating these C++ classes in the GPL-side C source.

The static parity guard in `tests/test_platform_services.py` pins:

- all aliases promoted in this round;
- the matching Ghidra `functions.csv` rows;
- representative HLIL evidence for default option fields, default-options
  call sites, setter/getter switch anchors, address-mask parse/store/clear
  behavior, vector growth/copy/erase helpers, `own_t` construction/destruction,
  and vtable/RTTI anchors; and
- this round note as the evidence ledger.

## Inference Boundary

This pass intentionally leaves the broad option destructor/copy helpers near
`sub_403480` and `sub_4038B0` unchanged. Their call sites and local evidence
show option-layout activity, but they are shared enough that a separate
copy/destructor-specific pass should pin them with their full call graph before
renaming existing aliases.

## Verification

Local verification for this pass:

- `Get-Content -Raw references/analysis/quakelive_symbol_aliases.json | ConvertFrom-Json | Out-Null`
- `python -m pytest -q tests/test_platform_services.py::test_zmq_options_default_and_mask_vector_round_378_aliases_are_pinned tests/test_platform_services.py::test_zmq_poller_base_io_object_round_377_aliases_are_pinned tests/test_platform_services.py::test_zmq_io_thread_reaper_object_command_round_376_aliases_are_pinned tests/test_platform_services.py::test_zmq_mailbox_select_signaler_round_370_aliases_are_pinned tests/test_platform_services.py::test_zmq_socket_base_and_msg_internal_aliases_round_374_are_pinned tests/test_platform_services.py::test_zmq_public_api_aliases_and_round_365_evidence_are_pinned`
  passed with `6 passed`.
- `python -m pytest -q tests/test_engine_cvar_retail_parity.py::test_engine_cvar_seventeenth_network_bootstrap_tranche_matches_retail_contracts tests/test_server_full_parity_gate.py::test_server_full_parity_gate_writes_status_artifact`
  passed with `2 passed`.

## Parity Estimate

- Focused ZMQ options/defaults/address-mask vector mapping:
  **before 22% -> after 88%**.
- ZMQ-related source reconstruction confidence, including retained
  publication/RCON ownership, public wrappers, socket/message helpers,
  command-delivery support, queue backing-store evidence, object lifecycle
  ownership, event-loop timer/fd-watch wiring, and option/default storage:
  **before 85.3% -> after 85.7%**.
- Overall Quake Live source parity:
  **before 55.51% -> after 55.52%**.
