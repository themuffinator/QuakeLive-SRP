# Quake Live Steam Mapping Round 632: GameServer Bootstrap Setter Initialized Guards

Date: 2026-06-12

## Scope

This round maps the retail Steam GameServer bootstrap setter lane and
reconstructs explicit initialized-state guards in the SRP public bootstrap
wrappers. The retail owner is `SteamServer_Init`, promoted from `sub_466ed0`.
The source boundaries are `QL_Steamworks_ServerSetDedicated`,
`QL_Steamworks_ServerLogOn`, `QL_Steamworks_ServerSetProduct`, and
`QL_Steamworks_ServerSetGameDir`.

Steam launch/runtime online behavior remains behind `QL_BUILD_ONLINE_SERVICES`.
This round tightens wrapper fidelity; it does not enable live Steam services.

## Retail Evidence

- `references/analysis/quakelive_symbol_aliases.json` promotes
  `FUN_00466ed0`, `sub_466ED0`, and `sub_466ed0` to `SteamServer_Init`.
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  records `FUN_00466ed0,00466ed0,495,0,unknown`.
- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
  confirms the bootstrap dependency through
  `STEAM_API.DLL!SteamGameServer_Init @ 00159314` and the follow-up interface
  dependency through `STEAM_API.DLL!SteamGameServer @ 0015918a`.
- Binary Ninja HLIL shows `00466ed0    int32_t* sub_466ed0()`, the
  pre-existing initialized guard at `00466ee7  if (data_e30358 == 0)`,
  `SteamGameServer_Init`, and then `00466fc7          data_e30358 = eax_10`.
- After `data_e30358` is set and checked for failure, retail dispatches the
  GameServer bootstrap setters: dedicated state through vtable slot `0x10`,
  account logon/anonymous logon through `0x14` and `0x18`, heartbeats through
  `0x9c`, product through `0x04`, and game-dir through `0x0c`.

Observed fact: retail reaches the bootstrap setter slots only after
`SteamGameServer_Init` has populated `data_e30358` with a successful non-zero
state.

Inferred mapping: SRP's `state.gameServerInitialised` mirrors retail
`data_e30358`, while `Com_InitSteamGameServer` is the source bootstrap owner
corresponding to retail `sub_466ed0`.

## Source Reconstruction

`src/common/platform/platform_steamworks.c` now makes the retail initialized
boundary explicit in the public bootstrap wrappers:

1. `QL_Steamworks_ServerSetDedicated` rejects calls while
   `state.gameServerInitialised` is false before resolving `SteamGameServer`
   and dispatching slot `0x10`.
2. `QL_Steamworks_ServerLogOn` rejects calls while
   `state.gameServerInitialised` is false before resolving `SteamGameServer`,
   then keeps the retained account-token versus anonymous-logon split at slots
   `0x14` and `0x18`.
3. `QL_Steamworks_ServerSetProduct` validates the product string, rejects
   uninitialized GameServer state, and then dispatches slot `0x04`.
4. `QL_Steamworks_ServerSetGameDir` validates the game-dir string, rejects
   uninitialized GameServer state, and then dispatches slot `0x0c`.

The shared `QL_Steamworks_GetGameServer` helper still retains the broader
`state.initialised`, `state.gameServerInitialised`, and `SteamGameServer`
checks. The new wrapper-level guards make the public bootstrap boundary match
the retail post-init slot-dispatch lane directly.

## Bootstrap Wiring

`src/code/qcommon/common.c` remains the bootstrap owner:

- `Com_InitSteamGameServer` resolves net IP/port, VAC, dedicated state, and the
  version string before calling `QL_Steamworks_ServerInitWithVersion`.
- After successful init, it calls `QL_Steamworks_ServerSetDedicated`, reads
  `sv_setSteamAccount`, calls `QL_Steamworks_ServerLogOn`, disables
  heartbeats, publishes product/game-dir, and prints the retained
  `Steam Gameserver initialized.` diagnostic.
- The online-service policy remains unchanged; default-disabled builds keep the
  compatibility fallback instead of attempting live Steam GameServer startup.

## Validation

Added `test_steam_gameserver_bootstrap_setter_wrapper_guards_track_round_632`
to pin:

- promoted aliases and Ghidra rows for `sub_466ed0`;
- Steam GameServer and GameServer-init imports;
- Binary Ninja ordering from `data_e30358 = eax_10` through dedicated, logon,
  heartbeat, product, and game-dir slot dispatch;
- wrapper initialized-state guards before `QL_Steamworks_GetGameServer`;
- product/game-dir input validation before initialized-state guards; and
- source bootstrap call ordering in `Com_InitSteamGameServer`.

## Parity Estimate

Focused GameServer bootstrap setter wrapper guard confidence:
**80% -> 99%**.

Focused Steam GameServer bootstrap wiring confidence:
**93% -> 99%**.

overall Steam launch/runtime integration mapping confidence **93.66% -> 93.68%**.
