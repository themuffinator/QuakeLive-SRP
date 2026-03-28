# Implementation Plan

This plan tracks the highest-value parity work remaining after the 2026-03-06 audit refresh.

## Strategic goal

The long-term parity target is that this engine should, in theory, be able to replace the retail Quake Live engine: load retail `cgamex86.dll`, `qagamex86.dll`, and `uix86.dll`, present the retail main menu, and interoperate with retail Quake Live server/platform flows. Quake Live-only online services remain behind `QL_BUILD_ONLINE_SERVICES`, default disabled, until an open replacement path exists.

## Recently closed

### Task 20: Match-flow configstring parity [COMPLETED]
Priority: High
Files: `src/code/game/g_match_state.c`, `src/code/game/g_main.c`, `src/code/game/g_spawn.c`, `src/code/cgame/cg_servercmds.c`, `src/code/cgame/cg_draw.c`, `src/code/cgame/cg_scoreboard.c`, `src/code/cgame/cg_newdraw.c`

Retail HLIL showed dedicated configstring handling for sudden-death and ready-up state that the repo only partially mirrored.

Completed work:

1. Published `CS_SUDDENDEATH_STATUS` from qagame.
2. Parsed `CS_SUDDENDEATH_STATUS`, `CS_READYUP_STATUS`, and `CS_WARMUP_READY` in cgame.
3. Routed ready-up deadline and warmup readiness counts into the warmup overlay.
4. Switched HUD sudden-death state to the runtime flag instead of the spawn-delay configuration flag.

### Task 25: Cgame particle module parity cleanup [COMPLETED]
Priority: Medium
Files: `src/code/cgame/cg_marks.c`, `src/code/cgame/cg_particles.c`, cgame build manifests

Retail HLIL shows a compact client particle subsystem: a 1024-slot arena, an `explode1`-only animation registry, and a `CG_ParticleExplosion` path that seeds animated rocket sprites at half-alpha. The repo had drifted into a split state where the compiled runtime lived in `cg_marks.c` while the standalone `cg_particles.c` copy carried older Wolf-style expansion data that was not wired into the build.

Completed work:

1. Removed the duplicate particle runtime block from `cg_marks.c` and restored `cg_particles.c` as the compiled owner across the cgame build manifests.
2. Reduced the shader animation registry to the retail-backed `explode1` entry and restored the 1024-particle arena size recorded in HLIL.
3. Aligned `CG_ParticleExplosion` with the retail alpha and case-insensitive animation lookup behavior used by the rocket explosion path.

### Task 26: Native game-module import/export parity [COMPLETED]
Priority: Critical
Files: `src/code/qcommon/vm.c`, `src/code/client/cl_cgame.c`, `src/code/client/cl_ui.c`, `src/code/server/sv_game.c`, `src/code/cgame/*`, `src/code/game/*`, `src/code/ui/*`, platform DLL loaders, export-validation tooling

Retail Quake Live native DLLs do not use the legacy `vmMain` numbering directly. They expose a structured `dllEntry` handshake plus recovered native export-slot layouts that differ from the old Q3 VM ABI.

Completed work:

1. Recovered and named the native export-slot tables for `cgame`, `qagame`, and `ui` without renumbering the legacy `vmMain` enums.
2. Restored the structured Quake Live `dllEntry(exports, imports, apiVersion)` seam in the module-side source and platform DLL loaders.
3. Updated native dispatch so engine `VM_Call` numbers map onto the recovered retail export-slot order instead of indexing `dllExports` directly.
4. Split native import-table dispatch from legacy syscall-contract logging so source-built native DLL traffic no longer looks like old VM syscall traffic.
5. Added export-manifest validation and runtime verification proving the rebuilt engine loads source-built native `ui`, `qagame`, and `cgame` DLLs on the normal startup and map paths.

## Current highest-priority open work

### Task 21: Native launcher/platform host reconstruction [OPEN]
Priority: Critical
Primary areas: `src/code/client/`, `src/code/qcommon/`, platform bridge layers

The largest remaining parity gap is still the retail `quakelive_steam.exe` host stack. The source tree lacks direct reconstruction for:

1. Steam-backed platform/bootstrap services.
2. Web/Awesomium-style navigation and resource bridge behavior.
3. Launcher-to-engine state publication used by retail menus and platform flows.
4. Strict compatibility validation against retail game DLLs and their exact runtime assumptions, not just the reconstructed source-built DLLs.

Short-term goal:

- identify the smallest vertical slice that removes a real retail behavior gap without requiring a full browser runtime

Remaining work after Task 26:

