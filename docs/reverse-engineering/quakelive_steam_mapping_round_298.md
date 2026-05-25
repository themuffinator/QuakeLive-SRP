# Quake Live Steam Host Mapping Round 298

## Scope

This round promotes the retained Steam server-browser row returned by
`SteamMatchmakingServers()->vtable[0x1c]` from an opaque pointer into a typed
source-level projection. It builds directly on round 297's native
`ISteamMatchmakingServers` wrapper and stays inside the platform layer; the
client `CL_SteamBrowser_*` ownership and browser-event publishing path remain a
separate integration task.

Evidence order:

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `docs/reverse-engineering/quakelive_steam_mapping_round_08.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_237.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_297.md`

## Observed Facts

The owning binary remains `quakelive_steam.exe`; the committed Ghidra metadata
reports 5473 functions, 351 imports, and 4377 promoted analysis symbols.
`functions.csv` records `FUN_00462a50` at `00462a50` with size 860, and round
08 promotes that function as `JSBrowser_OnServerResponded`.

At `00462a8c`, `JSBrowser_OnServerResponded` calls
`SteamMatchmakingServers()->vtable[0x1c]` with the retained request/index pair.
That is the old `ISteamMatchmakingServers::GetServerDetails` slot. It rejects
null rows, then calls `SteamUtils()->vtable[0x24]` and compares the row AppID
against the current Steam AppID before publishing a server-details payload.

The field walk matches the retail-era `gameserveritem_t` layout. Binary Ninja
prints a mixture of byte-offset additions and indexed expressions in this
function; the table below normalizes those signals into byte offsets.

| Byte offset | Reconstructed field | HLIL signal | Confidence |
| --- | --- | --- | --- |
| `0x00` | connection/server port | `zx.d(*result_1)` for `port` and response id | High |
| `0x02` | query port | SDK layout companion to `servernetadr_t` | Medium |
| `0x04` | packed IPv4 address | `*(result_1 + 4)` for `ip` and response id | High |
| `0x08` | ping | `*(result_1 + 8)` for `ping` | High |
| `0x0c` | successful-response flag | SDK layout between ping and game-dir strings | Medium |
| `0x0d` | do-not-refresh flag | SDK layout between ping and game-dir strings | Medium |
| `0x0e` | game directory | 32-byte SDK string preceding map | Medium |
| `0x2e` | map | `&result_1[0x17]` for `map` | High |
| `0x4e` | game description / gametype | `&result_1[0x27]` for `gametype` | High |
| `0x90` | app id | `*(result_1 + 0x90)` compared to `SteamUtils()->GetAppID()` | High |
| `0x94` | current player count | `*(result_1 + 0x94)` for `numPlayers` | High |
| `0x98` | max player count | `*(result_1 + 0x98)` for `maxPlayers` | High |
| `0x9c` | bot player count | `*(result_1 + 0x9c)` for `botPlayers` | High |
| `0xa0` | password-protected flag | `result_1[0x50].b` for `password` | High |
| `0xa1` | VAC/secure flag | `*(result_1 + 0xa1)` for `vac` | High |
| `0xa4` | last played time | `*(result_1 + 0xa4)` for `lastPlayed` | High |
| `0xa8` | server version | SDK layout between `lastPlayed` and server name | Medium |
| `0xac` | server name | `&result_1[0x56]` for `name` | High |
| `0xec` | game tags | `&result_1[0x76]` for `tags` | High |
| `0x16c` | SteamID low dword | `*(result_1 + 0x16c)` for `steam_id` formatting | High |
| `0x170` | SteamID high dword | `*(result_1 + 0x170)` for `steam_id` formatting | High |

Two small behavior details are deliberately not folded into the new projection.
First, `JSBrowser_OnServerResponded` uses `sub_461f10` as a display-name
fallback when the row's server name is empty. The wrapper now exposes the raw
row content; browser payload fallback formatting should stay in the future
browser publisher, not in the data projection. Second, round 237 shows the
client-owned details request token uses a signed port while the details
response id uses an unsigned port. The projection returns typed fields so the
two string contracts can continue to be built by their owning publish paths.

## Source Reconstruction

The platform wrapper now exposes `ql_steam_server_item_t`, a bounded public
projection for the retained server row. It includes the connection address,
query port, ping, game directory, map, game description, AppID, player counts,
password/VAC flags, last-played timestamp, server version, name, tags, and
SteamID.

`platform_steamworks.c` gained an internal
`ql_steam_gameserveritem_raw_t` layout that matches the normalized offsets
above. `QL_Steamworks_ReadServerListDetails` now:

- calls the existing `QL_Steamworks_GetServerListDetails` wrapper for slot
  `0x1c`;
- clears the caller-provided output on all exits;
- rejects null rows;
- validates the raw row AppID against `QL_Steamworks_GetAppID()`;
- copies all bounded strings through the existing Steam string helper; and
- returns a typed `ql_steam_server_item_t` only for a valid current-AppID row.

The disabled `QL_BUILD_STEAMWORKS=0` path stays harmless: the inline stub zeros
the output and returns `qfalse`.

The Steamworks harness now retains a mock row with the reconstructed layout and
returns it through the mocked `GetServerDetails` vtable slot. The Python
harness gained `SteamServerItem` coverage that proves the typed projection
copies every exposed field, preserves the `GetServerDetails` request/index
call, rejects mismatched AppIDs, and still zeros output when Steamworks is
disabled.

## Open Questions

- The client browser still uses the retained source-browser compatibility lane
  for friends/history results. This round only makes the native server-row data
  available to a future owner.
- Empty-name display fallback remains at the browser-publisher layer. The
  candidate owner is still `sub_461f10`, and it should be mapped before the
  typed row is used to publish `servers.details.*.response`.
- Query-handle cancellation for ping/player/rules detail probes is still not
  reconstructed.
- Medium-confidence fields (`queryPort`, response flags, `gameDir`, and
  `serverVersion`) are supported by the retail SDK layout and surrounding
  offsets, but are not directly emitted by `JSBrowser_OnServerResponded`.

## Verification

Focused validation passed:

- `python -m pytest tests/test_steamworks_harness.py -q --tb=short`
  reported `62 passed`.

No game launch was needed; the evidence and behavior under test are static
wrapper layout/projection contracts.

## Parity Estimate

Before this round, the scoped server-row field reconstruction was roughly 15%
complete: round 297 proved the `GetServerDetails` slot and payload fields, but
source still treated the row as an opaque pointer. After this round, the scoped
server-row projection is about 75% complete. The remaining 25% is mostly
browser-publisher integration, empty-name fallback promotion, query-handle
cancellation, and stronger confirmation for the fields inferred from SDK
layout rather than direct payload emission.

For the broader Steamworks subsystem, this moves the estimate from about 66% to
67% parity with the observed retail Steamworks surface. It is a meaningful
native server-browser step, not a claim of full product-level browser parity.
