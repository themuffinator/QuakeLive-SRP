# Quake Live Steam Host Mapping Round 26

## Scope

This round revisits the lone post-cinematic cgame wrapper at `data_565B00`, which earlier rounds left in the generic `GetEntityToken` / `inPVS` neighborhood.

The goal was to determine whether `sub_4B0330` is only loosely adjacent to the renderer export seam, or whether the committed corpus now gives enough evidence to promote it safely.

The primary local evidence for this round is:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `src/code/renderer/tr_public.h`
- `src/code/renderer/tr_init.c`
- `src/code/client/cl_cgame.c`
- `src/code/client/snd_dma.c`

## `sub_4B0330`: Renderer Export Wrapper At `0x1A8`

`sub_4B0330` is now stable enough to promote as the native cgame `GetEntityToken` wrapper.

Observed local facts:

1. The owning host slab contains `data_565B00 = sub_4B0330`, immediately after the native cinematic band and immediately before the already-mapped parser continuation at `data_565B04..data_565B14`.
2. `sub_4B0330` is a pure jump through `data_146CCD0`, so it is a thin wrapper over a cached external/exported callback rather than its own engine logic.
3. The adjacent renderer-export jump band already has exact anchors:
   - `sub_4AFFF0 -> jump(data_146CCC8)` and is already mapped as `QLCGImport_R_RegisterFont`
   - `sub_4B0100 -> jump(data_146CCCC)` and is already mapped as `QLCGImport_R_RemapShader`
4. The local renderer export table in `tr_public.h` places the next two exports in exactly this order:
   - `RegisterFont`
   - `RemapShader`
   - `GetEntityToken`
   - `inPVS`
5. `tr_init.c` assigns those exports in the same order:
   - `re.RegisterFont = RE_RegisterFont;`
   - `re.RemapShader = R_RemapShader;`
   - `re.GetEntityToken = R_GetEntityToken;`
   - `re.inPVS = R_inPVS;`
6. The committed host HLIL also shows the adjacent callback `data_146CCD4` being called directly from the sound spatialization path with two vector pointers:
   - `data_146CCD4(&data_126093C, &var_14)`
7. That call shape matches `R_inPVS( const vec3_t p1, const vec3_t p2 )` exactly and explains why the export immediately after `data_146CCD0` is already consumed without a small dedicated wrapper row.
8. In the local cgame import dispatch, the matching cgame-side contract is:
   - `case CG_GET_ENTITY_TOKEN: return re.GetEntityToken( VMA(1), args[2] );`

The important closure is not just that `sub_4B0330` sits near renderer-owned imports, but that the surrounding export order is now anchored on both sides:

- previous export anchor: `RemapShader`
- next export anchor: direct `R_inPVS` use through `data_146CCD4`

That makes `data_146CCD0` the remaining renderer export in between, which is `GetEntityToken`.

## Why This Is Stronger Than The Earlier Passes

Earlier rounds only had the slot position plus a general `GetEntityToken` / `inPVS` neighborhood guess. This round adds the missing second signal:

- the direct `data_146CCD4` vector-pair caller in sound spatialization proves the next renderer export is `inPVS`

Once that adjacent export is pinned, the wrapper at `sub_4B0330 -> data_146CCD0` is no longer ambiguous.

## Promoted Aliases

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4B0330` (`0x004B0330`) | `QLCGImport_GetEntityToken` | Observed plus bounded inference | Native cgame wrapper over the renderer `GetEntityToken` export. |

## Open Questions

1. The paired no-arg seam at `0x1C8` / `0x1CC` is still only bounded as stereo-view utility logic around `sub_10011490`; I do not yet have a stable higher-level name for either helper.
2. `sub_4B0370`, `sub_4B03C0`, and `sub_4B03D0` remain bounded but unnamed. Their call shapes are clearer now than their final API ownership.
3. The raw native cgame thunk at `0x4B02F0` remains semantically closed as `stopBackgroundTrack`, but it still does not have a stable committed Ghidra function row, so it stays documented-only.
