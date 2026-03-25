# Quake Live Parity Audit

Last updated: 2026-03-06

This audit reflects the current repository state against the retail Quake Live HLIL references and a fresh Windows `Debug|x86` build/runtime pass. The goal is not to score every file equally; it is to rank the gaps that still materially separate the repo from retail behavior.

## Overall assessment

- Core game and cgame reconstruction are now in the `medium-high parity` range.
- The largest remaining parity deficits are no longer basic gameplay systems; they are the native launcher/platform layer and the missing retail UI asset/menu stack.
- The most actionable gameplay-side gap found in this audit was match-flow configstring parity. That gap is now closed for the sudden-death/ready-up/warmup-ready path.

## What this audit closed

### Match-flow configstring parity

Retail HLIL shows dedicated client parsing for the match-flow side channels around `CS_MATCH_STATE`, including sudden-death and ready-up status configstrings. The repo previously had a split implementation:

- server code published `CS_MATCH_STATE`, `CS_READYUP_STATUS`, and `CS_WARMUP_READY`
- `CS_SUDDENDEATH_STATUS` existed in `bg_public.h` but was not actually published
- cgame did not parse `CS_SUDDENDEATH_STATUS`, `CS_READYUP_STATUS`, or `CS_WARMUP_READY`
- the HUD scoreboard treated the sudden-death spawn-delay config flag as if it meant "sudden death is active"

This task corrected that mismatch by:

- publishing `CS_SUDDENDEATH_STATUS` from qagame
- parsing `CS_SUDDENDEATH_STATUS`, `CS_READYUP_STATUS`, and `CS_WARMUP_READY` in cgame
- feeding ready-up deadline and readiness counts into the warmup overlay
- switching the HUD scoreboard and sudden-death label logic to use runtime sudden-death state instead of configuration-only flags

Result: match-flow HUD state is materially closer to the retail side-channel model shown in HLIL, and the client no longer drops those server updates on the floor.

## Current parity by area

### 1. Native launcher and platform host
Status: Low parity
Priority: Highest

This remains the largest gap in the repository.

- Retail Quake Live shipped a native `quakelive_steam.exe` host with Steam integration, web/launcher services, Awesomium-backed UI plumbing, image/HTTP bridges, and platform bootstrap code.
- The GPL-derived open tree still relies on classic engine/UI structures and does not reconstruct the retail host stack in source form.
- This gap impacts login/auth flow, browser-driven navigation, avatar/resource loading, workshop-style data paths, and multiple menu interactions that retail delegated to the launcher.

This is the highest-value parity target, but it is also the broadest reconstruction effort.

### 2. Retail UI asset/menu parity
Status: Low-medium parity
Priority: High

A fresh runtime pass still reports large volumes of missing retail UI assets and menu incompatibilities.

Observed on 2026-03-06:

- many missing `ui/assets/...` images
- missing font atlas assets with fallback text rendering
- `ui/hud.menu` parse errors for unsupported `font` keywords

Impact:

- visual parity remains materially below retail
- some HUD/menu layouts still depend on fallbacks rather than real retail assets or retail-compatible menu parsing
- this gap is currently constrained by the repository rule that `src/ui/` is read-only

Because the UI tree is read-only, the best short-term path is engine-side tolerance, bridge validation, and documenting which retail UI expectations are still unmet.

### 3. Ownerdraw/stat payload completion
Status: Medium parity
Priority: High

The repo has made substantial progress on scorestats, team pickup telemetry, key items, and placement ownerdraws. The remaining gap is not the existence of the pipeline; it is finishing and validating the residual retail-only fields and keeping the runtime payload aligned with the HLIL-backed ownerdraw behavior.

The current codebase already contains a large in-progress payload expansion. The next meaningful work here is to finish the remaining retail field mapping and keep validating against captured runtime baselines.

### 4. Match flow, warmup, sudden death, and scoreboard state
Status: Medium-high parity
Priority: Medium

This area improved in this task. The remaining work is lower-impact than the launcher/UI gaps and is now mostly about chasing smaller sequencing differences instead of missing whole data channels.

### 5. Physics, race, and gametype-specific gameplay
Status: Medium-high parity
Priority: Medium

The repo already has substantial reconstruction in movement and gametype logic. The main remaining need here is targeted validation against retail references, not wholesale subsystem creation.

## High-priority gaps to close next

1. Reconstruct the native launcher/platform host behavior currently represented only by HLIL and documentation.
2. Reduce retail UI/menu parity failures that still surface as missing assets, font fallbacks, and menu parse warnings at runtime.
3. Finish the remaining ownerdraw/stat payload parity work and keep runtime validation aligned with retail captures.

## Verification snapshot

Fresh verification completed on 2026-03-06:

- `MSBuild` solution build: `Debug|x86` succeeded
- focused pytest: `tests/test_match_state_configstring.py -q` passed the new match-flow assertions on Windows
- normal runtime pass: reached active gameplay state and produced an engine screenshot
- forced-crash pass: produced a fresh dump under `build\\win32\\Debug\\dumps`

Artifacts from the fresh runtime passes:

- normal engine screenshot: `build\\win32\\Debug\\bin\\baseq3\\screenshots\\ownerdraw_capture.jpg`
- crash-pass window capture metadata: `build\\win32\\Debug\\dumps\\screenshots\\startup_crash_window_20260306_112842.json`
- crash-pass screenshot: `build\\win32\\Debug\\dumps\\screenshots\\startup_crash_window_20260306_112842.png`
- crash dump: `build\\win32\\Debug\\dumps\\quakelive_steam_20260306_112848_445.dmp`

## Bottom line

The repo is no longer blocked on missing basic gameplay plumbing in the audited area. The highest remaining parity gaps are now:

- launcher/platform reconstruction
- retail UI/menu asset parity
- final ownerdraw/stat payload cleanup

The code change implemented in this task addressed the most concrete high-impact gameplay/UI state gap that was both HLIL-backed and directly actionable in the writable source tree.
