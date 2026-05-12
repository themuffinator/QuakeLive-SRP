# quakelive_steam.exe Mapping Round 222

Date: 2026-05-11

Scope: the shared engine net-address helper lane in
`src/code/qcommon/net_chan.c`, focusing on retained retail address-type
contracts rather than external-library or platform-owned code.

## Summary

This round did not add new aliases. It tightened the checked-in qcommon
address-helper behavior so it matches the smaller retained retail contracts in
`NET_CompareBaseAdr` and `NET_CompareAdr`.

Classification mix:

- `0` engine/qcommon support function aliases
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main source wins are:

- [`NET_CompareBaseAdr`](../../src/code/qcommon/net_chan.c) no longer keeps an
  IPX byte-compare branch that the retained retail helper does not preserve.
- [`NET_CompareAdr`](../../src/code/qcommon/net_chan.c) now matches the retail
  special-case behavior for equal `NA_BOT` addresses, while also dropping the
  stale IPX equality branch.

## Evidence Notes

- `sub_4D6D60` is the retained `NET_CompareBaseAdr` owner. In committed HLIL:
  1. it first requires equal address types,
  2. returns true only for type `2` (`NA_LOOPBACK`),
  3. compares raw IPv4 bytes only for type `4` (`NA_IP`),
  4. and otherwise falls through to `Com_Printf("NET_CompareBaseAdr: bad address type\n")`.
- That means the checked-in `NA_IPX` byte-compare path was wider than retail
  and has now been removed.
- `sub_4D6EB0` is the retained `NET_CompareAdr` owner. In committed HLIL:
  1. it first requires equal address types,
  2. returns true immediately for type `2` (`NA_LOOPBACK`) and type `0`
     (`NA_BOT`),
  3. compares IPv4 bytes plus port only for type `4` (`NA_IP`),
  4. and otherwise falls through to `Com_Printf("NET_CompareAdr: bad address type\n")`.
- The checked-in source previously diverged in two ways:
  1. it treated `NA_BOT` pairs as a bad type instead of equal,
  2. and it still preserved a full `NA_IPX` byte-and-port compare path that
     the retail helper no longer carries.
- `sub_4D6F30` (`NET_IsLocalAddress`) remains the simple retained pure check
  `arg1 == 2`, which matches the existing `NA_LOOPBACK` test and did not need
  source changes this round.

## Aliases Added

- none

## Verification

Static/source validation:

- `pytest tests/test_engine_netcode_parity.py -q --tb=no -k "net_address_helpers or cl_serverinfopacket or ping_helper_lane or cl_setserverinfo"`
  passed
- `git diff --check -- src/code/qcommon/net_chan.c tests/test_engine_netcode_parity.py docs/reverse-engineering/quakelive_steam_mapping_round_222.md`
  reported only the repo's existing LF -> CRLF normalization warnings on the
  touched text files

Alias accounting for the current dirty worktree:

- before this pass: `2236` raw `quakelive_steam` aliases, `2157` strict
  address-backed aliases
- after this pass: `2236` raw `quakelive_steam` aliases, `2157` strict
  address-backed aliases
- strict Ghidra address-backed coverage after this pass: `39.412%` of `5473`
  committed functions

Parity estimate after this pass:

- strict-retail shared net-address helper lane: `99%` before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

The next strong nearby pass is still the unresolved client command-wrapper seam
around `localservers`, `globalservers`, `ping`, and `serverstatus`, but the
remaining work there should wait for stable retail ownership evidence instead
of leaning on inherited Quake III text alone.
