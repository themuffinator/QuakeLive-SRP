# Retail Windows Toolchain Audit

This note records the build-tool evidence recoverable from the retail Quake
Live Windows binaries and the project settings the repo now uses to stay as
close to that retail toolchain shape as possible.

## Evidence summary

Observed facts from the retail PE headers and debug directories:

- `quakelive_steam.exe`, `cgamex86.dll`, `qagamex86.dll`, `uix86.dll`, and
  `awesomium_process.exe` all report linker version `10.0`.
- The same binaries all target Win32 (`IMAGE_FILE_MACHINE_I386`) with subsystem
  version `5.1`, `SectionAlignment=4096`, and `FileAlignment=512`.
- The id-built binaries carry CodeView PDB paths rooted at
  `W:\quakelive_clean\...`:
  - `W:\quakelive_clean\quakelive_steam.pdb`
  - `W:\quakelive_clean\baseq3\cgamex86.pdb`
  - `W:\quakelive_clean\baseq3\game.pdb`
  - `W:\quakelive_clean\baseq3\ui.pdb`
- `awesomium_process.exe` is a vendor helper and carries
  `C:\dev\chromium2\chromium\src\build\Release\awesomium_process.pdb`.
- `quakelive_steam.exe` and `awesomium_process.exe` are linked at image base
  `0x400000`.
- Retail `cgamex86.dll`, `qagamex86.dll`, and `uix86.dll` are all linked at
  preferred base address `0x10000000`.
- `quakelive_steam.exe` and `awesomium_process.exe` carry
  `DYNAMIC_BASE | NX_COMPAT | TERMINAL_SERVER_AWARE`.
- The three gameplay/UI DLLs carry `DYNAMIC_BASE | NX_COMPAT`.
- `cgamex86.dll`, `qagamex86.dll`, `uix86.dll`, and `awesomium_process.exe`
  contain load-config entries with security cookies and SafeSEH handler tables.
- `quakelive_steam.exe` does not contain a load-config table in the shipped
  retail image.
- The retail launcher reserves the default `1 MB` stack (`1048576`) and commits
  `4096` bytes.

Inference from the Rich headers:

- Repeated Rich-header build markers `40219` are consistent with the Visual C++
  2010 SP1 toolchain family. The repo therefore treats VC++ 2010 SP1-era
  compiler/linker output as the closest documented match for the id-built
  Windows binaries.

## Retail CRT split

Observed fact from the import tables:

- `quakelive_steam.exe`, `cgamex86.dll`, and `uix86.dll` import
  `MSVCR100.dll`.
- `qagamex86.dll` imports both `MSVCR100.dll` and `MSVCP100.dll`.
- `awesomium_process.exe` does not import `MSVCR100.dll` or `MSVCP100.dll`.

Inference:

- The retail launcher and gameplay/UI modules were linked against the dynamic
  VC++ 2010 CRT (`/MD`-style).
- The shipped `awesomium_process.exe` helper used a static CRT path (`/MT`-style).

## Repository settings that now match retail more closely

The retail-facing project files now default to:

- `ToolsVersion="4.0"` for the VS2010/MSBuild 4.0 project model.
- `PlatformToolset=v100`.
- `/MD` or `/MDd` for `quakelive_steam.exe`, `qagamex86.dll`,
  `cgamex86.dll`, and `uix86.dll`.
- `/MT` or `/MTd` for `awesomium_process.exe`.
- `MinimumRequiredVersion=5.01` so the emitted PE subsystem version stays at
  Windows XP (`5.1`), matching retail.
- `RandomizedBaseAddress=true` and `DataExecutionPrevention=true` for the
  retail-facing binaries that ship with `DYNAMIC_BASE` and `NX_COMPAT`.
- `TerminalServerAware=true` for the two retail executables.
- `ImageHasSafeExceptionHandlers=true` for `qagamex86.dll`, `cgamex86.dll`,
  `uix86.dll`, and `awesomium_process.exe`.
- `BaseAddress=0x10000000` for the three gameplay/UI DLLs.
- `StackReserveSize=1048576` for `quakelive_steam.exe`.
- `ProgramDatabaseFile=$(OutDir)game.pdb` for `qagamex86.dll`, matching the
  retail debug-directory filename.
- `GenerateManifest=false` for the two executable projects so the checked-in
  manifest resources, rather than linker-generated defaults, define the shipped
  application metadata.

## Version resources and manifests

Observed facts from the retail executable resources:

- `quakelive_steam.exe` ships only icon/group-icon, version-info, and manifest
  resources; it does not ship a string-table resource.
- The retail launcher version resource reports:
  - `FileDescription=Quake Live`
  - `InternalName=Quake Live`
  - `OriginalFilename=quake3.exe`
  - `ProductName=quake3`
- `awesomium_process.exe` ships version-info and a minimal `asInvoker`
  manifest.
- The retail launcher manifest includes:
  - `requestedExecutionLevel level="asInvoker"`
  - `Microsoft.Windows.Common-Controls` version `6.0.0.0`
  - `Microsoft.VC80.CRT` version `8.0.50727.762`
- The checked-in launcher manifest also carries the modern DPI-awareness block
  used by the current Win32 host glue; `tools/ci/audit-retail-metadata.ps1`
  treats that block as part of the source-visible metadata contract so the
  modern compatibility lane and renderer host tests agree.

The repo now stages those executable metadata resources explicitly in:

- `src/code/win32/winquake.rc`
- `src/code/win32/awesomium_process.rc`
- `src/code/win32/quakelive_steam.manifest`
- `src/code/win32/awesomium_process.manifest`

## External vendor binaries

The repo does not attempt to rebuild Awesomium, Steamworks, ANGLE, FFmpeg, or
other third-party payload DLLs. Those remain exact retail binaries staged from
`assets/quakelive/`, which is the closest possible match.

## Verification

Run:

```powershell
pwsh tools\ci\audit-retail-toolchain.ps1
pwsh tools\ci\audit-retail-metadata.ps1
```

Use `-Strict` to also fail when the local machine does not have a usable
`v100` toolset installed.
