# Quake Live Steam Host Mapping Round 67

## Scope

This round continues the writable host reconstruction work after round 66,
using already-mapped `quakelive_steam.exe` advertisement-bridge ownership to
close another concrete launcher/platform gap.

The target slice is the retail advertisement bridge bounded earlier in:

- Round 15: `QLUIImport_ActivateAdvert` and `AdvertisementBridge_InitUI`
- Round 30: advert-cell shader setup/refresh helpers
- Round 31: `QLCGImport_SetActiveAdvert` and
  `AdvertisementBridge_SetActiveAdvert`
- Round 32: lower UI advert-cell shader suppliers

Primary evidence for this source-reconstruction pass:

- `docs/reverse-engineering/quakelive_steam_mapping_round_15.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_30.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_31.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_32.md`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `src/code/client/cl_cgame.c`
- `src/code/client/cl_ui.c`
- `src/code/ui/ui_main.c`

## Reconstructed Source Closures

### `sub_4F1EF0`: `AdvertisementBridge_SetActiveAdvert`

Observed retail facts already documented in Round 31:

1. Native cgame reaches this helper through `QLCGImport_SetActiveAdvert`.
2. The cgame-side `activateAdvert` command feeds an integer advert token into
   that path.
3. `CL_Shutdown` clears the same helper with a literal zero.

Writable source closure landed in this round:

- `QL_CG_trap_SetActiveAdvert` no longer drops the argument.
- `cl_cgame.c` now tracks the active advert selection/reset state through
  `CL_AdvertisementBridge_SetActiveAdvert`, mirroring the mapped cgame-side
  host seam rather than leaving it as a dead stub.

### `sub_4F22C0`: `AdvertisementBridge_ActivateAdvert`

Observed retail facts already documented in Round 15:

1. Native UI reaches this helper through `QLUIImport_ActivateAdvert`.
2. The retail `activateAdvert` script command calls that UI import with a
   parsed integer advert id.
3. Round 31 already showed that this UI path stays distinct from the cgame-side
   active-advert state setter.

Writable source closure landed in this round:

- `QL_UI_trap_ActivateAdvert` no longer ignores the advert id.
- `cl_cgame.c` now exposes `CL_AdvertisementBridge_ActivateAdvert`, keeping the
  UI activation path distinct from the cgame-side active-state path just as the
  retail host does.

### `sub_4F20C0`: `AdvertisementBridge_InitUI`

Observed retail facts already documented in Round 15:

1. `_UI_Init` calls the no-argument host import at `0x148`.
2. The host slab forwards that row directly into `AdvertisementBridge_InitUI`.

Writable source closure landed in this round:

- `QL_UI_trap_InitAdvertisementBridge` now routes through the explicit
  `CL_AdvertisementBridge_InitUI` helper instead of only inlining a raw bridge
  refresh call.

### Advert-cell shader fallback path

Observed retail facts already documented in Rounds 30 and 32:

1. The advertisement-bridge setup/refresh helpers fall back to the ordinary
   host shader lookup path when the bridge does not override a result.
2. In the reconstructed engine, regular UI shader registration already routes
   Steam-backed resources through `CL_Steam_RegisterShader`.

Writable source closure landed in this round:

- `QL_UI_RegisterDefaultAdvertCellShader` and
  `QL_CG_RegisterDefaultAdvertCellShader` now route fallback advert shaders
  through `CL_Steam_RegisterShader`.
- That keeps advert cells on the same `steam://` cache path as the rest of the
  reconstructed Steam-backed UI image surface instead of bypassing it with a
  direct `re.RegisterShaderNoMip` call.

## Verification

This round extends the existing host validation with targeted static checks for
the advert bridge and advert shader fallback path.

Targeted result:

- `python -m pytest tests/test_steamworks_harness.py tests/test_platform_services.py tests/test_ui_menu_files.py -q`
- `42 passed`

The new assertions prove:

- UI import `82` now routes through `CL_AdvertisementBridge_InitUI`
- UI import `84` now routes through `CL_AdvertisementBridge_ActivateAdvert`
- native cgame `SetActiveAdvert` now routes through
  `CL_AdvertisementBridge_SetActiveAdvert`
- UI/cgame advert-cell fallback shader helpers now use
  `CL_Steam_RegisterShader`

## Completion Summary

No new alias rows were added in `references/analysis/quakelive_symbol_aliases.json`
this round; the mapping work here was consumed as source reconstruction against
already-promoted host ownership.

Current global `quakelive_steam.exe` mapping coverage remains:

- raw alias entries: `944`
- address-backed aliases: `943`
- Ghidra function coverage: `17.230%` of `5473`

Source reconstruction improved the writable Task 21 host baseline by removing
another retail-mapped inert bridge surface: the advertisement activation/state
callbacks and the advert-cell `steam://` fallback path now behave like first-
class host seams instead of dead stubs.