1. Validate the engine against the retail `cgamex86.dll`, `qagamex86.dll`, and `uix86.dll` binaries and document any import or return-value mismatches that still only work for source-built DLLs.
2. Close any residual ownership, restart, or lifetime differences in native module calls where retail binaries may expect stricter host behavior than the reconstructed source currently exercises.
3. Reconstruct the launcher/bootstrap/platform surfaces needed for retail main-menu flow, server-browser flow, and network or auth hand-off behavior.
4. Keep UI/menu compatibility work focused on engine-side tolerance and writable bridge layers because the retail asset/UI stack is still missing and `src/ui/` remains read-only.

### Task 22: UI/menu asset and compatibility remediation [OPEN]
Priority: High
Primary areas: engine-side UI compatibility and documentation

Fresh runtime verification still reports many missing retail UI assets plus `ui/hud.menu` compatibility warnings.

Constraints:

- `src/ui/` is read-only
- retail menu/assets cannot be reconstructed by freely editing the UI VM tree in this repo

Actionable work:

1. Improve engine-side tolerance for retail menu constructs where possible.
2. Audit which missing assets are true parity blockers versus harmless warnings.
3. Document the runtime-visible gaps that remain because the retail UI asset stack is absent.

Completed in this task:

1. Restored the retail native UI export-table seam in the writable engine/UI surface by adding `UI_RefreshDisplayContext`, `Menus_AnyVisible`, `UI_ForEachArenaName`, and `UI_DrawAdvertisementWaitScreen` parity helpers outside the read-only `src/ui/` tree.
2. Restored the missing source-side `UI_CDKeyMenu` wrapper layer in `src/code/ui/ui_cdkey.c`, wiring the legacy public entry points back to the generated bridge credential menu and re-adding the missing `ui.q3asm` source manifest plus `ui.vcxproj` source entry.
3. Restored the retail `UI_ConsoleCommand` wrappers for `listPlayerModels`, `menu_open`, and `menu_close` in the writable `src/code/ui/` runtime surface.
4. Restored the retail-only `UI_CROSSHAIR_COLOR` and `UI_VOTESTRING` ownerdraw paths in `src/code/ui/ui_main.c`, including the numbered crosshair-color palette control.
5. Restored the retail `UI_STARTING_WEAPONS` ownerdraw path in `src/code/ui/ui_main.c`, including the loadout-mask icon strip and queued-primary preview sourced from `CS_LOADOUT_MASK` and `cg_weaponPrimaryQueued`.
6. Restored the retail advert compatibility seam in the writable UI runtime by adding `cellId`/`defaultContent` parsing, `activateAdvert`, advert-cell shader setup or refresh helpers, and the `UI_ADVERT` draw path outside the read-only `src/ui/` tree.
7. Restored retail item-level `font` compatibility in the writable UI runtime by adding `ItemParse_font`, explicit item font buckets, and font-aware text measurement or paint callbacks so the read-only Quake Live menu scripts no longer depend on GPL-era scale heuristics alone.
8. Restored the retail `toggle` script command in the writable UI runtime by mirroring the named-menu open or close branch recorded in the retail script command table and HLIL.
9. Aligned the retail `setplayermodel` and `setplayerhead` script handlers with the mapped `model` and `headmodel` cvar targets instead of the older GPL team-model cvars.
10. Restored the retail `precision`, `cvara`, `cvarInt`, `cvarPreset`, and `cvarPresetList` parser/runtime slice in the writable UI runtime, including preset-list synchronization, preset application, slider-color dispatch, and precision-aware cvar text formatting for the read-only Quake Live option menus.
11. Restored the retail `UI_SERVER_SETTINGS` ownerdraw in the writable UI runtime, consuming the currently mirrored `CS_SERVERINFO`, `CS_PMOVE_SETTINGS`, and `CS_CUSTOM_SETTINGS` surfaces for gametype, limit, movement, Instagib, and modified-weapon panel rows while leaving the undocumented retail `0x2A9` / `0x2AA` configstring backend as the remaining gap.
12. Restored the retail `UI_NEXTMAP` ownerdraw in the writable UI runtime by fetching the undocumented `0x29A` next-map configstring slot first and falling back to the mirrored `CS_ROTATION_TITLES` payload or cached rotation metadata until the exact backend publisher is recovered.
13. Restored the native `uix86.dll` project seam for `Debug|Win32` and `Release|Win32` by wiring `ui.def` back into the linker settings and re-enabling the native UI source set so the built DLL exports `vmMain` and `dllEntry` instead of linking as a near-empty stub.
14. Closed the native UI loader-validation gap by fixing the full-source `ui_main.c` / credential-bridge compile blockers so the engine now loads `build\win32\Debug\bin\baseq3\uix86.dll` directly during the normal windowed validation pass instead of rejecting it and falling back to the retail asset DLL.
15. Restored the retail `backgroundSize`, `cvarTest2`/`3`/`4`, `showCvar2`/`3`/`4`, and `hideCvar2`/`3`/`4` parser/runtime slice in the writable UI runtime, and widened the shared menu item bank so the shipped read-only Quake Live menus no longer desync after the old 96-item ceiling is exceeded.
16. Removed the source-only startup `gameinfo.txt` bootstrap from `_UI_Init` and added a bounded `UI_LoadBestScores` guard so missing retail `gameinfo.txt` assets no longer degrade into `games/(null)_0.game` / `demos/(null)_0.dm_*` filesystem probes during validated UI startup.
17. Closed the retail `UI_SERVER_SETTINGS` backend gap by reconstructing the `0x2A9` / `0x2AA` info-string publishers, replacing the old source-only `g_customSettings` bit walk with the retail mask layout, and aligning the writable UI ownerdraw with the recovered rows and Race icon suppression rules.
18. Removed the source-only `VM_CallNativeExports(ui)` trace spam from the engine VM bridge and aligned the writable UI `ui_browserAwesomium` registration default with the build-disabled online-services policy so validated startup logs no longer report a local cvar default mismatch.
19. Restored the retail `CG_DrawTeammatePOIs` seam in `src/code/cgame/cg_draw.c` by projecting visible teammates through the classic HUD path, clamping the name or location slab with the retail `..` trim behavior, and appending the recovered health, armor, flag, powerup, and task markers backed by the existing cgame status surfaces.
20. Restored the retail same-team crosshair target vitals seam in `CG_DrawCrosshairNames`, including the `0/1/2` `cg_drawCrosshairTeamHealth` mode behavior, the `0.26` name scale, and the centered `health / armor` readout driven by `cg_drawCrosshairTeamHealthSize`.
21. Reconstructed the retail fixed `CG_DrawTeamInfo` slab in `src/code/cgame/cg_draw.c`, restoring the top-anchored 16px icon cadence, 22px row step, clipped name and location text, carry and task icons, and health or armor bar presentation with a bounded score-row fallback when the team-info transport is absent.
22. Restored the classic lower-right `CG_DrawPowerups` / `CG_DrawLowerRight` seam in `src/code/cgame/cg_draw.c`, rebuilding the retail 3-second powerup popup around the mirrored `cg.powerupActive` and `cg.powerupTime` fields, the `%i:%i%i` timer text, the `x%i` stacked-powerup suffix, and the lower-right `cg_drawTeamOverlay == 2` branch.
23. Restored the retail classic-HUD `CG_DrawSpeedometer` seam in `src/code/cgame/cg_draw.c`, adding the 128-sample speed history ring, the recovered graph-mode split, and the numeric speed label ahead of the legacy lower-right stack while keeping the existing ownerdraw text helper intact.
24. Restored the retail classic-HUD `CG_DrawInputCmds` seam across `src/code/cgame/cg_draw.c`, `src/code/game/q_shared.h`, `src/code/qcommon/msg.c`, and `src/code/game/g_active.c`, mirroring the live or followed command bytes into `playerState_t`, serializing them through the snapshot delta stream, and drawing the recovered `gfx/2d/race/cmd_*` arrow slab ahead of the classic speedometer.

