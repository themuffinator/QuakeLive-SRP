# quakelive_steam.exe Mapping Round 246

Date: 2026-05-12

Scope: the retained client browser/workshop `GetAllUGC` integer-contract seam
in `src/code/client/cl_main.c` and
`src/common/platform/platform_steamworks.c`, focused on reconstructing the
retail engine-owned handoff while avoiding external-library implementation
work.

## Summary

This round removes the source-invented `page >= 1` validation from the shared
`GetAllUGC` request path and renames the source-side parameter contract from
`page` to the more faithful generic `filter`. The checked-in browser shim and
Steamworks wrapper were still treating the incoming integer like a bounded
page number, but the committed retail dispatcher and companion decomp both
show a simpler handoff: the browser method coerces its first JS argument with
`ToInteger(...)` and forwards that value directly into
`SteamWorkshop_GetAllUGC(...)`, which in turn passes the same integer through
to the Steam UGC query constructor without a visible minimum-value guard.

Classification mix:

- `0` new engine/client aliases
- `0` engine/client alias renames
- `1` engine/client source reconstruction contract fix
- `1` platform-service-owned function contract fix
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main source-parity win is:

- [`cl_main.c`](../../src/code/client/cl_main.c) and
  [`platform_steamworks.c`](../../src/common/platform/platform_steamworks.c)
  no longer reject `GetAllUGC` requests solely because the incoming integer is
  less than `1`, which brings the browser-to-workshop handoff closer to the
  retained host contract.

## Evidence Notes

Observed facts from the committed retail corpus:

- The retained `qz_instance` `GetAllUGC` dispatcher arm at `0043261F` checks
  only that at least one JS argument is present.
- That same dispatcher arm then calls `Awesomium::JSValue::ToInteger(...)` at
  `00432640` and immediately forwards the resulting integer into
  `sub_460DC0` at `00432641`.
- The committed companion decomp for `SteamWorkshop_GetAllUGC`
  (`0x00460DC0`) shows the function passing its single `param_1` argument
  directly into the Steam UGC `CreateQueryAllUGCRequest(1, 0, appId, appId,
  param_1)` call and then binding the async callback owner
  `SteamCallbacks_OnGetAllUGCQueryCompleted`.
- Neither the retail dispatcher nor the committed companion decomp shows a
  visible `param < 1` rejection in that handoff lane.

Source-side inference used this round:

- The earlier source name `page` was a convenience label, not a retail-backed
  contract. The strongest stable statement the committed evidence supports is
  that the browser passes a single integer filter-like value into
  `SteamWorkshop_GetAllUGC(...)`.
- Keeping the wrapper parameter as `uint32_t` still matches the committed
  companion function signature and the downstream Steam call shape, while
  removing the extra guard avoids imposing a stronger policy than the retained
  host appears to enforce.
- I intentionally did not promote a more specific enum name for the filter,
  because Round 09's open question about the exact semantic meaning of that
  integer is still unresolved.

## Source Reconstruction

- [`cl_main.c`](../../src/code/client/cl_main.c) now exposes
  `CL_Steam_RequestAllUGC( int filter )`, retains only the provider-available
  guard, and forwards the coerced browser integer directly into
  `QL_Steamworks_RequestAllUGCQuery( (uint32_t)filter )`.
- [`client.h`](../../src/code/client/client.h) now mirrors that reconstructed
  parameter name.
- [`platform_steamworks.h`](../../src/common/platform/platform_steamworks.h)
  and [`platform_steamworks.c`](../../src/common/platform/platform_steamworks.c)
  now expose `QL_Steamworks_RequestAllUGCQuery( uint32_t filter )`, remove the
  source-only `filter < 1u` rejection, and pass the same integer through to
  the Steam UGC query constructor.
- [`test_platform_services.py`](../../tests/test_platform_services.py) now pins
  the updated `filter` naming, the absence of the stale `"invalid query page"`
  log branch, and the direct retained-style `createQueryFn(..., filter )`
  handoff.

## Verification

Static/source validation:

- `pytest tests/test_platform_services.py -q --tb=no -k "client_browser_lobby_social_shims_reconstruct_retail_qz_instance_dispatch_surface or client_browser_js_bridge_reconstructs_qz_instance_contract"`
  passed with `2 passed, 73 deselected`
- `git diff --check -- src/code/client/cl_main.c src/code/client/client.h src/common/platform/platform_steamworks.c src/common/platform/platform_steamworks.h tests/test_platform_services.py docs/reverse-engineering/quakelive_steam_mapping_round_246.md`
  reported only the repo's existing LF -> CRLF normalization warnings on the
  touched text files

Additional note:

- Pytest still emitted the existing `.pytest_cache` permission warning, but
  the assertions passed.

Alias accounting for the current dirty worktree:

- before this pass: `2238` raw `quakelive_steam` aliases, `2157` strict
  address-backed aliases
- after this pass: `2238` raw `quakelive_steam` aliases, `2157` strict
  address-backed aliases
- strict Ghidra address-backed coverage after this pass: `39.412%` of `5473`
  committed functions

Parity estimate after this pass:

- strict-retail client browser/workshop `GetAllUGC` integer-contract seam:
  `99%` before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

The next nearby engine-only pass is to keep walking the retained browser and
workshop helpers where the source may still carry user-facing validation or
parameter naming that is stronger than the committed `qz_instance` ownership
evidence supports.
