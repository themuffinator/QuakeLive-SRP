# Quake Live Steam Host Mapping Round 79

## Scope

This round closes the next bounded `quakelive_steam.exe` host lifetime seam
that was still only partially reconstructed after the earlier Steam
game-server bootstrap and shutdown passes:

- the retail `net_restart` command owner at `sub_4EF4F0`
- the exact restart order between Steam game-server shutdown, Win32 network
  reconfiguration, and the common Steam game-server bootstrap

The evidence stayed inside the committed corpus plus the writable source tree:

- `references/hlil/quakelive/quakelive_steam.exe/`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `src/code/win32/win_net.c`
- `src/code/qcommon/common.c`
- `src/code/qcommon/qcommon.h`
- `tests/test_platform_services.py`

## `sub_4EF4F0`: retail `net_restart` owner

The committed HLIL shows `net_restart` resolving directly to `sub_4EF4F0`,
with a short three-step owner:

1. call `sub_465D30()`
2. call `sub_4EF250( data_12D12A0 )`
3. tail-call `sub_466ED0()`

Earlier rounds had already reconstructed the adjacent meanings of those
helpers:

- `sub_465D30()` is the shared Steam game-server shutdown owner
- `sub_4EF250(...)` is the retained Win32 `NET_Config( networkingEnabled )`
  owner
- `sub_466ED0()` is the common Steam game-server bootstrap reconstructed in
  Round 78

This round wires that ownership into the retained source instead of leaving
the restart path as a pure Quake-side network toggle.

## Retained source changes

The writable source now mirrors the retail restart order in one bounded place:

- `src/code/win32/win_net.c`
  - `NET_Restart()` now calls:
    - `QL_Steamworks_ServerShutdown()`
    - `NET_Config( networkingEnabled )`
    - `Com_InitSteamGameServer()`

To support that reuse cleanly, the common bootstrap helper is now public:

- `src/code/qcommon/common.c`
  - `Com_InitSteamGameServer()` is no longer file-local
- `src/code/qcommon/qcommon.h`
  - declares `Com_InitSteamGameServer()`

That keeps the retained ownership aligned with the HLIL without inventing a
second bootstrap helper or moving the actual Steam game-server init work away
from the common owner already closed in Round 78.

## Verification

Updated coverage landed in:

- `tests/test_platform_services.py`

Command run:

```text
python -m pytest tests/test_steamworks_harness.py tests/test_platform_services.py tests/test_ui_menu_files.py -q
```

Result:

- `72 passed`

## Outcome

This round did not add new address aliases. It consumed already-mapped retail
ownership in one concrete way:

- `net_restart` now reconstructs the retail Steam game-server lifetime order
  instead of only re-running the Quake-side network configuration path

Estimated parity for this round: `79% -> 80%`.
