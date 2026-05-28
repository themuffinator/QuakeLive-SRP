# Quake Live Steam Mapping Round 332: Awesomium SDK Dependency Hygiene

Date: 2026-05-28

Scope: Awesomium WebUI SDK/runtime dependency boundary, helper-process linkage,
and removal of local SDK ABI replication.

## Evidence Checked

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt`
  maps the retail browser host calling Awesomium C++ constructors, WebCore,
  WebSession, WebView, and `WebKeyboardEvent` seams.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part07.txt`
  records imported Awesomium names such as
  `??0WebKeyboardEvent@Awesomium@@QAE@IIJ@Z`.
- `references/reverse-engineering/ghidra/awesomium_process/decompile_top_functions.c`
  reduces the helper executable's source-owned behavior to
  `Awesomium::ChildProcessMain(hInstance)`.
- The local source audit found no committed Awesomium SDK headers or libraries,
  and found the helper project generating `awesomium_import.lib` from a local
  `.def` file.

## Source Reconstruction

- Removed the local C++ ABI fallback layer from `cl_awesomium_win32.cpp`:
  `__thiscall` typedefs, vtable slot dispatch helpers, local object storage,
  decorated constructor lookups, and raw `BitmapSurface` field offsets are no
  longer present.
- Kept the live client adapter on external Awesomium SDK C API exports from
  `awesomium.dll`. Optional SDK exports remain optional; missing required
  exports now report explicit SDK-export diagnostics.
- Corrected the keyboard event path to the SDK event-object sequence:
  `_Awe_new_WebKeyboardEvent_1@12`,
  `_Awe_WebView_InjectKeyboardEvent@8`, and
  `_Awe_delete_WebKeyboardEvent@4`.
- Corrected the transparent-state import to `_Awe_WebView_SetTransparent@8`.
- Stopped treating `_Awe_WebSession_Release@4` as a cache-clear export. It is
  now used only to release the WebSession during shutdown; `CL_Awesomium_ClearCache`
  is a documented no-op until a real public cache-clear SDK export is identified.
- Replaced `src/code/win32/awesomium.def` with an external SDK dependency:
  `awesomium_process.vcxproj` requires `AwesomiumSdkDir` or `AWESOMIUM_SDK_DIR`
  when `QLBuildOnlineServices=1` and links `awesomium.lib`.
- `quakelive_steam.vcxproj` now declares the external Awesomium SDK/runtime
  dependency for online builds and can copy `awesomium.dll` from the SDK runtime
  folder.
- `awesomium_process.cpp` includes `<Awesomium/ChildProcess.h>` instead of
  locally redeclaring `Awesomium::ChildProcessMain`.
- `awesomium_process.rc` now carries project-owned version metadata, avoiding an
  accidental claim that the rebuilt helper is an Awesomium Technologies binary.

## Validation

Validation for this round is recorded in `IMPLEMENTATION_PLAN.md` Task A116.
Runtime launch was not required: the task is a source/build dependency-boundary
correction, and the relevant claims are covered by source inspection, MSBuild
metadata, pytest anchors, and the Awesomium browser-host verifier.

## Parity Estimate

- Focused Awesomium SDK-clean integration lane: **64% -> 94%**.
- Overall Awesomium WebUI wiring remains **99.0% -> 99.0%**. Behavior parity is
  not increased by removing SDK replication, but the implementation is now more
  faithful to the repository policy that proprietary Awesomium code remains an
  external dependency.
- Repo-wide parity remains **98% -> 98%** because online-service behavior is
  still intentionally gated behind `QL_BUILD_ONLINE_SERVICES` and native JS
  object marshalling remains mapped rather than fully reconstructed.
