# Quake Live Steam Mapping Round 186

## Scope

This round is source-only and closes the next stable Steam lobby callback
payload seam in `src/` without changing the host alias corpus.

The target gap was the retained browser-event callback family in
`CL_Steam_Lobby_*`:

- `lobby.%s.create` still used the older `result` key and the error path still
  published a synthetic `{"result":...,"id":...}` wrapper
- `lobby.%s.user.joined` / `lobby.%s.user.left` still published the raw
  `stateChange` bitfield instead of the retained occupancy payload
- `lobby.%s.chat` still exposed `type`, and the game-created / kicked /
  join-requested callbacks still carried extra compatibility-only fields that
  the retail callback blocks do not publish

Primary evidence stayed inside the committed retail corpus and reconstructed
source tree:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `src/code/client/cl_main.c`
- `tests/test_platform_services.py`

## Reconstructed Source Closures

### Lobby create callbacks now use the retained status/error payload split

`CL_Steam_Lobby_OnLobbyCreated(...)` now mirrors the retail callback payload
split more closely:

- success publishes `{"id":"...","status":1}`
- failure publishes `{"code":...,"message":"Unable to create lobby"}`

That removes the older synthetic `result` wrappers and matches the callback
shape seen in the retail HLIL.

### Lobby membership updates now publish occupancy instead of raw state bits

`CL_Steam_Lobby_OnLobbyChatUpdate(...)` still logs the incoming
`stateChange` details for debugging, but the browser-facing payload now mirrors
the retained event surface:

- event names are the exact `lobby.%s.user.joined` and `lobby.%s.user.left`
  forms
- payloads now carry `id`, `name`, `num_players`, and `max_players`

That is a better reconstruction than exposing the raw bitfield to the web
bridge, because the retail callback publishes the lobby occupancy summary
instead.

### Chat/game/kick/join-requested callbacks no longer over-report fields

This pass also trims the remaining obvious compatibility wrappers from the same
callback family:

- `lobby.%s.chat` now publishes only `id`, `name`, and `msg`
- `lobby.%llu.game_created` now publishes only `ip`, `port`, and `id`
- `lobby.%llu.kicked` now publishes only `id`
- `lobby.%llu.join_requested` now publishes only `id`

That leaves the source aligned with the retail callback vocabulary instead of
continuing to expose fields like `type`, `server`, `admin`, `disconnected`,
and `friend` that are not present in the committed HLIL callback payloads.

### `lobby.%llu.updated` stays deferred

I intentionally left `CL_Steam_Lobby_OnLobbyDataUpdate(...)` alone in this
round. The retail callback still reads as a thinner update owner than the
current compatibility payload, but the exact public object shape remains less
stable than the rest of the callback family on current evidence. I did not
want to force a premature narrowing there.

## Verification

Static/source verification only:

- `python -m pytest tests/test_platform_services.py tests/test_steamworks_harness.py -q`
- `MSBuild` of `Debug|Win32` using
  `WindowsTargetPlatformVersion=10.0.26100.0`
- `git diff --check`

The updated tests pin:

- the retained `status` and `Unable to create lobby` payload split
- the exact joined/left event names and occupancy payload keys
- removal of the older extra lobby callback wrapper fields from the chat,
  game-created, kicked, and join-requested browser-event lane

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
