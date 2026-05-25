# Quake Live Steam Host Mapping Round 309

## Scope

This round reconstructs the retained `JSBrowserDetails` shared completion
counter that decides when the per-server detail request object is ready to be
released. Earlier server-browser rounds exposed the detail id, event names, and
successful rules/player payloads; this pass covers the lifetime signal shared
by ping, rules, and player-detail callbacks.

Evidence order:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `docs/reverse-engineering/quakelive_steam_mapping_round_307.md`
- `src/common/platform/platform_steamworks.[ch]`
- `tests/steamworks_harness.c`
- `tests/test_steamworks_harness.py`

## Observed Facts

`sub_4630b0` allocates `0x58` bytes for the retained detail object and installs
three callback vtables: one at the object base, one at `base + 4`, and one at
`base + 8`. It then enters `sub_461f70`.

`sub_461f70` stores the detail identity and launches the three Steam detail
queries:

| Operation | Stored or passed value |
| --- | --- |
| server IP | object offset `+0xc` |
| server port | object offset `+0x10` |
| detail id | object offset `+0x14`, formatted as `"%u_%i"` |
| `PingServer` response | `base + 8` callback view |
| `ServerRules` response | `base` callback view |
| `PlayerDetails` response | `base + 4` callback view |

The terminal callbacks all increment the same base-object completion counter:

| Callback family | Observed increment | Base-object field | Release condition |
| --- | --- | --- | --- |
| ping response/failure | `*(arg1 + 0x4c)` from `base + 8` | `base + 0x54` | delete `base` when count reaches `3` |
| rules failed/end | `*(arg1 + 0x54)` from `base` | `base + 0x54` | delete `base` when count reaches `3` |
| players failed/end | `*(arg1 + 0x50)` from `base + 4` | `base + 0x54` | delete `base` when count reaches `3` |

Successful rules/player response callbacks build and publish payloads but do
not advance the completion counter. The observed terminal callbacks imply a
raw shared counter; this wrapper intentionally does not add per-lane
deduplication that is not visible in the retail code. The Steamworks callback
contract is expected to provide one terminal signal per detail lane.

## Source Reconstruction

`platform_steamworks.[h/c]` now exposes:

- `QL_STEAM_SERVER_BROWSER_DETAIL_COMPLETION_TARGET`
- `ql_steam_server_browser_detail_lifecycle_t`
- `QL_Steamworks_InitServerBrowserDetailLifecycle`
- `QL_Steamworks_CompleteServerBrowserDetailCallback`

The initializer reuses the retained `%u_%i` detail identity and starts the
shared completion count at zero. The completion helper increments the shared
count, reports `releaseReady` only when the third terminal callback arrives,
and clamps further calls so the native wrapper cannot run beyond the observed
retail release threshold.

Disabled builds zero lifecycle output and return false, preserving the
default-offline behavior required for Steamworks/online-service divergence.

## Open Questions

- The real native adapter object, vtable layout, and deletion owner are still
  not wired into the client. This round models the release decision, not the
  callback allocation itself.
- Client event publication still needs a single owner decision before native
  detail callbacks can replace or coexist with the source-browser
  compatibility publisher.
- The wrapper leaves terminal-callback deduplication to the eventual callback
  owner because the HLIL shows a shared counter rather than per-lane flags.

## Verification

Focused validation passed:

- `python -m pytest tests/test_steamworks_harness.py::test_server_browser_detail_lifecycle_reconstructs_retail_three_callback_release_counter -q --tb=short`
  reported `2 passed`.

Broader validation also passed:

- `python -m pytest tests/test_steamworks_harness.py -q --tb=short`
  reported `76 passed`.
- `python -m pytest tests/test_platform_services.py::test_msbuild_steamworks_sdk_dependency_stays_external_and_optional tests/test_platform_services.py::test_steamworks_modern_adapter_gaps_stay_explicit_until_owned tests/test_platform_services.py::test_client_browser_server_shims_reconstruct_retail_server_browser_surface -q --tb=short`
  reported `3 passed`.
- `git diff --check -- src/common/platform/platform_steamworks.c src/common/platform/platform_steamworks.h tests/steamworks_harness.c tests/test_steamworks_harness.py docs/plans/steamworks-parity-plan.md docs/steam_platform_abstraction.md docs/reverse-engineering/quakelive_steam_mapping_round_309.md`
  reported no whitespace errors; Git only emitted existing line-ending
  normalization warnings for tracked files.

No runtime game launch is needed for this pass; the change is a native wrapper
projection and harness behavior reconstruction.

## Parity Estimate

Before this round, the scoped native server-browser wrapper was about 94%
complete: detail response fields were pinned, but the retained detail-object
completion threshold was still implicit. After this round, the scoped wrapper
is about 95% complete.

For the broader Steamworks subsystem, this keeps the estimate at about 69%
parity with the observed retail Steamworks surface. The release decision is
now explicit, while the callback allocation owner and client publication path
remain open.
