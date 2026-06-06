# Quake Live ZMQ/CZMQ Mapping Round 362

Date: 2026-06-06

Focus: finish the remaining anonymous ZMQ/CZMQ helper headers in
`quakelive_steam.exe`, including retained `idZMQ` RCON peer-tree scaffolding,
late `zsys` IPv6 setters, and the small `zconfig` name setter left open after
round 361.

## Retail Evidence

- Owning binary: `assets/quakelive/quakelive_steam.exe`.
- Structured companion corpus:
  `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
  reports 5,473 functions, 351 imports, 2 exports, and 4,377 promoted
  analysis symbols.
- Canonical HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`.
- Upstream source corroboration used CZMQ v4.2.1:
  [zsys.c](https://github.com/zeromq/czmq/blob/v4.2.1/src/zsys.c) and
  [zconfig.c](https://github.com/zeromq/czmq/blob/v4.2.1/src/zconfig.c).

## Alias Reconstruction

This pass added 10 aliases to
`references/analysis/quakelive_symbol_aliases.json`.

| Address | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `0x004F3E30` | `std_tree_rightmost_zmq_rcon_peer_node` | High | Walks node right links until the sentinel, and is used by the retained peer erase path to repair the header rightmost pointer. |
| `0x004F3E50` | `std_tree_leftmost_zmq_rcon_peer_node` | High | Walks node left links until the sentinel, and is used by the retained peer erase path to repair the header leftmost pointer. |
| `0x004F3E70` | `std_tree_next_zmq_rcon_peer_node` | High | Implements the MSVC tree iterator successor path, including right-subtree minimum lookup and parent ascent. |
| `0x004F3EC0` | `std_tree_prev_zmq_rcon_peer_node` | High | Implements the matching predecessor path, used by `idZMQ_InsertRconPeer` before duplicate-key handling. |
| `0x004F4150` | `std_tree_rotate_right_zmq_rcon_peer_node` | High | Performs the right-rotation primitive used during peer-node erase rebalancing. |
| `0x004F43B0` | `std_tree_rotate_left_zmq_rcon_peer_node` | High | Performs the left-rotation primitive used during peer-node erase rebalancing. |
| `0x004F4640` | `std_tree_create_zmq_rcon_peer_node` | High | Allocates a 0x14-byte MSVC tree node, initializes left/parent/right links to the header, sets node color/state bytes, and stores the peer key pointer consumed by `idZMQ_InsertRconPeer`. |
| `0x004F6DE0` | `zsys_set_ipv6_address` | High | Calls `zsys_init`, frees the retained global string at `data_12d30d4`, duplicates the new value, and is called from `zsys_init` only when `ZSYS_IPV6_ADDRESS` is present. |
| `0x004F6E10` | `zsys_set_ipv6_mcast_address` | High | Same setter shape for `data_12d30d8`, called from `zsys_init` only when `ZSYS_IPV6_MCAST_ADDRESS` is present. |
| `0x004FB5F0` | `zconfig_s_set_name` | High | Frees a string slot and duplicates or clears the incoming name; `zconfig_new` calls it for the new node name, matching upstream `zconfig_set_name`. |

## Observed Facts

- The `idZMQ` peer-table corridor from `0x004F3E30` through
  `0x004F5080` now has no anonymous function headers in the alias artifact.
- The bundled CZMQ corridor from `0x004F5100` through `0x004FBD90` now also
  has no anonymous function headers in the alias artifact.
- The `zsys` IPv6 setter names were left open in round 361 because CZMQ
  v3.0.2 did not carry enough matching context. CZMQ v4.2.1 provides the
  exact `ZSYS_IPV6_ADDRESS` and `ZSYS_IPV6_MCAST_ADDRESS` environment wiring,
  matching the retail HLIL calls at `0x004F7671` and `0x004F768F`.
- The retained `idZMQ` RCON peer set is MSVC red-black tree scaffolding over
  peer identity strings. These aliases intentionally describe tree ownership
  and mechanics rather than public gameplay behavior.

## Inference Boundary

This is a mapping-only pass. It does not change game source, does not enable
live online services, and does not claim live ZAP/CURVE parity. The remaining
source-reconstruction gap is behavioral fidelity inside `src/code/server/sv_zmq.c`,
especially around exact CZMQ actor/auth behavior and the retail tree-backed
RCON peer container versus the current portable fallback representation.

## Verification

- `references/analysis/quakelive_symbol_aliases.json` parses through
  `ConvertFrom-Json`.
- Current `quakelive_steam` alias count: 3,013 entries, with 3,007
  address-backed aliases.
- Recounted anonymous function headers:
  - `0x004F3E30..0x004F5080`: 0 remaining.
  - `0x004F5100..0x004FBD90`: 0 remaining.

## Parity Estimate

- Focused retail ZMQ/CZMQ helper mapping:
  **before 84% -> after 88%**.
- ZMQ-related source reconstruction confidence, including retained
  publication/RCON ownership:
  **before 78% -> after 80%**.
- Overall Quake Live source parity:
  **before 55.3% -> after 55.35%**.
