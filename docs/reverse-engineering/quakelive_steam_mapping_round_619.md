# Quake Live Steam Mapping Round 619: UGC Query Call Result Publication Lifecycle

Date: 2026-06-12

## Scope

This round pins the retail Steam Workshop `GetAllUGC` browser method from
launch-time callback bootstrap through runtime query publication:

- `GetAllUGC`
- `SteamWorkshop_GetAllUGC`
- `SteamCallbacks_OnGetAllUGCQueryCompleted`
- `SteamCallbacks_RunUGCQueryCompleted`
- `SteamCallbacks_RunUGCQueryCompletedCallResult`
- `SteamCallbacks_Init`

The focus is the asynchronous `SteamUGCQueryCompleted_t` call-result lane:
create the all-UGC request, send it, bind the call result, publish
`web.ugc.results` or `web.ugc.failed`, and release the SteamUGC query handle.
No live Steam behavior was enabled, and no game launch was required.

## Retail Evidence

Observed Binary Ninja HLIL and Ghidra evidence:

- Alias map:
  - `FUN_0045fd00` -> `SteamCallbacks_OnGetAllUGCQueryCompleted`
  - `FUN_004606b0` -> `SteamCallbacks_RunUGCQueryCompleted`
  - `FUN_004606d0` -> `SteamCallbacks_RunUGCQueryCompletedCallResult`
  - `FUN_00460dc0` -> `SteamWorkshop_GetAllUGC`
  - `FUN_004613a0` -> `SteamCallbacks_Init`
- Ghidra function rows keep the relevant bodies at `0045fd00`, `004606b0`,
  `004606d0`, `00460dc0`, and `004613a0`.
- Ghidra imports confirm `SteamAPI_RegisterCallResult`,
  `SteamAPI_UnregisterCallResult`, `SteamAPI_RegisterCallback`, `SteamUGC`,
  and `SteamUtils` are part of the retained retail Steam surface.
- Ghidra analysis symbols expose
  `CCallResult<class_SteamCallbacks,struct_SteamUGCQueryCompleted_t>::vftable`
  and its RTTI metadata.
- HLIL `sub_460dc0` obtains the retail app id from `SteamUtils`, calls
  `ISteamUGC::CreateQueryAllUGCRequest` slot `0x04` with query type `1`,
  matching type `0`, creator/consumer app ids, and the raw incoming filter,
  then sends the query through slot `0x0c`.
- HLIL `sub_460dc0` unregisters any previous call result, stores the new
  low/high call handle, stores `sub_45fd00` as the completion target, and
  registers the call result through `SteamAPI_RegisterCallResult`.
- HLIL `sub_45fd00` reads each result through SteamUGC slot `0x10`, reads the
  preview URL through slot `0x14`, builds title/description/id/image rows,
  publishes `web.ugc.results`, and releases the query through slot `0x34`.
- HLIL failure handling releases the query and publishes `web.ugc.failed`.
- HLIL `sub_4613a0` constructs the
  `CCallResult<class SteamCallbacks, struct SteamUGCQueryCompleted_t>` object
  with callback id `0xd49`, and `sub_461500` stores it in `data_e2c20c`.
- HLIL strings preserve `GetAllUGC`, `web.ugc.results`, and
  `web.ugc.failed`.

## Source Reconstruction

SRP already has the source reconstruction for this lane; this round adds the
explicit parity gate tying the source behavior to the reference corpus:

- browser bridge:
  - `GetAllUGC` retains retail method slot `0x0055C170`
  - `QLJSHandler_OnMethodCall`
  - `CL_Steam_RequestAllUGC`
- platform request wrappers:
  - `QL_Steamworks_RequestAllUGCQuery`
  - `QL_Steamworks_GetQueryUGCResult`
  - `QL_Steamworks_GetQueryUGCPreviewURL`
  - `QL_Steamworks_ReleaseQueryUGCRequest`
  - retail `ReleaseQueryUGCRequest` slot ownership through SteamUGC vtable
    slot `0x34`
- call-result lifecycle:
  - `QL_STEAM_CALLBACK_UGC_QUERY_COMPLETED` = `0xd49`
  - `ql_steam_ugc_query_completed_raw_t`, size `0x18`
  - `QL_Steamworks_DispatchUGCQueryCompleted`
  - `QL_Steamworks_BindUGCQueryCallResult`
  - `QL_Steamworks_UnbindCallResultObject`
- client publication owner:
  - `SteamCallbacks_Init`
  - `CL_Steam_Client_OnUGCQueryCompleted`
  - `CL_Steam_BuildUGCQueryResultsJson`

The retained source deliberately keeps the `GetAllUGC` filter as a raw integer
contract. The filter labels document this as `raw GetAllUGC integer filter`
with an `unpromoted GetAllUGC filter semantic`, because the retail references
prove forwarding and vtable shape more strongly than they prove a safe public
enum name for every accepted value.

## Compatibility Boundary

This remains an explicit online-service divergence boundary. In default/offline
builds, the disabled `platform_steamworks.h` stubs return unavailable labels,
reject UGC requests, clear result/preview buffers, no-op the release call, and
reject call-result binding. Live Steam behavior stays behind
`QL_BUILD_ONLINE_SERVICES`.

When online services are enabled, SRP mirrors the retail observable contract:

1. the browser method forwards one coerced integer filter;
2. the platform layer creates and sends one all-UGC query;
3. the async call result is bound to the client callback bundle;
4. successful results publish `web.ugc.results` as a JSON array of
   title/description/id/image rows;
5. failed or I/O-failed results publish `web.ugc.failed`; and
6. every delivered completion releases the query handle.

## Validation

New focused parity gate:

```powershell
python -m pytest tests/test_platform_services.py::test_steam_ugc_query_call_result_publication_lifecycle_tracks_round_619 -q --tb=short
```

The gate checks aliases, Ghidra function/import rows, analysis symbols, HLIL
callback/request/call-result bodies, HLIL string and vtable anchors, the web
method binding, source-side request forwarding, call-result bind/unbind
ownership, raw ABI layout, callback id, dispatch projection, JSON publication,
release ordering, disabled-header stubs, harness coverage, this round note, and
the Task A488 planning anchor.

## Confidence

- Focused Steam `GetAllUGC` async request/call-result confidence:
  **before 94% -> after 99%**.
- Focused UGC browser publication/release confidence:
  **before 94% -> after 99%**.
- Overall Steam launch/runtime integration mapping confidence:
  **93.40% -> 93.42%**.
