# Quake Live Steam Host Mapping Round 23

## Scope

This round returns to the raw native `cgamex86.dll` import band immediately after the Round 22 sound seam. The goal was to close the remaining render-registration wrappers between the already-mapped `startBackgroundTrack` / `registerModel` / `registerShaderNoMip` anchors.

The primary local evidence for this round is:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `src/code/client/cl_cgame.c`
- `src/code/client/ql_cgame_imports.inc`
- `src/code/cgame/cg_syscalls.c`

## Raw Post-Sound Import Band

Observed local facts:

1. The owning host slots at `data_565958` are:
   - `data_565A14 = sub_4AFED0` (`+0xBC`)
   - `data_565A18 = 0x4B02F0` (`+0xC0`)
   - `data_565A1C = sub_4AFEE0` (`+0xC4`)
   - `data_565A20 = sub_4BEEC0` (`+0xC8`)
   - `data_565A24 = sub_4BEED0` (`+0xCC`)
   - `data_565A28 = sub_4AFEF0` (`+0xD0`)
   - `data_565A2C = sub_4AFF00` (`+0xD4`)
2. The reconstructed native cgame import order in `ql_cgame_imports.inc` and `cl_cgame.c` matches the same sequence:
   - `CG_S_STARTBACKGROUNDTRACK`
   - `CG_S_STOPBACKGROUNDTRACK`
   - `CG_R_LOADWORLDMAP`
   - `CG_R_REGISTERMODEL`
   - `CG_R_REGISTERSKIN`
   - `CG_R_REGISTERSHADER`
   - `CG_R_REGISTERSHADERNOMIP`
3. The direct raw `data_1074CCCC + offset` callers in native cgame match those roles exactly enough to promote the missing wrappers.

That gives two independent signals for the seam: slot order in the host table and direct raw caller shape in native cgame.

## Background-Track Pair At `+0xBC..+0xC0`

The music pair is now fully bounded, even though only one side can be promoted in JSON.

Observed local facts:

1. `sub_10025320` copies two `0x3F`-byte strings into local buffers, null-terminates them, then calls `(*(data_1074CCCC + 0xBC))(&var_44, &var_84)`.
2. That exact two-string shape matches `trap_S_StartBackgroundTrack( intro, loop )` in `ql_cgame_imports.inc`.
3. In the command dispatcher around `1004B402`, native cgame compares against the literal command `"stopMusic"` and then calls `(*(data_1074CCCC + 0xC0))()` with no arguments.
4. That exact no-argument shape matches `trap_S_StopBackgroundTrack()` and the `CG_S_STOPBACKGROUNDTRACK` handler in `cl_cgame.c`.
5. The committed Ghidra export still does not surface a stable `sub_4B02F0` function row, so `+0xC0` stays documented-only for now.

This confirms the band boundary around the render-registration seam below.

## Raw Offset `0xC4`: `R_LoadWorldMap`

`sub_4AFEE0` is now exact.

Observed local facts:

1. `data_565A1C = sub_4AFEE0`.
2. In `sub_10022F40`, native cgame clears local media state, begins the `"game media"` load pass, and then calls `(*(data_1074CCCC + 0xC4))(0x10A3FF64)` before the bulk model/shader registration loop starts.
3. That placement matches the source-side `trap_R_LoadWorldMap( mapname )` call in the early graphics-registration path: it consumes the current map name first, then begins per-asset registration.
4. The next raw slots immediately after `+0xC4` are the already-bounded `registerModel`, `registerSkin`, `registerShader`, and `registerShaderNoMip` band, which is the same order preserved by `cg_syscalls.c`.
5. The host wrapper itself is a pure import forward (`jump(data_146CC78)`), which is exactly the shape expected for a thin trap wrapper.

That closes `sub_4AFEE0` as the raw native cgame import wrapper for `R_LoadWorldMap`.

## Raw Offset `0xCC`: `R_RegisterSkin`

`sub_4BEED0` is now exact.

Observed local facts:

1. `data_565A24 = sub_4BEED0`.
2. `sub_1003D130` builds the literal asset paths:
   - `"models/players/%s/lower_%s.skin"`
   - `"models/players/%s/upper_%s.skin"`
   - `"models/players/%s/head_%s.skin"`
3. Each of those strings is passed directly to `(*(data_1074CCCC + 0xCC))(&var_44)`, and the returned handles are stored into the player model record.
4. The adjacent failure logs are explicit:
   - `Leg skin load failure: %s`
   - `Torso skin load failure: %s`
   - `Head skin load failure: %s`
5. Other raw `+0xCC` callers use the same `.skin` asset class, such as `"models/flag2/red.skin"` and `"models/powerups/harvester/blue.skin"`.

That is exact enough to promote `sub_4BEED0` as `QLCGImport_R_RegisterSkin`.

## Raw Offset `0xD0`: `R_RegisterShader`

`sub_4AFEF0` is now exact.

Observed local facts:

1. `data_565A28 = sub_4AFEF0`.
2. Native cgame calls `(*(data_1074CCCC + 0xD0))` with gameplay-facing shader/material names such as:
   - `"lagometer"`
   - `"viewDamageBlend"`
   - `"bloodSpray2"`
   - `"sprites/friend"`
   - `"railDisc"`
   - `"bulletExplosion"`
3. The same slot also receives many conventional shader path strings like `"gfx/2d/net.tga"`, `"icons/headshot"`, and `"models/weaphits/electric.tga"`, which is still consistent with the generic `R_RegisterShader` path.
4. The neighboring `+0xD4` slot is already mapped as `QLCGImport_R_RegisterShaderNoMip`, and its callers skew toward menu art, levelshots, HUD icons, flag-status art, medal art, and other pure 2D UI surfaces.
5. That `+0xD0` / `+0xD4` usage split matches the normal idTech `RegisterShader` versus `RegisterShaderNoMip` division closely enough to make the raw wrapper stable.

That closes `sub_4AFEF0` as `QLCGImport_R_RegisterShader`.

## Promoted Aliases

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4AFEE0` (`0x004AFEE0`) | `QLCGImport_R_LoadWorldMap` | Observed | Raw native cgame import wrapper for `trap_R_LoadWorldMap`. |
| `sub_4AFEF0` (`0x004AFEF0`) | `QLCGImport_R_RegisterShader` | Observed | Raw native cgame import wrapper for `trap_R_RegisterShader`. |
| `sub_4BEED0` (`0x004BEED0`) | `QLCGImport_R_RegisterSkin` | Observed | Raw native cgame import wrapper for `trap_R_RegisterSkin`. |

## Open Questions

1. `data_565A18` / `0x4B02F0` is now semantically closed as `stopBackgroundTrack`, but it still lacks a stable committed Ghidra function row, so I am keeping it unaliased in JSON.
2. The older `data_5659E8 = sub_4AFE00` raw sound-side thunk remains open. This pass did not revisit the `+0x90` seam.
