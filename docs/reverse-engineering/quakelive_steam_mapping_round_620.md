# Quake Live Steam Mapping Round 620: Server Callback Registration And Dispatch Lifecycle

Date: 2026-06-12

## Scope

This round pins the dedicated Steam GameServer callback path used by retail
`quakelive_steam.exe` and the SRP server-side reconstruction around it:

- `SteamServerCallbacks_Init`
- `SteamServerCallbacks_OnServersConnected`
- `SteamServerCallbacks_OnConnectFailure`
- `SteamServerCallbacks_OnServersDisconnected`
- `SteamServerCallbacks_OnValidateAuthTicketResponse`
- `SteamServerCallbacks_OnP2PSessionRequest`
- `SteamGameServer_RunCallbacks`
- SRP's server-owned `GSStatsReceived_t` and `GSStatsStored_t` callback lanes

The focus is registration, dispatch ownership, callback-pump separation, and
source-side server handling. No live Steam behavior was enabled, and no game
launch was required.

## Retail Evidence

Observed Binary Ninja HLIL and Ghidra evidence:

- Alias map:
  - `FUN_00465b70` -> `SteamServerCallbacks_OnP2PSessionRequest`
  - `FUN_00465c10` -> `SteamServerCallbacks_OnConnectFailure`
  - `FUN_00465c30` -> `SteamServerCallbacks_OnServersDisconnected`
  - `FUN_00465c50` -> `SteamServerCallbacks_OnValidateAuthTicketResponse`
  - `FUN_00466800` -> `SteamServerCallbacks_OnServersConnected`
  - `FUN_00466db0` -> `SteamServerCallbacks_Init`
- Ghidra function rows keep the larger callback bodies at `00465b70`,
  `00465c50`, and `00466db0`.
- Ghidra imports confirm `SteamAPI_RegisterCallback`, `SteamGameServer`,
  `SteamGameServerNetworking`, `SteamGameServerStats`, `SteamGameServerUtils`,
  and `SteamGameServer_RunCallbacks` are part of the retained retail Steam
  surface.
- Ghidra analysis symbols expose the callback vtables and RTTI for:
  - `SteamServersConnected_t`
  - `SteamServerConnectFailure_t`
  - `SteamServersDisconnected_t`
  - `ValidateAuthTicketResponse_t`
  - `P2PSessionRequest_t`
  - `idSteamStats` server stats callbacks
- HLIL `sub_466db0` constructs and registers the five retail
  `SteamServerCallbacks` callback objects with ids `0x65`, `0x66`, `0x67`,
  `0x8f`, and `0x4b2`.
- HLIL `sub_466850` pumps `SteamGameServer_RunCallbacks` from the server frame
  path, keeping GameServer callbacks separate from the client callback pump.
- HLIL `sub_466800` publishes identity, refreshes published server state, and
  syncs serverinfo key/value state after connecting to Steam servers.
- HLIL `sub_465c10` and `sub_465c30` clear the connected flag and log connect
  failure/disconnect messages without using the callback result payload.
- HLIL `sub_465c50` owns the ValidateAuthTicketResponse path, including the
  retained `net_fakevacban` override.
- HLIL `sub_465b70` accepts server-side P2P sessions only for active matching
  clients through `SteamGameServerNetworking`.

## Source Reconstruction

SRP now has focused coverage tying this evidence to these source surfaces:

- alias support:
  - promoted missing `FUN_00465c10`, `FUN_00465c30`, and `FUN_00466800`
    aliases for the server callback thunks
- raw ABI layouts:
  - `ql_steam_servers_connected_raw_t`, size `0x01`
  - `ql_steam_server_connect_failure_raw_t`, size `0x04`
  - `ql_steam_servers_disconnected_raw_t`, size `0x04`
  - `ql_steam_validate_auth_ticket_response_raw_t`, size `0x14`
  - `ql_steam_gs_stats_received_raw_t`, size `0x0c`
  - `ql_steam_gs_stats_stored_raw_t`, size `0x0c`
- platform dispatch shims:
  - `QL_Steamworks_DispatchServersConnected`
  - `QL_Steamworks_DispatchServerConnectFailure`
  - `QL_Steamworks_DispatchServersDisconnected`
  - `QL_Steamworks_DispatchValidateAuthTicketResponse`
  - `QL_Steamworks_DispatchServerP2PSessionRequest`
  - `QL_Steamworks_DispatchGSStatsReceived`
  - `QL_Steamworks_DispatchGSStatsStored`
- registration lifecycle:
  - `QL_Steamworks_RegisterServerCallbacks`
  - `QL_Steamworks_UnregisterServerCallbacks`
  - `QL_Steamworks_RunServerCallbacks`
  - disabled inline stubs in default/offline builds
- server callback owners:
  - `SV_SteamServerConnectedCallback`
  - `SV_SteamServerConnectFailureCallback`
  - `SV_SteamServerDisconnectedCallback`
  - `SV_SteamServerValidateAuthTicketResponseCallback`
  - `SV_SteamServerP2PSessionRequestCallback`
  - `SV_SteamServerGSStatsReceivedCallback`
  - `SV_SteamServerGSStatsStoredCallback`
  - `SV_SteamServerInitCallbacks`

SRP intentionally registers seven server callback surfaces in the platform
server bundle. Five match the retail `SteamServerCallbacks` object exactly,
while `GSStatsReceived_t` and `GSStatsStored_t` are the server-owned
`idSteamStats` lanes that still need the GameServer callback pump and the same
default-disabled online-service policy boundary.

## Compatibility Boundary

This remains an explicit online-service boundary. Default/offline builds reject
server callback registration through the disabled `platform_steamworks.h` stub
and never pump live GameServer callbacks. Online-service builds route all seven
server callback objects through `SteamGameServer_RunCallbacks`; client, lobby,
microtransaction, Workshop, and avatar callback bundles stay on the client
callback pump.

The retained runtime contract is:

1. connected callbacks publish server identity, refresh published state,
   requery stats sessions, and sync serverinfo key/value pairs;
2. connect-failure and disconnect callbacks clear the connected flag and log
   the retail messages without consuming result payloads;
3. ValidateAuthTicketResponse callbacks finalize the pending server-owned auth
   session and apply the retained fake-VAC test override;
4. server P2P callbacks accept sessions only for active matching clients;
5. GSStats callbacks update or retry the retained per-client server stats
   session; and
6. unregister tears down the server callback objects in reverse order.

## Validation

New focused parity gate:

```powershell
python -m pytest tests/test_platform_services.py::test_steam_server_callback_registration_dispatch_lifecycle_tracks_round_620 -q --tb=short
```

The gate checks promoted aliases, Ghidra function/import rows, analysis
symbols, HLIL callback bodies, callback ids, vtable anchors, raw ABI layouts,
platform dispatch shims, register/unregister order, server callback owners,
disabled stubs, harness GameServer callback pump coverage, this round note, and
the Task A489 planning anchor.

## Confidence

- Focused Steam server callback registration confidence:
  **before 93% -> after 99%**.
- Focused GameServer callback dispatch/pump split confidence:
  **before 94% -> after 99%**.
- Overall Steam launch/runtime integration mapping confidence:
  **93.42% -> 93.44%**.
