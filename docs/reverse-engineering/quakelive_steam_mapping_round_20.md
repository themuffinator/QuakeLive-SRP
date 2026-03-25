# Quake Live Steam Host Mapping Round 20

## Scope

This round maps the native `cgamex86.dll` display-context callback seam that feeds `CG_LoadHudMenu`.

The focus is the retail callback slab rooted at `data_565958`. A fresh pass through the host HLIL, the native `cgamex86.dll` HLIL, and the local reconstruction closes the sound/render wrappers that native cgame copies into its local `cgDC`-shaped callback block before calling `Init_Display`.

The primary local evidence for this round is:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `src/code/cgame/cg_main.c`
- `src/code/ui/ui_shared.h`

## Native Cgame Display-Context Slab Base

This pass corrects the slab base explicitly before promoting any new names.

Observed local facts:

1. `quakelive_steam.exe` creates the native cgame VM with `sub_4E9FF0("cgame", &data_146CC38, &data_565958, &var_8)`, so the owning callback slab base is `data_565958`.
2. The relevant host slots are:
   - `data_565A10 = sub_4AFEC0` (`+0xB8`)
   - `data_565A14 = sub_4AFED0` (`+0xBC`)
   - `data_565A18 = 0x4B02F0` (`+0xC0`)
   - `data_565A20 = sub_4BEEC0` (`+0xC8`)
   - `data_565A2C = sub_4AFF00` (`+0xD4`)
   - `data_565A70 = sub_4BEF40` (`+0x118`)
   - `data_565A74 = sub_4B0000` (`+0x11C`)
   - `data_565A88 = sub_4BEF80` (`+0x130`)
   - `data_565A90 = sub_4B0060` (`+0x138`)
   - `data_565A94 = sub_4B0070` (`+0x13C`)
   - `data_565A9C = sub_4BEF90` (`+0x144`, already mapped as `QLCGImport_R_ModelBounds`)
   - `data_565ACC = sub_4AFFF0` (`+0x174`, already mapped as `QLCGImport_R_RegisterFont`)
3. In native cgame `sub_10029210`, those same slots are copied into the local callback slab in the order:
   - `data_10A25620 = *(result + 0xD4)`
   - `data_10A25624 = *(result + 0x138)`
   - `data_10A2563C = *(result + 0xC8)`
   - `data_10A25640 = *(result + 0x144)`
   - `data_10A25654 = *(result + 0x118)`
   - `data_10A25658 = *(result + 0x11C)`
   - `data_10A2565C = *(result + 0x130)`
   - `data_10A25660 = *(result + 0x174)`
   - `data_10A256CC = *(result + 0xB8)`
   - `data_10A256D0 = *(result + 0xBC)`
   - `data_10A256D4 = *(result + 0xC0)`
4. `src/code/cgame/cg_main.c` assigns the same `displayContextDef_t` members in `CG_LoadHudMenu`, and `src/code/ui/ui_shared.h` preserves the matching field order:
   - `registerShaderNoMip`
   - `setColor`
   - `registerModel`
   - `modelBounds`
   - `clearScene`
   - `addRefEntityToScene`
   - `renderScene`
   - `registerFont`
   - `registerSound`
   - `startBackgroundTrack`
   - `stopBackgroundTrack`

That alignment gives two independent signals for every promotion below: the host slot position and the source-side callback order.

## Sound And Background-Track Callbacks At `+0xB8..+0xC0`

The sound trio at the tail of `displayContextDef_t` is now semantically closed.

Observed local facts:

1. Native cgame copies `*(result + 0xB8)`, `*(result + 0xBC)`, and `*(result + 0xC0)` into `data_10A256CC`, `data_10A256D0`, and `data_10A256D4` in `sub_10029210`.
2. In `CG_LoadHudMenu`, the matching source assignments are:
   - `cgDC.registerSound = &trap_S_RegisterSound;`
   - `cgDC.startBackgroundTrack = &trap_S_StartBackgroundTrack;`
   - `cgDC.stopBackgroundTrack = &trap_S_StopBackgroundTrack;`
3. The host wrappers are:
   - `sub_4AFEC0`: pure tailcall to `sub_4D9E50`
   - `sub_4AFED0`: pure tailcall to `sub_4DB060`
   - `data_565A18`: literal thunk at `0x4B02F0`
4. The committed Ghidra export still does not surface a stable `sub_4B02F0` function row, so I am documenting `+0xC0` as the `stopBackgroundTrack` slot without adding a JSON alias yet.

This is enough to promote `sub_4AFEC0` and `sub_4AFED0` as the native cgame `registerSound` and `startBackgroundTrack` import wrappers.

## Render Registration At `+0xC8` And `+0xD4`

The model/shader registration pair is now high-confidence.

Observed local facts:

