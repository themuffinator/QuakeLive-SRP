# Quake Live Steam Host Mapping Round 302

## Scope

This round promotes the retail `JSBrowser_RequestServers` request-mode and
filter contract into named Steamworks wrapper helpers. It keeps the client on
the source-backed compatibility browser path, but makes the native wrapper's
mode behavior explicit and test-pinned for a future client owner.

Evidence order:

- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `docs/reverse-engineering/quakelive_steam_mapping_round_297.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_301.md`
- `src/common/platform/platform_steamworks.[ch]`
- `tests/steamworks_harness.c`
- `tests/test_steamworks_harness.py`

## Observed Facts

The retained `JSBrowser_RequestServers` owner builds a single
`gamedir=baseq3` matchmaking filter before dispatching most request modes. The
mode switch maps:

| JS mode | Steamworks slot | Filter |
| --- | --- | --- |
| `0` or invalid/default | `RequestInternetServerList` at vtable offset `0x00` | `gamedir=baseq3` |
| `1` | `RequestLANServerList` at vtable offset `0x04` | none |
| `2` | `RequestFriendsServerList` at vtable offset `0x08` | `gamedir=baseq3` |
| `3` | `RequestFavoritesServerList` at vtable offset `0x0c` | `gamedir=baseq3` |
| `4` | `RequestHistoryServerList` at vtable offset `0x10` | `gamedir=baseq3` |

The HLIL branch `arg2 - 1 u> 3` sends mode `0` and out-of-range values through
the internet request path, so the source wrapper should treat invalid modes as
internet/default rather than inventing a separate error mode.

## Source Reconstruction

`platform_steamworks.[ch]` now exposes two request-mode helpers:

- `QL_Steamworks_GetServerBrowserRequestModeLabel`
- `QL_Steamworks_ServerBrowserRequestModeUsesGamedirFilter`

The enabled wrapper returns stable labels for `internet`, `lan`, `friends`,
`favorites`, and `history`, with invalid/default modes labeled `internet`.
The disabled inline wrapper keeps the same source-level labels, since this is
an observed ABI contract rather than a live Steamworks capability.

`QL_Steamworks_RequestServerList` now calls the filter predicate before
constructing the `gamedir=baseq3` filter, so LAN remains the only unfiltered
path and invalid/default modes explicitly keep the internet filter behavior.

The Steamworks harness exports the helper labels/predicate and extends the
server-browser slot test so both enabled and disabled builds pin:

- the five retained labels;
- invalid/default mode labeling as `internet`;
- LAN as the only no-filter mode; and
- invalid/default dispatch through the internet list slot with
  `gamedir=baseq3`.

## Open Questions

- Client ownership is still open: `CL_SteamBrowser_*` does not yet allocate a
  native `JSBrowser`-style owner or publish native row events.
- The native owner still needs a deliberate state/lifecycle reconstruction for
  the retail refresh flag and previous-request release behavior before it can
  replace the compatibility browser lane.

## Verification

Focused validation passed:

- `python -m pytest tests/test_steamworks_harness.py::test_server_browser_helpers_use_mapped_matchmaking_servers_slots -q --tb=short`
  reported `2 passed`.
- `python -m pytest tests/test_steamworks_harness.py -q --tb=short`
  reported `64 passed`.
- `python -m pytest tests/test_platform_services.py::test_steamworks_modern_adapter_gaps_stay_explicit_until_owned tests/test_platform_services.py::test_client_browser_server_shims_reconstruct_retail_server_browser_surface -q --tb=short`
  reported `2 passed`.
- `git diff --check -- src/common/platform/platform_steamworks.c src/common/platform/platform_steamworks.h tests/steamworks_harness.c tests/test_steamworks_harness.py src/code/client/cl_main.c docs/plans/steamworks-parity-plan.md docs/steam_platform_abstraction.md docs/reverse-engineering/quakelive_steam_mapping_round_302.md`
  reported no whitespace errors.

No runtime game launch was needed; this pass covered wrapper mapping and
harness behavior only.

## Parity Estimate

Before this round, the scoped native server-browser request-mode wrapper was
about 78% complete: the slots were wired, but the mode/filter contract was
implicit inside `RequestServerList`. After this round, the scoped wrapper is
about 81% complete because the retail mode labels, filter predicate, and
default-to-internet behavior are named and tested.

For the broader Steamworks subsystem, this keeps the estimate at about 67%
parity with the observed retail Steamworks surface. It tightens the native
server-browser wrapper map without changing product browser behavior.
