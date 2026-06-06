# Quake Live Steamworks Mapping Round 363

Date: 2026-06-06

Focus: SteamUGC query result, preview URL, and request-release slot mapping
with executable harness coverage.

## Retail Evidence

- Owning binary: `assets/quakelive/quakelive_steam.exe`.
- Canonical HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`.
- `0x00460DF3` dispatches `SteamUGC` slot `0x04` as
  `CreateQueryAllUGCRequest( 1, 0, appId, appId, arg1 )`.
- `0x00460E04` dispatches `SteamUGC` slot `0x0c` to send the query request.
- `0x0045FD88` dispatches `SteamUGC` slot `0x10` while iterating completed
  UGC query rows.
- `0x0045FDAA` dispatches `SteamUGC` slot `0x14` for the preview URL read.
- `0x004613A0` initializes the `SteamUGCQueryCompleted_t` call-result owner.
- Structured companion corpus:
  `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
  imports `SteamUGC`, and
  `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
  identifies the imported
  `CCallResult<class_SteamCallbacks,struct_SteamUGCQueryCompleted_t>` vtable.
- Symbol/name support:
  `references/analysis/quakelive_symbol_aliases.json` maps
  `SteamCallbacks_OnGetAllUGCQueryCompleted` and
  `SteamWorkshop_GetAllUGC`.

## Observed Facts

The source already reconstructs the retained UGC query wrapper family in
`src/common/platform/platform_steamworks.c`:

- `QL_Steamworks_RequestAllUGCQuery` uses slots `0x04` and `0x0c`, passes the
  raw incoming filter value to the create-query call, binds the async
  `SteamUGCQueryCompleted_t` call result, and releases the query on setup
  failure.
- `QL_Steamworks_GetQueryUGCResult` uses slot `0x10`, reads the published-file
  ID at offset `0`, reads title at details offset `0x18`, and reads
  description at details offset `0x99`.
- `QL_Steamworks_GetQueryUGCPreviewURL` uses slot `0x14`.
- `QL_Steamworks_ReleaseQueryUGCRequest` uses slot `0x34`.

Before this pass, the harness executable coverage proved the create/send
filter pass-through and UGC call-result binding, but the row readback,
preview-URL readback, and direct release slot still depended on static source
assertions.

## Source Reconstruction

- Extended `tests/steamworks_harness.c` with mocked `SteamUGC` row readback
  and preview URL slots at vtable offsets `0x10` and `0x14`.
- Reused the reconstructed details offsets `0x18` and `0x99` in the harness
  mock so the public wrapper has to copy title and description from the same
  buffer layout as the retained source model.
- Exported harness wrappers for `QL_Steamworks_GetQueryUGCResult`,
  `QL_Steamworks_GetQueryUGCPreviewURL`, and
  `QL_Steamworks_ReleaseQueryUGCRequest`, including disabled-build stubs that
  zero outputs and do not perform live Steam calls.
- Added mock state and query result controls for published-file ID, title,
  description, preview URL, success/failure results, query handle capture, and
  row index capture.
- Added ctypes coverage proving:
  - successful result readback copies item ID, title, and description;
  - successful preview readback copies the preview URL;
  - release dispatches the same 64-bit query handle through slot `0x34`;
  - result and preview failures clear stale caller buffers; and
  - disabled Steamworks builds retain the offline fallback contract.

## Inference Boundary

This pass does not promote a semantic enum for the `GetAllUGC` integer filter.
Round 246 remains the strongest current filter evidence: the retail-backed
contract is raw integer pass-through into `CreateQueryAllUGCRequest`, not a
source-side page validator. This pass also does not claim live Steam backend
timing, workshop publication availability, or network/service behavior. It
only closes the local wrapper/harness evidence gap for the observed UGC query
readback slots.

## Verification

- `python -m pytest tests/test_steamworks_harness.py::test_ugc_query_result_preview_and_release_use_retail_slots tests/test_steamworks_harness.py::test_all_ugc_query_forwards_filter_to_retail_query_slot tests/test_platform_services.py::test_client_browser_lobby_social_shims_reconstruct_retail_qz_instance_dispatch_surface -q`
  passed with `9 passed`.

## Parity Estimate

- Focused UGC query result/preview/release harness coverage:
  **before 55% -> after 94%**.
- Combined UGC query wrapper and call-result projection:
  **before 96% -> after 98%**.
- Broader Steamworks parity remains approximately **99%** because live backend
  timing, workshop availability, and filter semantic naming remain outside
  this static/harness pass.
