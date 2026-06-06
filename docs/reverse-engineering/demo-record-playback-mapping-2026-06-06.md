# Demo Record/Playback Mapping Round

Date: 2026-06-06

## Scope

This pass rechecked the Quake Live Steam host demo recording and playback
surface for protocol-91 `.dm_91` files and followed the related wiring into the
browser-facing demo list, console completion, cgame demo playback flag, and HUD
controls.

Writable source touched:

- `src/code/client/cl_cgame.c`
- `tests/test_demo_record_playback_mapping_parity.py`

Evidence used:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/analysis/quakelive_symbol_aliases.json`
- existing cgame symbol-map comments for demo playback controls

## Observed Retail Facts

1. `sub_4B82A0` remains `CL_WriteDemoMessage`. HLIL writes the current server
   message sequence, the post-header message length, and the payload bytes into
   the active demo handle.
2. `sub_4B8300` remains `CL_StopRecord_f`. It writes the `-1/-1` demo trailer,
   closes the file handle, clears the recording flags, and prints
   `Stopped demo.`.
3. `sub_4B8390` remains `CL_DemoFilename`, including the `demo9999.tga`
   fallback for out-of-range automatic demo numbers.
4. `sub_4B8430` remains `CL_Record_f`. It records through
   `demos/%s.dm_%d`, uses protocol `0x5b / 91`, publishes `game.demo` after a
   successful file open, serializes the retained gamestate/configstring and
   baseline packet, then writes the initial demo message.
5. `sub_4B87A0` remains `CL_WalkDemoExt`, iterating the supported protocol list
   and trying `demos/%s.dm_%d` until a readable demo is found.
6. `sub_4BB2A0`, `sub_4BB330`, and `sub_4BB450` remain
   `CL_DemoCompleted`, `CL_ReadDemoMessage`, and `CL_PlayDemo_f`. The playback
   path reads the same two-int message envelope, rejects payloads over
   `MAX_MSGLEN`, reports truncated payloads, supports explicit `.dm_??`
   filenames, and falls back to the protocol list when the supplied extension
   is unsupported or absent.
7. The Awesomium `GetDemoList` dispatcher at `0x0043335B` calls the filesystem
   list helper with `demos`, `dm_91`, then pushes each returned file-list string
   directly into a JavaScript array. No extension-stripping operation is
   visible in that retail block.
8. `Console_CompleteArgument` intentionally remains split from the browser
   demo list: the console completion still scans `.dm_73` after accepting only
   `demo` or `\demo`, matching the previously recovered retail quirk.
9. The cgame side keeps the demo-playback state as an explicit top-level draw
   argument: `CL_CGameRendering` passes `clc.demoplaying`, `CG_DrawActiveFrame`
   stores it in `cg.demoPlayback`, and `CG_DrawDemoPlaybackControls` renders the
   retail key legend around `cl_freezeDemo`, timescale stepping, and
   `cg_drawDemoHUD`.

## Source Reconstruction

The only source change justified in this round was the browser demo-list return
shape. `CL_WebHost_BuildDemoListJson` already enumerated with
`dm_%d / NET_DemoProtocol()`, which currently resolves to `dm_91`, but it then
stripped `.dm_91` before appending each JSON string. The retail block pushes
raw file-list entries, so the helper now returns raw `.dm_91` filenames.

No C body change was justified for the packet envelope or playback reader:
those paths already match the observed retail shape, including little-endian
server sequence and length fields, `MAX_MSGLEN` rejection, truncation handling,
protocol-list fallback, and the `-1/-1` terminator.

## Confidence

High for the demo packet envelope, file extension, browser-list return shape,
and playback fallback. These are supported by HLIL control flow, string
anchors, Ghidra function rows, existing alias promotion, and current writable
source.

Medium for broader runtime parity of arbitrary third-party `.dm_91` captures,
because this pass did not launch the client or replay live retail demo files.
The existing `tools/trace/demo_transcript.py` remains the reviewable intake path
for future captured demo evidence.

## Open Questions

1. The retained console completion `.dm_73` scan remains an observed retail
   quirk rather than an error. Reopening it would need newer retail evidence
   showing that `sub_4B6A60` changed.
2. This pass did not attempt live replay validation. That remains a runtime
   evidence task only if a future `.dm_91` capture exposes behavior that static
   mapping cannot settle.

## Verification

- `python -m pytest tests/test_demo_record_playback_mapping_parity.py -q`
- `python -m pytest tests/test_demo_record_playback_mapping_parity.py tests/test_engine_command_parity.py tests/test_engine_client_command_parity.py tests/test_engine_netcode_parity.py -q --tb=short`
- `python -m pytest tests/test_platform_services.py -q --tb=short`

Parity estimate for the focused demo recording/playback and related browser,
console, and cgame wiring surface: **before 96% -> after 99%**. The remaining
1% is live-capture playback freshness, not a known static source mismatch.
