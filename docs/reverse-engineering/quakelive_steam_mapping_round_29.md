# Quake Live Steam Host Mapping Round 29

## Scope

This round revisits the remaining control rows in the raw native `cgamex86.dll` advertisement bridge seam.

Round 28 separated the raw host slab at `data_1074CCCC` from the copied local `data_1074CCF8` block and closed the `SetFrameTime` / `UpdateViewParameters` wrappers. The next stable layer is the adjacent one-argument map-path setter at `+0xF0` and the local delay-gate helpers around `data_12D2674`.

The primary local evidence for this round is:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `docs/reverse-engineering/quakelive_steam_mapping_round_13.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_28.md`

## Raw Advertisement Control Band At `+0xF0..+0x104`

The relevant raw host rows in the native cgame slab are:

- `data_565A48 = sub_4AFF50` (`+0xF0`)
- `data_565A4C = j_sub_4F2000` (`+0xF4`)
- `data_565A50 = j_sub_4F2020` (`+0xF8`)
- `data_565A58 = sub_4AFFD0` (`+0x100`, already mapped in Round 28)
- `data_565A5C = sub_4AFFE0` (`+0x104`)

The stable point here is that `+0xF0` and `+0x104` are not generic `cgDC` members. They are raw cgame import rows in the same advertisement-facing bridge seam that Round 13 and Round 28 already bounded.

## `sub_4AFF50` And `sub_4F1FE0`: Map-Path Setter

This pair is now stable enough to promote.

Observed local facts:

1. The committed Ghidra export exposes stable rows for both functions:
   - `FUN_004AFF50,004aff50,9,0,unknown`
   - `FUN_004F1FE0,004f1fe0,31,0,unknown`
2. The owning raw cgame slab contains `data_565A48 = sub_4AFF50`, which is offset `+0xF0` from `data_565958`.
3. `sub_4AFF50` is a pure tailcall to `sub_4F1FE0`.
4. `sub_4F1FE0` is a guarded one-argument dispatch through advertisement bridge vtable slot `+0x20`.
5. Native cgame prepares the argument buffer as a formatted BSP path:
   - `sub_10048BA9` writes `data_10A3FF64` with `sub_10057510(0x10A3FF64, 0x40, "maps/%s.bsp")`
6. Later in `CG_Init`, native cgame passes that same buffer through the raw import row:
   - `0x10029CA0  (*(data_1074CCCC + 0xF0))(0x10A3FF64)`
7. Round 28 already established that `+0xF0` remains on the raw host slab rather than the copied local `data_1074CCF8` block, so this is a raw bridge configuration input, not a local display-context callback.

That is enough to promote the wrapper and the underlying helper as a map-path setter for the advertisement bridge. The observed argument is the full `maps/%s.bsp` path, not just a short map name, so the promoted name stays at the path level.

## `sub_4F22E0`: Delay Gate Check

The local delay-check helper is now exact enough to name behaviorally.

Observed local facts:

1. The committed Ghidra export exposes `FUN_004F22E0,004f22e0,34,0,unknown`.
2. `sub_4F22E0` returns `1` immediately when `data_12D2674 == 0`.
3. Otherwise it returns the boolean result of `sub_4EF510() > data_12D2674`.
4. Multiple host callsites use that return value as a gate before continuing a UI/input path:
   - `sub_4B5360`
   - `sub_4B54E0`
   - `sub_4B5800`
   - `sub_4BE270`
   - `sub_4B7C3D`
5. Round 13 already bounded `data_12D2670` as advertisement-facing shared host functionality, so the guard belongs to that same subsystem rather than to generic browser code.

This is not a generic timer query. The helper is a gate that returns true once no delay is active or once the stored deadline has passed.

## `sub_4F2310` And `sub_4AFFE0`: Delay Clear Helper

The paired clear/reset helper is now stable enough to promote as well.

Observed local facts:

1. The committed Ghidra export exposes stable rows for both functions:
   - `FUN_004F2310,004f2310,11,0,unknown`
   - `FUN_004AFFE0,004affe0,9,0,unknown`
2. `sub_4F2310` performs one exact action:
   - `data_12D2674 = 0`
3. `sub_4AFFE0` is a pure tailcall to `sub_4F2310`.
4. The owning raw cgame slab contains `data_565A5C = sub_4AFFE0`, which is offset `+0x104` from `data_565958`.
5. Host code also calls the helper directly from the disconnect/reset path:
   - `0x004B8C86  sub_4F2310()`
6. That direct host use matches the behavioral read of `sub_4F22E0`: clearing the stored deadline disables the delay gate immediately.

This is enough to promote both the underlying helper and its raw cgame import wrapper as the delay-clear path for the advertisement bridge seam.

## What Stays Open

The two no-argument bridge wrappers in the middle of this band remain open:

- `data_565A4C = j_sub_4F2000` (`+0xF4`)
- `data_565A50 = j_sub_4F2020` (`+0xF8`)

Observed local facts:

1. `+0xF4` is called once late in native cgame init at `0x10029FA4`.
2. `+0xF8` is called from `sub_10029FC0()` immediately before the retail `ui_mainmenu` cvar update.
3. Those callsites are clearly bridge-facing, but the committed corpus still does not pin their public semantics tightly enough to promote names without churn.

So this round promotes only the map-path and delay-gate helpers whose behavior closes directly from arguments and state.

## Promoted Aliases

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4AFF50` (`0x004AFF50`) | `QLCGImport_AdvertisementBridge_SetMapPath` | Observed | Raw native cgame wrapper that forwards the formatted `maps/%s.bsp` path into the advertisement bridge. |
| `sub_4AFFE0` (`0x004AFFE0`) | `QLCGImport_AdvertisementBridge_ClearDelay` | Observed plus bounded inference | Raw native cgame wrapper that forwards directly into the advertisement bridge delay-clear helper. |
| `sub_4F1FE0` (`0x004F1FE0`) | `AdvertisementBridge_SetMapPath` | Observed | One-argument advertisement bridge dispatch used from native cgame with the formatted BSP path buffer. |
| `sub_4F22E0` (`0x004F22E0`) | `AdvertisementBridge_IsDelayElapsed` | Observed | Returns true when no delay is active or when the stored delay deadline has passed. |
| `sub_4F2310` (`0x004F2310`) | `AdvertisementBridge_ClearDelay` | Observed | Clears the local advertisement bridge delay/deadline state by zeroing `data_12D2674`. |

## Open Questions

1. `sub_4F2000` and `sub_4F2020` still need one more behavior-level signal before promotion. Their callsites are now bounded, but not yet semantically closed.
2. `sub_4F1FC0` remains open as the neighboring one-argument advertisement bridge dispatch. I still do not have a direct retail raw cgame call proving its input contract.
3. The no-op row at `data_565A40 = sub_4D7980` remains intentionally unnamed in subsystem terms even though the slab position is stable.
