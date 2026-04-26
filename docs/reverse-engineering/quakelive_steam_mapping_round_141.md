# quakelive_steam.exe Mapping Round 141

Date: 2026-04-26

Scope: refreshed largest-unaliased queue after round 140. This pass consumed
the queue-head `zauth.c` authentication lane around `sub_4F67A0`, the adjacent
Win32 networking lifecycle around `sub_4EF250`, a zlib deflate-init pair
headed by `sub_500940`, and a libpng storage-function lane headed by
`sub_50D220`.

## Summary

This round mapped `21` `quakelive_steam.exe` functions from the refreshed
largest-unaliased queue and exact adjacent engine/platform/support neighbors.
Classification mix:

- `5` engine-owned functions
- `7` platform-service-owned functions
- `9` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

No source debt was opened. This pass intentionally favored exact local-source
anchors over speculative owner naming for the still-opaque queue head around
`sub_463980`, `sub_435070`, `sub_440AD0`, and `sub_4109D0`.

This round also corrects the strict Ghidra-backed coverage accounting. The
raw alias corpus still counts every committed alias row, but the
`address-backed` figure below now strictly measures aliases whose key address
exists in `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`.
Under that stricter check, `sub_4EF4F0 -> NET_Restart` remains a useful
HLIL-backed alias but does not increment Ghidra address-backed coverage.

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_4EF250` | `538` | engine-owned | `NET_Config` | High | No source debt; exact Win32 networking enable/disable gate in `win_net.c`, including restart-on-latched-cvar-change behavior and UDP/SOCKS socket teardown. |
| 2 | `sub_4F63D0` | `539` | platform-service-owned | `s_zap_request_new` | High | No engine debt; exact CZMQ `zauth.c` helper that receives and decodes a ZAP request and extracts mechanism-specific frames. |
| 3 | `sub_4F67A0` | `581` | platform-service-owned | `s_self_authenticate` | High | No engine debt; exact `zauth.c` authentication dispatcher over NULL/PLAIN/CURVE/GSSAPI with blacklist/whitelist handling and ZAP reply emission. |
| 4 | `sub_500940` | `541` | CRT/STL/support-library | `deflateInit2_` | High | No engine debt; exact zlib initializer for configurable deflate streams with method/windowBits/memLevel/strategy validation and allocation. |
| 5 | `sub_50D220` | `550` | CRT/STL/support-library | `png_set_IHDR` | High | No engine debt; exact libpng info-storage function that validates IHDR fields, computes channels/pixel depth/rowbytes, and stores the image header. |
| 6 | `sub_4EF320` | `108` | engine-owned | `NET_Init` | High | No source debt; exact Winsock bootstrap path that registers cvars and tail-calls `NET_Config(qtrue)`. |
| 7 | `sub_4EF3C0` | `35` | engine-owned | `NET_Shutdown` | High | No source debt; exact Win32 networking shutdown wrapper over `NET_Config(qfalse)` plus `WSACleanup`. |
| 8 | `sub_4EF3F0` | `35` | engine-owned | `NET_Sleep` | High | No source debt; exact event-wait sleep helper over the SOCKS/UDP wait handle. |
| 9 | `sub_4EF4F0` | `19` | engine-owned | `NET_Restart` | High | No source debt; exact restart wrapper calling the Steam server shutdown/init helpers around `NET_Config(networkingEnabled)`. |
| 10 | `sub_4F6370` | `81` | platform-service-owned | `s_zap_request_destroy` | High | No engine debt; exact destructor for the internal `zap_request_t` frame/string bundle. |
| 11 | `sub_4F65F0` | `58` | platform-service-owned | `s_zap_request_reply` | High | No engine debt; exact CZMQ helper that formats and sends the six-frame ZAP reply. |
| 12 | `sub_4F6630` | `218` | platform-service-owned | `s_authenticate_plain` | High | No engine debt; exact PLAIN username/password verifier against the loaded password hash. |
| 13 | `sub_4F6710` | `104` | platform-service-owned | `s_authenticate_curve` | High | No engine debt; exact CURVE allow-any / certstore membership check. |
| 14 | `sub_4F6780` | `30` | platform-service-owned | `s_authenticate_gssapi` | High | No engine debt; exact GSSAPI allow path that logs the principal/identity pair and returns success. |
| 15 | `sub_500B60` | `38` | CRT/STL/support-library | `deflateInit_` | High | No engine debt; exact zlib wrapper over `deflateInit2_` with default method/windowBits/memLevel/strategy parameters. |
| 16 | `sub_50CE70` | `596` | CRT/STL/support-library | `png_set_cHRM_fixed` | Medium-high | No engine debt; exact fixed-point chromaticity storage path with range/all-zero guards before storing the `cHRM` tuple. |
| 17 | `sub_50D060` | `121` | CRT/STL/support-library | `png_set_gAMA` | High | No engine debt; exact floating-point gamma setter that clamps, converts to fixed-point gamma, and marks the gAMA field valid. |
| 18 | `sub_50D0E0` | `118` | CRT/STL/support-library | `png_set_gAMA_fixed` | High | No engine debt; exact fixed-point gamma setter with negative/overflow guards and synchronized float/fixed storage. |
| 19 | `sub_50D160` | `178` | CRT/STL/support-library | `png_set_hIST` | High | No engine debt; exact hIST allocator/copy helper gated by palette size validity. |
| 20 | `sub_50D450` | `28` | CRT/STL/support-library | `png_set_oFFs` | High | No engine debt; exact offset storage helper setting x/y offsets and unit type. |
| 21 | `sub_50D480` | `462` | CRT/STL/support-library | `png_set_pCAL` | High | No engine debt; exact pCAL allocation/copy helper for purpose string, units string, and parameter vector ownership. |

## Evidence Notes

- `sub_4EF250`, `sub_4EF320`, `sub_4EF3C0`, `sub_4EF3F0`, and
  `sub_4EF4F0` close a coherent engine-owned Win32 networking lifecycle lane
  in [`src/code/win32/win_net.c`](../../src/code/win32/win_net.c). The
  `WSAStartup`, `WSACleanup`, `NET_GetCvars`, `NET_Config`, and
  `SteamServer_Shutdown`/`SteamServer_Init` call patterns line up exactly.
- `sub_4F6370`, `sub_4F63D0`, `sub_4F65F0`, `sub_4F6630`, `sub_4F6710`,
  `sub_4F6780`, and `sub_4F67A0` close the local CZMQ `zauth.c` request,
  reply, and authentication cluster. The internal static-function names are
  anchored directly against upstream
  [`zauth.c`](https://raw.githubusercontent.com/zeromq/czmq/master/src/zauth.c)
  plus the committed HLIL strings and source-path references.
- `sub_500940` and `sub_500B60` are an exact zlib pair from
  [`src/libs/_deps/zlib/deflate.c`](../../src/libs/_deps/zlib/deflate.c). The
  version/stream-size gate, `windowBits`/`memLevel`/`strategy` validation, and
  allocation of `window`/`prev`/`head` match `deflateInit2_` exactly.
- `sub_50CE70`, `sub_50D060`, `sub_50D0E0`, `sub_50D160`, `sub_50D220`,
  `sub_50D450`, and `sub_50D480` close a contiguous libpng storage-function
  lane in [`src/libs/_deps/libpng/pngset.c`](../../src/libs/_deps/libpng/pngset.c).
  The argument shapes, warning strings, field writes, and ownership transfers
  line up with the public `png_set_*` entry points.

## Aliases Added

- `sub_4EF250 -> NET_Config`
- `sub_4EF320 -> NET_Init`
- `sub_4EF3C0 -> NET_Shutdown`
- `sub_4EF3F0 -> NET_Sleep`
- `sub_4EF4F0 -> NET_Restart`
- `sub_4F6370 -> s_zap_request_destroy`
- `sub_4F63D0 -> s_zap_request_new`
- `sub_4F65F0 -> s_zap_request_reply`
- `sub_4F6630 -> s_authenticate_plain`
- `sub_4F6710 -> s_authenticate_curve`
- `sub_4F6780 -> s_authenticate_gssapi`
- `sub_4F67A0 -> s_self_authenticate`
- `sub_500940 -> deflateInit2_`
- `sub_500B60 -> deflateInit_`
- `sub_50CE70 -> png_set_cHRM_fixed`
- `sub_50D060 -> png_set_gAMA`
- `sub_50D0E0 -> png_set_gAMA_fixed`
- `sub_50D160 -> png_set_hIST`
- `sub_50D220 -> png_set_IHDR`
- `sub_50D450 -> png_set_oFFs`
- `sub_50D480 -> png_set_pCAL`

## Coverage

- Raw alias corpus: `1595 -> 1616`
- Strict Ghidra address-backed aliases: `1525 -> 1545`
- Strict Ghidra address-backed coverage: `27.864% -> 28.229%` of `5473`

`sub_4EF4F0 -> NET_Restart` is currently HLIL-backed only and is not present as
a separate function row in the committed Ghidra `functions.csv`, so it raises
the raw alias count without changing the strict Ghidra address-backed count.

## Validation

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
- duplicate-key scan over `references/analysis/quakelive_symbol_aliases.json`
- `git diff --check`

Validation should report JSON parse success, no duplicate keys, and only the
existing CRLF normalization warnings if present.

## Parity Estimate

Parity estimate after this mapping-only pass remains unchanged:

- strict-retail Windows replacement target: `100%` before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

After this round, the refreshed largest-unaliased queue begins with:

| # | Address | Ghidra name | Size |
| ---: | --- | --- | ---: |
| 1 | `0x00463980` | `FUN_00463980` | `592` |
| 2 | `0x00435070` | `FUN_00435070` | `566` |
| 3 | `0x00440AD0` | `FUN_00440ad0` | `560` |
| 4 | `0x004109D0` | `FUN_004109d0` | `559` |
| 5 | `0x004C6BD0` | `FUN_004c6bd0` | `558` |
| 6 | `0x0040B050` | `FUN_0040b050` | `555` |
| 7 | `0x00419AD0` | `FUN_00419ad0` | `555` |
| 8 | `0x0040F7E0` | `FUN_0040f7e0` | `549` |
| 9 | `0x0041CFB0` | `FUN_0041cfb0` | `549` |
| 10 | `0x0042BA60` | `FUN_0042ba60` | `549` |

The next pass should start with `sub_463980`, `sub_435070`, and
`sub_440AD0`, then keep working down the remaining top queue while preserving
the existing classification guardrails on unresolved engine, platform-service,
and support-library rows.
