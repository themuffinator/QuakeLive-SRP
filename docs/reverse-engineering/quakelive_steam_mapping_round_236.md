# quakelive_steam.exe Mapping Round 236

Date: 2026-05-11

Scope: the retained client identity and social-bootstrap seam in
`src/code/client/cl_main.c`, focused on retail engine-owned persona-sync and
command-registration behavior while avoiding external-library implementation
work.

## Summary

This round tightens two small but real retail gaps in the checked-in client
host: local persona changes now resync the player `name` cvar through the
retail persona helper, and the `CL_Init` social/bootstrap registration order
now matches the committed retail lane more closely.

Classification mix:

- `0` new engine/client aliases
- `0` engine/client alias renames
- `2` engine/client source reconstruction behavior fixes
- `1` engine/client source reconstruction ownership/name alignment
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main source-parity wins are:

- [`cl_main.c`](../../src/code/client/cl_main.c) now reconstructs the retail
  local-persona callback gate inside `CL_Steam_Client_OnPersonaStateChange`:
  when the callback targets the local user and the name-change bit is set, the
  source now re-runs `SteamClient_SyncPersonaNameCvar()`.
- [`cl_main.c`](../../src/code/client/cl_main.c) now uses the promoted retail
  helper name `SteamClient_SyncPersonaNameCvar` instead of the older
  compatibility-flavored `CL_Steam_SyncPersonaNameCvar`.
- [`CL_Init`](../../src/code/client/cl_main.c) now registers
  `clientviewprofile` / `clientfriendinvite` before
  `QLWebHost_RegisterCommands()`, then runs persona sync, which matches the
  committed retail registration order much more closely.

## Evidence Notes

- Round 04 already bounded the small retail helper at `0x00460610` as
  `SteamClient_SyncPersonaNameCvar`, with two observed call sites:
  - one during `CL_Init`
  - one from the persona-state callback owner at `0x00460800`
- The committed HLIL for `sub_460800` shows the exact local-user/name-change
  gate:
  - fetch local SteamID
  - compare it against the callback SteamID
  - test `(arg1[2].b & 1) != 0`
  - then call `sub_460610()`
- The committed `CL_Init` lane still shows this ordering:
  1. `sub_4c81d0("clientviewprofile", sub_460e60)`
  2. `sub_4c81d0("clientfriendinvite", sub_460e60)`
  3. `sub_4f3cd0()`
  4. `sub_460610()`
  5. conditional `sub_4cd250("country", sub_460690(...))`
- The checked-in source already had the right broad helpers, but it still:
  - missed the callback-side persona resync
  - called the browser registration helper before the two overlay commands
  - kept the persona helper under a less retail-shaped local name

## Source Reconstruction

- [`cl_main.c`](../../src/code/client/cl_main.c) now calls
  `SteamClient_SyncPersonaNameCvar()` from
  `CL_Steam_Client_OnPersonaStateChange(...)` when:
  - the callback name-change bit is set
  - `QL_Steamworks_GetUserSteamID(...)` succeeds
  - the callback SteamID matches the local SteamID
- [`cl_main.c`](../../src/code/client/cl_main.c) now names the helper
  `SteamClient_SyncPersonaNameCvar`, matching the promoted retail owner.
- [`cl_main.c`](../../src/code/client/cl_main.c) now orders the adjacent
  `CL_Init` social/bootstrap calls as:
  - `clientviewprofile`
  - `clientfriendinvite`
  - `QLWebHost_RegisterCommands()`
  - `SteamClient_SyncPersonaNameCvar()`
  - `CL_Steam_SeedCountryCvar()`

## Verification

Static/source validation:

- `pytest tests/test_engine_client_command_parity.py tests/test_platform_services.py tests/test_engine_cvar_retail_parity.py -q --tb=no -k "steam_command_registration_and_identity_wiring or overlay_commands_reconstruct_retail_steam_surface or client_identity_bootstrap_and_ui_subscription_lanes_stay_explicit or client_social_presence_and_ugc_callback_lanes_stay_explicit or engine_cvar_ninth_client_userinfo_tranche_matches_retail_contracts"`
  passed with `4 passed, 122 deselected`
- `git diff --check -- src/code/client/cl_main.c tests/test_engine_client_command_parity.py tests/test_platform_services.py tests/test_engine_cvar_retail_parity.py`
  reported only the repo's existing LF -> CRLF normalization warnings on the
  touched text files

Alias accounting for the current dirty worktree:

- before this pass: `2238` raw `quakelive_steam` aliases, `2157` strict
  address-backed aliases
- after this pass: `2238` raw `quakelive_steam` aliases, `2157` strict
  address-backed aliases
- strict Ghidra address-backed coverage after this pass: `39.412%` of `5473`
  committed functions

Parity estimate after this pass:

- strict-retail client identity/social bootstrap seam: `99%` before,
  `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

The next nearby engine-only pass is to keep walking the remaining client
bootstrap and callback seams where retail helper ownership is still slightly
flattened in writable source, while continuing to stay out of Steam SDK or
browser-runtime internals.
