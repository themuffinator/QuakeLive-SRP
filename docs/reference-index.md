# Reference Index

This document catalogs the material checked into the `references/` directory and links each artifact to the corresponding Quake Live or Quake III Arena module in `src/`. "Gap status" indicates whether we already have matching source in this repo or if additional recovery work is required.

## HLIL dumps

| Reference path | Contents & purpose | Implied module(s) | Matching source location(s) | Gap status | Suggested follow-up owner |
| --- | --- | --- | --- | --- | --- |
| `references/hlil/quakelive/cgamex86.dll/` (`cgamex86.dll_hlil.txt` and split parts) | High Level IL disassembly of the Quake Live client game module. | Client Game VM | `src/code/cgame/` | **Covered** – source tree present, needs parity checks only. | Game VM reverse engineering |
| `references/hlil/quakelive/qagamex86.dll/` (`qagamex86.dll.bndb_hlil_part*.txt`) | HLIL dump of the dedicated game logic VM used by the server. | Game VM (server) | `src/code/game/` | **Covered** – source available for comparison. | Game VM reverse engineering |
| `references/hlil/quakelive/uix86.all/` (`uix86.dll_hlil.txt` and part files) | HLIL reconstruction of the UI dynamic library that drives menus/HUD. | UI VM | `src/code/ui/`, supplemental menu defs in `src/ui/` | **Covered** – sources mirror binary, diff audit recommended. | UI systems |
| `references/hlil/quakelive/quakelive_steam.exe/` (`quakelive_steam.exe_hlil_part*.txt`) | HLIL export of the Windows launcher that hosts the game and Steam hooks. | Native launcher & platform glue | _No equivalent in `src/`_ | **Missing** – native host code absent from repo; see `docs/reverse-engineering/quakelive_steam_parity_plan.md` for subsystem mapping. | Platform integration (Windows/Steam) |
| `references/hlil/quake3/quake3.exe/` (`quake3.exe_hlil_part*.txt`) | HLIL of the original Quake III Arena executable for historical parity. | Engine (client/server/renderer) | `src/code/client/`, `src/code/qcommon/`, `src/code/server/`, `src/code/renderer/` | **Covered** – open-source engine already imported. | Engine maintainers |

## Ghidra reference corpus

| Reference path | Contents & purpose | Implied module(s) | Matching source location(s) | Gap status | Suggested follow-up owner |
| --- | --- | --- | --- | --- | --- |
| `references/reverse-engineering/ghidra/quakelive_steam/` | Committed Ghidra export set for the retail Windows host executable: metadata, imports/exports, function inventory, promoted symbols, and top-function decompiles. | Native launcher, platform glue, Steam and Awesomium host behavior | `src/code/client/`, `src/code/qcommon/`, `src/code/renderer/`, `src-re/` | **Partial** – evidence is now committed, but source reconstruction is still missing for large parts of the host stack. | Platform integration (Windows/Steam) |
| `references/reverse-engineering/ghidra/awesomium_process/` | Committed Ghidra export set for the retail Awesomium helper subprocess. See `docs/reverse-engineering/awesomium_process-mapping.md` and the `awesomium_process` alias slab in `references/analysis/quakelive_symbol_aliases.json` for the current symbol recovery pass. | Browser subprocess bootstrap, CRT/runtime glue | `src/code/win32/awesomium_process.cpp`, `src/code/awesomium_process.vcxproj`, external Awesomium SDK `awesomium.lib` | **Covered** – the repo now reconstructs the executable-owned bootstrap and build surface while keeping the Awesomium SDK/runtime external; the remaining browser runtime still belongs to `awesomium.dll`, not to the helper itself. | Platform integration (Windows/Awesomium) |
| `references/reverse-engineering/ghidra/cgamex86/` | Structured Ghidra export set for the retail client game module. See `references/symbol-maps/cgame.json`, `docs/reverse-engineering/cgame-mapping.md`, `docs/reverse-engineering/cgame-cgs.md`, `docs/reverse-engineering/cgame-cg.md`, `docs/reverse-engineering/cgame-cgmedia.md`, `docs/reverse-engineering/cgame-clientinfo.md`, `docs/reverse-engineering/cgame-centity.md`, `docs/reverse-engineering/cgame-markpoly.md`, `docs/reverse-engineering/cgame-letype.md`, `docs/reverse-engineering/cgame-localentity.md`, and `docs/reverse-engineering/cgame-score.md` for the current function and type recovery passes. | Client Game VM | `src/code/cgame/` | **Covered** – use for parity audits, naming recovery, HUD/prediction control-flow mapping, and top-level `cgs_t` / `cg_t` / `cgMedia_t` / `clientInfo_t` / `centity_t` / `markPoly_t` / `localEntity_t` / `score_t` layout recovery plus `leType_t` enum recovery. | Game VM reverse engineering |
| `references/reverse-engineering/ghidra/qagamex86/` | Structured Ghidra export set for the retail server-side game module. | Game VM (server) | `src/code/game/` | **Covered** – use for gameplay parity and configstring recovery. | Game VM reverse engineering |
| `references/reverse-engineering/ghidra/uix86/` | Structured Ghidra export set for the retail UI module. | UI VM | `src/code/ui/`, `src/ui/` | **Covered** – use for menu dispatch, feeder, and bridge fallback analysis. | UI systems |

