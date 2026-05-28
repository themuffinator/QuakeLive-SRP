# Quake Live Steam Mapping Round 333

Date: 2026-05-28

Scope: retail `web_*` cvar ownership, cached cvar globals, and live WebUI
consumers.

## Evidence

Primary retail signals:

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt` records
  the owning binary as `quakelive_steam.exe`.
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  identifies the relevant browser host functions: `FUN_004f3d70`,
  `FUN_004f2d30`, and `FUN_004f2590`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt:32923`
  registers `web_browserActive` into global `data_145ca50` with default `0`
  and flags `0x40`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:16547`
  registers `web_zoom` into `data_12d3060` with default `100` and flags `1`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:16550`
  registers `web_console` into `data_12d3064` with default `0` and flags `1`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:15764`
  shows the live WebView zoom path reading `data_12d3060->modified`, calling
  WebView slot `0xc4` with `data_12d3060->integer`, then clearing the modified
  latch.
- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c:45529`
  shows WebCore initialization reading `DAT_012d3064 + 0x30`, pinning
  `web_console` as a cached cvar pointer rather than a repeated name lookup.

## Source Reconstruction

`src/code/qcommon/common.c` now mirrors the core cached global for
`web_browserActive`:

- `com_webBrowserActive` stores the `Cvar_Get( "web_browserActive", "0",
  CVAR_ROM )` result.
- `Com_Frame()` uses the cached pointer when deciding whether an active browser
  should keep the idle sleep path enabled.
- The registration order now matches the retail sequence around `com_build`,
  `com_introplayed`, `com_idleSleep`, `web_browserActive`, and
  `com_allowConsole`.

`src/code/client/cl_cgame.c` now mirrors the browser-host cached globals:

- `cl_webZoom`, `cl_webConsole`, and `cl_webBrowserActive` retain the cvar
  pointers returned by `QLWebHost_RegisterCommands()`.
- `cl_webCvarRetailMappings[]` documents the recovered retail global address,
  default, flags, and runtime owner for each `web_*` cvar.
- `QLViewHandler_OnAddConsoleMessage()` reads the cached `web_console` cvar.
- Live Awesomium zoom application reads the cached `web_zoom` cvar, consumes
  its modified latch, and keeps the existing startup/navigation/reload
  reapply paths so dynamic SDK loading still receives the correct initial zoom.

## Guardrails

The current evidence set supports exactly three retail `web_*` cvars:

| Cvar | Retail global | Default | Flags | Owner |
| --- | ---: | --- | ---: | --- |
| `web_zoom` | `0x012D3060` | `100` | `CVAR_ARCHIVE` | WebView zoom slot `0xc4` |
| `web_console` | `0x012D3064` | `0` | `CVAR_ARCHIVE` | console-message listener |
| `web_browserActive` | `0x0145CA50` | `0` | `CVAR_ROM` | browser active state bridge |

No additional `web_*` cvar names were found in the committed
`quakelive_steam.exe` HLIL or Ghidra corpora during this pass. Names such as
`web_showBrowser`, `web_changeHash`, `web_hideBrowser`, `web_showError`,
`web_clearCache`, and `web_reload` are command registrations, not cvars.
`web_stopRefresh` remains source-side compatibility wiring for the retained UI
fallback path and is documented outside the strict retail command set.

## Parity Movement

Before this round, the focused `web_*` cvar lane was about `96%`
source-visible: the right names, defaults, and flags were registered, but the
retail cached cvar globals and modified-latch consumers were only partially
represented.

After this round, the focused lane is about `99%` source-visible and `99%`
mapped. Remaining differences are bounded to source-side compatibility helpers
around `web_stopRefresh` and dynamic Awesomium SDK fallback behavior, not to the
retail `web_*` cvar ownership itself.