### Task 23: Ownerdraw/stat payload completion and validation [IN PROGRESS]
Priority: High
Primary areas: `src/code/game/`, `src/code/cgame/`, runtime validation harnesses

Large parts of the scorestats and ownerdraw pipeline are already in place. Remaining work is focused on the last retail-aligned payload details and keeping runtime fixtures honest.

Open subtasks:

1. Finish any residual per-player/per-team field mappings still using placeholders or approximations.
2. Compare additional runtime captures against retail-aligned expectations where HLIL alone is ambiguous.
3. Keep the debug-ownerdraw assertion path current as payload shape evolves.

## Secondary work

### Task 24: Gameplay validation sweep [OPEN]
Priority: Medium
Primary areas: physics, race, gametype-specific rules

The movement and gameplay code is no longer the top parity risk, but it still needs targeted retail validation.

Subtasks:

1. [x] Validate Attack & Defend round-controller parity against retail HLIL and the `qagame` symbol mapping after the latest gameplay-side changes.
2. [x] Restore the recovered retail award-configstring block and the init-side spawn-point count helper after the follow-up qagame parity pass.
3. Re-run focused Race checks after major gameplay-side changes.
4. Continue verifying match-flow sequencing against HLIL whenever state-machine code changes.
5. Capture regressions with focused tests instead of relying on broad manual inspection.

## Verification expectations after gameplay/client changes

When code changes can affect startup or runtime stability:

1. Build `Debug|x86`.
2. Run a normal launch pass with logging enabled.
3. Confirm active startup markers in `build\\win32\\Debug\\bin\\baseq3\\qconsole.log`.
4. Capture both a process-bound screenshot and an engine screenshot when possible.
5. Run a forced-crash probe to confirm dump generation still works.

## Working priority order

1. Native launcher/platform host reconstruction.
2. UI/menu asset and compatibility remediation within repository constraints.
3. Ownerdraw/stat payload completion and runtime validation.
4. Targeted gameplay validation sweeps.
