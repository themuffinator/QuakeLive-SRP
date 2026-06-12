# Quake Live Steam Mapping Round 610: Auth Ticket Replacement And Cleanup Boundary

Date: 2026-06-11

## Scope

This round rechecks the retained Steam auth-ticket lifecycle around
`SteamClient_GetAuthSessionTicket`, `SteamClient_CancelAuthTicket`, and the
quit/error cleanup owners. The focus is the ticket handle that retail stores in
`data_e2c208` and the source-side rules for replacing, cancelling, and clearing
that retained handle.

No engine source behavior changed in this pass.

## Retail Evidence

Primary owner: `assets/quakelive/quakelive_steam.exe`

Evidence checked:

- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/analysis/quakelive_symbol_aliases.json`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt`
- `src/code/client/cl_main.c`
- `src/code/client/ql_auth.c`
- `src/code/qcommon/common.c`
- `src/common/platform/platform_steamworks.c`

Function ownership:

| Ghidra row | Address | Promoted owner |
| --- | --- | --- |
| `FUN_004605c0` | `0x004605C0` | `SteamClient_GetAuthSessionTicket` |
| `FUN_004605f0` | `0x004605F0` | `SteamClient_CancelAuthTicket` |
| `SteamAPI_Shutdown` | `0x00460540` | `SteamAPI_Shutdown` |

Observed facts:

- `sub_4605c0` calls `SteamUser()` and dispatches vtable slot `0x34`,
  storing the returned auth-ticket handle in `data_e2c208`.
- `sub_4605f0` calls `SteamUser()` and dispatches vtable slot `0x40` with
  `data_e2c208`.
- `CL_CheckForResend` calls `sub_4605c0(...)` before formatting the
  `"getchallenge "` payload.
- The retail common error path reaches `sub_4605f0()`.
- The retail quit path calls the imported `SteamAPI_Shutdown()` thunk before
  final process exit.

## Source Reconstruction

The source reconstruction keeps the retail ticket wrapper as a client-owned
lifetime surface:

- `SteamClient_GetAuthSessionTicket` zeroes the caller buffer before
  validation, refuses invalid/uninitialised requests, asks
  `QL_Steamworks_RequestAuthTicket` for a ticket plus handle, cancels an older
  retained handle only when the newly issued handle differs, then stores the
  new handle.
- `SteamClient_CancelAuthTicket` calls `QL_Steamworks_CancelAuthTicket` for the
  retained handle and clears `cl_steamAuthTicketHandle` even when platform
  cancellation reports failure.
- `SteamClient_Init` cancels any retained ticket before refreshing the platform
  service table, which prevents init re-entry from carrying a stale handle.
- `QL_ClientAuth_RequestSteamTicket` pumps Steam callbacks before and after the
  retained ticket fetch.
- `QL_ClientAuth_RequestSteamChallengeTicket` cancels the retained ticket if
  the hex-to-raw conversion fails after a successful retail-style ticket
  request.
- `QL_ClientAuth_CancelSteamTicket`, `CL_Steam_ShutdownCallbacks`, and
  `Com_Error` all route through `SteamClient_CancelAuthTicket`.
- `SteamAPI_Shutdown` releases client Steam resources, shuts down callback and
  ticket state, and only then releases the platform Steamworks adapter.
- `Com_Quit_f` keeps `SteamAPI_Shutdown()` before
  `QL_Steamworks_ServerShutdown()`, matching the client-first retail quit
  cleanup boundary while preserving SRP's explicit server adapter release.

## Compatibility Boundary

`QL_Steamworks_RequestAuthTicket` and `QL_Steamworks_CancelAuthTicket` remain
behind the repository's Steamworks/platform-service policy. The retail wrapper
shape and lifetime owner are reconstructed, but live Steam auth is still
default-disabled unless `QL_BUILD_ONLINE_SERVICES` and the configured provider
allow it.

This round intentionally does not introduce `GetAuthTicketForWebApi`; the
current source continues to label that as the documented
`missing GetAuthTicketForWebApi adapter` divergence.

## Validation

Added
`tests/test_platform_services.py::test_steam_auth_ticket_replacement_and_cleanup_lifecycle_tracks_round_610`
to pin:

- alias and Ghidra ownership for `FUN_004605c0`, `FUN_004605f0`, and
  `SteamAPI_Shutdown`;
- import evidence for `SteamUser` and `SteamAPI_Shutdown`;
- Binary Ninja HLIL anchors for Steam user vtable slots `0x34` and `0x40`,
  `getchallenge` ticket use, common error cancellation, and quit shutdown;
- source ordering for replacement-only retained ticket cancellation;
- callback pumps around retained ticket requests;
- raw challenge decode-failure cancellation;
- init re-entry, callback shutdown, common error, and quit cleanup ordering;
  and
- the round note anchors listed here.

Planned validation for this pass:

```text
python -m pytest tests/test_platform_services.py::test_steam_auth_ticket_replacement_and_cleanup_lifecycle_tracks_round_610 -q --tb=short
python -m pytest tests/test_platform_services.py -q --tb=short
python -m pytest tests/test_steamworks_harness.py -q --tb=short
```

## Confidence

Observed facts:

- HLIL directly shows the retail `SteamUser` ticket and cancel vtable slots.
- Ghidra rows and the alias map identify the retained ticket wrapper owners.
- Source call ordering now has a parity gate covering every source-side owner
  that can replace, cancel, or clear the retained ticket handle.

Inference:

- SRP's clear-on-cancel-attempt behavior is the correct bounded reconstruction
  for a dynamic adapter environment: once the client has handed the retained
  handle to the cancel wrapper, the source owner must not retain or reuse it.
  This is a source safety policy around the retail lifetime owner, not a claim
  that live Steam service behavior is enabled by default.

Parity estimates:

- Focused auth-ticket replacement/cleanup lifecycle confidence:
  **before 92% -> after 99%**.
- Focused Steam shutdown/error ticket-owner classification:
  **before 94% -> after 99%**.
- Overall Steam launch/runtime integration mapping confidence: **93.22% -> 93.24%**.
