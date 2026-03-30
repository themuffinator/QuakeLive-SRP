# Quake Live Steam Host Mapping Round 85

## Scope

This round closes the next bounded `quakelive_steam.exe` host edge-contract
slice at the native import/syscall bridge:

- explicit `qboolean` normalization for native UI import arguments/results
- explicit `qboolean` normalization for native cgame import arguments/results
- explicit `qboolean` normalization for native qagame import arguments/results

The evidence stayed inside the committed corpus plus the writable source tree:

- `docs/architecture/native-pipeline.md`
- `src/code/client/cl_ui.c`
- `src/code/client/cl_cgame.c`
- `src/code/server/sv_game.c`
- `src/code/client/keys.h`
- `src/code/client/snd_public.h`
- `tests/test_platform_services.py`

## Native import/syscall `qboolean` boundary

The previous rounds tightened the host-side boolean contract on direct
`VM_Call(...)` owners and on the central native export switch in `vm.c`.

Observed facts from the current source-visible native import bridge:

- `S_RegisterSound( const char *sample, qboolean compressed )`
- `S_ClearLoopingSounds( qboolean killall )`
- `Key_IsDown( int keynum )` returns `qboolean`
- `Key_GetOverstrikeMode( void )` returns `qboolean`
- `Key_SetOverstrikeMode( qboolean state )`
- `LAN_MarkServerVisible( int source, int n, qboolean visible )`
- `LAN_ServerIsVisible(...)` and `LAN_UpdateVisiblePings(...)` return
  `qboolean`
- `CL_GetSnapshot(...)`, `CL_GetServerCommand(...)`, and `CL_GetUserCmd(...)`
  return `qboolean`
- `SV_EntityContact(...)`, `SV_inPVS(...)`, `SV_inPVSIgnorePortals(...)`,
  `SV_GetClientSteamId(...)`, and `SV_VerifyClientSteamAuth(...)` return
  `qboolean`
- `SV_AdjustAreaPortalState( ..., qboolean open )`

Before this round, those native import/syscall bridge cases still forwarded raw
int-sized truth values directly into engine-side handlers or returned the raw
result without an explicit host-side `qtrue` / `qfalse` boundary.

## Retained source changes

The writable source now tightens that contract in three bridge owners:

- `src/code/client/cl_ui.c`
  - normalizes the documented UI-side sound, key, LAN, and CD-key
    `qboolean` import args/results
- `src/code/client/cl_cgame.c`
  - normalizes the documented cgame-side sound, snapshot, command, key, and
    renderer query `qboolean` import args/results
- `src/code/server/sv_game.c`
  - normalizes the documented qagame-side visibility, auth, SteamID, and area
    portal `qboolean` import args/results

That closes the same host-side contract band on the native import/syscall side
instead of leaving those bridges to rely on implicit integer truthiness.

## Verification

Updated coverage landed in:

- `tests/test_platform_services.py`

Command run:

```text
python -m pytest tests/test_steamworks_harness.py tests/test_platform_services.py tests/test_ui_menu_files.py -q
```

Result:

- `79 passed`

## Outcome

This round did not add new address aliases. It consumed already-mapped host
ownership in one concrete way:

- the native UI/cgame/qagame import bridges now enforce explicit `qboolean`
  normalization for the documented sound, key, LAN, snapshot, visibility, and
  auth contracts instead of forwarding raw int-sized truth values through the
  host-side syscall shims

Estimated parity for this round: `85% -> 86%`.
