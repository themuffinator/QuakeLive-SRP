# Quake Live Steam Host Mapping Round 301

## Scope

This round reconciles the client browser compatibility telemetry with the
native `ISteamMatchmakingServers` wrapper reconstructed in rounds 297-300. It
does not wire the client browser onto the native wrapper; it corrects the
source-facing label so the remaining gap is recorded as missing client
integration rather than missing low-level wrapper coverage.

Evidence order:

- `docs/reverse-engineering/quakelive_steam_mapping_round_181.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_297.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_298.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_299.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_300.md`
- `src/code/client/cl_main.c`
- `tests/test_platform_services.py`

## Observed Facts

Round 181 documents the retained client browser methods as source-backed
compatibility mappings: internet/LAN/favorites use the inherited Quake browser
source lanes, while friends and history are mapped onto the nearest retained
source lists. That compatibility behavior is still present in
`CL_Steam_RequestServers`.

Rounds 297-300 changed the lower layer. `platform_steamworks.[ch]` now exposes
build-gated wrappers for the observed `ISteamMatchmakingServers` list request
slots, request refresh/release, `GetServerDetails`, ping/rules/player detail
queries, typed row projection, empty-name display fallback, and the adjacent
`CancelServerQuery` primitive.

The client telemetry still described the native browser gap as
`missing ISteamMatchmakingServers adapter`, which was accurate before the
wrapper reconstruction but is now too broad. The remaining observed gap is that
`CL_SteamBrowser_*` has not been wired to own the native request handles,
publish native rows, or drive the detail-query lifecycle.

## Source Reconstruction

`CL_SteamBrowser_NativeAdapterGapLabel` now returns:

- `ISteamMatchmakingServers wrapper not client-wired`

The JSON event shape remains unchanged. The payload still publishes
`nativeAdapterGap`, alongside the compatibility owner
`source-browser compatibility`, the missing native product owner
`ISteamMatchmakingServers`, and the friends/history mapping reason. This keeps
existing diagnostics stable while correcting the meaning of the value.

The source-bound Steamworks tests were updated to pin the new label in both
the general modern-adapter guard and the client browser server-shim guard.

## Open Questions

- Which owner should replace the current source-backed friends/history mapping
  when the client browser is finally wired to native
  `ISteamMatchmakingServers` request handles?
- Should request cancellation be driven from an explicit client refresh/cancel
  owner, or should the reconstructed detail-query callbacks continue to rely on
  the completion counters observed in the current HLIL slice?
- How should native server rows be published into the retained browser event
  stream without breaking the offline/source-browser compatibility mode?

## Verification

Focused validation passed:

- `python -m pytest tests/test_platform_services.py::test_steamworks_modern_adapter_gaps_stay_explicit_until_owned -q --tb=short`
- `python -m pytest tests/test_platform_services.py::test_client_browser_server_shims_reconstruct_retail_server_browser_surface -q --tb=short`
- `python -m pytest tests/test_steamworks_harness.py -q --tb=short`
- The combined pytest run reported `66 passed`.
- `git diff --check -- src/code/client/cl_main.c tests/test_platform_services.py docs/plans/steamworks-parity-plan.md docs/steam_platform_abstraction.md docs/reverse-engineering/quakelive_steam_mapping_round_301.md`
  reported no whitespace errors.

No runtime game launch is needed for this pass; the change is a source-bound
telemetry correction.

## Parity Estimate

Before this round, the scoped client browser integration labeling was about
60% complete: source-backed compatibility was visible, but the label still
claimed the native adapter was missing outright. After this round, the scoped
labeling is about 70% complete because it now distinguishes an existing
low-level wrapper from the still-open client product wiring.

For the broader Steamworks subsystem, this keeps the estimate at about 67%
parity with the observed retail Steamworks surface. It improves map accuracy
and source reconstruction around the server-browser boundary without changing
runtime browser behavior.
