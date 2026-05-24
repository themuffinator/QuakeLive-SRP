# Quake Live Steam Mapping Round 287

Date: 2026-05-24

Scope: Awesomium `QLResourceInterceptor` host/filter reconstruction and source
wiring in `src/code/client/cl_steam_resources.c`.

## Evidence

Primary retail signals:

- `references/analysis/quakelive_symbol_aliases.json` promotes
  `sub_434600` as `QLResourceInterceptor_OnFilterNavigation` and `sub_434620`
  as `QLResourceInterceptor_OnRequest`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
  shows `0x00434600` returning false unconditionally. This matches the
  Awesomium `ResourceInterceptor::OnFilterNavigation` slot behavior.
- The `QLResourceInterceptor::vftable` at `0x00547f94` lists
  `vFunc_0 = sub_434620` and `vFunc_1 = sub_434600`, giving a direct vtable
  ownership link between the request path and the filter path.
- `0x00434620` reads the `fs_webpath` cvar, extracts `WebURL::host`,
  `WebURL::path`, and `WebURL::filename`, and compares the host against the
  two-byte string `data_52cbfc`, observed as `ql`.
- The same function compares the path against `data_52cbf0`, observed as
  `/screenshot`, then builds a path from `fs_homepath`, `fs_game`,
  `screenshots/`, and the WebURL filename.
- For non-screenshot requests with host `ql`, the function combines
  `fs_webpath` with the WebURL path and creates an
  `Awesomium::ResourceResponse`. Non-`ql` requests return null.

Companion string anchors:

| Address | String | Observed use |
|---|---|---|
| `0x0052cbe0` | `screenshots/` | Screenshot local path segment. |
| `0x0052cbf0` | `/screenshot` | Special resource-interceptor path prefix. |
| `0x0052cbfc` | `ql` | Retail resource-interceptor host. |
| `0x0052cc00` | `fs_webpath` | Web root cvar used for normal `ql` host resources. |

## Source Reconstruction

The source now carries the retail host/filter lane explicitly:

- `QLResourceInterceptor_OnFilterNavigation()` mirrors `sub_434600` by
  returning `qfalse` for every URL.
- `QL_RESOURCE_INTERCEPTOR_HOST` preserves the retail `ql` host literal.
- `QL_RESOURCE_INTERCEPTOR_SCREENSHOT_PATH` preserves the retail
  `/screenshot` path literal.
- `QLResourceInterceptor_ParseURL()` extracts host, path, and filename fields
  matching the HLIL's use of `WebURL::host`, `WebURL::path`, and
  `WebURL::filename`.
- `QLResourceInterceptor_BuildMappedRequest()` keeps the special screenshot
  branch separate from the normal web-root branch.
- `QLResourceInterceptor_RequestRetailHost()` resolves the mapped request
  through `CL_LauncherRequestData()` and carries the resulting buffer and MIME
  type back to the existing data-source response object.
- `QLResourceInterceptor_OnRequest()` now checks the filter callback, tries the
  Steam data source, tries the recovered `ql` host branch, and only then falls
  back to the broader launcher compatibility request.

Because this repository keeps Quake Live-only online/resource services behind
`QL_BUILD_ONLINE_SERVICES`, the source projection maps retail paths onto the
already documented open fallback roots:

- `asset://ql/screenshot/<name>` becomes `quakelive://screenshots/<name>`,
  which uses the existing home screenshot mapping.
- `asset://ql/<path>` becomes `https://cdn.quakelive.com/<path>`, which uses
  the existing web-root mapping.

This is a deliberate source-visible reconstruction of the retail branch shape,
not a claim that the default build recreates Awesomium's exact
`ResourceResponse::Create` object lifetime or live service behavior.

## Guardrails

Observed:

- Retail `OnFilterNavigation` returns false.
- Retail `OnRequest` owns the `ql` host, `/screenshot` path, `fs_webpath`, and
  screenshot local path split.
- The vtable ties `sub_434620` and `sub_434600` to
  `QLResourceInterceptor`.

Inferred:

- The repository's `asset://ql/...` projection is the closest open fallback
  expression of the retail `ql` host path because the source does not keep a
  live Awesomium C++ `ResourceResponse` owner in default builds.
- Screenshot requests intentionally route through the pre-existing
  `quakelive://screenshots/` fallback root instead of directly constructing
  `fs_homepath/fs_game/screenshots/` in `cl_steam_resources.c`.

Still bounded:

- The source does not recreate Awesomium's concrete C++ `ResourceResponse`
  allocation ABI.
- Steam-backed data source response threading remains a bounded compatibility
  lane covered by earlier `cl_steam_resources.c` notes.
- Default builds continue to disable live online services by policy.

## Validation

New and updated static coverage:

- `tests/test_awesomium_browser_parity.py` checks the filter function, `ql`
  host literal, `/screenshot` branch, mapped fallback roots, and ordering before
  the generic launcher fallback.
- `tests/test_platform_services.py` checks that the recovered branch survives
  the online-service-disabled compatibility policy.
- `tools/ci/verify-awesomium-browser-host-parity.ps1` now verifies source,
  alias, and mapping anchors for this round.

## Parity Movement

Before this round, the Awesomium resource-interceptor source reconstruction was
about 78% closed for the recovered host/filter lane: the broad request fallback
existed, but the `QLResourceInterceptor_OnFilterNavigation`, `ql` host, and
`/screenshot` path split were not source-visible.

After this round, the lane is about 94% source-reconstructed and 97% mapped.
The remaining delta is the intentional default-build compatibility boundary:
literal Awesomium `ResourceResponse` allocation, live service behavior, and
SteamDataSource asynchronous completion are still bounded rather than recreated
as default behavior.
