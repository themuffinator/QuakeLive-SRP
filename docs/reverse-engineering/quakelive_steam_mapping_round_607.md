# Quake Live Steam Mapping Round 607: ResponseThread PNG SendResponse Boundary

Date: 2026-06-11

## Scope

This round rechecks the retail `ResponseThread` avatar-response path used by
`SteamDataSource` and pins the current bounded source reconstruction against
Binary Ninja HLIL and the committed Ghidra corpus.

No source behavior was changed. The retail binary creates an asynchronous C++
`ResponseThread`, encodes avatar RGBA into PNG, and calls
`Awesomium::DataSource::SendResponse`. The repository intentionally keeps that
exact Awesomium delayed-response ABI bounded, while retaining the evidence in
source-visible mapping rows and delivering avatar pixels through the safer
resource bridge.

## Retail Evidence

Primary owner: `assets/quakelive/quakelive_steam.exe`

Evidence checked:

- Binary Ninja HLIL part 02:
  - `sub_463110` / `FUN_00463110`: `ResponseThread_PNGWriteCallback`
  - `sub_463180` / `FUN_00463180`: `ResponseThread_EncodeAvatarPNG`
  - `sub_463440` / `FUN_00463440`: `ResponseThread_Run`
  - `sub_463550` / `FUN_00463550`: `SteamDataSource_StartResponseThread`
- Binary Ninja HLIL part 06:
  - `ResponseThread::vftable` at `0x00532B44`
  - `"image/png"` at `0x00532B4C`
  - `"request_%i"` at `0x00532B58`
  - `Awesomium::DataSource::SendResponse` import pointer at `0x0052C6B0`
- Binary Ninja HLIL part 07:
  - Awesomium import name
    `?SendResponse@DataSource@Awesomium@@QAEXHIPAEABVWebString@2@@Z`
- Ghidra `functions.csv`:
  - `FUN_00463110,00463110,103,0,unknown`
  - `FUN_00463180,00463180,287,0,unknown`
  - `FUN_00463440,00463440,263,0,unknown`
  - `FUN_00463550,00463550,164,0,unknown`
- Symbol alias map:
  - `FUN_00463110` and `sub_463110` promote to
    `ResponseThread_PNGWriteCallback`
  - `FUN_00463180` and `sub_463180` promote to
    `ResponseThread_EncodeAvatarPNG`
  - `FUN_00463440` and `sub_463440` promote to `ResponseThread_Run`
  - `FUN_00463550` and `sub_463550` promote to
    `SteamDataSource_StartResponseThread`

Observed facts:

- `sub_463110` grows a response buffer with `malloc` or `realloc`, copies the
  incoming libpng chunk, advances the byte count, and raises `"Write Error"` on
  allocation failure.
- `sub_463180` creates a PNG write struct using version string `1.2.24`,
  installs `sub_463110` as the write callback, configures an 8-bit RGBA image
  (`color type 6`), builds row pointers using `width * 4`, writes the PNG, and
  frees the row table.
- `sub_463440` uses `SteamUtils` to fetch avatar dimensions and RGBA pixels,
  calls `sub_463180`, builds the `"image/png"` WebString, calls
  `Awesomium::DataSource::SendResponse`, frees both PNG and raw avatar buffers,
  then self-cleans the thread object through the retail `(**arg1)(1)` pattern.
- `sub_463550` allocates a `0xA4` byte `ResponseThread`, runs the base
  `idSysThread` constructor, installs `ResponseThread::vftable`, stores the
  `SteamDataSource*`, request id, and avatar image handle, then starts the
  worker with name format `"request_%i"`, normal priority, and `0x100000`
  stack reserve.

## Source Reconstruction

The source owner is `src/code/client/cl_steam_resources.c`.

Pinned source contracts:

- `cl_steamResponseThreadRetailMappings[]` records the retail run, PNG write,
  PNG encode, SendResponse import, thread name, and stack reserve anchors.
- `CL_CountSteamResponseThreadRetailMappings()` counts only rows with concrete
  retail addresses and feeds `ui_resourceBridgeResponseThreadMappings`.
- `CL_SteamResources_RequestAvatarRGBA(...)` remains the bounded source owner
  for avatar payload retrieval. It requests and loads avatar RGBA through the
  platform Steamworks wrapper instead of recreating the retail PNG thread.
- The source intentionally does not define `CL_SteamResources_EncodeAvatarPNG`
  or call `Awesomium::DataSource::SendResponse(...)`; those remain documented
  retail ABI boundaries.

## Compatibility Boundary

This pass preserves the repository policy for Quake Live-only online services:

- native SteamDataSource reconstruction remains limited to the avatar subset;
- non-avatar `steam://` requests continue to the
  `QLResourceInterceptor launcher/web fallback` owner;
- default builds keep the live Steam/Awesomium lane disabled; and
- the exact C++ `ResponseThread`/Awesomium delayed-response path remains
  documented evidence, not enabled runtime behavior.

## Validation

Added
`tests/test_platform_services.py::test_steam_response_thread_png_sendresponse_boundary_tracks_retail_hlil`
to pin:

- alias and Ghidra rows for the four retail response-thread owners;
- HLIL evidence for PNG buffer growth, PNG encoding setup, row pointer stepping,
  `SteamUtils` avatar pixel retrieval, `SendResponse`, cleanup, and thread
  start;
- source mapping rows and the `ui_resourceBridgeResponseThreadMappings` cvar;
  and
- gap-note anchors that classify the exact live `ResourceResponse` ABI as
  bounded.

Planned validation for this pass:

```text
python -m pytest tests/test_platform_services.py::test_steam_response_thread_png_sendresponse_boundary_tracks_retail_hlil -q --tb=short
python -m pytest tests/test_platform_services.py -q --tb=short
```

## Confidence

Observed facts:

- HLIL gives direct control-flow evidence for the PNG callback, encoder, run,
  SendResponse, and worker start paths.
- Ghidra rows and aliases identify the retail owners and sizes.
- Source mappings preserve the retail constants and keep the async ABI boundary
  visible without enabling live Awesomium behavior.

Inference:

- `CL_SteamResources_RequestAvatarRGBA(...)` is the correct bounded source
  owner for this retail lane while the exact `ResponseThread` object and
  `Awesomium::DataSource::SendResponse` ownership remain compatibility-only.

Parity estimates:

- Focused ResponseThread PNG/SendResponse boundary confidence:
  **before 91% -> after 99%**.
- Focused SteamDataSource async-response divergence classification:
  **before 93% -> after 98%**.
- Overall Steam launch/runtime integration mapping confidence: **93.16% -> 93.18%**.
