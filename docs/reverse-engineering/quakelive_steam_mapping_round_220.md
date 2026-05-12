# quakelive_steam.exe Mapping Round 220

Date: 2026-05-11

Scope: the retained client server-browser info-packet lane in
`src/code/client/cl_main.c`, plus the adjacent qcommon debug-print helper
owner used throughout that path.

## Summary

This round added `1` additional `quakelive_steam.exe` alias and tightened one
checked-in client server-browser branch so it follows the smaller retail
`CL_ServerInfoPacket` contract instead of keeping an older IPX-era net-type
classification.

Classification mix:

- `1` engine/qcommon support function
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main source win is:

- [`CL_ServerInfoPacket`](../../src/code/client/cl_main.c) now stamps ping
  replies with the retained binary retail net-type classification: `1` for the
  IPv4 broadcast/IP address types and `0` otherwise, instead of the older
  writable-source ternary that still assigned `2` to IPX replies.

## Evidence Notes

- `sub_4BA230` is the retained `CL_ServerInfoPacket` owner. In the committed
  HLIL, once a pending ping slot matches the incoming address, the function:
  1. stamps the ping time,
  2. copies the info string,
  3. sets the temporary `nettype` value to `1` only when the incoming address
     type is within the retained broadcast/IP pair (`NA_BROADCAST` /
     `NA_IP`),
  4. otherwise falls back to `0`,
  5. and then writes that value back through `Info_SetValueForKey(...,
     "nettype", va(...))`.
- The same HLIL block does not show the older Quake III `udp` / `ipx` /
  `???` string switch or an IPX-specific `type = 2` assignment, so the
  checked-in source has now been reduced to the retail binary classification.
- `sub_4C9AB0` is the retained `Com_DPrintf` owner. The HLIL:
  1. checks the developer cvar/global gate before doing any work,
  2. formats into a local buffer with `_vsnprintf(...)`,
  3. prints through the already-mapped `Com_Printf` owner (`sub_4C9860`),
  4. and mirrors the message into the small retained console-log ring.
  That matches the engine debug-print helper used by `CL_ServerInfoPacket`
  for `"Different protocol info packet: %s\n"`,
  `"ping time %dms from %s\n"`, and
  `"MAX_OTHER_SERVERS hit, dropping infoResponse\n"`.

## Aliases Added

- `sub_4C9AB0` -> `Com_DPrintf`

## Verification

Static/source validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- `pytest tests/test_engine_netcode_parity.py tests/test_platform_services.py -q --tb=no -k "cl_setserverinfo or cl_serverinfopacket or browser_server_shims"`
  passed (`3 passed, 75 deselected`)
- `git diff --check -- src/code/client/cl_main.c references/analysis/quakelive_symbol_aliases.json tests/test_engine_netcode_parity.py docs/reverse-engineering/quakelive_steam_mapping_round_220.md`
  reported only the repo's existing LF -> CRLF normalization warnings on the
  touched text files

Alias accounting for the current dirty worktree:

- before this pass: `2235` raw `quakelive_steam` aliases, `2156` strict
  address-backed aliases
- after this pass: `2236` raw `quakelive_steam` aliases, `2157` strict
  address-backed aliases
- strict Ghidra address-backed coverage after this pass: `39.412%` of `5473`
  committed functions

Parity estimate after this pass:

- strict-retail client server-browser lane: `99%` before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

The next useful nearby pass is the unresolved client command-wrapper seam
around `localservers`, `globalservers`, `ping`, and `serverstatus`, where the
retail engine clearly preserves the server-browser dataflow but the exact
console-command owners still need stable address-backed names and any remaining
GPL-only wrapper behavior should be rechecked against HLIL before it is forced.
