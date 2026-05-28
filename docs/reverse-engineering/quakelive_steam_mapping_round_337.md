# Quake Live Steam Mapping Round 337: WebUI Hash Navigation and Escape Ownership

Date: 2026-05-28

Scope: live Awesomium menu transitions, shell-only surface ownership, and the
browser-owned Escape path involved in the Settings -> Escape regression.

## Evidence Checked

- `references/analysis/quakelive_symbol_aliases.json` maps `sub_4F2590` to
  `QLWebCore_Update` and the browser command owners around the `web_*`
  registration lane.
- Previous HLIL rounds establish `web_showBrowser`, `web_changeHash`, and
  `web_hideBrowser` as distinct browser commands rather than aliases for a full
  document reload.
- Runtime comparison showed retail consumes Escape while the WebUI owns input.
  The reconstructed source had been calling `CL_WebHost_HideBrowser()` from the
  `KEYCATCH_BROWSER` Escape branch, which reproduced the dark shell screen.

## Source Reconstruction

- `QLWebView_SetLocationHash` now returns success/failure and, for live
  Awesomium, executes JavaScript that updates `window.location.hash` in the
  existing document instead of reloading `asset://ql/index.html`.
- `QLWebHost_NavigateOrOpen` uses that hash update on an already-ready live
  view, then reapplies the retail `web_zoom` latch.
- `CL_KeyEvent` now consumes Escape as a no-op while `KEYCATCH_BROWSER` is set.
- The Awesomium startup script still supports `SendGameCommand("web_changeHash
  ...")`, but it no longer installs a JavaScript Escape/back shim.
- `CL_WebHost_SurfaceReadyForOverlay` and `CL_WebHost_UpdateOverlayOwnership`
  require a visible, contentful browser surface before the WebUI owns fullscreen
  drawing or browser keycatch state.

## Runtime Verification

- Before this correction, a WebUI-enabled launch followed by a Settings hash
  change and real Escape key injection wrote `shot0043.jpg`, reproducing the
  dark Q-logo/copyright shell.
- After the source correction, a windowed WebUI-enabled launch using the same
  real Escape key injection wrote
  `build/win32/Debug/bin/baseq3/screenshots/webui_escape_noop_after_patch.jpg`.
  The screenshot remains on the Game Settings WebUI, matching retail's no-op
  behavior.
- A Campgrounds launch-task style pass with `ui_browserAwesomium 0` wrote
  `build/win32/Debug/bin/baseq3/screenshots/campgrounds_after_webui_patch.jpg`
  without the prop-character atlas or dark WebUI shell overlaying the map.

## Parity Estimate

- Focused WebUI launch/cache/navigation lane: **94% -> 96%**.
- Overall Awesomium WebUI wiring: **99.2% -> 99.3%**. Native callback objects
  and the full retail JSValue bridge remain the largest unmapped pieces.
- Repo-wide parity remains **98% -> 98%** because online services are still
  intentionally gated behind `QL_BUILD_ONLINE_SERVICES`.
