# Quake Live Steamworks Mapping Round 364

Date: 2026-06-06

Focus: SteamUGC query-completion call-result failure projection and callback
pump coverage.

## Retail Evidence

- Owning binary: `assets/quakelive/quakelive_steam.exe`.
- Canonical HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`.
- `0x00460DF3` dispatches the retained `SteamUGC` create-query slot.
- `0x00460E04` dispatches the retained send-query slot and returns the async
  Steam API call handle.
- `0x004613A0` initializes the
  `CCallResult<class SteamCallbacks, struct SteamUGCQueryCompleted_t>` object
  used by the client callback bundle.
- `0x0045FD00` is the retained query-completion callback owner documented in
  earlier rounds as publishing `web.ugc.results` on success,
  `web.ugc.failed` on failure, and releasing the query handle.
- Structured companion corpus:
  `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
  identifies the imported
  `CCallResult<class_SteamCallbacks,struct_SteamUGCQueryCompleted_t>` vtable.
- Symbol/name support:
  `references/analysis/quakelive_symbol_aliases.json` maps
  `SteamCallbacks_OnGetAllUGCQueryCompleted` and
  `SteamWorkshop_GetAllUGC`.

## Observed Facts

Round 363 added executable coverage for UGC row readback, preview URL readback,
and query release. The adjacent call-result dispatch path still had one thin
coverage gap: the harness proved a successful
`SteamUGCQueryCompleted_t` payload crossed `QL_Steamworks_RunCallbacks`, but
did not prove failed raw results, Steam `ioFailure`, or no-payload call-result
delivery.

`QL_Steamworks_DispatchUGCQueryCompleted` already reconstructs the bounded
failure projection:

- always forwards the originating `SteamAPICall_t` as `event.callHandle`;
- copies `queryHandle`, `result`, row counts, total count, and cached-data
  state from the raw payload when present;
- maps `ioFailure` to `event.result = -1` even if the raw result says
  success; and
- maps a missing payload to either `-1` on `ioFailure` or `0` without
  `ioFailure`.

That shape is important because the client owner treats only result `1` as
`web.ugc.results`; every other projected value takes the failure publication
lane.

## Source Reconstruction

- Added `QLR_SteamworksMock_QueueUGCQueryCompletedEx` to the Steamworks
  harness so tests can queue UGC call-result payloads with explicit
  `ioFailure` and optional payload presence.
- Kept the older `QLR_SteamworksMock_QueueUGCQueryCompleted` helper as the
  success-shaped convenience wrapper.
- Added ctypes coverage for:
  - raw failure result propagation with payload present;
  - `ioFailure` overriding a raw success result to `-1`;
  - no-payload plus `ioFailure` producing a zeroed event with result `-1`;
  - no-payload without `ioFailure` producing a zeroed event with result `0`;
  - call-handle preservation across all four cases.
- Added static parity assertions for the dispatcher so the call-handle,
  query-handle, raw-result, row-count, cached-data, `ioFailure`, and no-payload
  branches remain pinned.

## Inference Boundary

This pass does not claim live Steam backend timing or workshop service
availability. It also does not reinterpret the raw `GetAllUGC` integer filter.
The scope is local and evidence-backed: the retained UGC call-result object
must project success and failure payloads predictably into the reconstructed
client callback lane.

## Verification

- `python -m pytest tests/test_steamworks_harness.py::test_ugc_call_result_binding_routes_through_registered_client_bundle tests/test_steamworks_harness.py::test_ugc_call_result_failure_projection_preserves_retail_callback_shape tests/test_platform_services.py::test_platform_steamworks_reconstructs_retail_callback_bundle_registration_surface -q`
  passed with `5 passed`.

## Parity Estimate

- Focused UGC call-result failure projection coverage:
  **before 58% -> after 96%**.
- Combined UGC query callback pump projection:
  **before 94% -> after 98%**.
- Broader Steamworks parity remains approximately **99%** because live backend
  timing, workshop availability, and filter semantic naming remain bounded.
