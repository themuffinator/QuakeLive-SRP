# Quake Live Steam Mapping Round 185

## Scope

This round is source-only and closes the next stable Steam social callback
payload seam in `src/` without changing the host alias corpus.

The target gap was the retained callback JSON family shared by the Steam social
lane in `cl_main.c`:

- `users.persona.%s.change` still wrapped the summary in a synthetic
  `{"changeFlags":...,"friend":...}` compatibility envelope
- `users.presence.%s.change` still wrapped the summary in a synthetic
  `{"appId":...,"friend":...}` compatibility envelope
- retail `quakelive_steam.exe` instead publishes two direct payload shapes:
  a full friend summary for persona changes and a smaller
  `{id,status,lanIp}` object for rich-presence updates

Primary evidence stayed inside the committed retail corpus and reconstructed
source tree:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `src/code/client/cl_main.c`
- `tests/test_platform_services.py`

## Reconstructed Source Closures

### Persona-change callbacks now publish the direct retained friend summary

`CL_Steam_Client_OnPersonaStateChange(...)` still logs the retained
`changeFlags` detail, but the browser-visible payload no longer invents a
second wrapper object around the friend summary.

This round keeps the shared `CL_Steam_FormatFriendSummaryJson(...)` owner from
round 184 and now publishes that JSON directly as the
`users.persona.%s.change` payload, which is the shape supported by the retail
HLIL callback block.

### Rich-presence callbacks now use the smaller retained presence payload

The rich-presence callback does not publish the full friend summary in retail.
It emits a compact payload carrying only the Steam id, status string, and LAN
IP string.

This round reconstructs that exact owner as
`CL_Steam_FormatFriendPresenceJson(...)` and routes
`CL_Steam_Client_OnFriendRichPresenceUpdate(...)` through it before publishing
`users.presence.%s.change`.

That removes the older synthetic `appId` / `friend` wrapper and keeps the
presence lane from over-reporting fields that are only present in the broader
summary object.

### The shared social payload vocabulary is now internally consistent

Rounds 184 and 185 together now give the Steam social/browser seam a cleaner
retail-aligned split:

- browser friend lists reuse the shared nested friend summary owner
- persona-change callbacks publish that same retained summary directly
- presence callbacks publish the retained minimal presence object directly

That is a better source reconstruction than keeping multiple callback-specific
compatibility wrappers whose keys were never present in the committed retail
evidence.

## Verification

Static/source verification only:

- `python -m pytest tests/test_platform_services.py tests/test_steamworks_harness.py -q`
- `MSBuild` of `Debug|Win32` using
  `WindowsTargetPlatformVersion=10.0.26100.0`
- `git diff --check`

The updated tests pin:

- the direct persona payload publication through
  `CL_Steam_FormatFriendSummaryJson(...)`
- the exact retained presence formatter shape
  `{"id":"%s","status":"%s","lanIp":"%s"}`
- removal of the older synthetic `changeFlags` / `friend` and
  `appId` / `friend` wrappers from the callback payload lane

## Coverage Impact

This round is source-only. Host alias totals stay unchanged:

- raw aliases: `2038`
- strict Ghidra address-backed aliases: `1970`
- strict Ghidra address-backed coverage: `35.995%`

The largest-unaliased host queue is therefore unchanged as well:

1. `0x004FC240`
2. `0x0041AD70`
3. `0x004E6730`

## Parity Estimate

- strict-retail Windows target: `100% -> 100%`
- repo-wide reconstructed source base: `98% -> 98%`
