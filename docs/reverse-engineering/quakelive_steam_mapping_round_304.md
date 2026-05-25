# Quake Live Steam Host Mapping Round 304

## Scope

This round reconstructs the browser-facing response projection used by
`JSBrowser_OnServerResponded`. It does not publish native browser events from
the client yet; it exposes the typed payload shape that a future native client
owner can hand to the retained web/event bridge.

Evidence order:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `docs/reverse-engineering/quakelive_steam_mapping_round_298.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_299.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_303.md`
- `src/code/client/cl_main.c`
- `src/common/platform/platform_steamworks.[ch]`

## Observed Facts

`JSBrowser_OnServerResponded` reads one row through
`ISteamMatchmakingServers::GetServerDetails` at vtable offset `0x1c`, rejects
rows whose AppID does not match `SteamUtils()->GetAppID()`, then constructs a
browser object with these fields:

| Browser field | Retail source |
| --- | --- |
| `name` | row server name, or the `sub_461f10` address fallback |
| `numPlayers` | row player count at offset `0x94` |
| `maxPlayers` | row max-player count at offset `0x98` |
| `ping` | row ping at offset `0x08` |
| `map` | row map string at offset `0x2e` |
| `botPlayers` | row bot count at offset `0x9c` |
| `password` | row password flag at offset `0xa0` |
| `vac` | row secure/VAC flag at offset `0xa1` |
| `ip` | packed row IP at offset `0x04` |
| `port` | connection port at offset `0x00` |
| `id` | unsigned response id built from IP and connection port |
| `steam_id` | row SteamID formatted as unsigned decimal text |
| `tags` | row game tags at offset `0xec` |
| `gametype` | row game description string at offset `0x4e` |
| `lastPlayed` | row last-played value at offset `0xa4` |

The retained source compatibility publisher in `CL_SteamBrowser_PublishServerResponse`
already uses the `servers.details.%u_%u.response` event-name family for source
browser rows. The native wrapper can therefore expose the response identity and
payload values without taking over event publication yet.

## Source Reconstruction

`platform_steamworks.[h/c]` now exposes:

- `ql_steam_server_browser_response_t`
- `QL_Steamworks_FormatServerBrowserResponseId`
- `QL_Steamworks_BuildServerBrowserResponse`
- `QL_Steamworks_ReadServerBrowserResponse`

The response projection:

- keeps the raw row projection in `ql_steam_server_item_t`;
- builds the browser-facing name from `displayName`, preserving the retail
  empty-name fallback from round 299;
- formats the response id as `"<packed-ip>_<unsigned-port>"`;
- formats the 64-bit row SteamID as decimal text;
- carries the native row game-description string as `gametype`;
- carries tags and lastPlayed directly from the row; and
- still relies on `QL_Steamworks_ReadServerListDetails` for AppID validation.

Disabled builds zero the output and return false, keeping the native browser
response path behind `QL_BUILD_ONLINE_SERVICES` / `QL_BUILD_STEAMWORKS`.

## Open Questions

- The future client owner still needs to publish `servers.details.<id>.response`
  events from this projection and reconcile them with the existing
  source-browser compatibility publisher.
- The committed HLIL confirms the response id uses the row IP and unsigned
  connection port. The source projection follows the retained compatibility
  publisher's current `packed-ip_port` order.
- Rules/player detail callbacks are still separate projections; this round
  only covers list-row responses.

## Verification

Focused validation passed:

- `python -m pytest tests/test_steamworks_harness.py::test_server_browser_response_projection_matches_retail_jsbrowser_payload_shape -q --tb=short`
  reported `2 passed`.
- `python -m pytest tests/test_steamworks_harness.py -q --tb=short`
  reported `68 passed`.
- `python -m pytest tests/test_platform_services.py::test_steamworks_modern_adapter_gaps_stay_explicit_until_owned tests/test_platform_services.py::test_client_browser_server_shims_reconstruct_retail_server_browser_surface -q --tb=short`
  reported `2 passed`.
- `git diff --check -- src/common/platform/platform_steamworks.c src/common/platform/platform_steamworks.h tests/steamworks_harness.c tests/test_steamworks_harness.py docs/plans/steamworks-parity-plan.md docs/steam_platform_abstraction.md docs/reverse-engineering/quakelive_steam_mapping_round_304.md`
  reported no whitespace errors.

No runtime game launch was needed; this pass covered wrapper projection and
harness behavior only.

## Parity Estimate

Before this round, the scoped native server-browser wrapper was about 85%
complete: row data and owner lifecycle were reconstructed, but the row response
payload shape was still implicit. After this round, the scoped wrapper is about
88% complete.

For the broader Steamworks subsystem, this keeps the estimate at about 68%
parity with the observed retail Steamworks surface. The native browser row
payload is now source-shaped and test-pinned, but product-level client event
publication remains open.
