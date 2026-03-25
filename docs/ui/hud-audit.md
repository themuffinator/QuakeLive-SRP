# HUD & Menu Asset Audit

## Scope
This audit compares the Quake Live reference snapshot in `assets/quakelive/baseq3/ui` against the GPL tree under `src/ui`. It captures the state of script coverage, supporting assets, and build integration tasks required to reproduce Quake Live’s HUD and menu presentation inside the open-source build.

## Inventory Snapshot
### Definition Parity
| Category | Reference Count | GPL Count | Notes |
| --- | --- | --- | --- |
| `.menu` / `.txt` definitions | 65 | 65 | The file inventory is now exact. The remaining raw drift is content-only and limited to `comp_spectator.menu`, `comp_spectator_follow.menu`, `hud.txt`, `hud3.txt`, `ingame_callvote.menu`, and `ingame_join.menu`.
| `menudef.h` | 1 | 1 | The Quake Live enum definitions exist in both trees and remain the canonical owner-draw ID source.
| Accessory config (`hud*.txt`) | 3 | 3 | `hud3.txt` is present in both trees; the remaining issue is that the frozen `src/ui/hud3.txt` text still differs from retail and contains merge-conflict damage.

### GPL-Only Bootstrap Files
The GPL branch introduces the following convenience files to seed the port:
- `credential.menu` powers the Steam authentication prompt.
- `ingame_quakelive.txt` consolidates HUD owner-draw registration for testing.
- `menus_quakelive.txt` bootstraps menu loading order while the asset bundle is incomplete.

These files should remain, but their dependencies must be harmonised with the restored Quake Live assets to avoid diverging behaviour.

## Supporting Assets & Dependencies
| Area | Reference Location | GPL Status | Gap Summary |
| --- | --- | --- | --- |
| HUD & menu art | `ui/assets/{hud,score,menu,flags,main_menu,statusbar}` | Mirrored | `src/ui/assets/` now matches the retail `ui/assets/` subtree exactly (`454 / 454` files, `0` content diffs). Remaining work is packaging/mounting, not asset mirroring.
| Fonts | `baseq3/fonts/*.ttf` | Automated | `tools/build_ui_bundle.sh` pulls in the Quake Live TTFs declared in `tools/packaging/ui_bundle_manifest.json`, bakes deterministic `.dat`/`.tga` pairs via `tools/packaging/bake_fonts.py`, and records glyph metrics in `artifacts/ui_bundle/metrics/font_metrics.json` for CI triage.
| Shader scripts | `baseq3/scripts/ui*.shader` (tracked in the global asset audit) | Packaged | The UI bundle manifest stages the retail `ui*.shader` scripts into the main bundle, so gradient, cursor, and overlay materials are now part of the packaged UI payload.
| Packaging hooks | `pak/ui` structure in the reference PK3s | Automated | `tools/build_ui_bundle.sh` now stages the retail `ui/*.menu`, `ui/*.txt`, `ui/assets/*`, `baseq3/icons/*`, `baseq3/levelshots/*`, and emits both `pak_uiql.pk3` and `pak_ui_src_retail_overlay.pk3`. The remaining work is runtime QA rather than missing bundle plumbing.

## Parity Gaps & Recommended Actions
| Area | Gap | Action |
| --- | --- | --- |
| Frozen `src/ui` drift | The read-only `src/ui` tree still differs from retail in 7 files, including merge-conflicted `hud.txt`, `hud3.txt`, and `ingame_callvote.menu`. | Generate and mount the retail override layer (`scripts/ui/write_retail_ui_overrides.py` or `pak_ui_src_retail_overlay.pk3`) instead of editing `src/ui` directly.
| HUD/menu art | Quake Live’s art hierarchy is mirrored in `src/ui/assets`, and the bundle now stages those files along with icons/levelshots. | Validate runtime mounting and screenshot parity rather than adding more packaging entries.
| Fonts & readability | Glyph counts must remain in lockstep with Quake Live defaults to keep scripted `textscale` stable. | Run `tools/build_ui_bundle.sh` (font bake) and `python tests/run_ui_validation.py` before landing HUD changes so glyph or shader drift is caught in CI logs.
| Shader/material coverage | The retail shader scripts are now packaged, but they still need runtime verification to confirm gradients/cursors resolve as expected. | Validate the packaged `ui*.shader` set in a launch-time renderer smoke test and capture screenshot evidence.
| Build integration | The package flow now exists, but it still needs runtime verification against in-game renders and mount order. | Keep `tools/build_ui_bundle.sh` and `tests/run_ui_validation.py` in CI, and add launch-time UI screenshot checks on top.

## Follow-Up Validation Checklist
- [x] Confirm all menu and metadata files referenced by Quake Live scripts exist in `src/ui` with identical casing.
- [ ] Confirm the 7-file frozen drift set remains stable and that the overlay package reproduces byte-identical retail replacements.
- [ ] Verify that UI art directories resolve in-game by launching with a clean homepath and inspecting HUD, scoreboard, and menu screens.
- [x] Run font bake tooling and compare generated atlas metrics against Quake Live defaults to ensure `textscale` directives remain accurate (`tools/build_ui_bundle.sh` + `tests/run_ui_validation.py`).
- [ ] Recompile shader caches with the imported `ui*.shader` files and validate gradients/cursors in the renderer.
- [ ] Exercise the packaging workflow to ensure PK3 generation is deterministic and platform-agnostic.

## Accessibility Backlog (Prioritised)
| Priority | Task | Rationale | Dependencies |
| --- | --- | --- | --- |
| P0 | Restore color-differentiated scoreboxes with redundant numeric/text cues. | Missing score textures eliminate dual-encoded feedback for colorblind users; reinstating art plus numeric overlays restores accessibility. | Requires `ui/assets/score` bundle.
| P0 | Reinstate locale-aware country/team dropdowns. | Dropdowns currently render empty states without `country.txt`/`teaminfo.txt`, blocking text-based identification. | Requires metadata import.
| P1 | Add textual overlays to spectator ink-fade panels. | Spectator HUD relies solely on texture gradients; adding captions/tooltips aids screen readers and low-vision players. | Depends on art bundle import for final layout.
| P1 | Document accessible font scaling expectations in `assetGlobalDef`. | Contributors need guidance to maintain legible `textscale` and contrast when swapping fonts. | Requires font bake workflow.
| P2 | Provide high-contrast cursor and highlight variants. | Cursor gradients lose contrast on bright backgrounds; shipping alternative themes allows users to select readable options. | Requires shader + art packaging.
| P2 | Automate checks for owner-draw visibility flags that gate accessibility cues. | Prevents regressions where visibility flags strip textual fallback elements in competitive HUDs. | Needs scripting QA harness.
