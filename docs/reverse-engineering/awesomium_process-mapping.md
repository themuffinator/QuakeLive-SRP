# awesomium_process.exe Mapping

## Overview

This pass adds `awesomium_process.exe` to the committed Ghidra reference corpus,
normalizes its function inventory in the shared alias set, and now also anchors
the thin bootstrap reconstruction in `src/code/win32/awesomium_process.cpp`,
and `src/code/awesomium_process.vcxproj`.

Observed facts from the committed corpus:

- `references/reverse-engineering/ghidra/awesomium_process/metadata.txt` reports
  `139` functions, `54` imports, `1` export-like entrypoint label, and a full
  top-function decompile export.
- The PE import table is minimal: `KERNEL32.dll` plus a single Awesomium import,
  `Awesomium::ChildProcessMain`.
- The CodeView debug directory preserves the original PDB path
  `C:\dev\chromium2\chromium\src\build\Release\awesomium_process.pdb`, which
  supports the reading that this executable is an Awesomium/Chromium helper build
  rather than Quake Live-specific game code.

## Ownership

`FUN_00401000` is the only product-specific executable body in the file. It sets
up a standard SEH frame, calls `Awesomium::ChildProcessMain(hInstance)`, and
returns to CRT startup. The rest of the binary is dominated by statically linked
Visual Studio 2010 CRT, locale, exception, and signal-management helpers.

That means the executable itself owns:

- process entry/bootstrap
- CRT error-reporting and signal plumbing
- locale / multibyte-codepage initialization
- resource / manifest hosting

It does not own the browser runtime itself; that behavior still lives in
`awesomium.dll`.

## Source reconstruction status

The repo now reconstructs the full executable-owned behavior:

- `src/code/win32/awesomium_process.cpp` mirrors the owned entry flow as
  `WinMain -> Awesomium::ChildProcessMain(hInstance)`.
- Strict SDK/import-table builds still depend on the external Awesomium SDK
  import library (`awesomium.lib`) instead of generating a repo-local import
  library. SDK-less Release builds keep the same source-owned call target by
  resolving the decorated `Awesomium::ChildProcessMain` symbol dynamically from
  `awesomium.dll`.
- `src/code/awesomium_process.vcxproj` now matches the retail helper's intended
  build profile more closely: static CRT, GUI subsystem version `5.01`,
  `/DYNAMICBASE`, `/NXCOMPAT`, `/TSAWARE`, and the preserved PDB breadcrumb
  `C:\dev\chromium2\chromium\src\build\Release\awesomium_process.pdb`.
- `src/code/win32/awesomium_process.cpp` includes the SDK
  `<Awesomium/ChildProcess.h>` header only when
  `QLUseAwesomiumSdk=1`; otherwise the online helper uses a dynamic loader and
  still does not locally redeclare Awesomium SDK object layouts.

The only intentional divergence is policy-driven: `QLBuildOnlineServices`
defaults to `0` for Debug and ad hoc source builds, which keeps that path on an
offline-safe stub. Windows Release-family builds now opt into
`QLBuildOnlineServices=1` so release artifacts carry the WebUI-capable helper;
add `QLUseAwesomiumSdk=1` when validating the strict retail import-table path.

## Alias policy

The alias set follows the same evidence guardrails used elsewhere in the repo:

- Keep Ghidra/CRT names when they are already specific and stable.
- Promote raw `FUN_...` helpers to descriptive names only when the body gives a
  clear role.
- Normalize `FID_conflict:_memcpy` to `memcpy_or_memmove` because Ghidra already
  proves the routine is the shared copy/move implementation, but the exact public
  export name is ambiguous.
- Keep the two private encoded callback slots as
  `CRT_SetEncodedCallbackSlot0` and `CRT_SetEncodedCallbackSlot1`; the binary
  initializes those globals but never dereferences them, so stronger names would
  overstate the evidence.

## Key promotions

- `FUN_00401000` -> `AwesomiumProcess_RunChildProcessMain`
- `FUN_004043dd` -> `CRT_UpdateThreadMbcInfoToSystemCodePage`
- `FUN_00404869` -> `memcpy_sse2_fastpath`
- `FUN_00402b10` -> `CRT_InitEncodedTerminateHandler`
- `FUN_00402bc2` -> `CRT_UnlockLock`
- `FUN_0040307b` -> `CRT_InvalidParameterNoInfo`
- `FUN_0040197a` -> `_c_exit`
- `FUN_00402ad4` -> `NLG_CallHandler`

The remaining tiny `FUN_...` helpers are mostly duplicated cleanup thunks created
for SEH/finally edges around locale, multibyte-info, and exit-table locks, so
their promoted names stay intentionally literal.

## Coverage impact

On the committed `awesomium_process.exe` Ghidra baseline of `139` functions, this
pass provides a stable alias for every function entry when combined with the
existing Ghidra-recognized CRT names and the new `awesomium_process` section in
`references/analysis/quakelive_symbol_aliases.json`.

On the source side, parity for the executable-owned surface is now effectively
closed: the remaining behavior belongs to `awesomium.dll`, not to
`awesomium_process.exe`.
