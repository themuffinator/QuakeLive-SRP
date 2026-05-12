# Quake Live Steam Mapping Round 190

## Scope

This round is source-only and corrects the retained Steam persona-change
browser event shape in `src/` without changing the host alias corpus.

The target gap was a thinner compatibility payload in
`CL_Steam_Client_OnPersonaStateChange(...)`. The checked-in source was
publishing the direct friend summary object, but retail HLIL shows a distinct
wrapper shape:

- top-level `id`
- top-level `state` change mask
- nested `friend` object carrying the full summary payload

Primary evidence stayed inside the committed retail corpus and reconstructed
source tree:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `src/code/client/cl_main.c`
- `src/common/platform/platform_steamworks.h`
- `tests/test_platform_services.py`

## Reconstructed Source Closure

### Persona-change now uses the retained wrapper instead of the thin summary

Retail `sub_460800` does not publish the same payload as
`users.presence.%llu.change`. The HLIL shows:

- `users.presence.%llu.change` publishing a thin `{id,status,lanIp}` object
- `users.persona.%llu.change` publishing `{id,state,friend:{...}}`

This round restores that split by adding
`CL_Steam_FormatPersonaChangeJson(...)` and routing the persona callback
through it. The nested `friend` object reuses the already reconstructed
friend-summary formatter, while the top-level wrapper carries the change mask
from `PersonaStateChange_t`.

The useful outcome is that the social callback surface now reflects the actual
retail distinction between “rich presence changed” and “persona metadata
changed” instead of collapsing both callbacks onto summary-shaped payloads.

## Verification

Static/source verification only:

- `python -m pytest tests/test_platform_services.py tests/test_steamworks_harness.py -q`
- `MSBuild` of `Debug|Win32` using
  `WindowsTargetPlatformVersion=10.0.26100.0`
- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
- `git diff --check`

The updated tests pin:

- the dedicated persona-change formatter owner
- the retained `{id,state,friend}` wrapper shape
- continued thin `users.presence` payloads for the rich-presence callback

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