1. `sub_10029210` copies `*(result + 0xC8)` into `data_10A2563C`, matching `cgDC.registerModel = &trap_R_RegisterModel;` in `CG_LoadHudMenu`.
2. `sub_10029210` copies `*(result + 0xD4)` into `data_10A25620`, matching `cgDC.registerShaderNoMip = &trap_R_RegisterShaderNoMip;`.
3. `sub_10029420` repeatedly calls `(*(data_1074CCCC + 0xD4))` with 2D HUD asset names such as:
   - `"ui/assets/gradientbar2.tga"`
   - `"menu/art/fx_base"`
   - `"ui/assets/scrollbar.tga"`
4. The local reconstruction uses `trap_R_RegisterShaderNoMip` for that same asset-cache path in `CG_LoadHudMenu`.
5. The host wrappers are simple import forwards:
   - `sub_4BEEC0 -> jump(data_146CC68)`
   - `sub_4AFF00 -> jump(data_146CC74)`

That closes `sub_4BEEC0` as `QLCGImport_R_RegisterModel` and `sub_4AFF00` as `QLCGImport_R_RegisterShaderNoMip`.

## Scene And Draw Callbacks At `+0x118..+0x13C`

The scene/render band is now pinned from both slot order and wrapper signature.

Observed local facts:

1. `sub_10029210` copies:
   - `*(result + 0x118)` into `data_10A25654`
   - `*(result + 0x11C)` into `data_10A25658`
   - `*(result + 0x130)` into `data_10A2565C`
   - `*(result + 0x138)` into `data_10A25624`
   - `*(result + 0x13C)` into `data_10A2562C`
2. `CG_LoadHudMenu` assigns the matching callbacks in exactly that order:
   - `cgDC.clearScene = &trap_R_ClearScene;`
   - `cgDC.addRefEntityToScene = &trap_R_AddRefEntityToScene;`
   - `cgDC.renderScene = &trap_R_RenderScene;`
   - `cgDC.setColor = &trap_R_SetColor;`
   - `cgDC.drawStretchPic = &trap_R_DrawStretchPic;`
3. The host wrappers line up with the expected call shapes:
   - `sub_4BEF40 -> jump(data_146CC84)` with no local argument shuffling
   - `sub_4B0000 -> jump(data_146CC88)` with one pointer argument
   - `sub_4BEF80 -> jump(data_146CC9C)` with one pointer argument
   - `sub_4B0060 -> jump(data_146CCA4)` with one color-vector pointer argument
   - `sub_4B0070 -> data_146CCA8(arg1..arg8, arg9)` with the exact eight-float-plus-handle shape from `drawStretchPic`
4. The neighboring anchors at `+0x144` (`QLCGImport_R_ModelBounds`) and `+0x174` (`QLCGImport_R_RegisterFont`) match the already-promoted aliases from earlier rounds, which keeps the whole band aligned.

This is enough to promote the full scene/render subset safely.

## Promoted Aliases

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4AFEC0` (`0x004AFEC0`) | `QLCGImport_S_RegisterSound` | Observed | Native cgame import wrapper for `trap_S_RegisterSound` in the `cgDC` callback slab. |
| `sub_4AFED0` (`0x004AFED0`) | `QLCGImport_S_StartBackgroundTrack` | Observed | Native cgame import wrapper for `trap_S_StartBackgroundTrack`. |
| `sub_4AFF00` (`0x004AFF00`) | `QLCGImport_R_RegisterShaderNoMip` | Observed | Native cgame import wrapper for HUD/menu shader registration. |
| `sub_4BEEC0` (`0x004BEEC0`) | `QLCGImport_R_RegisterModel` | Observed | Native cgame import wrapper for `trap_R_RegisterModel`. |
| `sub_4BEF40` (`0x004BEF40`) | `QLCGImport_R_ClearScene` | Observed | Native cgame import wrapper for `trap_R_ClearScene`. |
| `sub_4BEF80` (`0x004BEF80`) | `QLCGImport_R_RenderScene` | Observed | Native cgame import wrapper for `trap_R_RenderScene`. |
| `sub_4B0000` (`0x004B0000`) | `QLCGImport_R_AddRefEntityToScene` | Observed | Native cgame import wrapper for `trap_R_AddRefEntityToScene`. |
| `sub_4B0060` (`0x004B0060`) | `QLCGImport_R_SetColor` | Observed | Native cgame import wrapper for `trap_R_SetColor`. |
| `sub_4B0070` (`0x004B0070`) | `QLCGImport_R_DrawStretchPic` | Observed | Native cgame import wrapper for `trap_R_DrawStretchPic`. |

## Open Questions

1. `data_565A18` / `0x4B02F0` is semantically the native cgame `stopBackgroundTrack` slot, but it still lacks a stable committed Ghidra function row, so I am leaving it documented but unaliased.
2. This round intentionally does not rename the adjacent local cgame helpers (`sub_100126A0`, `sub_10008440`, `sub_100083B0`, `sub_10008410`) because their ownership is already clear from source reconstruction and the remaining value is on the host import side.
