# quakelive_steam.exe Mapping Round 243

Date: 2026-05-12

Scope: the retained client browser/social overlay-dialog validation seam in
`src/code/client/cl_main.c` and
`src/common/platform/platform_steamworks.c`, focused on reconstructing the
retail engine-owned `ActivateGameOverlayToUser` argument contract while
avoiding external-library implementation work.

## Summary

This round relaxes the reconstructed overlay-to-user dialog validation so the
source no longer rejects empty-but-present dialog strings before the Steam
Friends call. The checked-in wrappers were still enforcing a sharper
`!dialog || !dialog[0]` boundary, while the committed retail browser dispatch
stringifies the dialog argument and forwards it directly into the Steam
Friends `ActivateGameOverlayToUser` call.

Classification mix:

- `0` new engine/client aliases
- `0` engine/client alias renames
- `1` engine/client source reconstruction contract fix
- `1` platform-service-owned function contract fix
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main source-parity wins are:

- [`cl_main.c`](../../src/code/client/cl_main.c) now rejects only a null
  dialog pointer in `CL_Steam_ActivateOverlayToUser(...)`, leaving
  empty-but-present strings to flow through the shared overlay wrapper.
- [`platform_steamworks.c`](../../src/common/platform/platform_steamworks.c)
  now mirrors that contract in `QL_Steamworks_ActivateOverlayToUser(...)`
  instead of short-circuiting on `dialog[0] == '\0'` before the retained
  Steam Friends vtable call.

## Evidence Notes

Observed facts from the committed retail corpus:

- In the retained browser dispatcher, the `ActivateGameOverlayToUser` method
  first converts the user-id argument to a string and parses it through
  `sscanf("%llu", ...)` at `004323b5`.
- The same method arm then converts the dialog argument to a string with
  `Awesomium::JSValue::ToString(...)` and issues the Steam Friends virtual
  call through slot `0x74`:
  - `004323f9` converts argument `0` to a string
  - `00432424` loads the `0x74` vtable slot
  - `00432432` invokes that slot with the converted dialog string
- No empty-string precheck is visible between the dialog string conversion and
  the retained Steam Friends call in that retail path.

Source-side inference used this round:

- The reconstructed source already centralizes this browser-owned behavior in
  `CL_Steam_ActivateOverlayToUser(...)` and
  `QL_Steamworks_ActivateOverlayToUser(...)`, so matching the retail
  null-versus-empty validation boundary at those owners is the cleanest local
  reconstruction.
- The null-pointer guards remain in place because the retail dispatcher still
  passes a concrete string object through the call path, and the current
  writable source has no reason to manufacture a null dialog pointer.

## Source Reconstruction

- [`cl_main.c`](../../src/code/client/cl_main.c) now logs
  `"missing overlay dialog"` only when `dialog` is null in
  `CL_Steam_ActivateOverlayToUser(...)`.
- [`platform_steamworks.c`](../../src/common/platform/platform_steamworks.c)
  now returns `qfalse` only for a null dialog pointer before looking up the
  Steam Friends interface and `0x74` dispatch slot.
- [`test_platform_services.py`](../../tests/test_platform_services.py)
  now pins the relaxed `if ( !dialog )` contract in both the client wrapper
  and the platform-facing overlay owner.

## Verification

Static/source validation:

- `pytest tests/test_platform_services.py -q --tb=no -k "client_browser_lobby_social_shims_reconstruct_retail_qz_instance_dispatch_surface or client_overlay_commands_reconstruct_retail_steam_surface or client_browser_js_bridge_reconstructs_qz_instance_contract"`
  passed with `3 passed, 72 deselected`
- `git diff --check -- src/code/client/cl_main.c src/common/platform/platform_steamworks.c tests/test_platform_services.py docs/reverse-engineering/quakelive_steam_mapping_round_243.md`
  reported only the repo's existing LF -> CRLF normalization warnings on the
  touched text files

Additional note:

- A broader `tests/test_platform_services.py` sweep still encounters the
  existing unrelated `SteamLobby_Init` signature/parity failure outside this
  write scope.

Alias accounting for the current dirty worktree:

- before this pass: `2238` raw `quakelive_steam` aliases, `2157` strict
  address-backed aliases
- after this pass: `2238` raw `quakelive_steam` aliases, `2157` strict
  address-backed aliases
- strict Ghidra address-backed coverage after this pass: `39.412%` of `5473`
  committed functions

Parity estimate after this pass:

- strict-retail client browser/social overlay dialog-validation seam: `99%`
  before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

The next nearby engine-only pass is to keep walking the remaining
browser-driven social methods where the reconstructed source may still impose
slightly stricter argument validation than the retained `qz_instance`
dispatcher appears to carry.