## Extracted assets

| Reference path | Contents & purpose | Implied module(s) | Matching source location(s) | Gap status | Suggested follow-up owner |
| --- | --- | --- | --- | --- | --- |
| `assets/quakelive/baseq3/cgamex86.dll` | Shipped client VM binary. Useful for binary-to-source diffing. | Client Game VM | `src/code/cgame/` | **Covered** – rebuilds possible from current source. | Game VM reverse engineering |
| `assets/quakelive/baseq3/qagamex86.dll`, `qagamex64.so`, `qagamei386.so` | Windows and Linux server VM binaries. | Game VM (server) | `src/code/game/` | **Covered** – cross-platform sources present; verify Linux build scripts. | Game VM reverse engineering |
| `assets/quakelive/baseq3/uix86.dll` | Shipping UI VM binary. | UI VM | `src/code/ui/`, `src/ui/` | **Covered** – source available; investigate UI asset diffs. | UI systems |
| `assets/quakelive/baseq3/ui/` | Extracted menu definitions and UI assets (`*.menu`, `assets/`, etc.). | UI data layer | `src/ui/` | **Covered** – text assets match repo copy; ensure localization parity. | UI systems |
| `assets/quakelive/baseq3/botfiles/` | Bot chat scripts and behavior configs. | Bot AI | `src/code/botlib/` | **Covered** – botlib source available; needs data verification. | AI/bot maintainer |
| `assets/quakelive/baseq3/scripts/`, `maps/`, `fonts/`, `icons/`, config samples (`*.cfg`) | Gameplay scripts, map metadata, HUD fonts/icons, shipping config baselines. | Game content pipeline | `src/code/game/` (script loaders), `src/code/client/` (HUD/font usage) | **Partial** – runtime loaders exist, but actual art/map sources are not present. | Content pipeline |
| `assets/quake3/src/` | Snapshot of the GPL Quake III Arena source release used as upstream. | Whole engine & toolchain | `src/` (mirrors this layout) | **Covered** – repository already seeded with same tree. | Engine maintainers |

## Notable gaps & suggested actions

- **Cgame corpus disagreements:** `docs/reverse-engineering/cgame-mapping.md` records two current mismatches that should survive future corpus refreshes: Ghidra listing `0x10063D56 entry` as an export while HLIL only exports `dllEntry`, and HLIL exposing `CG_Init` at `0x10029820` while the committed Ghidra function inventory omits that boundary.
- **Native launcher / platform services:** `quakelive_steam.exe` HLIL shows we lack the Windows host executable, Steam API bindings (client + server), workshop/UGC glue, and any anti-cheat/bootstrap logic. See `docs/reverse-engineering/quakelive_steam_parity_plan.md` for the proposed subsystem mapping and integration points.
- **Art & map source assets:** While compiled assets (`maps/`, `icons/`, fonts) are preserved, we do not have the editable source files (map `.map`, vector art, PSDs). Content pipeline owners should source original asset repositories or recreate tooling to regenerate them.
- **Service-side integrations:** No references for Quake Live backend services (authentication, stats) were found. If these are required, coordination with LiveOps/Backend is needed to locate service definitions.
