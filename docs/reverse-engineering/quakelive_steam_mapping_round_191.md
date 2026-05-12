# Quake Live Steam Mapping Round 191

## Scope

This round is source-only and tightens two Steam lobby callback behaviors in
`src/` to match the retained retail shapes more conservatively, without
changing the host alias corpus.

The targets were:

- `CL_Steam_Lobby_OnLobbyDataUpdate(...)`, where the checked-in source was
  still publishing an inferred nested `lobbydata` object for lobby-owned
  updates.
- `CL_Steam_Lobby_OnLobbyKicked(...)`, where the checked-in source was only
  clearing current-lobby state when the kicked lobby matched the cached local
  lobby.

Primary evidence stayed inside the committed retail corpus and reconstructed
source tree:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `src/code/client/cl_main.c`
- `tests/test_platform_services.py`

## Reconstructed Source Closure

### `lobby.%llu.updated` now keeps the thinner retained payload

Retail `sub_465490` clearly inserts top-level `"id"` into the published object
and conditionally walks lobby key/value pairs when `memberId == lobbyId`.
However, the final publish call still passes the top-level object built in
`var_828`, not the temporary enumerated object built in `var_83c`.

This round therefore removes the earlier source-side inference that promoted a
published `{"id":"...","lobbydata":{...}}` shape. The callback now emits the
more conservative retained payload:

- `{"id":"<lobby steamid>"}`

That keeps the source aligned with what the committed HLIL actually shows,
instead of preserving a richer wrapper that had not been revalidated strongly
enough.

### `lobby.%llu.kicked` now clears lobby state unconditionally after publish

Retail `sub_464830` publishes the kicked-lobby event and then immediately
clears the cached current-lobby globals without first checking whether the
incoming lobby ID matches the cached one.

This round removes the older guarded clear and restores the retail ordering:

1. publish `lobby.%llu.kicked`
2. clear current-lobby state

The useful outcome is that the source now matches both the retail payload
boundary and the retail post-callback state reset behavior for the stable
lobby callback seam.

## Verification

Static/source verification only:

- `python -m pytest tests/test_platform_services.py tests/test_steamworks_harness.py -q`
- `MSBuild` of `Debug|Win32` using
  `WindowsTargetPlatformVersion=10.0.26100.0`
- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
- `git diff --check`

The updated tests pin:

- the thinner retained `lobby.%llu.updated` payload
- the absence of the older nested `lobbydata` inference in that callback
- unconditional current-lobby clearing after `lobby.%llu.kicked`

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
