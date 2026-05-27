# Clean-room reverse builds

## Overview
The clean-room prototypes for the Quake Live client and gameplay frame loops live
under `src-re/prototypes/`. They are compiled alongside the legacy QVM
artifacts so the deterministic harnesses can exercise both implementations.
The build scripts emit shared objects or DLLs under `build/re/` so local tooling
and CI can locate the binaries without hard-coding platform-specific paths.

These prototypes are not the Linux/macOS product build. Hosted push and nightly
workflows now use `tools/ci/build-posix-native.sh` for native POSIX packages
from the real `src/code` tree, while this clean-room lane remains a narrow
reverse-harness target.

## Building locally

### Linux / macOS

Use the helper script to compile the clean-room shared-library artefacts:

```bash
./tools/ci/build-cleanroom.sh
```

Linux outputs are written to `build/re/linux/` with a `.so` extension. macOS
outputs are written to `build/re/macos/` with a `.dylib` extension. Override
compiler settings with the following environment variables when required:

- `QLR_RE_CC` – alternate compiler (defaults to `gcc`).
- `QLR_RE_CFLAGS` – additional C compiler flags (`-std=c99 -Wall -Wextra -O2 -fPIC` by default).
- `QLR_RE_LDFLAGS` – linker flags (defaults to `-shared` on Linux and `-dynamiclib` on macOS).
- `QLR_RE_BUILD_ROOT` – alternate output directory.

### Windows

Run the existing Visual Studio build script, which now also drives the
clean-room modules via `cl.exe`:

```powershell
pwsh tools/ci/build-windows-dlls.ps1
```

The helper writes DLLs to `build\re\windows\`. Extend the compiler flags by
setting `QLR_RE_MSVC_FLAGS` before invoking the script (for example to add `/Zi`
for debug symbols).

## Deterministic trace harness

The reverse binaries are exercised by the deterministic trace harness via
`tests/run_harnesses.py`:

```bash
python tests/run_harnesses.py --target re --reverse-build-root build/re/linux
```

The runner binds deterministic contexts into the shared objects, produces a
normalised log (`logs/re/native-shim.log`), and stores artefacts under
`artifacts/tests/trace/re/latest/`. Pointer values are normalised to `0xPTR` so the log
remains stable across runs. Expectation data lives in
`tests/expectations/re/native-shim.log` and is diffed against the observed log to
highlight regressions.

## CI expectations

The hosted build workflows compile native POSIX outputs from `src/code` on both
Linux and macOS. `Push Verification` runs Linux and macOS native build jobs on
every push, while `Nightly Build` publishes tarballs and manifests from
`build/posix/linux/dist/` and `build/posix/macos/dist/` with 30-day retention.
The native POSIX helper builds the current baseq3 `cgame`, `qagame`, and `ui`
shared modules from the same source lists used by the native project files, then
builds the dedicated host from the Unix makefile, with Quake Live online-service
adapters disabled by default.

The `Deterministic Harnesses` workflow now includes a `Reverse` leg that runs on
`ubuntu-latest`. It

1. builds the clean-room `.so` files via `tools/ci/build-cleanroom.sh`,
2. executes `tests/run_harnesses.py --target re` pointing at `build/re/linux`, and
3. publishes the normalised log plus diff artefacts.

The upload step persists `${ARTIFACT_ROOT}/trace/**/*.log` and
`${ARTIFACT_ROOT}/trace/**/*.diff` alongside the existing match and client
outputs so regressions are easy to inspect from CI.
