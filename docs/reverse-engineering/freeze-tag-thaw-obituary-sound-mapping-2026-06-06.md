# Freeze Tag Thaw Obituary And Sound Mapping - 2026-06-06

## Scope

This pass maps the retail assisted-thaw completion event layer that sits between
Freeze helper progress and the thaw visual burst. The qagame targets are
`G_FreezeClientEndFrame` and `G_FreezeSetClientFrozenState`; the related cgame
target is `CG_Obituary`.

## Evidence

- qagame owner binary: `qagamex86.dll`.
- qagame canonical HLIL:
  `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt`.
- qagame companion Ghidra:
  `references/reverse-engineering/ghidra/qagamex86/decompile_top_functions.c`.
- cgame owner binary: `cgamex86.dll`.
- cgame canonical HLIL:
  `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil_split/cgamex86.dll_hlil_part01.txt`.
- cgame symbol strings:
  `references/symbol-maps/cgame.json`.

## Observed Retail Facts

In retail `FUN_1004CD40` / `G_FreezeClientEndFrame`, assisted thaw completion
awards the helper, sends the `"ASSIST"` medal token, and emits an
`EV_OBITUARY` temp entity before the thaw visual path:

- event ordinal `0x3a`, matching `EV_OBITUARY`.
- `eventParm = 0x1e`, matching `MOD_THAW`.
- `otherEntityNum` is the thawed client.
- `otherEntityNum2` is the retained helper client.
- `svFlags = 0x20`, matching `SVF_BROADCAST`.

Immediately after the obituary event, retail emits event ordinal `0x2c`,
matching `EV_GLOBAL_TEAM_SOUND`, and writes `(team != TEAM_BLUE) + 2` to the
sound payload. With the shared team enum, that maps to `GTS_RED_RETURN` for
blue-team clients and `GTS_BLUE_RETURN` otherwise.

Retail then calls `FUN_10046D80` / `GibEntity`. The follow-up mapping in
`docs/reverse-engineering/freeze-tag-thaw-respawn-tail-mapping-2026-06-06.md`
now reconstructs that Freeze-only `EV_THAW_PLAYER` / `PM_NORMAL` /
`ClientSpawn` tail in source.

On cgame, retail `CG_Obituary` contains the matching Freeze strings:
`"was auto-thawed"`, `"You thawed %s."`, and `"was thawed by"`.

## Source Reconstruction

- Added `G_FreezeEmitThawCompletionEvents` for the assisted-thaw path.
- The helper emits `EV_OBITUARY` with `MOD_THAW`, target client, retained thaw
  helper, and `SVF_BROADCAST`.
- The helper then broadcasts the retail team-sound payload through the existing
  `G_BroadcastGlobalTeamSound` bridge, using `GTS_RED_RETURN` for blue-team
  clients and `GTS_BLUE_RETURN` otherwise.
- `G_FreezeSetClientFrozenState` calls the helper only for non-auto thaw, so
  round-end winning-team thaw cleanup remains quiet until the non-helper
  retail paths are reconstructed explicitly.
- `CG_Obituary` now handles `MOD_THAW` with retail thaw text for world,
  local-helper, and remote-helper obituary cases.

## Confidence And Open Questions

Confidence is high for assisted-thaw obituary and team-sound publication: the
qagame Ghidra body and HLIL show the event ordinals, payload fields, broadcast
flag, helper client source, and team-sound payload formula, while the cgame
HLIL and symbol map show the matching thaw obituary strings.

Open follow-up: audit whether the retail thaw respawn tail layers any
Freeze-specific spawn protection or loadout preservation on top of the normal
`ClientSpawn` path.
