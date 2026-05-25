# Quake Live Steam Host Mapping Round 300

## Scope

This round audits the native Steam server-browser detail-query lifecycle around
`JSBrowserDetails_RequestServerDetails` and adds the bounded low-level
`CancelServerQuery` wrapper needed by any future native browser owner. It does
not wire cancellation into product behavior, because the committed retail HLIL
does not show that callback owner calling the cancel slot.

Evidence order:

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `docs/reverse-engineering/quakelive_steam_mapping_round_08.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_297.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_299.md`

## Observed Facts

The committed corpus contains only one imported `SteamMatchmakingServers`
symbol. The detail-request owner at `00461f70` stores the requested IP and port,
builds the signed detail token with `"%u_%i"`, and starts three detail probes:

| Offset | API role | Retail call order | Response object |
| --- | --- | --- | --- |
| `0x34` | `PingServer` | first | `this + 8` |
| `0x3c` | `ServerRules` | second | `this + 0` |
| `0x38` | `PlayerDetails` | third | `this + 4` |

The response object allocated by the public `RequestServerDetails` wrapper is
`0x58` bytes. The three interface vptrs are placed at offsets `0x00`, `0x04`,
and `0x08`, and the request bootstrap writes IP/port/token at `0x0c`,
`0x10`, and `0x14`.

The callbacks use completion counters to decide when the response object can be
deleted:

| Callback family | Representative callbacks | Counter | Delete base |
| --- | --- | --- | --- |
| server row / ping response | `sub_461fe0` success, `sub_462340` completion helper | `+0x4c` | `arg1 - 8` |
| rules response | `sub_462490` failed, `sub_4625a0` end | `+0x54` | `arg1` |
| players response | `sub_462830` failed, `sub_462940` end | `+0x50` | `arg1 - 4` |

Each family deletes the shared allocation when its counter reaches three. The
HLIL excerpts in this corpus do not show a `SteamMatchmakingServers()->vtable`
call at `0x40` in these callbacks or in the request bootstrap. The only
observed SteamMatchmakingServers offsets in the detail path are `0x34`, `0x3c`,
and `0x38`; list management separately uses `0x18`, `0x1c`, and `0x24`.

The older Steamworks ABI places `CancelServerQuery` immediately after
`ServerRules`, at vtable offset `0x40`. That adjacency gives enough confidence
to expose a low-level wrapper, but not enough to claim retail product behavior
called it in the observed path.

## Source Reconstruction

`platform_steamworks.[ch]` now exposes:

- `QL_Steamworks_CancelServerQuery( ql_steam_server_query_t query )`

The wrapper:

- remains behind `QL_BUILD_STEAMWORKS`;
- ignores non-positive query handles, matching the wrapper's existing failed
  request outputs;
- resolves the optional `SteamMatchmakingServers` interface;
- dispatches vtable slot `0x40`; and
- stays unwired from the client/browser flow until a native browser owner is
  deliberately integrated.

The disabled build still compiles to a harmless inline no-op.

The Steamworks harness now mocks slot `0x40`, records the cancel call count and
last canceled query, and pins the wrapper behavior. The focused test proves
that query `0` is ignored and that the retained ping/player/rules handles
returned by `QL_Steamworks_RequestServerDetails` can be canceled through the
new slot.

## Open Questions

- The retail `JSBrowserDetails` owner appears to rely on callback completion
  and object deletion rather than explicit query cancellation. If later evidence
  finds a cancellation caller outside the currently committed HLIL slice, the
  integration layer should wire this wrapper there.
- Product-level browser integration is still open: native row projection,
  display-name fallback, detail-query creation, and cancellation are now
  available as low-level pieces, but the retained client browser still uses the
  bounded compatibility lane.

## Verification

Focused validation passed:

- `python -m pytest tests/test_steamworks_harness.py -q --tb=short`
  reported `64 passed`.

No runtime game launch was needed; this pass covered static wrapper dispatch
and harness behavior.

## Parity Estimate

Before this round, the scoped server-browser detail-query wrapper was about 72%
complete: request creation, row projection, and display fallback were present,
but the adjacent cancellation primitive was not exposed. After this round, the
scoped low-level wrapper is about 78% complete. The remaining gap is native
client/browser integration and stronger evidence for whether retail ever
canceled live detail handles from another owner.

For the broader Steamworks subsystem, this keeps the estimate at about 67%
parity with the observed retail Steamworks surface. It improves lifecycle
coverage inside the native server-browser wrapper without changing product
browser behavior.
