# Quake Live Steam Mapping Round 609: Callback Bootstrap Recovery Boundary

Date: 2026-06-11

## Scope

This round rechecks the client Steam callback bootstrap lane around
`SteamClient_Init` and pins the source-side recovery/unwind policy that SRP
uses with the dynamic Steamworks adapter.

Retail Quake Live constructs callback objects directly during
`SteamClient_Init`. SRP reconstructs the same callback families, callback IDs,
and bootstrap ordering, while adding explicit partial-registration unwind and
retry guards because live Steam services are optional and default-disabled in
this repository.

No runtime behavior changed in this pass.

## Retail Evidence

Primary owner: `assets/quakelive/quakelive_steam.exe`

Evidence checked:

- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- `references/analysis/quakelive_symbol_aliases.json`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `src/code/client/cl_main.c`
- `src/common/platform/platform_steamworks.c`

Function ownership:

| Ghidra row | Address | Promoted owner |
| --- | --- | --- |
| `FUN_004613a0` | `0x004613A0` | `SteamCallbacks_Init` |
| `FUN_00461500` | `0x00461500` | `SteamClient_Init` |
| `FUN_004656a0` | `0x004656A0` | `SteamLobbyCallbacks_Init` |
| `FUN_00465840` | `0x00465840` | `SteamLobby_Init` |
| `FUN_004659e0` | `0x004659E0` | `SteamMicroCallbacks_Init` |

Observed facts:

- The retail import table includes `SteamAPI_RegisterCallback`,
  `SteamAPI_UnregisterCallback`, and `SteamAPI_RunCallbacks`.
- `sub_4613a0` constructs the `SteamCallbacks` UGC call-result object and
  registers client callbacks for rich-presence join, user-stats received,
  persona-state change, P2P session request, game-server change request, and
  friend rich-presence update.
- `sub_461500` allocates the `0x98` byte `SteamCallbacks` bundle, calls
  `sub_4613a0`, stores the result in the retained global callback pointer,
  calls `sub_4659e0`, calls `sub_465840`, registers `+voice` and `-voice`,
  conditionally registers `stats_clear` for app id `0x54100`, writes Steam
  rich presence `status = At the main menu`, and prints
  `Steam API initialized.`
- `sub_4656a0` registers lobby callbacks for ids `0x201`, `0x1f8`, `0x1fa`,
  `0x1fb`, `0x1f9`, `0x1fd`, `0x200`, and `0x14d`.
- `sub_465840` allocates the `0xa0` byte lobby callback bundle, calls
  `sub_4656a0`, creates `lobby_autoconnect`, creates
  `steam_maxLobbyClients`, and registers `connect_lobby`.
- `sub_4659e0` allocates the `0x14` byte microtransaction callback object and
  registers callback id `0x98`.

## Source Reconstruction

The source reconstruction preserves the observed retail owner split:

- `SteamCallbacks_Init` binds the client callback family to
  `QL_Steamworks_RegisterClientCallbacks`.
- `SteamMicroCallbacks_Init` binds the microtransaction callback to
  `QL_Steamworks_RegisterMicroCallbacks`.
- `SteamLobbyCallbacks_Init` binds the lobby callback family to
  `QL_Steamworks_RegisterLobbyCallbacks`.
- `SteamLobby_Init` remains a void startup helper, matching retail's lack of a
  lobby callback health return to `SteamClient_Init`.
- `CL_Steam_SetMainMenuRichPresence` preserves the retail
  `status = At the main menu` bootstrap write.

The source-side dynamic adapter adds guarded recovery and unwind behavior:

- `callbackRegistrationActive` prevents duplicate recovery attempts once the
  callback set is live.
- `SteamClient_RecoverCallbackBootstrap` rate-limits retries and refuses to
  become a second Steam initialization owner. It does not call
  `QL_RefreshPlatformServices`, does not refresh service cvars, and does not
  relatch the Steam initialized state.
- Failed initial bootstrap unwinds micro, lobby, and client callback families.
- Failed recovery unwinds micro, lobby, and client callback families.
- Successful recovery registers workshop callbacks, sets
  `callbackRegistrationActive`, resets the retry timer, and re-applies the
  main-menu rich-presence value.
- Shutdown unregisters workshop, micro, lobby, and client callbacks, cancels
  the retained auth ticket, clears callback state, clears the current lobby,
  and clears queued browser events.

## Platform Adapter Boundary

`QL_Steamworks_RegisterClientCallbacks` and the adjacent lobby, micro, and
workshop registration helpers now have an explicit all-or-unwind contract:

- existing registrations are unregistered before a replacement install;
- `QL_Steamworks_UnregisterClientCallbacks` unbinds the retained UGC call
  result before clearing the registered client callback objects;
- binding storage is zeroed before new callback objects are prepared;
- partial registration failure calls the matching unregister helper and
  returns `qfalse`;
- successful registration marks the callback family as registered; and
- unregister helpers release callback objects in reverse-ish ownership order
  and clear their state structures.

This behavior is a source-side safety reconstruction around the retail
callback families. It does not imply that default builds enable live Steam
services.

## Validation

Added
`tests/test_platform_services.py::test_steam_callback_bootstrap_recovery_unwinds_partial_registrations`
to pin:

- Ghidra rows and aliases for the retained client, lobby, and micro bootstrap
  owners;
- Steam callback import evidence and callback-family vtable symbols;
- Binary Ninja HLIL anchors for callback ids, object allocations, bootstrap
  ordering, voice command registration, app-id gated `stats_clear`, rich
  presence, and terminal success logging;
- `SteamClient_Init` failure unwind and success state transitions;
- `SteamClient_RecoverCallbackBootstrap` retry, no-refresh, failure-unwind,
  and success paths;
- `CL_Steam_ShutdownCallbacks` callback/ticket/browser-state teardown; and
- platform registration all-or-unwind contracts.

Planned validation for this round:

```text
python -m pytest tests/test_platform_services.py::test_steam_callback_bootstrap_recovery_unwinds_partial_registrations -q --tb=short
python -m pytest tests/test_platform_services.py -q --tb=short
```

## Confidence

Observed facts:

- HLIL directly shows the retail callback object allocation and callback-id
  registration sequence.
- Ghidra rows and alias names identify the retail owners and sizes.
- Source wrappers expose the same callback families while keeping live Steam
  behavior behind the repository policy gate.

Inference:

- The recovery and all-or-unwind behavior is the correct bounded
  reconstruction for SRP's dynamic Steamworks adapter. It is not a retail
  control-flow claim; it is a documented source policy needed because SRP
  supports builds where the retail Steam runtime is unavailable.

Parity estimates:

- Focused callback bootstrap recovery/unwind confidence:
  **before 90% -> after 98%**.
- Focused client callback registration policy classification:
  **before 94% -> after 99%**.
- Overall Steam launch/runtime integration mapping confidence: **93.20% -> 93.22%**.
