# Quake Live Steam Host Mapping Round 28

## Scope

This round corrects the ownership of the native `cgamex86.dll` callback seam around `data_565A54..data_565A58`.

The main goal was to stop treating that band as if it were part of the copied local `cgDC` block from `sub_10029210`, and instead classify the stable rows as raw advertisement-bridge callbacks that stay on `data_1074CCCC`.

The primary local evidence for this round is:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `docs/reverse-engineering/quakelive_steam_mapping_round_13.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_20.md`

## `data_1074CCCC` Versus `data_1074CCF8`

The raw and copied callback slabs are now explicitly separated.

Observed local facts:

1. Native cgame `sub_10029210` starts from `result = data_1074CCCC` and then builds a second local slab at `data_10A25620`.
2. That function finishes by setting `data_1074CCF8 = &data_10A25620`.
3. The copied local slab only selects specific rows from the raw slab, such as:
   - `*(result + 0xD4)` -> `data_10A25620`
   - `*(result + 0x138)` -> `data_10A25624`
   - `*(result + 0xC8)` -> `data_10A2563C`
   - `*(result + 0x144)` -> `data_10A25640`
   - `*(result + 0x118)` -> `data_10A25654`
   - `*(result + 0x11C)` -> `data_10A25658`
   - `*(result + 0x130)` -> `data_10A2565C`
   - `*(result + 0x174)` -> `data_10A25660`
4. The raw advertisement rows at `+0xFC` and `+0x100` are not copied into `data_1074CCF8`.
5. That means native cgame uses two different callback surfaces:
   - `data_1074CCCC` for the full retail host slab
   - `data_1074CCF8` for the reduced local `cgDC`-shaped copy

This distinction matters because the `0xFC..0x100` band is raw-slab-only. It should not be inferred from `displayContextDef_t` field order.

## Raw Advertisement Bridge Band At `+0xF4..+0x104`

The owning host rows in the raw cgame slab are:

- `data_565A4C = j_sub_4F2000` (`+0xF4`)
- `data_565A50 = j_sub_4F2020` (`+0xF8`)
- `data_565A54 = sub_4AFF80` (`+0xFC`)
- `data_565A58 = sub_4AFFD0` (`+0x100`)
- `data_565A5C = sub_4AFFE0` (`+0x104`)

Round 13 already established that the small `sub_4AFF*` wrappers belong to the advertisement bridge behind `data_12D2670`, not to the browser/Awesomium path. This pass closes the two wrappers whose exact host targets are already named.

## `sub_4AFFD0`: Raw Cgame Wrapper For `AdvertisementBridge_SetFrameTime`

`sub_4AFFD0` is now stable enough to promote.

Observed local facts:

1. The committed Ghidra export exposes a stable `FUN_004AFFD0,004affd0,9,0,unknown` row.
2. The owning raw cgame slab contains `data_565A58 = sub_4AFFD0`, which is offset `+0x100` from the slab base `data_565958`.
3. `sub_4AFFD0` is a pure tailcall to `sub_4F1F50`.
4. Round 13 already promoted `sub_4F1F50` as `AdvertisementBridge_SetFrameTime`.
5. Native cgame calls the raw slot directly during loading/progress updates:
   - `(*(data_1074CCCC + 0x100))(0x3E8)` at `0x1001CBD8`
   - the same `0x3E8` call repeats at `0x1001CDEF`, `0x10022FDD`, `0x10024A06`, `0x10029C8E`, `0x10029CFD`, `0x10029D4A`, `0x10029D97`, and `0x10029F1A`
6. Because `+0x100` never flows into the copied `data_1074CCF8` slab, this is raw host callback ownership, not a local `cgDC` member.

That is enough to promote `sub_4AFFD0` as the native cgame advertisement-bridge frame-time wrapper.

## `sub_4AFF80`: Raw Cgame Wrapper For `AdvertisementBridge_UpdateViewParameters`

`sub_4AFF80` is now stable enough to promote at the wrapper level.

Observed local facts:

1. The committed Ghidra export exposes a stable `FUN_004AFF80,004aff80,60,0,unknown` row.
2. The owning raw cgame slab contains `data_565A54 = sub_4AFF80`, which is offset `+0xFC` from `data_565958`.
3. `sub_4AFF80` is a pure tailcall to `sub_4F1F70`.
4. Round 13 already promoted `sub_4F1F70` as `AdvertisementBridge_UpdateViewParameters`.
5. The wrapper preserves the full retail call signature into that helper:
   - four integer/pointer-sized arguments
   - three float arguments
   - two trailing integer/pointer-sized arguments
6. Like `+0x100`, this row is absent from the `sub_10029210` copy into `data_1074CCF8`, which keeps it on the raw host slab rather than the local `cgDC` subset.

This is not enough to recover user-facing field names for each argument yet, but it is enough to stabilize the wrapper as the raw cgame import that forwards into the already-mapped advertisement view-parameter helper.

## What Stays Open In This Band

Three nearby raw advertisement rows are still documented-only:

- `data_565A4C = j_sub_4F2000` (`+0xF4`)
- `data_565A50 = j_sub_4F2020` (`+0xF8`)
- `data_565A5C = sub_4AFFE0` (`+0x104`)

Observed local facts:

1. `+0xF4` is called once during native cgame startup at `0x10029FA4`.
2. `+0xF8` is called once in `sub_10029FC0` before the `ui_mainmenu` cvar registration.
3. `sub_4AFFE0` tailcalls `sub_4F2310`, which only resets `data_12D2674`.
4. Those rows are clearly part of the same advertisement-facing bridge surface, but I do not yet have a stable behavioral name for each one.

So this round promotes only the two wrappers whose downstream helper ownership is already exact.

## Promoted Aliases

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4AFF80` (`0x004AFF80`) | `QLCGImport_AdvertisementBridge_UpdateViewParameters` | Observed plus bounded inference | Raw native cgame wrapper that forwards directly into `AdvertisementBridge_UpdateViewParameters`. |
| `sub_4AFFD0` (`0x004AFFD0`) | `QLCGImport_AdvertisementBridge_SetFrameTime` | Observed | Raw native cgame wrapper that forwards directly into `AdvertisementBridge_SetFrameTime`. |

## Open Questions

1. `j_sub_4F2000` and `j_sub_4F2020` are now clearly part of the same raw advertisement bridge seam, but they still need one more behavior-level signal before promotion.
2. `sub_4AFFE0 -> sub_4F2310` is only bounded as an advertisement bridge reset/throttle clear path; the final public-facing name is still open.
3. The renderer-facing raw rows at `+0x12C`, `+0x134`, and `+0x140` remain intentionally untouched here. The `data_1074CCCC` versus `data_1074CCF8` split proved that forcing those names from local `cgDC` order would still be unsafe.
