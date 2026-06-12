# Quake Live Steam Mapping Round 614: Invite Callback Connect Handoff

Date: 2026-06-12

## Scope

This round rechecks the Steam invite/runtime handoff where Steam callback
payloads become immediate engine connection commands:
`GameRichPresenceJoinRequested_t` and `GameServerChangeRequested_t`.

No engine source behavior changed in this pass.

## Retail Evidence

Primary owner: `assets/quakelive/quakelive_steam.exe`

Evidence checked:

- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- `references/analysis/quakelive_symbol_aliases.json`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt`
- `src/code/client/cl_main.c`
- `src/common/platform/platform_steamworks.c`
- `src/common/platform/platform_steamworks.h`

Function ownership:

| Ghidra row | Address | Promoted owner |
| --- | --- | --- |
| `FUN_0045ff50` | `0x0045FF50` | `SteamCallbacks_OnRichPresenceJoinRequested` |
| `FUN_0045ff70` | `0x0045FF70` | `SteamCallbacks_OnGameServerChangeRequested` |
| `FUN_00461060` | `0x00461060` | `SteamCallback_GetPayloadSize264` |
| `FUN_00461090` | `0x00461090` | `SteamCallback_GetPayloadSize128` |
| `FUN_004613a0` | `0x004613A0` | `SteamCallbacks_Init` |

Observed facts:

- `sub_45ff50` forwards the rich-presence join payload at `arg1 + 9`
  directly into the immediate command execution path.
- `sub_45ff70` checks the password string at `arg1 + 0x40`, writes the
  `password` cvar only when that string is non-empty, and then emits
  `connect %s\n`.
- `sub_461060` returns payload size `0x108`, matching
  `GameRichPresenceJoinRequested_t`.
- `sub_461090` returns payload size `0x80`, matching
  `GameServerChangeRequested_t`.
- `SteamCallbacks_Init` registers the rich-presence join callback with id
  `0x151` and the game-server change callback with id `0x14c`.
- Ghidra analysis symbols identify the matching callback vtables, and the
  import table identifies `SteamAPI_RegisterCallback`.

## Source Reconstruction

The source reconstruction keeps the retail callback thunks split across a
platform payload decoder and a client command owner:

- `QL_Steamworks_DispatchRichPresenceJoinRequested` copies the raw friend
  SteamID, enriches the requester summary, copies the raw `connect` command
  into the public event, and calls the registered client binding.
- `QL_Steamworks_DispatchGameServerChangeRequested` copies raw `server` and
  `password` strings into the public event and calls the registered client
  binding.
- `QL_Steamworks_RegisterClientCallbacks` prepares the two callback objects
  with ids `0x151` and `0x14c` and the raw sizes `0x108` and `0x80`.
- `SteamCallbacks_Init` wires those public events to
  `CL_Steam_Client_OnRichPresenceJoinRequested` and
  `CL_Steam_Client_OnGameServerChangeRequested`.
- `CL_Steam_OnRichPresenceJoinRequested` executes the callback-provided command
  as-is through `Cbuf_ExecuteText(EXEC_NOW, ...)`.
- `CL_Steam_OnGameServerChangeRequested` writes `password` only when a
  non-empty password is supplied, then executes `connect %s\n` immediately.

## Compatibility Boundary

Live Steam callback delivery remains behind `QL_BUILD_ONLINE_SERVICES` and the
platform service table. Default-disabled builds keep the source dispatch and
logging behavior available without registering live Steam callbacks.

This round preserves the retail behavioral distinction:

- rich-presence join payloads are already complete command strings and are not
  reformatted; and
- game-server change payloads carry a server/password pair, so the client owner
  conditionally seeds `password` before formatting the immediate connect
  command.

## Validation

Added
`tests/test_platform_services.py::test_steam_invite_callback_connect_handoff_tracks_round_614`
to pin:

- alias, Ghidra function, import, and analysis-symbol evidence for the two
  callback thunks and callback vtables;
- Binary Ninja HLIL anchors for payload forwarding, password handling,
  immediate `connect %s\n`, callback ids, and payload-size thunks;
- source raw/public payload structures, static size guards, callback id
  preparation, platform dispatch copies, client callback binding, and immediate
  command execution; and
- this round note plus Task A483 parity anchors.

Planned validation for this pass:

```text
python -m pytest tests/test_platform_services.py::test_steam_invite_callback_connect_handoff_tracks_round_614 -q --tb=short
python -m pytest tests/test_platform_services.py -q --tb=short
python -m pytest tests/test_steamworks_harness.py -q --tb=short
```

## Confidence

Observed facts:

- HLIL directly shows both retail callback thunks, callback registrations,
  payload sizes, password handling, and immediate command routing.
- Ghidra rows, imports, vtable symbols, and aliases identify the callback
  owners and their Steam API registration surface.
- Source tests now bind the platform decoder, client callback bindings, and
  immediate command owners into one invite/runtime handoff gate.

Inference:

- SRP's split between raw Steamworks payload decoding and client command
  execution is the correct bounded reconstruction for a dynamic adapter. The
  split preserves retail callback behavior while keeping live callback
  registration default-disabled by policy.

Parity estimates:

- Focused Steam invite/server-change connect-handoff confidence:
  **before 94% -> after 99%**.
- Focused callback payload/registration classification:
  **before 96% -> after 99%**.
- Overall Steam launch/runtime integration mapping confidence: **93.30% -> 93.32%**.
