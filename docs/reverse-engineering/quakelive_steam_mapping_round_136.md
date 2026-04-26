# quakelive_steam.exe Mapping Round 136

Date: 2026-04-26

Scope: refreshed largest-unaliased queue after round 135. This pass resolved
the queue-head botlib/parser/TCP-address exacts headed by `sub_411F30`,
`sub_4A0CD0`, `sub_4A9570`, and `sub_4AD4F0`, then harvested the adjacent
JsonCpp and ZeroMQ TCP-address-mask neighbors needed to close the lane
cleanly.

## Summary

This round mapped `7` `quakelive_steam.exe` functions from the refreshed
largest-unaliased queue and nearby exact neighbors. Classification mix:

- `4` engine-owned functions
- `2` platform-service-owned functions
- `1` CRT/STL/support-library function
- `0` Awesomium functions
- `0` Steam SDK support functions

No source debt was opened. This tranche is mostly exact botlib and bundled
libzmq support, with one bounded JsonCpp numeric-decoder helper.

This pass intentionally kept `sub_4615E0`, `sub_463670`, and `sub_463980`
unaliased even though their ownership remains clear: they are STL
red-black-tree iterator-erase helpers. I also left `sub_4F67A0` unresolved for
the previously documented CZMQ `zauth.c` source-anchor reason. `sub_40B050`
and `sub_419AD0` were rechecked and remain classified as CRT/STL red-black-tree
insert/rebalance helpers rather than engine debt.

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_411F30` | `580` | platform-service-owned | `zmq_tcp_address_t_resolve` | High | No engine debt; exact libzmq `tcp_address.cpp` host/port resolver with IPv6 bracket handling and interface-resolution split. |
| 2 | `sub_4A0CD0` | `573` | engine-owned | `BotMovementViewTarget` | High | No engine debt; exact botlib lookahead target helper from `be_ai_move.c`. |
| 3 | `sub_4A9570` | `556` | engine-owned | `PC_ExpandBuiltinDefine` | High | No engine debt; exact botlib preprocessor builtin-define expander from `l_precomp.c`. |
| 4 | `sub_4AD4F0` | `564` | engine-owned | `PS_ReadEscapeCharacter` | High | No engine debt; exact botlib script escape parser from `l_script.c`. |
| 5 | `sub_4124E0` | `559` | platform-service-owned | `zmq_tcp_address_mask_t_resolve` | High | No engine debt; exact libzmq slash-mask resolver paired with the already-mapped `tcp_address_mask_t_to_string`. |
| 6 | `sub_42D770` | `562` | CRT/STL | `JsonReader_decodeDouble` | Medium-high | No engine debt; bounded JsonCpp double parser/error path used from `JsonReader_decodeNumber`. |
| 7 | `sub_49A160` | `553` | engine-owned | `BotCheckValidReplyChatKeySet` | High | No engine debt; exact botlib reply-chat key validator from `be_ai_chat.c`. |

## Evidence Notes

- `sub_411F30` is now stable as `zmq_tcp_address_t_resolve`. The body splits
  the input at the final `:`, strips IPv6 brackets from the host fragment,
  recognizes wildcard/default-port spellings, resolves either through the
  already-mapped `zmq_tcp_address_t_resolve_interface` or the direct
  `getaddrinfo` helper, and finally installs the network-order port into the
  copied sockaddr. That exactly matches the remaining `tcp_address.cpp`
  resolver lane and closes the earlier bad-demangle ambiguity.
- `sub_4124E0` is the matching `zmq_tcp_address_mask_t_resolve` helper. It
  splits `address/mask`, resolves the address portion through the same
  `tcp_address.cpp` support lane, validates the stored mask width against IPv4
  or IPv6 limits, and writes the parsed prefix length into the object field
  that the already-mapped `zmq_tcp_address_mask_t_to_string` later renders.
- `sub_4A0CD0` is an exact `BotMovementViewTarget` hit. The HLIL carries the
  same `move state handle %d out of range` / `invalid move state %d` guards,
  walks reachabilities with the local `BotAddToTarget` helper, stops at
  teleport/rocket/BFG jump travel types, and returns a lookahead target along
  the path exactly like `be_ai_move.c`.
- `sub_4A9570` is an exact `PC_ExpandBuiltinDefine` match. The builtin switch
  emits the line number, source filename, quoted date, or quoted time token,
  uses the same token allocator/fatal `"out of token space\n"` path, and is
  called directly from the already-mapped `PC_ExpandDefine`.
- `sub_4AD4F0` is an exact `PS_ReadEscapeCharacter` match. The body handles
  the standard quoted escapes, hex `\\x..`, decimal escape accumulation, and
  the same `"unknown escape char"` / `"too large value in escape character"`
  diagnostics from `l_script.c`.
- `sub_42D770` is the bounded JsonCpp floating-point decode helper called from
  `JsonReader_decodeNumber` when integer parsing falls through to a real-value
  path. It `sscanf`s the token into a double, constructs the real-valued
  `Json::Value`, and emits the same `is not a number` diagnostic when parsing
  fails.
- `sub_49A160` is an exact `BotCheckValidReplyChatKeySet` match. The source
  warnings about `&` / `!` prefixes, template-space checks, nested `!` key
  containment, and mixed variable/string-key validation all line up directly
  with `be_ai_chat.c`.
- `sub_4615E0`, `sub_463670`, and `sub_463980` remain intentionally unnamed
  STL iterator-erase helpers, while `sub_40B050` and `sub_419AD0` are the
  matching red-black-tree insert/rebalance helpers for other support-library
  containers. `sub_4F67A0` remains classified as platform-service-owned CZMQ
  auth dispatch without a stable public-name anchor.

## Aliases Added

- `sub_411F30` -> `zmq_tcp_address_t_resolve`
- `sub_4124E0` -> `zmq_tcp_address_mask_t_resolve`
- `sub_42D770` -> `JsonReader_decodeDouble`
- `sub_49A160` -> `BotCheckValidReplyChatKeySet`
- `sub_4A0CD0` -> `BotMovementViewTarget`
- `sub_4A9570` -> `PC_ExpandBuiltinDefine`
- `sub_4AD4F0` -> `PS_ReadEscapeCharacter`

## Verification

Alias artifact validation:

- `references/analysis/quakelive_symbol_aliases.json` parses through
  `python -m json.tool`
- duplicate-key scan passed after the alias update
- recount after this pass: `1548` raw alias entries, `1542` address-keyed
  aliases
- address-keyed coverage: `28.175%` of `5473` functions
- refreshed unresolved queue was recomputed against the committed Ghidra
  function-start corpus after the alias update
- no game/runtime launch was performed; this was a static mapping pass

Parity estimate after this mapping-only pass remains unchanged:

- strict-retail Windows replacement target: `100%` before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

After this round, the refreshed largest-unaliased queue begins with:

| # | Address | Ghidra name | Size |
| ---: | --- | --- | ---: |
| 1 | `0x004615E0` | `FUN_004615e0` | `592` |
| 2 | `0x00463670` | `FUN_00463670` | `592` |
| 3 | `0x00463980` | `FUN_00463980` | `592` |
| 4 | `0x004F67A0` | `FUN_004f67a0` | `581` |
| 5 | `0x00435070` | `FUN_00435070` | `566` |
| 6 | `0x0047F600` | `FUN_0047f600` | `564` |
| 7 | `0x00440AD0` | `FUN_00440ad0` | `560` |
