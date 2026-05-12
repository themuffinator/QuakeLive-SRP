# Quake Live Steam Mapping Round 187

## Scope

This round is source-only and closes the next stable Steam lobby data seam in
`src/` without changing the host alias corpus.

The target gap was the remaining bridge between the lobby create/update
callbacks and the retained Steam lobby-data surface:

- the source tree still lacked the exact `SteamMatchmaking()->SetLobbyData`
  wrapper used by the retail `LobbyCreated_t` callback
- `CL_Steam_Lobby_OnLobbyEnter(...)` still open-coded the lobby-data JSON loop
  instead of using a shared owner
- `CL_Steam_Lobby_OnLobbyDataUpdate(...)` still published the older synthetic
  `member` / `success` wrapper instead of the thinner retail update object

Primary evidence stayed inside the committed retail corpus and reconstructed
source tree:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`
- `src/code/client/cl_main.c`
- `src/common/platform/platform_steamworks.c`
- `src/common/platform/platform_steamworks.h`
- `tests/test_platform_services.py`

## Reconstructed Source Closures

### The retained lobby-data setter now exists as a first-class Steam wrapper

Retail `CL_Steam_Lobby_OnLobbyCreated(...)` does not stop at publishing the
browser event. On successful creation it first calls the matchmaking interface
slot at `0x50 / 4` to write the default lobby-data pair `"hello" -> "world"`.

This round reconstructs that missing owner as:

- `QL_Steamworks_SetLobbyData(...)` in `platform_steamworks.c`
- declaration plus build-disabled inline stub in `platform_steamworks.h`

The client callback now uses that exact wrapper instead of silently omitting
the retained side effect.

### Lobby data now has one shared JSON owner

`CL_Steam_Lobby_OnLobbyEnter(...)` previously hand-built the `lobbydata`
object inline. This round lifts that work into
`CL_Steam_AppendLobbyDataJson(...)`, which centralises the retained
`GetLobbyDataCount` / `GetLobbyDataByIndex` walk and the escaping/append
surface used by the browser payload lane.

That keeps the same payload shape for lobby enter, but it removes duplication
and gives the update callback a clear, source-backed reuse point.

### `lobby.%llu.updated` now mirrors the thinner retained update object

`CL_Steam_Lobby_OnLobbyDataUpdate(...)` no longer publishes the older
compatibility payload with `member` and `success`.

It now uses the thinner retained split:

- member-level updates publish only `{"id":"..."}`
- lobby-owned updates publish `{"id":"...","lobbydata":{...}}`

The second shape is an inference from the retail HLIL rather than a literal
one-line decompiler match. The evidence is strong enough to promote because
the retail callback rebuilds a full lobby key/value object immediately before
publishing `lobby.%llu.updated`; the committed decompiler drops the explicit
attach edge, but the object-construction work is otherwise dead unless that
map is part of the outbound payload.

## Verification

Static/source verification only:

- `python -m pytest tests/test_platform_services.py tests/test_steamworks_harness.py -q`
- `MSBuild` of `Debug|Win32` using
  `WindowsTargetPlatformVersion=10.0.26100.0`
- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
- `git diff --check`

The updated tests pin:

- the new `QL_Steamworks_SetLobbyData(...)` wrapper slot owner (`0x50 / 4`)
- the create-callback `hello` / `world` side effect
- reuse of the shared lobby-data JSON helper from both the enter and update
  callback lanes
- the thinner `lobby.%llu.updated` payload split

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
