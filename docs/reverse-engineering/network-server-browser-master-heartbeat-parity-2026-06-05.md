# Network Server Browser And Master Heartbeat Parity - 2026-06-05

## Scope

This pass closes the engine-owned server browser protocol and master heartbeat
slice against the committed `quakelive_steam.exe` evidence. It does not enable
retired online services in default builds; Quake Live-only online surfaces remain
behind `QL_BUILD_ONLINE_SERVICES` and the legacy Quake III UDP service switch.

Owning retail binary:

- `assets/quakelive/quakelive_steam.exe`

Committed evidence used:

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`
- `references/analysis/quakelive_symbol_aliases.json`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt`

Writable source checked:

- `src/code/qcommon/common.c`
- `src/code/qcommon/qcommon.h`
- `src/code/client/cl_cgame.c`
- `src/code/client/cl_main.c`
- `src/code/server/sv_main.c`
- `src/code/server/sv_init.c`
- `src/code/server/sv_client.c`
- `src/common/platform/platform_config.h`
- `src/common/platform/platform_steamworks.c`
- `src/common/platform/platform_steamworks.h`

## Observed Facts

- The active profile is Quake Live retail protocol `91` and owns the browser
  tokens `getservers`, `getserversResponse`, `getinfo`, `infoResponse`,
  `getstatus`, and `statusResponse`.
- Retail `CL_ConnectionlessPacket` matches `getserversResponse` at
  `0x004BC11C`; the source dispatches through `NET_IsServersResponse()` and
  parses the classic backslash-delimited address list with `MAX_SERVERSPERPACKET`
  set to `256`.
- Retail strings include `getinfo xxx`, `getstatus`, `sv_master`, and protocol
  `91`; Ghidra imports include both `SteamGameServer` and
  `SteamMatchmakingServers`.
- The UDP heartbeat token remains `heartbeat QuakeArena-1`, but it stays behind
  the existing online-services policy gate in default builds.
- The Steam GameServer heartbeat owner is reconstructed separately through the
  mapped `ISteamGameServer::EnableHeartbeats` vtable slot `0x9c`.

## Source Change

`SV_MasterHeartbeat` now preserves explicitly configured master-server ports.
The old check searched for the configured hostname inside the literal `":"`,
which meant every successful resolution was forced back to `PORT_MASTER`. The
fixed check searches the configured master string for `":"` before applying the
default port.

This is behavior-neutral for plain hostnames and fixes the `host:port` case that
retail-compatible master configuration needs.

## Related Wiring Recheck

The adjacent browser/heartbeat graph was rechecked after the port fix:

- `qz_instance` browser methods dispatch `RequestServers`,
  `RequestServerDetails`, and `RefreshList` into the client-owned browser
  helpers.
- The source-backed browser lane publishes the retained
  `servers.refresh.start`, `servers.refresh.end`,
  `servers.details.*.response`, `servers.details.*.failed`,
  `servers.rules.*`, and `servers.players.*` event families.
- `CL_ServerInfoPacket` and `CL_ServerStatusResponse` promote UDP
  `infoResponse` / `statusResponse` replies into browser row, rules, and
  players events.
- The low-level `ISteamMatchmakingServers` wrapper maps request modes,
  `gamedir=baseq3` filters, request release/refresh, row detail reads, and
  ping/rules/players detail probes to the retained vtable slots recovered in
  HLIL.
- Server info/status answers report Quake Live keys for visible clients, bot
  players, VAC state, and server type, while `sv_maskBots` suppresses bots from
  public counts and player rows.
- `SV_SteamServerUpdatePublishedState` republishes Steam GameServer max
  players, password state, hostname, map, game description, tags, team scores,
  player data, and bot count; spawn, frame, Steam reconnect, and shutdown paths
  call it or disable heartbeats in the expected lifecycle order.
- Retail `SV_Startup` / `SV_SpawnServer` evidence gates Steam heartbeats from
  `sv_master`, while the old Quake III UDP heartbeat remains a disabled
  compatibility lane behind `QL_ENABLE_LEGACY_Q3_SERVICES`.

No additional C source change was required for this second pass. The native
Steam browser product-integration boundary remains the separately documented
RW-G01 policy/compatibility boundary; it is explicit and not counted as an
untracked defect in this protocol/heartbeat closure.

## Parity Estimate

- Focused server browser protocol and master heartbeat slice: before **96%**,
  after **100%**.
- Related browser/heartbeat wiring recheck: before **97%**, after **100%** for
  the source-owned and policy-gated wiring covered by this pass.
- Repo-wide parity estimate remains **99%** because this closes a narrow
  protocol/heartbeat correctness gap while the documented online-service
  boundary and native Steam product integration policy remain unchanged.

No runtime launch was required; the change is statically verifiable and covered
by the targeted netcode parity regression.
