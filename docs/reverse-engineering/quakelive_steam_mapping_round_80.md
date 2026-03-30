# Quake Live Steam Host Mapping Round 80

## Scope

This round closes the next bounded `quakelive_steam.exe` host edge-contract
slice that still diverged from the documented retail/native ownership:

- the native `GAME_CLIENT_CONNECT` denial-string return contract used by the
  direct-connect, map-restart, and spawn-time reconnect owners
- the strict-boolean `UI_HASUNIQUECDKEY` return contract in the client host

The evidence stayed inside the committed corpus plus the writable source tree:

- `references/hlil/quakelive/quakelive_steam.exe/`
- `docs/architecture/native-pipeline.md`
- `src/code/server/sv_game.c`
- `src/code/server/sv_client.c`
- `src/code/server/sv_ccmds.c`
- `src/code/server/sv_init.c`
- `src/code/client/cl_ui.c`

## `GAME_CLIENT_CONNECT`: engine-owned denial text

The current native-pipeline notes already flagged `GAME_CLIENT_CONNECT` as a
remaining host-compatibility seam because the engine still depended on
`VM_ExplicitArgPtr` at each callsite to reinterpret the denial pointer
returned by the game module.

The committed HLIL also shows the retail host treating the reconnect result as
an immediate owner decision inside the map-restart path: the call through
`(data_13E180C + 0x20)` returns a denial value, zero means success, and the
owner drops the client plus logs
`"SV_MapRestart_f(%d): dropped client %i - denied!\n"` when that value is
non-zero.

This round reconstructs the missing host-owned buffer boundary instead of
leaving each caller to reinterpret the module return directly.

## Retained source changes

The writable source now routes all three `GAME_CLIENT_CONNECT` owners through a
single shared helper:

- `src/code/server/sv_game.c`
  - `SV_GameClientConnect()`
  - copies the denial text into the engine-owned
    `sv_gameClientConnectDenied[MAX_STRING_CHARS]` buffer
- `src/code/server/server.h`
  - declares `SV_GameClientConnect()`
- `src/code/server/sv_client.c`
  - `SV_DirectConnect()` now uses the shared helper
- `src/code/server/sv_ccmds.c`
  - `SV_MapRestart_f()` now uses the shared helper
- `src/code/server/sv_init.c`
  - `SV_SpawnServer()` reconnect handling now uses the shared helper

That removes the repeated inline `VM_ExplicitArgPtr( gvm, VM_Call(...) )`
pattern from the reconnect owners and gives native denial strings an
engine-owned lifetime boundary before they are logged, printed, or passed into
drop paths.

## `UI_HASUNIQUECDKEY`: strict boolean normalization

The documented native ABI notes also called out the `UI_usesUniqueCDKey()`
wrapper as an unnecessary strict comparison against `qtrue`.

The writable source now normalizes the native return value as a strict
non-zero-to-`qtrue` / zero-to-`qfalse` contract in `src/code/client/cl_ui.c`.
That keeps the wrapper aligned with the intended `qboolean` API shape instead
of requiring the UI module to return exactly `1`.

## Verification

Updated coverage landed in:

- `tests/test_platform_services.py`

Command run:

```text
python -m pytest tests/test_steamworks_harness.py tests/test_platform_services.py tests/test_ui_menu_files.py -q
```

Result:

- `74 passed`

## Outcome

This round did not add new address aliases. It consumed already-mapped host
ownership in two concrete ways:

- native `GAME_CLIENT_CONNECT` denial strings now cross into engine-owned
  storage before the three host reconnect owners consume them
- `UI_usesUniqueCDKey()` now reflects the documented strict-boolean return
  contract instead of comparing only against exact `qtrue`

Estimated parity for this round: `80% -> 81%`.
