# Quake Live Steam Host Mapping Round 307

## Scope

This round reconstructs the retained `JSBrowserDetails` rules/player response
payload projections. Round 306 pinned the detail id and event-name families;
this pass adds the browser-facing fields carried by successful rules and
player detail callbacks.

Evidence order:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `docs/reverse-engineering/quakelive_steam_mapping_round_306.md`
- `src/code/client/cl_main.c`
- `src/common/platform/platform_steamworks.[ch]`

## Observed Facts

The retained rules response callback builds a browser object with:

| Field | Source |
| --- | --- |
| `id` | detail id at object offset `+0x14` |
| `ip` | server IP at object offset `+0xc` |
| `port` | server port at object offset `+0x10` |
| `rule` | first callback argument |
| `value` | second callback argument |

It publishes that object through `servers.rules.%s.response`.

The retained player response callback builds a browser object with:

| Field | Source |
| --- | --- |
| `id` | player-detail view id at object offset `+0x10` |
| `ip` | player-detail view IP at object offset `+8` |
| `port` | player-detail view port at object offset `+0xc` |
| `name` | first callback argument |
| `score` | second callback argument |
| `time` | observed constant-key assignment in the HLIL; source compatibility carries parsed time |

It publishes that object through `servers.players.%s.response`.

The source compatibility publisher already emits the same outward field names
for rules and players. This round promotes those fields into the native wrapper
projection so future native detail callbacks can publish a typed payload
without re-deriving the contract in client code.

## Source Reconstruction

`platform_steamworks.[h/c]` now exposes:

- `QL_STEAM_SERVER_BROWSER_RULE_LENGTH`
- `QL_STEAM_SERVER_BROWSER_RULE_VALUE_LENGTH`
- `QL_STEAM_SERVER_BROWSER_PLAYER_NAME_LENGTH`
- `ql_steam_server_browser_rule_response_t`
- `ql_steam_server_browser_player_response_t`
- `QL_Steamworks_BuildServerBrowserRuleResponse`
- `QL_Steamworks_BuildServerBrowserPlayerResponse`

Both builders reuse the round-306 detail identity/event projection. The rules
builder fills the retained `rule` and `value` fields and publishes the
`servers.rules.%s.response` identity. The player builder fills `name`, `score`,
and `time`, preserving the existing source compatibility contract for `time`
while noting the HLIL quirk as an open evidence point rather than inventing a
new browser field.

Disabled builds zero output structures and return false so default/offline
builds do not report native Steam detail payloads.

## Open Questions

- The retained three-completion lifetime counter at the rules/player callback
  offsets still needs a small native owner model.
- The player `time` field deserves another cross-check against adjacent
  Binary Ninja or Ghidra evidence because the HLIL shows a suspicious constant
  construction while the compatibility source carries parsed time.
- Client event publication still needs a single owner decision before these
  projections are wired into `CL_SteamBrowser_*`.

## Verification

Focused validation passed:

- `python -m pytest tests/test_steamworks_harness.py::test_server_browser_detail_response_payloads_match_retail_jsbrowserdetails_contract -q --tb=short`
  reported `2 passed`.
- `python -m pytest tests/test_steamworks_harness.py -q --tb=short`
  reported `74 passed`.
- `python -m pytest tests/test_platform_services.py::test_steamworks_modern_adapter_gaps_stay_explicit_until_owned tests/test_platform_services.py::test_client_browser_server_shims_reconstruct_retail_server_browser_surface -q --tb=short`
  reported `2 passed`.
- `git diff --check -- src/common/platform/platform_steamworks.c src/common/platform/platform_steamworks.h tests/steamworks_harness.c tests/test_steamworks_harness.py docs/plans/steamworks-parity-plan.md docs/steam_platform_abstraction.md docs/reverse-engineering/quakelive_steam_mapping_round_307.md`
  reported no whitespace errors.

No runtime game launch was needed; this pass covered native wrapper projection
and harness behavior only.

## Parity Estimate

Before this round, the scoped native server-browser wrapper was about 92%
complete: detail identity and event names were reconstructed, but successful
detail response payloads were still implicit. After this round, the scoped
wrapper is about 94% complete.

For the broader Steamworks subsystem, this keeps the estimate at about 69%
parity with the observed retail Steamworks surface. The successful
rules/player detail payloads are now pinned, while lifetime ownership and
client publication remain open.
