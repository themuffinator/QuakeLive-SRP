# Quake Live Steam Host Mapping Round 299

## Scope

This round closes the empty-name display fallback left open by round 298. The
focus is the small helper at `00461f10` that `JSBrowser_OnServerResponded`
uses when a Steam server-browser row has an empty server name.

Evidence order:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `docs/reverse-engineering/quakelive_steam_mapping_round_08.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_237.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_298.md`

## Observed Facts

`sub_461f10` is a compact helper called from both details-response paths when
the server-row name at byte offset `0xac` is empty:

- `sub_461fe0` checks `&arg2[0x56]`, calls `sub_461f10(arg2)` if the first byte
  is zero, and publishes the returned string as payload field `"name"`.
- `sub_462a50` performs the same check after fetching a row through
  `SteamMatchmakingServers()->vtable[0x1c]`.

The helper itself reads the packed row IP at byte offset `0x04`, the connection
port at byte offset `0x00`, and formats into one of four 64-byte static buffers:

| Retail signal | Reconstructed meaning |
| --- | --- |
| `(data_e30330 << 6) + 0xe30230` | Four-slot ring buffer, 64 bytes per string. |
| `_snprintf(..., 0x40, "%u.%u.%u.%u:%i", ...)` | Bounded dotted-address fallback string. |
| `eax:3.b`, `eax:2.b`, `eax:1.b`, `eax.b` | Raw row IP bytes emitted most-significant byte first. |
| `zx.d(*arg1)` passed to `%i` | Connection port is formatted as a positive integer from the row's 16-bit value. |
| `(data_e30330 + 1) & 3` | Ring buffer advances modulo four. |

This fallback is part of the browser-facing display payload, not the raw Steam
server row. Round 237's signed request/detail-token address formatting remains
a separate client request-object contract.

## Source Reconstruction

`ql_steam_server_item_t` now separates the raw server name from the display name
used by retail's details payload:

- `name` remains the raw `gameserveritem_t` server-name string.
- `displayName` contains the raw name when present, otherwise the
  `"%u.%u.%u.%u:%i"` address fallback reconstructed from `sub_461f10`.

`platform_steamworks.c` gained two small helpers:

- `QL_Steamworks_FormatServerListFallbackName`
- `QL_Steamworks_CopyServerListDisplayName`

The fallback helper intentionally formats the raw row IP most-significant byte
first, matching the `sub_461f10` byte extraction rather than the retained
client request-token helper. It uses the same 64-byte effective bound through
the public `QL_STEAM_SERVER_BROWSER_DISPLAY_NAME_LENGTH` constant.

The Steamworks harness now exposes
`QLR_SteamworksMock_SetServerBrowserServerName`, allowing tests to force the
empty-name path. Python harness coverage proves that:

- non-empty row names are copied to both `name` and `displayName`;
- AppID rejection still clears both strings; and
- empty row names produce the retail-style address fallback.

## Open Questions

- The source still does not publish native Steam server rows into the retained
  browser event queue. The typed row and display-name projection are ready for
  that future owner, but this round does not wire it.
- The four-slot ring-buffer implementation detail is not reproduced because
  the public projection owns caller-provided storage. That preserves the
  visible string contract without reintroducing transient global buffers.
- Ping/player/rules query-handle cancellation remains open from round 297.

## Verification

Focused validation passed:

- `python -m pytest tests/test_steamworks_harness.py -q --tb=short`
  reported `64 passed`.

No runtime game launch was needed; this was a static wrapper and harness
projection task.

## Parity Estimate

Before this round, the scoped server-row projection was about 75% complete:
field extraction and AppID validation were reconstructed, but the retail
display-name fallback was still an open browser-payload detail. After this
round, the scoped server-row projection is about 82% complete. The remaining
work is mostly native browser-event integration and query-handle lifecycle
cleanup.

For the broader Steamworks subsystem, this keeps the estimate at about 67%
parity with the observed retail Steamworks surface. It improves fidelity inside
the native server-browser slice but does not yet change product-level browser
behavior.
