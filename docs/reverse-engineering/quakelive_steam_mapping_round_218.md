# quakelive_steam.exe Mapping Round 218

Date: 2026-05-11

Scope: the early Win32 network address-conversion lane in
`src/code/win32/win_net.c`, centered on the retained
`NetadrToSockadr` / `Sys_StringToSockaddr` / `Sys_StringToAdr` /
`Sys_IsLANAddress` helpers.

## Summary

This round resolved `4` additional `quakelive_steam.exe` aliases and tightened
the checked-in Win32 string-address parsers so they follow the smaller retail
AF_INET-only contract instead of the older Quake III IPX-capable helper shape.

Classification mix:

- `4` engine-owned functions
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main source win is:

- [`Sys_StringToSockaddr`](../../src/code/win32/win_net.c) and
  [`Sys_StringToAdr`](../../src/code/win32/win_net.c) now mirror the retail
  host more closely by resolving only the retained IPv4-or-hostname lane
  through `inet_addr(...)` / `gethostbyname(...)`, setting the AF_INET family
  or `NA_IP` type directly, and dropping the repo-only Win32 IPX string parser
  from this path.

## Evidence Notes

- The decisive source anchors are the early helper block in
  [`win_net.c`](../../src/code/win32/win_net.c): `NetadrToSockadr`,
  `Sys_StringToSockaddr`, `Sys_StringToAdr`, `Sys_GetPacket`,
  `Sys_SendPacket`, and `Sys_IsLANAddress`.
- `sub_4EE150` is the retained `NetadrToSockadr` owner. The HLIL shows the
  direct conversion from `NA_BROADCAST` / `NA_IP` into an AF_INET
  `sockaddr_in`, including the broadcast `0xffffffff` write and the direct port
  copy from the `netadr_t` payload.
- `sub_4EE1B0` is the retained `Sys_StringToSockaddr` owner. The HLIL zeroes a
  `sockaddr_in`, writes `sin_family = AF_INET`, then chooses between
  `inet_addr(...)` for numeric strings and `gethostbyname(...)` for hostnames
  before copying the first resolved IPv4 address into `sin_addr`.
- `sub_4EE210` is the retained `Sys_StringToAdr` owner. The HLIL is even
  smaller than the checked-in source used to be: it resolves the same
  numeric-or-hostname IPv4 lane directly into `netadr_t.ip`, then writes
  `type = NA_IP` and clears the port field.
- `sub_4EE570` is the retained `Sys_IsLANAddress` owner. The HLIL preserves the
  same loopback fast path, class-based local-IP comparison, and RFC1918 class B
  / class C checks that the checked-in source already carries.
- Important boundary note: the committed HLIL in this lane does not show the
  older Quake III Win32 IPX string parser. The checked-in source therefore now
  keeps IPX handling only in the retained packet/socket transport helpers, not
  in the string-resolution path.
- Related observation: `SockadrToNetadr(...)` still appears inlined into the
  packet receive path around `sub_4EE260`, so I did not force a separate
  promotion for that helper in this round.

## Aliases Added

- `sub_4EE150` -> `NetadrToSockadr`
- `sub_4EE1B0` -> `Sys_StringToSockaddr`
- `sub_4EE210` -> `Sys_StringToAdr`
- `sub_4EE570` -> `Sys_IsLANAddress`

## Verification

Static/source validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- `pytest tests/test_engine_cvar_retail_parity.py -q --tb=no -k "seventeenth_network_bootstrap_tranche_matches_retail_contracts or network_event_wait_path_matches_retail_contracts or network_address_string_parsers_match_retail_contracts"`
  passed (`3 passed`)
- `git diff --check -- src/code/win32/win_net.c references/analysis/quakelive_symbol_aliases.json tests/test_engine_cvar_retail_parity.py`
  reported only the repo's existing LF -> CRLF normalization warnings on the
  touched text files

Alias accounting for the current dirty worktree:

- before this pass: `2231` raw `quakelive_steam` aliases, `2156` strict
  address-backed aliases
- after this pass: `2235` raw `quakelive_steam` aliases, `2160` strict
  address-backed aliases
- strict Ghidra address-backed coverage after this pass: `39.466%` of `5473`
  committed functions

Parity estimate after this pass:

- strict-retail Windows replacement target: `100%` before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

The next useful nearby pass is the remaining early Win32 net helper overhang
around the inlined `SockadrToNetadr(...)` receive-path shape in
`sub_4EE260` and the adjacent IPX/bootstrap owners, where the current checked-in
source still retains broader legacy helper boundaries than the retail HLIL
seems to expose.
