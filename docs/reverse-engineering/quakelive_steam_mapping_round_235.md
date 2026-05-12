# quakelive_steam.exe Mapping Round 235

Date: 2026-05-11

Scope: the retained client Steam callback-bootstrap ownership seam in
`src/code/client/cl_main.c`, focused on reconstructing retail engine-owned
helper boundaries while avoiding external-library implementation work.

## Summary

This round splits the checked-in client Steam bootstrap back into the smaller
retail-shaped owners that the committed HLIL shows: client callbacks, lobby
callbacks, microtransaction callbacks, and the lobby bootstrap seam that owns
its callback bundle plus the `connect_lobby` registration and lobby cvars.

Classification mix:

- `0` new engine/client aliases
- `0` engine/client alias renames
- `4` engine/client source reconstruction ownership fixes
- `1` engine/client compatibility-only helper extraction
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main source-parity wins are:

- [`cl_main.c`](../../src/code/client/cl_main.c) now reconstructs the retail
  callback-owner split as:
  - `SteamCallbacks_Init`
  - `SteamLobbyCallbacks_Init`
  - `SteamMicroCallbacks_Init`
  - `SteamLobby_Init`
- `SteamClient_Init` now follows the retail bootstrap order more closely by
  calling those smaller owners directly instead of flattening them through the
  older `CL_Steam_InitCallbacks` helper.
- The workshop callback lane is now isolated in
  `CL_Steam_RegisterWorkshopCallbacks`, which keeps the compatibility-owned
  callback fallback separate from the retail callback owners instead of mixing
  them into the reconstructed Steam bootstrap seam.

## Evidence Notes

- The promoted retail alias set already identifies the relevant bootstrap
  owners:
  - `sub_4613A0 -> SteamCallbacks_Init`
  - `sub_461500 -> SteamClient_Init`
  - `sub_4656A0 -> SteamLobbyCallbacks_Init`
  - `sub_465840 -> SteamLobby_Init`
  - `sub_4659E0 -> SteamMicroCallbacks_Init`
- The committed retail `SteamClient_Init` lane shows the bootstrap sequence as:
  1. client callback registration owner
  2. microtransaction callback registration owner
  3. lobby bootstrap owner
  4. `+voice`
  5. `-voice`
  6. conditional `stats_clear`
  7. initial main-menu rich-presence write
- Earlier checked-in source had the right broad behavior, but it flattened the
  retail callback-owner boundaries into a larger `CL_Steam_InitCallbacks`
  helper that mixed client, lobby, micro, and workshop registration concerns.
- The committed retail evidence is strong enough to restore the smaller
  engine-owned owners without needing to speculate about Steam SDK internals.

## Source Reconstruction

- [`cl_main.c`](../../src/code/client/cl_main.c) now restores the retail
  client callback bundle owner in `SteamCallbacks_Init`.
- [`cl_main.c`](../../src/code/client/cl_main.c) now restores the retail lobby
  callback bundle owner in `SteamLobbyCallbacks_Init`.
- [`cl_main.c`](../../src/code/client/cl_main.c) now restores the retail
  microtransaction callback bundle owner in `SteamMicroCallbacks_Init`.
- [`cl_main.c`](../../src/code/client/cl_main.c) now restores the retail lobby
  bootstrap seam in `SteamLobby_Init`, including `lobby_autoconnect`,
  `steam_maxLobbyClients`, and `connect_lobby`.
- [`cl_main.c`](../../src/code/client/cl_main.c) keeps the non-retail workshop
  callback registration in `CL_Steam_RegisterWorkshopCallbacks` so the
  compatibility polling fallback stays explicit and separate.

## Verification

Static/source validation:

- `pytest tests/test_engine_client_command_parity.py tests/test_platform_services.py tests/test_client_workshop_bootstrap_parity.py tests/test_client_sound_voice_parity.py -q --tb=no -k "steam_client_init or steam_callback_owner or workshop_bootstrap or steam_voice_frame or connect_lobby or stats_clear or callback_bundle"`
  passed with `7 passed, 95 deselected`
- `git diff --check -- src/code/client/cl_main.c tests/test_engine_client_command_parity.py tests/test_platform_services.py tests/test_client_workshop_bootstrap_parity.py tests/test_client_sound_voice_parity.py docs/reverse-engineering/quakelive_steam_mapping_round_235.md`
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

- strict-retail client callback-bootstrap ownership lane: `98%` before,
  `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

The next nearby engine-only pass is to keep walking the remaining client
Steam/bootstrap ownership seams where retail helper boundaries are still
flattened, while continuing to avoid speculative changes inside Steam SDK or
browser-host implementation code.
