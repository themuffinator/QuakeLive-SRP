# UI Strings & Assets Parity Audit (Quake Live)

## Scope
This report cross-references the committed `src/ui/` tree with the retail Quake Live
`assets/quakelive/baseq3/ui/` drop and the UI HLIL-backed mapping notes to highlight
remaining parity gaps after the writable `src/code/ui/` runtime work.

## Sources Reviewed
- `assets/quakelive/baseq3/ui/`
- `references/hlil/quakelive/uix86.all/uix86.dll_hlil.txt`
- `docs/reverse-engineering/ui-mapping-pass-2026-03-20.md`
- `src/code/ui/`
- `src/ui/`

## Repository Constraint Note
`src/ui/` is read-only in this repository, so remaining menu-script drift cannot be
fixed in place by agent edits. The writable mitigation is now
`scripts/ui/write_retail_ui_overrides.py`, which emits retail-correct copies of the
drifted files into a writable homepath-style overlay.

## Inventory Parity
`src/ui/` and `assets/quakelive/baseq3/ui/` currently have the same committed file
inventory: `520` files on each side, including a fully mirrored `assets/` subtree.

Within `ui/assets`, the parity state is exact:
- `src/ui/assets/` exists.
- `src/ui/assets/` and `assets/quakelive/baseq3/ui/assets/` both contain `454` files.
- There are `0` missing files, `0` extra files, and `0` content diffs in that subtree.

That means the current `src/ui` parity gaps are no longer missing-file or missing-asset
problems inside `src/ui`; they are content drift problems in a small set of text panels.

## Remaining `src/ui` Content Drift
Only `7` committed `src/ui` files still differ from their retail Quake Live counterparts:
- `comp_spectator.menu`
- `comp_spectator_follow.menu`
- `hud.txt`
- `hud3.txt`
- `ingame_callvote.menu`
- `ingame_join.menu`
- `menudef.h`

The observed drift breaks down into three buckets:
- Unresolved merge-conflict damage:
  - `hud.txt`
  - `hud3.txt`
  - `ingame_callvote.menu`
- Source-biased menu-script drift:
  - `comp_spectator.menu`
  - `comp_spectator_follow.menu`
  - `ingame_join.menu`
- Header drift:
  - `menudef.h`

Representative mismatches:
- The spectator compare menus in `src/ui/comp_spectator.menu` and
  `src/ui/comp_spectator_follow.menu` still use the older
  `CG_1ST_PLYR_HEALTH_ARMOR`, `CG_2ND_PLYR_HEALTH_ARMOR`, and
  `CG_HEALTH_COLORIZED` ownerdraw surface, while the retail files use the Quake Live
  spectator ids `CG_SPEC_COMPARE_PRIMARY`, `CG_SPEC_COMPARE_SECONDARY`,
  `CG_SPEC_FOLLOW_PRIMARY`, and `CG_SPEC_FOLLOW_SECONDARY`.
- `src/ui/ingame_join.menu` still carries the older country dropdown block that is not
  present in the retail file.
- `src/ui/menudef.h` still exposes a local `FEEDER_COUNTRIES` define and a block of
  older ownerdraw ids that are absent from the retail header.

## Writable Mitigation
`scripts/ui/write_retail_ui_overrides.py` compares `src/ui/` against the retail
`assets/quakelive/baseq3/ui/` tree and writes retail copies of the drifted files into
a writable homepath-style overlay at `baseq3/ui/...`.

`tools/build_ui_bundle.sh` now also packages the same drift set into
`build/ui_bundle/pak_ui_src_retail_overlay.pk3`, so source-based layouts can ship the
retail corrections as a layered UI package without mutating the frozen `src/ui` tree.

Default usage:

```powershell
python scripts/ui/write_retail_ui_overrides.py
```

By default this writes overrides to:

```text
build/ui_retail_overrides/baseq3/ui/
```

That overlay can be mounted through a writable `fs_homepath` without mutating the
read-only `src/ui` tree.

## External Asset Gap Outside `src/ui`
The remaining art discrepancy now sits outside `src/ui`: the mapped retail UI still
references a small `menu/art/*` set that is absent from `assets/quakelive/baseq3/menu/art/`,
including:
- `menu/art/3_cursor2`
- `menu/art/fx_base`
- `menu/art/fx_blue`
- `menu/art/fx_cyan`
- `menu/art/fx_grn`
- `menu/art/fx_red`
- `menu/art/fx_teal`
- `menu/art/fx_white`
- `menu/art/fx_yel`
- `menu/art/unknownmap`

Those are not `src/ui` parity gaps, but they remain relevant to retail-correct UI
rendering because the writable engine code still registers and uses those names.

## Notes on Backlog Items
`docs/documentation-backlog.md` highlights metadata text tables such as `country.txt`,
`teaminfo.txt`, and `hud3.txt`. Those files already exist in both
`assets/quakelive/baseq3/ui/` and `src/ui/`; the remaining issue is the content drift
called out above, not file absence.
