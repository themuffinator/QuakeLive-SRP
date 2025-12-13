# Client CVar Notes

The client registration table now mirrors the Quake Live HLIL defaults:

- Networking and input
  - `cl_maxpackets` defaults to 125 and is marked cheat-protected, while `cl_timeout` is tightened to 40s and `cl_timeNudge` is clamped server-side to the HLIL [-20, 0] window.
  - Input filtering follows Quake Live defaults (`m_filter 0`) and exposes mouse acceleration helpers (`cl_mouseAccel*`, `cl_mouseSensCap`, `m_cpi`).
- Demo and sound-adjacent
  - Avidemo helpers (`cl_avidemo_latch`, `cl_avidemo_mintime`, `cl_avidemo_maxtime`) and `cl_demoRecordMessage` mirror the HLIL flags so demo capture matches Quake Live behavior.
- User info
  - Customization CVars now use Quake Live defaults (`color1 7`, `color2 25`, `sensitivity 4`, `rate 25000`) with protected/cloud flags to match the HLIL table.

## Platform-specific CVars

These CVars are only meaningful on Steam-enabled builds and should be stubbed or conditionally compiled on other platforms:

- `cl_platform` is a ROM marker describing the active platform (HLIL defaults it to `1` for Steam).
- Download bookkeeping (`cl_downloadName`, `cl_downloadTime`, `cl_downloadItem`, `cl_downloadCount`, `cl_downloadSize`) reflects Steam Workshop/UGC progress strings seen in the HLIL trace; non-Steam targets should keep them as inert temp CVars.
- `cl_allowConsoleChat` and the cloud/protected flags (`CVAR_PROTECTED`, `CVAR_VM_CREATED`, `CVAR_CLOUD`) are Quake Live-specific; other targets can treat them as no-op guards.
